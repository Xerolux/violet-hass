"""Regression tests for stale firmware update states."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.violet_pool_controller.update import (
    VioletPoolControllerUpdateEntity,
)


def _make_entity(data: dict[str, str]) -> tuple[VioletPoolControllerUpdateEntity, MagicMock]:
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
    coordinator.async_request_refresh = AsyncMock()

    config_entry = MagicMock()
    config_entry.entry_id = "test_entry_id"

    entity = VioletPoolControllerUpdateEntity(coordinator, config_entry)
    entity.async_write_ha_state = MagicMock()  # type: ignore[assignment]
    return entity, coordinator


@pytest.mark.asyncio
async def test_poll_completes_on_version_change_without_standby(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A stale update.log must not cause a false ten-minute timeout."""
    entity, coordinator = _make_entity(
        {
            "SYSTEM_swversion": "1.1.9",
            "SYSTEM_availableversion": "1.2.0",
        }
    )

    coordinator.device.api.get_update_state = AsyncMock(
        return_value="installation completed (100%)"
    )

    async def refresh_version() -> None:
        coordinator.data["SYSTEM_swversion"] = "1.2.0"

    coordinator.async_request_refresh = AsyncMock(side_effect=refresh_version)

    entity._update_in_progress = True
    entity._update_start_version = "1.1.9"
    entity._update_target_version = "1.2.0"
    monkeypatch.setattr(entity, "_UPDATE_VERSION_REFRESH_INTERVAL", 5)
    monkeypatch.setattr(entity, "_UPDATE_MAX_LIFETIME", 15)

    async def fast_sleep(_seconds: float) -> None:
        return None

    import custom_components.violet_pool_controller.update as update_mod

    monkeypatch.setattr(update_mod.asyncio, "sleep", fast_sleep)

    await entity._poll_update_state()

    assert entity._update_in_progress is False
    assert entity._update_progress is None
    assert entity._update_status_text is None
    coordinator.async_request_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_startup_ignores_stale_state_for_installed_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A completed update log must not be resumed after an HA restart."""
    entity, coordinator = _make_entity(
        {
            "SYSTEM_swversion": "1.2.0",
            "SYSTEM_availableversion": "1.2.0",
        }
    )
    coordinator.device.api.get_update_state = AsyncMock(
        return_value="installation completed (100%)"
    )

    parent_added = AsyncMock()
    monkeypatch.setattr(CoordinatorEntity, "async_added_to_hass", parent_added)

    await entity.async_added_to_hass()

    parent_added.assert_awaited_once()
    assert entity._update_in_progress is False
    assert entity._update_task is None


def test_version_change_confirms_completion() -> None:
    """The target version is accepted even while update state remains stale."""
    entity, coordinator = _make_entity(
        {
            "SYSTEM_swversion": "1.1.9",
            "SYSTEM_availableversion": "1.2.0",
        }
    )
    entity._update_start_version = "1.1.9"
    entity._update_target_version = "1.2.0"

    assert entity._firmware_version_confirms_completion() is False

    coordinator.data["SYSTEM_swversion"] = "1.2.0"

    assert entity._firmware_version_confirms_completion() is True
