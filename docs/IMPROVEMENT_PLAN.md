# Improvement plan: bugs, optimisations and documentation drift

Audit date: 2026-09-08. Audited state: `violet-hass` 2.6.1 (commit `92913dc`) and
`violet-poolController-api` 0.0.38 (commit `b5b5adf`).

This document is a **work order, not a change**. Nothing in the code was
modified while it was written. It is meant to be handed to an implementer (human
or AI) who executes the work packages one by one. Every package says *what* is
wrong, *where*, *why it matters*, *how* to fix it and *how to prove* the fix.

Baseline measured before writing this plan (both repos, nothing changed):

| Check | violet-hass | violet-poolController-api |
|---|---|---|
| `ruff check` | clean | clean |
| `mypy` | clean (67 files) | clean (15 files) |
| `pytest` | 895 passed (HA 2026.9.1, Python 3.14.7) | 250 passed (Python 3.13) |
| Coverage | 56 % total; `binary_sensor.py`, `button.py`, `light.py`, `diagnostics.py`, `sensor_organization.py` at 0 %; `switch.py` 23 %, `select.py` 28 %, `sensor.py` 28 %, `service_mixins/rules.py` 9 % | not measured |

So the tooling is green. Every finding below is a logic, safety, UX, or
documentation problem that the tooling cannot see.

---

## 0. How to work with this document

1. **One work package = one branch = one pull request.** Do not bundle P0 fixes
   with clean-ups. Small PRs get reviewed; big ones rot.
2. **Order:** finish all P0 packages first, then P1, then P2/P3/P4. Inside a
   priority the packages are independent unless a "Depends on" line says otherwise.
3. **Before every PR** run the repo's own gate. For `violet-hass`:
   ```bash
   ruff check custom_components/violet_pool_controller tests
   mypy custom_components/violet_pool_controller
   pytest tests/ -q
   ```
   For the API package:
   ```bash
   ruff check . && mypy violet_poolcontroller_api && pytest -q tests
   ```
   The HA suite needs Python 3.14 and `pip install -r requirements-dev.txt`.
4. **Write the regression test first** where a package lists one. A fix
   without a test will be undone by the next refactor.
5. **Language policy:** everything written into either repository is English
   (see `CLAUDE.md` → "Language Policy"). That includes the changelog entry.
6. **Changelog:** every user-visible fix gets a bullet under the next unreleased
   version in `CHANGELOG.md`. Internal clean-ups do not.
7. **Verify before you trust.** Line numbers in this document are from the
   audited commit and drift as soon as files change. Grep for the quoted code
   instead of relying on the number. Items marked *needs verification* were
   not reproduced against real controller firmware; check them against a live
   controller or the `getReadings` spec before changing behaviour.
8. **API-package changes ship separately.** A fix in `violet-poolController-api`
   needs a release (0.0.39), and only then can `manifest.json` /
   `requirements.txt` in `violet-hass` be bumped. Do not copy API code into the
   integration as a workaround.
9. **Security model** (`SECURITY.md`): never restore or assume device state;
   only act on explicit user commands. Several packages below exist because
   code drifted away from that rule. Do not introduce new drift while fixing.

Package IDs: `A` = safety-critical, `B` = functional bugs, `C` = code quality
and performance, `D` = tests, `E` = docs, CI and packaging. `API-` prefix means
the package lives in `violet-poolController-api`.

---

## P0 — Safety-critical (fix first, one PR each)

### A1 — Refill/backwash auto-stop never executes (integration)

**Files:** `service_mixins/cover.py` (refill), `service_mixins/pump.py`
(backwash), `safety_guard.py` (`_execute_stop`, `_resolve_api`),
`http_control.py`.

**What is wrong.** `control_refill_http action=fill` sends `REFILL,ON` through
`VioletControlClient.set_function_manually` and arms a restart-safe auto-stop
with `stop_target={"method": "set_function_manually", "args": ["REFILL", "OFF"]}`
(`service_mixins/cover.py` around line 115-131; the same for `BACKWASH` in
`service_mixins/pump.py` around line 197-213). When the timer fires,
`SafetyGuard._execute_stop` resolves the method with
`getattr(api, "set_function_manually")` on a **`VioletPoolAPI`** object.
`VioletPoolAPI` has no such method (it exists only on `VioletControlClient` in
`http_control.py`), so the guard logs
`"SafetyGuard: stop method 'set_function_manually' not found on API"` and
returns. **The valve or backwash is never stopped by Home Assistant.**

On top of that the start command carries **no duration**: the payload is
`REFILL,ON` although the controller's own template is
`REFILL,{action},{duration},0` (`const_devices.py` in the API package). The
controller-side timer is therefore unused too. Net effect: a manual refill has
no working safety stop at all. This is a flooding risk.

The existing tests did not catch it because the API is a `MagicMock`, which
has every attribute.

**Why the tests are green.** `tests/test_safety_guard.py` and
`tests/test_service_control.py` pass mocks that accept any method name.

**How to fix.**
1. Make the controller stop on its own: start refill/backwash via the public
   API method that carries a duration:
   `await coordinator.device.api.set_switch_state("REFILL", ACTION_ON, duration=int(refill_seconds))`
   (same for `BACKWASH`). Check `SWITCH_FUNCTIONS`/`DEVICE_PARAMETERS` in the
   API package for the exact action verbs the controller accepts for backwash
   (`RUN`/`ABORT` are used today in `http_control.py` but are not in the API's
   documented action list — *needs verification*; whichever verb is right,
   start and stop must use the same family).
2. Keep the HA-side timer as second line of defence, but make the stop target
   a method that exists on `VioletPoolAPI`:
   `{"method": "set_switch_state", "args": ["REFILL"], "kwargs": {"action": ACTION_OFF}}`.
3. In `SafetyGuard._execute_stop`, fail loudly at **arm** time, not at stop
   time: in `arm_auto_stop` validate `hasattr(api, stop_target["method"])`
   and raise `HomeAssistantError` if it is missing.
4. Replace the mocks in `tests/test_safety_guard.py` and
   `tests/test_service_control.py` with a `MagicMock(spec=VioletPoolAPI)` so a
   non-existent method fails the test.

**Regression test.** Arm an auto-stop with `duration_seconds=0` on a
`spec=VioletPoolAPI` mock and assert `set_switch_state` was awaited with
`("REFILL", action="OFF")`. A second test asserts that arming with
`method="does_not_exist"` raises.

**Depends on:** A2 (controller resolution) if both are done; A1 can be done
first and A2 adjusts the resolution.

---

### A2 — SafetyGuard is global, not per controller (integration)

**Files:** `safety_guard.py`, `service_mixins/{cover,pump,dosing}.py`,
`service_manager.py`.

**What is wrong.** Locks and auto-stops are keyed by `device_key` only
(`_locks`, `_auto_stop_tasks`, the persisted store). `_resolve_api()` returns
the API of the **first** loaded config entry. With two controllers:

- a refill started on controller B is stopped on controller A (or, after a
  restart, the persisted stop goes to whichever entry loads first);
- a 300 s dosing cooldown on A blocks the same channel on B.

Sending a command to a controller the user never addressed violates
`SECURITY.md` ("only acts on explicit user commands").

**How to fix.**
1. Change the guard's key to `(entry_id, device_key)` everywhere (`_locks`,
   `_auto_stop_tasks`, persisted records). Store `entry_id` in the persisted
   record.
2. `arm_auto_stop`, `set_lock`, `check_lock`, `enforce` take `entry_id` as first
   argument. Every call site in `service_mixins/*.py` already has
   `coordinator.config_entry.entry_id`.
3. `_execute_stop` resolves the API with
   `async_get_coordinator(hass, entry_id).device.api`; if the entry is not
   loaded, log and skip (do not fall back to another controller).
4. `service_manager.set_safety_lock` / `check_safety_lock` forward the entry id.

**Regression test.** Two fake coordinators with distinct entry ids and distinct
`spec=VioletPoolAPI` mocks. Arm a stop for entry B; assert only B's API received
`set_switch_state`. Set a lock on A; assert `enforce` on B does not raise.

---

### A3 — `smart_dosing action=stop` is blocked by its own cooldown (integration)

**File:** `service_mixins/dosing.py` around line 90-120.

**What is wrong.** `safety_guard.enforce(device_key, ...)` runs **before** the
`if action == "manual_dose" / "auto" / "stop"` branch. After a manual dose the
guard arms a 300 s cooldown, so `stop` (and `auto`) raise "Safety interval
active" for five minutes unless the caller passes `safety_override=True`. A user
who wants to abort a running dose cannot.

**How to fix.** Move the `enforce` call inside the `manual_dose` branch (the
refill and backwash handlers already do it this way). `stop` must never be
gated by a cooldown.

**Regression test.** Set a lock for `DOS_1_CL`, call the handler with
`action="stop"`, assert no exception and that `manual_dosing`/DOSSTOP was
awaited.

---

### A4 — `control_extension_relay` sends non-existent keys and state codes as actions (integration)

**File:** `service_mixins/extension.py` around line 222-255; schema in
`service_schemas.py`; docs in `services.yaml`.

**What is wrong.** The key is built as `f"EXT{relay_id}_1"`, so relay 3 becomes
`EXT3_1`. The controller only has `EXT1_1..EXT1_8` and `EXT2_1..EXT2_8`. The
action sent is `"4"`, `"6"`, `"0"` or `str(state)`, i.e. *read* state codes,
whereas the command grammar is `EXT1_1,{ON|OFF|AUTO},{duration},0`.
`tests/test_service_control.py` (around line 318-418) asserts this wrong
behaviour, so it stays green.

