> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Services.de)**

---

# 🤖 Services & Automations

All available services for advanced automation of your pool.

## Service Overview

| Service | Function | Parameters |
|---------|----------|------------|
| **control_pump** | Pump control | action, speed, duration |
| **smart_dosing** | Chemical dosing | dosing_type, action, duration |
| **manage_pv_surplus** | Solar surplus | mode, pump_speed |
| **control_dmx_scenes** | Light scenes | action, sequence_delay |
| **set_light_color_pulse** | Color pulses | pulse_count, pulse_interval |
| **manage_digital_rules** | Digital input rules | rule_key, action |
| **test_output** | Diagnostics | output, mode, duration |
| **export_diagnostic_logs** | Log export | device_id, lines, include_timestamps |

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
  entity_id: switch.violet_pump
data:
  action: speed_control
  speed: 2
  duration: 3600  # 1 hour
```

**Eco mode for 30 minutes**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pump
data:
  action: eco_mode
  duration: 1800
```

**Boost mode (maximum performance)**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pump
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
| `dosing_type` | Text | pH-, pH+, Chlorine, Flocculant | Which chemical? |
| `action` | Text | manual_dose, auto, stop | Action |
| `duration` | Number | 5-300 | Seconds |
| `safety_override` | Boolean | true/false | Ignore safety? |

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
| `rule_key` | DIRULE_1 to DIRULE_7 | Which rule? |
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