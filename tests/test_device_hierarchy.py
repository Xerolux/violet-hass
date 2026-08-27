"""Tests for grouping the controller's entities into sub-devices.

A controller reports several hundred values; listing them all under one device
makes the device page unusable. The entities are therefore split across
sub-devices that hang below the controller.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from custom_components.violet_pool_controller import device_hierarchy  # noqa: E402
from custom_components.violet_pool_controller.const import (  # noqa: E402
    CONF_API_URL,
    CONF_DEVICE_NAME,
    CONF_GROUP_ENTITIES,
    DOMAIN,
    MANUFACTURER,
)
from custom_components.violet_pool_controller.device_hierarchy import (  # noqa: E402
    SUB_DEVICES,
    _main_device_id,
    async_cleanup_sub_devices,
    async_precreate_devices,
    build_device_info,
    is_grouping_enabled,
    resolve_group,
    sub_device_identifier,
)
from custom_components.violet_pool_controller.runtime_data import (  # noqa: E402
    VioletRuntimeData,
)

_MAIN_IDENTIFIER = (DOMAIN, "192.168.178.55_1")


def _device_by_identifier(hass, entry, identifier):
    """Look up a device or child device by one identifier, scoped to its entry.

    Identifiers are unique per config entry since Home Assistant 2026.8. From
    2026.9 the sub-devices are child devices, which the main-device lookup does
    not return, so both collections are searched.
    """
    registry = dr.async_get(hass)
    if device := registry.async_get_device_by_identifier(identifier, entry.entry_id):
        return device
    if device_hierarchy._SUPPORTS_CHILD_DEVICES:
        return registry.async_get_child_device_by_identifier(identifier, entry.entry_id)
    return None


@pytest.fixture
def config_entry(hass):
    """Add a config entry with grouping enabled."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={CONF_API_URL: "192.168.178.55", CONF_DEVICE_NAME: "Test Pool Controller"},
    )
    entry.add_to_hass(hass)
    entry.runtime_data = VioletRuntimeData(coordinator=MagicMock())
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

        parent_key = (
            "parent_device_id" if device_hierarchy._SUPPORTS_CHILD_DEVICES else "via_device_id"
        )
        assert dr.async_get(hass).async_get(info[parent_key]) is not None
        # The deprecated identifier-tuple link is never written any more.
        assert "via_device" not in info

    def test_a_child_device_carries_no_hardware_identity(
        self, hass, config_entry, coordinator
    ):
        """A child device is a logical part; the hardware belongs to the parent.

        Before Home Assistant 2026.9 the sub-device is a device of its own and
        does carry manufacturer and model, so the two models are asserted apart.
        """
        async_precreate_devices(hass, config_entry, coordinator)
        info = build_device_info(hass, config_entry, coordinator, "PUMP")

        if device_hierarchy._SUPPORTS_CHILD_DEVICES:
            assert "manufacturer" not in info
            assert "model" not in info
            assert "via_device_id" not in info
            assert info["parent_device_id"]
        else:
            assert info["manufacturer"] == MANUFACTURER
            assert info["model"]
            assert "parent_device_id" not in info

    def test_parent_link_resolves_without_the_cache(self, hass, config_entry, coordinator):
        """The cached registry ids are an optimisation, not a requirement."""
        async_precreate_devices(hass, config_entry, coordinator)
        # Simulate a lookup before/without the pre-creation cache.
        config_entry.runtime_data.device_ids.clear()

        assert _main_device_id(hass, config_entry, coordinator) is not None

        info = build_device_info(hass, config_entry, coordinator, "PUMP")
        parent_key = (
            "parent_device_id" if device_hierarchy._SUPPORTS_CHILD_DEVICES else "via_device_id"
        )
        assert dr.async_get(hass).async_get(info[parent_key]) is not None

    def test_an_entity_stays_on_the_controller_without_a_parent(
        self, hass, config_entry, coordinator
    ):
        """A child device needs a registered parent; without one there is none.

        The controller device is normally created by async_precreate_devices, so
        this only happens if an entity is added before it - and then the entity
        belongs on the controller rather than on a device that cannot exist.
        """
        with patch.object(device_hierarchy, "_main_device_id", return_value=None):
            info = build_device_info(hass, config_entry, coordinator, "PUMP")

        if device_hierarchy._SUPPORTS_CHILD_DEVICES:
            assert info["identifiers"] == {_MAIN_IDENTIFIER}
        else:
            assert info["identifiers"] == {sub_device_identifier(config_entry, "filter_pump")}
            assert "via_device_id" not in info

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

        for sub_device in SUB_DEVICES:
            identifier = sub_device_identifier(config_entry, sub_device.id)
            assert _device_by_identifier(hass, config_entry, identifier) is not None

    def test_an_existing_sub_device_is_converted_in_place(
        self, hass, config_entry, coordinator
    ):
        """Upgrading to Home Assistant 2026.9 must not renumber a single device.

        An installation set up before 2026.9 has its sub-devices registered as
        full devices linked by via_device_id. Pre-creation turns them into child
        devices, and their registry ids have to survive that: the ids are what
        entities are attached to and what device-targeted automations name.
        """
        if not device_hierarchy._SUPPORTS_CHILD_DEVICES:
            pytest.skip("Child devices require Home Assistant 2026.9 or newer")

        registry = dr.async_get(hass)
        main = registry.async_get_or_create(
            config_entry_id=config_entry.entry_id, identifiers={_MAIN_IDENTIFIER}
        )
        # The pre-2026.9 shape: a device of its own, hanging off the controller.
        legacy = registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={sub_device_identifier(config_entry, "filter_pump")},
            manufacturer=MANUFACTURER,
            model="Circulation",
            via_device_id=main.id,
        )
        entity = er.async_get(hass).async_get_or_create(
            "sensor",
            DOMAIN,
            f"{config_entry.entry_id}_PUMP",
            config_entry=config_entry,
            device_id=legacy.id,
        )
        # Home Assistant refuses to convert a device that the same config entry
        # registered as a full device during the current load. A real upgrade
        # restores those devices from storage instead, so drop the live set to
        # reproduce the state a restart leaves behind.
        registry.async_config_entry_unloaded(config_entry.entry_id)

        async_precreate_devices(hass, config_entry, coordinator)

        child = registry.async_get_child_device_by_identifier(
            sub_device_identifier(config_entry, "filter_pump"), config_entry.entry_id
        )
        assert child is not None
        assert child.id == legacy.id
        assert child.parent_device_id == main.id
        # The entity followed its device rather than being orphaned.
        assert er.async_get(hass).async_get(entity.entity_id).device_id == legacy.id

    def test_empty_sub_devices_are_removed(self, hass, config_entry, coordinator):
        """A controller without a DMX module must not keep a lighting device."""
        async_precreate_devices(hass, config_entry, coordinator)

        # Give exactly one sub-device an entity.
        pump_device = _device_by_identifier(
            hass, config_entry, sub_device_identifier(config_entry, "filter_pump")
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
            _device_by_identifier(
                hass, config_entry, sub_device_identifier(config_entry, "filter_pump")
            )
            is not None
        )
        assert (
            _device_by_identifier(
                hass, config_entry, sub_device_identifier(config_entry, "lighting")
            )
            is None
        )

    def test_the_controller_device_is_never_removed(self, hass, config_entry, coordinator):
        """Cleanup must only ever touch sub-devices."""
        async_precreate_devices(hass, config_entry, coordinator)
        async_cleanup_sub_devices(hass, config_entry)

        assert _device_by_identifier(hass, config_entry, _MAIN_IDENTIFIER) is not None

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
        assert _device_by_identifier(hass, config_entry, _MAIN_IDENTIFIER) is not None
