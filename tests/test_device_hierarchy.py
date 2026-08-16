"""Tests for grouping the controller's entities into sub-devices.

A controller reports several hundred values; listing them all under one device
makes the device page unusable. The entities are therefore split across
sub-devices that hang below the controller.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from custom_components.violet_pool_controller.const import (  # noqa: E402
    CONF_API_URL,
    CONF_DEVICE_NAME,
    CONF_GROUP_ENTITIES,
    DOMAIN,
)
from custom_components.violet_pool_controller.device_hierarchy import (  # noqa: E402
    SUB_DEVICES,
    async_cleanup_sub_devices,
    async_precreate_devices,
    build_device_info,
    is_grouping_enabled,
    resolve_group,
    sub_device_identifier,
)

_MAIN_IDENTIFIER = (DOMAIN, "192.168.178.55_1")


@pytest.fixture
def config_entry(hass):
    """Add a config entry with grouping enabled."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={CONF_API_URL: "192.168.178.55", CONF_DEVICE_NAME: "Test Pool Controller"},
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def coordinator():
    """Return a coordinator stub exposing the controller device info."""
    coord = MagicMock()
    coord.device.controller_name = "Violet Pool Controller"
    coord.device.api_url = "192.168.178.55"
    coord.device.device_id = 1
    coord.device.device_info = {
        "identifiers": {_MAIN_IDENTIFIER},
        "name": "Violet Pool Controller",
    }
    return coord


class TestGroupResolution:
    """Test which sub-device a controller key lands on."""

    @pytest.mark.parametrize(
        "key,expected",
        [
            # Filter pump
            ("PUMP", "filter_pump"),
            ("PUMP_RUNTIME", "filter_pump"),
            ("pump_rs485_pwr", "filter_pump"),
            # Heating / solar, including the probes wired to each circuit
            ("HEATER", "heating"),
            ("HEATERSTATE", "heating"),
            ("onewire5_value", "heating"),
            ("SOLAR_RUNTIME", "solar"),
            ("onewire3_value", "solar"),
            # Dosing and water chemistry share one device
            ("DOS_1_CL", "dosing"),
            ("DOS_4_PHM_RUNTIME", "dosing"),
            ("pH_value", "dosing"),
            ("orp_value", "dosing"),
            # Lighting - the reason this feature was requested
            ("DMX_SCENE1", "lighting"),
            ("DMX_SCENE12", "lighting"),
            ("LIGHT", "lighting"),
            ("LIGHT_RUNTIME", "lighting"),
            # Remaining blocks
            ("COVER_STATE", "cover"),
            ("BACKWASH", "backwash"),
            ("REFILL", "water_refill"),
            ("PVSURPLUS", "pv_surplus"),
            ("INPUT1", "digital_io"),
            ("DIRULE_3", "digital_io"),
            ("ADC1_value", "digital_io"),
            ("EXT1_5", "extensions"),
            ("EXT2_8", "extensions"),
            ("CPU_TEMP", "system"),
            ("SYSTEM_swversion", "system"),
        ],
    )
    def test_keys_land_on_the_expected_device(self, key, expected):
        """Representative keys from every block."""
        assert resolve_group(key) == expected

    def test_extension_relays_win_over_the_digital_io_catch_all(self):
        """EXT keys must not be swallowed by the broad digital I/O pattern."""
        assert resolve_group("EXT1_1") == "extensions"

    def test_synthetic_entities_land_in_diagnostics(self):
        """Entities describing the connection, not the pool."""
        for key in ("system_health", "connection_latency", "firmware_update"):
            assert resolve_group(key) == "system"

    def test_unknown_keys_stay_on_the_controller(self):
        """Anything unrecognised keeps its old place rather than being guessed."""
        assert resolve_group("SOMETHING_COMPLETELY_NEW") is None
        assert resolve_group("") is None

    def test_every_group_id_has_a_device(self):
        """Guard against a mapping pointing at a device that does not exist."""
        known = {device.id for device in SUB_DEVICES}
        for key in ("PUMP", "DMX_SCENE1", "EXT1_1", "CPU_TEMP", "COVER_STATE"):
            assert resolve_group(key) in known


