"""Tests for error codes database and lookup."""

from unittest.mock import MagicMock

from custom_components.violet_pool_controller.error_codes import (
    get_error_entry,
    get_error_info,
)
from custom_components.violet_pool_controller.sensor_modules.specialized import (
    VioletHealthSensor,
)


def test_error_code_lookup_zero_padded_and_unpadded():
    """Ensure both unpadded and zero-padded error codes resolve correctly."""
    # Code 2 / 0002
    info_2 = get_error_info("2")
    info_0002 = get_error_info("0002")
    assert info_2["type"] == "ALERT"
    assert info_0002["type"] == "ALERT"
    assert info_2["subject"] == info_0002["subject"]

    # Code 10 / 0010
    info_10 = get_error_info("10")
    info_0010 = get_error_info("0010")
    assert info_10["type"] == "REMINDER"
    assert info_0010["type"] == "REMINDER"

    # Code 120 / 0120
    info_120 = get_error_info("120")
    info_0120 = get_error_info("0120")
    assert info_120["type"] == "WARNING"
    assert info_0120["type"] == "WARNING"

    # Non-digit code
    info_a1 = get_error_info("A1")
    assert info_a1["type"] == "WARNING"

    # Unknown code
    info_unknown = get_error_info("99999")
    assert info_unknown["type"] == "UNKNOWN"
    assert "99999" in info_unknown["subject"]


def test_get_error_entry():
    """Test get_error_entry with padded and unpadded strings."""
    entry_2 = get_error_entry("2")
    entry_0002 = get_error_entry("0002")
    assert entry_2 is not None
    assert entry_0002 is not None
    assert entry_2.code == entry_0002.code

    assert get_error_entry(None) is None
    assert get_error_entry("non_existent_code") is None


def test_violet_health_sensor_active_errors():
    """Test VioletHealthSensor correctly checks active errors and ignores last_error_id counter."""
    coordinator = MagicMock()
    coordinator.data = {
        "last_error_id": 904,  # Notification row counter, not an error code!
        "ERROR": "0",
        "LAST_ERROR": "0",
    }
    coordinator.last_update_success = True
    config_entry = MagicMock()

    sensor = VioletHealthSensor(coordinator, config_entry)
    errors, warnings, info = sensor._collect_problems()

    # last_error_id 904 should not trigger an error/notice
    assert errors == []
    assert warnings == []
    assert info == []
    assert sensor.native_value == "ok"

    # Now add an actual active error code
    coordinator.data = {
        "last_error_id": 904,
        "ERROR": "0002",  # Hardware problem
    }
    errors, warnings, info = sensor._collect_problems()
    assert len(errors) == 1
    assert "0002" in errors[0]
    assert sensor.native_value == "error"

    # Now add an active warning code
    coordinator.data = {
        "last_error_id": 904,
        "ERROR": "0120",  # Chlorine dosing ORP limit
    }
    errors, warnings, info = sensor._collect_problems()
    assert errors == []
    assert len(warnings) == 1
    assert "0120" in warnings[0]
    assert sensor.native_value == "warning"
