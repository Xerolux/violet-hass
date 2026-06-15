> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Switches.de)**

---

# Switches & Control – Switch Entities

> Complete documentation of all switch entities for the Violet Pool Controller.

---

## Overview

All switches on the Violet Pool Controller are **3-state switches**: they support not only `On` and `Off`, but also `Automatic`. The actual operating state is stored as **State 0–6** (see [Device States](Device-States) for the full reference).

| State | Constant        | Switch Display | Description |
|-------|-----------------|----------------|-------------|
| `0`   | `AUTO_OFF`      | `off`          | Auto mode, standby |
| `1`   | `AUTO_ON`       | `on`           | Auto mode, scheduled / running |
| `2`   | `AUTO_PRIO_OFF` | `off`          | Auto mode, blocked by control rule |
| `3`   | `AUTO_PRIO_ON`  | `on`           | Auto mode, forced ON by emergency rule |
| `4`   | `MANUAL_ON`     | `on`           | Manual ON (forced) |
| `5`   | `EMERGENCY_OFF` | `off`          | Switched OFF by emergency rule |
| `6`   | `MANUAL_OFF`    | `off`          | Manual OFF |

> ⚠️ **Older wiki versions had these states wrong**. The mapping above is the only correct one and is enforced by the `OutputState` enum in `violet_poolcontroller_api/const_devices.py`.

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
| `switch.violet_pool_controller_dos_4_phm` | pH- reducer dosing pump |
| `switch.violet_pool_controller_dos_5_php` | pH+ increaser dosing pump |
| `switch.violet_pool_controller_dos_1_cl` | Chlorine dosing pump |
| `switch.violet_pool_controller_dos_2_elo` | Electrolysis dosing |
| `switch.violet_pool_controller_dos_6_floc` | Flocculant dosing pump |

> **Safety note:** Controlling dosing pumps directly via switch is possible, but for precise dosing use the [`smart_dosing` service](Services#-service-smart_dosing) or the [`manual_dosing_http` service](Services#-service-manual_dosing_http). Dosing outputs use `POST /triggerManualDosing`, not `/setFunctionManually`.

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

DMX scenes 1–12 are exposed as **light entities** (not switches):

| Entity | Description |
|--------|-------------|
| `light.violet_pool_controller_dmx_scene1` … `light.violet_pool_controller_dmx_scene12` | DMX Scene 1–12 |

Use the standard light domain to control them:

```yaml
# Turn on lighting at sunset
automation:
  - alias: "Pool Lighting Sunset"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.violet_pool_controller_dmx_scene1
```

For coordinated scene control use the [`control_dmx_scenes` service](Services#-service-control_dmx_scenes) (all_on / all_off / all_auto / sequence / party_mode).

### Other Core Switches

| Entity | Description |
|--------|-------------|
| `switch.violet_pool_controller_pvsurplus` | PV surplus output (uses 0–2 scheme, see [Device States](Device-States#pvsurplus-exception)) |
| `switch.violet_pool_controller_backwash` | Backwash cycle |
| `switch.violet_pool_controller_backwashrinse` | Rinse cycle |
| `switch.violet_pool_controller_refill` | Water refill |
| `switch.violet_pool_controller_eco` | ECO mode |

---

### Extension Relays

| Entity | Description |
|--------|-------------|
| `switch.violet_pool_controller_ext1_1` to `switch.violet_pool_controller_ext1_8` | Extension module 1, relays 1–8 |
| `switch.violet_pool_controller_ext2_1` to `switch.violet_pool_controller_ext2_8` | Extension module 2, relays 1–8 |

> **Feature:** requires "Extension Outputs" to be enabled.

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
        entity_id: switch.violet_pool_controller_pump
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_pool_controller_ext1_1
```

### OMNI DC Outputs (6)

| Entity | Description |
|--------|-------------|
| `switch.violet_pool_controller_omni_dc0` … `switch.violet_pool_controller_omni_dc5` | OMNI DC motor outputs 0–5 |

OMNI DC outputs are typically used for OmniTronic multi-port valve positions or DC motor control.

### Digital Input Rule Switches (8)

| Entity | Description |
|--------|-------------|
| `switch.violet_pool_controller_dirule_1` … `switch.violet_pool_controller_dirule_8` | Switching rules 1–8 |

> **Feature:** requires "Digital Inputs" to be enabled. Use [`manage_digital_rules`](Services#-service-manage_digital_rules) or the dedicated rule services ([`configure_switching_rule`](Services#-service-configure_switching_rule), [`enable_rule`](Services#-service-enable_rule)) for full control.

---

## Switch Control via UI

### 3-State Toggle

In the Home Assistant UI, each switch shows:
- **Green (ON)**: Device active — states `1`, `3`, `4`
- **Gray (OFF)**: Device inactive — states `0`, `2`, `5`, `6`

For full Off/On/Auto control use the matching `select.*_mode` entity (e.g. `select.violet_pool_controller_pump_mode`).

### View State Details

Click on the entity → **Attributes** to view:
- `violet_state`: The raw state `0`–`6` (or composite like `"3|PUMP_ANTI_FREEZE"`)
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