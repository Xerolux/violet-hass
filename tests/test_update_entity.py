"""Tests for the firmware update entity."""

from unittest.mock import MagicMock

from custom_components.violet_pool_controller.update import (
    VioletPoolControllerUpdateEntity,
    _parse_update_progress,
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


def test_in_progress_reflects_local_flag() -> None:
    """in_progress tracks _update_in_progress, not coordinator data."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.2.0"})
    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())

    # Default: not in progress.
    assert entity.in_progress is False

    # Set the local flag — even with stale coordinator data, in_progress follows it.
    entity._update_in_progress = True
    assert entity.in_progress is True


def test_release_summary_shows_live_status_while_updating() -> None:
    """release_summary returns the live status while an update is running."""
    coordinator = _make_coordinator(
        {"SYSTEM_swversion": "1.1.9", "SYSTEM_availableversion": "1.2.0"}
    )
    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())

    # Idle: shows the normal update_description (no "läuft" marker).
    idle_summary = entity.release_summary
    assert idle_summary is None or "läuft" not in (idle_summary or "")

    # While updating: status text takes precedence.
    entity._update_in_progress = True
    entity._update_status_text = "downloading package (42%)"
    assert entity.release_summary == "Update läuft: downloading package (42%)"


def test_parse_update_progress_extracts_percentage() -> None:
    """A percentage in parentheses is extracted."""
    assert _parse_update_progress("downloading package (42%)") == 42


def test_parse_update_progress_extracts_bare_percentage() -> None:
    """A bare percentage token is extracted."""
    assert _parse_update_progress("progress: 88%") == 88


def test_parse_update_progress_no_percentage_returns_none() -> None:
    """No percentage present returns None (best-effort)."""
    assert _parse_update_progress("installing modules") is None


def test_parse_update_progress_clamps_above_100() -> None:
    """Values above 100 are clamped to 100."""
    assert _parse_update_progress("done (150%)") == 100
