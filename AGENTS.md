# AGENTS.md - Instructions for AI Agents & Chatbots

This file provides context and guidelines for AI assistants working on this project.

## Project Overview

**violet-poolController-api** is an async Python client library for the Violet Pool Controller HTTP API. It communicates with the controller hardware via HTTP (JSON and text/plain responses).

- **Language:** Python 3.12+
- **Framework:** `aiohttp` (async HTTP client)
- **Package:** `violet-poolcontroller-api` on PyPI
- **License:** AGPL-3.0-or-later

## Repository Structure

```
violet_poolcontroller_api/     # Main package
  api.py                       # VioletPoolAPI client class - all public methods
  const_api.py                 # API endpoints, actions, error codes, constants
  const_devices.py             # Device parameters, state mappings, VioletState class
  circuit_breaker.py           # Circuit breaker pattern for resilience
  utils_rate_limiter.py        # Token bucket rate limiter
  utils_sanitizer.py           # Input sanitization (XSS, path traversal, etc.)
  __init__.py                  # Public exports

tests/
  test_api.py                  # Unit tests (uses aioresponses for HTTP mocking)
  mock_server.py               # Full mock server simulating the controller
  test_api_smoke.py            # End-to-end smoke test against mock server
  test_mock_server.py          # Integration test (auth, full workflow)
```

## Commands

```bash
# Lint
python -m ruff check .

# Run unit tests
pytest tests/test_api.py

# Run mock server (for manual testing)
python tests/mock_server.py --user admin --password secret --port 8480

# Run full smoke test (starts mock server automatically)
python tests/test_api_smoke.py --user admin --password secret
```

## Architecture Notes

- All API methods are async and use `aiohttp.ClientSession`
- The controller uses Basic Auth (optional, configured by user)
- Controller responses are either JSON (`application/json`) or plain text (`text/plain`)
- Switch commands return multi-line text: `"OK\nPUMP\nON"` - parsed by `_command_result()`
- Dosing pumps (`DOS_*`) use `/triggerManualDosing` (POST), all other functions use `/setFunctionManually` (GET)
- Readings come in two formats: dict (base module) or list (dosing-standalone) - automatically normalized
- Extension relay keys (`EXT1_*`, `EXT2_*`) are filtered based on alive counters

## Mock Server

The mock server (`tests/mock_server.py`) simulates all controller endpoints for testing without real hardware.

Features:
- All 15 API endpoints with realistic responses
- Stateful: switch/dosing state changes are reflected in getReadings
- Basic Auth support (`--user` / `--password`)
- Simulated network latency (`--delay`)
- Dosing-standalone mode (`--standalone`)
- Sensor drift (pH, ORP, chlorine values change slowly over time)
- Error simulation via `/mock/error?code=500&count=3`
- State inspection via `/mock/state`
- Reset via `/mock/reset`

## Coding Conventions

- Line length: 100 (ruff config)
- Target: Python 3.12+
- Ruff rules: E, F, W, I, UP
- No comments unless explicitly requested
- All public methods have docstrings with Args/Returns/Raises
- German error messages from the controller are preserved as-is

## When Making Changes

1. Run `python -m ruff check .` after edits
2. Run `pytest tests/test_api.py` to verify unit tests pass
3. If adding new API methods: add corresponding mock server handler AND smoke test
4. If modifying endpoints: update both `const_api.py` constants and mock server
5. Never commit secrets, passwords, or real IP addresses
