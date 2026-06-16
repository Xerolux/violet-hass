# Codex Project Context

Generated for local agent memory from the repository Markdown set.

Source coverage:
- Indexed all Markdown files found by `rg --files -g '*.md'`: 113 files, about 40k lines.
- Deep-read high-signal project docs: `README.md`, `ARCHITECTURE.md`, `CLAUDE.md`,
  `docs/API_PACKAGE_CONTRACT.md`, `docs/TESTING.md`, `docs/wiki/Services.md`,
  `violet_poolcontroller_api/README.md`, plus manifest/requirements/pyproject files
  for current live version facts.
- Wiki and translated docs are mirrored heavily across English/German pages; treat this
  file as a compact working map, not a replacement for exact source docs.

## Project Identity

`violet-hass` is a monorepo for the Violet Pool Controller ecosystem:

- `custom_components/violet_pool_controller/`: Home Assistant custom integration
  distributed through HACS.
- `violet_poolcontroller_api/`: standalone async Python API client published as
  `violet-poolController-api` on PyPI.
- `tests/`: Home Assistant integration tests.
- `violet_poolcontroller_api/tests/`: API package tests and mock server.
- `docs/wiki/`: source for the GitHub wiki, with English and German pages.
- `Dashboard/` and `blueprints/`: example Lovelace dashboards and HA blueprints.

The integration is unofficial/community-driven and controls physical pool hardware.
Safety, explicit user action, and conservative failure behavior matter more than
convenience.

## Current Live Facts

These values were verified against code/config files, not just docs:

- Home Assistant domain: `violet_pool_controller`.
- Integration version: `2.0.0` in `manifest.json`, `const.py`, and root `pyproject.toml`.
- API package version: `0.0.32` in `violet_poolcontroller_api/pyproject.toml`.
- HACS minimum Home Assistant version: `2026.5.0` in `hacs.json`.
- Integration manifest requirement: `violet-poolController-api>=0.0.32`.
- Runtime requirements include `homeassistant>=2026.5.0`, `aiohttp>=3.11.0,<3.14`,
  `voluptuous>=0.15.2`, and the API package.
- Root package tooling currently targets Python `>=3.12` after local cleanup, while
  several user/developer docs still mention HA/Python 3.14.2. Verify before changing
  public docs.

## Architecture Summary

The integration uses Home Assistant's coordinator pattern:

- `VioletPoolDataUpdateCoordinator` is the single source of truth for polled data.
- `VioletPoolControllerDevice` owns the API object, availability, diagnostics,
  poll history, hardware detection cache, and recovery behavior.
- Entities extend `CoordinatorEntity` through `VioletPoolControllerEntity` helpers.
- Polling reads `getReadings?ALL` and optional config/runtime enrichment.
- Writes use optimistic local state/setpoint caches, followed by delayed refresh.

Core HA platforms loaded:

- `sensor`
- `binary_sensor`
- `switch`
- `select`
- `climate`
- `cover`
- `light`
- `number`
- `update`
- `button`

Important implementation directories:

- `config_flow_utils/`: validators, config constants, grouped sensor helpers.
- `sensor_modules/`: base/generic/monitoring/specialized sensors.
- `service_*.py`: service manager, schemas, control handlers, diagnostic handlers,
  refill/overflow, rule management, dosing config.
- `const.py`: integration constants and re-exports from the API package.
- `const_features.py`: feature flags, switch definitions, setpoint definitions.
- `const_sensors.py`: sensor definitions and feature mapping.

## API Package Contract

The API package is both local source and external PyPI dependency. Keep this boundary
stable.

The integration relies on:

- `violet_poolcontroller_api.api.VioletPoolAPI`
- `violet_poolcontroller_api.api.VioletPoolAPIError`
- `VioletAuthError`, `VioletUnsafeOperationError`, and related API exceptions where
  available.
- `violet_poolcontroller_api.utils_sanitizer.InputSanitizer`
- `violet_poolcontroller_api.const_api` and `const_devices` remaining importable.
- `const_devices.VioletState` and device state mappings.

Compatibility lesson from docs:

- An older API package update removed/reorganized control constants and caused the
  whole HA integration to fail import. Future API changes must keep public symbols
  backward-compatible or coordinate an integration update.

Key API behaviors:

- Fully async via `aiohttp`.
- Token-bucket rate limiter.
- Circuit breaker.
- Retry/backoff around network/server errors.
- Basic Auth support.
- SSL verification enabled by default, optional disable for trusted self-signed setups.
- Dosing standalone mode supports dosing-only controllers without base-module outputs.
- Mock server supports stateful hardware-free development.

## Security Model

Security docs emphasize a passive-first model:

- Never assume device state.
- Never restore outputs on startup.
- Never auto-recover by issuing control commands.
- Only act on explicit user commands or explicit service calls.
- Validate and sanitize all user-controlled values.
- Keep rate limiting enabled to protect the controller.
- Redact secrets in diagnostics.
- Prefer service calls with mandatory durations for dangerous operations.

