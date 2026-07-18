# Firmware Update Progress Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the user real-time feedback during a Violet Pool Controller firmware update and prevent double-clicking the install button.

**Architecture:** Replace the dead `SYSTEM_UPDATE_IN_PROGRESS` lookup with an entity-local polling task that drives `in_progress`, a status string, and a best-effort percentage from the controller's `get_update_state()` endpoint. Add `UpdateEntityFeature.PROGRESS`. Guard `async_install` against concurrent installs. Detect a running update at entity startup so the state survives HA reloads.

**Tech Stack:** Python 3.12, Home Assistant 2026.5.0+ (`UpdateEntity`, `UpdateEntityFeature`), `violet_poolcontroller_api` (`get_update_state`, `init_update`), pytest + pytest-asyncio (`asyncio_mode = auto`).

## Global Constraints

- Minimum HA version: `2026.5.0` (from `hacs.json`).
- Minimum Python: 3.12.
- Test framework: pytest with `asyncio_mode = auto`; async tests use `@pytest.mark.asyncio` (project convention — see `tests/test_discovery.py`).
- API client is imported as `from violet_poolcontroller_api import VioletPoolAPIError`.
- Coordinator access: `self.coordinator.device.api` (the `VioletPoolAPI` instance) and `self.coordinator.async_request_refresh()`.
- Lint: `ruff check custom_components/violet_pool_controller/` and `ruff check tests/` must pass.
- Spec: `docs/superpowers/specs/2026-07-18-update-progress-feedback-design.md`.
- Polling cadence: 5 seconds. Safety-net lifetime: 10 minutes.
- Status display during install: layered into `release_summary`.
- Repo-local git identity is already configured (`Basti <89860334+Xerolux@users.noreply.github.com>`).

---

## File Structure

**Modified:**
- `custom_components/violet_pool_controller/update.py` — the single integration source file touched. All entity logic lives here (state fields, polling task, guards, startup detection, cleanup, layered `release_summary`).
- `tests/test_update_entity.py` — extend with async tests for install/poll/startup/cleanup.

**Created:** none.

**Not touched (per spec YAGNI):** `device.py`, `update_helper.py`, coordinator, translations, sensors.

---

### Task 1: Add `UpdateEntityFeature.PROGRESS` and internal state fields

Establishes the data the rest of the feature reads and writes. Ends with the entity carrying the new fields and advertising `PROGRESS`, but no behaviour change yet (so existing tests still pass).

**Files:**
- Modify: `custom_components/violet_pool_controller/update.py`

**Interfaces:**
- Produces: `VioletPoolControllerUpdateEntity._update_in_progress`, `._update_progress`, `._update_status_text`, `._update_task` (instance attributes, initialized in `__init__`). Later tasks read/write these names verbatim.

- [ ] **Step 1: Add `asyncio` import and extend `_attr_supported_features`**

In `custom_components/violet_pool_controller/update.py`, add `import asyncio` at the top (after `from __future__ import annotations`, before `import logging`).

Then change the `_attr_supported_features` line in the class body from:

```python
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES
```

to:

```python
    _attr_supported_features = (
        UpdateEntityFeature.INSTALL
        | UpdateEntityFeature.RELEASE_NOTES
        | UpdateEntityFeature.PROGRESS
    )
```

- [ ] **Step 2: Initialize the new state fields in `__init__`**

In the `__init__` method, after the line `self._release_notes_cache: str = ""`, add:

```python
        # Live update state — driven by the polling task in _poll_update_state.
        self._update_in_progress: bool = False
        self._update_progress: int | None = None
        self._update_status_text: str | None = None
        self._update_task: asyncio.Task[None] | None = None
```

- [ ] **Step 3: Run the existing tests to confirm no regression**

