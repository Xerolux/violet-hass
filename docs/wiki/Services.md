> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Services.de)**

---

# 🤖 Services & Automations

All available services for advanced automation of your pool.

## Service Overview

The integration registers **44 services**. `services.yaml` in
`custom_components/violet_pool_controller/` is the authoritative list; the
tables below mirror it, and **Developer Tools → Actions** in Home Assistant
shows every field with its live selector.

### Core control & diagnostics
| Service | Function | Parameters |
|---------|----------|------------|
| `control_pump` | Pump control | action, speed, duration |
| `smart_dosing` | Chemical dosing | dosing_type, action, duration, safety_override |
| `manage_pv_surplus` | PV surplus | mode, pump_speed |
| `control_dmx_scenes` | Light scenes | device_id, action, sequence_delay |
| `set_light_color_pulse` | Colour pulses | pulse_count, pulse_interval |
| `manage_digital_rules` | Digital input rules | rule_key, action |
| `test_output` | Diagnostics | device_id, output, mode, duration |

### Direct HTTP control (`setFunctionManually`)
| Service | Function |
|---------|----------|
| `control_pump_http` | Filter pump; speed 1-3 switches to manual ON at that speed |
| `control_heater_http` | Heater, with setpoint (on/off + target_temperature) |
| `control_solar_http` | Solar circuit |
| `control_cover_http` | open / close / stop |
| `control_backwash_http` | run / abort |
| `manual_dosing_http` | Trigger dosing manually (chlorine / electrolysis / ph_minus / ph_plus / flocculant / **h2o2**), runtime 1-3600 s |
| `control_refill_http` | Start or stop a manual refill. **A duration is mandatory** so the valve cannot stay open |

> Dosing, backwash and refill are `UNSAFE_SWITCH_KEYS`. These services, with
> their mandatory durations, are the supported way to drive them - see
> [Security](Security).

### Dosing configuration
| Service | Function |
|---------|----------|
| `configure_dosing` | Set an arbitrary dosing config parameter |
| `set_dosing_target` | Set the dosing target value |
| `set_dosing_daytime` | Set the daytime window (HH:MM) |
| `set_dosing_max_daily` | Maximum daily volume |
| `enable_dosing` | Enable / disable a dosing system |
| `set_can_amount` | Update a canister's fill level after a refill or replacement |

### Rule management
| Service | Function |
|---------|----------|
| `configure_temp_rule` | Temperature rule (TEMPRULE_1-8) |
| `configure_analog_rule` | Analog threshold rule (ANALOGRULE_1-8) |
| `configure_switching_rule` | Digital input rule (SWITCHINGRULE_1-8) |
| `configure_timer_rule` | Time-based rule (TIMERRULE_1-8) |
| `enable_rule` | Enable / disable any rule type |

### Water level: refill & overflow
| Service | Function |
|---------|----------|
| `configure_refill` | Configure the automatic water refill system |
| `configure_overflow` | Configure overflow, dry-run and bathing-detection protection |
| `get_refill_status` | Refill configuration and live state |
| `get_overflow_status` | Overflow protection configuration and live state |

### System configuration
| Service | Function |
|---------|----------|
| `control_extension_relay` | Extension relay (relay_id 1-8, action, state, duration) |
| `configure_sensor_calibration` | Sensor calibration (sensor_id 1-12, offset, multiplier, min/max) |
| `set_omni_position` | Drive the OmniTronic multi-port valve to a fixed position |
| `set_system_service` | Enable/disable a controller-side service (FTP, Samba, SSH, AirPlay, …) |

