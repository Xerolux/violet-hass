# Changelog

All notable changes to this project will be documented in this file.

## v0.0.31

### Fixes
- **fix: DIRULE template substitution bug** — `DEVICE_PARAMETERS["DIRULE_*"]["api_template"]` used `f"DIRULE_{{rule_num}},..."` with doubled braces, producing a literal `{rule_num}` in the URL payload and crashing `format_map()` with `KeyError: rule_num`. Fixed to match the EXT-bank template pattern (`f"DIRULE_{rule_num},{{action}},0,0"`).
- **fix: error code 0005 text + severity** — the entry claimed *"Wartungsarbeiten am Cloud-Server"* (INFO); the controller actually uses code 0005 as a generic system-status notification. Re-classified as REMINDER with message *"Systemnachricht"*.

### Additions
- **feat: `ERROR_SEVERITY_REMINDER`** — the controller exposes four notification categories, not three. Added the missing `REMINDER` constant and applied it to the user-actionable codes (0003 birthday, 0005 system status, 0010/0011/0012 update-available, 0180/0181/0182 calibration reminders). `VioletPoolAPI.parse_error_notification()` now also returns an `is_reminder` flag alongside `is_alarm`/`is_warning`/`is_info`.
- **feat: missing controller error codes** — added the OmniTronic multi-port valve fault codes (0045/0046/0047/0049), electrolysis flow switch (0135), H2O2 dosing warnings (0142-0145), flocculant max daily amount (0172), and duplicate-coded relay extension (0210). Source: `notifications/codelist_*.csv` (fw 1.0.9 snapshot).
- **feat: `reset_blocking()` API method + HA service** — wraps `GET /resetBlocking`. Clears `BLOCKED_BY_ESC` and similar fault states so dosing resumes after the underlying issue is fixed (e.g. canister refilled). Equivalent to the "Reset" button on the controller's web UI.
- **feat: `set_can_amount()` API method + HA service** — wraps `POST /setCanAmount` with the correct `cid` mapping per channel. Use after refilling a chemical canister so the remaining-range calculation stays accurate. `reset=True` also clears the daily-dosing counter.
- **feat: `set_system_service()` / `get_system_services()` API methods + HA services** — toggle and query controller-side system services (FTP, Samba, SSH, AirPlay/Shairport, HomeKit bridge, Alexa, cloud tunnel, support tunnel). Wraps the 16 `/enable*` / `/disable*` endpoints plus `GET /getServiceStates`.
- **feat: `DOSSTOP` support in `http_control.trigger_manual_dosing()`** — the HA-side wrapper previously hardcoded `action=DOSSTART`. New `action` parameter accepts `DOSSTART` (default) or `DOSSTOP` so a running manual dosing run can be cancelled without bypassing the wrapper.
- **feat: OmniTronic direct valve control** — new `set_omni_position(position)` API method wraps `setFunctionManually?OMNI,OMNI_DC<N>` (positions 0-5). Position 0 = Filtration / return-to-AUTO, 1-5 = other physical ports. New HA service `set_omni_position`. Source: `includes/setFunctionManually.js` `manualOmniSwitching` (fw 1.0.9).
- **feat: RS485 variable-speed pump control** — three new API methods: `get_rs485_pump_data(pump_name)` returns the pump's live data + register config; `set_rs485_live(pump_name, slave_id, mode, level)` sends live control (mode = rpm/pwr/hz, clamped to the pump's validmin/validmax on the controller); `end_rs485_live()` releases the bus. Constants `RS485_PUMP_NAMES` (BADU_ECO_DRIVE_II, BADU_ECO_FLEX, BADU_PRIME_NEO_VS) and `RS485_PUMP_MODES` exported.
- **feat: `get_live_trace()` API method + HA service `get_live_trace_snapshot`** — wraps `GET /getLiveTrace`, parses the 3-line CSV (header/units/values, German decimal commas) into a flat dict. Useful for ad-hoc troubleshooting; the controller does not document this endpoint as stable, so prefer `get_readings()` for production polling.
- **feat: analog + temperature switching-rule sensors** — added 16 new diagnostic sensors (ANALOGRULE_1..8 + TEMPRULE_1..8) exposing the 0/1 active flags from `shm/ANALOGRULE_STATE.states` and `shm/TEMPRULE_STATE.states`.
- **feat: extra diagnostic sensors** — added 11 sensors that were previously dropped: `last_error_id`, `DOS_2_CURRENT_POLARITY`, `DOS_*_REMAINING_RANGE` (5 channels), `BACKWASH_OMNI_STATE`, `BACKWASH_OMNI_MOVING`, `BACKWASH_LAST_AUTO_RUN`, `BACKWASH_LAST_MANUAL_RUN`.
- **feat: shared `DOSING_STATE_DESCRIPTIONS` map** — centralised the previously-duplicated `_DETAIL_DESCRIPTIONS` dict (was 13 entries in two places). The new dict in `const.py` covers 40+ firmware state strings including OmniTronic faults (BLOCKED_BY_OMNI, BLOCKED_BY_Z1Z2), polarity reversal, missing module, max-amount limits, etc.
- **docs: `SPECIFIC_READING_GROUPS` semantics** — the `/getReadings` query tokens `DOSAGE`, `RUNTIMES`, `PUMPPRIOSTATE`, `BACKWASH`, `SYSTEM` are not regex filters but **feature flags**: omitting them silently drops the corresponding computed fields from the response even when `ALL` is present. Behaviour now documented at the constant definition and in `get_specific_readings()`.