Run: `python -m pytest tests/test_update_entity.py -v`
Expected: all 4 existing tests PASS (they don't reference the new fields).

- [ ] **Step 4: Lint the file**

Run: `python -m ruff check custom_components/violet_pool_controller/update.py`
Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add custom_components/violet_pool_controller/update.py
git commit -m "feat(update): add PROGRESS feature flag and update-state fields"
```

---

### Task 2: Rewrite `in_progress` and layer status into `release_summary`

Switches `in_progress` to read the real local flag (Task 1's `_update_in_progress`) instead of the never-written `SYSTEM_UPDATE_IN_PROGRESS` key. Layers live status text into `release_summary` during the install window.

**Files:**
- Modify: `custom_components/violet_pool_controller/update.py`
- Test: `tests/test_update_entity.py`

**Interfaces:**
- Produces: `VioletPoolControllerUpdateEntity.in_progress` now returns `self._update_in_progress`. `release_summary` returns a live status string while `_update_in_progress` is True.
- Consumes: `_update_in_progress`, `_update_status_text` (from Task 1).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_update_entity.py`:

```python
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

    # Idle: shows the normal update_description.
    idle_summary = entity.release_summary
    assert idle_summary is None or "läuft" not in (idle_summary or "")

    # While updating: status text takes precedence.
    entity._update_in_progress = True
    entity._update_status_text = "downloading package (42%)"
    assert entity.release_summary == "Update läuft: downloading package (42%)"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_update_entity.py::test_in_progress_reflects_local_flag tests/test_update_entity.py::test_release_summary_shows_live_status_while_updating -v`
Expected: both FAIL (`test_in_progress_reflects_local_flag` fails because `in_progress` still returns the old `SYSTEM_UPDATE_IN_PROGRESS` lookup; `test_release_summary_shows_live_status_while_updating` fails because `release_summary` returns the idle value).

- [ ] **Step 3: Rewrite `in_progress`**

Replace the existing `in_progress` property body in `update.py`:

```python
    @property
    def in_progress(self) -> bool:
        """Return True while an update is being installed."""
        if not self.coordinator.data:
            return False
        return bool(self.coordinator.data.get("SYSTEM_UPDATE_IN_PROGRESS", False))
```

with:

```python
    @property
    def in_progress(self) -> bool:
        """Return True while a firmware update is being installed.

        Driven by the entity-local _update_in_progress flag, which is set by
        async_install and refreshed by the _poll_update_state task.
        """
        return self._update_in_progress
```

- [ ] **Step 4: Layer live status into `release_summary`**

Replace the existing `release_summary` property body:

```python
    @property
    def release_summary(self) -> str | None:
        """Return brief update status (release notes are in async_release_notes)."""
        if not self.coordinator.data:
            return None
        info = parse_firmware_info(self.coordinator.data)
        return info.update_description
```

with:

```python
    @property
    def release_summary(self) -> str | None:
        """Return brief update status.

        While a firmware update is in progress, return the live status text
        from the controller. Otherwise return the update description (release
        notes are fetched on demand in async_release_notes).
        """
        if self._update_in_progress and self._update_status_text:
            return f"Update läuft: {self._update_status_text}"
        if not self.coordinator.data:
            return None
        info = parse_firmware_info(self.coordinator.data)
        return info.update_description
```

- [ ] **Step 5: Run the targeted tests to verify they pass**

Run: `python -m pytest tests/test_update_entity.py::test_in_progress_reflects_local_flag tests/test_update_entity.py::test_release_summary_shows_live_status_while_updating -v`
Expected: both PASS.

- [ ] **Step 6: Run the full update test file**

Run: `python -m pytest tests/test_update_entity.py -v`
Expected: all tests PASS (including the 4 original ones).

- [ ] **Step 7: Lint**

Run: `python -m ruff check custom_components/violet_pool_controller/update.py tests/test_update_entity.py`
Expected: no errors.

- [ ] **Step 8: Commit**

```bash
git add custom_components/violet_pool_controller/update.py tests/test_update_entity.py
git commit -m "feat(update): drive in_progress from local flag, show live status"
```

---

### Task 3: Implement `_parse_update_progress` helper

Small, pure helper that extracts a best-effort percentage from a `get_update_state()` response. Isolated so the polling task (Task 4) stays readable and the parser is unit-testable on its own.

**Files:**
- Modify: `custom_components/violet_pool_controller/update.py`
- Test: `tests/test_update_entity.py`

**Interfaces:**
- Produces: module-level function `_parse_update_progress(state: str) -> int | None` in `update.py`. Returns an int in [0, 100] if a percentage is found, else `None`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_update_entity.py`:

```python
from custom_components.violet_pool_controller.update import _parse_update_progress


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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_update_entity.py -k parse_update_progress -v`
Expected: all 4 FAIL with import error / `None != 42` etc.

- [ ] **Step 3: Implement the helper**

In `custom_components/violet_pool_controller/update.py`, add `import re` near the top imports, then add this module-level function below the `_LOGGER = ...` line and above `async def async_setup_entry`:

```python
_PROGRESS_RE = re.compile(r"(\d+)\s*%")


def _parse_update_progress(state: str) -> int | None:
    """Extract a best-effort percentage from an update-state string.

    The controller writes progress lines to /home/violet/log/update.log.
    Returns an int in [0, 100] if a percentage is found, else None.
    """
    match = _PROGRESS_RE.search(state)
    if not match:
        return None
    value = int(match.group(1))
    if value > 100:
        return 100
    return value
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_update_entity.py -k parse_update_progress -v`
Expected: all 4 PASS.

- [ ] **Step 5: Lint**

Run: `python -m ruff check custom_components/violet_pool_controller/update.py tests/test_update_entity.py`
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add custom_components/violet_pool_controller/update.py tests/test_update_entity.py
git commit -m "feat(update): add _parse_update_progress helper"
```

---

### Task 4: Implement the polling task `_poll_update_state`

The core of the feature. Loops every 5 s calling `get_update_state()`, updates the local fields, and ends when the controller reports `STANDBY` or when the 10-minute safety net is hit. Resilient to transient API errors.

**Files:**
- Modify: `custom_components/violet_pool_controller/update.py`
- Test: `tests/test_update_entity.py`

**Interfaces:**
- Consumes: `_parse_update_progress` (Task 3), `_update_in_progress` / `_update_progress` / `_update_status_text` (Task 1), `self.coordinator.device.api.get_update_state()`, `self.coordinator.async_request_refresh()`, `self.async_write_ha_state()`.
- Produces: `VioletPoolControllerUpdateEntity._poll_update_state()` coroutine. Sets `_update_in_progress = False` and clears the other fields on completion.

- [ ] **Step 1: Update test imports**

In `tests/test_update_entity.py`, replace the existing first import line:

```python
from unittest.mock import MagicMock
```

with:

```python
import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from violet_poolcontroller_api import VioletPoolAPIError

from homeassistant.exceptions import HomeAssistantError
```

These imports are used by the async tests in Tasks 4, 5, and 6. (`HomeAssistantError` and `VioletPoolAPIError` are used from Task 4 onward.)

- [ ] **Step 2: Write the failing tests**

Append to `tests/test_update_entity.py`:

```python
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

    try:
        await entity._poll_update_state()
    except asyncio.CancelledError:
        pass

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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_update_entity.py -k poll -v`
Expected: all 4 FAIL (AttributeError: `_poll_update_state` does not exist). Note: `test_poll_resilient_to_transient_api_error` requires `VioletPoolAPIError` imported in Step 1 of this task.

- [ ] **Step 3: Add poll-interval class constants**

In `VioletPoolControllerUpdateEntity` in `update.py`, add these two class-level constants immediately after the `_attr_entity_category = None` line:

```python
    # Update-state polling cadence (seconds) and maximum task lifetime before
    # the safety net aborts. Exposed as class constants so tests can shrink them.
    _UPDATE_POLL_INTERVAL = 5
    _UPDATE_MAX_LIFETIME = 600  # 10 minutes
```

- [ ] **Step 4: Implement `_poll_update_state`**

Add this method to `VioletPoolControllerUpdateEntity` in `update.py` (place it immediately before `async def async_release_notes`):

```python
    async def _poll_update_state(self) -> None:
        """Poll the controller for live update status until STANDBY or timeout.

        Runs as a background task after async_install or after startup detection.
        Updates _update_in_progress, _update_progress, and _update_status_text
        and writes HA state on each iteration. Resilient to transient errors.
        """
        interval = self._UPDATE_POLL_INTERVAL
        elapsed = 0

        while elapsed <= self._UPDATE_MAX_LIFETIME:
            try:
                state = await self.coordinator.device.api.get_update_state()
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001
                # Controller is briefly unreachable during its restart — keep polling.
                _LOGGER.debug(
                    "Transient error polling update state on %s: %s",
                    self.coordinator.device.device_name,
                    err,
                )
                await asyncio.sleep(interval)
                elapsed += interval
                continue

            normalized = (state or "").strip()
            if normalized.upper() == "STANDBY":
                self._update_in_progress = False
                self._update_progress = None
                self._update_status_text = None
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
                return

            self._update_in_progress = True
            self._update_progress = _parse_update_progress(normalized)
            self._update_status_text = normalized
            self.async_write_ha_state()

            await asyncio.sleep(interval)
            elapsed += interval

        # Safety net: exceeded max lifetime without reaching STANDBY.
        _LOGGER.error(
            "Firmware update on %s did not reach STANDBY within %d seconds; "
            "aborting progress tracking",
            self.coordinator.device.device_name,
            self._UPDATE_MAX_LIFETIME,
        )
        self._update_in_progress = False
        self._update_progress = None
        self._update_status_text = None
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/test_update_entity.py -k poll -v`
Expected: all 4 PASS.

- [ ] **Step 6: Run the full update test file**

Run: `python -m pytest tests/test_update_entity.py -v`
Expected: all tests PASS.

- [ ] **Step 7: Lint**

Run: `python -m ruff check custom_components/violet_pool_controller/update.py tests/test_update_entity.py`
Expected: no errors.

- [ ] **Step 8: Commit**

```bash
git add custom_components/violet_pool_controller/update.py tests/test_update_entity.py
git commit -m "feat(update): poll get_update_state until STANDBY with safety net"
```

---

### Task 5: Double-click guard in `async_install`

Refuses to start a second install while one is already running locally, and probes the controller in case an update was started externally. On success, sets `_update_in_progress` and starts the polling task.

**Files:**
- Modify: `custom_components/violet_pool_controller/update.py`
- Test: `tests/test_update_entity.py`

**Interfaces:**
- Consumes: `_poll_update_state` (Task 4), `_update_in_progress` / `_update_task` (Task 1), `self.coordinator.device.api.init_update()`, `self.coordinator.device.api.get_update_state()`.
- Produces: `async_install` sets `_update_in_progress = True` and `_update_task` on success, and raises `HomeAssistantError` on a concurrent install.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_update_entity.py`. (The `HomeAssistantError`, `AsyncMock`, and `asyncio` imports were added in Task 4 Step 1.)

```python
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
    try:
        await entity._update_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_async_install_starts_polling_on_success() -> None:
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

    await entity.async_install(version="1.2.0", backup=False)

    assert entity._update_in_progress is True
    assert entity._update_task is not None
    # Let the task run to STANDBY and finish.
    await entity._update_task
    assert entity._update_in_progress is False
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_update_entity.py -k async_install -v`
Expected: all 3 FAIL (current `async_install` does not guard, does not start a task).

- [ ] **Step 3: Rewrite `async_install`**

Replace the entire `async_install` method in `update.py`:

```python
    async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
        """Trigger firmware update on the controller.

        The controller downloads and installs the update via
        GET /initUpdate and then restarts (~30 seconds offline).
        Refuses to start a second install while one is already running.
        """
        # Guard 1: already tracking a local install.
        if self._update_in_progress:
            raise HomeAssistantError(
                "Update läuft bereits auf der Steuerung"
            )

        try:
            # Guard 2: an update may have been started externally (another client,
            # a previous crashed task). Probe the controller before triggering.
            current_state = await self.coordinator.device.api.get_update_state()
            if (current_state or "").strip().upper() != "STANDBY":
                _LOGGER.warning(
                    "Update on %s already in progress (state=%s); starting progress tracking",
                    self.coordinator.device.device_name,
                    current_state,
                )
                self._update_in_progress = True
                self._update_status_text = (current_state or "").strip()
                self._update_progress = _parse_update_progress(self._update_status_text or "")
                self.async_write_ha_state()
                self._update_task = asyncio.create_task(self._poll_update_state())
                raise HomeAssistantError(
                    "Update läuft bereits auf der Steuerung"
                )

            _LOGGER.info(
                "Triggering firmware update on %s",
                self.coordinator.device.device_name,
            )

            response = await self.coordinator.device.api.init_update()

            if response and response != "STARTING":
                _LOGGER.warning("Unexpected update response: %s", response)

            _LOGGER.info(
                "Firmware update initiated on %s. Device will restart in ~30 seconds.",
                self.coordinator.device.device_name,
            )

            self._update_in_progress = True
            self._update_status_text = "initiiert"
            self._update_progress = None
            self.async_write_ha_state()
            self._update_task = asyncio.create_task(self._poll_update_state())

            await self.coordinator.async_request_refresh()

        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.error("Failed to initiate firmware update: %s", err)
            raise HomeAssistantError(f"Firmware update failed: {err}") from err
```

- [ ] **Step 4: Run the targeted tests to verify they pass**

Run: `python -m pytest tests/test_update_entity.py -k async_install -v`
Expected: all 3 PASS.

- [ ] **Step 5: Run the full update test file**

Run: `python -m pytest tests/test_update_entity.py -v`
Expected: all tests PASS.

- [ ] **Step 6: Lint**

Run: `python -m ruff check custom_components/violet_pool_controller/update.py tests/test_update_entity.py`
Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add custom_components/violet_pool_controller/update.py tests/test_update_entity.py
git commit -m "feat(update): guard async_install against concurrent installs"
```

---

### Task 6: Startup detection and cleanup

Survive HA reload/restart mid-update: on entity add, probe the controller once and start the polling task if it is mid-update. On entity removal, cancel the polling task.

**Files:**
- Modify: `custom_components/violet_pool_controller/update.py`
- Test: `tests/test_update_entity.py`

**Interfaces:**
- Consumes: `_poll_update_state` (Task 4), `self.coordinator.device.api.get_update_state()`, `self._update_task` (Task 1).
- Produces: overrides of `async_added_to_hass` and `async_will_remove_from_hass`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_update_entity.py`. (Imports from Task 4 Step 1 already cover everything here.)

```python
async def _run_added_to_hass(entity: VioletPoolControllerUpdateEntity) -> None:
    """Call async_added_to_hass while bypassing the CoordinatorEntity super() call.

    CoordinatorEntity.async_added_to_hass requires a real hass runtime; the
    bypass lets us exercise our override's startup-detection logic in isolation.
    """
    from custom_components.violet_pool_controller import update as update_mod

    captured = {}

    async def fake_super_added(self: object) -> None:
        captured["called"] = True

    monkey_target = update_mod.CoordinatorEntity
    original = monkey_target.async_added_to_hass
    monkey_target.async_added_to_hass = fake_super_added  # type: ignore[assignment]
    try:
        await entity.async_added_to_hass()
    finally:
        monkey_target.async_added_to_hass = original  # type: ignore[assignment]
    assert captured.get("called") is True


@pytest.mark.asyncio
async def test_startup_detects_running_update() -> None:
    """async_added_to_hass starts polling if the controller is mid-update."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})

    async def fake_get_update_state() -> str:
        return "installing modules (60%)"

    coordinator.device.api.get_update_state = fake_get_update_state
    coordinator.async_request_refresh = AsyncMock()

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)

    await _run_added_to_hass(entity)

    assert entity._update_in_progress is True
    assert entity._update_status_text == "installing modules (60%)"
    assert entity._update_progress == 60
    assert entity._update_task is not None
    entity._update_task.cancel()
    try:
        await entity._update_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_startup_idle_when_standby() -> None:
    """async_added_to_hass does not start a task when the controller is idle."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})

    async def fake_get_update_state() -> str:
        return "STANDBY"

    coordinator.device.api.get_update_state = fake_get_update_state

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)

    await _run_added_to_hass(entity)

    assert entity._update_in_progress is False
    assert entity._update_task is None