**How to fix.**
1. Schema: replace `relay_id` with `bank` (`vol.In([1, 2])`) and `relay`
   (`vol.Range(1, 8)`), or accept a `relay_key` validated with
   `vol.In([k for k in SWITCH_FUNCTIONS if k.startswith("EXT")])`.
2. Handler: `await coordinator.device.api.set_switch_state(f"EXT{bank}_{relay}", action, duration=duration)`
   with `action` mapped `on→ACTION_ON`, `off→ACTION_OFF`, `auto→ACTION_AUTO`.
   Drop the numeric `state` field (or map 4→ON, 6→OFF, 0→AUTO).
3. Update `services.yaml`, `strings.json`, all `translations/*.json`, the
   wiki (`docs/wiki/Services.md` promises "EXT1_1 to EXT8_8") and rewrite the
   tests.

**Regression test.** Call with `bank=2, relay=5, action="on"`; assert
`set_switch_state("EXT2_5", "ON", duration=0)`.

---

### API-A5 — State-changing GET commands are retried (double actuation)

**Files (API package):** `api.py` (`_request`, `should_retry`), `_api_outputs.py`,
`_api_system.py`.

**What is wrong.** `should_retry = retryable if retryable is not None else method_upper in {"GET", "HEAD"}`.
The controller uses GET for nearly every mutation, so `set_switch_state`,
`set_output_test_mode`, `set_omni_position`, `set_rs485_live`, `end_rs485_live`,
`reset_blocking`, `set_system_service`, `init_update` are all retried up to
`max_retries` times on timeout or 5xx. A timeout *after* the controller applied
the command re-sends it. `PUSH` actions (digital-rule trigger, cover
open/close/stop) are toggles, so a retry flips the state back or moves the
cover twice. v0.0.36 already made POSTs non-retryable for exactly this reason.

**How to fix.**
1. Add `_NON_RETRYABLE_ENDPOINTS = frozenset({API_SET_FUNCTION_MANUALLY, API_SET_OUTPUT_TESTMODE, API_SET_RS485_LIVE, API_RESET_BLOCKING, API_INIT_UPDATE, <service enable/disable endpoints>})`
   in `api.py`.
2. `should_retry = retryable if retryable is not None else (method_upper in {"GET", "HEAD"} and endpoint.split("?")[0] not in _NON_RETRYABLE_ENDPOINTS)`.
3. Additionally pass `retryable=False` explicitly from every command method so
   the intent is visible at the call site.
4. Changelog entry, release 0.0.39, bump pin in `violet-hass`.

**Regression test.** Mirror `test_manual_dosing_post_is_not_retried` for
`trigger_digital_input_rule` on a 500 and for `init_update` on a 503: assert
exactly one request was sent.

---

### API-A6 — Rate-limiter timeout is a bypass, not a back-off

**File (API package):** `api.py` around line 344-354.

**What is wrong.** When `wait_if_needed(timeout=10.0)` times out, the code logs
a warning, sleeps 1 s and **sends the request anyway without a token**. Under
sustained overload every caller that waited 10 s then hits the controller at
once — the opposite of what the limiter is for.

**How to fix.** Raise instead of proceeding:
`raise VioletPoolAPIError(f"Rate limit wait for {endpoint} exceeded {API_RATE_LIMIT_WAIT_TIMEOUT}s") from err`
and make the timeout a named constant in `const_api.py`. If a caller needs the
old behaviour, add an explicit constructor flag (default off).

**Regression test.** Patch `RateLimiter.wait_if_needed` to raise
`TimeoutError`; assert `get_readings()` raises `VioletPoolAPIError` and the
HTTP mock recorded zero requests.

---

## P1 — Functional bugs

### B1 — Wrong password at startup never reaches the re-auth flow (integration)

**Files:** `device.py` `async_setup_device` (around line 1118-1199),
`__init__.py` `async_setup_entry` (around line 547-557).

**What is wrong.** The setup retry loop catches `except Exception` (so a
`VioletAuthError` from `device.async_update()` is retried three times and then
turned into `ConfigEntryNotReady`). The outer `except Exception` in
`async_setup_device` and again in `async_setup_entry` also wrap
`ConfigEntryAuthFailed` into `ConfigEntryNotReady`. Result: a wrong password
loops forever as "not ready"; `config_flow.async_step_reauth` is unreachable
from startup. (The coordinator's `_async_update_data` does the right thing at
line ~1104-1107; only the setup path is broken.)

**How to fix.**
1. In the loop: `except VioletAuthError as err: raise ConfigEntryAuthFailed(str(err)) from err`
   before the generic handler.
2. In both outer handlers add `except ConfigEntryAuthFailed: raise` before
   `except Exception`.
3. Simplify while there: drop the manual three-attempt loop and call
   `await coordinator.async_config_entry_first_refresh()` once. HA already
   retries `ConfigEntryNotReady` with back-off; the manual loop only adds 4-6
   extra requests per start.

**Regression test.** Mock `VioletPoolAPI.get_readings` to raise
`VioletAuthError`; `async_setup_entry` must raise `ConfigEntryAuthFailed`, not
`ConfigEntryNotReady`.

---

### B2 — Setpoint writes from number/select snap back to the old value for up to 60 s (integration)

**Files:** `number.py` (`async_set_native_value`, `_delayed_refresh`),
`select.py` (`async_select_option`), `device.py` (`_fetch_config_values`,
`request_config_refresh`, `update_setpoint_cache`), `entity.py` (`get_value`).

**What is wrong.** `getConfig` values (setpoints, `DOSAGE_*_use`) are cached
for `CONFIG_REFRESH_INTERVAL = 60` s. Only `climate.py` calls
`coordinator.update_setpoint_cache(...)`, which forces a refetch. `number.py`
and `select.py` set an optimistic value, schedule a refresh after 0.5 s, and
that refresh serves the **stale** cached config. The entity shows the new value
for half a second, then the old one for up to a minute.

**How to fix.**
1. In `number.async_set_native_value`, after a successful write call
   `self.coordinator.update_setpoint_cache(<config key actually written>, value)`.
2. In `select.async_select_option`, for the dosing/config branches call
   `self.coordinator.device.request_config_refresh()` before scheduling the
   delayed refresh.
3. Make `VioletPoolControllerEntity.get_value()` consult
   `coordinator._setpoint_cache` (expose it via a public
   `coordinator.get_cached_setpoint(key)`), so every platform benefits and
   `climate.py` stops reaching into a private attribute.

**Regression test.** Extend `tests/test_setpoint_cache_invalidation.py`: a
number write must set `device._config_refresh_requested` (or whatever the flag
is called) and the next poll must call `get_config`.

---

### B3 — Services: unusable from the UI, missing from `services.yaml`, area targeting rejected (integration)

**Files:** `services.yaml`, `service_schemas.py`, `services.py`, `strings.json`,
`translations/*.json`, `service_manager.py`.

Verified with a script against the audited commit:

- **17 services have neither `target:` nor a `device_id`/`entity_id` field in
  `services.yaml`**, while every schema in `service_schemas.py` requires one via
  `cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID)`. A UI call always
  fails validation: `control_heater_http, control_solar_http, control_cover_http,
  control_backwash_http, manual_dosing_http, configure_dosing, set_dosing_target,
  set_dosing_daytime, set_dosing_max_daily, enable_dosing, configure_temp_rule,
  configure_analog_rule, configure_switching_rule, configure_timer_rule,
  enable_rule, control_extension_relay, configure_sensor_calibration`.
  `control_backwash_http` additionally lacks its required
  `duration_seconds`/`safety_override` fields.
- **9 registered services are absent from `services.yaml` and from
  `strings.json["services"]`**: `configure_overflow, configure_refill,
  control_pump_http, control_refill_http, get_backwash_status,
  get_calibration_status, get_overflow_status, get_refill_status,
  get_system_update_status`. They show up in Developer Tools without
  description or fields.
- **3 dead keys** in `strings.json` (and in every translation file):
  `set_all_dmx_scenes_mode, set_digital_input_rule_lock_state,
  trigger_digital_input_rule` are not registered.
- The four services that *do* declare `target:` (`control_pump, smart_dosing,
  manage_pv_surplus, set_light_color_pulse`) reject `area_id`/`label_id`/
  `floor_id`: HA merges the target into `call.data`, and the `vol.Schema` has
  `PREVENT_EXTRA`.
- An unknown or unloaded `device_id` yields an empty coordinator list and the
  handler silently returns success.

**How to fix.**
1. Add `target: {device: {integration: violet_pool_controller}}` to all 17
   entries, plus the missing fields.
2. Add the 9 missing services to `services.yaml`, `strings.json` and the ten
   translation files (copy field definitions from `service_schemas.py` /
   `refill_overflow_schemas.py`). Remove the 3 dead keys everywhere.
3. Build target-capable schemas with `cv.make_entity_service_schema({...})`
   and resolve targets with
   `homeassistant.helpers.service.async_extract_config_entry_ids(call)` in
   `service_manager.get_coordinators_for_call`.
4. When no coordinator matches, raise
   `ServiceValidationError(translation_domain=DOMAIN, translation_key="no_matching_device")`
   (add the key to `strings.json`/translations).
5. Use `ServiceValidationError` (not `HomeAssistantError`) for every
   user-input problem in `service_mixins/_validation.py` and the handlers;
   keep `HomeAssistantError` for API failures. The `exceptions.*` keys
   `invalid_value`, `value_out_of_range`, `invalid_action`, `api_error` already
   exist in `strings.json`.
6. Schema/YAML drift to align: `control_pump.duration` (YAML max 86400,
   schema max 3600), `manage_digital_rules.rule_key` (YAML lists 1-7, schema
   1-8), `smart_dosing.dosing_type` (schema accepts `H2O2`, YAML does not; see
   B14), `control_pump_http.speed` accepts 0 which sends "manual ON at speed
   0" — restrict to 1-3.

