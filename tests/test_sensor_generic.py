"""Tests for generic sensor modules."""
from unittest.mock import MagicMock
import logging

from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass

from custom_components.violet_pool_controller.sensor_modules.generic import VioletSensor

async def test_violet_sensor_state_class_log_spam(hass, caplog):
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
    sensor.hass = hass

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
    sensor_bad.hass = hass

    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        _ = sensor_bad.state_class

    log_messages_bad = [r.message for r in caplog.records]
    log_present_bad = any("Overriding state_class to None for contact sensor: CLOSE_CONTACT_BAD" in msg for msg in log_messages_bad)

    assert log_present_bad, "Log should appear when safeguard overrides an incorrect state_class"
