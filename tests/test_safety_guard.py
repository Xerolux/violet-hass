"""Unit tests for SafetyGuard (no hass fixture required).

These tests use a mock persistence backend and a mock hass so they run
without ``pytest-homeassistant-custom-component`` installed.

Everything the guard tracks is scoped to a config entry. The tests below say
so explicitly, because keying by device key alone was a real bug: with two
controllers a refill started on B was stopped on whichever controller loaded
first, and a dosing cooldown on A blocked the same channel on B.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from violet_poolcontroller_api.api import VioletPoolAPI

from custom_components.violet_pool_controller.runtime_data import VioletRuntimeData
from custom_components.violet_pool_controller.safety_guard import SafetyGuard

ENTRY_A = "entry_a"
ENTRY_B = "entry_b"

# Every stop target below names a method that really exists on VioletPoolAPI.
# The mocks are built with ``spec=VioletPoolAPI`` so a target naming a method
# the API does not have fails the test instead of passing silently - which is
# exactly how the refill auto-stop went unnoticed: it named
# ``set_function_manually``, which lives on VioletControlClient, not on the API.
REFILL_STOP = {
    "method": "set_switch_state",
    "args": ["REFILL"],
    "kwargs": {"action": "OFF"},
}


class FakePersistence:
    """In-memory persistence backend."""

    def __init__(self) -> None:
        self._data: dict = {}

    async def async_load(self) -> dict:
        return self._data

    async def async_save(self, data: dict) -> None:
        self._data = data


@pytest.fixture(autouse=True)
def expected_lingering_tasks():
    """Allow lingering tasks from SafetyGuard background timers."""
    return True


def make_api() -> MagicMock:
    """Return an API mock that only answers to real VioletPoolAPI methods."""
    api = MagicMock(spec=VioletPoolAPI)
    api.set_switch_state = AsyncMock(return_value={"success": True})
    return api


def make_hass(*entries: tuple[str, MagicMock]) -> MagicMock:
    """Return a mock hass exposing the given (entry_id, api) pairs."""
    hass = MagicMock()
    hass.data = {}
    hass.async_create_background_task = lambda coro, name=None: asyncio.ensure_future(coro)

    registry: dict[str, MagicMock] = {}
    for entry_id, api in entries:
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.api = api
        entry = MagicMock()
        entry.entry_id = entry_id
        entry.runtime_data = VioletRuntimeData(coordinator=coordinator)
        registry[entry_id] = entry

    hass.config_entries.async_get_entry.side_effect = registry.get
    hass.config_entries.async_entries.return_value = list(registry.values())
    return hass


def make_guard(*entries: tuple[str, MagicMock]) -> tuple[SafetyGuard, FakePersistence, MagicMock]:
    """Create a SafetyGuard with mock hass + persistence."""
    persist = FakePersistence()
    hass = make_hass(*entries)
    return SafetyGuard(hass, persist), persist, hass


class TestSafetyLock:
    """Tests for the cooldown lock (check/set/clear)."""

    async def test_check_lock_false_when_no_lock(self):
        guard, _, _ = make_guard()
        assert guard.check_lock(ENTRY_A, "DOS_1_CL") is False

    async def test_set_lock_then_check_true(self):
        guard, _, _ = make_guard()
        guard.set_lock(ENTRY_A, "DOS_1_CL", duration_seconds=300)
        assert guard.check_lock(ENTRY_A, "DOS_1_CL") is True

    async def test_lock_does_not_leak_to_another_controller(self):
        """A cooldown on one controller must not block the same channel on another."""
        guard, _, _ = make_guard()
        guard.set_lock(ENTRY_A, "DOS_1_CL", duration_seconds=300)

        assert guard.check_lock(ENTRY_B, "DOS_1_CL") is False
        await guard.enforce(ENTRY_B, "DOS_1_CL")  # must not raise

    async def test_remaining_lock_time_decreases(self):
        guard, _, _ = make_guard()
        guard.set_lock(ENTRY_A, "DOS_1_CL", duration_seconds=100)
        remaining = guard.remaining_lock_time(ENTRY_A, "DOS_1_CL")
        assert 90 <= remaining <= 100

    async def test_remaining_lock_time_zero_when_no_lock(self):
        guard, _, _ = make_guard()
        assert guard.remaining_lock_time(ENTRY_A, "DOS_1_CL") == 0

    async def test_clear_lock(self):
        guard, _, _ = make_guard()
        guard.set_lock(ENTRY_A, "DOS_1_CL", duration_seconds=300)
        guard.clear_lock(ENTRY_A, "DOS_1_CL")
        assert guard.check_lock(ENTRY_A, "DOS_1_CL") is False

    async def test_set_lock_zero_duration_is_noop(self):
        guard, _, _ = make_guard()
        guard.set_lock(ENTRY_A, "DOS_1_CL", duration_seconds=0)
        assert guard.check_lock(ENTRY_A, "DOS_1_CL") is False


class TestEnforce:
    """Tests for enforce() gate behavior."""

    async def test_enforce_allows_when_no_lock(self):
        guard, _, _ = make_guard()
        await guard.enforce(ENTRY_A, "DOS_1_CL")  # should not raise

    async def test_enforce_raises_when_lock_active(self):
        from homeassistant.exceptions import HomeAssistantError

        guard, _, _ = make_guard()
        guard.set_lock(ENTRY_A, "DOS_1_CL", duration_seconds=300)
        with pytest.raises(HomeAssistantError, match="Safety interval active"):
            await guard.enforce(ENTRY_A, "DOS_1_CL")

    async def test_enforce_allows_with_safety_override(self):
        guard, _, _ = make_guard()
        guard.set_lock(ENTRY_A, "DOS_1_CL", duration_seconds=300)
        # safety_override bypasses the lock - must not raise
        await guard.enforce(ENTRY_A, "DOS_1_CL", safety_override=True)


class TestStopTargetValidation:
    """Arming must fail loudly when the stop command could never be sent."""

    async def test_unknown_stop_method_is_rejected_at_arm_time(self):
        """The refill auto-stop named a method the API does not have.

        It failed silently when the timer fired - at the far end of a refill,
        the one moment the timer exists for. Arming now refuses it.
        """
        from homeassistant.exceptions import HomeAssistantError

        api = make_api()
        guard, persist, _ = make_guard((ENTRY_A, api))

        with pytest.raises(HomeAssistantError, match="does not exist"):
            await guard.arm_auto_stop(
                ENTRY_A,
                "REFILL",
                duration_seconds=60,
                stop_target={"method": "set_function_manually", "args": ["REFILL", "OFF"]},
            )

        assert (await persist.async_load()).get("auto_stops", {}) == {}

    async def test_unloaded_entry_is_rejected_at_arm_time(self):
        from homeassistant.exceptions import HomeAssistantError

        guard, _, _ = make_guard()

        with pytest.raises(HomeAssistantError, match="not loaded"):
            await guard.arm_auto_stop(
                ENTRY_A, "REFILL", duration_seconds=60, stop_target=REFILL_STOP
            )


class TestAutoStop:
    """Tests for restart-persistent auto-stop timers."""

    async def test_arm_auto_stop_persists_deadline(self):
        api = make_api()
        guard, persist, _ = make_guard((ENTRY_A, api))

        await guard.arm_auto_stop(ENTRY_A, "REFILL", duration_seconds=60, stop_target=REFILL_STOP)

        stored = (await persist.async_load()).get("auto_stops", {})
        assert f"{ENTRY_A}::REFILL" in stored
        assert stored[f"{ENTRY_A}::REFILL"]["stop_target"]["method"] == "set_switch_state"
        await guard.cancel_auto_stop(ENTRY_A, "REFILL")

    async def test_arm_auto_stop_executes_stop_after_delay(self):
        api = make_api()
        guard, _, _ = make_guard((ENTRY_A, api))

        await guard.arm_auto_stop(ENTRY_A, "REFILL", duration_seconds=0.05, stop_target=REFILL_STOP)
        await asyncio.sleep(0.15)

        api.set_switch_state.assert_awaited_once_with("REFILL", action="OFF")

    async def test_stop_goes_to_the_controller_that_started_it(self):
        """With two controllers the stop must reach the one that was started."""
        api_a, api_b = make_api(), make_api()
        guard, _, _ = make_guard((ENTRY_A, api_a), (ENTRY_B, api_b))

        await guard.arm_auto_stop(ENTRY_B, "REFILL", duration_seconds=0.05, stop_target=REFILL_STOP)
        await asyncio.sleep(0.15)

        api_b.set_switch_state.assert_awaited_once_with("REFILL", action="OFF")
        api_a.set_switch_state.assert_not_awaited()

    async def test_cancel_auto_stop_prevents_execution(self):
        api = make_api()
        guard, _, _ = make_guard((ENTRY_A, api))

        await guard.arm_auto_stop(ENTRY_A, "REFILL", duration_seconds=0.2, stop_target=REFILL_STOP)
        await guard.cancel_auto_stop(ENTRY_A, "REFILL")
        await asyncio.sleep(0.3)

        api.set_switch_state.assert_not_awaited()

    async def test_rearming_keeps_the_new_deadline_persisted(self):
        """The cancelled timer's cleanup must not delete the run that replaced it."""
        api = make_api()
        guard, persist, _ = make_guard((ENTRY_A, api))

        await guard.arm_auto_stop(ENTRY_A, "REFILL", duration_seconds=0.1, stop_target=REFILL_STOP)
        await guard.arm_auto_stop(ENTRY_A, "REFILL", duration_seconds=600, stop_target=REFILL_STOP)
        # Give the cancelled task time to run its cleanup.
        await asyncio.sleep(0.25)

        stored = (await persist.async_load()).get("auto_stops", {})
        assert f"{ENTRY_A}::REFILL" in stored
        api.set_switch_state.assert_not_awaited()
        await guard.cancel_auto_stop(ENTRY_A, "REFILL")

    async def test_expired_deadline_executed_immediately_on_setup(self):
        """A deadline that expired during downtime runs on async_setup()."""
        api = make_api()
        persist = FakePersistence()
        persist._data = {
            "auto_stops": {
                f"{ENTRY_A}::REFILL": {
                    "deadline_epoch": time.time() - 10,
                    "stop_target": REFILL_STOP,
                }
            }
        }
        guard = SafetyGuard(make_hass((ENTRY_A, api)), persist)

        await guard.async_setup()
        await asyncio.sleep(0.15)

        api.set_switch_state.assert_awaited_once_with("REFILL", action="OFF")

    async def test_future_deadline_rearmed_on_setup(self):
        """A still-future deadline gets re-armed (not executed immediately)."""
        api = make_api()
        persist = FakePersistence()
        persist._data = {
            "auto_stops": {
                f"{ENTRY_A}::BACKWASH": {
                    "deadline_epoch": time.time() + 5,
                    "stop_target": {
                        "method": "set_switch_state",
                        "args": ["BACKWASH"],
                        "kwargs": {"action": "OFF"},
                    },
                }
            }
        }
        guard = SafetyGuard(make_hass((ENTRY_A, api)), persist)

        await guard.async_setup()
        await asyncio.sleep(0.1)

        api.set_switch_state.assert_not_awaited()
        stored = (await persist.async_load()).get("auto_stops", {})
        assert f"{ENTRY_A}::BACKWASH" in stored
        await guard.cancel_auto_stop(ENTRY_A, "BACKWASH")

    async def test_rearmed_timer_can_be_cancelled(self):
        """A re-armed timer used to be untracked, so a manual stop missed it.

        It then fired in the middle of the next run.
        """
        api = make_api()
        persist = FakePersistence()
        persist._data = {
            "auto_stops": {
                f"{ENTRY_A}::REFILL": {
                    "deadline_epoch": time.time() + 0.1,
                    "stop_target": REFILL_STOP,
                }
            }
        }
        guard = SafetyGuard(make_hass((ENTRY_A, api)), persist)
        await guard.async_setup()

        await guard.cancel_auto_stop(ENTRY_A, "REFILL")
        await asyncio.sleep(0.3)

        api.set_switch_state.assert_not_awaited()

    async def test_legacy_entry_without_controller_is_dropped(self):
        """Pre-2.7.0 entries name no controller; guessing one is not safe."""
        api = make_api()
        persist = FakePersistence()
        persist._data = {
            "auto_stops": {
                "REFILL": {
                    "deadline_epoch": time.time() - 10,
                    "stop_target": REFILL_STOP,
                }
            }
        }
        guard = SafetyGuard(make_hass((ENTRY_A, api)), persist)

        await guard.async_setup()
        await asyncio.sleep(0.15)

        api.set_switch_state.assert_not_awaited()
        assert (await persist.async_load()).get("auto_stops", {}) == {}


class TestResolveApi:
    """Tests for the per-entry API lookup."""

    async def test_resolve_api_returns_the_named_entry(self):
        api_a, api_b = make_api(), make_api()
        guard, _, _ = make_guard((ENTRY_A, api_a), (ENTRY_B, api_b))

        assert guard._resolve_api(ENTRY_A) is api_a
        assert guard._resolve_api(ENTRY_B) is api_b

    async def test_resolve_api_returns_none_for_unknown_entry(self):
        guard, _, _ = make_guard()
        assert guard._resolve_api(ENTRY_A) is None
