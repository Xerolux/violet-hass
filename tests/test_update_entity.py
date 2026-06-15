"""Tests for the firmware update entity."""

from unittest.mock import MagicMock

from custom_components.violet_pool_controller.update import (
    VioletPoolControllerUpdateEntity,
)


def _make_coordinator(data: dict | None) -> MagicMock:
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.last_update_success = True
    coordinator.device.device_name = "Violet Pool Controller"
    coordinator.device.device_info = {
        "identifiers": {("violet_pool_controller", "test")},
        "name": "Violet Pool Controller",
        "manufacturer": "PoolDigital GmbH & Co. KG",
        "model": "Violet Pool Controller",
    }
    return coordinator


def _make_config_entry() -> MagicMock:
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


def test_update_entity_shows_available_update() -> None:
    """Entity reports an update when available version is newer."""
    coordinator = _make_coordinator(
        {"SYSTEM_swversion": "1.1.9", "SYSTEM_availableversion": "1.2.0"}
    )
    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())

    assert entity.installed_version == "1.1.9"
    assert entity.latest_version == "1.2.0"


def test_update_entity_shows_installed_when_up_to_date() -> None:
    """Entity falls back to installed version when no update is available."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.2.0"})
    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())

    assert entity.installed_version == "1.2.0"
    assert entity.latest_version == "1.2.0"


def test_update_entity_unavailable_without_data() -> None:
    """Entity returns None for versions when coordinator has no data."""
    coordinator = _make_coordinator(None)
    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())

    assert entity.installed_version is None
    assert entity.latest_version is None


def test_update_entity_firmware_device_class() -> None:
    """Entity is categorized as a firmware update."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.2.0"})
    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())

    assert entity.device_class == "firmware"
