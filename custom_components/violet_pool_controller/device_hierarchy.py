# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Grouping of the controller's entities into sub-devices.

A Violet Pool Controller reports several hundred values. Presenting all of them
under a single device makes the device page unusable, so the entities are split
across a small set of sub-devices — one per functional block — that hang below
the controller in Home Assistant's device hierarchy.

The groups deliberately mirror the features users enable and disable in the
config flow (``AVAILABLE_FEATURES``), so the structure they see on the device
page is the structure they configured.

Two Home Assistant details shape this module:

* **Parent links.** ``DeviceInfo.via_device`` (an identifier tuple) is
  deprecated since Home Assistant 2026.8 in favour of ``via_device_id`` (the
  parent's registry id), and passing both raises. The integration supports
  Home Assistant from 2026.1, where ``via_device_id`` does not exist yet, so
  the field is chosen at runtime.
* **Entity ids.** With ``has_entity_name`` the entity id is derived from the
  *device* an entity belongs to, so moving entities onto sub-devices would turn
  ``sensor.violet_pool_controller_pump_runtime`` into
  ``sensor.filterpumpe_pump_runtime`` for newly created entities. Entity ids are
  therefore pinned to the controller name in :mod:`.entity` instead, which keeps
  shared dashboards working. Only the grouping changes, never an entity id.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_GROUP_ENTITIES, DEFAULT_GROUP_ENTITIES, DOMAIN, MANUFACTURER
from .runtime_data import get_runtime_data

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Home Assistant 2026.8 replaced the deprecated via_device identifier tuple with
# via_device_id. Detect once; the integration supports both releases.
_SUPPORTS_VIA_DEVICE_ID = "via_device_id" in DeviceInfo.__annotations__



@dataclass(frozen=True)
class SubDevice:
    """One functional block of the controller."""

    id: str
    name: str
    model: str

    @property
    def translation_key(self) -> str:
        """Return the translation key for the device name."""
        return self.id


# Order defines the order devices are pre-created in; it has no further meaning.
SUB_DEVICES: tuple[SubDevice, ...] = (
    SubDevice("filter_pump", "Filter Pump", "Circulation"),
    SubDevice("heating", "Heating", "Climate"),
    SubDevice("solar", "Solar Absorber", "Climate"),
    SubDevice("dosing", "Dosing & Water Chemistry", "Water Treatment"),
    SubDevice("lighting", "Lighting & DMX", "Lighting"),
    SubDevice("cover", "Pool Cover", "Cover"),
    SubDevice("backwash", "Backwash", "Water Treatment"),
    SubDevice("water_refill", "Water Refill", "Water Management"),
    SubDevice("pv_surplus", "PV Surplus", "Energy"),
    SubDevice("digital_io", "Digital Inputs & Rules", "I/O"),
    SubDevice("extensions", "Extension Modules", "I/O"),
    SubDevice("system", "System & Diagnostics", "Diagnostics"),
)

SUB_DEVICES_BY_ID: dict[str, SubDevice] = {device.id: device for device in SUB_DEVICES}

# Feature ids (as used by AVAILABLE_FEATURES and the *_FEATURE_MAP tables) that
# map onto a sub-device. Several dosing features share one device on purpose:
# splitting pH-, pH+, chlorine and flocculant apart produces more devices than
# it produces clarity.
_FEATURE_TO_GROUP: dict[str, str] = {
    "filter_control": "filter_pump",
    "heating": "heating",
    "solar": "solar",
    "ph_control": "dosing",
    "chlorine_control": "dosing",
    "flocculation": "dosing",
    "led_lighting": "lighting",
    "cover_control": "cover",
    "backwash": "backwash",
    "water_refill": "water_refill",
    "water_level": "water_refill",
    "pv_surplus": "pv_surplus",
    "digital_inputs": "digital_io",
    "extension_outputs": "extensions",
}

# Matched in order against the raw controller key. The controller's key space is
# far larger than the curated constant tables (a device reports ~400 values), so
# prefix rules carry most of the mapping and the feature tables act as a
# fallback for the curated entities.
_KEY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # --- Filter pump ---
    (re.compile(r"^PUMP(_|$)|^pump_|^FILTER|^filter_"), "filter_pump"),
    # --- Heating / solar ---
    (re.compile(r"^HEATER"), "heating"),
    (re.compile(r"^SOLAR"), "solar"),
    # --- Dosing and water chemistry ---
    (re.compile(r"^DOS[_\d]|^DOSAGE_|^pH_|^orp_|^pot_|^redox|^CHLOR", re.IGNORECASE), "dosing"),
    # --- Lighting ---
    (re.compile(r"^LIGHT|^DMX_"), "lighting"),
    # --- Cover ---
    (re.compile(r"^COVER"), "cover"),
    # --- Backwash ---
    (re.compile(r"^BACKWASH|^RINSE"), "backwash"),
    # --- Refill / water level ---
    (re.compile(r"^REFILL|^WATERLEVEL|^WATER_LEVEL", re.IGNORECASE), "water_refill"),
    # --- PV surplus ---
    (re.compile(r"^PVSURPLUS"), "pv_surplus"),
    # --- Extension relays (before the digital I/O catch-all) ---
    (re.compile(r"^EXT\d_"), "extensions"),
    # --- Digital inputs, switching rules, analog/impulse inputs ---
    (
        re.compile(
            r"^INPUT|^DI\d|^DIRULE_|^DIGITALINPUT|^SWITCHINGRULE|"
            r"^ANALOGRULE_|^TEMPRULE_|^ADC\d|^adc\d|^IMP\d|^imp\d"
        ),
        "digital_io",
    ),
    # --- System / diagnostics ---
    (
        re.compile(
            r"^CPU_|^SYSTEM_|^SW_|^HW_|^FW$|^fw$|^SERIAL|^serial|^RULE_|"
            r"^time|^date|^BUILD|^VERSION|^LAST_ERROR|^ERROR_|^RESET|^BLOCKING",
            re.IGNORECASE,
        ),
        "system",
    ),
)

