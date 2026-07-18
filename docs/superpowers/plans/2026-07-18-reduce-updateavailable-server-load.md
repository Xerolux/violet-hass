# Reduce SYSTEM_updateavailable Server Load — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop requesting `SYSTEM_updateavailable` (triggers a live backend query every poll, value never consumed) and throttle `SYSTEM_availableversion` to once per hour via an in-coordinator poll counter.

**Architecture:** Extract the `config_keys` list-building into a pure, unit-testable method `_build_config_keys()` on `VioletPoolControllerDevice`. That method always includes setpoints + `SYSTEM_swversion`, conditionally appends `SYSTEM_availableversion` based on a poll counter, and never includes `SYSTEM_updateavailable`. The comparison logic in `update_helper.py` stays untouched (already correct).

**Tech Stack:** Python 3.12, Home Assistant 2026.5.0+, pytest + pytest-asyncio (`asyncio_mode = auto`), `pytest-homeassistant-custom-component`. API library `violet-poolController-api` is a clean `getConfig` passthrough — **no API change needed** (verified: zero `SYSTEM_updateavailable` references in library source).

## Global Constraints

- Default polling interval: `DEFAULT_POLLING_INTERVAL = 10` seconds (`const.py:93`).
- Firmware-version refresh cadence: once per hour → `FIRMWARE_VERSION_REFRESH_POLLS = 360` poll cycles.
- Test framework: pytest with `asyncio_mode = auto`; async tests use `@pytest.mark.asyncio`.
- Tests run via the `.venv-ha-test` venv: `.venv-ha-test/bin/python -m pytest ...` and `.venv-ha-test/bin/ruff check ...`.
- API access pattern: `self.api.get_config(list_of_keys)` returns a `dict`.
- Lint: `ruff check custom_components/violet_pool_controller/ tests/` must pass.
- Spec: `docs/superpowers/specs/2026-07-18-reduce-updateavailable-server-load-design.md`.
- Repo-local git identity already configured (`Basti <89860334+Xerolux@users.noreply.github.com>`).
- No change to `update_helper.py`, `update.py`, or the API library.

---

## File Structure

**Modified:**
- `custom_components/violet_pool_controller/const.py` — add `FIRMWARE_VERSION_REFRESH_POLLS` constant.
- `custom_components/violet_pool_controller/device.py` — add `_firmware_version_poll_counter` field in `__init__`, extract `_build_config_keys()` method, call it from `_async_update_data`, remove the static list with `SYSTEM_updateavailable`.
- `tests/test_device.py` — new tests for `_build_config_keys()` cadence and the never-request-`SYSTEM_updateavailable` invariant.
- `CHANGELOG.md` — entry under `[Unreleased]`.

**Created:** none.
**Not touched (per spec YAGNI):** `update_helper.py`, `update.py`, API library, translations, sensors.

---

### Task 1: Add `FIRMWARE_VERSION_REFRESH_POLLS` constant

Establishes the tunable that the next task's counter reads. Trivial, isolated, lands first so the next task can import it.

**Files:**
- Modify: `custom_components/violet_pool_controller/const.py`

**Interfaces:**
- Produces: `custom_components.violet_pool_controller.const.FIRMWARE_VERSION_REFRESH_POLLS` (int, value 360).

- [ ] **Step 1: Add the constant**

In `custom_components/violet_pool_controller/const.py`, immediately after the line `DEFAULT_POLLING_INTERVAL = 10` (currently at line 93), add:

```python
DEFAULT_POLLING_INTERVAL = 10
# How often (in poll cycles) to fetch SYSTEM_availableversion from the
# controller. The controller refreshes this server-side value, and fetching it
# every poll causes avoidable backend load (the controller otherwise only
# checks for updates every ~12h or on manual invocation). At the default 10s
# polling interval, 360 = once per hour.
FIRMWARE_VERSION_REFRESH_POLLS = 360
```

- [ ] **Step 2: Verify import works**

Run: `.venv-ha-test/bin/python -c "from custom_components.violet_pool_controller.const import FIRMWARE_VERSION_REFRESH_POLLS; print(FIRMWARE_VERSION_REFRESH_POLLS)"`
Expected: prints `360`.

- [ ] **Step 3: Lint**

