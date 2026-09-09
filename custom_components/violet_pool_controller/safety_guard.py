# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================
"""Centralised safety guard for unsafe pool-equipment operations.

This module provides :class:`SafetyGuard`, the gate every code path that
drives dosing pumps, backwash valves, or water refill passes through.

Responsibilities
----------------
* **Enforce a cooldown** (safety interval) between successive operations on
  the same device key, so an automation cannot fire chemical dosing
  back-to-back.
* **Arm restart-safe auto-stop timers.**  A running refill or backwash must
  be stopped even when Home Assistant restarts mid-operation.  Deadlines are
  persisted (via ``hass.storage``) and re-armed on integration setup; any
  deadline that already expired during the downtime is executed immediately.
* **Log safety-relevant events** (warnings when ``safety_override`` is used,
  info when locks are armed/disarmed).

Everything is scoped to a config entry
--------------------------------------
Locks and auto-stops are keyed by ``(entry_id, device_key)``, and a stop is
dispatched to the coordinator of the entry that started the operation.  Keying
by device key alone made a two-controller setup unsafe: a refill started on
controller B was stopped on whichever controller happened to load first, and a
dosing cooldown on A blocked the same channel on B.  Sending a command to a
controller the user never addressed is exactly what SECURITY.md rules out.

Stop targets are validated when they are armed
----------------------------------------------
``stop_target["method"]`` is resolved against the API object at arm time, not
only when the timer fires.  A target naming a method the API does not have used
to fail silently at the far end of a refill, which is the one moment the timer
exists for.

The guard is intentionally framework-light: the persistence layer is injected
so the core logic can be unit-tested without a running Home Assistant.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Protocol

from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Storage key/version for hass.storage persistence.
STORAGE_KEY = f"{DOMAIN}.safety_guard"
STORAGE_VERSION = 1


class _CoordinatorLike(Protocol):
    """Structural type for the subset of coordinator we use."""

    @property
    def device(self) -> Any: ...


class SafetyPersistenceBackend(Protocol):
    """Persistence contract so the guard can be tested without HA storage."""

    async def async_load(self) -> dict[str, Any]:
        """Load persisted state (may return {})."""

    async def async_save(self, data: dict[str, Any]) -> None:
        """Persist state."""


class _HassStorageBackend:
    """hass.storage-backed persistence (used in production)."""

    def __init__(self, hass: HomeAssistant) -> None:
        from homeassistant.helpers.storage import Store

        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    async def async_load(self) -> dict[str, Any]:
        data = await self._store.async_load()
        return data if isinstance(data, dict) else {}

    async def async_save(self, data: dict[str, Any]) -> None:
        await self._store.async_save(data)


class SafetyGuard:
    """Central gate for all unsafe pool-equipment operations.

    A single instance lives on :class:`VioletServiceManager` and is shared by
    every service handler and the switch entity.  All dosing / backwash /
    refill code paths must call :meth:`enforce` before dispatching the command
    and :meth:`arm` after a successful start.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        persistence: SafetyPersistenceBackend,
    ) -> None:
        self._hass = hass
        self._persistence = persistence
        # In-memory safety locks: (entry_id, device_key) -> monotonic deadline.
        self._locks: dict[tuple[str, str], float] = {}
        # Active auto-stop tasks: (entry_id, device_key) -> running task.
        self._auto_stop_tasks: dict[tuple[str, str], asyncio.Task[Any]] = {}
        # Serialises the load-modify-save cycles below.  Three of them used to
        # interleave - arm, cancel and a task's own cleanup - so a freshly
        # persisted deadline could be deleted by the cancellation that
        # preceded it, silently losing the restart safety.
        self._persistence_lock = asyncio.Lock()

    # ------------------------------------------------------------------ #
    # Key handling
    # ------------------------------------------------------------------ #

    @staticmethod
    def _storage_key(entry_id: str, device_key: str) -> str:
        """Return the flat string key used inside the persisted mapping."""
        return f"{entry_id}::{device_key}"

    @staticmethod
    def _split_storage_key(storage_key: str) -> tuple[str, str] | None:
        """Split a persisted key, or return None for a pre-2.7.0 entry."""
        entry_id, separator, device_key = storage_key.partition("::")
        if not separator or not entry_id or not device_key:
            return None
        return entry_id, device_key

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    async def async_setup(self) -> None:
        """Load persisted deadlines and re-arm active auto-stop timers.

        Must be called once during integration setup, after the config entry's
        runtime data (and with it the coordinator) exists.
        """
        async with self._persistence_lock:
            data = await self._persistence.async_load()
            persisted: dict[str, Any] = data.get("auto_stops", {})
            if not persisted:
                return

            now = time.time()
            remaining: dict[str, Any] = {}
            for storage_key, entry in persisted.items():
                identity = self._split_storage_key(storage_key)
                if identity is None:
                    # Written before 2.7.0, when entries carried no entry id.
                    # There is no way to tell which controller it belongs to,
                    # and guessing would send a command to a controller the
                    # user never addressed.
                    _LOGGER.warning(
                        "SafetyGuard: dropping pre-2.7.0 auto-stop entry %r; it "
                        "does not name a controller. Check the equipment it "
                        "refers to manually",
                        storage_key,
                    )
                    continue
                entry_id, device_key = identity

                try:
                    deadline_epoch = float(entry["deadline_epoch"])
                except (KeyError, TypeError, ValueError):
                    _LOGGER.warning(
                        "SafetyGuard: skipping malformed persisted entry for %s",
                        storage_key,
                    )
                    continue

                # ``deadline_epoch`` is wall-clock time so it survives reboots;
                # the monotonic clock resets.  offset = real-world remaining.
                offset = deadline_epoch - now

                if offset <= 0:
                    # Already expired during downtime - execute the stop now.
                    _LOGGER.warning(
                        "SafetyGuard: auto-stop deadline for %s on entry %s expired "
                        "during downtime; executing stop command now",
                        device_key,
                        entry_id,
                    )
                    self._hass.async_create_background_task(
                        self._execute_stop(entry_id, device_key, entry.get("stop_target")),
                        f"{DOMAIN}_safety_stop_overdue_{storage_key}",
                    )
                else:
                    # Rearm with the real-world remaining duration.
                    remaining[storage_key] = entry
                    task = self._hass.async_create_background_task(
                        self._schedule_auto_stop(
                            entry_id, device_key, offset, entry.get("stop_target")
                        ),
                        f"{DOMAIN}_safety_stop_rearm_{storage_key}",
                    )
                    # Tracked, so a manual stop can cancel a re-armed timer.
                    # Untracked timers survived a manual stop and then fired
                    # in the middle of the next run.
                    self._auto_stop_tasks[entry_id, device_key] = task

            # Persist only the still-active entries.
            data["auto_stops"] = remaining
            await self._persistence.async_save(data)

    async def async_shutdown(self) -> None:
        """Cancel every armed timer without touching the persisted deadlines.

        Called when the last config entry unloads.  The deadlines stay on disk
        on purpose: a refill that is still running must be stopped when the
        integration comes back, and dropping the record here would lose that.
        """
        for task in list(self._auto_stop_tasks.values()):
            if not task.done():
                task.cancel()
        self._auto_stop_tasks.clear()
        self._locks.clear()

    # ------------------------------------------------------------------ #
    # Safety interval (cooldown between operations)
    # ------------------------------------------------------------------ #

    def check_lock(self, entry_id: str, device_key: str) -> bool:
        """Return True if a safety lock is currently active."""
        deadline = self._locks.get((entry_id, device_key))
        if deadline is None:
            return False
        if time.monotonic() >= deadline:
            # Expired - clean up.
            self._locks.pop((entry_id, device_key), None)
            return False
        return True

    def remaining_lock_time(self, entry_id: str, device_key: str) -> int:
        """Remaining cooldown seconds for a device (0 if none)."""
        deadline = self._locks.get((entry_id, device_key))
        if deadline is None:
            return 0
        remaining = deadline - time.monotonic()
        return max(0, int(remaining))

    async def enforce(
        self,
        entry_id: str,
        device_key: str,
        *,
        safety_override: bool = False,
    ) -> None:
        """Raise ``HomeAssistantError`` if a safety lock is active.

        Args:
            entry_id: The config entry whose controller is being addressed.
            device_key: The controller-side key (e.g. ``DOS_1_CL``, ``REFILL``).
            safety_override: If True the lock is skipped but a WARNING is logged
                so the override leaves an audit trail.
        """
        if safety_override:
            _LOGGER.warning(
                "SafetyGuard: safety_override=True - safety interval bypassed for %s",
                device_key,
            )
            return
        if self.check_lock(entry_id, device_key):
            remaining = self.remaining_lock_time(entry_id, device_key)
            from homeassistant.exceptions import HomeAssistantError

            raise HomeAssistantError(
                f"Safety interval active for {device_key}: {remaining}s remaining"
            )

    def set_lock(self, entry_id: str, device_key: str, duration_seconds: int) -> None:
        """Arm a cooldown lock of *duration_seconds* for a device."""
        if duration_seconds <= 0:
            return
        self._locks[entry_id, device_key] = time.monotonic() + duration_seconds
        _LOGGER.info("SafetyGuard: armed cooldown %ds for %s", duration_seconds, device_key)

    def clear_lock(self, entry_id: str, device_key: str) -> None:
        """Clear an active cooldown lock for a device."""
        if self._locks.pop((entry_id, device_key), None) is not None:
            _LOGGER.info("SafetyGuard: cleared cooldown for %s", device_key)

    # ------------------------------------------------------------------ #
    # Restart-safe auto-stop timers
    # ------------------------------------------------------------------ #

    async def arm_auto_stop(
        self,
        entry_id: str,
        device_key: str,
        duration_seconds: float,
        stop_target: dict[str, Any],
    ) -> None:
        """Start a restart-persistent auto-stop timer.

        Args:
            entry_id: The config entry whose controller must be stopped.
            device_key: The controller-side key being controlled.
            duration_seconds: After this many seconds the stop command runs.
            stop_target: Serializable descriptor of the stop command, e.g.
                ``{"method": "set_switch_state", "args": ["REFILL"],
                   "kwargs": {"action": "OFF"}}``.  ``method`` is resolved
                against the device's ``api`` object.

        Raises:
            HomeAssistantError: If ``stop_target`` names a method the API does
                not have.  Failing here is the point: a target that cannot be
                resolved is a timer that will not stop anything, and finding
                that out when the timer fires is too late.
        """
        if duration_seconds <= 0:
            return

        self._validate_stop_target(entry_id, device_key, stop_target)

        # Cancel any pre-existing timer for this key.
        await self.cancel_auto_stop(entry_id, device_key)

        task = self._hass.async_create_background_task(
            self._schedule_auto_stop(entry_id, device_key, duration_seconds, stop_target),
            f"{DOMAIN}_safety_auto_stop_{entry_id}_{device_key}",
        )
        self._auto_stop_tasks[entry_id, device_key] = task

        # Persist so the timer survives a restart.
        await self._persist_single(
            entry_id,
            device_key,
            {
                "deadline_epoch": time.time() + duration_seconds,
                "stop_target": stop_target,
            },
        )
        _LOGGER.warning(
            "SafetyGuard: armed auto-stop for %s in %.0fs (persisted)",
            device_key,
            duration_seconds,
        )

    async def cancel_auto_stop(self, entry_id: str, device_key: str) -> None:
        """Cancel an active auto-stop timer and drop its persisted deadline."""
        task = self._auto_stop_tasks.pop((entry_id, device_key), None)
        if task is not None and not task.done():
            task.cancel()
        await self._remove_persisted(entry_id, device_key)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _resolve_api(self, entry_id: str) -> Any:
        """Return the API of *entry_id*, or None when it is not loaded."""
        from .runtime_data import async_get_coordinator

        coordinator = async_get_coordinator(self._hass, entry_id)
        if coordinator is None:
            return None
        return getattr(coordinator.device, "api", None)

    def _validate_stop_target(
        self,
        entry_id: str,
        device_key: str,
        stop_target: dict[str, Any],
    ) -> None:
        """Fail now if the stop command could not be dispatched later."""
        from homeassistant.exceptions import HomeAssistantError

        method_name = stop_target.get("method") if stop_target else None
        if not method_name:
            msg = f"SafetyGuard: no stop method given for {device_key}"
            raise HomeAssistantError(msg)

        api = self._resolve_api(entry_id)
        if api is None:
            # The caller just talked to this controller, so this means the
            # entry unloaded in between.  Refuse rather than arm a timer with
            # nothing to dispatch to.
            msg = f"SafetyGuard: controller for {device_key} is not loaded"
            raise HomeAssistantError(msg)

        if not callable(getattr(api, str(method_name), None)):
            msg = (
                f"SafetyGuard: stop method {method_name!r} does not exist on the "
                f"controller API; refusing to start {device_key} without a "
                f"working auto-stop"
            )
            raise HomeAssistantError(msg)

    async def _schedule_auto_stop(
        self,
        entry_id: str,
        device_key: str,
        delay: float,
        stop_target: dict[str, Any] | None,
    ) -> None:
        """Sleep *delay* then execute the stop command and clean up."""
        try:
            await asyncio.sleep(max(0.0, delay))
            await self._execute_stop(entry_id, device_key, stop_target)
        except asyncio.CancelledError:
            # Normal cancellation when the operation is stopped manually.
            raise
        finally:
            # Only clean up if this task still owns the slot.  A cancelled task
            # used to delete the deadline of the run that replaced it.
            current = asyncio.current_task()
            if self._auto_stop_tasks.get((entry_id, device_key)) is current:
                self._auto_stop_tasks.pop((entry_id, device_key), None)
                await self._remove_persisted(entry_id, device_key)

    async def _execute_stop(
        self,
        entry_id: str,
        device_key: str,
        stop_target: dict[str, Any] | None,
    ) -> None:
        """Resolve *stop_target* against the device API and invoke it."""
        if not stop_target:
            _LOGGER.warning("SafetyGuard: no stop_target for %s, cannot auto-stop", device_key)
            return

        api = self._resolve_api(entry_id)
        if api is None:
            _LOGGER.error(
                "SafetyGuard: cannot auto-stop %s - config entry %s is not loaded. "
                "The equipment may still be running; check it manually",
                device_key,
                entry_id,
            )
            return

        method_name = stop_target.get("method")
        args = stop_target.get("args", [])
        kwargs = stop_target.get("kwargs", {})
        method = getattr(api, str(method_name), None) if method_name else None
        if method is None or not callable(method):
            _LOGGER.error(
                "SafetyGuard: stop method %r not found on API for %s",
                method_name,
                device_key,
            )
            return

        try:
            result = method(*args, **kwargs)
            if asyncio.iscoroutine(result):
                result = await result
            _LOGGER.warning(
                "SafetyGuard: auto-stopped %s via %s (result=%s)",
                device_key,
                method_name,
                result,
            )
        except Exception as err:  # noqa: BLE001 - we must not crash the timer task
            _LOGGER.error("SafetyGuard: auto-stop for %s FAILED: %s", device_key, err)

    # ---- persistence ---------------------------------------------------- #

    async def _persist_single(
        self,
        entry_id: str,
        device_key: str,
        entry: dict[str, Any],
    ) -> None:
        async with self._persistence_lock:
            data = await self._persistence.async_load()
            auto_stops = data.setdefault("auto_stops", {})
            auto_stops[self._storage_key(entry_id, device_key)] = entry
            await self._persistence.async_save(data)

    async def _remove_persisted(self, entry_id: str, device_key: str) -> None:
        async with self._persistence_lock:
            data = await self._persistence.async_load()
            auto_stops = data.get("auto_stops", {})
            if auto_stops.pop(self._storage_key(entry_id, device_key), None) is not None:
                await self._persistence.async_save(data)


@callback
def create_safety_guard(hass: HomeAssistant) -> SafetyGuard:
    """Factory used during integration setup."""
    return SafetyGuard(hass, _HassStorageBackend(hass))


__all__ = [
    "SafetyGuard",
    "SafetyPersistenceBackend",
    "create_safety_guard",
]
