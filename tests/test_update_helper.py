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
    firmware_info = parse_firmware_info({"SW_VERSION": "1.1.9", "SW_UPDATE_AVAILABLE": "1.2.0"})

    assert firmware_info.installed_version == "1.1.9"
    assert firmware_info.available_version == "1.2.0"
    assert firmware_info.update_available is True


def test_parse_firmware_info_legacy_sw_version_carrier() -> None:
    """SW_VERSION_CARRIER is read when SYSTEM_carrierboard_swversion is absent."""
    firmware_info = parse_firmware_info({"SW_VERSION": "1.2.0", "SW_VERSION_CARRIER": "2.3.0"})

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


def test_update_available_for_a_prerelease_installed_version() -> None:
    """A suffixed version must not hide the update.

    The comparison used ``int()`` on each dot-separated part, so "1.2.0-beta"
    raised ValueError and the helper reported "equal" - which meant a
    controller running a beta never saw the stable release that followed it.
    """
    firmware_info = parse_firmware_info(
        {"SYSTEM_swversion": "1.2.0-beta", "SYSTEM_availableversion": "1.2.0"}
    )

    assert firmware_info.update_available is True


def test_no_update_when_the_prerelease_is_the_newer_one() -> None:
    """A beta ahead of the installed stable release is still an update."""
    firmware_info = parse_firmware_info(
        {"SYSTEM_swversion": "1.2.0", "SYSTEM_availableversion": "1.2.0-beta"}
    )

    assert firmware_info.update_available is False


def test_multi_digit_version_parts_are_ordered_numerically() -> None:
    """1.10.0 is newer than 1.9.0, not older."""
    firmware_info = parse_firmware_info(
        {"SYSTEM_swversion": "1.9.0", "SYSTEM_availableversion": "1.10.0"}
    )

    assert firmware_info.update_available is True


def test_unorderable_versions_are_reported_as_an_update() -> None:
    """The controller only advertises a version when it has one to offer."""
    firmware_info = parse_firmware_info(
        {"SYSTEM_swversion": "custom-build", "SYSTEM_availableversion": "factory"}
    )

    assert firmware_info.update_available is True
