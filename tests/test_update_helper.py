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