### Status and diagnostics (these return data)
| Service | Function |
|---------|----------|
| `get_connection_status` | Connection health metrics |
| `get_error_summary` | Error summary and recovery suggestions |
| `get_backwash_status` | Backwash state, current step, filter pressure |
| `get_calibration_status` | Calibration state of every calibrated sensor |
| `get_refill_status` / `get_overflow_status` | See *Water level* above |
| `get_system_services_status` | Live state of every controller-side system service |
| `get_system_update_status` | Installed and available controller firmware |
| `get_live_trace_snapshot` | One-row snapshot of every controller reading |
| `export_diagnostic_logs` | Export recent logs (see [Extended Logging](Erweiterte-Protokollierung)) |
| `test_connection` | Test the connection to the controller |
| `clear_error_history` | Clear the integration's error history |
| `reset_blocking` | Clear fault-induced blockings (e.g. `BLOCKED_BY_ESC` after an empty canister) |

> **Dosing systems** accepted by the dosing services: `chlorine`,
> `electrolysis`, `ph_minus`, `ph_plus`, `flocculant`, `h2o2`.

> The detailed sections below cover the most-used services. Anything not
> documented in detail is still fully described by its own selectors in
> **Developer Tools → Actions**.

---

## 🔧 Service: control_pump - Pump Control

**Description**: Advanced pump control with speed and modes

### Available Actions
- `speed_control` - Set speed (1-3)
- `force_off` - Forced shutdown
- `eco_mode` - Energy saving mode
- `boost_mode` - Maximum performance
- `auto` - Return to automatic

### Examples

**Start pump at speed 2**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pool_controller_pump
data:
  action: speed_control
  speed: 2
  duration: 3600  # 1 hour
```

**Eco mode for 30 minutes**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pool_controller_pump
data:
  action: eco_mode
  duration: 1800
```

**Boost mode (maximum performance)**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pool_controller_pump
data:
  action: boost_mode
  duration: 600  # 10 minutes
```

---

## 🧪 Service: smart_dosing - Smart Dosing

**Description**: Manual or automatic dosing of chemicals

### Parameters

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `dosing_type` | Text | pH-, pH+, Chlorine, Electrolysis, Flocculant | Which chemical? |
| `action` | Text | manual_dose, auto, stop | Action |
| `duration` | Number | 5-300 | Seconds |
| `safety_override` | Boolean | true/false | Ignore safety interval |

### Examples

**Dose chlorine for 30 seconds**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.chlorine_dosing
data:
  dosing_type: "Chlorine"
  action: manual_dose
  duration: 30
```

**pH adjustment with safety checks**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.ph_dosing_minus
data:
  dosing_type: "pH-"
  action: manual_dose
  duration: 15
  safety_override: false
```

**Enable automatic dosing**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.chlorine_dosing
data:
  dosing_type: "Chlorine"
  action: auto
```

---

## ☀️ Service: manage_pv_surplus - PV Surplus

**Description**: Use solar panel surplus for pool heating

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `mode` | Text | activate/deactivate/auto | - | Mode |
| `pump_speed` | Number | 1-3 | 2 | Pump speed |

### Examples

**PV surplus at level 3**
```yaml
service: violet_pool_controller.manage_pv_surplus
target:
  entity_id: switch.pv_surplus_mode
data:
  mode: activate
  pump_speed: 3
```

**Deactivate PV surplus**
```yaml
service: violet_pool_controller.manage_pv_surplus
target:
  entity_id: switch.pv_surplus_mode
data:
  mode: deactivate
```

---

## 💡 Service: control_dmx_scenes - DMX Lighting

**Description**: Control pool lighting scenes

### Actions
- `all_on` - All lights on
- `all_off` - All lights off
- `all_auto` - Automatic
- `sequence` - Scene sequence
- `party_mode` - Party mode

### Examples

**Turn off all lights**
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: all_off
```

**Party mode with 3-second transitions**
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: sequence
  sequence_delay: 3
```

---

## 🔍 Service: test_output - Diagnostics

**Description**: Test outputs for diagnostics

### Parameters
- `output` - Which output (PUMP, HEATER, SOLAR, etc.)
- `mode` - SWITCH, ON, OFF
- `duration` - 1-900 seconds

### Example

**Test pump for 2 minutes**
```yaml
service: violet_pool_controller.test_output
target:
  device_id: <device_id>
data:
  output: PUMP
  mode: "ON"
  duration: 120
```

