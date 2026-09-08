> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Switches.de)**

---

# Switches & Control – Switch Entities

> Complete documentation of all switch entities for the Violet Pool Controller.

> **Entity ids in this wiki are examples.** An entity id is derived from the
> name you gave the controller in the config flow, so a controller called
> "Pool" produces `switch.pool_pump`, not `switch.violet_pool_controller_pump`.
> Home Assistant also never rewrites an id after first registration, so an
> older installation may still carry a differently-spelled id. **Look yours up
> in Developer Tools → States** and search for your controller's name before
> copying an automation.
>
> Ranges and option labels shown here are likewise the current defaults, not a
> contract. The authoritative values live in the code
> (`climate.py`'s `temperature_range()`, `const_sensors.py`, `select.py`) and
> in the entity's own attributes in Developer Tools.

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

> ⚠️ **Older wiki versions had these states wrong**. The mapping above is the only correct one and is enforced by the `OutputState` enum in the `violet_poolcontroller_api` package (`const_devices.py`).

---

## All Switch Entities

### Pump

| Entity | Description |
|--------|-------------|
| `switch.violet_pool_controller_pump` | Main filter pump (3 speed levels) |

**Note:** The pump supports 4 speed levels (0–3). For speed control, use the [`control_pump` service](Services#-service-control_pump).

```yaml
# Simple on/off
service: switch.turn_on
target:
  entity_id: switch.violet_pool_controller_pump

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
| `switch.violet_pool_controller_heater` | Pool heater |

> For thermostat control with target temperature: [Climate Entities](Climate)

```yaml
service: switch.turn_on
target:
  entity_id: switch.violet_pool_controller_heater
```

---

### Solar

| Entity | Description |
|--------|-------------|
| `switch.violet_pool_controller_solar` | Solar collector |

```yaml
# Only turn on when solar temperature > pool water
automation:
  trigger:
    platform: template
    value_template: >
      {{ states('sensor.violet_pool_controller_solar_temperature') | float(0) >
         states('sensor.violet_pool_controller_pool_temperature') | float(0) + 3 }}
  action:
    service: switch.turn_on
    target:
      entity_id: switch.violet_pool_controller_solar
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

Click on the entity → **Attributes**. A switch exposes:

| Attribute | Meaning |
|---|---|
| `raw_state` | The controller's raw state, e.g. `"3"` or a composite like `"3\|PUMP_ANTI_FREEZE"` |
| `mode` | Human-readable operating mode |
| `status_description` | Human-readable description of the current state |
| `runtime` | Runtime, when the controller reports `<KEY>_RUNTIME` |
| `pending_update` | Present while an optimistic value is waiting for the next poll |

Pump, heater, solar, dosing and backwash switches add device-specific
attributes on top of those (speed, canister level, remaining range, and so on).

> There is no `violet_state` attribute — the raw value is `raw_state` — and
> `last_changed` is a Home Assistant state property, not an attribute of this
> integration.

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
          {% set state = states('switch.violet_pool_controller_pump') %}
          {% set raw = state_attr('switch.violet_pool_controller_pump', 'raw_state') | int(-1) %}
          {% if raw == 0 %} Auto - standby
          {% elif raw == 1 %} Auto - active
          {% elif raw == 2 %} Auto - blocked by a rule
          {% elif raw == 3 %} Auto - forced on by an emergency rule
          {% elif raw == 4 %} Manual on
          {% elif raw == 5 %} Off by an emergency rule
          {% elif raw == 6 %} Manual off
          {% else %} Unknown
          {% endif %}
```

### Returning a switch to automatic

> **`switch.turn_off` does NOT return a device to automatic.** It sends
> **Manual OFF (state 6)**, which pins the device off and keeps the
> controller's own schedule and rules from ever switching it on again. A
> script that "sets everything to automatic" with `switch.turn_off` silently
> disables the pool.

Use the mode select entity instead — it is the only control that can reach
`AUTO`:

```yaml
script:
  all_automatic:
    alias: "Return every device to automatic"
    sequence:
      - action: select.select_option
        target:
          entity_id:
            - select.violet_pool_controller_pump_mode
            - select.violet_pool_controller_heater_mode
            - select.violet_pool_controller_solar_mode
        data:
          option: auto
```

Check the exact option label in **Developer Tools → States** first: it comes
from the translation of your Home Assistant language.

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
      {{ 'PUMP_ANTI_FREEZE' in state_attr('switch.violet_pool_controller_pump', 'raw_state') | string }}
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