---

## v0.0.30

(internal release — superseded by v0.0.31 before publishing)

## v0.0.29

(internal release — see `git log v0.0.28..v0.0.29` for details)

## v0.0.28

(internal release — see `git log v0.0.27..v0.0.28` for details)

---

## v0.0.27

### Fixes
- **fix: `manual_dosing(type, 0)` stops instead of sending a zero-second `DOSSTART`** — `/triggerManualDosing` requires an explicit runtime; `duration <= 0` now routes to `DOSSTOP` as documented
- **fix: broken lint/typing configuration** ÔÇö `tool.ruff.target-version` and `tool.mypy.python_version` contained the package version (`0.0.26`) instead of a Python version, which made `ruff` (and the `tox -e lint` CI job) fail to parse `pyproject.toml`
- **fix: PVSURPLUS made spec-conform** ÔÇö manual section 26.3 only documents `ON`/`OFF` for PVSURPLUS (no `AUTO`; getReadings reports only states 0/1/2). `set_switch_state("PVSURPLUS", "AUTO")` now sends `OFF` (with a warning) instead of the undocumented `PVSURPLUS,AUTO`, other unsupported actions raise `VioletPoolAPIError`; `set_pv_surplus()` clamps `pump_speed` to the documented 1ÔÇô3 range
- **fix: 4xx responses fail fast and bypass the circuit breaker** ÔÇö deterministic client errors (401/404, except 429) are no longer retried with backoff and no longer count as circuit breaker failures, so a misconfiguration (e.g. wrong credentials) keeps reporting the actual HTTP error instead of opening the breaker
- **fix: dosing action `AUTO` no longer starts a dosing run** ÔÇö `_trigger_dosing()` mapped every action except `OFF`/`STOP` to `DOSSTART`, so `set_switch_state("DOS_6_FLOC", "AUTO")` would have *started* a chemical dosing run. Per PoolDigital (support forum, thread 2227): `setFunctionManually` does not work for `DOS_*` outputs at all ÔÇö starting **and** stopping must go through `POST /triggerManualDosing`, and stopping returns the channel to automatic mode. `AUTO` now maps to `DOSSTOP`, unknown dosing actions raise `VioletPoolAPIError` instead of defaulting to `DOSSTART`
- **fix: `_command_result()` evaluates line 1 (`OK`/`ERROR`) per manual section 26.2** ÔÇö info texts that merely contain the word "error" no longer flip `success` to `False`
- **fix: `tests/test_mock_server.py` now starts the mock server via a pytest fixture** ÔÇö `pytest tests/` passes standalone again

