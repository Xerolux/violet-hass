> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Device-States.de)**

---

# Device States (0–6)

> The **most important concept** of the integration! Each controllable output (pump, heater, solar, light, dosing channels, extension relays, DMX scenes, …) reports one of 7 numeric state codes via `/getReadings`. Learn what they mean and how to use them in automations.

> Source of truth: `OutputState` enum in `violet_poolcontroller_api/const_devices.py` (manual section 26.1).

---

## The 7 Output State Codes

| Code | Enum constant        | ON/OFF | Mode     | Description |
|------|-----------------------|--------|----------|-------------|
| **0** | `AUTO_OFF`           | OFF    | Auto     | Auto mode active, device standby (conditions not met) |
| **1** | `AUTO_ON`            | ON     | Auto     | Auto mode active, device running (scheduled / conditions met) |
| **2** | `AUTO_PRIO_OFF`      | OFF    | Auto     | Auto mode, but blocked by a control rule (priority OFF) |
| **3** | `AUTO_PRIO_ON`       | ON     | Auto     | Auto mode, forced ON by an emergency rule (priority ON) |
| **4** | `MANUAL_ON`          | ON     | Manual   | User has manually switched the output ON (forced) |
| **5** | `EMERGENCY_OFF`      | OFF    | Auto     | Switched OFF by an emergency control rule |
| **6** | `MANUAL_OFF`         | OFF    | Manual   | User has manually switched the output OFF |

> ⚠️ **Older wiki versions had these states wrong** (e.g. state 1 listed as `MANUAL_ON`). The mapping above is the only correct one and is enforced by the `OutputState` enum used throughout the codebase.

---

## Boolean Simplification

```
┌──────────────────────────────────────────┐
│           DEVICE RUNNING (ON)            │
│   State 1  – AUTO_ON                     │
│   State 3  – AUTO_PRIO_ON (emergency)    │
│   State 4  – MANUAL_ON (forced)          │
├──────────────────────────────────────────┤
│          DEVICE NOT RUNNING (OFF)        │
│   State 0  – AUTO_OFF (standby)          │
│   State 2  – AUTO_PRIO_OFF (rule block)  │
│   State 5  – EMERGENCY_OFF (emergency)   │
│   State 6  – MANUAL_OFF                  │
└──────────────────────────────────────────┘
```

This is the value `OutputState.is_on` returns and what `switch`/`binary_sensor` entities expose as their primary `on`/`off` state.

---

## Mode Classification

| Mode   | States  | Meaning |
|--------|---------|---------|
| **Auto**     | 0, 1, 2, 3, 5 | Controller decides based on rules/schedules |
| **Manual**   | 4, 6          | User override – automatic rules are suspended |
| **Emergency**| 3, 5          | An emergency control rule is currently active |

Use the helper properties `is_on`, `is_manual`, `is_emergency` (or the `VioletState` class) instead of comparing raw integers.

---

## PVSURPLUS Exception

The `PVSURPLUS` output uses its own 0–2 scheme (manual section 26.3), not 0–6:

| Code | Enum constant    | ON/OFF | Meaning |
|------|------------------|--------|---------|
| **0** | `OFF`           | OFF    | PV surplus mode inactive |
| **1** | `ON_BY_INPUT`   | ON     | Activated by digital input |
| **2** | `ON_BY_HTTP`    | ON     | Activated by HTTP request |

---

## DMX Scenes

DMX scenes only use a subset of the 0–6 codes (enum `DmxSceneState`):

| Code | Meaning |
|------|---------|
| 0 | `AUTO_OFF` – scene not active |
| 1 | `AUTO_ON` – scene active via schedule |
| 4 | `MANUAL_ON` – scene forced on |
| 6 | `MANUAL_OFF` – scene manually off |

---

## Digital Input Rules (DIRULE_1..8)

State codes for `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_n` (enum `RuleState`):

| Code | Constant                | Meaning |
|------|--------------------------|---------|
| 0    | `INACTIVE`              | Rule inactive |
| 1    | `ACTIVE`                | Rule currently active |
| 5    | `BLOCKED_BY_RULE`       | Blocked by another rule |
| 6    | `BLOCKED_MANUALLY`      | Manually blocked |