@pytest.mark.asyncio
async def test_startup_probes_silently_fail() -> None:
    """A probe error at startup does not break entity setup."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})

    async def fake_get_update_state() -> str:
        raise VioletPoolAPIError("controller unreachable at startup")

    coordinator.device.api.get_update_state = fake_get_update_state

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)

    await _run_added_to_hass(entity)  # must not raise

    assert entity._update_in_progress is False
    assert entity._update_task is None


@pytest.mark.asyncio
async def test_will_remove_cancels_polling_task() -> None:
    """async_will_remove_from_hass cancels a running polling task."""
    coordinator = _make_coordinator({"SYSTEM_swversion": "1.1.9"})

    async def fake_get_update_state() -> str:
        await asyncio.sleep(30)  # never returns during the test
        return "STANDBY"

    coordinator.device.api.get_update_state = fake_get_update_state
    coordinator.async_request_refresh = AsyncMock()

    entity = VioletPoolControllerUpdateEntity(coordinator, _make_config_entry())
    _stub_entity_for_async(entity)
    entity._update_in_progress = True
    entity._update_task = asyncio.create_task(entity._poll_update_state())

    # Let the loop enter the first get_update_state call.
    await asyncio.sleep(0)

    # Bypass the CoordinatorEntity super() for the will-remove path too.
    from custom_components.violet_pool_controller import update as update_mod

    async def _noop_will_remove(self: object) -> None:
        return None

    original = update_mod.CoordinatorEntity.async_will_remove_from_hass
    update_mod.CoordinatorEntity.async_will_remove_from_hass = _noop_will_remove  # type: ignore[assignment]
    try:
        await entity.async_will_remove_from_hass()
    finally:
        update_mod.CoordinatorEntity.async_will_remove_from_hass = original  # type: ignore[assignment]

    assert entity._update_task is not None
    assert entity._update_task.cancelled() is True
    assert entity._update_in_progress is False
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_update_entity.py -k 'startup or will_remove' -v`
Expected: all 3 FAIL (`async_added_to_hass` / `async_will_remove_from_hass` not overridden).

- [ ] **Step 3: Implement the two overrides**

Add these methods to `VioletPoolControllerUpdateEntity` in `update.py`, placing them immediately after `_poll_update_state`:

```python
    async def async_added_to_hass(self) -> None:
        """Run when entity is added to HA.

        Probe the controller once: if an update is already in progress (e.g.
        after an HA restart or integration reload mid-update), start polling.
        """
        await super().async_added_to_hass()
        try:
            state = await self.coordinator.device.api.get_update_state()
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Could not probe update state at startup for %s: %s",
                self.coordinator.device.device_name,
                err,
            )
            return

        normalized = (state or "").strip()
        if normalized.upper() != "STANDBY":
            _LOGGER.info(
                "Detected in-progress firmware update on %s at startup (state=%s); "
                "resuming progress tracking",
                self.coordinator.device.device_name,
                normalized,
            )
            self._update_in_progress = True
            self._update_status_text = normalized
            self._update_progress = _parse_update_progress(normalized)
            self.async_write_ha_state()
            self._update_task = asyncio.create_task(self._poll_update_state())

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity is removed from HA. Cancel any running polling task."""
        task = self._update_task
        if task is not None and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._update_in_progress = False
        await super().async_will_remove_from_hass()
