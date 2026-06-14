"""Tests for firmware update parsing."""

from custom_components.violet_pool_controller.update_helper import parse_firmware_info


def test_parse_firmware_info_uses_known_1_2_0_fallback() -> None:
    """Controllers without explicit update keys still report released 1.2.0."""
    firmware_info = parse_firmware_info({"SW_VERSION": "1.1.9"})

    assert firmware_info.installed_version == "1.1.9"
    assert firmware_info.available_version == "1.2.0"
    assert firmware_info.update_available is True


def test_parse_firmware_info_boolean_update_flag_maps_to_1_2_0() -> None:
    """Boolean update flags from the controller produce a concrete latest version."""
    firmware_info = parse_firmware_info(
        {"SW_VERSION": "1.1.9", "SW_UPDATE_AVAILABLE": True}
    )

    assert firmware_info.available_version == "1.2.0"
    assert firmware_info.update_available is True
