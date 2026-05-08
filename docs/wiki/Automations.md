# Automation Examples

> Copy-paste YAML examples for common pool automations.

---

## Quick Start

All examples can be pasted directly into Home Assistant:
**Settings → Automations → Create → YAML Mode**

---

## Pump Control

### Daily Schedule (Time-Based)

```yaml
# Turn pump on in the morning
automation:
  - alias: "Pool: Pump On Morning"
    description: "Turn on filter pump daily at 8 AM"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 2

  - alias: "Pool: Pump Off Night"
    description: "Turn off filter pump at 10 PM"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 1
```

### Increase Pump Speed on Solar Surplus

```yaml
automation:
  - alias: "Pool: Pump on PV Surplus"
    description: "Filter more when solar production is high"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_production
        above: 3000
    condition:
      - condition: time
        after: "09:00:00"
        before: "18:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 3
          duration: 7200

  - alias: "Pool: Normalize pump after PV surplus"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_production
        below: 1000
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 2
```

### Frost Protection for Pump

```yaml
automation:
  - alias: "Pool: Frost Protection Pump"
    description: "Turn on pump when frost is imminent"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outside_temperature
        below: 3
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "off"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_pump
      - service: notify.mobile_app_phone
        data:
          title: "Frost Alert"
          message: "Frost protection active – filter pump turned on!"
```

---

## Water Chemistry & Dosing

### Automatic pH Correction

```yaml
automation:
  - alias: "Pool: pH too low – dose pH+"
    description: "Dose pH+ when pH drops below 7.1"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        below: 7.1
        for:
          minutes: 15
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "on"
    action:
      - service: violet_pool_controller.smart_dosing
        data:
          dosing_type: "pH+"
          action: manual_dose
          duration: 30
      - delay:
          minutes: 60
      - service: notify.mobile_app_phone
        data:
          title: "Pool pH Alert"
          message: "pH was too low ({{ states('sensor.violet_ph_value') }}). pH+ was dosed."

  - alias: "Pool: pH too high – dose pH-"
    description: "Dose pH- when pH rises above 7.6"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        above: 7.6
        for:
          minutes: 15
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "on"
    action:
      - service: violet_pool_controller.smart_dosing
        data:
          dosing_type: "pH-"
          action: manual_dose
          duration: 30
```

### Chlorine Dosing Based on ORP Value

```yaml
automation:
  - alias: "Pool: Chlorine refill at low ORP"
    description: "Dose chlorine when ORP drops below 650 mV"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_orp_value
        below: 650
        for:
          minutes: 30
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "on"
      - condition: time
        after: "10:00:00"
        before: "20:00:00"
    action:
      - service: violet_pool_controller.smart_dosing
        data:
          dosing_type: Chlor
          action: manual_dose
          duration: 45
```

### Weekly Shock Chlorination

```yaml
automation:
  - alias: "Pool: Weekly Shock Chlorination"
    description: "Refill chlorine every Monday"
    trigger:
      - platform: time
        at: "10:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: violet_pool_controller.smart_dosing
        data:
          dosing_type: Chlor
          action: manual_dose
          duration: 60
          safety_override: false
      - service: notify.mobile_app_phone
        data:
          message: "Weekly shock chlorination completed"
```

---

## Temperature & Heating

### Heating by Schedule

```yaml
automation:
  - alias: "Pool: Weekend Heating"
    description: "Weekend: Heat water to 30°C"
    trigger:
      - platform: time
        at: "06:00:00"
    condition:
      - condition: time
        weekday:
          - fri
          - sat
          - sun
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 30
          hvac_mode: heat

  - alias: "Pool: Weekday Eco Heating"
    trigger:
      - platform: time
        at: "06:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 26
          hvac_mode: auto
```

### Notification When Pool Is Warm Enough

```yaml
automation:
  - alias: "Pool: Temperature Notification"
    description: "Info when pool reaches bathing temperature"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_water_temperature
        above: 27
    condition:
      - condition: time
        after: "08:00:00"
        before: "21:00:00"
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool is warm!"
          message: >
            Water temperature: {{ states('sensor.violet_water_temperature') }}°C
            pH: {{ states('sensor.violet_ph_value') }}
            ORP: {{ states('sensor.violet_orp_value') }} mV
```