```

- [ ] **Step 4: Run the targeted tests to verify they pass**

Run: `python -m pytest tests/test_update_entity.py -k 'startup or will_remove' -v`
Expected: all 3 PASS.

- [ ] **Step 5: Run the full update test file**

Run: `python -m pytest tests/test_update_entity.py -v`
Expected: all tests PASS.

- [ ] **Step 6: Lint**

Run: `python -m ruff check custom_components/violet_pool_controller/update.py tests/test_update_entity.py`
Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add custom_components/violet_pool_controller/update.py tests/test_update_entity.py
git commit -m "feat(update): detect in-progress update at startup, clean up on remove"
```

---

### Task 7: Final verification and CHANGELOG note

Run the whole suite + lint, then update `CHANGELOG.md` with a user-facing entry describing the fix.

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Run the entire test suite**

Run: `python -m pytest tests/ -q`
Expected: all tests PASS, no collection errors.

- [ ] **Step 2: Lint the whole integration and tests**

Run: `python -m ruff check custom_components/violet_pool_controller/ tests/`
Expected: no errors.

- [ ] **Step 3: Read the top of CHANGELOG.md**

Run: `head -60 CHANGELOG.md`
Identify the current `[Unreleased]` section (or the most recent version section) and the format used for entries.

- [ ] **Step 4: Add a CHANGELOG entry**

