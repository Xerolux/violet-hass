# 🔒 Security Architecture – Violet Pool Controller

This document describes how the integration is built to be safe around pool
equipment, and what a contributor must not break. It carries no version or
review date of its own: it describes the code in this repository, and the way
to keep it honest is to change it in the same pull request as the code, not to
stamp it.

---

## Executive Summary

The **Violet Pool Controller** integration follows a **strict read-only, passive-first security model**. The integration:

- ✅ **Reads and displays** data from the pool controller
- ✅ **Only acts on explicit user commands** (no autonomous state changes)
- ✅ **Never assumes device states** (no restore-from-backup, no recovery of previous state)
- ✅ **Never auto-applies settings** (all configuration requires conscious user action)

This architecture ensures **maximum safety** for critical infrastructure like pool systems, where unintended state changes could cause harm (equipment damage, water overflow, chemical dosing errors).

---

## Table of Contents

1. [Core Security Principles](#core-security-principles)
2. [Architecture Overview](#architecture-overview)
3. [Security by Component](#security-by-component) - including
   [unsafe outputs](#7-unsafe-outputs-constpy-switchpy),
   [SafetyGuard](#8-safetyguard-safety_guardpy) and
   [AuthReportingAPI](#9-authreportingapi-auth_guardpy)
4. [Control Flow & User Actions](#control-flow--user-actions)
5. [Data Handling & Sanitization](#data-handling--sanitization)
6. [Connection Security](#connection-security)
7. [Error Handling & Recovery](#error-handling--recovery)
8. [Testing & Validation](#testing--validation)
9. [Security Checklist for Developers](#security-checklist-for-developers)
10. [Incident Response](#incident-response)

---

## Core Security Principles

### 1️⃣ **Passive-First Model**

The integration operates in **read-only mode by default**. All state changes are **reactive, not proactive**.

```
┌─────────────────┐
│  User Action    │  (explicit switch/button/service call)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validation     │  (schema + InputSanitizer; SafetyGuard for
│  + SafetyGuard  │   dosing, backwash and refill)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Call       │  (sends to controller)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Get Readings   │  (refresh state from controller)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Update UI      │  (display actual state)
└─────────────────┘
```

**Never** does the integration:
- Restore previous device states on startup
- Assume a device state based on configuration
- Auto-execute recovery logic without user confirmation
- Bypass user input validation

### 2️⃣ **No State Assumptions**

The integration **never assumes** what state a device should be in:

```python
# ❌ WRONG (NEVER DO THIS):
if device_was_on_before_reboot:
    await turn_on_pump()  # DANGEROUS!

# ✅ CORRECT (WHAT WE DO):
pump_state = await get_readings()  # Read actual state
display_to_user(pump_state)        # Show what we found
# User decides if action needed
```

### 3️⃣ **Explicit User Consent**

Every state change requires **explicit user action**:

| Action | Requires | Example |
|--------|----------|---------|
| Turn on pump | UI toggle or service call | `switch.turn_on(pump)` |
| Set temperature | UI slider or service call | `climate.set_temperature(25)` |
| Start dosing | Service call with params | `service.smart_dosing(channel=pH_MINUS, duration=30)` |
| Reset errors | Button press | `button.press(reset_errors)` |

---

## Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Home Assistant Core                        │
│  (Manages entity state, UI, automations, service dispatch)   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │ Switch │  │Climate │  │  Number  │  (Entity Platforms)
    │ Entity │  │Entity  │  │  Entity  │  (READ + CONTROL)
    └────┬───┘  └───┬────┘  └────┬─────┘
         │          │            │
         └──────────┼────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │ Data Update          │
        │ Coordinator          │ (Synchronizes data polling)
        │ (READ-ONLY)          │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Device Manager       │
        │ (Connection, Auth)   │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ VioletPoolAPI        │
        │ (Rate Limit, Retry,  │
        │  Circuit Breaker)    │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Input Sanitizer      │
        │ (XSS, Injection,     │
        │  Path Traversal)     │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Network Layer        │
        │ (aiohttp, SSL/TLS)   │
        └──────────────────────┘
```

### Trust Boundaries

```
🟢 TRUSTED                    🔴 UNTRUSTED
├─ Home Assistant            ├─ Pool Controller Network
├─ Config Entry Data         ├─ API Responses
├─ User Input (validated)    ├─ User Input (unvalidated)
└─ Internal State            └─ Third-party Services
```

---

## Security by Component

### 1. Switch Platform (`switch.py`)

**Threat Model**: Unauthorized device state changes

**Mitigations**:

| Control | Mechanism | Status |
|---------|-----------|--------|
| **Input Validation** | All user inputs validated (speed, duration, RPM) | ✅ Active |
| **State Change Logging** | Logs every state change with source | ✅ Active |
| **No Recovery Logic** | Device state NOT restored after reboot | ✅ Active |
| **Optimistic Cache** | Temporary UI-only cache, cleared after API refresh | ✅ Active |
| **API Confirmation** | All changes confirmed with actual read | ✅ Active |

**Code Evidence** (`switch.py`, `VioletSwitch.async_turn_on` /
`async_turn_off`):
```python
async def async_turn_on(self, **kwargs: Any) -> None:
    """Turn the switch on. Only executes on explicit user action."""
    await self._set_switch_state(ACTION_ON, **kwargs)

async def async_turn_off(self, **kwargs: Any) -> None:
    """Turn the switch off. Only executes on explicit user action."""
    await self._set_switch_state(ACTION_OFF, **kwargs)

# No auto-recovery, no state assumption, no background tasks
```

### 2. Climate Platform (`climate.py`)

**Threat Model**: Unintended temperature setpoints

**Mitigations**:

- Setpoint ranges validated against the limits in `climate.py` (do not repeat the numbers here; they change with pool type)
- HVAC mode changes logged
- Temperature limits enforced per pool type
- No automatic mode switching

### 3. Number Platform (`number.py`)

**Threat Model**: Out-of-range value injection

**Mitigations**:

- Min/max range validation enforced
- Step size validated
- Type conversion with error handling
- Sensor-specific constraints applied

### 4. Data Update Coordinator (`device.py`)

**Threat Model**: Stale or poisoned data causing wrong decisions

**Mitigations**:

| Control | Details |
|---------|---------|
| **Rate Limiting** | Token bucket in the API package; never bypassed, including on timeout |
| **Timeout Protection** | `CONF_TIMEOUT_DURATION`, 1–60 s (default 10 s) |
| **Retry Logic** | **Reads only.** Exponential backoff capped at 30 s, `CONF_RETRY_ATTEMPTS` 1–10 (default 3) |
| **Command Retries** | **None.** A state-changing command is sent exactly once (API package ≥ 0.0.39) |
| **Circuit Breaker** | Auto-pause API calls after repeated failures |
| **Data Validation** | All parsed data type-checked before use |

Why commands are not retried: a retried `setFunctionManually` can dose twice.
Since 0.0.39 the API package retries reads only, and the rate limiter is
applied to the retry as well - a timeout used to skip it, which turned one
slow controller into a burst of requests.

**Code Evidence** (`device.py`, `VioletPoolControllerDevice.async_update`):
```python
async def _fetch_controller_data(self) -> dict[str, Any]:
    """Fetch data with strict validation, never assume state."""
    readings = await self.api.get_readings()
    data = dict(readings) if readings is not None else {}
    
    # Type validation for every field
    def is_valid(val):
        return val is not None and str(val).strip().upper() != "N/A"
    
    # Hardware detection (never assumes, only detects)
    has_dosing = is_valid(data.get("SYSTEM_dosagemodule_cpu_temperature"))
    if has_dosing:
        self._hw_detected.add("DOSING")  # Sticky detection only
```

### 5. Input Sanitization (`violet_poolcontroller_api/utils_sanitizer.py`, in the [`violet-poolController-api`](https://github.com/Xerolux/violet-poolController-api) package)

**Threat Model**: Injection attacks (XSS, path traversal, command injection)

**Mitigations**:

| Attack Type | Protection |
|---|---|
| **XSS (HTML)** | Strip HTML tags, escape special chars |
| **Path Traversal** | Reject `../`, `..\\`, etc. |
| **Command Injection** | Reject shell metacharacters |
| **JSON Injection** | Strict JSON parsing, reject malformed |

**Usage**:
```python
from violet_poolcontroller_api.utils_sanitizer import InputSanitizer

sanitizer = InputSanitizer()
safe_ip = sanitizer.sanitize_ip_address(user_input)
safe_duration = sanitizer.sanitize_numeric(value, min=0, max=3600)
```

### 6. SSL/TLS Security

**Threat Model**: Man-in-the-middle attacks, credential interception

**Mitigations**:

| Control | Default | Configurable |
|---------|---------|---|
| **SSL/TLS** | **Off** (`http://`) | Yes, per config entry |
| **Certificate Verification** | **Off** | Yes, per config entry |
| **Cipher Strength** | Modern (TLS 1.2+) when SSL is on | OS-managed |

**Configuration** (`const.py`):
```python
DEFAULT_USE_SSL = False
DEFAULT_VERIFY_SSL = False
```

⚠️ **Both default to off, and that is a deliberate trade-off, not an
oversight.** Violet controllers ship with a self-signed certificate on a local
network; defaulting to verification on would make the very first setup fail
for almost every user, and the usual reaction to that is to turn verification
off and never look again. Enable both in the config flow if your controller
presents a certificate your Home Assistant trusts - the traffic carries the
controller password, so on any network you do not fully control, enabling them
is the right call.

### 7. Unsafe outputs (`const.py`, `switch.py`)

**Threat Model**: A plain on/off switch left on - an overdose of chlorine, or
a refill or backwash that floods.

Three families of output cannot be made safe by a switch, because a switch has
no time limit:

```python
# const.py
UNSAFE_SWITCH_KEYS: frozenset[str] = frozenset(
    {
        "DOS_1_CL", "DOS_2_ELO", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC",
        "BACKWASH", "BACKWASHRINSE", "REFILL",
    }
)
```

**Mitigations**:

| Control | Mechanism |
|---|---|
| **Disabled by default** | Entities for these keys are created with `entity_registry_enabled_default = False` unless the user opts in with `CONF_ALLOW_UNSAFE_SWITCHES` |
| **Supported path is a service** | `manual_dosing_http`, `control_backwash_http`, `control_refill_http` and friends take a **mandatory duration** |
| **Guarded even when enabled** | Turning one on goes through `SafetyGuard` (below), not straight to the API |

### 8. SafetyGuard (`safety_guard.py`)

**Threat Model**: Repeated or unattended operation of exactly those outputs -
an automation that fires dosing back-to-back, or a Home Assistant restart in
the middle of a refill that leaves the valve open.

`SafetyGuard` is the gate every code path driving dosing, backwash or refill
passes through. It does three things:

| Mechanism | What it prevents |
|---|---|
| **Cooldown** (`check_lock`, `enforce`, `set_lock`) | Back-to-back operations on the same device key. A caller can pass `safety_override`, and doing so is logged as a warning. |
| **Restart-safe auto-stop timers** (`arm_auto_stop`) | A running refill or backwash surviving a restart. Deadlines are persisted through `hass.storage`, re-armed on setup, and any deadline that expired during the downtime is executed immediately. |
| **Stop-target validation** (`_validate_stop_target`) | A stop that fails silently at the far end of a refill. The method named by a stop target is resolved against the API object when the timer is *armed*, not only when it fires. |

**Everything is scoped to a config entry.** Locks and auto-stops are keyed by
`(entry_id, device_key)`, and a stop is dispatched to the coordinator of the
entry that started the operation. Keying by device key alone made a
two-controller setup unsafe: a refill started on controller B was stopped on
whichever controller happened to load first, and a dosing cooldown on A blocked
the same channel on B. Sending a command to a controller the user never
addressed is exactly what this document rules out.

Tested in `tests/test_safety_guard.py`.

### 9. AuthReportingAPI (`auth_guard.py`)

**Threat Model**: A controller that silently rejects every command.

A config entry created through zeroconf discovery before credentials were
collected carries an empty username and password. Reading the controller often
works without a login, so the coordinator stays healthy and Home Assistant's
native re-auth never fires - while every switch and service call is rejected.
The first the user hears of it is a command failing.

`AuthReportingAPI` is a transparent proxy around the API client that separates
**reads** from **commands** (`set_*` plus `manual_dosing`,
`restore_calibration`, `reset_blocking`, `init_update`, `set_system_service`):

- the first rejected **command** raises the `controller_requires_auth` repair
  issue, with a "Fix it" form that collects the credentials;
- the first command that succeeds clears it again;
- **reads are left alone**, because their auth failures already route to the
  coordinator's re-auth path.

Tested in `tests/test_auth_guard.py`.


---

## Control Flow & User Actions

### Switch Control Flow

```
User toggles Switch in Home Assistant
         │
         ▼
async_turn_on() / async_turn_off() called
         │
         ▼
_set_switch_state(action) validates:
  ├─ Switch key exists
  ├─ Action is ON/OFF/AUTO (no arbitrary values)
  └─ Speed/duration within limits (if applicable)
         │
         ▼
API call: set_switch_state(key=PUMP, action=ON)
         │
         ▼
Controller responds: {"success": true}
         │
         ▼
Optimistic UI update (instant feedback)
         │
         ▼
Delayed refresh: get_readings() → confirm actual state
         │
         ▼
UI updated with real state from controller
```

### Service Call Control Flow

```
User calls service: smart_dosing(channel=pH_MINUS, duration=30)
         │
         ▼
service_schemas.py validates:
  ├─ channel in [pH_MINUS, pH_PLUS, CL, FLOCCULANT]
  ├─ duration in [1, 3600] seconds
  └─ device_id exists
         │
         ▼
Service handler queues API call
         │
         ▼
Rate limiter checks token bucket
         │
         ▼
API call: set_switch_state(key=DOS_1_PH_MINUS, action=ON, duration=30)
         │
         ▼
Controller executes dosing
         │
         ▼
Next poll cycle reads actual state
         │
         ▼
UI reflects actual dosing status
```

### Critical: Never Assumes State

```python
# ❌ WRONG - Would violate security model:
async def setup_entry(hass, entry):
    # If pump was on before, turn it back on
    if entry.data.get("pump_was_on"):  # DANGEROUS!
        await turn_on_pump()

# ✅ CORRECT - What we actually do:
async def setup_entry(hass, entry):
    coordinator = VioletPoolDataUpdateCoordinator(hass, device)
    await coordinator.async_config_entry_first_refresh()
    # Data coordinator reads actual state from controller
    # No restoration, no assumptions
```

---

## Data Handling & Sanitization

### Input Validation Pipeline

```
Raw User Input
     │
     ▼
Type Check (int, str, bool, etc.)
     │
     ▼
Range Validation (min/max bounds)
     │
     ▼
Format Validation (IP address, MAC, etc.)
     │
     ▼
Sanitization (XSS, injection, traversal)
     │
     ▼
Semantic Validation (device exists, feature enabled)
     │
     ▼
✅ Safe to use in API call
```

### Examples

#### Speed Validation (Pump Control)
```python
def _validate_speed(self, speed: Any) -> int:
    """Validate and clamp pump speed to 0-3."""
    try:
        val = int(speed)
        return max(0, min(3, val))  # Clamp to [0,3]
    except (ValueError, TypeError):
        return 2  # Safe default
```

#### Duration Validation (Dosing)
```python
def _validate_duration(self, duration: Any) -> int:
    """Validate dosing duration (1–3600 seconds)."""
    try:
        val = int(duration)
        return max(1, min(3600, val))  # Clamp to [1,3600]
    except (ValueError, TypeError):
        return 30  # Safe default
```

#### IP Address Validation
```python
from violet_poolcontroller_api.utils_sanitizer import InputSanitizer

sanitizer = InputSanitizer()
safe_host = sanitizer.sanitize_ip_address("192.168.1.100")
# Raises error if invalid: "..." characters, "drop table", etc.
```

---

## Connection Security

### Rate Limiting

**Token Bucket Algorithm**, implemented in the
[`violet-poolController-api`](https://github.com/Xerolux/violet-poolController-api)
package and applied to every request the integration makes, retries included:

- Enforced at `VioletPoolAPI._rate_limiter.acquire()`.
- A circuit breaker pauses calls after repeated consecutive failures.
- What the integration controls is how often it *asks*:
  `CONF_POLLING_INTERVAL`, 10–3600 s, default 10 s.

The rate limit is a property of the API package, not a config-entry option -
there is no `CONF_RATE_LIMIT` in `const.py`.

### Timeout & Retry

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Total Timeout** | `CONF_TIMEOUT_DURATION`, 1–60 s, default 10 s | Max time per request |
| **Retry Attempts (reads)** | `CONF_RETRY_ATTEMPTS`, 1–10, default 3 | Resilience to transient errors |
| **Retry Attempts (commands)** | 0 - sent exactly once | A retried dosing command doses twice |
| **Backoff** | Exponential, capped at 30 s | Avoid hammering a struggling controller |

### SSL/TLS Configuration

`use_ssl` and `verify_ssl` come from the config entry and both default to
`False` (see *SSL/TLS Security* above). The API client is constructed in
`device.py`, `VioletPoolControllerDevice.__init__`:

```python
api = VioletPoolAPI(
    host=api_url,
    use_ssl=use_ssl,       # config entry, DEFAULT_USE_SSL = False
    verify_ssl=verify_ssl, # config entry, DEFAULT_VERIFY_SSL = False
    timeout=timeout,       # CONF_TIMEOUT_DURATION, default 10 s
    max_retries=retries,   # CONF_RETRY_ATTEMPTS, default 3, reads only
)
```

---

## Error Handling & Recovery

### Connection Recovery (NOT State Recovery)

The integration **recovers the connection**, not the device state:

```python
# device.py, in the coordinator's update path
if self._consecutive_failures > 0 and not self._recovery_logged:
    _LOGGER.info(
        "Controller '%s' reachable again (after %d failure%s)",
        self.device_name,
        self._consecutive_failures,
        "s" if self._consecutive_failures > 1 else "",
    )
    self._recovery_logged = True
    
    # ✅ CORRECT: Only log recovery, NOT restore state
    # User will see current state after next poll
```

### Error Logging Strategy

| Error Type | Log Level | Action |
|---|---|---|
| **Connection Timeout** | WARNING | Log once, throttle repeated |
| **API Rate Limited** | INFO | Backoff, no user action |
| **Invalid Credentials** | ERROR | Require re-auth |
| **Unexpected Response** | ERROR | Log, await next poll |
| **Hardware Not Found** | DEBUG | Normal for optional modules |

### Throttling to Prevent Log Spam

```python
# device.py, failure-log throttling
FAILURE_LOG_INTERVAL = 300  # 5 minutes

def _should_log_failure(self) -> bool:
    """Check if failure should be logged (throttling)."""
    now = time.monotonic()
    if now - self._last_failure_log > FAILURE_LOG_INTERVAL:
        self._last_failure_log = now
        return True
    return False
```

---

## Testing & Validation

### Unit Tests Covering Security

**Test Files**:
- `tests/test_sanitizer.py` – Input sanitization
- `tests/test_api.py` – API communication & rate limiting
- `tests/test_config_flow.py` – Config validation
- `tests/test_entity_state.py` – State interpretation
- `tests/test_security_fixes.py` – Regression tests
- `tests/test_security_principles.py` – **The principles in this document,
  asserted against the code.** This is the file to read (and extend) rather
  than an example invented for the documentation.
- `tests/test_safety_guard.py` – Cooldowns, restart-safe auto-stop timers and
  per-entry scoping of `SafetyGuard`
- `tests/test_auth_guard.py` – `AuthReportingAPI` raising and clearing the
  `controller_requires_auth` repair issue

Run them with:

```bash
pytest tests/test_security_principles.py tests/test_safety_guard.py tests/test_auth_guard.py -v
```

### Continuous Integration

**GitHub Workflow** (`.github/workflows/validate.yml`):
- ✅ Ruff linter (catches code smells)
- ✅ MyPy type checking (prevents type confusion)
- ✅ Pytest full suite (functional correctness)
- ✅ HACS validation (Home Assistant compatibility)

---

## Security Checklist for Developers

Use this checklist when adding new features:

### ❌ Do NOT

- [ ] Auto-restore device state on startup
- [ ] Assume device state based on configuration
- [ ] Execute recovery logic without user confirmation
- [ ] Use unvalidated user input in API calls
- [ ] Store credentials in plain text (use encrypted config entry)
- [ ] Skip SSL certificate verification without reason
- [ ] Log sensitive data (credentials, tokens)
- [ ] Make breaking changes to entity IDs (breaks user automations)

### ✅ Do

- [ ] Validate all user inputs with explicit ranges/formats
- [ ] Log state changes (source: user, API, automation)
- [ ] Implement rate limiting for frequent operations
- [ ] Use try-except around API calls
- [ ] Refresh state after every state change (confirm with API)
- [ ] Document security implications of new features
- [ ] Test with invalid/malicious inputs
- [ ] Sanitize all user-provided strings

### Code Review Questions

When reviewing a PR:

1. **Does this feature assume device state?**
   - If yes, require explicit read from controller first

2. **Can this be triggered without user input?**
   - If yes, it violates security model

3. **Is user input validated?**
   - Check for: type, range, format, injection vectors

4. **Are API errors handled gracefully?**
   - Must not break or change device state

5. **Is the change logged?**
   - All actions should be auditable

---

## Incident Response

### What to Do If a Security Issue is Found

1. **Do NOT create a public issue.**
2. **Report it privately**, either way:
   - GitHub private vulnerability reporting:
     [Report a vulnerability](https://github.com/Xerolux/violet-hass/security/advisories/new)
     (preferred - it keeps the discussion attached to the repository)
   - Email the maintainer: **git@xerolux.de**
3. **Provide**:
   - Detailed description with reproduction steps
   - Impact assessment (scope, severity)
   - Suggested fix (if you have one)
4. **Timeline**: Maintainer will respond within 48 hours

### Security Incident Types

| Incident | Response | Timeline |
|----------|----------|----------|
| **Remote Code Execution** | Immediate patch | 24h |
| **State Assumption Bug** | Hotfix | 48h |
| **Authentication Bypass** | Mandatory upgrade | 1 week |
| **Information Disclosure** | Patch + audit | 2 weeks |

---

## Glossary

| Term | Definition |
|------|-----------|
| **State Assumption** | Assuming a device state without reading from the controller (DANGEROUS) |
| **Passive-First** | Read-only by default, action-only on explicit user command |
| **Rate Limiting** | Controlling frequency of API requests (prevent flooding) |
| **Circuit Breaker** | Auto-pause API calls after repeated failures |
| **Sanitization** | Removing/escaping dangerous input patterns |
| **Optimistic Update** | Temporary UI cache before API confirmation |
| **Recovery** | Re-establishing connection (NOT restoring state) |

---

## References

- [Home Assistant Security Best Practices](https://developers.home-assistant.io/docs/security_best_practices)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)
- [CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code](https://cwe.mitre.org/data/definitions/95.html)

---## Keeping this document true

There is no review date and no sign-off table here on purpose: the previous
version carried "Version 1.0 / 2026-06-15 / Next Audit: 2026-09-15", which said
nothing about whether the code still matched, and quietly went stale.

Instead:

- Change this file in the same pull request that changes the behaviour it
  describes. A security claim without matching code is worse than no claim.
- Cite **function and class names**, never line numbers - the previous version
  pointed at `switch.py:421-441` and `device.py:528-535`, which had both moved.
- If you assert a behaviour here, assert it in
  `tests/test_security_principles.py` too.
