> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Climate.de)**

---

# Climate & Heating – Climate Entities

> Thermostat control for pool heater and solar system.

---

## Overview

The Climate entities provide a full thermostat interface for:
- **Pool Heater** (heat pump, gas, electric)
- **Solar Heating** (solar collector with differential control)

---

## Climate Entities

| Entity | Description | Default Setpoint |
|--------|-------------|------------------|
| `climate.violet_heater` | Main pool heater | 28°C |
| `climate.violet_solar` | Solar heating circuit | 30°C |

---

## HVAC Modes

Each Climate entity supports three modes:

| Mode | Description | When to Use |
|------|-------------|-------------|
| `off` | Heater completely off | Off-season |
| `heat` | Heat to target temperature | Active use |
| `auto` | Controller regulates automatically | Normal operation |

---

## Setting the Target Temperature

### Via Home Assistant UI

Click on the Climate entity → use the temperature slider.

### Via Service

```yaml
service: climate.set_temperature
target:
  entity_id: climate.violet_heater
data:
  temperature: 28
  hvac_mode: heat
```

### Via Number Entity (Alternative)

```yaml
service: number.set_value
target:
  entity_id: number.violet_target_pool_temperature
data:
  value: 28
```

---

## Available Number Entities for Setpoints

| Entity | Description | Range |
|--------|-------------|-------|
| `number.violet_target_pool_temperature` | Pool target temperature | 10–40°C |
| `number.violet_target_solar_temperature` | Solar max temperature | 20–60°C |
| `number.violet_target_ph` | pH setpoint | 6.0–8.0 |
| `number.violet_target_orp` | ORP setpoint | 200–900 mV |

---

## Automations

### Adjust Temperature by Day of Week

```yaml
automation:
  - alias: "Weekend Pool Heat Up"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: time
        weekday:
          - sat
          - sun
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 30
          hvac_mode: heat

  - alias: "Weekday Pool Eco Mode"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 26
          hvac_mode: auto
```

### Disable Heater in Bad Weather

```yaml
automation:
  - alias: "Heater off in rain"
    trigger:
      - platform: state
        entity_id: weather.home
        to: "rainy"
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.violet_heater
        data:
          hvac_mode: "off"
```

### Use Solar Surplus for Heating

```yaml
automation:
  - alias: "Use PV surplus for pool"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_export_power
        above: 2000
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.violet_heater
        data:
          hvac_mode: heat
      - service: violet_pool_controller.manage_pv_surplus
        data:
          mode: activate
          pump_speed: 2
```

### Temperature Target Based on Weather

```yaml
automation:
  - alias: "Adjust target temperature based on outside temperature"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outside_temperature
        above: 25
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 28

  - alias: "Cool days: Increase temperature"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outside_temperature
        below: 18
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 30
```

---

## Solar Differential Control

Solar heating operates with **differential control**:

```
Turn solar on when:
  T_Solar > T_Pool + Differential (e.g. 5°C)

Turn solar off when:
  T_Solar < T_Pool + Hysteresis (e.g. 2°C)
```

The Solar Climate entity displays the current solar maximum temperature as the setpoint.

**Template Sensor for Solar Differential:**

```yaml
template:
  - sensor:
      - name: "Solar-Pool Temperature Difference"
        unit_of_measurement: "°C"
        state: >
          {{ (states('sensor.violet_solar_temperature') | float(0) -
              states('sensor.violet_water_temperature') | float(0)) | round(1) }}
```

---

## PV Surplus Integration

Combine solar system with pool heating:

```yaml
automation:
  - alias: "Optimal PV Usage"
    trigger:
      - platform: time_pattern
        minutes: "/15"
    condition:
      - condition: template
        value_template: >
          {{ states('sensor.solar_production_power') | float(0) > 1500 }}
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ states('sensor.violet_water_temperature') | float(0) < 30 }}
            sequence:
              - service: climate.set_temperature
                target:
                  entity_id: climate.violet_heater
                data:
                  temperature: 30
                  hvac_mode: heat
          - conditions:
              - condition: template
                value_template: >
                  {{ states('sensor.violet_water_temperature') | float(0) >= 30 }}
            sequence:
              - service: climate.set_hvac_mode
                target:
                  entity_id: climate.violet_heater
                data:
                  hvac_mode: "off"
```

---

## Dashboard Card

```yaml
# Thermostat card for pool heater
type: thermostat
entity: climate.violet_heater
name: Pool Heater

# Combined card with temperatures
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.violet_heater
  - type: entities
    title: Temperatures
    entities:
      - sensor.violet_water_temperature
      - sensor.violet_solar_temperature
      - entity: sensor.outside_temperature
        name: Outside Temperature
```

---

## Climate Entity Attributes

| Attribute | Description |
|----------|-------------|
| `current_temperature` | Current water temperature |
| `target_temperature` | Configured target temperature |
| `hvac_mode` | Current mode (off/heat/auto) |
| `hvac_action` | Current action (idle/heating) |
| `min_temp` | Minimum target temperature |
| `max_temp` | Maximum target temperature |

---

## Troubleshooting

### Climate Shows Wrong Temperature

The current temperature of the Climate entity is sourced from the water temperature sensor. Check `sensor.violet_water_temperature`.

### Heater Does Not Turn On

1. Check HVAC mode (must be `heat`)
2. Current temperature < target temperature?
3. Check heater switch (`switch.violet_heater`)
4. Check error codes → [Error-Codes](Error-Codes)

### Target Temperature Not Applied

1. Wait briefly (next polling cycle)
2. Reload integration
3. Check logs for API errors

---

*Back: [Switches](Switches) | Next: [Services](Services)*