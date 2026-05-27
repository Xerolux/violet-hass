# Changelog

All notable changes to this project will be documented in this file.

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

🚀 Initial Release of the Violet Pool Controller API

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