---

## Composite / Pipe-Separated States

Some readings (e.g. `PUMPSTATE`, `HEATERSTATE`, `SOLARSTATE`) return composite values with a `|` separator. The numeric prefix is the state code from the table above; the suffix carries additional context.

| Example                          | Numeric state | Context |
|----------------------------------|---------------|---------|
| `"3\|PUMP_ANTI_FREEZE"`          | 3 (AUTO_PRIO_ON) | Frost protection active |
| `"2\|BLOCKED_BY_OUTSIDE_TEMP"`   | 2 (AUTO_PRIO_OFF) | Blocked by outside temperature rule |
| `"5\|BLOCKED_BY_PUMP_OFF"`       | 5 (EMERGENCY_OFF) | Dosing paused, pump is off |

The integration extracts the numeric prefix automatically; the suffix is preserved in the entity attribute and surfaces in the composite-state sensor (`PUMPSTATE`, `HEATERSTATE`, `SOLARSTATE`).

### Full list of detail codes

The integration understands these block/wait reason codes (defined in `DOSING_STATE_DESCRIPTIONS`):

- **Frost**: `PUMP_ANTI_FREEZE`
- **Thresholds**: `BLOCKED_BY_TRESHOLDS`, `BLOCKED_BY_THRESHOLDS`, `BLOCKED_BY_CL_TRESHOLDS`, `BLOCKED_BY_CL_THRESHOLDS`, `THRESHOLDS_REACHED`, `THRESHOLDS_REACHED_CL`
- **Pump dependency**: `BLOCKED_BY_PUMP`, `BLOCKED_BY_PUMP_OFF`, `BLOCKED_BY_PUMP_DELAY`, `BLOCKED_BY_START_DELAY`, `BLOCKED_BY_POSTRUN`, `BLOCKED_BY_HEATER_OFF_DELAY`
- **Flow / circulation**: `BLOCKED_BY_FLOW`, `BLOCKED_BY_MISSING_FLOW`, `BLOCKED_BY_MISSING_CIRCULATION`, `WAITING_FOR_PUMP`, `WAITING_FOR_FLOW`
- **Other subsystems**: `BLOCKED_BY_SOLAR`, `BLOCKED_BY_HEATER`, `BLOCKED_BY_BACKWASH`, `BLOCKED_BY_OUTSIDE_TEMP`, `BLOCKED_BY_MAXTEMP`, `BLOCKED_BY_BOILER_TEMP`, `BLOCKED_BY_MAX_AMOUNT`
- **Hardware**: `BLOCKED_BY_MISSING_MODULE`, `BLOCKED_BY_SENSOR_FAULT`
- **Rules / overrides**: `BLOCKED_BY_EMERGENCY_CONTROL_RULE`, `BLOCKED_BY_ESC`, `BLOCKED_BY_MANUAL_OFF`, `BLOCKED_BY_UPDATE`, `BLOCKED_BY_RULE`
- **OmniTronic multi-port valve**: `BLOCKED_BY_OMNI`, `BLOCKED_BY_OMIN` (firmware typo), `BLOCKED_BY_OMNI_POS`, `BLOCKED_BY_Z1Z2`
- **Electrolysis**: `BLOCKED_BY_POLEREVERSAL` (firmware typo)
- **Waiting states**: `WAITING_FOR_DOSAGECONTROLLERS`, `WAITING_FOR_HEATER_POSTRUN`, `WAITING_FOR_PREFILL`, `WAITING_FOR_STARTTIME`
- **Active dosing**: `DOSING`, `DOSING_PAUSED`, `MANUAL_DOSING`

---

## Using States in Home Assistant

### Read the raw state

```yaml
{{ states('switch.violet_pool_controller_pump') }}                       # "on" / "off"
{{ state_attr('switch.violet_pool_controller_pump', 'violet_state') }}   # "2" or "3|PUMP_ANTI_FREEZE"
```

### Check state groups