Under the `[Unreleased]` heading (or the current beta section if no `[Unreleased]` exists), add a bullet following the existing style. Use the existing tense and prefix convention (e.g. `### Changed`, `### Fixed`). Example, adapted to the file's actual heading style:

```markdown
### Fixed
- Firmware-Update: Der "Aktualisieren"-Button bleibt während des 2–3 minütigen Updates deaktiviert und zeigt den Live-Status der Steuerung an. Mehrfaches Klicken wird verhindert.
```

If the file uses English entries, mirror that instead. Match the surrounding format exactly.

- [ ] **Step 5: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): note firmware update progress feedback"
```

---

## Verification Summary

After Task 7, the feature is complete and verified:

- `UpdateEntityFeature.PROGRESS` is advertised → HA renders progress UI and disables the button while `in_progress` is True.
- `in_progress` reflects the real local flag, driven by the polling task.
- `release_summary` shows `Update läuft: <status>` during the install.
- `async_install` refuses double-clicks and external concurrent installs with a `HomeAssistantError`.
- The polling task updates status/percentage every 5 s, ends on `STANDBY`, survives transient errors, and aborts after 10 min as a safety net.
- Startup detection resumes tracking after an HA reload mid-update.
- Entity removal cancels the polling task cleanly.
- Full test suite + ruff pass.