### Improvements
- **feat: state display texts are language-configurable** ÔÇö `VioletState.display_mode` was hardwired to German; the default stays `"de"` for backwards compatibility, but the language can now be set per instance (`VioletState(..., language="en")`), per call (`display_mode_for("en")`), or globally (`set_state_translation_language("en")`). `STATE_TRANSLATIONS`, `get_state_translation_language` and `set_state_translation_language` are exported from the package root

---

## v0.0.25

### Improvements
- **fix: restore public API constants** ÔÇö `ACTION_*`, `COVER_FUNCTIONS`, and `COVER_STATE_MAP` symbols are now part of the stable public API contract and cannot be removed without a major version bump
- **chore: properly export all public constants** from `__init__.py` so they are accessible via `import *` patterns used by the Home Assistant integration

### Installation
```bash
pip install violet-poolController-api==0.0.25
```

---

## v0.0.18

### Improvements
- **feat: complete error code reference from manual section 27.2** ÔÇö all ~80 controller error codes (0000-0209) with exact German descriptions and severity levels (ALARM/WARNING/INFO)
- **feat: add `parse_error_notification()` and `parse_multiple_errors()` helpers** for decoding controller error notifications into structured dicts suitable for Home Assistant sensor entities
- **feat: improved `_command_result()` response parsing** ÔÇö multi-line controller responses now return structured `output` and `message` fields (line 1=OK/ERROR, line 2=output, line 3+=info)
- **fix: PVSURPLUS command verified correct** ÔÇö speed parameter goes in WERT_1 (position 3) per manual section 26.3
- **chore: export `ERROR_CODES`, `ERROR_SEVERITY_*` from `__init__.py`**
- **test: add 19 new tests** covering error code parsing, multi-line response parsing, PV surplus with speed (68 total)

### Manual verification (section 26.2)
All `/setFunctionManually` commands verified against manual v1.1.9:
- `PUMP,{action},{duration},{speed}` (26.2.1)
- `EXT{1|2}_{1-8},{action},{duration},0` (26.2.2)
- `LIGHT,{action},0,0` / `DMX_SCENE{1-12},{action},0,0` / `ALLON/ALLOFF/ALLAUTO` (26.2.3)
- `DIRULE_{1-7},PUSH/LOCK/UNLOCK,0,0` (26.2.4)
- `PVSURPLUS,ON/OFF,{speed},0` (26.3)

### Installation
```bash
pip install violet-poolController-api==0.0.18
```

---

## v0.0.17

### Improvements
- **feat: add `get_hardware_profile()`** for detecting connected hardware modules (base, dosing, ext1, ext2)
- **feat: filter orphan EXT* keys** from getReadings when module not physically connected
- **feat: add i18n language selector** with flag icons (EN/DE) to all documentation pages
- **feat: add German translations** for all documentation in `docs/de/`
- **feat: add Wiki sidebar** (`_Sidebar.md`) with language selection
- **docs: fix pyproject.toml `target-version`** (was package version instead of Python version)
- **chore: extend CI to Python 3.13** (now tests 3.12, 3.13, 3.14)
- **chore: add mypy config** for type checking
- **chore: add `__init__.py` public API exports** (`from violet_poolcontroller_api import VioletPoolAPI`)
- **chore: sync `setup.py` version and deps** with `pyproject.toml`
- **chore: make `circuit_breaker.reset()` async** for thread safety
- **chore: expand `.gitignore`** (pytest, ruff, mypy caches)
- **chore: add pyproject classifiers** for Python 3.12/3.13/3.14, AsyncIO framework, keywords
- **test: add 29 new tests** covering all previously untested public methods (49 total)

### Installation
```bash
pip install violet-poolController-api==0.0.17
```

---

