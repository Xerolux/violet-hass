# Update Progress Feedback Design

**Date:** 2026-07-18
**Status:** Approved (verbal) — pending spec review
**Scope:** `custom_components/violet_pool_controller/update.py` and its tests

## Problem

When a firmware update is available on the Violet Pool Controller, clicking
"Aktualisieren" in Home Assistant triggers the update (it runs for 2–3 minutes
on the controller), but there is **no feedback to the user**:

- The `in_progress` property (`update.py:130-135`) reads a key
  `SYSTEM_UPDATE_IN_PROGRESS` from coordinator data, but **no code path ever
  writes that key**. The property is permanently `False`.
- As a result, the update button stays clickable. The user can click it
  repeatedly during the install window with no indication that an update is
  already running.
- `UpdateEntityFeature.PROGRESS` is not declared in `_attr_supported_features`,
  so HA does not render the progress UI even if `in_progress` were correct.

The underlying API library already exposes `api.get_update_state()`
(`GET /getUpdateState`), which returns the live update log (progress) or
`"STANDBY"` when idle. This method is implemented in the library but currently
**has zero call sites** in the integration.

## Goal

Give the user clear, real-time feedback during the firmware update and prevent
the misleading double-click behaviour. The controller itself is the source of
truth for update status — we surface what it already exposes.

## Non-Goals (YAGNI)

- No precise percentage parsing from complex log formats. If the log yields no
  clear percentage, we show only a status string + the HA spinner. Best-effort,
  no over-engineering.
- No changes to the `VioletPoolDataUpdateCoordinator` polling logic.
- No translation work for status strings — the controller's live log lines are
  shown raw (technical in nature).
- No progress persistence across reloads beyond a single startup probe (see
  Architecture decision below).

## Architecture Decision

**Entity-local polling task** (not Coordinator-integrated).

Rationale:

1. The coordinator already has complex dynamic polling logic (faster polling
   when pump/dosing active, otherwise configured interval). Mixing a 5-second
   update-status cadence in there would tangle two unrelated concerns.
2. Single-responsibility: the update entity owns its install lifecycle.
3. Reload/restart safety is achieved via a single `get_update_state()` probe in
   `async_added_to_hass` — if the controller is mid-update when HA starts, the
   polling task is started immediately.

**Status display via `release_summary`** during the update (not `update_status`).

Rationale: HA's `update_status` property only exists in HA ≥ 2025.6. The
project's minimum HA version is `2026.5.0` (per `hacs.json` and `CLAUDE.md`),
so technically `update_status` would be available. We still default to
`release_summary` because:

- It renders reliably in the More-Info dialog and the update card across all
  supported HA versions and frontends (mobile included).
- `release_summary` is already overridden in this entity, so extending it
  during the install window is a minimal, contained change.

We layer the live status text in front of the regular `update_description`
while `_update_in_progress` is True, and restore the normal `release_summary`
behaviour once the update completes.

## Design

### Components

**A. Declare `UpdateEntityFeature.PROGRESS`**

Extend `_attr_supported_features`:

```python
_attr_supported_features = (
    UpdateEntityFeature.INSTALL
    | UpdateEntityFeature.RELEASE_NOTES
    | UpdateEntityFeature.PROGRESS
)
```

This makes HA render the progress UI (spinner / percentage) and automatically
disable the install button while `in_progress` is True.

**B. Internal state fields on the entity**

Added to `__init__`:

- `_update_in_progress: bool = False` — drives the `in_progress` property.
- `_update_progress: int | None = None` — best-effort 0–100, parsed from log.
- `_update_status_text: str | None = None` — human-readable live status (last
  log line / phase string).
- `_update_task: asyncio.Task[None] | None = None` — reference to the polling
  task, for cancellation.

**C. Rewrite `in_progress`**

Replace the dead `SYSTEM_UPDATE_IN_PROGRESS` lookup with a return of
`_update_in_progress`. When HA passes a specific `version`, we still return
True (any in-progress install matches).

**D. Layer live status into `release_summary`**

While `_update_in_progress` is True, `release_summary` returns the live status
text (e.g. `"Update läuft: <status>"`), taking precedence over the normal
`update_description`. When idle, behaviour is unchanged.

**E. Polling task `_poll_update_state()`**

A coroutine on the entity, started as a task. Loop:

1. Call `await self.coordinator.device.api.get_update_state()`.
2. If the response is `STANDBY` (case-insensitive, stripped):
   - Set `_update_in_progress = False`, clear `_update_progress` and
     `_update_status_text`.
   - Trigger `await self.coordinator.async_request_refresh()` so
     `installed_version` updates from the freshly-restarted controller.
   - `self.async_write_ha_state()`.
   - Return (ends the task).
3. Otherwise:
   - Set `_update_in_progress = True`.
   - Parse a best-effort percentage from the response (regex `\((\d+)%\)` or
     `(\d+)%`). If found, set `_update_progress`; else leave as `None`.
   - Set `_update_status_text` to the response (or last non-empty line).
   - `self.async_write_ha_state()`.
4. `await asyncio.sleep(5)` (5-second cadence, per decision).
5. Loop.

**Error handling in the polling task:**

- On `VioletPoolAPIError`, `TimeoutError`, or generic `Exception`: log a
  warning at debug level (the controller is briefly unreachable during its
  restart — that is expected mid-update) and continue polling. Do not crash the
  task.
