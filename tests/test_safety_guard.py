"""Unit tests for SafetyGuard (no hass fixture required).

These tests use a mock persistence backend and a mock hass so they run
without ``pytest-homeassistant-custom-component`` installed.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.violet_pool_controller.safety_guard import SafetyGuard


class FakePersistence:
    """In-memory persistence backend."""

    def __init__(self) -> None:
        self._data: dict = {}

    async def get_auto_stop_store_data(self) -> dict | None:
        return self._data.get("auto_stops")

    async def async_load(self) -> dict:
        return self._data

    async def async_save(self, data: dict) -> None:
        self._data = data


@pytest.fixture(autouse=True)
def expected_lingering_tasks():
    """Allow lingering tasks from SafetyGuard background timers."""
    return True


def make_guard() -> tuple[SafetyGuard, FakePersistence, MagicMock]:
    """Create a SafetyGuard with mock hass + persistence."""
    persist = FakePersistence()
    hass = MagicMock()
    hass.data = {}
    hass.services = MagicMock()
    hass.config = MagicMock()
    hass.config.config_dir = "/config"
    # async_create_background_task should schedule on the running loop.
    hass.async_create_background_task = lambda coro, name=None: asyncio.ensure_future(coro)
    guard = SafetyGuard(hass, persist)
    return guard, persist, hass


class TestSafetyLock:
    """Tests for the cooldown lock (check/set/clear)."""

    async def test_check_lock_false_when_no_lock(self):
        guard, _, _ = make_guard()
        assert guard.check_lock("DOS_1_CL") is False

    async def test_set_lock_then_check_true(self):
        guard, _, _ = make_guard()
        guard.set_lock("DOS_1_CL", duration_seconds=300)
        assert guard.check_lock("DOS_1_CL") is True

    async def test_remaining_lock_time_decreases(self):
        guard, _, _ = make_guard()
        guard.set_lock("DOS_1_CL", duration_seconds=100)
        remaining = guard.remaining_lock_time("DOS_1_CL")
        assert 90 <= remaining <= 100

    async def test_remaining_lock_time_zero_when_no_lock(self):
        guard, _, _ = make_guard()
        assert guard.remaining_lock_time("DOS_1_CL") == 0

    async def test_clear_lock(self):
        guard, _, _ = make_guard()
        guard.set_lock("DOS_1_CL", duration_seconds=300)
        guard.clear_lock("DOS_1_CL")
        assert guard.check_lock("DOS_1_CL") is False

    async def test_set_lock_zero_duration_is_noop(self):
        guard, _, _ = make_guard()
        guard.set_lock("DOS_1_CL", duration_seconds=0)
        assert guard.check_lock("DOS_1_CL") is False


class TestEnforce:
    """Tests for enforce() gate behavior."""

    async def test_enforce_allows_when_no_lock(self):
        guard, _, _ = make_guard()
        await guard.enforce("DOS_1_CL")  # should not raise

    async def test_enforce_raises_when_lock_active(self):
        from homeassistant.exceptions import HomeAssistantError

        guard, _, _ = make_guard()
        guard.set_lock("DOS_1_CL", duration_seconds=300)
        with pytest.raises(HomeAssistantError, match="Safety interval active"):
            await guard.enforce("DOS_1_CL")

    async def test_enforce_allows_with_safety_override(self):
        guard, _, _ = make_guard()
        guard.set_lock("DOS_1_CL", duration_seconds=300)
        # safety_override bypasses the lock — must not raise
        await guard.enforce("DOS_1_CL", safety_override=True)


class TestAutoStop:
    """Tests for restart-persistent auto-stop timers."""

    async def test_arm_auto_stop_persists_deadline(self):
        guard, persist, _ = make_guard()
        await guard.arm_auto_stop(
            "REFILL",
            duration_seconds=60,
            stop_target={"method": "set_function_manually", "args": ["REFILL", "OFF"]},
        )
        stored = (await persist.async_load()).get("auto_stops", {})
        assert "REFILL" in stored
        data = stored["REFILL"]["stop_target"]
        assert "method" in data
        assert data["method"] == "set_function_manually"
        guard.cancel_auto_stop("REFILL")

    async def test_arm_auto_stop_executes_stop_after_delay(self):
        guard, _, _ = make_guard()
        api = MagicMock()
        api.set_function_manually = AsyncMock(return_value=True)
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.api = api
        guard._hass.data = {"violet_pool_controller": {None: coordinator}}

        await guard.arm_auto_stop(
            "REFILL",
            duration_seconds=0.05,
            stop_target={"method": "set_function_manually", "args": ["REFILL", "OFF"]},
        )
        # Let the background task run.
        await asyncio.sleep(0.15)
        api.set_function_manually.assert_awaited_once_with("REFILL", "OFF")

    async def test_cancel_auto_stop_prevents_execution(self):
        guard, _, _ = make_guard()
        api = MagicMock()
        api.set_function_manually = AsyncMock(return_value=True)
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.api = api
        guard._hass.data = {"violet_pool_controller": {None: coordinator}}

        await guard.arm_auto_stop(
            "REFILL",
            duration_seconds=0.2,
            stop_target={"method": "set_function_manually", "args": ["REFILL", "OFF"]},
        )
        guard.cancel_auto_stop("REFILL")
        await asyncio.sleep(0.3)
        api.set_function_manually.assert_not_awaited()
        guard.cancel_auto_stop("REFILL")

    async def test_expired_deadline_executed_immediately_on_setup(self):
        """A deadline that expired during downtime runs on async_setup()."""
        persist = FakePersistence()
        hass = MagicMock()
        hass.data = {}
        hass.async_create_background_task = lambda coro, name=None: asyncio.ensure_future(coro)
        # Pre-seed an already-expired deadline (offset <= 0 → runs immediately).
        persist._data = {
            "auto_stops": {
                "REFILL": {
                    "deadline_monotonic": 0,
                    "deadline_epoch": time.time() - 10,  # 10s ago
                    "stop_target": {"method": "set_function_manually", "args": ["REFILL", "OFF"]},
                }
            }
        }
        api = MagicMock()
        api.set_function_manually = AsyncMock(return_value=True)
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.api = api
        hass.data = {"violet_pool_controller": {None: coordinator}}

        guard = SafetyGuard(hass, persist)
        await guard.async_setup()
        # The immediate stop runs as a background task.
        await asyncio.sleep(0.15)
        api.set_function_manually.assert_awaited_once_with("REFILL", "OFF")

    async def test_future_deadline_rearmed_on_setup(self):
        """A still-future deadline gets re-armed (not executed immediately)."""
        persist = FakePersistence()
        hass = MagicMock()
        hass.data = {}
        hass.async_create_background_task = lambda coro, name=None: asyncio.ensure_future(coro)
        persist._data = {
            "auto_stops": {
                "BACKWASH": {
                    "deadline_monotonic": 0,
                    "deadline_epoch": time.time() + 5,  # 5s in the future
                    "stop_target": {
                        "method": "set_switch_state",
                        "args": ["BACKWASH"],
                        "kwargs": {"action": "OFF"},
                    },
                }
            }
        }
        api = MagicMock()
        api.set_switch_state = AsyncMock(return_value=True)
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.api = api
        hass.data = {"violet_pool_controller": {None: coordinator}}

        guard = SafetyGuard(hass, persist)
        await guard.async_setup()
        # Should NOT have been called yet (5s remaining).
        await asyncio.sleep(0.1)
        api.set_switch_state.assert_not_awaited()
        # The re-armed entry should remain persisted.
        stored = (await persist.async_load()).get("auto_stops", {})
        assert "BACKWASH" in stored


class TestResolveApi:
    """Tests for _resolve_api helper."""

    async def test_resolve_api_returns_first_available(self):
        guard, _, _ = make_guard()
        api = MagicMock()
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.api = api
        guard._hass.data = {"violet_pool_controller": {None: coordinator}}
        assert guard._resolve_api() is api

    async def test_resolve_api_returns_none_when_no_coordinators(self):
        guard, _, _ = make_guard()
        guard._hass.data = {"violet_pool_controller": {}}
        assert guard._resolve_api() is None
