# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================
"""Centralised safety guard for unsafe pool-equipment operations.

This module provides :class:`SafetyGuard`, the single gate every code path
that drives dosing pumps, backwash valves, or water refill must pass through.

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

        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)

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
        # In-memory safety locks: device_key -> monotonic deadline.
        self._locks: dict[str, float] = {}
        # Active auto-stop tasks: device_key -> running asyncio.Task.
        self._auto_stop_tasks: dict[str, asyncio.Task[Any]] = {}

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    async def async_setup(self) -> None:
        """Load persisted deadlines and re-arm active auto-stop timers.

        Must be called once during integration setup, after coordinators are
        available in ``hass.data[DOMAIN]``.
        """
        data = await self._persistence.async_load()
        persisted: dict[str, Any] = data.get("auto_stops", {})
        if not persisted:
            return

        now = time.time()
        remaining: dict[str, Any] = {}
        for device_key, entry in persisted.items():
            try:
                deadline_epoch = float(entry["deadline_epoch"])
            except (KeyError, TypeError, ValueError):
                _LOGGER.warning(
                    "SafetyGuard: skipping malformed persisted entry for %s", device_key
                )
                continue

            # ``deadline_epoch`` is wall-clock time so it survives reboots;
            # the monotonic clock resets.  offset = real-world remaining.
            offset = deadline_epoch - now

            if offset <= 0:
                # Already expired during downtime — execute the stop now.
                _LOGGER.warning(
                    "SafetyGuard: auto-stop deadline for %s expired during "
                    "downtime; executing stop command now",
                    device_key,
                )
                self._hass.async_create_background_task(
                    self._execute_stop(device_key, entry.get("stop_target")),
                    f"{DOMAIN}_safety_stop_overdue_{device_key}",
                )
            else:
                # Rearm with the real-world remaining duration.
                remaining[device_key] = entry
                self._hass.async_create_background_task(
                    self._schedule_auto_stop(device_key, offset, entry.get("stop_target")),
                    f"{DOMAIN}_safety_stop_rearm_{device_key}",
                )

        # Persist only the still-active entries.
        await self._persist_auto_stops(remaining)

    # ------------------------------------------------------------------ #
    # Safety interval (cooldown between operations)
    # ------------------------------------------------------------------ #

    def check_lock(self, device_key: str) -> bool:
        """Return True if a safety lock is currently active for *device_key*."""
        deadline = self._locks.get(device_key)
        if deadline is None:
            return False
        if time.monotonic() >= deadline:
            # Expired — clean up.
            self._locks.pop(device_key, None)
            return False
        return True

    def remaining_lock_time(self, device_key: str) -> int:
        """Remaining cooldown seconds for *device_key* (0 if none)."""
        deadline = self._locks.get(device_key)
        if deadline is None:
            return 0
        remaining = deadline - time.monotonic()
        return max(0, int(remaining))

    async def enforce(
        self,
        device_key: str,
        *,
        safety_override: bool = False,
    ) -> None:
        """Raise ``HomeAssistantError`` if a safety lock is active.

        Args:
            device_key: The controller-side key (e.g. ``DOS_1_CL``, ``REFILL``).
            safety_override: If True the lock is skipped but a WARNING is logged
                so the override leaves an audit trail.
        """
        if safety_override:
            _LOGGER.warning(
                "SafetyGuard: safety_override=True — safety interval bypassed for %s",
                device_key,
            )
            return
        if self.check_lock(device_key):
            remaining = self.remaining_lock_time(device_key)
            from homeassistant.exceptions import HomeAssistantError

            raise HomeAssistantError(
                f"Safety interval active for {device_key}: {remaining}s remaining"
            )

    def set_lock(self, device_key: str, duration_seconds: int) -> None:
        """Arm a cooldown lock of *duration_seconds* for *device_key*."""
        if duration_seconds <= 0:
            return
        self._locks[device_key] = time.monotonic() + duration_seconds
        _LOGGER.info("SafetyGuard: armed cooldown %ds for %s", duration_seconds, device_key)

    def clear_lock(self, device_key: str) -> None:
        """Clear an active cooldown lock for *device_key*."""
        if self._locks.pop(device_key, None) is not None:
            _LOGGER.info("SafetyGuard: cleared cooldown for %s", device_key)

    # ------------------------------------------------------------------ #
    # Restart-safe auto-stop timers
    # ------------------------------------------------------------------ #

    async def arm_auto_stop(
        self,
        device_key: str,
        duration_seconds: float,
        stop_target: dict[str, Any],
    ) -> None:
        """Start a restart-persistent auto-stop timer.

        Args:
            device_key: The controller-side key being controlled.
            duration_seconds: After this many seconds the stop command runs.
            stop_target: Serializable descriptor of the stop command, e.g.
                ``{"method": "set_function_manually", "args": ["REFILL", "OFF"]}``
                or ``{"method": "set_switch_state",
                       "args": ["DOS_1_CL"], "kwargs": {"action": "OFF"}}``.
                ``method`` is resolved against the device's ``api`` object.
        """
        if duration_seconds <= 0:
            return

        # Cancel any pre-existing timer for this key.
        self.cancel_auto_stop(device_key)

        task = self._hass.async_create_background_task(
            self._schedule_auto_stop(device_key, duration_seconds, stop_target),
            f"{DOMAIN}_safety_auto_stop_{device_key}",
        )
        self._auto_stop_tasks[device_key] = task

        # Persist so the timer survives a restart.
        deadline_monotonic = time.monotonic() + duration_seconds
        deadline_epoch = time.time() + duration_seconds
        await self._persist_single(
            device_key,
            {
                "deadline_monotonic": deadline_monotonic,
                "deadline_epoch": deadline_epoch,
                "stop_target": stop_target,
            },
        )
        _LOGGER.warning(
            "SafetyGuard: armed auto-stop for %s in %.0fs (persisted)",
            device_key,
            duration_seconds,
        )

    def cancel_auto_stop(self, device_key: str) -> None:
        """Cancel an active auto-stop timer and drop its persisted deadline."""
        task = self._auto_stop_tasks.pop(device_key, None)
        if task is not None and not task.done():
            task.cancel()
        self._hass.async_create_background_task(
            self._remove_persisted(device_key),
            f"{DOMAIN}_safety_remove_{device_key}",
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    async def _schedule_auto_stop(
        self,
        device_key: str,
        delay: float,
        stop_target: dict[str, Any] | None,
    ) -> None:
        """Sleep *delay* then execute the stop command and clean up."""
        try:
            await asyncio.sleep(max(0.0, delay))
            await self._execute_stop(device_key, stop_target)
        except asyncio.CancelledError:
            # Normal cancellation when the operation is stopped manually.
            raise
        finally:
            self._auto_stop_tasks.pop(device_key, None)
            await self._remove_persisted(device_key)

    async def _execute_stop(
        self,
        device_key: str,
        stop_target: dict[str, Any] | None,
    ) -> None:
        """Resolve *stop_target* against the device API and invoke it."""
        if not stop_target:
            _LOGGER.warning("SafetyGuard: no stop_target for %s, cannot auto-stop", device_key)
            return

        api = self._resolve_api()
        if api is None:
            _LOGGER.error("SafetyGuard: cannot auto-stop %s — device API not found", device_key)
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

    def _resolve_api(self) -> Any:
        """Find a device API from the registered coordinators.

        Skips non-coordinator entries (e.g. the ``service_manager`` key).
        """
        for value in self._hass.data.get(DOMAIN, {}).values():
            # Coordinators expose a ``device`` attribute with an ``api``;
            # the service_manager and other non-coordinator values do not.
            device = getattr(value, "device", None)
            api = getattr(device, "api", None)
            if api is not None:
                return api
        return None

    # ---- persistence ---------------------------------------------------- #

    async def _persist_auto_stops(self, entries: dict[str, Any]) -> None:
        data = await self._persistence.async_load()
        data["auto_stops"] = entries
        await self._persistence.async_save(data)

    async def _persist_single(self, device_key: str, entry: dict[str, Any]) -> None:
        data = await self._persistence.async_load()
        auto_stops = data.setdefault("auto_stops", {})
        auto_stops[device_key] = entry
        await self._persistence.async_save(data)

    async def _remove_persisted(self, device_key: str) -> None:
        data = await self._persistence.async_load()
        auto_stops = data.get("auto_stops", {})
        if device_key in auto_stops:
            auto_stops.pop(device_key)
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