Critical physical-risk areas:

- Dosing can overdose chemicals.
- Refill can flood/overflow.
- Backwash can damage equipment if uncontrolled.
- Cover movement has safety implications.

Recent local fixes relevant to safety:

- Unsafe dosing/backwash/refill switch defaults are controlled by `allow_unsafe_switches`
  and enforced again after platform setup.
- Backwash/refill auto-stop tasks are scheduled through Home Assistant task tracking
  instead of raw long-lived `asyncio.create_task`.

## State Model

Most controller outputs use states `0..6`:

- `0`: auto standby, off
- `1`: auto active/scheduled, on
- `2`: auto priority off/rule blocked, off
- `3`: auto priority on/emergency rule, on
- `4`: manual on/forced, on
- `5`: off by emergency rule, off
- `6`: manual off, off

State strings may include detail suffixes, for example `3|PUMP_ANTI_FREEZE`.
The integration must preserve detail context where useful.

Exception:

- `PVSURPLUS` has its own scheme: `0` off, `1` on via digital input, `2` on via HTTP.

## Services And Automation Surface

The docs describe 30+ HA services in phases:

Core/control/diagnostics:

- `control_pump`
- `smart_dosing`
- `manage_pv_surplus`
- `control_dmx_scenes`
- `set_light_color_pulse`
- `manage_digital_rules`
- `test_output`
- `export_diagnostic_logs`
- `get_connection_status`
- `get_error_summary`
- `test_connection`
- `clear_error_history`

HTTP control:

- `control_pump_http`
- `control_heater_http`
- `control_solar_http`
- `control_cover_http`
- `control_backwash_http`
- `manual_dosing_http`
- `control_refill_http`

Dosing config:

- `configure_dosing`
- `set_dosing_target`
- `set_dosing_daytime`
- `set_dosing_max_daily`
- `enable_dosing`

Rule/system/refill/maintenance services include temp/analog/switching/timer rules,
extension relay control, calibration, refill/overflow config, reset blocking,
can amount, system service status/control, Omni position, live trace snapshots,
update/backwash/calibration status.

When adding services:

1. Update `services.yaml`.
2. Add Voluptuous schema in `service_schemas.py`.
3. Implement handler in the appropriate service module.
4. Register in `services.py`.
5. Add translations.
6. Add tests.

## Configuration And Discovery

Setup paths:

- HACS custom repository installation is primary.
- Manual install copies `custom_components/violet_pool_controller`.
- Config flow asks for disclaimer, host/port/SSL/auth, pool data, features/sensors,
  and polling interval/options depending on flow.
- ZeroConf/mDNS discovery uses `_http._tcp.local.` with `violet*` and
  `_violet-controller._tcp.local.` service types.
- Multi-controller support uses unique identifiers based on host/device ID and
  separates devices/areas by controller name.

Connection/security options:

- `use_ssl`
- `verify_ssl`
- timeout
- retry attempts
- polling interval
- username/password
- dosing standalone
- allow unsafe switches

## Testing And Tooling

Documented setup:

```bash
./scripts/setup-test-env.sh
./scripts/run-tests.sh
```

Common direct commands:

```bash
pytest tests/ -v
pytest violet_poolcontroller_api/tests/ -v
pytest -v
python -m ruff check custom_components/violet_pool_controller/
python -m ruff check violet_poolcontroller_api/violet_poolcontroller_api/
python -m mypy custom_components/violet_pool_controller/
python -m mypy violet_poolcontroller_api/violet_poolcontroller_api/
```

Important local caveats:

- This Codex environment initially lacked `pytest`, `ruff`, and `aiohttp`; do not
  assume tests can run until the venv/dev deps are installed.
- `tests/conftest.py` includes HA compatibility patches, including thread filtering
  for `_run_safe_shutdown_loop` and timezone/deprecation handling.
- `pytest.ini` uses `asyncio_mode = auto` and function-scoped loops.
- If imports fail in ad-hoc local scripts, set `PYTHONPATH` or install the API package
  editable with `pip install -e ./violet_poolcontroller_api[test]`.

Useful verification after edits:

```bash
python -m compileall -q custom_components/violet_pool_controller violet_poolcontroller_api/violet_poolcontroller_api
git diff --check
```

## Documentation Map

Root docs:

- `README.md` / `README.de.md`: project overview, HACS quick start, features,
  repo structure, disclaimer.
- `ARCHITECTURE.md`: monorepo structure, coordinator/entity/service/API patterns.
- `CLAUDE.md`: developer instructions and high-signal implementation map.
- `SECURITY.md`: security architecture and passive-first rules.
- `CONTRIBUTING.md`: contribution flow, style, tests, PR checklist.
- `CHANGELOG.md`: integration release notes.
- `BACKLOG_PROGRESS.md`: historical PR/backlog progress, mostly complete.
- `CONTROL_IMPLEMENTATION_ROADMAP.md`: roadmap of control endpoints/services.
- `WIKI.md`: large combined wiki snapshot.