- **Safety-net lifetime:** track elapsed time; if the task runs longer than
  **10 minutes**, abort, log an error, reset `_update_in_progress = False`, and
  trigger one final coordinator refresh. This prevents permanently-stuck tasks
  if the controller never returns to `STANDBY`.

**F. Double-click guard in `async_install`**

At the very start of `async_install`:

1. If `self._update_in_progress` is already True → raise
   `HomeAssistantError("Update läuft bereits …")`. HA surfaces this to the
   user.
2. As a belt-and-suspenders check against updates started from elsewhere
   (another client, a prior crashed task): do a single `await
   api.get_update_state()` probe. If not `STANDBY`, set
   `_update_in_progress = True`, start the polling task, and raise
   `HomeAssistantError("Update läuft bereits auf der Steuerung")`.

Only after these checks pass do we call `init_update()` and start the polling
task on success.

**G. Startup detection in `async_added_to_hass`**

Override `async_added_to_hass`:

- Call `await super().async_added_to_hass()`.
- Probe `await api.get_update_state()` once.
- If not `STANDBY`: set `_update_in_progress = True`, set an initial status
  text, and start the polling task.
- Wrap in try/except — a failure to probe at startup must not break entity
  setup; log at debug level and proceed as idle.

**H. Cleanup in `async_will_remove_from_hass`**

Override `async_will_remove_from_hass`:

- If `_update_task` is not None and not done, cancel it and await its
  cancellation (swallowing `asyncio.CancelledError`).
- Reset `_update_in_progress = False` (the entity is gone; if it comes back,
  startup detection will re-detect).

### Data Flow

```
User clicks "Aktualisieren"
  → async_install()
      → guard: _update_in_progress already True → HomeAssistantError
      → guard: api.get_update_state() != STANDBY → start task, raise
      → api.init_update()                       (GET /initUpdate)
      → _update_in_progress = True
      → _update_task = create_task(_poll_update_state())
      → async_write_ha_state()                  (button disabled immediately)

Polling task (every 5s, max 10 min):
  → api.get_update_state()                      (GET /getUpdateState)
      → not STANDBY: parse %, set status text, write_ha_state, sleep 5s, loop
      → STANDBY: reset flags, coordinator.async_request_refresh(), end task
      → exception: log debug, sleep 5s, loop
      → >10 min elapsed: abort, reset, final refresh

HA start / integration reload:
  → async_added_to_hass()
      → api.get_update_state() once
          → not STANDBY: _update_in_progress=True, start task
          → STANDBY / error: stay idle

Entity removal:
  → async_will_remove_from_hass()
      → cancel _update_task
```

### Concurrency Notes

- Only one polling task exists per entity at a time. `async_install` refuses
  to start a second one (guard F).
- `asyncio.create_task` is used (not `hass.async_create_task`) so the task is
  bound to the entity's lifecycle, not the global loop, simplifying cleanup.
- All writes to the internal state fields happen on the event loop; no locks
  needed (single-threaded asyncio).

## Testing

Extend `tests/test_update_entity.py`. Required cases:

1. **`async_install` sets in_progress and starts task** — with mocked
   `init_update` returning `"STARTING"`, after `async_install`:
   `_update_in_progress` is True, `_update_task` is not None and not done.
2. **Double-click guard** — calling `async_install` while
   `_update_in_progress` is True raises `HomeAssistantError` and does **not**
   call `init_update` a second time.
3. **External-update guard** — `get_update_state` returns a non-`STANDBY`
   value at install time; `async_install` raises `HomeAssistantError`, sets
   `_update_in_progress=True`, starts the polling task, and does **not** call
   `init_update`.
4. **Polling progress** — `get_update_state` returns a progress string
   containing a percentage; `_update_progress` and `_update_status_text` are
   set correctly, `async_write_ha_state` is called.
5. **Polling completion** — `get_update_state` returns `STANDBY` on a later
   iteration; the task ends, `_update_in_progress` is reset to False,
   `coordinator.async_request_refresh` is awaited.
6. **Polling resilience** — `get_update_state` raises `VioletPoolAPIError`
   once mid-loop; the task does **not** crash, continues to the next
   iteration.
7. **Startup detection** — `async_added_to_hass` with `get_update_state`
   returning non-`STANDBY` starts the polling task; returning `STANDBY` does
   not.
8. **Cleanup** — `async_will_remove_from_hass` cancels a running task.
9. **Safety-net** — task running past 10 minutes aborts and resets state.

Tests must mock `asyncio.sleep` (or use a fake clock / `asyncio.Future`-based
loop exit) so they don't actually wait 5 seconds.

## Risks

- **`get_update_state` response format is undocumented in the integration.**
  The library docstring says it tails `/home/violet/log/update.log` and
  returns `STANDBY` when idle. The percentage regex is best-effort; if the log
  format doesn't contain percentages, we degrade gracefully to status-only.
  No correctness risk — just less granular UI.
- **10-minute safety net** could falsely abort a very slow update. The user
  reported 2–3 minutes typical, so 10 minutes is a comfortable upper bound.
  Configurable later if needed (YAGNI for now).
- **Task leak on unexpected exceptions in `async_install`.** Mitigated by
  starting the task only after `init_update` succeeds.
