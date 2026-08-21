# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""The Violet Pool Controller integration."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .config_entry_helpers import (
    extract_api_host,
    get_entry_value,
    with_non_default_port,
)
from .config_flow_utils.constants import (
    MAX_POLLING_INTERVAL,
    MAX_RETRIES,
    MAX_TIMEOUT,
    MIN_RETRIES,
    MIN_TIMEOUT,
)
from .const import (
    CONF_ACTIVE_FEATURES,
    CONF_ADAPTIVE_POLLING,
    CONF_ALLOW_UNSAFE_SWITCHES,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_GROUP_ENTITIES,
    CONF_PASSWORD,
    CONF_POLLING_INTERVAL,
    CONF_PORT,
    CONF_RETRY_ATTEMPTS,
    CONF_SELECTED_SENSORS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    CONFIG_ENTRY_VERSION,
    DEFAULT_ADAPTIVE_POLLING,
    DEFAULT_CONTROLLER_NAME,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    MIN_SUPPORTED_POLLING_INTERVAL,
    UNSAFE_SWITCH_KEYS,
)
from .device_hierarchy import async_cleanup_sub_devices, async_precreate_devices
from .entity_cleanup import async_remove_orphaned_entities
from .runtime_data import VioletRuntimeData, get_runtime_data

_LOGGER = logging.getLogger(__name__)

# Platforms to be loaded
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.UPDATE,
    Platform.BUTTON,
]

# YAML configuration is deprecated
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


# =============================================================================
# SETUP FUNCTIONS
# =============================================================================


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old config entry.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry to migrate.

    Returns:
        True if migration was successful, False otherwise.
    """
    _LOGGER.debug("Migrating config entry from version %s", config_entry.version)

    if config_entry.version > CONFIG_ENTRY_VERSION:
        # Downgrade: the entry was written by a newer version of the integration.
        _LOGGER.error(
            "Config entry version %s is newer than this integration supports (%s)",
            config_entry.version,
            CONFIG_ENTRY_VERSION,
        )
        return False

    if config_entry.version < 2:
        _migrate_v1_to_v2(hass, config_entry)

    if config_entry.version < 3:
        _migrate_v2_to_v3(hass, config_entry)

    _LOGGER.debug("Config entry migrated to version %s", CONFIG_ENTRY_VERSION)
    return True


def _migrate_v1_to_v2(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Add the features that ECO and the DMX scenes were split into.

    Both used to be ungated (ECO) or part of ``led_lighting`` (DMX scenes).
    A stored feature list never mentions the new ids, and an unknown id counts
    as disabled - so without this migration the entities would silently vanish
    on update. The new ids therefore inherit the behaviour the entry had:
    ``eco_mode`` was always on, ``dmx_scenes`` follows ``led_lighting``.
    """
    inherited = {"eco_mode": True, "dmx_scenes": None}

    def _upgrade(features: list[str]) -> list[str]:
        upgraded = list(features)
        for feature_id, enabled in inherited.items():
            if feature_id in upgraded:
                continue
            keep = enabled if enabled is not None else "led_lighting" in upgraded
            if keep:
                upgraded.append(feature_id)
        return upgraded

    data = dict(config_entry.data)
    options = dict(config_entry.options)
    changed = False

    for container in (data, options):
        features = container.get(CONF_ACTIVE_FEATURES)
        # Only touch a list that is actually stored; absent means "everything".
        if isinstance(features, list):
            upgraded = _upgrade(features)
            if upgraded != features:
                container[CONF_ACTIVE_FEATURES] = upgraded
                changed = True

    hass.config_entries.async_update_entry(config_entry, data=data, options=options, version=2)
    if changed:
        _LOGGER.info(
            "Config entry %s: added the eco_mode/dmx_scenes features to the "
            "stored selection so the existing entities are kept",
            config_entry.entry_id,
        )