# Entities the integration synthesises itself rather than reading from the
# controller. They describe the connection, not the pool, so they belong to the
# diagnostics device.
_SYNTHETIC_SYSTEM_KEYS = frozenset(
    {
        "system_health",
        "connection_latency",
        "last_event_age",
        "api_request_rate",
        "average_latency",
        "active_errors",
        "pool_health",
        "firmware_update",
        "reset_blocking",
    }
)

# Temperature probes are only meaningful together with the circuit they measure.
_ONEWIRE_GROUPS: dict[str, str] = {
    "onewire3_value": "solar",
    "onewire4_value": "solar",
    "onewire5_value": "heating",
    "onewire6_value": "heating",
}


@callback
def is_grouping_enabled(entry: ConfigEntry) -> bool:
    """Return whether entities should be split across sub-devices."""
    return bool(
        entry.options.get(
            CONF_GROUP_ENTITIES,
            entry.data.get(CONF_GROUP_ENTITIES, DEFAULT_GROUP_ENTITIES),
        )
    )


@callback
def resolve_group(key: str) -> str | None:
    """Return the sub-device id for a controller key, or None for the main device.

    Args:
        key: The raw controller key (or synthetic entity key) of an entity.

    Returns:
        The id of the owning sub-device, or ``None`` when the entity has no
        obvious home and should stay on the controller device itself.
    """
    if not key:
        return None

    if key in _SYNTHETIC_SYSTEM_KEYS:
        return "system"

    if (group := _ONEWIRE_GROUPS.get(key)) is not None:
        return group

    for pattern, group in _KEY_PATTERNS:
        if pattern.search(key):
            return group

    # Fall back to the curated feature tables for keys the patterns don't cover.
    from .const import SENSOR_FEATURE_MAP

    feature = SENSOR_FEATURE_MAP.get(key)
    if feature and (group := _FEATURE_TO_GROUP.get(feature)):
        return group

    return None


@callback
def group_for_feature(feature_id: str | None) -> str | None:
    """Return the sub-device id belonging to a feature id, if any."""
    if not feature_id:
        return None
    return _FEATURE_TO_GROUP.get(feature_id)


@callback
def main_device_identifier(coordinator) -> tuple[str, str]:
    """Return the identifier of the controller device itself."""
    return DOMAIN, f"{coordinator.device.api_url}_{coordinator.device.device_id}"


@callback
def sub_device_identifier(entry: ConfigEntry, group: str) -> tuple[str, str]:
    """Return the stable identifier of one sub-device."""
    return DOMAIN, f"{entry.entry_id}_group_{group}"


def _main_identifiers(coordinator) -> set[tuple[str, str]]:
    """Return the controller device's identifiers, or an empty set."""
    try:
        identifiers = coordinator.device.device_info.get("identifiers")
    except (AttributeError, TypeError):
        return set()
    if not identifiers or not isinstance(identifiers, (set, frozenset)):
        return set()
    return set(identifiers)


