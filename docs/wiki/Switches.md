> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Switches.de)**

---

# Switches & Control – Switch Entities

> Complete documentation of all switch entities for the Violet Pool Controller.

---

## Overview

All switches on the Violet Pool Controller are **3-state switches**: they support not only `On` and `Off`, but also `Automatic`. The actual operating state is stored as **State 0–6**.

| State | Meaning | Switch Display |
|-------|---------|----------------|
| `0` – AUTO_OFF | Automatic, currently off | `off` |
| `1` – MANUAL_ON | Manually turned on | `on` |
| `2` – AUTO_ON | Automatic, currently on | `on` |
| `3` – AUTO_TIMER | Automatic with timer, on | `on` |
| `4` – FORCED_ON | Forced on | `on` |
| `5` – AUTO_WAITING | Automatic, waiting for condition | `off` |
| `6` – MANUAL_OFF | Manually turned off | `off` |

> Detailed state explanation: [Device States](Device-States)

---

## All Switch Entities

### Pump

| Entity | Description |
|--------|-------------|
| `switch.violet_pump` | Main filter pump (3 speed levels) |

**Note:** The pump supports 4 speed levels (0–3). For speed control, use the [`control_pump` service](Services#-service-control_pump).

```yaml
# Simple on/off
service: switch.turn_on
target:
  entity_id: switch.violet_pump

# Speed with service
service: violet_pool_controller.control_pump
data:
  action: speed_control
  speed: 2
  duration: 3600
```

---

### Heater

| Entity | Description |
|--------|-------------|
| `switch.violet_heater` | Pool heater |

> For thermostat control with target temperature: [Climate Entities](Climate)

```yaml
service: switch.turn_on
target:
  entity_id: switch.violet_heater
```

---

### Solar

| Entity | Description |
|--------|-------------|
| `switch.violet_solar` | Solar collector |

```yaml
# Only turn on when solar temperature > pool water
automation:
  trigger:
    platform: template
    value_template: >
      {{ states('sensor.violet_solar_temperature') | float(0) >
         states('sensor.violet_water_temperature') | float(0) + 3 }}
  action:
    service: switch.turn_on
    target:
      entity_id: switch.violet_solar
```

---

### Dosing Pumps

| Entity | Description |
|--------|-------------|
| `switch.violet_ph_minus` | pH reducer dosing pump |
| `switch.violet_ph_plus` | pH increaser dosing pump |
| `switch.violet_chlorine` | Chlorine dosing pump |
| `switch.violet_flocculant` | Flocculant dosing pump |

> **Safety note:** Controlling dosing pumps directly via switch is possible, but for precise dosing use the [`smart_dosing` service](Services#-service-smart_dosing).

```yaml
# Recommended: Service with time control
service: violet_pool_controller.smart_dosing
data:
  dosing_type: "pH-"
  action: manual_dose
  duration: 30
```

---

### DMX Lighting

| Entity | Description |
|--------|-------------|
| `switch.violet_dmx_scene_1` | DMX Scene 1 |
| `switch.violet_dmx_scene_2` | DMX Scene 2 |
| `switch.violet_dmx_scene_3` | DMX Scene 3 |
| `switch.violet_dmx_scene_4` | DMX Scene 4 |
| `switch.violet_dmx_scene_5` | DMX Scene 5 |
| `switch.violet_dmx_scene_6` | DMX Scene 6 |
| `switch.violet_dmx_scene_7` | DMX Scene 7 |
| `switch.violet_dmx_scene_8` | DMX Scene 8 |

```yaml
# Turn on lighting at sunset
automation:
  - alias: "Pool Lighting Sunset"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_dmx_scene_1
```

---

### Extension Relays

| Entity | Description |
|--------|-------------|
| `switch.violet_relay_1` to `switch.violet_relay_8` | Freely configurable relays |

Extension relays can be used for various devices:
- Waterfall pump
- Counter-current system
- Air blower
- Lighting (non-DMX)

```yaml
# Waterfall only when pump is running
automation:
  - alias: "Waterfall with Pump"
    trigger:
      - platform: state
        entity_id: switch.violet_pump
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_relay_1
```

---

## Switch Control via UI

### 3-State Toggle

In the Home Assistant UI, each switch shows:
- **Green (ON)**: Device active (states 1, 2, 3, 4)
- **Gray (OFF)**: Device inactive (states 0, 5, 6)

Clicking toggles between manual-ON and Automatic mode.

### View State Details

Click on the entity → **Attributes** to view:
- `raw_state`: The numeric state 0–6
- `mode`: Current operating mode
- `last_changed`: Last state change

---

## Automation: Useful Patterns

### Daily Pump Schedule

```yaml
automation:
  - alias: "Pump Daily Program"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 2

  - alias: "Pump Night Reduction"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 1
```

### Evaluate Switch State in Template Sensor

```yaml
template:
  - sensor:
      - name: "Pump Mode"
        state: >
          {% set state = states('switch.violet_pump') %}
          {% set raw = state_attr('switch.violet_pump', 'raw_state') | int(-1) %}
          {% if raw == 0 %} Auto off
          {% elif raw == 1 %} Manual on
          {% elif raw == 2 %} Auto on
          {% elif raw == 3 %} Timer active
          {% elif raw == 4 %} Forced on
          {% elif raw == 5 %} Waiting
          {% elif raw == 6 %} Manual off
          {% else %} Unknown
          {% endif %}
```

### Set All Switches to Automatic

```yaml
script:
  all_automatic:
    alias: "Set All Switches to Automatic"
    sequence:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.violet_pump
            - switch.violet_heater
            - switch.violet_solar
            - switch.violet_ph_minus
            - switch.violet_chlorine
```

---

## Composite States (Pipe Separator)

Some switches show composite states:

```
"3|PUMP_ANTI_FREEZE"
"2|SOLAR_DIFF_ACTIVE"
"4|MANUAL_OVERRIDE"
```

The first segment (before `|`) is the numeric state (0–6).
The second segment indicates an operational mode.

**Check in automations:**

```yaml
condition:
  - condition: template
    value_template: >
      {{ 'PUMP_ANTI_FREEZE' in state_attr('switch.violet_pump', 'raw_state') | string }}
```

---

## Troubleshooting

### Switch always shows `unavailable`

1. Is the controller reachable? → [Troubleshooting](Troubleshooting)
2. Feature enabled in setup?
3. Reload integration: Settings → Devices & Services → Violet → Reload

### Switch doesn't respond to control

1. Check if controller is in manual override mode
2. Check logs: Settings → System → Logs
3. Rate limiting active? Wait briefly and try again

### Pump won't turn on

Possible causes:
- Frost protection active (`PUMP_ANTI_FREEZE` in state)
- Safety lockout active (check error code)
- Pressure switch error (Error Code 20/21)

→ See [Error Codes](Error-Codes) for details

---

*Back: [Home](Home) | Next: [Climate & Heating](Climate)*