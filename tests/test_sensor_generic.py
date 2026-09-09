"""Tests for generic sensor modules."""

import logging
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)

from custom_components.violet_pool_controller.const_sensors import ONEWIRE_ROMCODE_SENSORS
from custom_components.violet_pool_controller.sensor import _create_standard_sensors
from custom_components.violet_pool_controller.sensor_modules import (
    _build_sensor_description,
    generic,
    should_skip_sensor,
)
from custom_components.violet_pool_controller.sensor_modules.energy import (
    VioletPumpPowerSensor,
)
from custom_components.violet_pool_controller.sensor_modules.generic import (
    VioletSensor,
    VioletStatusSensor,
)


def _make_generic_sensor(key: str, data: dict) -> VioletSensor:
    """Build a generic sensor on top of a mocked coordinator."""
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.device.available = True
    coordinator.last_update_success = True
    coordinator.device.device_info = {}

    config_entry = MagicMock()
    config_entry.entry_id = "test_entry_id"
    config_entry.options.get.return_value = False
    config_entry.data.get.return_value = False

    return VioletSensor(
        coordinator,
        config_entry,
        SensorEntityDescription(key=key, name=key, device_class="timestamp"),
    )


def _mock_coordinator(data: dict):
    """Return a coordinator mock carrying the given readings."""
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.device.available = True
    coordinator.last_update_success = True
    coordinator.device.device_info = {}
    return coordinator


def _mock_config_entry():
    """Return a config entry mock accepted by the base entity."""
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry_id"
    config_entry.options.get.return_value = False
    config_entry.data.get.return_value = False
    return config_entry


def _make_status_sensor(key: str, data: dict) -> VioletStatusSensor:
    """Build a status sensor on top of a mocked coordinator."""
    return VioletStatusSensor(
        _mock_coordinator(data),
        _mock_config_entry(),
        SensorEntityDescription(key=key, name=key),
    )


def _make_pump_power_sensor(data: dict) -> VioletPumpPowerSensor:
    """Build the estimated pump power sensor on a mocked coordinator."""
    return VioletPumpPowerSensor(_mock_coordinator(data), _mock_config_entry())


def _as_local_wall_epoch(value: datetime, timezone: ZoneInfo) -> float:
    """Encode a real instant the same way Violet's local-epoch fields do."""
    local = value.astimezone(timezone)
    return local.replace(tzinfo=UTC).timestamp()


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
    config_entry.options.get.return_value = False  # FORCE_UPDATE default
    config_entry.data.get.return_value = False  # fallback

    # Create description for a contact sensor
    description = SensorEntityDescription(
        key="CLOSE_CONTACT", name="Close Contact", state_class=None, translation_key=None
    )

    # Instantiate sensor
    sensor = VioletSensor(coordinator, config_entry, description)
    # Manually add hass to entity (usually done by add_entities)
    # Check logs
    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        _ = sensor.state_class

    log_messages = [r.message for r in caplog.records]
    log_present = any(
        "Overriding state_class to None for contact sensor: CLOSE_CONTACT" in msg
        for msg in log_messages
    )

    assert not log_present, "Log spam should be gone when state_class is already None"

    # Verify safeguard still works
    description_bad = SensorEntityDescription(
        key="CLOSE_CONTACT_BAD",
        name="Close Contact Bad",
        state_class=SensorStateClass.MEASUREMENT,
        translation_key=None,
    )
    sensor_bad = VioletSensor(coordinator, config_entry, description_bad)

    with caplog.at_level(logging.DEBUG):
        caplog.clear()
        _ = sensor_bad.state_class

    log_messages_bad = [r.message for r in caplog.records]
    log_present_bad = any(
        "Overriding state_class to None for contact sensor: CLOSE_CONTACT_BAD" in msg
        for msg in log_messages_bad
    )

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


def test_onewire_rcode_sensor_is_translated():
    """OneWire ROM-code sensors carry the shared translation key of their probe."""

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
    assert rom_sensor.entity_description.translation_key == "onewire1_romcode"
    # The English name stays on the description: it is what the entity_id is
    # derived from, while the displayed name comes from the translation.
    assert rom_sensor.entity_description.name == "OneWire ROM Code 1"


def test_timestamp_local_wall_epoch_is_converted_to_real_utc(monkeypatch):
    """Controller-local epoch fields must not appear two hours in the future."""
    timezone = ZoneInfo("Europe/Berlin")
    now = datetime.now(UTC).replace(microsecond=0)
    event = now - timedelta(minutes=4)
    data = {
        "CURRENT_TIME_UNIX": _as_local_wall_epoch(now, timezone),
        "DOS_1_CL_LAST_ON": _as_local_wall_epoch(event, timezone),
    }

    # Restore HA's global timezone before its cleanup fixture runs.
    with monkeypatch.context() as patch:
        patch.setattr(generic.dt_util, "DEFAULT_TIME_ZONE", timezone)
        sensor = _make_generic_sensor("DOS_1_CL_LAST_ON", data)

        assert sensor.native_value == event