def _migrate_v2_to_v3(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Widen a sensor-only selection to the platforms it now governs.

    The stored selection was made when it only decided which *sensors* exist,
    so a user who unticked ``PUMP`` to hide the raw reading never meant to lose
    their pump switch. Now that every platform honours the selection, those
    entries would disappear on update.

    The keys of all non-sensor entity definitions are therefore added once, at
    migration time: the entity set stays exactly as it is today, and pruning it
    becomes the user's decision. Adding a key can only keep an entity - the
    feature gates and "key present in the controller response" checks still
    apply on top.
    """
    from .const_features import BINARY_SENSORS, DMX_LIGHTS, SELECT_CONTROLS, SWITCHES

    tables: tuple[tuple[Sequence[Any], str], ...] = (
        (SWITCHES, "key"),
        (BINARY_SENSORS, "key"),
        (SELECT_CONTROLS, "device_key"),
        (DMX_LIGHTS, "key"),
    )
    control_keys: set[str] = set()
    for table, field in tables:
        for definition in table:
            key = definition.get(field) if isinstance(definition, dict) else None
            if key:
                control_keys.add(str(key))

    data = dict(config_entry.data)
    options = dict(config_entry.options)
    added = 0

    for container in (data, options):
        selection = container.get(CONF_SELECTED_SENSORS)
        # No stored selection means "everything" - nothing to widen.
        if not isinstance(selection, list):
            continue
        missing = sorted(control_keys - set(selection))
        if missing:
            container[CONF_SELECTED_SENSORS] = list(selection) + missing
            added = max(added, len(missing))

    hass.config_entries.async_update_entry(config_entry, data=data, options=options, version=3)
    if added:
        _LOGGER.info(
            "Config entry %s: kept %d control datapoints that the selection now "
            "governs - deselect them in the options if you do not want them",
            config_entry.entry_id,
            added,
        )


def _migrate_duplicate_prefix_entity_ids(
    entity_registry: er.EntityRegistry,
    config_entry_id: str,
) -> None:
    """Rename entity_ids that contain a duplicated domain slug.

    Entities registered before the strip_redundant_device_prefix fix may have
    entity_ids like ``switch.violet_pool_controller_violet_pool_controller_beleuchtung``.
    This migration renames them to ``switch.violet_pool_controller_beleuchtung``
    so that automations and dashboards referencing the new names work correctly.
    """
    double_slug = f"{DOMAIN}_{DOMAIN}_"
    migrated_count = 0

    for entity_entry in er.async_entries_for_config_entry(entity_registry, config_entry_id):
        entity_id = entity_entry.entity_id
        dot = entity_id.find(".")
        if dot == -1:
            continue
        object_id = entity_id[dot + 1 :]
        if not object_id.startswith(double_slug):
            continue

        # Collapse any number of repeated domain slugs down to one.
        new_object_id = object_id
        while new_object_id.startswith(double_slug):
            new_object_id = f"{DOMAIN}_" + new_object_id[len(double_slug) :]

        new_entity_id = f"{entity_id[: dot + 1]}{new_object_id}"
        if entity_registry.async_get(new_entity_id) is not None:
            _LOGGER.debug(
                "Skipping migration %s → %s: target already exists",
                entity_id,
                new_entity_id,
            )
            continue
        _LOGGER.info(
            "Migrating entity_id '%s' → '%s' (duplicate device prefix removed)",
            entity_id,
            new_entity_id,
        )
        try:
            entity_registry.async_update_entity(entity_id, new_entity_id=new_entity_id)
            migrated_count += 1
        except Exception as err:
            _LOGGER.error(
                "Failed to migrate entity_id '%s' → '%s': %s",
                entity_id,
                new_entity_id,
                err,
            )

    if migrated_count > 0:
        _LOGGER.info(
            "Entity migration complete: %d duplicate prefixes removed for config_entry %s",
            migrated_count,
            config_entry_id,
        )


def _disable_unsafe_switches(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    config_entry_id: str,
) -> None:
    """Auto-disable unsafe manual control switches for safety.

    Switches like dosing, backwash, and refill should use Services instead
    because they require mandatory time limits to prevent equipment damage,
    chemical overdose, and flooding.
    """
    from .const import CONF_ALLOW_UNSAFE_SWITCHES, DEFAULT_ALLOW_UNSAFE_SWITCHES

    # Get the config entry to check the allow_unsafe_switches setting
    entry = hass.config_entries.async_get_entry(config_entry_id)
    if not entry:
        return

    allow_unsafe = entry.options.get(
        CONF_ALLOW_UNSAFE_SWITCHES,
        entry.data.get(CONF_ALLOW_UNSAFE_SWITCHES, DEFAULT_ALLOW_UNSAFE_SWITCHES),
    )

    prefix = f"{config_entry_id}_"

    if allow_unsafe:
        # If user explicitly allowed unsafe switches, re-enable any previously disabled ones
        _LOGGER.warning(
            "⚠️ SAFETY WARNING: Unsafe switches are ENABLED for '%s'. "
            "User accepts full responsibility for risks (equipment damage, chemical overdose, flooding)",
            config_entry_id,
        )
        re_enabled_count = 0
        for entity_entry in er.async_entries_for_config_entry(entity_registry, config_entry_id):
            if entity_entry.domain != "switch":
                continue
            if not entity_entry.unique_id.startswith(prefix):
                continue
            key = entity_entry.unique_id[len(prefix) :]
            if key not in UNSAFE_SWITCH_KEYS:
                continue
            if entity_entry.disabled_by != er.RegistryEntryDisabler.INTEGRATION:
                continue
            _LOGGER.info("Re-enabling unsafe switch '%s' (%s)", entity_entry.entity_id, key)
            try:
                entity_registry.async_update_entity(entity_entry.entity_id, disabled_by=None)
                re_enabled_count += 1
            except Exception as err:
                _LOGGER.error(
                    "Failed to re-enable unsafe switch '%s': %s",
                    entity_entry.entity_id,
                    err,
                )
        if re_enabled_count > 0:
            _LOGGER.info(
                "Re-enabled %d unsafe switches for '%s'", re_enabled_count, config_entry_id
            )
        return

    # Disable unsafe switches for safety
    disabled_count = 0
    for entity_entry in er.async_entries_for_config_entry(entity_registry, config_entry_id):
        # Only process switches
        if entity_entry.domain != "switch":
            continue

        # Extract key from unique_id (format: "{entry_id}_{key}")
        if not entity_entry.unique_id.startswith(prefix):
            continue

        key = entity_entry.unique_id[len(prefix) :]

        # Check if this is an unsafe switch
        if key not in UNSAFE_SWITCH_KEYS:
            continue

        # Skip if already disabled
        if entity_entry.disabled:
            continue

        # Disable the entity
        _LOGGER.warning(
            "🚨 SAFETY: Auto-disabling unsafe switch '%s' (%s). Use Services instead!",
            entity_entry.entity_id,
            key,
        )
        try:
            entity_registry.async_update_entity(
                entity_entry.entity_id, disabled_by=er.RegistryEntryDisabler.INTEGRATION
            )
            disabled_count += 1
        except Exception as err:
            _LOGGER.error(
                "Failed to disable unsafe switch '%s': %s",
                entity_entry.entity_id,
                err,
            )

    if disabled_count > 0:
        _LOGGER.warning(
            "🚨 SAFETY: Disabled %d unsafe switches for '%s'. Use Services with time limits instead!",
            disabled_count,
            config_entry_id,
        )



def _backfill_unique_id(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Give an entry the unique id discovery matches against.

    Entries created before the config flow set a unique id carry ``None``.
    ``_abort_if_unique_id_configured()`` has nothing to compare such an entry
    against, so zeroconf offers the very same controller as a new discovery
    again and again - reported on the forum as "HA findet regelmässig neue
    Violet Pool Controller".

    Runs on every setup rather than in ``async_migrate_entry``: the affected
    entries are already at the current version, so a version-gated migration
    would never reach them.
    """
    if entry.unique_id:
        return

    # extract_api_host also understands the legacy `host` / `base_ip` keys,
    # which is a second reason an old entry never matched. It raises when the
    # entry names no host at all - there is nothing to build an id from then.
    try:
        host = extract_api_host(entry.data)
    except ValueError:
        return

    try:
        device_id = int(entry.data.get(CONF_DEVICE_ID, 1))
    except (TypeError, ValueError):
        device_id = 1

    unique_id = f"{host}-{device_id}"
    hass.config_entries.async_update_entry(entry, unique_id=unique_id)
    _LOGGER.info(
        "Assigned unique id %s to an entry that had none; discovery will stop "
        "offering this controller as new",
        unique_id,
    )

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.

    Returns:
        True if setup was successful.

    Raises:
        ConfigEntryNotReady: If the controller is not ready.
        HomeAssistantError: If the configuration is invalid.
    """
    _LOGGER.info(
        "Setting up Violet Pool Controller (entry_id=%s, controller=%s)",
        entry.entry_id,
        entry.data.get(CONF_CONTROLLER_NAME, entry.data.get(CONF_DEVICE_NAME, "Unknown")),
    )

    _backfill_unique_id(hass, entry)

    # Lazy imports to avoid blocking the event loop
    from violet_poolcontroller_api.api import VioletPoolAPI

    from .device import async_setup_device

    # Extract configuration
    config = _extract_config(entry)

    # Validate configuration
    if not _validate_config(config):
        raise HomeAssistantError("Invalid configuration")

    try:
        host = with_non_default_port(config["ip_address"], config["port"])
        # Create API instance
        from .const import CONF_DOSING_STANDALONE, DEFAULT_DOSING_STANDALONE

        dosing_standalone = entry.data.get(CONF_DOSING_STANDALONE, DEFAULT_DOSING_STANDALONE)

        api = VioletPoolAPI(
            host=host,
            session=aiohttp_client.async_get_clientsession(hass),
            username=config["username"],
            password=config["password"],
            use_ssl=config["use_ssl"],
            verify_ssl=config["verify_ssl"],
            timeout=config["timeout_duration"],
            max_retries=config["retry_attempts"],
            dosing_standalone=dosing_standalone,
        )

        # Set up device and coordinator
        coordinator = await async_setup_device(hass, entry, api)

        if not coordinator:
            _LOGGER.error("Failed to set up coordinator for %s", config["device_name"])
            raise ConfigEntryNotReady("Coordinator setup failed")

        # Everything this entry needs at runtime lives on the entry itself.
        # structural_options records which options the created entities are
        # based on, so the update listener can tell a structural change
        # (features, sensors) apart from a setting that can be applied without
        # a reload.
        entry.runtime_data = VioletRuntimeData(
            coordinator=coordinator,
            structural_options=_structural_options(entry),
        )

        # Migrate entity_ids that have the duplicate device prefix (e.g.
        # switch.violet_pool_controller_violet_pool_controller_beleuchtung →
        # switch.violet_pool_controller_beleuchtung).  Must run before
        # platforms are loaded so that the registry already contains the
        # corrected entity_ids when entities re-register themselves.
        _migrate_duplicate_prefix_entity_ids(er.async_get(hass), entry.entry_id)

        # Auto-disable unsafe switches (dosing, backwash, refill) that require
        # mandatory time limits via Services instead of switches
        _disable_unsafe_switches(hass, er.async_get(hass), entry.entry_id)

        # Create the controller device and its sub-devices before the platforms
        # run, so every entity finds its parent regardless of platform order.
        async_precreate_devices(hass, entry, coordinator)

        # Load platforms. A second enforcement pass afterwards is not needed:
        # the switch platform creates every UNSAFE_SWITCH_KEYS entity with
        # entity_registry_enabled_default derived from the same option, so
        # registry entries created during this setup are already disabled.
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        # Register update listener for config changes (e.g., polling_interval)
        entry.async_on_unload(entry.add_update_listener(async_update_listener))

        # Register services (only once for the entire integration)
        from .services import async_register_services

        await async_register_services(hass)

        # Drop registry entries the platforms no longer provide, so disabling a
        # feature, deselecting a sensor or removing a hardware module actually
        # makes the matching entities disappear instead of leaving them behind
        # as permanently unavailable "restored" entries.
        async_remove_orphaned_entities(hass, entry, PLATFORMS)

        # Drop sub-devices that ended up empty (hardware module absent, feature
        # disabled) and every sub-device when grouping is switched off.
        async_cleanup_sub_devices(hass, entry)

        _LOGGER.info(
            "Setup completed successfully for '%s' (entry_id=%s)",
            config["device_name"],
            entry.entry_id,
        )

        return True

    except ConfigEntryNotReady:
        # Re-raise ConfigEntryNotReady to allow Home Assistant to handle retries
        _LOGGER.warning(
            "Setup for '%s' is not ready yet, will be retried automatically",
            config["device_name"],
        )
        raise

    except Exception as err:
        _LOGGER.exception("Unexpected error during setup (entry_id=%s): %s", entry.entry_id, err)
        raise ConfigEntryNotReady(f"Setup error: {err}") from err


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry with proper resource cleanup.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry to unload.

    Returns:
        True if unload was successful, False otherwise.
    """
    device_name = entry.data.get(CONF_DEVICE_NAME, "Unknown")
    _LOGGER.info("Unloading '%s' (entry_id=%s)", device_name, entry.entry_id)

    try:
        # Unload platforms first
        unload_ok = bool(await hass.config_entries.async_unload_platforms(entry, PLATFORMS))

        if unload_ok:
            # NOTE: Do NOT close the aiohttp session - it is managed by Home
            # Assistant (created via async_get_clientsession) and must only be
            # closed by it. Everything else lives on entry.runtime_data, which
            # Home Assistant drops as part of the unload.
            _LOGGER.info("Successfully unloaded '%s' (entry_id=%s)", device_name, entry.entry_id)
        else:
            _LOGGER.warning(
                "Failed to unload platforms for '%s' (entry_id=%s)",
                device_name,
                entry.entry_id,
            )

        return unload_ok

    except Exception as err:
        _LOGGER.exception("Error during unload of '%s': %s", device_name, err)
        return False


def _structural_options(entry: ConfigEntry) -> dict[str, Any]:
    """Return the options that decide *which* entities are created.

    Changing any of these requires re-running the platform setups, because the
    entity list is built from them. Everything else (polling interval, timeout,
    credentials, ...) is applied on the running coordinator instead.
    """
    options: dict[str, Any] = {}

    for option in (
        CONF_ACTIVE_FEATURES,
        CONF_SELECTED_SENSORS,
        CONF_ALLOW_UNSAFE_SWITCHES,
        CONF_GROUP_ENTITIES,
    ):
        value = entry.options.get(option, entry.data.get(option))
        # Feature/sensor selections are order-insensitive lists.
        options[option] = sorted(value) if isinstance(value, list) else value

    return options


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry updates (e.g., polling_interval, timeout, retry changes).

    This function is called when the user modifies integration options.

    Changes to the enabled features or the sensor selection decide which
    entities exist and therefore require a reload of the config entry. All
    other settings are applied dynamically on the running coordinator.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry that was updated.
    """
    _LOGGER.info(
        "Config entry updated for '%s' (entry_id=%s)",
        entry.data.get(CONF_DEVICE_NAME, "Unknown"),
        entry.entry_id,
    )

    runtime_data = get_runtime_data(entry)
    if runtime_data is None:
        _LOGGER.warning("Coordinator not found for entry_id=%s", entry.entry_id)
        return

    coordinator = runtime_data.coordinator

    # Reload when the feature/sensor selection changed - the entities are
    # created from it, so it can only take effect by re-running the platforms.
    current_options = _structural_options(entry)

    if runtime_data.structural_options != current_options:
        _LOGGER.info(
            "Feature/sensor selection changed for entry_id=%s, reloading integration",
            entry.entry_id,
        )
        hass.config_entries.async_schedule_reload(entry.entry_id)
        return

    # Track if any setting was updated
    settings_updated = False

    # 1. Update polling settings if changed. Compare against the coordinator's
    # configured (base) interval, not update_interval - the latter is stretched
    # while the controller is idle and would otherwise look like a change on
    # every options save.
    new_polling_interval = get_entry_value(
        entry,
        CONF_POLLING_INTERVAL,
        DEFAULT_POLLING_INTERVAL,
    )
    new_adaptive_polling = get_entry_value(
        entry,
        CONF_ADAPTIVE_POLLING,
        DEFAULT_ADAPTIVE_POLLING,
    )

    if coordinator.apply_polling_options(new_polling_interval, new_adaptive_polling):
        _LOGGER.info(
            "Polling settings updated to %ds (adaptive: %s, entry_id=%s)",
            new_polling_interval,
            new_adaptive_polling,
            entry.entry_id,
        )

        # Force an immediate refresh so the new interval takes effect now
        await coordinator.async_request_refresh()
        settings_updated = True
    else:
        _LOGGER.debug(
            "Polling settings unchanged at %ds (entry_id=%s)",
            new_polling_interval,
            entry.entry_id,
        )

    # 2. Update API connection settings if changed
    if hasattr(coordinator.device, "update_api_config"):
        api_updated = await coordinator.device.update_api_config(entry)
        if api_updated:
            settings_updated = True

    # Log summary
    if settings_updated:
        _LOGGER.info(
            "All settings updated successfully for entry_id=%s",
            entry.entry_id,
        )
    else:
        _LOGGER.debug(
            "No settings changes detected for entry_id=%s",
            entry.entry_id,
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _extract_config(entry: ConfigEntry) -> dict[str, Any]:
    """Extract and normalize configuration from a ConfigEntry.

    This function retrieves configuration values from the ConfigEntry's data and
    options, providing default values for missing optional settings. It also handles
    legacy configuration keys for backward compatibility.

    Args:
        entry: The Home Assistant ConfigEntry.

    Returns:
        A dictionary containing the extracted and normalized configuration.

    Raises:
        HomeAssistantError: If the IP address (host) is missing from the configuration.
    """
    # Extract IP address with fallbacks for legacy keys
    try:
        ip_address = extract_api_host(entry.data)
    except ValueError as err:
        _LOGGER.error("Required IP address is missing from the configuration.")
        raise HomeAssistantError(str(err)) from err

    port = entry.data.get(CONF_PORT, DEFAULT_PORT)

    # Numeric settings are clamped to the range the integration supports.
    # The config/options flow and this module used to disagree about the
    # allowed ranges, so a value the UI happily accepted (e.g. a 600s polling
    # interval or a 3s timeout) made the next setup fail outright. Clamping
    # keeps such an entry working instead of leaving the user with a
    # permanently broken integration.
    # Build the configuration dictionary with defaults
    return {
        "ip_address": ip_address.strip(),
        "port": port,
        "use_ssl": entry.data.get(CONF_USE_SSL, True),
        "verify_ssl": entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME, ""),
        "password": entry.data.get(CONF_PASSWORD, ""),
        "device_name": entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
        "controller_name": entry.data.get(CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME),
        "polling_interval": _clamped_setting(
            entry,
            CONF_POLLING_INTERVAL,
            DEFAULT_POLLING_INTERVAL,
            MIN_SUPPORTED_POLLING_INTERVAL,
            MAX_POLLING_INTERVAL,
        ),
        "timeout_duration": _clamped_setting(
            entry,
            CONF_TIMEOUT_DURATION,
            DEFAULT_TIMEOUT_DURATION,
            MIN_TIMEOUT,
            MAX_TIMEOUT,
        ),
        "retry_attempts": _clamped_setting(
            entry,
            CONF_RETRY_ATTEMPTS,
            DEFAULT_RETRY_ATTEMPTS,
            MIN_RETRIES,
            MAX_RETRIES,
        ),
        "adaptive_polling": bool(
            get_entry_value(entry, CONF_ADAPTIVE_POLLING, DEFAULT_ADAPTIVE_POLLING)
        ),
        "active_features": get_entry_value(
            entry,
            CONF_ACTIVE_FEATURES,
            [],
        ),
    }


def _clamped_setting(
    entry: ConfigEntry,
    key: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    """Return a numeric entry setting clamped into its supported range.

    Falls back to ``default`` for values that are not numeric at all.
    """
    raw = get_entry_value(entry, key, default)
    try:
        value = int(float(raw))
    except (TypeError, ValueError):
        _LOGGER.warning("Invalid value for '%s': %r - using default %s", key, raw, default)
        return default

    clamped = max(minimum, min(maximum, value))
    if clamped != value:
        _LOGGER.warning(
            "Value for '%s' (%s) is outside the supported range %s-%s - using %s",
            key,
            value,
            minimum,
            maximum,
            clamped,
        )
    return clamped


def _validate_config(config: dict[str, Any]) -> bool:
    """Validate the extracted configuration.

    This function checks for the presence of required keys and ensures that numeric
    values are within their acceptable ranges.

    Args:
        config: The configuration dictionary to validate.

    Returns:
        True if the configuration is valid, False otherwise.
    """
    required_keys = ["ip_address", "device_name"]

    for key in required_keys:
        if not config.get(key):
            _LOGGER.error("Missing required configuration key: %s", key)
            return False

    # Numeric ranges use the same limits as the config/options flow. The values
    # are already clamped by _extract_config, so this only catches programming
    # errors, never a user-supplied setting.
    numeric_ranges = (
        ("polling_interval", MIN_SUPPORTED_POLLING_INTERVAL, MAX_POLLING_INTERVAL),
        ("timeout_duration", MIN_TIMEOUT, MAX_TIMEOUT),
        ("retry_attempts", MIN_RETRIES, MAX_RETRIES),
    )
    for key, minimum, maximum in numeric_ranges:
        if not minimum <= config[key] <= maximum:
            _LOGGER.error(
                "Invalid %s: %s (must be between %s and %s)",
                key,
                config[key],
                minimum,
                maximum,
            )
            return False

    _LOGGER.debug("Configuration validated successfully.")
    return True


# =============================================================================
# ZEROCONF DISCOVERY (Gold Level)
# =============================================================================


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Remove a device entry associated with a config entry.

    Called by HA when the user removes a device from the device registry.
    Returns True to allow removal; False to prevent it.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry owning the device.
        device_entry: The device entry to remove.

    Returns:
        True if the device can be removed, False otherwise.
    """
    _LOGGER.info(
        "Removing device entry '%s' from config entry '%s'",
        device_entry.name,
        config_entry.title,
    )
    # Allow removal of any device entry associated with this config entry.
    # The coordinator data will reflect the actual hardware on the next poll.
    return True


@callback
def async_zeroconf_get_service_info(
    hass: HomeAssistant,
    info: ZeroconfServiceInfo,
    service_info_type: str,
) -> None:
    """Handle ZeroConf discovery of Violet Pool Controller.

    This function is called by Home Assistant when a matching ZeroConf service
    is discovered on the network. It stores the device information for later
    use in the config flow.

    Args:
        hass: The Home Assistant instance.
        info: The ZeroConf service info.
        service_info_type: The service type.

    Returns:
        None. Device info is stored for later retrieval by the config flow.
    """
    from .discovery import get_discovery_handler

    _LOGGER.info("ZeroConf discovery triggered for %s", info.name)

    # Get discovery handler and store the device info
    handler = get_discovery_handler()
    handler.async_discover_service(hass, info)

    # Note: No return value needed. Home Assistant will automatically
    # show discovered devices in the UI and start the config flow when
    # the user clicks "Configure".