class TestDeviceInfo:
    """Test the DeviceInfo handed to entities."""

    def test_entity_is_placed_on_its_sub_device(self, hass, config_entry, coordinator):
        """A DMX scene belongs to the lighting device, not the controller."""
        async_precreate_devices(hass, config_entry, coordinator)
        info = build_device_info(hass, config_entry, coordinator, "DMX_SCENE1")

        assert info["identifiers"] == {sub_device_identifier(config_entry, "lighting")}
        assert "Lighting" in info["name"]

    def test_sub_device_links_to_the_controller(self, hass, config_entry, coordinator):
        """The sub-device must hang below the controller, not float free."""
        async_precreate_devices(hass, config_entry, coordinator)
        info = build_device_info(hass, config_entry, coordinator, "PUMP")

        # via_device_id on HA 2026.8+, via_device before that - exactly one.
        assert ("via_device_id" in info) != ("via_device" in info)
        if "via_device_id" in info:
            registry = dr.async_get(hass)
            assert registry.async_get(info["via_device_id"]) is not None
        else:
            assert info["via_device"] == _MAIN_IDENTIFIER

    def test_unknown_key_stays_on_the_controller(self, hass, config_entry, coordinator):
        """Ungrouped entities keep the controller device."""
        async_precreate_devices(hass, config_entry, coordinator)
        info = build_device_info(hass, config_entry, coordinator, "SOMETHING_NEW")

        assert info["identifiers"] == {_MAIN_IDENTIFIER}

    def test_grouping_can_be_switched_off(self, hass, config_entry, coordinator):
        """With the option off every entity stays on the controller."""
        hass.config_entries.async_update_entry(
            config_entry, options={CONF_GROUP_ENTITIES: False}
        )
        assert is_grouping_enabled(config_entry) is False

        info = build_device_info(hass, config_entry, coordinator, "DMX_SCENE1")
        assert info["identifiers"] == {_MAIN_IDENTIFIER}

    def test_grouping_is_on_by_default(self, config_entry):
        """Without an explicit option the hierarchy is active."""
        assert is_grouping_enabled(config_entry) is True


class TestPrecreateAndCleanup:
    """Test device pre-creation and removal of empty sub-devices."""

    def test_all_sub_devices_are_created_up_front(self, hass, config_entry, coordinator):
        """Platform order must not decide whether a parent link resolves."""
        async_precreate_devices(hass, config_entry, coordinator)

        registry = dr.async_get(hass)
        for sub_device in SUB_DEVICES:
            identifier = sub_device_identifier(config_entry, sub_device.id)
            assert registry.async_get_device(identifiers={identifier}) is not None

    def test_empty_sub_devices_are_removed(self, hass, config_entry, coordinator):
        """A controller without a DMX module must not keep a lighting device."""
        async_precreate_devices(hass, config_entry, coordinator)

        # Give exactly one sub-device an entity.
        registry = dr.async_get(hass)
        pump_device = registry.async_get_device(
            identifiers={sub_device_identifier(config_entry, "filter_pump")}
        )
        er.async_get(hass).async_get_or_create(
            "sensor",
            DOMAIN,
            f"{config_entry.entry_id}_PUMP",
            config_entry=config_entry,
            device_id=pump_device.id,
        )

        removed = async_cleanup_sub_devices(hass, config_entry)

        assert removed == len(SUB_DEVICES) - 1
        assert (
            registry.async_get_device(
                identifiers={sub_device_identifier(config_entry, "filter_pump")}
            )
            is not None
        )
        assert (
            registry.async_get_device(
                identifiers={sub_device_identifier(config_entry, "lighting")}
            )
            is None
        )

    def test_the_controller_device_is_never_removed(self, hass, config_entry, coordinator):
        """Cleanup must only ever touch sub-devices."""
        async_precreate_devices(hass, config_entry, coordinator)
        async_cleanup_sub_devices(hass, config_entry)

        registry = dr.async_get(hass)
        assert registry.async_get_device(identifiers={_MAIN_IDENTIFIER}) is not None

    def test_switching_grouping_off_removes_every_sub_device(
        self, hass, config_entry, coordinator
    ):
        """Turning the option off must leave no orphaned sub-devices behind."""
        async_precreate_devices(hass, config_entry, coordinator)
        hass.config_entries.async_update_entry(
            config_entry, options={CONF_GROUP_ENTITIES: False}
        )

        removed = async_cleanup_sub_devices(hass, config_entry)

        assert removed == len(SUB_DEVICES)
        registry = dr.async_get(hass)
        assert registry.async_get_device(identifiers={_MAIN_IDENTIFIER}) is not None