## v0.0.16

### Improvements
- Update deps, fix read/write reliability

### Installation
```bash
pip install violet-poolController-api==0.0.16
```

---

## v0.0.15

### Improvements
- Version bump to 0.0.15

### Installation
```bash
pip install violet-poolController-api==0.0.15
```

---

## v0.0.14

### Bugfixes
- Fix EXT module alive detection when alive_count is zero, bump version

### Installation
```bash
pip install violet-poolController-api==0.0.14
```

---

## v0.0.13

### Bugfixes
- Update to version 0.0.13.

### Installation
```bash
pip install violet-poolController-api==0.0.13
```

---

## v0.0.12

### Bugfixes
- **fix: hardware profile detection no longer reports phantom EXT2 modules.** The controller always returns relay keys (`EXT1_*`, `EXT2_*`) with a default value of `0`, even when the physical module is absent. The old detection checked whether the key existed and was not `"N/A"`, which caused false positives. The new implementation uses the controller's alive counters (`SYSTEM_ext1module_alive_count`, `SYSTEM_ext2module_alive_count`) and falls back to checking for non-zero `_LAST_ON` timestamps on older firmware versions.

### Installation
```bash
pip install violet-poolController-api==0.0.12
```

---

## v0.0.11

### Bugfixes
- fix: clean up import order (PEP 8), deduplicate hardware detection into `_build_hardware_profile()`, export `VioletPoolAPI` and `VioletPoolAPIError` from `__init__.py`
- fix: rate limiter now records blocked requests in history so `get_stats()` correctly reports `recent_blocked_1min` (was always 0)
- fix: make `CircuitBreaker.reset()` async and acquire the internal lock before mutating state
- fix: introduce `DMX_SCENE_COUNT = 12` constant in `const_api.py` and replace hardcoded `range(1, 13)` in `set_all_dmx_scenes()`
- fix: cap duration in `set_output_test_mode()` to 86 400 s (24 h) to prevent controller firmware overflow on unconstrained input
- fix: restore `setup.py` which is required by the release workflow for version bumping

### Installation
```bash
pip install violet-poolController-api==0.0.11
```

---

## v0.0.10

### Features
- feat: add hardware profile detection via `get_hardware_profile`
  Automatically detect the base module, dosing module, and relay extensions based on `get_readings()`.

### Bugfixes
- fix(github): set git config globally for wiki sync workflow

### Installation
```bash
pip install violet-poolController-api==0.0.10
```

---

## v0.0.9

### Commits since v0.0.8

- 4049429 Update release.yml
- 446910d chore: bump version to 0.0.9
- 9a48bbf pypi-environment
- 73746c2 fix(github): Add environment claim to trusted PyPI publishing workflow
- d11b9c8 chore: bump version to 0.0.9
- 628364e fix-auto-detect-dosing-standalone
- d53a9e0 Merge branch 'main' into fix-auto-detect-dosing-standalone-6258129374762791943
- 761ae52 fix: resolve PyPI publishing OIDC permission issue
- 2a18c66 chore: bump version to 0.0.9
- ff0ea5c fix-auto-detect-dosing-standalone
- 9876c99 feat: create v0.0.9 release and publish to PyPI
- be299ad fix-auto-detect-dosing-standalone
- ac90bfb feat: auto-detect standalone dosing setup from getReadings response
- 7f8e42f optimize-api
- 5ae51ea refactor: optimize api components

### Installation
```bash
pip install violet-poolController-api==0.0.9
```

---

## v0.0.8

### Commits since v0.0.6

- ad432c1 fix-pages-and-release-
- 8c7c358 fix: add missing os import in release workflow
- 46c43ff fix-pages-and-release
- b457b5b fix: Update GitHub Pages action versions to correct stable versions
- fae65eb /jules-fix-pages-and-release
- 0a3708b chore: fix github pages node warnings and tag release v0.0.7
- 984f174 0.0.7-standalone-readings
- 5fabda6 docs: update readme, wiki and changelog for v0.0.7

