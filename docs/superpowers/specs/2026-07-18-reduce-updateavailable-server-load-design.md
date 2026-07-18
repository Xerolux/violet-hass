# Reduce SYSTEM_updateavailable Server Load — Design

**Date:** 2026-07-18
**Status:** Approved (verbal) — pending spec review
**Scope:** `custom_components/violet_pool_controller/device.py`, `const.py`, and tests
**Reported by:** Controller manufacturer (PoolDigital)

## Problem

The coordinator polls `getConfig` every cycle (default `DEFAULT_POLLING_INTERVAL = 10`
seconds, `const.py:93`) with three firmware keys: `SYSTEM_swversion`,
`SYSTEM_availableversion`, `SYSTEM_updateavailable`. Per the manufacturer:

- `SYSTEM_updateavailable` triggers a **live backend server query** on every request.
- The controller itself only checks for updates every ~12 hours or on manual
  user invocation (SYSTEM -> UPDATE).

With many devices × 6 polls/minute, the integration generates heavy, unnecessary
server load. Worse: the value of `SYSTEM_updateavailable` is **never consumed**
by any code. The update-availability decision is already made by a numeric
version comparison (`SYSTEM_availableversion` > `SYSTEM_swversion`) in
`update_helper.py:32-44`. The flag is pure waste on the wire.

`SYSTEM_availableversion` also pulls a server-fresh value; the manufacturer
confirmed they want this throttled, not just the flag removed.

## Goal

Eliminate the live backend query entirely and throttle the server-side version
fetch to once per hour. Preserve correct update-availability UX (just refreshed
hourly instead of every 10s — acceptable for firmware checks).

## Non-Goals (YAGNI)

- No on-demand "check for update now" feature.
- No user-facing config option for the interval (constant only; can be added
  later if requested).
- No persistence of the poll counter across reloads.
- No change to the API library (`violet-poolController-api` is a clean
  `getConfig` passthrough — verified, no `SYSTEM_updateavailable` references in
  library source).
- No change to `update_helper.py` comparison logic (already correct).

## Architecture Decision