---

## Lighting & Atmosphere

### Automatic Evening Lighting

```yaml
automation:
  - alias: "Pool: Evening Lighting"
    description: "Turn on lighting at sunset"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:15:00"
    condition:
      - condition: time
        before: "23:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_dmx_scene_1
      - delay:
          hours: 3
      - service: switch.turn_off
        target:
          entity_id: switch.violet_dmx_scene_1

  - alias: "Pool: Lights off at sunrise"
    trigger:
      - platform: sun
        event: sunrise
    action:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.violet_dmx_scene_1
            - switch.violet_dmx_scene_2
```

### Party Mode

```yaml
automation:
  - alias: "Pool: Activate Party Mode"
    trigger:
      - platform: state
        entity_id: input_boolean.party_mode
        to: "on"
    action:
      - service: violet_pool_controller.control_dmx_scenes
        data:
          action: party_mode
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 2
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 30
          hvac_mode: heat

  - alias: "Pool: Deactivate Party Mode"
    trigger:
      - platform: state
        entity_id: input_boolean.party_mode
        to: "off"
    action:
      - service: violet_pool_controller.control_dmx_scenes
        data:
          action: all_off
```

---

## Cover

### Automatic Cover Control

```yaml
automation:
  - alias: "Pool: Close cover on rain"
    trigger:
      - platform: state
        entity_id: weather.home
        to: "rainy"
    condition:
      - condition: state
        entity_id: cover.violet_cover
        state: "open"
    action:
      - service: cover.close_cover
        target:
          entity_id: cover.violet_cover
      - service: notify.mobile_app_phone
        data:
          message: "Pool cover automatically closed (rain)"

  - alias: "Pool: Open cover in the morning"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: state
        entity_id: weather.home
        state: "sunny"
    action:
      - service: cover.open_cover
        target:
          entity_id: cover.violet_cover
```

---

## Maintenance Reminders

### Calibration Reminder

```yaml
automation:
  - alias: "Pool: Calibration Reminder"
    description: "Monthly reminder for electrode calibration"
    trigger:
      - platform: time
        at: "10:00:00"
    condition:
      - condition: template
        value_template: >
          {{ now().day == 1 }}
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool Maintenance"
          message: >
            Monthly reminder:
            - Calibrate pH electrode
            - Check ORP electrode
            - Clean filter
            - Check canister fill levels
```

### Weekly Check with Status Report

```yaml
automation:
  - alias: "Pool: Weekly Status Report"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool Weekly Check"
          message: >
            Water: {{ states('sensor.violet_water_temperature') }}°C
            pH: {{ states('sensor.violet_ph_value') }}
            ORP: {{ states('sensor.violet_orp_value') }} mV
            Chlorine: {{ states('sensor.violet_chlorine') }} mg/l
            Pump: {{ states('switch.violet_pump') }}
            Heater: {{ states('climate.violet_heater') }}
```

---

## Alarms & Notifications

### Alarm System for Critical Values

```yaml
automation:
  - alias: "Pool: Critical pH Alarm"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        below: 6.8
    action:
      - service: notify.mobile_app_phone
        data:
          title: "ALARM: Pool pH Critical!"
          message: >
            pH Value: {{ states('sensor.violet_ph_value') }}
            Dose pH+ immediately!

  - alias: "Pool: Temperature Sensor Alarm"
    trigger:
      - platform: state
        entity_id: sensor.violet_water_temperature
        to: "unavailable"
        for:
          minutes: 5
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool Sensor Failure"
          message: "Temperature sensor not reporting a value!"
```

---

## Blueprints: Ready-Made Templates

The repository contains ready-made blueprints in the `blueprints/automation/` directory.

**Installation:**
1. Copy blueprint file to `config/blueprints/automation/violet_pool/`
2. Settings → Automations → Blueprints → Import

---

*Back: [Services](Services) | Next: [Troubleshooting](Troubleshooting)*