Run: `.venv-ha-test/bin/ruff check custom_components/violet_pool_controller/const.py`
Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add custom_components/violet_pool_controller/const.py
git commit -m "feat(const): add FIRMWARE_VERSION_REFRESH_POLLS constant"
```

---

### Task 2: Add the firmware poll counter field

Adds the counter that drives the throttling decision. No behaviour change yet (the counter exists but nothing reads it).

**Files:**
- Modify: `custom_components/violet_pool_controller/device.py`

**Interfaces:**
- Produces: `VioletPoolControllerDevice._firmware_version_poll_counter` (int, initialized to 0). Task 3 reads and increments it.
- Consumes: nothing yet.

- [ ] **Step 1: Add the counter to `__init__`**

In `custom_components/violet_pool_controller/device.py`, in the `__init__` method of `VioletPoolControllerDevice`, immediately after the line `self._update_counter = 0` (currently at line 105), add:

```python
        self._update_counter = 0
        # Poll-cycle counter for throttling SYSTEM_availableversion fetches
        # (see _build_config_keys). Resets on every coordinator reload.
        self._firmware_version_poll_counter: int = 0
```

- [ ] **Step 2: Add the import of the constant**

In the same file, find the existing import block from `.const`. It currently imports things like `DOMAIN`, `DEFAULT_POLLING_INTERVAL`, etc. Add `FIRMWARE_VERSION_REFRESH_POLLS` to that import. The exact line looks like:

```python
from .const import (
    CONF_ACTIVE_FEATURES,
    ...
    DOMAIN,
)
```

Add `FIRMWARE_VERSION_REFRESH_POLLS,` to the list (keeping alphabetical order, which ruff's isort enforces — place it among the `F` entries or wherever the existing `DEFAULT_*` constants live).

- [ ] **Step 3: Verify the import resolves**

Run: `.venv-ha-test/bin/python -c "from custom_components.violet_pool_controller.device import VioletPoolControllerDevice; print('ok')"`
Expected: prints `ok` (no ImportError).

- [ ] **Step 4: Run existing device tests to confirm no regression**

Run: `.venv-ha-test/bin/python -m pytest tests/test_device.py -q`
Expected: all existing tests PASS (the counter is unused so far).

- [ ] **Step 5: Lint**

Run: `.venv-ha-test/bin/ruff check custom_components/violet_pool_controller/device.py`
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add custom_components/violet_pool_controller/device.py
git commit -m "feat(device): add firmware version poll counter field"
```

---

### Task 3: Extract `_build_config_keys()` and remove `SYSTEM_updateavailable`

The core change. Extracts the static list into a method that builds the keys dynamically: always includes setpoints + `SYSTEM_swversion`, appends `SYSTEM_availableversion` only when the counter hits the cadence, and never includes `SYSTEM_updateavailable`. The method increments the counter as a side effect (so callers don't forget).

**Files:**
- Modify: `custom_components/violet_pool_controller/device.py`
- Test: `tests/test_device.py`

**Interfaces:**
- Produces: `VioletPoolControllerDevice._build_config_keys(self) -> list[str]`. Pure-ish: reads `self._firmware_version_poll_counter`, increments it by 1, returns the key list. Never includes `"SYSTEM_updateavailable"`.
- Consumes: `FIRMWARE_VERSION_REFRESH_POLLS` (Task 1), `self._firmware_version_poll_counter` (Task 2).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_device.py`. First check the top-of-file imports — ensure `FIRMWARE_VERSION_REFRESH_POLLS` is imported from `.const` and `VioletPoolControllerDevice` from `.device` (the latter is already imported per the existing head shown in planning). Add the import line for the constant:

```python
from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
    FIRMWARE_VERSION_REFRESH_POLLS,
)
```

Then append these tests at the end of the file (outside any class, or inside `TestVioletPoolControllerDevice` — match the file's existing style; the file uses a class so add them as methods inside it):

```python
    def test_build_config_keys_always_includes_swversion_and_setpoints(self, mock_hass, mock_api):
        """Every poll must include swversion and the setpoint keys."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = 0
        keys = device._build_config_keys()

        assert "SYSTEM_swversion" in keys
        assert "HEATER_set_temp" in keys
        assert "DOSAGE_phminus_setpoint" in keys

    def test_build_config_keys_first_poll_includes_availableversion(self, mock_hass, mock_api):
        """Counter == 0 (first poll after start) fetches availableversion immediately."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = 0
        keys = device._build_config_keys()

        assert "SYSTEM_availableversion" in keys

    def test_build_config_keys_throttles_availableversion(self, mock_hass, mock_api):
        """availableversion is fetched only every FIRMWARE_VERSION_REFRESH_POLLS cycles."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = 1  # not a cadence boundary
        keys = device._build_config_keys()

        assert "SYSTEM_availableversion" not in keys

    def test_build_config_keys_availableversion_again_at_cadence(self, mock_hass, mock_api):
        """availableversion reappears exactly when counter hits a multiple of the cadence."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = FIRMWARE_VERSION_REFRESH_POLLS
        keys = device._build_config_keys()

        assert "SYSTEM_availableversion" in keys

    def test_build_config_keys_never_includes_updateavailable(self, mock_hass, mock_api):
        """The live-server-trigger flag must NEVER be requested (value never consumed)."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        # Sweep many cycles to be sure it never shows up regardless of counter.
        device._firmware_version_poll_counter = 0
        seen_keys = set()
        for _ in range(FIRMWARE_VERSION_REFRESH_POLLS + 5):
            seen_keys.update(device._build_config_keys())

        assert "SYSTEM_updateavailable" not in seen_keys

    def test_build_config_keys_increments_counter(self, mock_hass, mock_api):
        """Each call advances the counter by exactly 1."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = 0
        device._build_config_keys()
        device._build_config_keys()

        assert device._firmware_version_poll_counter == 2