**Regression test.** See D1 (parity test). It must fail on the audited commit
and pass after this package.

---

### B4 — Config flow: sensor discovery ignores the port and can create an entity-less entry (integration)

**Files:** `config_flow_utils/sensor_helper.py` (`get_grouped_sensors`),
`config_flow.py` (`_auto_configure_entities`, `_detect_active_features`,
`_test_connection`).

**What is wrong.**
- `_test_connection` appends `:port` to the host for non-default ports;
  `get_grouped_sensors` builds `VioletPoolAPI(host=config_data[CONF_API_URL])`
  **without** the port. For a controller on port 8080 the test succeeds, the
  discovery fails, the exception is swallowed and `{}` is returned.
- `get_grouped_sensors` also calls `validate_credentials_strength()`, which
  raises for controller passwords shorter than 4 characters or in a small
  blacklist. The connection test does not apply that rule, so "1234" passes the
  test and then silently produces an empty result.
- `_auto_configure_entities` then stores `CONF_SELECTED_SENSORS = []`.
  `entity_selection.py` treats `None` as "everything" but an **empty list as
  "nothing"** — the entry is created with no keyed entities and no error.
- `_detect_active_features` has no rule for `dmx_scenes` and `eco_mode`,
  although both are in `AVAILABLE_FEATURES` and `feature_keys.py` routes
  `DMX_*`/`ECO*` keys to them. Fresh setups hide DMX and ECO until the user
  re-enables them in options.

**How to fix.**
1. In `get_grouped_sensors` use the same host+port helper the connection test
   uses (`with_non_default_port(...)` in `config_entry_helpers.py`).
