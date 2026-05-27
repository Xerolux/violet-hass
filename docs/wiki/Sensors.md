> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Sensors.de)**

---

# Sensors & Measurements

> Complete documentation of all sensor entities – from water chemistry to system diagnostics.

---

## Sensor Overview

The integration automatically creates sensor entities based on the enabled features and available data from the controller.

### Water Chemistry Sensors

| Entity ID | Name | Unit | Range | Description |
|-----------|------|------|-------|-------------|
| `sensor.violet_ph_value` | pH Value | – | 6.0–8.0 | Current pH value of the pool water |
| `sensor.violet_orp_value` | ORP/Redox | mV | 200–900 | Oxidation-reduction potential |
| `sensor.violet_chlorine` | Free Chlorine | mg/L | 0.1–3.0 | Free chlorine level |
| `sensor.violet_conductivity` | Conductivity | µS/cm | – | Electrical conductivity (salt content) |

**Optimal Water Values:**

```
┌────────────────────────────────────────────────────────┐
│                IDEAL POOL WATER VALUES                  │
├─────────────────┬──────────┬──────────┬────────────────┤
│ Parameter       │ Minimum  │ Optimal  │ Maximum        │
├─────────────────┼──────────┼──────────┼────────────────┤
│ pH              │ 7.0      │ 7.2–7.4  │ 7.6            │
│ ORP/Redox       │ 600 mV   │ 650–750  │ 800 mV         │
│ Free Chlorine   │ 0.2 mg/L │ 0.5–1.0  │ 2.0 mg/L       │
│ Conductivity    │ –        │ Floor-   │ –              │
│                 │          │ dependent│                │
└─────────────────┴──────────┴──────────┴────────────────┘
```

### Temperature Sensors

| Entity ID | Name | Unit | Description |
|-----------|------|------|-------------|
| `sensor.violet_water_temperature` | Water Temperature | °C | Pool water temperature |
| `sensor.violet_solar_temperature` | Solar Temperature | °C | Solar collector temperature |
| `sensor.violet_ambient_temperature` | Outdoor Temperature | °C | Ambient temperature |
| `sensor.violet_heater_temperature` | Heater Temperature | °C | Heat exchanger temperature |

### Analog Inputs (AI1–AI8)

| Entity ID | Description |
|-----------|-------------|
| `sensor.violet_ai1` | Analog input 1 (configurable) |
| `sensor.violet_ai2` | Analog input 2 (configurable) |
| ... | ... |
| `sensor.violet_ai8` | Analog input 8 (configurable) |

Analog inputs can be used for external sensors (pressure sensor, flow meter, etc.). The unit depends on the connected sensor.

---

## System Sensors

### Diagnostics & Status

| Entity ID | Name | Type | Description |
|-----------|------|------|-------------|
| `sensor.violet_system_error_codes` | Error Codes | String | Current error codes (empty = no error) |
| `sensor.violet_pump_runtime` | Pump Runtime | h | Total operating hours of the pump |
| `sensor.violet_filter_runtime` | Filter Runtime | h | Operating hours since last backwash |
| `sensor.violet_last_calibration` | Last Calibration | Date | Date of last sensor calibration |
| `sensor.violet_firmware_version` | Firmware Version | String | Controller firmware version |

### Calibration History

The integration automatically parses the calibration history from the controller:

| Entity ID | Description |
|-----------|-------------|
| `sensor.violet_ph_calibration_date` | Last pH calibration date |
| `sensor.violet_orp_calibration_date` | Last ORP calibration date |
| `sensor.violet_chlorine_calibration_date` | Last chlorine calibration date |

---

## Sensor Calibration

### Calibration Intervals

| Sensor | Recommended Interval | Method |
|--------|---------------------|--------|
| **pH** | Monthly | Buffer solution pH 7.0 & pH 4.0 |
| **ORP/Redox** | Along with pH calibration | ORP reference solution |
| **Free Chlorine** | Check weekly | Photometer/test strips |
| **Temperatures** | Annually | Reference thermometer |

### Detect Calibration Errors