```

Note on the `VioletPoolControllerDevice.__new__(...)` pattern: it constructs the instance without running `__init__` (which requires a live `hass`/`api`/`config_entry`). The method under test only reads/writes `_firmware_version_poll_counter`, so this lightweight construction is sufficient and matches the spec's preference for unit-testability of the list-building logic.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv-ha-test/bin/python -m pytest tests/test_device.py -k build_config_keys -v`
Expected: all 6 FAIL with `AttributeError: ... has no attribute '_build_config_keys'`.

- [ ] **Step 3: Add the `_build_config_keys` method**

In `custom_components/violet_pool_controller/device.py`, add this method to the `VioletPoolControllerDevice` class. Place it immediately above `async def _async_update_data` (find that method definition; the new method logically feeds it):

```python
    def _build_config_keys(self) -> list[str]:
        """Build the getConfig key list for the current poll cycle.

        Always includes the setpoint keys and SYSTEM_swversion (the latter is a
        local cached value used for device-registry resolution). SYSTEM_availableversion
        is appended only on the first poll and then once every
        FIRMWARE_VERSION_REFRESH_POLLS cycles, because fetching it triggers a
        server-side refresh on the controller. SYSTEM_updateavailable is NEVER
        requested: it forces a live backend check and its value is discarded —
        the update-available decision is made by numeric version comparison in
        update_helper.py.
        """
        keys = [
            # Setpoints (controller exposes these via getConfig, not getReadings)
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
            # Firmware version (local cached value, cheap to read every poll)
            "SYSTEM_swversion",
        ]
        if self._firmware_version_poll_counter % FIRMWARE_VERSION_REFRESH_POLLS == 0:
            keys.append("SYSTEM_availableversion")
        self._firmware_version_poll_counter += 1
        return keys
```

- [ ] **Step 4: Replace the static list in `_async_update_data`**

In `_async_update_data`, replace the static `config_keys = [...]` block (currently lines 467-484, from `config_keys = [` through the closing `]`) plus the line `config_data = await self.api.get_config(config_keys)` with:

```python
                # Fetch config-based setpoints and firmware version. The list is
                # built dynamically by _build_config_keys, which throttles
                # SYSTEM_availableversion and omits SYSTEM_updateavailable entirely
                # (both were causing avoidable backend server load).
                config_keys = self._build_config_keys()
                config_data = await self.api.get_config(config_keys)
                if isinstance(config_data, dict):
                    data.update(config_data)
```

Keep the surrounding `try`/`except asyncio.CancelledError`/`except Exception` exactly as-is — only the inner list construction is replaced.

- [ ] **Step 5: Run the new tests to verify they pass**

Run: `.venv-ha-test/bin/python -m pytest tests/test_device.py -k build_config_keys -v`
Expected: all 6 PASS.

- [ ] **Step 6: Run the full device test file**

Run: `.venv-ha-test/bin/python -m pytest tests/test_device.py -q`
Expected: all tests PASS (existing + new).

- [ ] **Step 7: Run update-related tests to confirm no regression**

Run: `.venv-ha-test/bin/python -m pytest tests/test_update_entity.py tests/test_update_helper.py -q`
Expected: all tests PASS.

- [ ] **Step 8: Lint**

Run: `.venv-ha-test/bin/ruff check custom_components/violet_pool_controller/device.py tests/test_device.py`
Expected: no errors.