def test_timestamp_real_unix_epoch_is_kept(monkeypatch):
    """Controllers that already return real Unix epochs remain compatible."""
    timezone = ZoneInfo("Europe/Berlin")
    now = datetime.now(UTC).replace(microsecond=0)
    event = now - timedelta(hours=5)
    data = {
        "CURRENT_TIME_UNIX": now.timestamp(),
        "DOS_4_PHM_LAST_OFF": event.timestamp(),
    }

    with monkeypatch.context() as patch:
        patch.setattr(generic.dt_util, "DEFAULT_TIME_ZONE", timezone)
        sensor = _make_generic_sensor("DOS_4_PHM_LAST_OFF", data)

        assert sensor.native_value == event


def test_uninitialised_future_last_event_is_unknown(monkeypatch):
    """A far-future firmware sentinel means "never", not "in 474 years"."""
    timezone = ZoneInfo("Europe/Berlin")
    now = datetime.now(UTC).replace(microsecond=0)
    future = now + timedelta(days=474 * 365)
    data = {
        "CURRENT_TIME_UNIX": _as_local_wall_epoch(now, timezone),
        "DOS_1_CL_LAST_CAN_RESET": _as_local_wall_epoch(future, timezone) * 1000,
    }

    with monkeypatch.context() as patch:
        patch.setattr(generic.dt_util, "DEFAULT_TIME_ZONE", timezone)
        sensor = _make_generic_sensor("DOS_1_CL_LAST_CAN_RESET", data)

        assert sensor.native_value is None


# ---------------------------------------------------------------------------
# Sensor classification must not depend on the value sampled at setup time
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "key",
    ["orp_value_min", "onewire7_value_min", "pH_value_max", "ADC1_value"],
)
def test_classification_is_stable_across_startup_values(key):
    """A reading that happens to be 0 or 1 must not change the sensor's identity.

    The device class, unit and icon used to be picked from the *value* present
    when the integration started, so a probe reading 0.0 got a different unit
    (and a different long-term statistics series) than the same probe reading
    25.3.
    """
    boolean_looking = _build_sensor_description(key, "0", {})
    numeric = _build_sensor_description(key, "25.3", {})

    assert boolean_looking.device_class == numeric.device_class
    assert boolean_looking.native_unit_of_measurement == numeric.native_unit_of_measurement
    assert boolean_looking.state_class == numeric.state_class
    assert boolean_looking.icon == numeric.icon


@pytest.mark.parametrize(
    "key",
    [
        "INPUT1",
        "INPUT12",
        "INPUT_CE1",
        "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_1",
        "DOS_1_CL_USE",
        "DMX_SCENE7",
    ],
)
def test_state_code_keys_are_not_measurements(key):
    """State codes are enumerations; recording them as measurements is wrong."""
    description = _build_sensor_description(key, "1", {})

    assert description.state_class is None


# ---------------------------------------------------------------------------
# Status sensors publish a stable mode key, not a German display string
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0", "auto_inactive"),
        ("1", "auto_active"),
        ("2", "auto_inactive"),
        ("3", "auto_active"),
        ("4", "manual_on"),
        ("5", "auto_inactive"),
        ("6", "manual_off"),
        ("3|PUMP_ANTI_FREEZE", "frost_protection"),
        ("PUMP_ANTI_FREEZE", "frost_protection"),
        ("ERROR", "error"),
        ("MAINTENANCE", "maintenance"),
        ("[]", "unknown"),
        ("", "unknown"),
        ("SOMETHING_NEW", "unknown"),
    ],
)
def test_status_mode_is_a_stable_english_key(raw, expected):
    """The API renders German by default and the integration never sets a language."""
    assert generic.status_mode(raw, "PUMP") == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("0", "auto_inactive"), ("1", "auto_active"), ("2", "manual_on")],
)
def test_pv_surplus_has_its_own_state_scheme(raw, expected):
    """0 = off, 1 = on via digital input, 2 = on via HTTP request."""
    assert generic.status_mode(raw, "PVSURPLUS") == expected


def test_status_sensor_declares_its_options():
    """An enum sensor must offer every value it can report."""
    sensor = _make_status_sensor("PUMP", {"PUMP": "4"})

    assert sensor.device_class == SensorDeviceClass.ENUM
    assert sensor.native_value in sensor.options
    assert sensor.state_class is None
    assert sensor.native_unit_of_measurement is None


def test_status_sensor_prefers_the_detail_state_key():
    """PUMPSTATE carries the operational mode; PUMP carries only the code."""
    sensor = _make_status_sensor("PUMP", {"PUMP": "3", "PUMPSTATE": "3|PUMP_ANTI_FREEZE"})

    assert sensor.native_value == "frost_protection"


# ---------------------------------------------------------------------------
# Estimated pump power
# ---------------------------------------------------------------------------


def test_pump_power_ignores_off_state_codes():
    """PUMP_RPM_2 = "6" is "manual off", not "speed 2 running"."""
    sensor = _make_pump_power_sensor({"PUMP_RPM_2": "6", "PUMP_RPM_1": "0"})

    assert sensor.extra_state_attributes["speed_level"] is None
    assert sensor.native_value == 0.0


def test_pump_power_reports_the_running_level():
    """A speed output reporting an on code drives the estimate."""
    sensor = _make_pump_power_sensor({"PUMP_RPM_2": "4", "PUMP_RPM_1": "0"})

    assert sensor.extra_state_attributes["speed_level"] == 2
    assert sensor.native_value == 280.0