---

## 📋 Service: manage_digital_rules - Digital Input Rules

**Description**: Manage automation rules for digital inputs

### Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `rule_key` | DIRULE_1 to DIRULE_8 | Which rule? |
| `action` | trigger, lock, unlock | Action to execute |

### Examples

**Trigger rule 1**
```yaml
service: violet_pool_controller.manage_digital_rules
data:
  rule_key: DIRULE_1
  action: trigger
```

**Lock rule 2 (disable)**
```yaml
service: violet_pool_controller.manage_digital_rules
data:
  rule_key: DIRULE_2
  action: lock
```

---

## 🎨 Service: set_light_color_pulse - Color Pulsing

**Description**: Send color pulse commands to pool lighting

### Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `pulse_count` | 1 | 1-10 | Number of pulses |
| `pulse_interval` | 500 | 100-2000 ms | Interval between pulses |

### Example

**5 color pulses with 1 second interval**
```yaml
service: violet_pool_controller.set_light_color_pulse
data:
  pulse_count: 5
  pulse_interval: 1000
```

---

## 📊 Service: export_diagnostic_logs - Log Export (NEW)

**Description**: Export integration logs for troubleshooting and support

### Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `device_id` | - | - | Target device (required) |
| `lines` | 100 | 10-10000 | Number of log lines |
| `include_timestamps` | true | true/false | Include timestamps? |
| `save_to_file` | false | true/false | Save to `/config/`? |

### Examples

**Export 100 log lines (default)**
```yaml
service: violet_pool_controller.export_diagnostic_logs
target:
  device_id: <device_id>
data:
  lines: 100
```

**Save 500 log lines with timestamps to file**
```yaml
service: violet_pool_controller.export_diagnostic_logs
target:
  device_id: <device_id>
data:
  lines: 500
  include_timestamps: true
  save_to_file: true
```

---

## 🌐 Service: control_heater_http - Heater via HTTP

**Description**: Control pool heater with a target temperature via direct HTTP command.

```yaml
service: violet_pool_controller.control_heater_http
data:
  action: "on"
  target_temperature: 28
```

| Parameter | Range | Description |
|-----------|-------|-------------|
| `action` | on, off | Heater action |
| `target_temperature` | 10–60 °C | Target temperature |

---

## ☀️ Service: control_solar_http - Solar via HTTP

```yaml
service: violet_pool_controller.control_solar_http
data:
  action: "on"
  target_temperature: 30
```

Same parameter structure as `control_heater_http`.

---

## 🏊 Service: control_cover_http - Cover Control

```yaml
service: violet_pool_controller.control_cover_http
data:
  action: open   # open | close | stop
```

---

## 🔄 Service: control_backwash_http - Backwash via HTTP

```yaml
service: violet_pool_controller.control_backwash_http
data:
  action: run    # run | abort
```

---

## 🧪 Service: manual_dosing_http - Manual Dosing via HTTP

**Description**: Manually trigger a dosing pump via `POST /triggerManualDosing`. Supports **all six dosing systems** including H2O2.

```yaml
service: violet_pool_controller.manual_dosing_http
data:
  dosing_system: chlorine
  runtime_seconds: 30
```

| Parameter | Values | Description |
|-----------|--------|-------------|
| `dosing_system` | chlorine, electrolysis, ph_minus, ph_plus, flocculant, **h2o2** | Required |
| `runtime_seconds` | 1–3600 | Required |

---

## ⚙️ Service: configure_dosing - Dosing Configuration

Set any dosing config parameter (`config_key`) to a `value`:

```yaml
service: violet_pool_controller.configure_dosing
data:
  dosing_system: ph_minus
  config_key: DOSAGE_phminus_setpoint
  value: "7.2"
```

---

## 🎯 Service: set_dosing_target - Dosing Target

```yaml
service: violet_pool_controller.set_dosing_target
data:
  dosing_system: chlorine
  target_value: 75
```