2. Remove `validate_credentials_strength` from the discovery path (it is the
   controller's password, not something the user chooses).
3. In `_auto_configure_entities`: if `detected_keys` is empty, store `None`
   (= all) and log a warning; never store `[]` from auto-detection.
4. Replace the hand-written marker table in `_detect_active_features` with
   `feature_for_key()` from `feature_keys.py`:
   `active = sorted({f for k in detected_keys if (f := feature_for_key(k))})`.

**Regression test.** Config-flow test with port 8080 where the API mock
asserts the host it was constructed with; a second test where discovery
returns `{}` and asserts `CONF_SELECTED_SENSORS is None`.

---

### B5 — Options flow copies `entry.data` (incl. password) into `entry.options` and shadows later reconfigures (integration)

**Files:** `config_flow_support.py` (`OptionsFlowHandler.current_config` and
every `async_create_entry(data=final_options)`), `config_entry_helpers.py`
(`get_entry_value`), `device.py` (`update_api_config`).

**What is wrong.** `current_config = {**data, **options}` and every options
step saves `{**self.current_config, **self._updated_options}`. After the first
options save, host/port/username/**password**/polling/timeout live in
`options` too. `get_entry_value()` is options-first, so a later
`reconfigure_connection` that writes new polling/timeout into `data` is
silently overridden by the stale copy in `options`. `update_api_config` sees
credentials in options and rebuilds the API client on every options save.

**How to fix.**
1. Save only the changed keys:
   `return self.async_create_entry(title="", data={**self.config_entry.options, **self._updated_options})`.
2. Add a one-off migration (bump `CONFIG_ENTRY_VERSION` or a minor version) that
   strips `CONF_API_URL, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, CONF_USE_SSL,
   CONF_VERIFY_SSL, CONF_DEVICE_ID` from existing `entry.options`.
3. Then simplify `device.update_api_config` (see C-list) — most of it exists
   to cope with this shadowing.

**Regression test.** Options-flow test: after saving features, assert
`entry.options` contains no `CONF_PASSWORD`. Reconfigure test: change polling
in `data` after an options save and assert `get_entry_value` returns the new
value.

---

### B6 — Generic `except Exception` swallows the integration's own translated errors (integration)

**Files:** `switch.py` (`_set_switch_state`, around line 540-568),
`climate.py` (two sites around line 388 and 449), `select.py` (around line 316).

**What is wrong.** Inside the `try` the code raises
`HomeAssistantError(translation_key="failed_to_set_value")`; the trailing
`except Exception` catches it and re-raises `unexpected_error` with the message
as `detail`. Users see "Unexpected error: …" instead of the intended text.
`number.py` and `light.py` already do it right.

**How to fix.** Add `except HomeAssistantError: raise` immediately before each
generic `except Exception`.

**Regression test.** Make the API mock return `{"success": False}`; assert the
raised `HomeAssistantError.translation_key == "failed_to_set_value"`.

---

### B7 — Climate fabricates 28 °C for out-of-range setpoints and silently ignores writes (integration)

**File:** `climate.py` (`_get_target_temperature` around line 232-248,
`_validate_temperature`, `async_set_temperature`, temperature limits in
`const_features.py`).

**What is wrong.** If the controller setpoint is outside 20-35 °C (heater) or
20-40 °C (solar) the entity returns `DEFAULT_TARGET_TEMP` (28 °C) and a write
outside that range is dropped with `return`. The API accepts 5-45 / 5-55 °C
(`SETPOINT_RANGES` in `_api_model.py`). A whirlpool at 38 °C shows a fabricated
28 °C and cannot be changed from HA. Fabricated state contradicts
`SECURITY.md`.

**How to fix.** Set `_attr_min_temp/_attr_max_temp` from the API's
`SETPOINT_RANGES`; return the real value (or `None`) in
`_get_target_temperature`; in `async_set_temperature` raise
`ServiceValidationError(translation_key="value_out_of_range", ...)` instead of
returning. Align `const_features.py` ranges. Also import `STATE_AUTO_ACTIVE`
from `state_constants.py` instead of redefining it with a different value (3
vs 1) at the top of `climate.py`.

**Regression test.** Coordinator data with `HEATER_set_temp = 38`; assert
`target_temperature == 38`.

---

### B8 — Pump speed level detection treats "manual OFF" as active (integration)

**Files:** `switch.py` around line 345-356 (`int(rpm_val) > 0`),
`sensor_modules/energy.py` around line 78 (same expression).

**What is wrong.** `PUMP_RPM_n` carries a state code 0-6. Codes 2, 5, 6 are
OFF states but `> 0` counts them as active, so the switch attribute reports a
speed and the power sensor reports watts for a pump that is off.
`number.py` already uses the correct `in (1, 3, 4)`.

**How to fix.** Replace `int(rpm_val) > 0` with `int(rpm_val) in (1, 3, 4)` in
both files; better, add `get_state_code(key)` to the base entity (see B10) and
use `get_state_definition(code).is_active`.

**Regression test.** `PUMP_RPM_2 = "6"` must yield `active_speed is None` and
power 0.

---

### B9 — Light platform gated on the wrong feature (integration)

**File:** `light.py` around line 129; `const_features.py` `DMX_LIGHTS`.

**What is wrong.** `if "led_lighting" not in active_features: return` while
every `DMX_LIGHTS` entry declares `feature_id: "dmx_scenes"`, which is never
read. Disabling "DMX Scenes" keeps the 12 lights; disabling "LED Lighting"
removes them.

**How to fix.** Delete the module-level check; inside the loop
`if (fid := light_config.get("feature_id")) and fid not in active_features: continue`.

**Regression test.** Setup with `active_features=["led_lighting"]` only must
create zero DMX lights; with `["dmx_scenes"]` twelve.

Same pattern in `binary_sensor.py` around line 236: it consults a separate
`BINARY_SENSOR_FEATURE_MAP` instead of `sensor_config["feature_id"]`, so
`INPUT1..12`/`INPUT_CE1..4` ignore the `digital_inputs` feature. Use the
`feature_id` from the table and delete the map.

---

### B10 — Composite states `"3|PUMP_ANTI_FREEZE"` mis-parsed outside `interpret_state_as_bool` (integration)

**Files:** `entity.py`, `climate.py` (`get_int_value` on `HEATER`/`SOLAR`),
`select.py` (`current_option`, `isdigit()` path), `switch.py` (hierarchy
attributes), `light.py` (`is_on`).

**What is wrong.** `convert_to_int("3|PUMP_ANTI_FREEZE")` returns `None`, so
climate reports `HVACMode.AUTO`/`IDLE` for a heater that is on, and the select
falls into the string path and reports `auto` for `"6|…"`.

**How to fix.** Add `get_state_code(key) -> int | None` to
`VioletPoolControllerEntity` that applies `parse_composite_state()` first, and
use it in the four places.

**Regression test.** Parametrised over `"3|PUMP_ANTI_FREEZE"`, `"6|X"`, `"1"`,
`"[]"`.

---

### B11 — Select entities: dosing "on" equals "auto", flocculant reads the wrong key, PV surplus offers a fake "auto" (integration)

**File:** `select.py` around line 140-180 and 262-278; `const_features.py`
`SELECT_CONTROLS`.

- `option in (MODE_AUTO, MODE_ON)` both call `set_dosage_enabled(..., True)`
  and the read path never returns "on" → selecting "on" snaps to "auto".
  Give dosing selects `options=[off, auto]` only.
- `dos_floc_mode` writes `DOSAGE_floc_use` but reads the `DOS_6_FLOC` output
  state, so an enabled-but-idle flocculant shows "off". Resolve the read key
  from `BINARY_DOSING_CONFIG_KEYS` as well.
- `pvsurplus_mode` offers "auto" but the API rewrites `AUTO` to `OFF` with a
  warning. Mark it `binary: True` (and fix `manage_pv_surplus mode=auto` in
  `service_mixins/climate.py` the same way, or document that "auto" releases
  the HTTP trigger).
- Attribute keys `HEATER_TARGET_TEMP`/`SOLAR_TARGET_TEMP` do not exist
  (the real config keys are `HEATER_set_temp`/`SOLAR_maxtemp`); the same wrong
  keys are used in `switch.py` attributes.

**Regression test.** There are no select tests today; add `tests/test_select.py`
covering the three cases.

---

### B12 — Update entity declares `PROGRESS` but never exposes `update_percentage` (integration)

**File:** `update.py` (feature flags around line 117-121; `_update_progress`
is written at four places, never read by HA).

**How to fix.** Add
```python
@property
def update_percentage(self) -> int | None:
    return self._update_progress if self._update_in_progress else None
```
Also: the user-facing strings "Update läuft: …", "Update läuft bereits auf
der Steuerung", "initiiert" in `update.py` are German in code; move them to
`exceptions`/state translations (see C6). `update_helper._compare_versions`
returns 0 for non-numeric parts ("1.2.0-beta"), hiding updates — compare with
`packaging.version` or `awesomeversion` (HA ships `awesomeversion`).

---

### B13 — `EnhancedErrorHandler` is never fed; diagnostics and error services always report zero (integration)

**Files:** `error_handler.py` (class around line 309-540), `device.py`
(`async_update` failure branches), `service_diagnostics.py`,
`diagnostics.py`.

**What is wrong.** `classify_error/record_error/record_success` have no
callers outside the module (verified by grep). `get_error_summary`,
`should_trigger_reauth`, `get_recovery_suggestion` and the `error_statistics`
block in diagnostics therefore always show an empty history. In addition
`offline_duration` mixes clocks: `_offline_since` is set with
`time.monotonic()` but read with `time.time()` in `get_error_summary`
(≈1.7 billion seconds).

**How to fix (pick one, do not leave it half-wired).**
- *Wire it:* one handler instance **per device** (not the process-global
  singleton), call `record_error(classify_error(err))` in the three failure
  branches of `device.async_update` and `record_success()` on success; fix the
  clock; replace the `list` + `pop(0)` history with `deque(maxlen=100)`.
- *Or delete it* together with the `get_error_summary`/`clear_error_history`
  services and the diagnostics block, and say so in the changelog.

The diagnostics services also use the global handler for "per device" output
and `clear_error_history` wipes all controllers before validating ids
(`service_diagnostics.py` around line 265-273) — per-device instances fix both.

**Regression test.** Fail two polls, succeed one; assert
`get_error_summary()["total_errors"] == 2` and a sane `offline_duration`.
The existing `assert total_errors >= 0` in `test_offline_scenarios.py` is
vacuous and must be replaced.

---

### B14 — H2O2 dosing paths are inconsistent across integration and API

**Files:** `service_helpers.py` (`DOSING_API_MAPPING`, `DOSING_TYPE_MAPPING`),
`service_mixins/dosing.py`, API `_api_dosing.py`, API `const_api.py`.

`smart_dosing dosing_type=H2O2 action=manual_dose` calls
`api.manual_dosing("H2O2")`, which raises "Unknown dosing type" because the
API's `DOSING_FUNCTIONS` has no H2O2; `action=stop` maps H2O2 to `DOS_1_CL`
and stops **chlorine**. The API constants say H2O2 shares `DOS_1_CL` with
`from=3`, but `_trigger_dosing` hard-codes `"from": "1"`.

**How to fix.** API side: add `source: int = 1` to `_trigger_dosing` and an
H2O2 entry (`"H2O2": "DOS_1_CL"`, source 3) or document that H2O2 manual dosing
is unsupported. Integration side: either route H2O2 through the new API
argument or remove `H2O2` from `DOSING_TYPE_MAPPING` and the schema until the
API supports it. Never let `stop` fall through to the chlorine channel.

---

### B15 — `HardwareConfig` crashes on non-numeric flags and loses all controller names (integration)

**File:** `hardware_config.py` (six `int(self.config.get(enable_key, 0))`
sites around lines 68, 84, 107, 138, 210, 250).

**What is wrong.** A flag value such as `"N/A"`, `""` or `"true"` raises
`ValueError` in `__init__`; `device.load_hardware_config` swallows it and every
controller-provided name is lost with one log line.

**How to fix.** Add `_as_int(value, default=0)` (`int(float(str(value).strip()))`
in a `try`, default on failure) and use it at all six sites. Also do not set
`_hardware_config_loaded = True` on exception in `device.load_hardware_config`
so a transient error is retried on the next reload.

**Regression test.** `HardwareConfig({"DI1_enabled": "N/A"})` must not raise.

---

### B16 — Coordinator serves stale data as a successful update for the first four failures (integration)

**File:** `device.py` `async_update` (around line 535-579 and 669-724),
`entity.py` `available`.

**What is wrong.** Failures 1-4 return `self._data` unchanged, so
`coordinator.last_update_success` stays `True` and entities keep showing old
values as fresh — with adaptive polling at 60 s that is about five minutes of
stale-as-live data. The three failure branches also diverge: the
`controller_unavailable_*` repair issue is only raised in the empty-data
branch, never for `VioletPoolAPIError`, and it is only deleted when the *same*
device object recovers, so a restart leaves a stale repair until the user
clicks "Fix".

**How to fix.** Raise `UpdateFailed` on every failed poll (the coordinator
keeps the last good `data` and flips `available` itself); keep the counter only
for log throttling. Factor one `_record_failure(reason)` used by all three
branches. After a successful first refresh in `async_setup_device` call
`async_delete_issue(hass, DOMAIN, f"controller_unavailable_{entry_id}")`.
`tests/test_offline_scenarios.py` encodes the current behaviour and must be
updated deliberately.

---

### B17 — Unstable main device identifier (integration)

**Files:** `device.py` (`device_info`, identifier `f"{api_url}_{device_id}"`),
`device_hierarchy.py`.

**What is wrong.** Host and non-default port are baked into the device
identifier. A reconfigure that changes the IP creates a *new* device; the old
one keeps the user's name/area and lingers. Entity unique ids are already
`{entry_id}_{key}`, so only the device is unstable.

**How to fix.** Use `(DOMAIN, entry.entry_id)` as identifier and migrate once
in `async_migrate_entry`: look up the device by the old identifier and
`async_update_device(device_id, new_identifiers={(DOMAIN, entry.entry_id)})`.
Also make `async_remove_config_entry_device` return `False` for the main
device while the entry is loaded.

---

### B18 — Config flow: reconfigure keeps the old unique id, wrong error key, lost form input, plaintext password defaults (integration)

**File:** `config_flow.py`, `config_flow_support.py`.

- `async_step_reconfigure_connection` updates `data` but never
  `async_set_unique_id`; use `self.async_update_reload_and_abort(entry, data_updates=..., unique_id=new_id)`.
- It sets `errors[CONF_API_URL] = "invalid_ip"` but the translation key is
  `invalid_ip_address` (`config_flow_utils/constants.py`); the UI shows the raw
  string.
- After a failed connection the form is re-rendered with static defaults, so
  all input is lost; use `self.add_suggested_values_to_schema(schema, user_input)`.
- Reconfigure and repair forms put the stored password as a plain `str`
  default; use `TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))`
  and never pre-fill it.
- Zeroconf: `self._title_placeholders` is stored but
  `self.context["title_placeholders"]` is never set, so the discovery card
  shows only the integration name.
- `reauth` reads `self.context["entry_id"]`; use `self._get_reauth_entry()`.
- `async_step_feature_selection`, `async_step_sensor_selection`,
  `async_step_repair` and their schemas/strings are unreachable — delete.
- `discovery.py` and `__init__.async_zeroconf_get_service_info` are dead: HA
  routes manifest zeroconf matches to `ConfigFlow.async_step_zeroconf`; nothing
  calls them. Delete both and `tests/test_discovery.py` (keep
  `test_discovery_duplicates.py`, which tests the flow).

---

### B19 — Status sensors default to German and mis-map `PVSURPLUS` (integration)

**File:** `sensor_modules/generic.py` (`VioletStatusSensor.native_value`),
`const_sensors.py` `STATUS_SENSORS`.

**What is wrong.** `native_value` returns `VioletState(raw).display_mode`; the
API's default translation language is `"de"` and the integration never calls
`set_state_translation_language`, so English users get German status text.
`PVSURPLUS` uses its own scheme (0 off, 1 on via digital input, 2 on via
HTTP) but is mapped through `DEVICE_STATE_MAPPING`, so value 2 reads as "Auto –
Priority OFF".

**How to fix.** Return a stable mode key (`auto_active, auto_inactive,
manual_on, manual_off, frost_protection, error, maintenance, unknown`; special
case for `PVSURPLUS`), declare `device_class=SensorDeviceClass.ENUM` with
`options`, and add `entity.sensor.<key>.state.*` translations in all ten
files. The same applies to `pool_health`/`active_errors`, whose state
translations exist only in `strings.json` and not in `en.json`/`de.json`.

---

### B20 — Sensor metadata depends on the value at startup (integration)

**File:** `sensor_modules/base.py` (`_is_boolean_value` used in
`determine_device_class`/`determine_state_class`/icon around lines 421, 501,
555).

**What is wrong.** For keys not in `UNIT_MAP`, device class and icon are
chosen from the *raw value* at setup. `orp_value_min`, `pH_value_max`,
`onewire7_value_min` (probe missing → "0") get `device_class=None` and a toggle
icon when the value happens to be 0/1, and TEMPERATURE/VOLTAGE otherwise.
Unit and device class flipping between restarts corrupts long-term
statistics.

**How to fix.** Decide on the key only: an explicit `_BOOLEAN_VALUE_KEYS`
set, delete the value heuristic. Also return `state_class=None` for
state-code keys (`DIGITALINPUTRULE_STATE_*`, `INPUT1..12`, `DOS_*_USE`,
`DMX_SCENEn`) instead of `MEASUREMENT`, and drop
`device_class=SensorDeviceClass.AQI` on the LSI/CSI saturation-index sensors.

**Regression test.** Build the sensor twice with values `"0"` and `"25.3"`
for `onewire7_value_min`; device class and icon must be identical.

---

### B21 — Overflow/refill configuration services write flags the user did not send (integration)

**File:** `refill_overflow_service.py` (`handle_configure_overflow`,
`handle_configure_refill`), `refill_overflow_schemas.py`,
`service_mixins/system.py` (calibration).

**What is wrong.** `OVERFLOW_use`, `OVERFLOW_dryrun_use`, `OVERFLOW_bathing_use`
are always written with default `True`, so a call meant to raise the level
also enables two protections — an implicit state change beyond the explicit
command. Truthiness checks (`if dryrun := ...`, `if blocks_dosing := ...`,
`if offset := ...`) make `False` and `0.0` unwritable.

**How to fix.** Make the `*_use` fields `vol.Optional` without defaults, send
only keys the caller provided, and test with `is not None`. Status services
(`get_refill_status`, `get_overflow_status`, backwash status) compare raw
readings (`> 0`, `int(...)`) that may be strings or composite; parse with the
entity helpers (*needs verification* of the real key formats — none of
`REFILL_state`, `OVERFLOW_*` appear in `tests/getReadings_spec.json`).

---

### B22 — Service handlers write config keys that do not exist in the API package (integration, *needs verification*)

**Files:** `service_mixins/climate.py` (`HEATER_target_temp`,
`SOLAR_target_temp`), `service_mixins/dosing.py` (`DOSAGE_x_set_ppm`,
`_set_ph`, `_daytime_on/_off`, `_max_daily_ml`), `service_mixins/rules.py`
(`_prog_*`), `service_mixins/system.py` (`SENSOR_{n}_offset/...`).

The API package's authoritative names are `HEATER_set_temp`, `SOLAR_maxtemp`,
`DOSAGE_phminus_setpoint`, `DOSAGE_chlorine_setpoint_orp`, … and it exposes
`set_device_temperature`, `set_ph_target`, `set_orp_target`,
`set_target_value` with range checks. Use those instead of hand-built keys.
For the dosing daytime/max-daily, rule and calibration keys, capture a real
`getConfig` dump from a controller and either fix the names or remove the
services; do not ship writes to guessed keys.

---

### B23 — `http_control.py` bypasses API validation and the auth guard (integration)

**File:** `http_control.py`, `auth_guard.py`.

`VioletControlClient.set_function_manually` calls the private `api._request`
directly, so it skips `validate_duration`, the dosing routing to
`/triggerManualDosing`, the standalone-mode guard, the cover
`acknowledge_unsafe` gate, and `AuthReportingAPI` (a 401/403 there never
raises the `controller_requires_auth` repair). `timeout` parameters are
accepted and ignored.

**How to fix.** Reduce `VioletControlClient` to a thin façade over public API
methods (`set_switch_state`, `set_cover_command(acknowledge_unsafe=True)`,
`set_config`, `manual_dosing`). If the API lacks something (e.g. the
`from_param` for H2O2), add it to the API package (B14) rather than
re-implementing the wire format here. Extend `_CONTROL_METHOD_NAMES` in
`auth_guard.py` with `trigger_digital_input_rule`, `control_pump`,
`end_rs485_live`.

---

### B24 — Diagnostics dump identifiers unredacted (integration)

**File:** `diagnostics.py`.

`current_data` dumps every controller key; `IP_ADDRESS`, `MAC_ADDRESS`,
`SERIAL_NUMBER`, `HW_SERIAL_CARRIER` are identifiers HA expects to be
redacted. Add them to `_REDACT_KEYS` and wrap the block in
`async_redact_data`. There is no test for `async_get_config_entry_diagnostics`
at all (coverage 0 %) — add one.

---

### B25 — `_disable_unsafe_switches` re-disables switches the user re-enabled (integration)

**File:** `__init__.py` around line 284-388.

It runs on every start and disables any unsafe switch whose
`disabled_by is None`, i.e. one the user deliberately re-enabled in the UI.
`switch.py` already sets `entity_registry_enabled_default` from the same
option. Drop the per-start pass, or only touch entries with
`disabled_by == RegistryEntryDisabler.INTEGRATION`, and record in
`entry.options` that the one-time migration ran.

---

### B26 — Services are never unregistered on last unload (integration)

**File:** `__init__.py` `async_unload_entry`, `services.py`.

`async_register_services` guards with `has_service(...)` and nothing removes
the services or the `VioletServiceManager` (with its `SafetyGuard` store and
timers) when the last entry unloads. Add `async_unload_services(hass)` that
removes all 44 services and cancels the guard's tasks, called when
`async_loaded_entries(hass)` becomes empty.

---

### API-B27 — `aiohttp<3.15` upper bound will block installation inside Home Assistant

**File (API package):** `pyproject.toml` `dependencies`.

HA core tracks aiohttp releases closely (2026.9 already ships 3.14.x). The
day HA moves to 3.15, `pip` inside HA refuses `violet-poolController-api` and
the integration fails to set up. Drop the upper bound (or `<4`) and keep the
`aioresponses` shim in `tests/conftest.py` as the compatibility layer.
Release as 0.0.39 together with A5/A6.

---

### API-B28 — Readings parsers raise `TypeError` on list/dict values

**File (API package):** `readings.py` (`_parse_output_state`,
`_parse_dmx_state`, `_parse_rule_state`, `_parse_pv_surplus`).

`int(raw)` is wrapped in `except (ValueError, KeyError)` only. The controller
does emit list values (`DOS_*_STATE` is "LIST, STRING" in
`docs/getReadings_clean.json`), and `VioletReadings({"DMX_SCENE1": []}).dmx_scenes`
crashes the consumer. Add one `_opt_int(raw)` helper
(`int(float(str(raw).split("|")[0].strip()))` inside
`except (ValueError, TypeError, OverflowError)`) and use it in all four.
Test with `[]`, `{}`, `"1.0"`, `"4|X"`.

---

### API-B29 — Smaller API defects (one PR)

- `_api_system.get_log`: `has_more = lines and ...` returns `[]` for an empty
  body and `split("\n")` keeps `\r`. Use `splitlines()` and
  `bool(lines) and lines[-1].strip() == "LOAD_MORE"`.
- Invalid JSON (HTML login/captive page) is a `VioletPayloadError`, which the
  circuit breaker counts; six such responses open the breaker and hide the
  real message. Add `VioletPayloadError` to `ignored_exceptions`.
- `ssl.create_default_context()` in `__init__` loads the system CA store from
  disk (blocking, on the event loop) only to set `CERT_NONE`. Return
  `ssl=False` from `_ssl_param` when verification is disabled.
- `set_target_value` validates `numeric_value` but posts the original string;
  send `numeric_value`.
- `_sanitize_config_payload` turns `None` into `"None"`, lists into `"1 2"`,
  `nan` into `0.0`; raise `VioletPoolAPIError` for non-scalar/non-finite
  values.
- `validate_api_parameter` silently rewrites keys (`"DOSAGE_ph.minus"` →
  `"DOSAGE_phminus"`); raise when `sanitized != param`.
- `validate_device_key` upper-cases case-sensitive keys (`pH_value` →
  `PH_VALUE`); validate with `^[A-Za-z0-9_]+$` and do not modify.
- `sanitize_numeric` turns `"1,5"` into `15.0`; treat a single comma as the
  decimal separator and return the default for anything that still does not
  parse.
- Priorities: `set_switch_state`/`set_output_test_mode` should run
  `API_PRIORITY_CRITICAL`, `set_config` `HIGH`, `get_history`/`get_log`
  `LOW`; today a pump-off command queues behind sensor polls.
- Credentials in a `host` string leak into the `ValueError` message
  (`"Invalid hostname format: admin:s3cret@…"`); use a fixed message.
  Truncate 4xx bodies copied into exceptions to ~200 chars. Allow `_` in the
  hostname regex (mDNS names such as `violet_pool.local`).
- `manual_dosing`: call `validate_duration` before `duration <= 0`
  (non-numeric input raises `TypeError` today).
- `parse_uptime_string` returns 0 if the firmware ever includes seconds;
  delegate to `parse_runtime_string`. `parse_epoch_seconds` should treat
  `ts <= 0` as unset.
- `circuit_breaker.py`: the "OPENED due to N failures" log prints the
  threshold, not the count; `get_stats()` "lock held" branch is unreachable.
- `utils_rate_limiter.get_stats()["current_tokens"]` is stale (no refill
  before read); `request_history`, `_last_known_tokens`,
  `history_cleanup_interval` are dead bookkeeping.
- Public exports promised in the changelog are missing from `__init__.py`:
  `validate_duration`, `RS485_PUMP_NAMES`, `RS485_PUMP_MODES`,
  `DEVICE_STATE_MAPPING`, `SWITCH_FUNCTIONS`, `DOSING_FUNCTIONS`,
  `API_PRIORITY_*`, `CircuitBreakerState`, `get_device_state_info`,
  `get_device_mode_from_state`. Add them and a test that `__all__` covers
  them.
- `max_retries` is really "attempts" (`attempt_limit = self._max_retries`);
  either fix the docs or use `+ 1`, and fix the misleading comment in
  `tests/test_api.py` around line 169.

---

## P2 — Code quality and performance

### C1 — De-duplicate the service layer (integration)

- The four dosing dicts (`DOSING_INDEX_MAP`, `DOSING_FROM_PARAM_MAP`,
  `DOSING_SYSTEMS`, `DOSING_SYSTEM_TO_KEY`) are pasted verbatim into
  `service_control.py` and every file in `service_mixins/` (8 copies); only
  `dosing.py` uses them. Move them to `service_helpers.py`, delete the unused
  `DOSING_CONFIG_PREFIX_MAPPING`, `DOSING_H2O2_FROM_PARAM`,
  `MIN/MAX_TEMPERATURE`, `MIN/MAX_PH` there.
- `service_schemas.py`: the `vol.All(vol.Schema({entity_id, device_id, ...}), has_at_least_one_key)`
  wrapper appears ~25 times and the dosing-system `vol.In` list 6 times.
  Factor `_targeted(fields) -> vol.Schema` and `DOSING_SYSTEM_SELECTOR`.
  (Superseded partly by B3 step 3 — do B3 first.)
- `services.py`: eight near-identical registration loops → one table
  `(name, handler, supports_response)`.
- `service_manager.py`: `get_coordinators_for_entities`, `extract_device_key`,
  `check_safety_lock`, `get_remaining_lock_time` are unused; delete. Its
  docstring says "supports HA from 2026.1" — the floor is 2026.8.
- `service_diagnostics.py` (814 lines) mixes diagnostics with maintenance
  control (`reset_blocking`, `set_can_amount`, `set_system_service`,
  `set_omni_position`); move those into `service_mixins/maintenance.py`.
- Every `raise HomeAssistantError(...)` inside an `except` without
  `from err` (pump, climate, cover, dosing, rules, extension, system mixins)
  loses the traceback; add `from err` (ruff rule B904 — consider enabling `B`
  in `pyproject.toml`).
- `set_light_color_pulse` sleeps up to 20 s inside the service call; run the
  pulse sequence as a background task like the DMX sequence.

### C2 — Dead code and duplicate constants (integration)

Delete after confirming with grep that nothing references them:

- `entity_cleanup.discard_provided_entities`, `device_hierarchy.discard_device_ids`
- `entity.get_bool_value`, `climate._get_expected_state`, `cover.is_open`,
  `cover._last_action` (test-only; rewrite `tests/test_cover.py` to assert on
  the API mock), `switch.async_added_to_hass` no-op,
  `switch._STATE_DESCRIPTIONS` (duplicates `state_constants.STATE_DEFINITIONS`)
- Four copies of `_handle_refresh_error` in `climate.py`, `select.py`,
  `number.py`, `switch.py` — identical to the one in `entity.py`; use the base
  one.
- `const.VERSION_INFO` (unused, says API 0.0.24 / 2026-07-19),
  `device._first_failure_logged` (written, never read), the duplicate
  `from violet_poolcontroller_api.api import VioletPoolAPI` inside
  `device.update_api_config`, the `ImportError` fallbacks for
  `VioletAuthError`/`VioletReadings` at the top of `device.py` (obsolete with
  API ≥ 0.0.38), `number.py`/`cover.py` compat shims for pre-2026.8 HA.
- `entity.STATE_MAP`, `AUTO_OFF_STATES == OFF_STATES`, `AUTO_ON_STATES ==
  ON_STATES`: derive one map from `state_constants.STATE_DEFINITIONS`.
- `hardware_config.py` hard-coded `entity_id` strings (never read).
- `sensor_organization.py` keys match no real entity key; only
  `service_diagnostics.py` imports it — either fix the keys or delete.
- `device_hierarchy._ONEWIRE_GROUPS` duplicates `SENSOR_FEATURE_MAP`; the
  hierarchy prefix table and `feature_keys.py` disagree (`ECO`, `OMNI_DC`
  missing; `_FEATURE_TO_GROUP` lacks `eco_mode`, `dmx_scenes`). Derive the
  group from `feature_for_key()` with a small override table.
- `switch.py` setup-time debug loops (around lines 745-762 and 819-838) call
  `_get_switch_state()` on not-yet-added entities and log "INIT → ON" at every
  start; remove.

### C3 — Performance (integration)

- `entity.available` logs at DEBUG on every property read while unavailable;
  with ~300 entities that is thousands of lines per outage. Log once per
  transition in the coordinator instead.
- `device.async_update` makes four full copies of the ~400-key dict per poll
  (`dict(_readings)`, `dict(data)`, `dict(self._data)`, `VioletReadings(data)`);
  return `self._data` and let `VioletReadings` make the single defensive copy.
- `device_hierarchy.build_device_info` runs a regex chain plus registry lookup
  per entity (~300×); cache `resolve_group` with `functools.lru_cache`.
- `generic._controller_uses_local_wall_epoch` recomputed per timestamp sensor
  per read; `specialized._collect_problems` runs twice per state write over all
  keys; `update.py` re-parses firmware info in three properties. Cache per
  coordinator data object (e.g. keyed by `id(coordinator.data)`).
- `feature_keys` rebuilds `set(active_features)` per call; accept a
  `frozenset` computed once per platform setup.
- `device.py`: `super().__init__(update_interval=timedelta(seconds=polling_interval))`
  uses the **unclamped** value while `_base_interval` is clamped; clamp both.
  `_firmware_version_poll_counter` counts config fetches, not polls, so
  `FIRMWARE_VERSION_REFRESH_POLLS = 360` means every 6 h, not hourly — rename
  to `FIRMWARE_VERSION_REFRESH_FETCHES = 60` or move the counter.
- "Lazy imports to avoid blocking the event loop" (`__init__.py`,
  `device.py`, `safety_guard.py`, `switch.py`) is inverted: an import inside
  an async function performs file I/O *on* the loop. Move them to module
  level.
- `datetime.now()` in `device.py`/`diagnostics.py` is naive local time; use
  `homeassistant.util.dt.utcnow()`.
- Adaptive idle detection ignores `COVER_STATE`, `LIGHT`, `DMX_SCENE*`,
  `PVSURPLUS`, `EXT*`; a moving cover is polled at 3× interval. Product
  decision — at least add cover-moving states.

### C4 — `device.update_api_config` (integration)

Reads credentials from `data` but change detection inspects only `options`;
`verify_ssl`/`dosing_standalone` are never compared; `use_ssl` defaults to
`True` here and in `__init__._extract_config` while `DEFAULT_USE_SSL = False`
(latent flip for entries without the key); timeout/retries are unclamped.
Every flow that changes connection data already reloads the entry. Delete the
method and have `async_update_listener` schedule a reload when any connection
field differs; hot-apply only polling options. Use `DEFAULT_USE_SSL`
everywhere.

### C5 — SafetyGuard persistence races (integration)

`cancel_auto_stop` fires `_remove_persisted` as a background task,
`arm_auto_stop` awaits `_persist_single`, and the cancelled task's `finally`
also removes the same key — three unlocked load-modify-save sequences on one
`Store`. Wrap every load/modify/save in one `asyncio.Lock`; in
`_schedule_auto_stop.finally` only remove when
`self._auto_stop_tasks.get(key) is asyncio.current_task()`; make
`cancel_auto_stop` async and await the removal; store the timers re-armed in
`async_setup` in `_auto_stop_tasks` so they can be cancelled. Do this together
with A1/A2.

### C6 — German in code (both repos)

Language policy says code, comments, log messages and fallback names are
English. Still German at the audited commit (the language-policy tests do not
scan Python sources in `violet-hass`, and the API test's word list misses
these):

- `violet-hass`: `update.py` ("Update läuft…", "initiiert"),
  `const_sensors.py` `name` fields (e.g. "Letzte Fehler-ID"; they are the
  fallback object-id source), `state_constants.py` `name_de`/`description_de`
  (move to translations), docstrings in `tests/test_sanitizer.py`,
  `tests/test_config_flow.py`, `tests/test_api.py`, `tests/test_device.py`,
  `tests/test_entity_state.py`, comments in `.gitattributes`,
  `tests/docker/test_credentials.example.txt`, all `Dashboard/*.yaml` headers,
  the badge alt texts in `CHANGELOG.md` lines 7-8.
- API package: `utils_sanitizer.py` (≈20 docstrings/log lines: "Sanitize
  einen …", "Gefährliche Zeichen entfernt", "Ungültiger …"),
  `utils_rate_limiter.py` (4 log lines), `_api_system.py`
  `"Unbekannter Fehlercode"`, `const_api.SWITCH_FUNCTIONS` labels
  ("Erweiterung", "DMX Szene", "Schaltregel"), `docs/API_REFERENCE.md` and
  `docs/violet_standalone_manual.md` (German files in the English docs root;
  `API_REFERENCE.md` also has ~150 mojibake sequences and header v0.0.23).
  The 0.0.38 changelog claims these files were translated — correct the
  changelog when fixing.

Extend `GERMAN_WORDS` in both `test_language_policy.py` files with `und, bei,
einen, eine, erlaubt, Wert, verwende, ungültig, verfügbar, zurück` (word
boundaries make these safe) and port the Python-source scan from the API repo
into `violet-hass/tests/test_language_policy.py` with exemptions for
`translations/`, `README.de.md`, `docs/wiki/*.de.md`.

### C7 — Translations parity (integration)

Runtime UI reads `translations/<lang>.json`, not `strings.json`, and they
have drifted:

- `en.json` lacks the whole `options.step.safety` step, the selectors
  `main_menu`, `options_menu`, `reconfigure_option`, `features`,
  `entity.sensor.pool_health.*`, `entity.sensor.active_errors`,
  `exceptions.read_only_entity`, and the `fields` sub-trees of ~30 services.
- `de.json` lacks `options.step.safety`, `reconfigure_connection…verify_ssl`,
  `exceptions.read_only_entity`, field names for six services.
- `strings.json` lacks `config.step.connection.data.port`,
  `options.step.settings.data.invert_cover`, ~91 sensor keys that `en.json`
  has, and carries ~19 unused sensor keys and 12 unused `switch.dmx_scene*`.
- `icons.json`: `sensor.firmware_version`, `sensor.recovery_success_rate`
  unused; many number/select/switch keys have no entry.
- `binary_sensor.py` synthesises icons by appending `-off` to any icon,
  producing non-existent MDI names (`mdi:gauge-off`, `mdi:expansion-card-off`);
  drop the property and add `state` blocks to `icons.json`.

Regenerate `en.json` from `strings.json` (they should be identical for a
custom integration), fix `de.json`, and add the parity test from D1.

---

## P3 — Tests

### D1 — Parity tests (write these first; they gate B3 and C7)

Add `tests/test_service_parity.py`:
- `set(services.yaml) == set(registered service names) == set(strings.json["services"])`
  (collect registered names by calling `async_register_services` on a
  `hass` fixture, or by importing the registration table after C1).
- every `services.yaml` entry has `target:` or a `device_id`/`entity_id`
  field when its schema requires one.
- for every service, the YAML `fields` keys equal the schema's keys.

Add `tests/test_translation_parity.py`:
- key set of `strings.json` equals key set of `translations/en.json`;
- every other language file has the same key set as `en.json`;
- every `translation_key` used in Python (`grep -o 'translation_key="[a-z_]+"'`)
  exists under the right platform in `strings.json`;
- every `exceptions` key raised in code exists.

### D2 — Cover the 0 % platforms

`binary_sensor.py`, `button.py`, `light.py`, `diagnostics.py`,
`sensor_organization.py` have no tests; `select.py`, `sensor.py`, `switch.py`
are below 30 %; `service_mixins/rules.py` at 9 %, `refill_overflow_service.py`
at 10 %. For each platform add one setup test (entities created from
`tests/getReadings_spec.json`, feature gating on/off) and one command test
per command path, asserting on a `MagicMock(spec=VioletPoolAPI)`.

### D3 — Regression tests listed in A1-A4, B1-B2, B4-B9, B13, B15, B20

Each package above names its test. Put them in the existing file for that
module where one exists.

### D4 — Test-infrastructure clean-up

- `tests/conftest_api_mock.py` is imported by nothing (only
  `conftest_ha_mock` is); delete it.
- `tests/conftest_ha_mock.py` (~600 lines of stub HA) and the mock branch in
  `conftest.py` only activate when HA / the API package are not installed —
  CI always installs both, so a test that passes only under the mocks is a
  false positive nobody sees. Delete the mock layer and make a missing HA/API
  a hard `pytest.exit("install requirements-dev.txt")`, or gate it behind an
  explicit `VIOLET_TEST_MOCKS=1`.
- `tests/conftest.py` monkey-patches (`dt_util.get_time_zone` remap,
  global `threading.enumerate` filter, socket-plugin juggling, Windows hacks):
  remove each one, run the suite on the pinned harness, keep only what is
  still required, and update `CLAUDE.md` ("thread-safety workaround") to
  match.
- `tests/docker/run_docker_test.sh` calls `docker compose` but no compose
  file or Dockerfile exists anywhere in the repo, and it issues real pump
  ON/OFF commands against hardware. Delete `tests/docker/` or add the compose
  file plus a prominent warning.
- `tests/live_*_check.py`: move to `scripts/live/`, read env vars inside
  `main()` instead of at import, document them in `CLAUDE.md`.
- `tests/test_translations.py`: duplicate `strings_data` fixture (two
  identical copies), `test_disclaimer_bilingual` is a `pass` stub.
- `tests/test_security_principles.py` only checks that files/constants
  exist; add behavioural assertions (setup and coordinator never call
  `set_switch_state`; auto-stop targets the originating entry).
- `tests/test_readings.py` (API repo) is largely vacuous (fixtures use keys
  the model does not expose, `assert x is not None`); rewrite against
  `pump`, `cover`, `onewire_*`, `dmx_scenes`, `digital_rules`, composite
  states. API repo `tox.ini` runs only `tests/test_api.py` while CI runs all
  of `tests/`; align on `pytest -q tests`.
- API repo: `tests/mock_server.py` serves `/setTargetValues` and
  `/setDosingParameters`, endpoints that do not exist on the controller
  (`_api_dosing.py` says so); remove them. `test_api_smoke.py` uses
  `time.sleep(2)` instead of the readiness poll that `test_mock_server.py`
  already has.

---

## P4 — Documentation, CI, packaging

### E1 — Pin floating GitHub Actions (supply chain)

`validate.yml`: `home-assistant/actions/hassfest@master`, `hacs/action@main`.
`security.yml`: `trufflesecurity/trufflehog@main` (×3),
`aquasecurity/trivy-action@master`. Pin each to a release tag or commit SHA
with a version comment (`uses: owner/action@<sha> # vX.Y.Z`); for hassfest,
which has no releases, pin a commit of `home-assistant/actions` and let
Dependabot bump it. Then delete `docs/CI_CD_ACTION_PINNING.md`, which
documented this task and was never executed.

### E2 — Remove tracked local files

`.zcode/plans/plan-sess_….md` (a German AI plan file) and
`.claude/settings.local.json` (Windows paths, PowerShell allow rules) are
committed. `git rm` both and add `.zcode/` and `.claude/settings.local.json`
to `.gitignore`.

### E3 — One source of truth for tool versions and floors

Floors differ between `requirements-dev.txt` (`ruff>=0.9.0`, `mypy>=1.0.0`,
`pytest>=8.3.0`), `tox.ini` (`ruff>=0.15.0`, `mypy>=2.1.0`), `pyproject.toml`
`[project.optional-dependencies].dev` (never installed; `tox` uses
`package = skip`) and `CLAUDE.md` (`ruff>=0.15.16`, `pytest>=9.0.3`,
`pytest-asyncio>=1.3.0`). Make `requirements-dev.txt` authoritative with the
`CLAUDE.md` floors, have `tox.ini` install `-r requirements-dev.txt`, delete
the `dev` extra from `pyproject.toml` (or reduce it to the same list), and
delete the `<0.13.317; python_version < '3.14'` harness line (tests run only
on 3.14). Fix the stale comments in `requirements.txt` ("Kept at 2026.6.0+"),
`requirements-dev.txt` ("pins pytest-asyncio==0.24.x"), `pyproject.toml`
("Home Assistant 2026.5.x"). Remove `[tool.mypy] mypy_path = ["../violet-poolController-api"]`
so mypy checks the installed package (which ships `py.typed`) and CI and local
runs see the same code.

### E4 — `CLAUDE.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, `SECURITY.md`

`CLAUDE.md`:
- "loads 7 platforms" in the tree vs "10 platforms" above (10 is right).
- "10 CI/CD pipelines" vs "(4 workflows)" (4 is right); "tests/ (21 files)"
  (51 test files); "4 automation templates" (5); "docs/ (27+ files)"; remove
  counts from the tree — they rot every release.
- Module inventory omits `service_mixins/` (nine files), `safety_guard.py`,
  `auth_guard.py`, `device_hierarchy.py`, `entity_cleanup.py`,
  `entity_selection.py`, `sensor_modules/energy.py`, `brand/`; it says
  service handlers live in `service_control.py` (they are in
  `service_mixins/*.py`); it lists `tests/test_improvements.py`, which does
  not exist.
- "`_recovery_lock` … see device.py:42-58", "exponential backoff 10 s → 300 s,
  max 10 recovery attempts": neither exists. Retries live in the API package
  (`min(30, 2^(n-1))`, `max_retries` 1-10) plus HA's `ConfigEntryNotReady`.
- "SSL certificate verification enabled by default (`verify_ssl=True`)":
  `DEFAULT_USE_SSL = False`, `DEFAULT_VERIFY_SSL = False`. `SECURITY.md`
  repeats the wrong default.
- "Installed via `requirements.txt`": HA installs from `manifest.json`;
  `requirements.txt` is the dev mirror (its own header says so). Same error
  in `ARCHITECTURE.md` and `docs/wiki/API-Package.md`.
- Runtime dependency list claims `aiohttp>=3.13.5`, `voluptuous>=0.16.0` in
  `requirements.txt`; the file has two lines.
- "Tests against Home Assistant 2026.5.x": the harness pins 2026.8.3 / 2026.9.
- Services section lists 11 of 44 services; "binary sensors DI1-DI8" (code
  has DI1-12); "Unique identifiers use `{api_url}_{device_id}`" describes the
  device, entity unique ids are `{entry_id}_{key}`; "Fixing API Issues → check
  retry/backoff in device.py" → API package.
- Light platform "RGB/brightness" (ONOFF only); cover "position tracking"
  (none); button "5+ buttons" (one); switch section lists DMX scenes (they
  are lights).
- Mention the coverage floor (`pyproject.toml` `fail_under = 40`) and the
  `live_*_check.py` scripts.

`ARCHITECTURE.md`: header `>=0.0.35`, footer "2.0.0 + 0.0.33 / 2026-06-16",
"Minimum HA 2026.1.0", "HA 2026.5.x compatibility", line 40 "CLAUDE.md (you
are here)", `get_readings()` returns `dict` (it returns `VioletReadings`),
"Configurable 5-300 seconds" (10-3600), `CONF_ENABLE_DIAGNOSTIC_LOGGING` and
`POOL_TEMP_SETPOINT` do not exist, release section says the workflow
"auto-updates manifest.json" (it only verifies) and describes `api-v*` tags
(the API repo uses `workflow_dispatch` + `v*`). Add the missing modules to
the service diagram.

`CONTRIBUTING.md`: "Python 3.14.2 / HA 2026.1.0", "Quality scale: Bronze,
next Silver" (manifest says platinum), file tree lists `api.py` and
`config_flow_utils.py`, install line omits `requirements-dev.txt`, commit
format `[Scope] Brief` contradicts conventional commits, references
`CONTRIBUTORS.md` (missing), venv named `venv` (CLAUDE.md `.venv`, scripts
`.venv-ha-test`, devcontainer `venv` — pick one).

`SECURITY.md`: reporting address `security@violet-pool.dev` is not a project
domain (API repo uses `git@xerolux.de`); "Version 1.0 / 2026-06-15"; calls the
integration an "add-on"; cites line numbers that moved; embeds a
"(hypothetical)" test; describes a "Command Queue" that does not exist;
"backoff 1-8 s, max 3 attempts" vs the API's actual policy; does not mention
`UNSAFE_SWITCH_KEYS`, `SafetyGuard`, `AuthReportingAPI` — the actual safety
mechanisms. Rewrite the mechanism section from the code.

### E5 — GitHub templates and metadata

- `.github/PULL_REQUEST_TEMPLATE.md`: references `scripts/lint.sh` (missing),
  "Run `black .`" (project uses ruff), "version in `const.py` and
  `manifest.json`" (five files plus changelog), `### Screenshots` merged into
  the previous line.
- `.github/CODEOWNERS` line 44 references `config_flow_utils.py` (now a
  directory).
- `.github/ISSUE_TEMPLATE/bug_report.md` is GitHub's generic web-app template
  (asks for browser/smartphone); `custom.md` is empty. Ask for HA version,
  integration version, firmware, diagnostics download, logs.
- `.github/labeler.yml` exists but no workflow uses it; delete or add the
  workflow.
- `manifest.json`: add `"loggers": ["violet_poolcontroller_api"]` so "Enable
  debug logging" in the UI captures the API package.
- `custom_components/violet_pool_controller/brand/` (8 PNGs) ships in the
  release zip; HA does not read brand images from the component directory.
  Move to `/brand/` and update `docs.yml`, `README.md`, `index.html`, or
  exclude it in `scripts/build_release.py`.
- `pyproject.toml` `[project]`: description says "+ API client" (external),
  `requires-python>=3.12` (tests need 3.14); keep it minimal.

### E6 — CI workflow hygiene

- `validate.yml` matrix names "Tests (Python 3.12)" but py312/py313 run only
  `ruff`; rename to "Lint" or drop them (ruff output does not depend on the
  interpreter).
- `tox.ini`: `ruff format --check` disabled citing a 0.15.x bug; 0.16 is
  installed. Verify and re-enable.
- Coverage: `tox` runs `--cov` without `--cov-fail-under`; the only gate is
  `pyproject.toml` `fail_under = 40` while `CLAUDE.md` says ">80 %". Add
  `--cov-fail-under=50` explicitly (current 56 %) and raise with D2.
- `release.yml` grants `contents: write` to the whole reusable validate
  workflow because `dev-release` lives in `validate.yml`; move `dev-release`
  into its own workflow triggered by `workflow_run` (the API repo already does
  this) and drop the override.
- `validate.yml` concurrency `cancel-in-progress: true` cancels an in-flight
  release validation when called from `release.yml` on a re-run of the same
  tag; make it conditional on `github.event_name != 'workflow_call'`.
- `security.yml`: quote `$GITHUB_STEP_SUMMARY`, move `security-events: write`
  to job level, add `timeout-minutes` to `security-summary`.
- `docs.yml` copies a hand-picked file list; use `cp -R docs _site/docs`.
- `.devcontainer/devcontainer.json`: image `python:3.13` but
  `scripts/setup-test-env.sh` exits unless Python ≥ 3.14; interpreter path
  `venv/` while the script creates `.venv-ha-test`; installs the black
  extension; uses removed `python.linting.*` settings; bind-mounts `.git` onto
  itself.
- `scripts/run-tests.sh`: `set -e` exits before the failure banner;
  `scripts/quick-import-test.py` imports `custom_components…const_api` (moved
  to the API package in 2.3.x) and always fails — delete or rewrite.
- API repo: `actions/setup-python@v6` while the others are v7; `tox.ini`
  runs a subset of tests; `docs.yml` wiki sync pushes `index.html`,
  `getReadings_clean.json` and `docs/de/Home.md` (page-name collision with
  `docs/Home.md` — GitHub wiki ignores directories; *needs verification* on
  the live wiki); exclude non-`.md` files and rename German pages to
  `<Page>.de.md`. `SECURITY.md` support table says only `>= 1.0` is
  supported (package is 0.0.x). `CHANGELOG.md` sections 0.0.38/0.0.36/0.0.35
  have no dates. `AGENTS.md` repository tree and test commands are stale
  (missing `_api_*.py`, `parsers.py`, `readings.py`, seven test files; says
  `pytest tests/test_api.py`). `README.md` says `get_readings()` returns a
  dict (it returns `VioletReadings`) and hardware detection uses
  `SYSTEM_dosagemodule_cpu_temperature` (it uses `SYSTEM_*_alive_count`).
  Add a `MANIFEST.in` so the sdist either ships a runnable `tests/`
  (with `conftest.py` and `mock_server.py`) or none of it.

### E7 — Wiki and site

- `docs/app.js` `routes` lacks `Testing`, `API-Reference`, `Icon-Reference`,
  `README`; 26 in-wiki links to those pages 404 on the Pages site.
  `docs/index.html` nav omits Dashboards, Icon-Reference, Testing,
  API-Reference. The site is German-only (`lang="de"`, fetches `.de.md`
  first) although `README.md` sends English readers there.
- Dead links to `docs/help/configuration-guide.{de,en}.md` and
  `ICON_UPGRADE_SUMMARY.md` in `Changelog.md`, `Configuration.md`, `Home.md`,
  `Installation-and-Setup.md` (and `.de` twins).
- `Erweiterte-Protokollierung.md` documents a `log_export` service (real name
  `export_diagnostic_logs`).
- `Services.md` says "30+ services", documents 25, and is missing 15
  registered services (`configure_overflow, configure_refill,
  control_pump_http, control_refill_http, get_backwash_status,
  get_calibration_status, get_live_trace_snapshot, get_overflow_status,
  get_refill_status, get_system_services_status, get_system_update_status,
  reset_blocking, set_can_amount, set_omni_position, set_system_service`).
- Version strings frozen at 2.3.0-beta.1 / HA 2026.1 / API 0.0.33 in
  `_Sidebar*.md`, `_Footer*.md`, `Home*.md`, `Installation-and-Setup.md`,
  `Contributing.md`, `README.md`, `Diagnostics.md`, `docs/index.html`,
  `index.html`. Add a test that greps these for the `.version` string.
- "add-on" wording in ~10 pages (HA add-ons are supervisor containers; this
  is an integration).
- `Entities.md`, `Switches.md`, `Climate.md`: entity ids (`switch.violet_pump`,
  `climate.violet_heater`, `number.violet_target_ph`), ranges, attribute names
  (`violet_state`, `last_changed`) and the "Set all switches to automatic via
  `switch.turn_off`" advice (it sends Manual OFF, state 6) do not match the
  code. `Entities.md` says dosing selects offer "Off / Manual / Auto" and lists
  DMX lights under `led_lighting`.
- `Configuration.md` feature table (`DOSING_PH_MINUS`, `DMX 1-8`, `REL1-REL8`)
  does not match `AVAILABLE_FEATURES`; `adaptive_polling`, `group_entities`,
  `invert_cover`, `allow_unsafe_switches` are undocumented.
- `docs/wiki/Changelog.md` is a hand-written second changelog that stops at
  2.3.x; replace with a link to the root `CHANGELOG.md`.
- `docs/wiki/README.md` uses `.md` suffixes and German anchor slugs.
- `docs/HA_QUALITY_SCALE_PROGRESS.md` claims "80 %+ coverage", "10 services",
  "10 workflows", "certified against OWASP Top 10"; reduce to a link to
  `quality_scale.yaml`.
- `README.md` line ~100 says the API is developed "in this repo" while line
  ~131 says it lives in its own repository; feature table says "3-speed pump"
  (4 levels, 0-3) and "8 controllable scenes" (12). Same in `README.de.md`.
- `blueprints/automation/*.yaml` reference `blueprints/README.md`, which is
  gitignored (`.gitignore`: `/blueprints/README.md`) and therefore missing on
  GitHub; un-ignore it or drop the reference. They also declare `min_version: "2024.6.0"` while the integration needs 2026.8;
  `Dashboard/*.yaml` use German-era entity ids (`_ruckspulung`, `_heizung`)
  that a fresh install does not produce.

---

## Findings that were checked and rejected

To save the implementer time, these claims from the audit were **not**
confirmed and must not be acted on:

- "SafetyGuard `arm_auto_stop`/`set_lock` are never called in production" —
  false; `service_mixins/{pump,cover,dosing}.py` call them (which is why A1
  matters).
- "`hass.data[DOMAIN]` is still used for per-entry state" — false; only the
  service manager lives there, as `runtime_data.py` documents.
- `ruff`, `mypy` and the test suites are clean in both repositories; do not
  spend time "fixing lint" that is not there.

## Suggested PR sequence

1. A1 + C5 (guard correctness) → 2. A2 → 3. A3 → 4. A4 → 5. API-A5 + API-A6 +
API-B27 + API-B28 (release 0.0.39, bump pin) → 6. B1 → 7. B2 → 8. D1 then B3
→ 9. B4 → 10. B5 + C4 → 11. B6-B12 (one PR per platform) → 12. B13 →
13. B14-B26 → 14. C1-C3, C6, C7 → 15. D2-D4 → 16. E1-E7.