Docs directory:

- Installation and migration guides.
- HA quality scale progress.
- Auto-discovery guide.
- API sensor reference.
- API package contract.
- Testing guides.
- Multi-controller guide.
- Violet card quick start and roadmap.
- Standalone manual.
- Release notes/changelogs.

Wiki directory:

- English/German pairs for Installation, Configuration, Sensors, Switches,
  Climate, Services, Automations, Troubleshooting, Diagnostics, Error Codes,
  Security, Multi-Controller, Testing, API Reference, API Package, FAQ, etc.
- `docs/wiki/_Sidebar*.md` controls wiki navigation.
- `wiki-sync.yml` syncs this tree to GitHub wiki.

Dashboards and blueprints:

- `Dashboard/`: Lovelace YAML examples and guide.
- `blueprints/`: helper setup and automation blueprints for temperature, pH,
  cover, and backwash control.

API package docs:

- `violet_poolcontroller_api/README.md`: standalone API usage and mock server.
- `violet_poolcontroller_api/CHANGELOG.md`: API release history.
- `violet_poolcontroller_api/RELEASE_NOTES_v*.md`: version-specific notes.
- `violet_poolcontroller_api/AGENTS.md`: agent instructions for API package work.

## CI/CD And Release

Workflows described in docs:

- Validation: ruff, mypy, pytest, hassfest, HACS.
- API package CI: Python 3.12-3.14 matrix.
- Integration release: `v*` tags.
- API release: `api-v*` tags, PyPI publish.
- API dependency sync workflow updates manifest requirement after API version changes.
- Security workflow: CodeQL + secret scanning.
- Wiki sync workflow publishes `docs/wiki/`.

Version consistency matters across:

- `custom_components/violet_pool_controller/manifest.json`
- `custom_components/violet_pool_controller/const.py`
- root `pyproject.toml`
- `.version` if present
- release notes/changelog
- API version in `violet_poolcontroller_api/pyproject.toml`

## Known Drift And Things To Recheck

- Several docs still mention Python 3.14.2 as minimum runtime/tooling. Root
  `pyproject.toml` has been relaxed locally to `>=3.12`; Home Assistant runtime
  docs may still correctly require Python 3.14 for HA 2026.5. Reconcile before
  publishing.
- Some docs mention old test counts such as `53+`; actual test inventory is larger.
- `docs/API_PACKAGE_CONTRACT.md` references old exact pinning to `0.0.24`; live
  manifest currently uses `violet-poolController-api>=0.0.32`.
- Wiki pages may mention beta versions while manifest is `2.0.0`.
- README links to `violet_poolcontroller_api/docs/API_REFERENCE.md`, but the local
  `rg --files` markdown index did not show that exact path. Verify before release.

## Recent Local Work In This Thread

Files modified before this memory file:

- `custom_components/violet_pool_controller/__init__.py`
- `custom_components/violet_pool_controller/device.py`
- `custom_components/violet_pool_controller/service_control.py`
- `custom_components/violet_pool_controller/switch.py`
- `pyproject.toml`
- `tests/test_security_fixes.py`
- `violet_poolcontroller_api/violet_poolcontroller_api/api.py`

Intent of those changes:

- Fix unsafe switch enforcement on first setup.
- Track long-running safety auto-stop tasks through Home Assistant.
- Add debug logging for optional runtime enrichment failures.
- Support IPv6 host parsing while rejecting userinfo, invalid ports, and paths.
- Add regression coverage for host validation.
- Harmonize local root tooling to Python 3.12.

Verification performed:

- `python -m compileall -q custom_components/violet_pool_controller violet_poolcontroller_api/violet_poolcontroller_api tests/test_security_fixes.py`
- targeted URL parser snippet with local dummy `aiohttp` when deps were missing
- `git diff --check`

Not performed in this shell:

- Full `pytest` suite, because `pytest` was not installed at the time.
- Ruff/mypy, because local tool dependencies were not installed at the time.

## Agent Working Notes

When resuming work:

- Prefer exact source files over this memory for final truth.
- Read `CLAUDE.md`, `ARCHITECTURE.md`, and this file first for orientation.
- For API changes, also read `docs/API_PACKAGE_CONTRACT.md`.
- For safety-sensitive changes, read `SECURITY.md` and tests around security principles.
- For UI/entity behavior, inspect `const_features.py`, `const_sensors.py`, platform files,
  and translations.
- For service changes, inspect `services.yaml`, `service_schemas.py`, `services.py`,
  and relevant handler modules.
- Be careful with user/uncommitted changes. Do not revert unrelated work.