`target_value` range: 0–100.

---

## 🕐 Service: set_dosing_daytime - Daytime Window

```yaml
service: violet_pool_controller.set_dosing_daytime
data:
  dosing_system: ph_minus
  day_start: "07:00"
  day_end: "22:00"
```

---

## 📏 Service: set_dosing_max_daily - Max Daily Volume

```yaml
service: violet_pool_controller.set_dosing_max_daily
data:
  dosing_system: chlorine
  max_daily_ml: 500
```

`max_daily_ml` range: 10–10000 ml.

---

## 🔌 Service: enable_dosing - Enable / Disable Dosing

```yaml
service: violet_pool_controller.enable_dosing
data:
  dosing_system: electrolysis
  enabled: true
```

---

## 🌡️ Service: configure_temp_rule - Temperature Rule (1–8)

Configure a temperature-based automation rule (manual section 8.1). Each rule can drive up to three outputs (`output_1..3` + `output_*_state` 0–6).

```yaml
service: violet_pool_controller.configure_temp_rule
data:
  rule_id: 1
  enabled: true
  sensor_1: 1            # 1–8
  sensor_2: 0            # 0=absolute, 1–8=sensor
  logic: ">="
  diff_value: 5
  hyst_value: 1
  runtime_on:  "07:00"
  runtime_off: "22:00"
  output_1: "PUMP"
  output_1_state: 1
```

---

## 📊 Service: configure_analog_rule - Analog Input Rule (1–8)

```yaml
service: violet_pool_controller.configure_analog_rule
data:
  rule_id: 1
  enabled: true
  adc_input: 1
  logic: ">="
  threshold: 1.5
  hysteresis: 0.1
  output_1: "BACKWASH"
  output_1_state: 1
```

---

## 🔀 Service: configure_switching_rule - Digital Input Rule (1–8)

```yaml
service: violet_pool_controller.configure_switching_rule
data:
  rule_id: 1
  enabled: true
  di_input: 1            # 1–12
  contact_type: 0        # 0 = NO, 1 = NC
  output: "EXT1_1"
  action_on: 4
  action_off: 6
  timeout: 60
```

---

## ⏰ Service: configure_timer_rule - Timer Rule (1–8)

```yaml
service: violet_pool_controller.configure_timer_rule
data:
  rule_id: 1
  enabled: true
  on_time: "08:00"
  off_time: "22:00"
  weekdays: 127          # bitmask 0–127 (Mo-Su)
  output_1: "LIGHT"
  output_1_state: 4
```

---

## 🔧 Service: enable_rule - Enable / Disable Any Rule

```yaml
service: violet_pool_controller.enable_rule
data:
  rule_type: temprule    # temprule | analogrule | switchingrule | timerrule
  rule_id: 1
  enabled: false
```

---

## 🔌 Service: control_extension_relay - Extension Relay

```yaml
service: violet_pool_controller.control_extension_relay
data:
  relay_id: 1            # 1–8
  action: "on"           # on | off | toggle
  # state: 4             # optional direct 0–6 (overrides action)
  # duration: 3600       # optional seconds
```

---

## 🌡️ Service: configure_sensor_calibration - Sensor Calibration

```yaml
service: violet_pool_controller.configure_sensor_calibration
data:
  sensor_id: 1           # 1–12
  offset: -0.3           # -10 to +10 °C
  multiplier: 1.0        # 0.5–2.0
  min_value: 0
  max_value: 100
```

---

## Using Developer Tools

You can test services directly in Developer Tools:

1. **Developer Tools** → **Services**
2. Select service (e.g., `violet_pool_controller.control_pump`)
3. Enter target and data
4. Click **"CALL SERVICE"**
5. See result in service log

---

## Next Steps

- 📖 Read: [Automations](Automations) - Practical examples
- 🎯 States: [Device-States](Device-States) - Understanding states
- 🚨 Errors: [Troubleshooting](Troubleshooting) - Resolve service errors