```yaml
# Automation: Notification when pH is out of range
automation:
  - alias: "pH Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        above: 7.6
        for:
          minutes: 15
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        below: 7.0
        for:
          minutes: 15
    action:
      - service: notify.mobile_app
        data:
          title: "Pool Warning"
          message: "pH value out of range: {{ states('sensor.violet_ph_value') }}"
```

---

## Sensor Attributes

Each sensor contains additional attributes:

```yaml
# Example: sensor.violet_ph_value attributes
state: "7.3"
attributes:
  unit_of_measurement: ""
  device_class: null
  friendly_name: "pH Value"
  last_update: "2026-02-22T10:30:00+00:00"
  controller_ip: "192.168.1.100"
  raw_value: 7.3
```

---

## Sensors in Automations

### Monitor Water Chemistry

```yaml
# Complete water chemistry monitoring
automation:
  - alias: "Pool Water Chemistry Monitor"
    trigger:
      # pH too low
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        below: 7.0
        id: ph_low
      # pH too high
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        above: 7.6
        id: ph_high
      # Chlorine too low
      - platform: numeric_state
        entity_id: sensor.violet_chlorine
        below: 0.3
        id: chlorine_low
      # ORP too low
      - platform: numeric_state
        entity_id: sensor.violet_orp_value
        below: 600
        id: orp_low
    action:
      - service: notify.mobile_app
        data:
          title: "Pool Alert"
          message: >
            {% if trigger.id == 'ph_low' %}
              pH too low: {{ states('sensor.violet_ph_value') }} (target: 7.0–7.4)
            {% elif trigger.id == 'ph_high' %}
              pH too high: {{ states('sensor.violet_ph_value') }} (target: 7.0–7.4)
            {% elif trigger.id == 'chlorine_low' %}
              Chlorine too low: {{ states('sensor.violet_chlorine') }} mg/L
            {% elif trigger.id == 'orp_low' %}
              ORP too low: {{ states('sensor.violet_orp_value') }} mV
            {% endif %}
```

### Temperature-Based Heater Control

```yaml
automation:
  - alias: "Pool Heater on Temperature Drop"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_water_temperature
        below: 26.0
    condition:
      - condition: time
        after: "08:00:00"
        before: "20:00:00"
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.violet_heater
        data:
          hvac_mode: heat
```

### Solar Control Based on Temperature Difference

```yaml
automation:
  - alias: "Start solar when collector is warmer than pool"
    trigger:
      - platform: template
        value_template: >
          {{
            (states('sensor.violet_solar_temperature') | float) -
            (states('sensor.violet_water_temperature') | float) > 5
          }}
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_solar
```

---

## Template Sensors

You can create custom template sensors to combine data:

```yaml
# configuration.yaml or templates.yaml
template:
  - sensor:
      - name: "Pool Hygiene Status"
        state: >
          {% set ph = states('sensor.violet_ph_value') | float(0) %}
          {% set chlor = states('sensor.violet_chlorine') | float(0) %}
          {% set orp = states('sensor.violet_orp_value') | float(0) %}
          {% if 7.0 <= ph <= 7.4 and chlor >= 0.3 and orp >= 650 %}
            Optimal
          {% elif 6.8 <= ph <= 7.6 and chlor >= 0.2 %}
            Acceptable
          {% else %}
            Action Required
          {% endif %}
        icon: >
          {% if this.state == 'Optimal' %}mdi:check-circle
          {% elif this.state == 'Acceptable' %}mdi:alert-circle
          {% else %}mdi:alert{% endif %}

      - name: "Pool Temperature Difference Solar"
        unit_of_measurement: "°C"
        state: >
          {{ (states('sensor.violet_solar_temperature') | float(0)) -
             (states('sensor.violet_water_temperature') | float(0)) | round(1) }}
```

---

## Troubleshooting Sensor Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| Sensor shows `unavailable` | Controller not reachable | Check connection |
| Sensor shows `unknown` | Sensor not present/enabled on controller | Enable feature in setup |
| Incorrect value | Sensor not calibrated | Perform calibration |
| Value fluctuates uncontrollably | Sensor dirty | Clean sensor |
| Negative value | Sensor cable defective | Check cable/sensor |

---

**Next:** [Switches & Control](Switches) | [Climate & Heating](Climate) | [Services](Services)