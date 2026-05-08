# Device States (0–6)

> The **most important concept** of the integration! Learn what the 7 device states mean and how to use them in automations.

---

## The 7 Device States

The Violet Controller distinguishes 7 operating states for each controllable device:

| State | Constant | Status | Type | Description |
|-------|----------|--------|------|-------------|
| **0** | `AUTO_OFF` | OFF | Automatic | Automatic active – device not running (conditions not met) |
| **1** | `MANUAL_ON` | ON | Manual | User has manually turned on |
| **2** | `AUTO_ON` | ON | Automatic | Automatic active – device running (conditions met) |
| **3** | `AUTO_TIMER` | ON | Automatic | Automatic with timer control – device currently running |
| **4** | `MANUAL_FORCED` | ON | Manual | Manually forced – ignores all automatic rules |
| **5** | `AUTO_WAITING` | OFF | Automatic | Automatic active – waiting for conditions (e.g. safety interval) |
| **6** | `MANUAL_OFF` | OFF | Manual | User has manually turned off |

---

## State Groups

### Device Status (ON/OFF)

```
┌──────────────────────────────────────────┐
│             DEVICE RUNNING (ON)          │
│  State 1 (MANUAL_ON)                     │
│  State 2 (AUTO_ON)                       │
│  State 3 (AUTO_TIMER)                    │
│  State 4 (MANUAL_FORCED)                 │
├──────────────────────────────────────────┤
│          DEVICE NOT RUNNING (OFF)        │
│  State 0 (AUTO_OFF)                      │
│  State 5 (AUTO_WAITING)                  │
│  State 6 (MANUAL_OFF)                    │
└──────────────────────────────────────────┘
```

### Control Type (Automatic vs. Manual)

```
┌──────────────────────────────────────────┐
│          AUTOMATIC MODE                  │
│  State 0 – Ready, waiting               │
│  State 2 – Running by program           │
│  State 3 – Running by schedule          │
│  State 5 – Waiting for conditions       │
├──────────────────────────────────────────┤
│          MANUAL MODE                     │
│  State 1 – Manual on                    │
│  State 4 – Forced on                    │
│  State 6 – Manual off                   │
└──────────────────────────────────────────┘
```

---

## Visualization in Home Assistant

| State | Icon Color | Meaning |
|-------|-----------|---------|
| 0 (AUTO_OFF) | Blue | Ready in automatic mode |
| 1 (MANUAL_ON) | Orange | Manually turned on |
| 2 (AUTO_ON) | Green | Running automatically |
| 3 (AUTO_TIMER) | Green | Running by schedule |
| 4 (MANUAL_FORCED) | Orange | Forced on |
| 5 (AUTO_WAITING) | Blue | Automatic waiting |
| 6 (MANUAL_OFF) | Red | Manually turned off |

---

## Detailed Explanation of Each State

### State 0 – AUTO_OFF (Automatic, Ready)

The controller is in **automatic mode**, but the device is currently **not active** – because the conditions (temperature, time, etc.) are not yet met.

```
Example pump: Daily program running, but scheduled time not yet reached.
→ Device starts automatically when condition is met.
```

**In HA**: Switch shows `off`, attribute `violet_state = "0"`

---

### State 1 – MANUAL_ON (Manual On)

The user has **manually turned on** the device. Automatic rules are overridden.

```
Example: User manually turns on pump for pool cleaning.
→ Runs until manually turned off or set back to AUTO.
```

**In HA**: Switch shows `on`, attribute `violet_state = "1"`

---

### State 2 – AUTO_ON (Automatic, On)

The controller is in automatic mode and the device is **active** – because all conditions are met.

```
Example heater: Pool temperature < setpoint → heater runs automatically.
→ Stops automatically when setpoint is reached.
```

**In HA**: Switch shows `on`, attribute `violet_state = "2"`

---

### State 3 – AUTO_TIMER (Automatic, Timer)

Device is running automatically due to a **timer control** in the controller.

```
Example: Pump runs daily 08:00–12:00 via timer program.
→ Stops automatically at schedule end.
```

**In HA**: Switch shows `on`, attribute `violet_state = "3"`

---

### State 4 – MANUAL_FORCED (Manual, Forced)

The device has been **forced on** and ignores all safety and automatic restrictions.

```
Example: Heater is forced on despite temperature limits.
→ Only for maintenance/testing! Use with caution!
```

**In HA**: Switch shows `on`, attribute `violet_state = "4"`

> **Warning**: State 4 can bypass safety checks. Only use for authorized maintenance work!

---

### State 5 – AUTO_WAITING (Automatic, Waiting)

The controller wants to turn on the device, but is **waiting** for a condition:
- Safety interval (e.g. 5 minutes after dosing)
- Error needs to be resolved
- Other dependency not met

```
Example dosing: Chlorine was dosed, controller waits
for safety interval before restarting.
```

**In HA**: Switch shows `off`, attribute `violet_state = "5"`

---

### State 6 – MANUAL_OFF (Manual, Off)

The user has **manually turned off** the device. Automatic rules are overridden.

