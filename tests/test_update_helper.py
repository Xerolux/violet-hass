"""Tests for firmware update parsing."""

from custom_components.violet_pool_controller.update_helper import parse_firmware_info


def test_parse_firmware_info_reads_correct_field_names() -> None:
    """parse_firmware_info uses the firmware's actual field names from getReadings."""
    firmware_info = parse_firmware_info(
        {"SYSTEM_swversion": "1.1.9", "SYSTEM_availableversion": "1.2.0"}
    )

    assert firmware_info.installed_version == "1.1.9"
    assert firmware_info.available_version == "1.2.0"
    assert firmware_info.update_available is True


def test_parse_firmware_info_no_available_version_when_up_to_date() -> None:
    """When availableversion equals installed version, no update is shown."""
    firmware_info = parse_firmware_info(
        {"SYSTEM_swversion": "1.2.0", "SYSTEM_availableversion": "1.2.0"}
    )

    assert firmware_info.installed_version == "1.2.0"
    assert firmware_info.available_version is None
    assert firmware_info.update_available is False


def test_parse_firmware_info_fallback_when_version_missing() -> None:
    """Controllers without version keys fall back to 0.0.0."""
    firmware_info = parse_firmware_info({})

    assert firmware_info.installed_version == "0.0.0"
    assert firmware_info.available_version is None
    assert firmware_info.update_available is False


def test_parse_firmware_info_empty_available_version() -> None:
    """Empty availableversion means up to date — no update shown."""
    firmware_info = parse_firmware_info(
        {"SYSTEM_swversion": "1.2.0", "SYSTEM_availableversion": ""}
    )

    assert firmware_info.available_version is None
    assert firmware_info.update_available is False


def test_parse_firmware_info_legacy_sw_version_keys() -> None:
    """Older firmware / getReadings spec uses SW_VERSION and SW_UPDATE_AVAILABLE."""
    firmware_info = parse_firmware_info(
        {"SW_VERSION": "1.1.9", "SW_UPDATE_AVAILABLE": "1.2.0"}
    )

    assert firmware_info.installed_version == "1.1.9"
    assert firmware_info.available_version == "1.2.0"
    assert firmware_info.update_available is True


def test_parse_firmware_info_legacy_sw_version_carrier() -> None:
    """SW_VERSION_CARRIER is read when SYSTEM_carrierboard_swversion is absent."""
    firmware_info = parse_firmware_info(
        {"SW_VERSION": "1.2.0", "SW_VERSION_CARRIER": "2.3.0"}
    )

    assert firmware_info.installed_version == "1.2.0"
    assert firmware_info.carrier_version == "2.3.0"


def test_parse_firmware_info_system_keys_take_precedence() -> None:
    """SYSTEM_swversion wins when both key families are present."""
    firmware_info = parse_firmware_info(
        {
            "SYSTEM_swversion": "2.0.0",
            "SW_VERSION": "1.9.9",
            "SYSTEM_availableversion": "2.1.0",
            "SW_UPDATE_AVAILABLE": "1.9.9",
        }
    )

    assert firmware_info.installed_version == "2.0.0"
    assert firmware_info.available_version == "2.1.0"
