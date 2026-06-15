> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Sensors.de)**

---

# Sensors & Measurements

> Complete documentation of all sensor entities – from water chemistry to system diagnostics.

> Entity-IDs use the prefix `violet_pool_controller` (or `violet_pool_controller_<device_id>` for multi-controller setups). The suffixes below are appended to that prefix.

---

## Sensor Overview

The integration creates sensor entities dynamically based on the enabled features and the readings reported by `/getReadings`. See [Entities](Entities) for the complete list of suffixes.

### Water Chemistry Sensors

| Suffix | Name | Unit | Typical Range |
|--------|------|------|----------------|
| `pH_value` | pH Value | pH | 6.0–8.0 |
| `orp_value` | ORP / Redox | mV | 200–900 |
| `pot_value` | Free Chlorine | mg/l | 0.1–3.0 |

**Optimal water values:**

```
┌────────────────────────────────────────────────────────┐
│                IDEAL POOL WATER VALUES                  │
├─────────────────┬──────────┬──────────┬────────────────┤
│ Parameter       │ Minimum  │ Optimal  │ Maximum        │
├─────────────────┼──────────┼──────────┼────────────────┤
│ pH              │ 7.0      │ 7.2–7.4  │ 7.6            │
│ ORP/Redox       │ 600 mV   │ 650–750  │ 800 mV         │
│ Free Chlorine   │ 0.2 mg/L │ 0.5–1.0  │ 2.0 mg/L       │
└─────────────────┴──────────┴──────────┴────────────────┘
```

### Temperature Sensors (1-Wire 1–12)

| Suffix | Name | Unit | Feature |
|--------|------|------|---------|
| `onewire1_value` | Pool Water | °C | always |
| `onewire2_value` | Outside Temperature | °C | always |
| `onewire3_value` | Solar Absorber | °C | solar |
| `onewire4_value` | Absorber Return | °C | solar |
| `onewire5_value` | Heat Exchanger | °C | heating |
| `onewire6_value` | Heater Storage | °C | heating |
| `onewire7_value` … `onewire12_value` | Temperature Sensor 7–12 | °C | always |

### Analog Sensors

| Suffix | Name | Unit |
|--------|------|------|
| `ADC1_value` | Filter Pressure | bar |
| `ADC2_value` | Overflow Tank | cm |
| `ADC3_value` | Flow Meter (4-20 mA) | m³/h |
| `ADC4_value` | Analog Sensor 4 (4-20 mA) | – |
| `ADC5_value` | Analog Sensor 5 (0-10 V) | V |
| `IMP1_value` | Dosing Inflow | cm/s |
| `IMP2_value` | Pump Flow Rate | m³/h |

Analog inputs can be wired to external sensors (pressure transducer, flow meter, level probe, …). The unit depends on the connected sensor.

---

## System & Diagnostic Sensors

### System Sensors

| Suffix | Name | Unit |
|--------|------|------|
| `SYSTEM_cpu_temperature` | CPU Temperature | °C |
| `SYSTEM_carrier_cpu_temperature` | Carrier CPU Temperature | °C |
| `SYSTEM_dosagemodule_cpu_temperature` | Dosing Module CPU Temperature | °C |
| `SYSTEM_memoryusage` | System Memory Usage | – |
| `CPU_UPTIME` | Device Uptime | – |
| `LOAD_AVG` | CPU Load Average | – |
| `pump_rs485_pwr` | RS485 Pump Power | W |

### Status Sensors

`PUMP`, `HEATER`, `SOLAR`, `BACKWASH`, `BACKWASHRINSE`, `LIGHT`, `REFILL`, `ECO`, `PVSURPLUS`, `FW` — each shows the readable state for the corresponding output.

### Composite State Sensors (with detail codes)

