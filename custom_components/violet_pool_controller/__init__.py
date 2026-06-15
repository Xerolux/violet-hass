# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""The Violet Pool Controller integration."""

from __future__ import annotations

import logging
from datetime import timedelta
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
from .const import (
    CONF_ACTIVE_FEATURES,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_ENABLE_DIAGNOSTIC_LOGGING,
    CONF_PASSWORD,
    CONF_POLLING_INTERVAL,
    CONF_PORT,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_CONTROLLER_NAME,
    DEFAULT_ENABLE_DIAGNOSTIC_LOGGING,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)

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

    if config_entry.version == 1:
        # Version 1 requires no migration
        _LOGGER.debug("Config entry already at version 1, no migration needed")
        return True

    # Add future migrations here
    _LOGGER.warning("Unknown config entry version: %s", config_entry.version)
    return False


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
        object_id = entity_id[dot + 1:]
        if not object_id.startswith(double_slug):
            continue

        # Collapse any number of repeated domain slugs down to one.
        new_object_id = object_id
        while new_object_id.startswith(double_slug):
            new_object_id = f"{DOMAIN}_" + new_object_id[len(double_slug):]

        new_entity_id = f"{entity_id[:dot + 1]}{new_object_id}"
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
        entry.data.get(
            CONF_CONTROLLER_NAME, entry.data.get(CONF_DEVICE_NAME, "Unknown")
        ),
    )

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

        dosing_standalone = entry.data.get(
            CONF_DOSING_STANDALONE, DEFAULT_DOSING_STANDALONE
        )

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

        # Store coordinator in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator

        # Migrate entity_ids that have the duplicate device prefix (e.g.
        # switch.violet_pool_controller_violet_pool_controller_beleuchtung →
        # switch.violet_pool_controller_beleuchtung).  Must run before
        # platforms are loaded so that the registry already contains the
        # corrected entity_ids when entities re-register themselves.
        _migrate_duplicate_prefix_entity_ids(er.async_get(hass), entry.entry_id)

        # Load platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        # Apply logging configuration
        _apply_logging_config(entry)

        # Register update listener for config changes (e.g., polling_interval)
        entry.async_on_unload(entry.add_update_listener(async_update_listener))

        # Register services (only once for the entire integration)
        from .services import async_register_services

        await async_register_services(hass)

        # Clean up sensor/binary_sensor entities whose data key is no longer
        # present in the coordinator data (e.g. hardware module removed).
        # Entity unique_ids are formatted as "{entry_id}_{key}" (see entity.py).
        if coordinator.data:
            ent_reg = er.async_get(hass)
            entities = er.async_entries_for_config_entry(ent_reg, entry.entry_id)
            static_keys = {
                "system_health",
                "connection_latency",
                "last_event_age",
                "api_request_rate",
                "average_latency",
            }

            prefix = f"{entry.entry_id}_"
            for entity in entities:
                if entity.domain in (
                    "sensor",
                    "binary_sensor",
                ) and entity.unique_id.startswith(prefix):
                    key = entity.unique_id[len(prefix) :]
                    if key not in coordinator.data and key not in static_keys:
                        _LOGGER.debug(
                            "Removing unsupported entity %s (key=%s)",
                            entity.entity_id,
                            key,
                        )
                        ent_reg.async_remove(entity.entity_id)

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
        _LOGGER.exception(
            "Unexpected error during setup (entry_id=%s): %s", entry.entry_id, err
        )
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
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

        if unload_ok:
            # Get coordinator for cleanup
            coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
            if coordinator and hasattr(coordinator.device, "api"):
                # NOTE: Do NOT close the aiohttp session - it's managed by
                # Home Assistant! The session is created by HA via
                # async_get_clientsession() and should only be closed by HA
                _LOGGER.debug(
                    "API object reference released for entry_id=%s", entry.entry_id
                )

            # Remove coordinator from hass.data
            if entry.entry_id in hass.data.get(DOMAIN, {}):
                hass.data[DOMAIN].pop(entry.entry_id)
                _LOGGER.debug("Coordinator removed for entry_id=%s", entry.entry_id)

            _LOGGER.info(
                "Successfully unloaded '%s' (entry_id=%s)", device_name, entry.entry_id
            )
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


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle config entry updates (e.g., polling_interval, timeout, retry changes).

    This function is called when the user modifies integration options.
    It updates ALL settings dynamically without requiring a reload.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry that was updated.
    """
    _LOGGER.info(
        "Config entry updated for '%s' (entry_id=%s)",
        entry.data.get(CONF_DEVICE_NAME, "Unknown"),
        entry.entry_id,
    )

    # Get coordinator
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not coordinator:
        _LOGGER.warning("Coordinator not found for entry_id=%s", entry.entry_id)
        return

    # Track if any setting was updated
    settings_updated = False

    # 1. Update polling interval if changed
    new_polling_interval = get_entry_value(
        entry,
        CONF_POLLING_INTERVAL,
        DEFAULT_POLLING_INTERVAL,
    )

    current_interval = coordinator.update_interval.total_seconds()

    if new_polling_interval != current_interval:
        _LOGGER.info(
            "Updating polling interval from %ds to %ds (entry_id=%s)",
            current_interval,
            new_polling_interval,
            entry.entry_id,
        )

        coordinator.update_interval = timedelta(seconds=new_polling_interval)

        # Force an immediate refresh so the new interval takes effect now
        await coordinator.async_request_refresh()

        _LOGGER.info(
            "Polling interval updated successfully to %ds (entry_id=%s)",
            new_polling_interval,
            entry.entry_id,
        )
        settings_updated = True
    else:
        _LOGGER.debug(
            "Polling interval unchanged at %ds (entry_id=%s)",
            new_polling_interval,
            entry.entry_id,
        )

    # 2. Update API connection settings if changed
    if hasattr(coordinator.device, "update_api_config"):
        api_updated = await coordinator.device.update_api_config(entry)
        if api_updated:
            settings_updated = True

    # 3. Apply logging configuration
    _apply_logging_config(entry)

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


def _apply_logging_config(entry: ConfigEntry) -> None:
    """Apply logging configuration based on settings.

    Args:
        entry: The config entry.
    """
    enable_diagnostic = get_entry_value(
        entry,
        CONF_ENABLE_DIAGNOSTIC_LOGGING,
        DEFAULT_ENABLE_DIAGNOSTIC_LOGGING,
    )

    logger = logging.getLogger(__package__)

    if enable_diagnostic:
        # User wants extended/diagnostic logging
        # We also enable DEBUG level for this package
        if logger.getEffectiveLevel() > logging.DEBUG:
            logger.setLevel(logging.DEBUG)
            _LOGGER.info(
                "Diagnostic logging enabled: Log level set to DEBUG for %s", __package__
            )
    else:
        # Revert to default behavior (inherit from parent)
        # Note: We can't easily 'reset' to previous state without tracking it,
        # but setting to NOTSET usually causes it to inherit from parent (root)
        if logger.level == logging.DEBUG:
            logger.setLevel(logging.NOTSET)
            _LOGGER.info(
                "Diagnostic logging disabled: Log level reset for %s", __package__
            )


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
        "controller_name": entry.data.get(
            CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME
        ),
        "polling_interval": get_entry_value(
            entry,
            CONF_POLLING_INTERVAL,
            DEFAULT_POLLING_INTERVAL,
        ),
        "timeout_duration": get_entry_value(
            entry,
            CONF_TIMEOUT_DURATION,
            DEFAULT_TIMEOUT_DURATION,
        ),
        "retry_attempts": get_entry_value(
            entry,
            CONF_RETRY_ATTEMPTS,
            DEFAULT_RETRY_ATTEMPTS,
        ),
        "active_features": get_entry_value(
            entry,
            CONF_ACTIVE_FEATURES,
            [],
        ),
    }


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

    # Validate numeric ranges
    if not 5 <= config["polling_interval"] <= 300:
        _LOGGER.error(
            "Invalid polling_interval: %s (must be between 5 and 300)",
            config["polling_interval"],
        )
        return False

    if not 5 <= config["timeout_duration"] <= 60:
        _LOGGER.error(
            "Invalid timeout_duration: %s (must be between 5 and 60)",
            config["timeout_duration"],
        )
        return False

    if not 1 <= config["retry_attempts"] <= 10:
        _LOGGER.error(
            "Invalid retry_attempts: %s (must be between 1 and 10)",
            config["retry_attempts"],
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
