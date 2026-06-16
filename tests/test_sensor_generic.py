"""Tests for generic sensor modules."""
import logging
from unittest.mock import MagicMock

from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass

from custom_components.violet_pool_controller.const_sensors import ONEWIRE_ROMCODE_SENSORS
from custom_components.violet_pool_controller.sensor import _create_standard_sensors
from custom_components.violet_pool_controller.sensor_modules import (
    _build_sensor_description,
    should_skip_sensor,
)
from custom_components.violet_pool_controller.sensor_modules.generic import VioletSensor


def test_violet_sensor_state_class_log_spam(caplog):
    """Test that retrieving state_class for contact sensor does not spam logs."""

    # Mock coordinator
    coordinator = MagicMock()
    coordinator.data = {}
    coordinator.device.available = True
    coordinator.last_update_success = True
    # device_info is needed by Entity
    coordinator.device.device_info = {}

    # Mock config entry
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry_id"
    config_entry.options.get.return_value = False # FORCE_UPDATE default
    config_entry.data.get.return_value = False # fallback

    # Create description for a contact sensor
    description = SensorEntityDescription(
        key="CLOSE_CONTACT",
        name="Close Contact",
        state_class=None,
        translation_key=None
    )

    # Instantiate sensor
    sensor = VioletSensor(coordinator, config_entry, description)
    # Manually add hass to entity (usually done by add_entities)
    # Check logs
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        _ = sensor.state_class

    log_messages = [r.message for r in caplog.records]
    log_present = any("Overriding state_class to None for contact sensor: CLOSE_CONTACT" in msg for msg in log_messages)

    assert not log_present, "Log spam should be gone when state_class is already None"

    # Verify safeguard still works
    description_bad = SensorEntityDescription(
        key="CLOSE_CONTACT_BAD",
        name="Close Contact Bad",
        state_class=SensorStateClass.MEASUREMENT,
        translation_key=None
    )
    sensor_bad = VioletSensor(coordinator, config_entry, description_bad)

    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        _ = sensor_bad.state_class

    log_messages_bad = [r.message for r in caplog.records]
    log_present_bad = any("Overriding state_class to None for contact sensor: CLOSE_CONTACT_BAD" in msg for msg in log_messages_bad)

    assert log_present_bad, "Log should appear when safeguard overrides an incorrect state_class"


def test_onewire_rcode_sensor_keeps_text_value():
    """OneWire ROM-code sensors must stay as text without a temperature unit."""

    coordinator = MagicMock()
    coordinator.data = {"onewire1_rcode": "28121883321901A9"}
    coordinator.device.available = True
    coordinator.last_update_success = True
    coordinator.device.device_info = {}

    config_entry = MagicMock()
    config_entry.entry_id = "test_entry_id"
    config_entry.options.get.return_value = False
    config_entry.data.get.return_value = False

    assert not should_skip_sensor("onewire1_rcode", coordinator.data["onewire1_rcode"])

    description = _build_sensor_description(
        "onewire1_rcode",
        coordinator.data["onewire1_rcode"],
        ONEWIRE_ROMCODE_SENSORS,
        translation_key="onewire1_rcode",
    )
    assert description.native_unit_of_measurement is None
    assert description.device_class is None
    assert description.state_class is None

    sensor = VioletSensor(coordinator, config_entry, description)
    assert sensor.native_value == "28121883321901A9"


def test_onewire_rcode_sensor_uses_explicit_name_without_translation():
    """OneWire ROM-code sensors should rely on their explicit name, not missing translations."""

    coordinator = MagicMock()
    coordinator.data = {"onewire1_rcode": "28121883321901A9"}
    coordinator.device.available = True
    coordinator.last_update_success = True
    coordinator.device.device_info = {}
    coordinator.device.device_name = "Violet Pool Controller"
    coordinator.device.controller_name = "Violet Pool Controller"

    config_entry = MagicMock()
    config_entry.entry_id = "test_entry_id"
    config_entry.title = "Test Pool"
    config_entry.options.get.side_effect = lambda key, default=None: default
    config_entry.data.get.side_effect = lambda key, default=None: default

    sensors = _create_standard_sensors(
        coordinator,
        config_entry,
        {
            "active_features": set(),
            "selected_sensors": set(),
            "create_all": True,
        },
        handled_keys=set(),
    )

    rom_sensor = next(
        sensor for sensor in sensors if sensor.entity_description.key == "onewire1_rcode"
    )
    assert rom_sensor.entity_description.translation_key is None
    assert getattr(rom_sensor, "_attr_name", None) == "OneWire-ROM-Code 1"