`PUMPSTATE`, `HEATERSTATE`, `SOLARSTATE` carry the full composite value like `"3|PUMP_ANTI_FREEZE"` or `"2|BLOCKED_BY_OUTSIDE_TEMP"`. See [Device States](Device-States#composite--pipe-separated-states) for the full list of detail codes.

### Dosing State Sensors

`DOS_1_CL_STATE`, `DOS_2_ELO_STATE`, `DOS_4_PHM_STATE`, `DOS_5_PHP_STATE`, `DOS_6_FLOC_STATE`.

---

## Runtime & Statistics

### Per-output Runtime Sensors

Each output exposes a `*_RUNTIME` sensor carrying today's runtime:

- `PUMP_RUNTIME`, `SOLAR_RUNTIME`, `HEATER_RUNTIME`, `LIGHT_RUNTIME`
- `BACKWASH_RUNTIME`, `BACKWASHRINSE_RUNTIME`, `ECO_RUNTIME`, `REFILL_RUNTIME`
- `DOS_1_CL_RUNTIME`, `DOS_2_ELO_RUNTIME`, `DOS_3_ELO_REV_RUNTIME`, `DOS_4_PHM_RUNTIME`, `DOS_5_PHP_RUNTIME`, `DOS_6_FLOC_RUNTIME`
- `EXT1_1_RUNTIME`–`EXT2_8_RUNTIME` (16 extension relays)
- `OMNI_DC0_RUNTIME`–`OMNI_DC5_RUNTIME` (6 OMNI motors)
- `PUMP_RPM_0_RUNTIME`–`PUMP_RPM_3_RUNTIME` (4 RPM levels)

### Dosing Statistics

For every dosing channel:

| Suffix | Description | Unit |
|--------|-------------|------|
| `*_DAILY_DOSING_AMOUNT_ML` | Daily dosing consumption | ml |
| `*_TOTAL_CAN_AMOUNT_ML`    | Remaining canister amount | ml |

### Pump RPM Sensors

| Suffix | Description | Unit |
|--------|-------------|------|
| `PUMP_RPM_0`–`PUMP_RPM_3` | RPM level state code (0-6) | – |
| `PUMP_RPM_0_VALUE`–`PUMP_RPM_3_VALUE` | Measured RPM | RPM |

### Digital Rule Stopwatch

`DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH1..8` — remaining timer (seconds) for each switching rule.

---

## Sensor Calibration

### Recommended Calibration Intervals

| Sensor | Interval | Method |
|--------|----------|--------|
| **pH** | Monthly | Buffer solution pH 7.0 & pH 4.0 |
| **ORP/Redox** | Together with pH | ORP reference solution |
| **Free Chlorine** | Weekly check | Photometer / test strips |
| **Temperatures** | Annually | Reference thermometer |

### Trigger calibration via service

The integration exposes `configure_sensor_calibration` (sensor ID 1–12, offset, multiplier, min/max). See [Services](Services#-service-configure_sensor_calibration).

### Detect calibration drift

```yaml
automation:
  - alias: "pH Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        above: 7.6
        for: "00:15:00"
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        below: 7.0
        for: "00:15:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Pool Warning"
          message: "pH out of range: {{ states('sensor.violet_pool_controller_ph_value') }}"
```

---

## Sensors in Automations

### Complete water-chemistry monitor

```yaml
automation:
  - alias: "Pool Water Chemistry Monitor"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        below: 7.0
        id: ph_low
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        above: 7.6
        id: ph_high
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_pot_value
        below: 0.3
        id: chlorine_low
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_orp_value
        below: 600
        id: orp_low
    action:
      - service: notify.mobile_app
        data:
          title: "Pool Alert"
          message: >
            {% if trigger.id == 'ph_low' %}pH too low: {{ states('sensor.violet_pool_controller_ph_value') }}
            {% elif trigger.id == 'ph_high' %}pH too high: {{ states('sensor.violet_pool_controller_ph_value') }}
            {% elif trigger.id == 'chlorine_low' %}Chlorine too low: {{ states('sensor.violet_pool_controller_pot_value') }} mg/l
            {% elif trigger.id == 'orp_low' %}ORP too low: {{ states('sensor.violet_pool_controller_orp_value') }} mV
            {% endif %}
```

### Solar control based on temperature difference

```yaml
automation:
  - alias: "Start solar when collector is warmer than pool"
    trigger:
      - platform: template
        value_template: >
          {{ (states('sensor.violet_pool_controller_onewire3_value') | float(0)) -
             (states('sensor.violet_pool_controller_onewire1_value') | float(0)) > 5 }}
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_pool_controller_solar
```

---

## Template Sensors

```yaml
template:
  - sensor:
      - name: "Pool Hygiene Status"
        state: >
          {% set ph = states('sensor.violet_pool_controller_ph_value') | float(0) %}
          {% set chlor = states('sensor.violet_pool_controller_pot_value') | float(0) %}
          {% set orp = states('sensor.violet_pool_controller_orp_value') | float(0) %}
          {% if 7.0 <= ph <= 7.4 and chlor >= 0.3 and orp >= 650 %}Optimal
          {% elif 6.8 <= ph <= 7.6 and chlor >= 0.2 %}Acceptable
          {% else %}Action Required{% endif %}
        icon: >
          {% if this.state == 'Optimal' %}mdi:check-circle
          {% elif this.state == 'Acceptable' %}mdi:alert-circle
          {% else %}mdi:alert{% endif %}

      - name: "Pool Temperature Difference Solar"
        unit_of_measurement: "°C"
        state: >
          {{ ((states('sensor.violet_pool_controller_onewire3_value') | float(0)) -
              (states('sensor.violet_pool_controller_onewire1_value') | float(0))) | round(1) }}
```

---

## Troubleshooting Sensor Issues

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| Sensor shows `unavailable` | Controller not reachable | Check connection |
| Sensor shows `unknown` | Sensor not present / feature disabled | Enable feature in setup |
| Incorrect value | Sensor not calibrated | Perform calibration |
| Value fluctuates | Sensor dirty / measurement noise | Clean sensor, raise hysteresis |
| Negative value | Sensor cable defective | Check cable/sensor |
| `DOS_2_ELO_*` missing | No electrolysis module installed | Check hardware |

---

**Next:** [Switches & Control](Switches) | [Climate & Heating](Climate) | [Services](Services)