```
Example: Pool is turned off for winter shutdown.
→ Device does not start automatically until set back to AUTO.
```

**In HA**: Switch shows `off`, attribute `violet_state = "6"`

---

## Composite States (States with Additional Info)

Some states contain a **pipe separator (`|`)** with additional context:

```
Format: {STATE_NUMBER}|{DESCRIPTION}

Examples:
  "3|PUMP_ANTI_FREEZE"        → State 3, frost protection active
  "2|BLOCKED_BY_TEMP"         → State 2, but blocked by temperature
  "5|SAFETY_INTERVAL"         → State 5, safety interval running
  "1|HIGH_PRESSURE_WARNING"   → State 1, high pressure warning
```

**Important**: The **number before the `|`** determines the state! The text after is only context information.

In Home Assistant, the full string is stored as the entity state:
```yaml
# Example entity attribute
violet_state: "3|PUMP_ANTI_FREEZE"
# The binary status (on/off) is based on the number: 3 → ON
```

---

## Using States in Home Assistant

### Read State Value

```yaml
# Template: Read current state
{{ states('switch.violet_pump') }}        # → "on" or "off"
{{ state_attr('switch.violet_pump', 'violet_state') }}  # → "2" or "3|PUMP_ANTI_FREEZE"
```

### React to State Changes

```yaml
automation:
  - alias: "Notification on manual pump control"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('switch.violet_pump', 'violet_state') in ['1', '4', '6'] }}
    action:
      - service: notify.mobile_app_my_phone
        data:
          title: "Pool"
          message: "Pump is in manual mode!"
```

### Check State Groups in Condition

```yaml
# Check if device is ON (States 1,2,3,4)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pump', 'violet_state') | int(default=0) in [1, 2, 3, 4] }}

# Check if device is in automatic mode (States 0,2,3,5)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pump', 'violet_state') | int(default=0) in [0, 2, 3, 5] }}

# Check if device is manually controlled (States 1,4,6)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pump', 'violet_state') | int(default=0) in [1, 4, 6] }}
```

---

## Typical State Sequences

### Normal Daily Operation (Pump)

```
06:00  [0] AUTO_OFF    – Automatic running, pump waiting
08:00  [3] AUTO_TIMER  – Timer starts, pump running
12:00  [0] AUTO_OFF    – Timer end, pump stops
16:00  [2] AUTO_ON     – Temperature condition met, pump running
18:00  [0] AUTO_OFF    – Temperature reached, pump stops
```

### Manual Intervention

```
[2] AUTO_ON     – Pump running automatically
[1] MANUAL_ON   – User manually turns on (test/cleaning)
[0] AUTO_OFF    – User returns control (click "AUTO")
[2] AUTO_ON     – Automatic takes over again
```

### Dosing Sequence

```
[0] AUTO_OFF    – Dosing ready
[2] AUTO_ON     – Chlorine level low → dosing starts
[5] AUTO_WAITING– Dosing complete, safety interval running (5 min)
[0] AUTO_OFF    – Safety interval passed, ready for next dose
```

### Error Case (Heater)

```
[2] AUTO_ON     – Heater running
[5] AUTO_WAITING– Error detected, heater paused
[0] AUTO_OFF    – Error resolved, waiting for next condition
[2] AUTO_ON     – Normal state restored
```

---

## State Debugging

### Via Developer Tools

1. **Developer Tools → States**
2. Search for `switch.violet_pump`
3. Check state and attributes

### Template Console

```
Developer Tools → Template
```

```yaml
# All state info at once
Pump State: {{ states('switch.violet_pump') }}
Violet State: {{ state_attr('switch.violet_pump', 'violet_state') }}
Mode: {{ 'MANUAL' if state_attr('switch.violet_pump', 'violet_state') | int(0) in [1,4,6] else 'AUTOMATIC' }}
Running: {{ 'YES' if state_attr('switch.violet_pump', 'violet_state') | int(0) in [1,2,3,4] else 'NO' }}
```

### Check Logs

```bash
tail -f /config/home-assistant.log | grep violet_pool_controller
```

---

## Common State Issues

### Problem: State stays permanently at "6" (MANUAL_OFF)

**Cause:** Device was manually turned off and left in "Manual" mode.

**Solution:** Click "AUTO" in HA, or:
```yaml
service: switch.turn_on
target:
  entity_id: switch.violet_pump
# Switches back to automatic
```

---

### Problem: State constantly alternates between 0 and 2

**Cause:** Automatic conditions oscillate at the threshold (e.g. temperature ±0.1°C).

**Solution:**
- Increase hysteresis in the controller
- Increase polling interval (to reduce measurement noise)

---

### Problem: State 5 (WAITING) takes very long

**Cause:**
- Safety interval after dosing (5–10 minutes is normal)
- Error code on controller

**Solution:**
- Check error codes: `sensor.violet_system_error_codes`
- Wait (safety interval is intentional)
- If >30 minutes: Restart controller

---

**Next:** [Sensors](Sensors) | [Switches](Switches) | [Services](Services)