**In-coordinator poll counter (Option A).** The coordinator already runs the
poll loop, so adding a counter and conditionally including `SYSTEM_availableversion`
in the `config_keys` list is the smallest, most isolated change. No new task,
no second coordinator, no threading risk. `SYSTEM_swversion` stays in every
poll because the coordinator uses it for device-registry resolution
(`device.py:518-530`) — removing it would require special-casing there without
saving server load (it's a local cached value, not a live trigger).

Rejected alternatives:
- Separate slow coordinator (Option B): too much boilerplate for one key.
- On-demand only (Option C): poor UX, users could go days without learning an
  update is available.

## Design

### Components

**A. New constant in `const.py`**

```python
# How often (in poll cycles) to fetch SYSTEM_availableversion from the
# controller. The controller refreshes this server-side value, and fetching it
# every poll causes avoidable backend load. At the default 10s polling
# interval, 360 = once per hour.
FIRMWARE_VERSION_REFRESH_POLLS = 360
```

**B. Poll counter in `VioletPoolControllerDevice` (`device.py`)**

Add `self._firmware_version_poll_counter: int = 0` in `__init__`.

**C. Dynamic `config_keys` in `_async_update_data` (`device.py:465-494`)**

Replace the static list with a dynamically-built one:

- Always include `SYSTEM_swversion` (cheap, used by device-registry resolution).
- Include `SYSTEM_availableversion` only when
  `self._firmware_version_poll_counter % FIRMWARE_VERSION_REFRESH_POLLS == 0`
  — i.e., on the first poll after start (counter == 0) and then once per hour.
- **Never include `SYSTEM_updateavailable`** (removed entirely).
- Increment `self._firmware_version_poll_counter` after building the list.

The block currently looks like:

```python
config_keys = [
    "HEATER_set_temp",
    "SOLAR_maxtemp",
    "DOSAGE_phminus_setpoint",
    "DOSAGE_chlorine_setpoint_orp",
    "DOSAGE_chlorine_lowerval_cl",
    "DOSAGE_chlorine_use",
    "DOSAGE_electrolysis_use",
    "DOSAGE_phminus_use",
    "DOSAGE_phplus_use",
    "DOSAGE_floc_use",
    "SYSTEM_swversion",
    "SYSTEM_availableversion",
    "SYSTEM_updateavailable",
]
config_data = await self.api.get_config(config_keys)
```

Becomes:

```python
config_keys = [
    "HEATER_set_temp",
    "SOLAR_maxtemp",
    "DOSAGE_phminus_setpoint",
    "DOSAGE_chlorine_setpoint_orp",
    "DOSAGE_chlorine_lowerval_cl",
    "DOSAGE_chlorine_use",
    "DOSAGE_electrolysis_use",
    "DOSAGE_phminus_use",
    "DOSAGE_phplus_use",
    "DOSAGE_floc_use",
    "SYSTEM_swversion",
]
# SYSTEM_availableversion triggers a server-side refresh on the controller.
# Fetch it infrequently (hourly at default 10s polling) to avoid load.
# SYSTEM_updateavailable is intentionally NOT requested: it forces a live
# backend check and its value is never consumed — the update-available
# decision is made by numeric version comparison in update_helper.py.
if self._firmware_version_poll_counter % FIRMWARE_VERSION_REFRESH_POLLS == 0:
    config_keys.append("SYSTEM_availableversion")
self._firmware_version_poll_counter += 1
config_data = await self.api.get_config(config_keys)
```

**D. No change to `update_helper.py` or `update.py`.**

`parse_firmware_info` already treats missing/empty `SYSTEM_availableversion`
gracefully (`available_version` → `None`, `update_available` → `False`,
`latest_version` falls back to `installed_version`). On polls where the key is
not fetched, the previous value simply stays in `coordinator.data` (dict
merge keeps prior keys), so the update entity shows the last known state — no
flicker.

### Data Flow

```
Every poll (~10s):
  → build config_keys (always: swversion + setpoints)
  → if counter % 360 == 0: also append availableversion
  → counter += 1
  → getConfig -> merge into coordinator.data
  → update entity reads installed/available, compares numerically
```

Between hourly fetches, `coordinator.data["SYSTEM_availableversion"]` retains
its previous value (dict update merges, doesn't clear), so the update entity
keeps showing the last-known state without flicker.

### Edge Cases

- **First poll after start (counter == 0):** `availableversion` is fetched
  immediately → user sees current state within seconds of HA boot.
- **Coordinator reload:** counter resets to 0 in `__init__` → immediate fetch
  on first poll. No persistence needed (YAGNI).
- **Custom polling interval:** if a user sets `CONF_POLLING_INTERVAL = 30s`,
  `availableversion` is fetched every 360 × 30s = 3 hours. Trade-off owned by
  the user's own interval setting. Documented in the constant comment.
- **Empty/missing `SYSTEM_availableversion`:** handled by `parse_firmware_info`
  → no update shown until next hourly fetch succeeds.

## Testing

Extend `tests/` (likely `test_update_helper.py` or a coordinator test):

1. **`SYSTEM_updateavailable` is never in config_keys** — across 500 simulated
   polls, assert the key never appears in the `get_config` argument list.
2. **`SYSTEM_availableversion` cadence** — across 720 simulated polls,
   assert `availableversion` appears in `config_keys` exactly twice (counter
   == 0 and counter == 360). `SYSTEM_swversion` appears in all 720.
3. **First-poll immediate fetch** — counter == 0 → `availableversion` present.
4. **Counter increments** — after each poll, `_firmware_version_poll_counter`
   is one higher.
5. **Existing `test_update_helper.py` tests remain green** — comparison logic
   unchanged.

Tests will likely need a coordinator-level harness (or a direct test of the
`config_keys` construction logic) since the polling happens inside
`_async_update_data`. If the list-building is extracted into a small helper
method (e.g. `_build_config_keys() -> list[str]`), it becomes trivially
unit-testable without running the full coordinator — preferred for testability.

## Risks

- **Stale `availableversion` for up to an hour.** Acceptable for firmware
  checks. Mitigated by immediate fetch on first poll and on every reload.
- **Behavioral change in `latest_version` refresh rate.** Users currently see
  new firmware within 10s of the server publishing it; now within an hour.
  This is the explicit goal (server load reduction), not a regression.
- **Counter not persisted across reloads** → re-fetches on every reload. By
  design; reloads are rare.

## Files Touched

- `custom_components/violet_pool_controller/const.py` — add constant.
- `custom_components/violet_pool_controller/device.py` — add counter field,
  dynamic `config_keys` construction, remove `SYSTEM_updateavailable`.
- `tests/` — new tests for the counter/cadence logic.
- `CHANGELOG.md` — entry under `[Unreleased]`.

## Out of Scope

- API library (`violet-poolController-api`) — needs no change.
- `update_helper.py` comparison logic — already correct.
- `update.py` entity logic — reads what the coordinator provides.