- Add RELEASE_NOTES_v0.0.7.md with changelog and explanations.
- Update README.md to explain transparent Standalone payload parsing.
- Add Standalone description to docs/Fetching-Data.md.
- 6193cea feat: add standalone getReadings parser and bump version to 0.0.7

- Add support for flattening standalone `getReadings` list payload.
- Bump package version to 0.0.7 in pyproject.toml and setup.py.
- Fix Node 20 deprecation warnings in GH Actions.
- e8577ff feat: add standalone getReadings parser and bump version to 0.0.7

- Add support for flattening standalone `getReadings` list payload.
- Bump package version to 0.0.7 in pyproject.toml and setup.py.
- Fix Node 20 deprecation warnings in GH Actions.
- 38e245c Add files via upload

### Installation
```bash
pip install violet-poolController-api==0.0.8
```

---

## v0.0.7

### Features
* **Seamless Standalone Firmware Support:** The `getReadings` API responses now automatically parse and flatten the newer, list-based JSON payloads provided by the Violet Standalone controller format. This change is fully backwards-compatible, allowing downstream applications (like Home Assistant) to handle both Base Module and Standalone outputs identically without additional configuration.

### Fixes & Chores
* **GitHub Actions:** Resolved Node 20 deprecation warnings by forcing actions to run on Node 24 (`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true`).
* Bumped project version to `0.0.7` across `pyproject.toml` and `setup.py`.

### Installation
```bash
pip install violet-poolController-api==0.0.7
```

---

## v0.0.6 - Standalone Dosing

### Feature

* Added standalone dosing mode via the new `dosing_standalone` API initialization parameter.
* In standalone mode, `DOS_*` operations remain available while base-module-dependent functions (for example pump/light/backwash) are blocked.

### Reliability

* Blocked operations now return explicit, user-facing error messages instead of failing implicitly.

### Tests and Documentation

* Added standalone-focused tests for manual dosing behavior and blocked base-module actions.
* Updated `README.md` and related docs to describe standalone initialization and behavior.

Installation:
```bash
pip install violet-poolController-api==0.0.6
```

---

## v0.0.5 - Bugfix Release

### Bug Fixes

* **Circuit Breaker stale timestamp**: `last_failure_time` used a cached timestamp from before the function call instead of `time.monotonic()` at the actual failure moment. This caused the circuit breaker to transition to HALF_OPEN too early.
* **4xx errors counted as circuit breaker failures**: HTTP 4xx client errors (400, 404, etc.) incorrectly triggered `VioletPoolAPIError`, which incremented the circuit breaker failure counter. They now raise `ClientResponseError` instead, leaving the circuit breaker unaffected.
* **Dead code removed**: Unreachable fallback exception in `_request()` replaced with a clearer message.
* **Missing `DEVICE_PARAMETERS` for ECO and REFILL**: `ECO` and `REFILL` were defined in `SWITCH_FUNCTIONS` but had no corresponding `DEVICE_PARAMETERS` entry, causing `set_switch_state()` to fall back to a generic template.

### Improvements

* CI matrix now tests Python 3.12 and 3.14 via tox.
* Connect timeout calculation corrected.
* Removed unnecessary async methods.

Installation:
```bash
pip install violet-poolController-api==0.0.5
```

---

­ƒÜÇ Initial Release of the Violet Pool Controller API

This is the first official release of the asynchronous Python client for the VIOLET Pool Controller by PoolDigital.

Features included in this release:

* Fully asynchronous operations using aiohttp.
* Built-in Circuit Breaker and Rate Limiter to protect the controller.
* Strict payload input sanitization.
* Support for reading all pool sensors and states.
* Support for controlling pumps, relays, heating targets, and light scenes (DMX/LED).
* Support for triggering manual chemical dosing.

Installation:
```bash
pip install violet-poolController-api==0.0.2
```

Note: This API is actively used by the official Violet Home Assistant Integration.

---