@callback
def async_precreate_devices(hass: HomeAssistant, entry: ConfigEntry, coordinator) -> None:
    """Create the controller device and every sub-device up front.

    Platforms are set up in an unspecified order, so the first entity added may
    well belong to a sub-device whose parent does not exist yet. Creating all of
    them here — and caching their registry ids — guarantees that every parent
    link resolves, whichever platform happens to run first.
    """
    runtime_data = get_runtime_data(entry)
    if not is_grouping_enabled(entry):
        if runtime_data is not None:
            runtime_data.device_ids.clear()
        return

    main_identifiers = _main_identifiers(coordinator)
    if not main_identifiers:
        _LOGGER.debug(
            "Controller device has no identifiers yet; skipping sub-device pre-creation"
        )
        return

    registry = dr.async_get(hass)
    device_ids: dict[str, str] = {}

    # Only the identifiers are passed: the controller's name, model and firmware
    # are filled in by Home Assistant when its first entity is added.
    main_device = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers=main_identifiers,
    )
    device_ids["__main__"] = main_device.id

    for sub_device in SUB_DEVICES:
        device = registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={sub_device_identifier(entry, sub_device.id)},
        )
        device_ids[sub_device.id] = device.id

    if runtime_data is not None:
        runtime_data.device_ids = device_ids
    _LOGGER.debug(
        "Pre-created %d sub-devices for entry_id=%s",
        len(SUB_DEVICES),
        entry.entry_id,
    )


@callback
def build_device_info(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator,
    key: str,
) -> DeviceInfo:
    """Return the device an entity belongs to.

    Falls back to the controller device when grouping is disabled or the key has
    no matching group.
    """
    main_info: DeviceInfo = coordinator.device.device_info

    if not is_grouping_enabled(entry):
        return main_info

    group = resolve_group(key)
    if group is None or (sub_device := SUB_DEVICES_BY_ID.get(group)) is None:
        return main_info

    info = DeviceInfo(
        identifiers={sub_device_identifier(entry, sub_device.id)},
        name=f"{coordinator.device.controller_name} {sub_device.name}",
        manufacturer=MANUFACTURER,
        model=sub_device.model,
        translation_key=sub_device.translation_key,
    )

    runtime_data = get_runtime_data(entry)
    device_ids: dict[str, str] = runtime_data.device_ids if runtime_data else {}
    if _SUPPORTS_VIA_DEVICE_ID:
        # Home Assistant 2026.8+: identifiers are no longer unique across config
        # entries, so the parent has to be addressed by its registry id. Passing
        # both via_device and via_device_id raises, so only ever set one.
        if (parent_id := device_ids.get("__main__")) is not None:
            # Not in the DeviceInfo TypedDict before Home Assistant 2026.8; the
            # guard above is exactly the runtime check for its availability.
            info["via_device_id"] = parent_id  # type: ignore[typeddict-unknown-key]
    elif identifiers := _main_identifiers(coordinator):
        info["via_device"] = next(iter(identifiers))

    return info


@callback
def async_cleanup_sub_devices(hass: HomeAssistant, entry: ConfigEntry) -> int:
    """Drop sub-devices that ended up without entities.

    A controller without a DMX module never produces lighting entities, so its
    pre-created "Lighting & DMX" device would otherwise linger as an empty
    entry. Also removes every sub-device when grouping is switched off.

    Returns:
        The number of removed devices.
    """
    from homeassistant.helpers import entity_registry as er

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    grouping = is_grouping_enabled(entry)
    prefix = f"{entry.entry_id}_group_"
    removed = 0

    for device in dr.async_entries_for_config_entry(device_registry, entry.entry_id):
        is_sub_device = any(
            domain == DOMAIN and value.startswith(prefix) for domain, value in device.identifiers
        )
        if not is_sub_device:
            continue

        if grouping and er.async_entries_for_device(
            entity_registry, device.id, include_disabled_entities=True
        ):
            continue

        device_registry.async_remove_device(device.id)
        removed += 1

    if removed:
        _LOGGER.debug(
            "Removed %d empty sub-device(s) for entry_id=%s",
            removed,
            entry.entry_id,
        )

    return removed


@callback
def discard_device_ids(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Drop the cached registry ids of a config entry.

    Home Assistant deletes ``runtime_data`` on unload, so this is only needed
    when the cache has to be reset while the entry stays loaded.
    """
    runtime_data = get_runtime_data(entry)
    if runtime_data is not None:
        runtime_data.device_ids.clear()
