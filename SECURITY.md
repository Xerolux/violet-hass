# 🔒 Security Architecture – Violet Pool Controller

**Version**: 1.0  
**Last Updated**: 2026-06-15  
**Status**: Production Ready  

---

## Executive Summary

The **Violet Pool Controller** integration follows a **strict read-only, passive-first security model**. The add-on:

- ✅ **Reads and displays** data from the pool controller
- ✅ **Only acts on explicit user commands** (no autonomous state changes)
- ✅ **Never assumes device states** (no restore-from-backup, no recovery of previous state)
- ✅ **Never auto-applies settings** (all configuration requires conscious user action)

This architecture ensures **maximum safety** for critical infrastructure like pool systems, where unintended state changes could cause harm (equipment damage, water overflow, chemical dosing errors).

---

## Table of Contents

1. [Core Security Principles](#core-security-principles)
2. [Architecture Overview](#architecture-overview)
3. [Security by Component](#security-by-component)
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
│  Command Queue  │  (validates & queues)
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

**Never** does the add-on:
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

**Code Evidence**:
```python
# From switch.py:421-441
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

- Setpoint ranges validated (e.g., 5°C – 40°C)
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
| **Rate Limiting** | Token bucket algorithm (configurable 0.5–10 req/sec) |
| **Timeout Protection** | 10s total timeout, 8s per socket |
| **Retry Logic** | Exponential backoff (1–8 seconds), max 3 attempts |
| **Circuit Breaker** | Auto-pause API calls after 5 consecutive failures |
| **Data Validation** | All parsed data type-checked before use |

**Code Evidence** (device.py:322-400):
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

### 5. Input Sanitization (`violet_poolcontroller_api/utils_sanitizer.py`)

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
| **SSL/TLS** | Enabled | No |
| **Certificate Verification** | ✅ Enabled | Yes (⚠️ warn if disabled) |
| **Cipher Strength** | Modern (TLS 1.2+) | OS-managed |

**Configuration**:
```python
# From manifest.json
"verify_ssl": true  # Default: certificate verification ON

# Config flow allows disabling only for self-signed in trusted networks
CONF_VERIFY_SSL = "verify_ssl"
DEFAULT_VERIFY_SSL = True
```

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

**Token Bucket Algorithm**:
- Configurable rate: 0.5 – 10 requests/sec (default: 2 req/sec)
- Prevents API flooding
- Circuit breaker kicks in after 5 consecutive failures

```python
# Configuration
CONF_RATE_LIMIT = 2.0  # requests per second
DEFAULT_RATE_LIMIT = 2.0

# Enforced at: VioletPoolAPI._rate_limiter.acquire()
```

### Timeout & Retry

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Connection Timeout** | 8s | Fail fast on unreachable host |
| **Socket Timeout** | 8s | Fail fast on slow responses |
| **Total Timeout** | 10s | Max time per request |
| **Retry Attempts** | 3 (configurable) | Resilience to transient errors |
| **Backoff** | Exponential: 1s, 2s, 4s | Avoid thundering herd |

### SSL/TLS Configuration

```python
# From device.py:277-287
api = VioletPoolAPI(
    host=api_url,
    use_ssl=True,                    # Always use HTTPS
    verify_ssl=True,                 # Verify certificate by default
    timeout=10,                      # 10s total
    max_retries=3,
)

# User can disable verify_ssl ONLY for self-signed certs
# (generates warning in logs)
```

---

## Error Handling & Recovery

### Connection Recovery (NOT State Recovery)

The add-on **recovers the connection**, not the device state:

```python
# From device.py:528-535
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
# From device.py:306-320
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

**Example Test** (Preventing state assumption):
```python
# tests/test_security_fixes.py (hypothetical)
async def test_no_restore_on_startup():
    """Verify pump is NOT restored to previous state on startup."""
    config = create_config_entry(pump_was_on=True)
    
    coordinator = VioletPoolDataUpdateCoordinator(...)
    await coordinator.async_config_entry_first_refresh()
    
    pump_state = coordinator.data.get("PUMP")
    # Must reflect actual controller state, not config
    assert pump_state in [0, 1, 2, 3, 4, 5, 6]  # Real states only
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

1. **Do NOT create a public issue**
2. **Email**: security@violet-pool.dev (or maintainer)
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

## Security Audit Trail

### Version 1.0 (2026-06-15)

**Reviewed Components**:
- ✅ Switch platform (turn_on/turn_off only on user action)
- ✅ Climate platform (setpoint changes only on user action)
- ✅ Number platform (value changes only on user action)
- ✅ Input sanitization (XSS, injection, traversal protection)
- ✅ Rate limiting (token bucket, circuit breaker)
- ✅ Connection recovery (logs only, no state recovery)
- ✅ Error handling (throttled logging, no silent failures)

**Security Findings**: 0 critical, 0 high

**Recommendations**:
1. Continue regular security audits (quarterly)
2. Monitor for new Home Assistant security advisories
3. Keep `violet-poolController-api` dependency updated
4. Run regular penetration testing

### Signed Off By

- **Security Reviewer**: Xerolux (Maintainer)
- **Review Date**: 2026-06-15
- **Next Audit**: 2026-09-15

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

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-15 | Initial security architecture document |

**Last Updated**: 2026-06-15  
**Next Review**: 2026-09-15
