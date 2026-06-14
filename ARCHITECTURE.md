# Architecture: violet-hass Monorepo

## Overview

This repository contains two tightly coupled components for the Violet Pool Controller ecosystem:

1. **`violet_poolcontroller_api/`** - Standalone Python package (PyPI: `violet-poolController-api`)
   - Async HTTP client communicating with Violet Pool Controller hardware
   - Rate limiting, circuit breaker, input sanitization
   - Independent of Home Assistant - usable standalone

2. **`custom_components/violet_pool_controller/`** - Home Assistant integration (HACS)
   - Exposes pool sensors, switches, climate, covers, etc. to HA
   - Depends on `violet_poolcontroller_api` for hardware communication
   - Config flow with ZeroConf auto-discovery

## Dependency Graph

```
custom_components/violet_pool_controller/
    ├── violet_poolcontroller_api  (PyPI package, dev: local editable install)
    └── homeassistant              (runtime)

violet_poolcontroller_api/
    ├── aiohttp>=3.11.0
    └── (no HA dependencies)
```

## Where to Change What

| Task | Location |
|------|----------|
| Add/modify API endpoints | `violet_poolcontroller_api/violet_poolcontroller_api/api.py` |
| Add device constants | `violet_poolcontroller_api/violet_poolcontroller_api/const_devices.py` |
| Add API constants | `violet_poolcontroller_api/violet_poolcontroller_api/const_api.py` |
| Fix HA integration bug | `custom_components/violet_pool_controller/` |
| Add HA entity (sensor, switch, etc.) | `custom_components/violet_pool_controller/sensor.py` (or switch.py, etc.) |
| Change API dependencies | `violet_poolcontroller_api/pyproject.toml` |
| Change HA integration dependencies | `custom_components/violet_pool_controller/manifest.json` |
| Add API tests | `violet_poolcontroller_api/tests/` |
| Add HA integration tests | `tests/` |

## Testing

Requires Python 3.14.2+.

```bash
# Create and activate a Python 3.14 venv
python3.14 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dev dependencies (API package editable)
pip install -r requirements-dev.txt

# API tests only
pytest violet_poolcontroller_api/tests/ -v

# HA integration tests only (requires Linux/WSL/macOS; HA uses Unix-only modules)
pytest tests/ -v

# Everything
pytest -v
```

## Versioning & Publishing

### API (PyPI)
- Version defined in `violet_poolcontroller_api/pyproject.toml`
- Publish via tag: `git tag api-v1.0.0 && git push origin api-v1.0.0`
- Workflow: `.github/workflows/publish-api.yml`

### HA Integration (HACS)
- Version defined in `custom_components/violet_pool_controller/manifest.json`
- Published via release tags: `git tag v1.2.5 && git push origin v1.2.5`
- Workflow: `.github/workflows/release.yml`

### Version Sync
- When API version changes in `pyproject.toml`, the `sync-api-version` workflow
  automatically updates `manifest.json` requirements

## CI Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `validate.yml` | Push/PR to main | HA integration tests, hassfest, HACS validation |
| `test-api.yml` | API file changes | API unit tests, lint, type check |
| `publish-api.yml` | `api-v*` tags | Build & publish API to PyPI |
| `release.yml` | `v*` tags | HA integration release with ZIP artifact |
| `dev-release.yml` | Push to main | Dev prerelease build |
| `sync-api-version` | API pyproject.toml change | Keep manifest.json in sync |

## Key Design Decisions

- **Domain kept as `violet_pool_controller`**: No breaking change for existing users
- **API still published to PyPI**: HACS users get it automatically via HA's dependency resolver
- **Editable install for dev**: `pip install -e ./violet_poolcontroller_api` links local code
- **Separate tag prefixes**: `v*` for HA integration, `api-v*` for API package