```yaml
# Device ON (states 1, 3, 4)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pool_controller_pump', 'violet_state')
         | regex_replace('\|.*', '') | int(default=-1) in [1, 3, 4] }}

# Device in MANUAL mode (states 4, 6)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pool_controller_pump', 'violet_state')
         | regex_replace('\|.*', '') | int(default=-1) in [4, 6] }}

# Device under EMERGENCY rule (states 3, 5)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pool_controller_pump', 'violet_state')
         | regex_replace('\|.*', '') | int(default=-1) in [3, 5] }}
```

### Notify on manual override

```yaml
automation:
  - alias: "Pump in manual mode"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('switch.violet_pool_controller_pump', 'violet_state')
             | regex_replace('\|.*', '') | int(default=-1) in [4, 6] }}
        for: "00:05:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Pool"
          message: "Pump was switched to MANUAL mode"
```

### Detect frost protection

```yaml
automation:
  - alias: "Pump frost protection active"
    trigger:
      - platform: template
        value_template: >
          {{ 'PUMP_ANTI_FREEZE' in
             (state_attr('switch.violet_pool_controller_pump', 'violet_state') | string) }}
    action:
      - service: notify.mobile_app
        data:
          message: "Frost protection activated – pump runs automatically"
```

---

## Visualization in Home Assistant

| State | Icon color | State translations key |
|-------|-----------|------------------------|
| 0 (AUTO_OFF)         | Blue    | `auto_inactive` |
| 1 (AUTO_ON)          | Green   | `auto_active` |
| 2 (AUTO_PRIO_OFF)    | Blue    | `auto_inactive` |
| 3 (AUTO_PRIO_ON)     | Cyan    | `frost_protection` (when `PUMP_ANTI_FREEZE`) / `auto_active` |
| 4 (MANUAL_ON)        | Orange  | `manual_on` |
| 5 (EMERGENCY_OFF)    | Purple  | `error` |
| 6 (MANUAL_OFF)       | Red     | `manual_off` |

Source: `STATE_ICONS`, `STATE_COLORS`, `STATE_TRANSLATIONS` in `const_devices.py`.

---

## Typical State Sequences

### Daily pump schedule

```
06:00  [0] AUTO_OFF       – Schedule not yet active
08:00  [1] AUTO_ON        – Timer starts pump
12:00  [0] AUTO_OFF       – Timer ends, standby
16:00  [1] AUTO_ON        – Temperature condition met
18:00  [0] AUTO_OFF       – Setpoint reached
```

### Manual intervention

```
[1] AUTO_ON       – Running by schedule
[4] MANUAL_ON     – User forces ON
[6] MANUAL_OFF    – User switches OFF
[1] AUTO_ON       – Returned to AUTO via select entity
```

### Chlorine dosing with safety interval

```
[0] AUTO_OFF       – Ready
[1] AUTO_ON        – Chlorine low → dosing
[5] EMERGENCY_OFF  – Safety interval / blocked by pump off
[2] AUTO_PRIO_OFF  – Blocked by max daily amount
[0] AUTO_OFF       – Ready again
```

---

## Troubleshooting State Issues

### State stuck at `6` (MANUAL_OFF)

**Cause:** Output was manually switched off; auto rules are bypassed.
**Fix:** Set the matching `select.*_mode` entity back to `Auto`, or call the corresponding switch service.

### State alternates between 0 and 1 rapidly

**Cause:** A rule condition oscillates around its threshold.
**Fix:** Increase the rule's hysteresis on the controller, or increase the polling interval.

### State stays at `5` (EMERGENCY_OFF) for a long time

**Cause:** Open error condition or unmet dependency (e.g. pump off, flow missing, max daily amount reached).
**Fix:** Check `sensor.violet_pool_controller_*_state` and the [Error Codes](Error-Codes) page.

### State stays at `2` (AUTO_PRIO_OFF)

**Cause:** A higher-priority control rule is blocking the output (e.g. outside temperature, pump off).
**Fix:** Inspect the `*STATE` composite sensor for the `BLOCKED_BY_*` suffix.

---

**Next:** [Sensors](Sensors) | [Switches](Switches) | [Services](Services)