- [ ] **Step 9: Commit**

```bash
git add custom_components/violet_pool_controller/device.py tests/test_device.py
git commit -m "feat(device): throttle SYSTEM_availableversion, drop SYSTEM_updateavailable

Extracts the getConfig key list into _build_config_keys(), which:
- always includes SYSTEM_swversion and the setpoint keys,
- appends SYSTEM_availableversion only on the first poll and then once
  per FIRMWARE_VERSION_REFRESH_POLLS (hourly at default 10s polling),
- never requests SYSTEM_updateavailable (it triggers a live backend
  query and its value was never consumed; update availability is decided
  by numeric version comparison in update_helper.py).

Reduces per-device backend server load from ~6 queries/minute to ~1/hour."
```

---

### Task 4: Final verification and CHANGELOG entry

Run the whole suite + lint, then add a user-facing CHANGELOG entry describing the server-load reduction.

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Run the entire test suite**

Run: `.venv-ha-test/bin/python -m pytest tests/ -q`
Expected: all tests PASS (no collection errors, no regressions).

- [ ] **Step 2: Lint the whole integration and tests**

Run: `.venv-ha-test/bin/ruff check custom_components/violet_pool_controller/ tests/`
Expected: no errors.

- [ ] **Step 3: Sanity-check the full multi-poll behaviour**

Run this one-off script to simulate 1000 polls and confirm the cadence end-to-end (this is a manual verification step, not a committed test):

```bash
.venv-ha-test/bin/python -c "
from custom_components.violet_pool_controller.const import FIRMWARE_VERSION_REFRESH_POLLS
from custom_components.violet_pool_controller.device import VioletPoolControllerDevice

device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
device._firmware_version_poll_counter = 0

n = 1000
av_hits = 0
ua_hits = 0
sw_hits = 0
for _ in range(n):
    keys = device._build_config_keys()
    if 'SYSTEM_availableversion' in keys: av_hits += 1
    if 'SYSTEM_updateavailable' in keys: ua_hits += 1
    if 'SYSTEM_swversion' in keys: sw_hits += 1

print(f'polls={n}')
print(f'SYSTEM_swversion hits: {sw_hits} (expected {n})')
print(f'SYSTEM_availableversion hits: {av_hits} (expected {n // FIRMWARE_VERSION_REFRESH_POLLS + 1})')
print(f'SYSTEM_updateavailable hits: {ua_hits} (expected 0)')
assert sw_hits == n
assert ua_hits == 0
assert av_hits == n // FIRMWARE_VERSION_REFRESH_POLLS + 1
print('OK')
"
```
Expected: prints `OK` (swversion every poll, updateavailable never, availableversion at the cadence rate).

- [ ] **Step 4: Add CHANGELOG entry**

In `CHANGELOG.md`, the top currently has a `## Version 2.3.0 (2026-07-18)` section (from the previous release). Add a new `[Unreleased]` section above it. Read the current top first:

Run: `head -8 CHANGELOG.md`

Then insert above the `## Version 2.3.0` line:

```markdown
## [Unreleased]

### 🔧 Technische Verbesserungen

- **Reduzierte Server-Last beim Firmware-Update-Check** - Die Integration fragt `SYSTEM_updateavailable` (löste bisher alle 10 Sekunden einen Live-Server-Check aus, Wert wurde nicht verwendet) gar nicht mehr ab und holt `SYSTEM_availableversion` nur noch stündlich statt alle 10 Sekunden. Die Update-Verfügbarkeit wird weiterhin zuverlässig über Versionsvergleich ermittelt. Entlastet das Violet-Backend bei vielen Geräten deutlich.

## Version 2.3.0 (2026-07-18)
```

Match the surrounding German style and emoji conventions (`### 🔧` for technical improvements, as used in prior sections).

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): note reduced update-check server load"
```

---

## Verification Summary

After Task 4, the change is complete and verified:

- `SYSTEM_updateavailable` is **never** present in `config_keys` (proven across 1000 simulated polls + a dedicated test).
- `SYSTEM_availableversion` is fetched on the first poll and then once per `FIRMWARE_VERSION_REFRESH_POLLS` (hourly at default polling).
- `SYSTEM_swversion` remains in every poll for device-registry resolution.
- The update entity continues to work via the unchanged numeric version comparison in `update_helper.py`.
- Full test suite + ruff pass.
- API library unchanged (no PR needed — verified zero references).
