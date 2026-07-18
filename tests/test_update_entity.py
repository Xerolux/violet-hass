"""Tests for the firmware update entity."""

import asyncio
import contextlib
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.exceptions import HomeAssistantError
from violet_poolcontroller_api import VioletPoolAPIError

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


def _stub_entity_for_async(entity: VioletPoolControllerUpdateEntity) -> None:
    """Stub HA-bound methods so the entity can run without a real hass runtime."""
    entity.async_write_ha_state = MagicMock()  # type: ignore[assignment]


@pytest.mark.asyncio
async def test_poll_marks_progress_then_completes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Polling sets progress/status, then ends on STANDBY and refreshes."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})
    states = iter(["downloading package (42%)", "STANDBY"])

    async def fake_get_update_state() -> str:
        return next(states)

    coordinator.device.api.get_update_state = fake_get_update_state
    coordinator.async_request_refresh = AsyncMock()

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)
    entity._update_in_progress = True

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
async def test_poll_sets_progress_mid_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    """The first non-STANDBY read sets progress/status before the loop continues."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})

    async def fake_get_update_state() -> str:
        return "downloading (42%)"

    coordinator.device.api.get_update_state = fake_get_update_state
    coordinator.async_request_refresh = AsyncMock()

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)
    entity._update_in_progress = True

    stopped = False

    async def stopping_sleep(_seconds: float) -> None:
        nonlocal stopped
        stopped = True
        raise asyncio.CancelledError()

    import custom_components.violet_pool_controller.update as update_mod

    monkeypatch.setattr(update_mod.asyncio, "sleep", stopping_sleep)

    with contextlib.suppress(asyncio.CancelledError):
        await entity._poll_update_state()

    assert stopped is True
    assert entity._update_progress == 42
    assert entity._update_status_text == "downloading (42%)"


@pytest.mark.asyncio
async def test_poll_resilient_to_transient_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A transient API error mid-loop does not crash the polling task."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})
    call_count = 0

    async def fake_get_update_state() -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise VioletPoolAPIError("controller temporarily unreachable")
        return "STANDBY"

    coordinator.device.api.get_update_state = fake_get_update_state
    coordinator.async_request_refresh = AsyncMock()

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)
    entity._update_in_progress = True

    async def fast_sleep(_seconds: float) -> None:
        return None

    import custom_components.violet_pool_controller.update as update_mod

    monkeypatch.setattr(update_mod.asyncio, "sleep", fast_sleep)

    # Should not raise despite the first-iteration API error.
    await entity._poll_update_state()

    assert call_count == 2  # retried after the error
    assert entity._update_in_progress is False  # cleared by STANDBY


@pytest.mark.asyncio
async def test_poll_aborts_after_safety_net_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """If STANDBY is never reached, the safety net aborts and resets state."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})

    async def fake_get_update_state() -> str:
        return "stuck (50%)"  # never STANDBY

    coordinator.device.api.get_update_state = fake_get_update_state
    coordinator.async_request_refresh = AsyncMock()

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)
    entity._update_in_progress = True

    async def fast_sleep(_seconds: float) -> None:
        return None

    import custom_components.violet_pool_controller.update as update_mod

    monkeypatch.setattr(update_mod.asyncio, "sleep", fast_sleep)
    # Shrink the safety net so the test exits after one iteration.
    monkeypatch.setattr(entity, "_UPDATE_MAX_LIFETIME", 3)

    # Should not raise — the safety net logs and resets state.
    await entity._poll_update_state()

    assert entity._update_in_progress is False  # reset by safety net
    assert entity._update_progress is None
    assert entity._update_status_text is None
    coordinator.async_request_refresh.assert_awaited()


@pytest.mark.asyncio
async def test_async_install_rejects_double_click() -> None:
    """Calling async_install while already in progress raises and does not re-trigger."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})

    init_calls = 0

    async def fake_init_update() -> str:
        nonlocal init_calls
        init_calls += 1
        return "STARTING"

    async def fake_get_update_state() -> str:
        return "STANDBY"

    coordinator.device.api.init_update = fake_init_update
    coordinator.device.api.get_update_state = fake_get_update_state
    coordinator.async_request_refresh = AsyncMock()

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)
    entity._update_in_progress = True  # already running

    with pytest.raises(HomeAssistantError):
        await entity.async_install(version="1.2.0", backup=False)

    assert init_calls == 0  # never reached the controller


@pytest.mark.asyncio
async def test_async_install_rejects_external_running_update() -> None:
    """If the controller reports a running update, install refuses and starts polling."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})

    init_calls = 0

    async def fake_init_update() -> str:
        nonlocal init_calls
        init_calls += 1
        return "STARTING"

    async def fake_get_update_state() -> str:
        return "downloading (10%)"

    coordinator.device.api.init_update = fake_init_update
    coordinator.device.api.get_update_state = fake_get_update_state
    coordinator.async_request_refresh = AsyncMock()

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)

    with pytest.raises(HomeAssistantError):
        await entity.async_install(version="1.2.0", backup=False)

    assert init_calls == 0
    assert entity._update_in_progress is True
    assert entity._update_task is not None
    # Cancel the started task so pytest can tear down cleanly.
    entity._update_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await entity._update_task


@pytest.mark.asyncio
async def test_async_install_starts_polling_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful init_update sets in_progress and starts the polling task."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})

    async def fake_init_update() -> str:
        return "STARTING"

    async def fake_get_update_state() -> str:
        return "STANDBY"

    coordinator.device.api.init_update = fake_init_update
    coordinator.device.api.get_update_state = fake_get_update_state
    coordinator.async_request_refresh = AsyncMock()

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)

    async def fast_sleep(_seconds: float) -> None:
        return None

    import custom_components.violet_pool_controller.update as update_mod

    monkeypatch.setattr(update_mod.asyncio, "sleep", fast_sleep)

    await entity.async_install(version="1.2.0", backup=False)

    assert entity._update_in_progress is True
    assert entity._update_task is not None
    # Let the task run to STANDBY and finish.
    await entity._update_task
    assert entity._update_in_progress is False
