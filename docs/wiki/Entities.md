> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Entities.de)**

---

# 🎛️ Entities - Violet Pool Controller

## Overview of All Available Entities

This page lists all entities created by the Violet Pool Controller integration. All icons were **optimized in March 2026** and now use consistent, professional MDI icons.

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Total Entities** | 150+ |
| **Categories** | 8 |
| **Icons Optimized** | 68+ |
| **Icon Set** | Material Design Icons (MDI) |
| **Status** | All verified & working |

---

## 📋 Table of Contents

1. [Sensors](#-sensors)
2. [Binary Sensors](#-binary-sensors)
3. [Switches](#-switches)
4. [Select Controls](#-select-controls)
5. [Number Entities (Setpoints)](#-number-entities-setpoints)
6. [Climate Entities](#-climate-entities)
7. [Entity Naming Convention](#-entity-naming-convention)
8. [Multi-Controller](#-multi-controller)

---

## 🌡️ Sensors

### Temperature Sensors (6 Entities)

| Entity ID | Name | Icon | Unit | Description |
|-----------|------|------|------|-------------|
| `sensor.violet_pool_controller_onewire1_value` | Pool Water | 🏊 `mdi:pool` | °C | Pool water temperature |
| `sensor.violet_pool_controller_onewire2_value` | Outdoor Temperature | 🌡️ `mdi:thermometer` | °C | Outdoor air temperature |
| `sensor.violet_pool_controller_onewire3_value` | Solar Absorber | ☀️ `mdi:solar-power` | °C | Solar collector temperature |
| `sensor.violet_pool_controller_onewire4_value` | Absorber Return | 🔧 `mdi:pipe-valve` | °C | Return temperature with valve |
| `sensor.violet_pool_controller_onewire5_value` | Heat Exchanger | ♨️ `mdi:radiator` | °C | Heat exchanger temperature |
| `sensor.violet_pool_controller_onewire6_value` | Heating Storage | 🚿 `mdi:water-boiler` | °C | Storage temperature |

**Feature Dependency:**
- `onewire1_value`, `onewire2_value`: Always available
- `onewire3_value`, `onewire4_value`: Requires feature **"Solar Absorber"**
- `onewire5_value`, `onewire6_value`: Requires feature **"Heater"**

### Water Chemistry Sensors (3 Entities)

| Entity ID | Name | Icon | Unit | Description |
|-----------|------|------|------|-------------|
| `sensor.violet_pool_controller_ph_value` | pH Value | ⚗️ `mdi:ph` | pH | **Dedicated pH icon!** |
| `sensor.violet_pool_controller_orp_value` | Redox Potential | ⚡ `mdi:lightning-bolt-circle` | mV | Redox potential with circle |
| `sensor.violet_pool_controller_pot_value` | Chlorine Level | 🧪 `mdi:water-plus` | mg/l | Chlorine level in water |

**Feature Dependency:**
- `pH_value`: Requires feature **"pH Control"**
- `orp_value`, `pot_value`: Requires feature **"Chlorine Control"**

### Analog Sensors (7 Entities)

| Entity ID | Name | Icon | Unit | Description |
|-----------|------|------|------|-------------|
| `sensor.violet_pool_controller_adc1_value` | Filter Pressure | 🌡️ `mdi:gauge` | bar | Pressure gauge |
| `sensor.violet_pool_controller_adc2_value` | Overflow Tank | 💧 `mdi:water-sync` | cm | Overflow water level |
| `sensor.violet_pool_controller_adc3_value` | Flow Meter | ↔️ `mdi:swap-horizontal` | m³/h | Flow arrows |
| `sensor.violet_pool_controller_adc4_value` | Analog Sensor 4 | 📊 `mdi:gauge` | - | Universal sensor (4-20mA) |
| `sensor.violet_pool_controller_adc5_value` | Analog Sensor 5 | 〰️ `mdi:sine-wave` | V | Universal sensor (0-10V) |
| `sensor.violet_pool_controller_imp1_value` | Flow Switch | 🔧 `mdi:pipe-valve` | cm/s | Flow switch |
| `sensor.violet_pool_controller_imp2_value` | Pump Flow Rate | 💧 `mdi:water-pump` | m³/h | Volume flow |

**Feature Dependency:** All analog sensors are created automatically when data is available.

### System Sensors (7 Entities)

| Entity ID | Name | Icon | Unit | Description |
|-----------|------|------|------|-------------|
| `sensor.violet_pool_controller_cpu_temp` | CPU Temperature | 🔥 `mdi:thermometer-alert` | °C | Temperature with warning |
| `sensor.violet_pool_controller_cpu_temp_carrier` | Carrier Board | 🖥️ `mdi:motherboard` | °C | Main board |
| `sensor.violet_pool_controller_cpu_uptime` | System Uptime | ⏰ `mdi:clock-time-eight` | - | Clock display |
| `sensor.violet_pool_controller_system_cpu_temperature` | System CPU | 🌡️ `mdi:thermometer-check` | °C | Temperature check |
| `sensor.violet_pool_controller_system_carrier_cpu_temperature` | Carrier CPU | 💾 `mdi:memory` | °C | Memory chip |
| `sensor.violet_pool_controller_system_dosagemodule_cpu_temperature` | Dosing Module CPU | 💾 `mdi:memory-lan` | °C | LAN memory |
| `sensor.violet_pool_controller_system_memoryusage` | Memory Usage | 💾 `mdi:memory-lan` | % | Memory utilization |

**Feature Dependency:** Always available.

### Status Sensors (7 Entities)

| Entity ID | Name | Icon | Unit | Description |
|-----------|------|------|------|-------------|
| `sensor.violet_pool_controller_pump` | Pump Status | ⚙️ `mdi:pump` | - | Pump status |
| `sensor.violet_pool_controller_heater` | Heater Status | ♨️ `mdi:radiator` | - | Heater status |
| `sensor.violet_pool_controller_solar` | Solar Status | ☀️ `mdi:solar-power` | - | Solar status |
| `sensor.violet_pool_controller_backwash` | Backwash Status | 🔄 `mdi:autorenew` | - | Auto-renew cycle |
| `sensor.violet_pool_controller_light` | Light Status | 💡 `mdi:lightbulb` | - | Light status |
| `sensor.violet_pool_controller_pvsurplus` | PV Surplus | ☀️ `mdi:solar-power` | - | PV surplus |
| `sensor.violet_pool_controller_fw` | Firmware | 📦 `mdi:package-variant` | - | Firmware version |

**Feature Dependency:**
- `heater`: Requires feature **"Heater"**
- `solar`: Requires feature **"Solar Absorber"**
- `backwash`: Requires feature **"Backwash"**
- `light`: Requires feature **"LED Lighting"**
- `pvsurplus`: Requires feature **"PV Surplus"**

### Dosing Sensors (5 Entities)

| Entity ID | Name | Icon | Unit | Description |
|-----------|------|------|------|-------------|
| `sensor.violet_pool_controller_dos_1_cl_state` | Chlorine Status | 🧪 `mdi:flask-outline` | - | Chlorine dosing |
| `sensor.violet_pool_controller_dos_2_elo_state` | Electrolysis | ⚡ `mdi:lightning-bolt` | - | Electrolysis status |
| `sensor.violet_pool_controller_dos_4_phm_state` | pH- Status | 🧪 `mdi:flask-minus` | - | pH minus dosing |
| `sensor.violet_pool_controller_dos_5_php_state` | pH+ Status | 🧪 `mdi:flask-plus` | - | pH plus dosing |
| `sensor.violet_pool_controller_dos_6_floc_state` | Flocculant | 💧 `mdi:water` | - | Flocculant status |

**Feature Dependency:**
- `DOS_1_CL_STATE`, `DOS_2_ELO_STATE`: Requires feature **"Chlorine Control"**
- `DOS_4_PHM_STATE`, `DOS_5_PHP_STATE`: Requires feature **"pH Control"**
- `DOS_6_FLOC_STATE`: Requires feature **"Flocculant Dosing"**

---

## 📊 Binary Sensors

### Core Operational States (7 Entities)

| Entity ID | Name | Icon | Device Class | Description |
|-----------|------|------|--------------|-------------|
| `binary_sensor.violet_pool_controller_pump` | Pump State | 💧 `mdi:water-pump` | running | Pump running |
| `binary_sensor.violet_pool_controller_solar` | Solar State | ☀️ `mdi:solar-power` | running | Solar active |
| `binary_sensor.violet_pool_controller_heater` | Heater State | ♨️ `mdi:radiator` | running | Heater active |
| `binary_sensor.violet_pool_controller_light` | Light State | 💡 `mdi:lightbulb` | - | Light on |
| `binary_sensor.violet_pool_controller_backwash` | Backwash State | 🔄 `mdi:autorenew` | running | Backwash running |
| `binary_sensor.violet_pool_controller_refill` | Refill State | 💧 `mdi:water` | running | Refill active |
| `binary_sensor.violet_pool_controller_pvsurplus` | PV Surplus | ☀️ `mdi:solar-power` | - | PV surplus |

### Diagnostic Problem Sensors (5 Entities)

| Entity ID | Name | Icon | Device Class | Description |
|-----------|------|------|--------------|-------------|
| `binary_sensor.violet_pool_controller_circulation_state` | Circulation Issue | ⚠️ `mdi:water-alert` | problem | Circulation problem |
| `binary_sensor.violet_pool_controller_electrode_flow_state` | Electrode Flow Issue | ✅ `mdi:water-check` | problem | Electrode flow |
| `binary_sensor.violet_pool_controller_pressure_state` | Pressure Issue | 🌡️ `mdi:gauge` | problem | Pressure problem |
| `binary_sensor.violet_pool_controller_can_range_state` | Can Range Issue | 🍾 `mdi:bottle-tonic` | problem | Canister problem |

### Additional Binary Sensors

| Entity ID | Name | Icon | Device Class | Description |
|-----------|------|------|--------------|-------------|
| `binary_sensor.violet_pool_controller_eco` | ECO Mode | 🍃 `mdi:leaf` | - | Eco mode active |
| `binary_sensor.violet_pool_controller_input_{1-12}` | Digital Input {1-12} | 🔌 `mdi:electric-switch` | - | Digital inputs |
| `binary_sensor.violet_pool_controller_input_ce{1-4}` | Digital Input CE{1-4} | 🔌 `mdi:electric-switch` | - | Digital inputs CE |

**Feature Dependency:**
- `INPUT_{1-12}`, `INPUT_CE{1-4}`: Requires feature **"Digital Inputs"**

---

## 🔌 Switches

### Main Control Switches (11 Entities)

| Entity ID | Name | Icon | Description |
|-----------|------|------|-------------|
| `switch.violet_pool_controller_pump` | Filter Pump | 💧 `mdi:water-pump` | Pump on/off |
| `switch.violet_pool_controller_solar` | Solar Absorber | ☀️ `mdi:solar-power` | Solar on/off |
| `switch.violet_pool_controller_heater` | Heater | ♨️ `mdi:radiator` | Heater on/off |
| `switch.violet_pool_controller_light` | Lighting | 💡 `mdi:lightbulb` | Light on/off |
| `switch.violet_pool_controller_dos_5_php` | Dosing pH+ | 🧪 `mdi:flask-plus` | Dose pH+ |
| `switch.violet_pool_controller_dos_4_phm` | Dosing pH- | 🧪 `mdi:flask-minus` | Dose pH- |
| `switch.violet_pool_controller_dos_1_cl` | Chlorine Dosing | 🧪 `mdi:flask-outline` | Dose chlorine |
| `switch.violet_pool_controller_dos_6_floc` | Flocculant | 💧 `mdi:water` | Dose flocculant |
| `switch.violet_pool_controller_pvsurplus` | PV Surplus | ☀️ `mdi:solar-power` | PV mode |
| `switch.violet_pool_controller_backwash` | Backwash | 🔄 `mdi:autorenew` | Start backwash |
| `switch.violet_pool_controller_backwashrinse` | Rinse | 🔄 `mdi:autorenew` | Start rinse |

### DMX Scene Switches (12 Entities)

| Entity ID | Name | Icon | Description |
|-----------|------|------|-------------|
| `switch.violet_pool_controller_dmx_scene{1-12}` | DMX Scene {1-12} | 💡 `mdi:lightbulb-multiple` | Control light scenes |

**Feature Dependency:** Requires feature **"LED Lighting"**

### Extension Switches (16 Entities)

| Entity ID | Name | Icon | Description |
|-----------|------|------|-------------|
| `switch.violet_pool_controller_ext1_{1-8}` | Extension 1.{1-8} | 🔌 `mdi:toggle-switch-outline` | Extension 1 |
| `switch.violet_pool_controller_ext2_{1-8}` | Extension 2.{1-8} | 🔌 `mdi:toggle-switch-outline` | Extension 2 |

**Feature Dependency:** Requires feature **"Extension Outputs"**

### Digital Rule Switches (7 Entities)

| Entity ID | Name | Icon | Description |
|-----------|------|------|-------------|
| `switch.violet_pool_controller_dirule_{1-7}` | Switching Rule {1-7} | 📜 `mdi:script-text` | Control switching rules |

**Feature Dependency:** Requires feature **"Digital Inputs"**

---

## 🎛️ Select Controls

### Mode Selects (8 Entities)

| Entity ID | Name | Icon | Options | Description |
|-----------|------|------|---------|-------------|
| `select.violet_pool_controller_pump_mode` | Pump Mode | 💧 `mdi:water-pump` | Off/On/Auto | Pump: Off/On/Auto |
| `select.violet_pool_controller_heater_mode` | Heater Mode | ♨️ `mdi:radiator` | Off/On/Auto | Heater: Off/On/Auto |
| `select.violet_pool_controller_solar_mode` | Solar Mode | ☀️ `mdi:solar-power` | Off/On/Auto | Solar: Off/On/Auto |
| `select.violet_pool_controller_light_mode` | Light Mode | 💡 `mdi:lightbulb` | Off/On/Auto | Light: Off/On/Auto |
| `select.violet_pool_controller_dos_cl_mode` | Chlorine Mode | 🧪 `mdi:flask-outline` | Off/Manual/Auto | Chlorine dosing |
| `select.violet_pool_controller_dos_phm_mode` | pH- Mode | 🧪 `mdi:flask-minus` | Off/Manual/Auto | pH minus dosing |
| `select.violet_pool_controller_dos_php_mode` | pH+ Mode | 🧪 `mdi:flask-plus` | Off/Manual/Auto | pH plus dosing |
| `select.violet_pool_controller_pvsurplus_mode` | PV Mode | ☀️ `mdi:solar-power` | Off/On/Auto | PV surplus mode |

**Feature Dependency:**
- `pump_mode`: Requires feature **"Filter Pump"**
- `heater_mode`: Requires feature **"Heater"**
- `solar_mode`: Requires feature **"Solar Absorber"**
- `light_mode`: Requires feature **"LED Lighting"**
- `dos_cl_mode`: Requires feature **"Chlorine Control"**
- `dos_phm_mode`, `dos_php_mode`: Requires feature **"pH Control"**
- `pvsurplus_mode`: Requires feature **"PV Surplus"**

---

## 🔢 Number Entities (Setpoints)

### Chemistry Setpoints (3 Entities)

| Entity ID | Name | Icon | Min | Max | Step | Default | Unit |
|-----------|------|------|-----|-----|------|---------|------|
| `number.violet_pool_controller_ph_setpoint` | pH Setpoint | ⚗️ `mdi:ph` | 6.8 | 7.8 | 0.1 | 7.2 | pH |
| `number.violet_pool_controller_orp_setpoint` | Redox Setpoint | ⚡ `mdi:lightning-bolt-circle` | 600 | 800 | 10 | 700 | mV |
| `number.violet_pool_controller_chlorine_setpoint` | Chlorine Setpoint | 🧪 `mdi:water-plus` | 0.2 | 2.0 | 0.1 | 0.6 | mg/l |

**Feature Dependency:**
- `ph_setpoint`: Requires feature **"pH Control"**
- `orp_setpoint`, `chlorine_setpoint`: Requires feature **"Chlorine Control"**

### Temperature Setpoints (2 Entities)

| Entity ID | Name | Icon | Min | Max | Step | Default | Unit |
|-----------|------|------|-----|-----|------|---------|------|
| `number.violet_pool_controller_heater_target_temp` | Heater Target Temperature | ♨️ `mdi:radiator` | 20.0 | 35.0 | 0.5 | 28.0 | °C |
| `number.violet_pool_controller_solar_target_temp` | Solar Target Temperature | ☀️ `mdi:solar-power` | 20.0 | 40.0 | 0.5 | 30.0 | °C |

**Feature Dependency:**
- `heater_target_temp`: Requires feature **"Heater"**
- `solar_target_temp`: Requires feature **"Solar Absorber"**

### Pump Speed (1 Entity)

| Entity ID | Name | Icon | Min | Max | Step | Default | Unit |
|-----------|------|------|-----|-----|------|---------|------|
| `number.violet_pool_controller_pump_speed` | Pump Speed | ⚙️ `mdi:pump` | 1 | 3 | 1 | 2 | - |

**Feature Dependency:** Requires feature **"Filter Pump"**

### Canister Volumes (4 Entities)

| Entity ID | Name | Icon | Min | Max | Step | Default | Unit |
|-----------|------|------|-----|-----|------|---------|------|
| `number.violet_pool_controller_chlorine_canister_volume` | Chlorine Canister Volume | 🛢️ `mdi:barrel` | 100 | 50000 | 100 | 10000 | ml |
| `number.violet_pool_controller_ph_minus_canister_volume` | pH- Canister Volume | 🛢️ `mdi:barrel` | 100 | 50000 | 100 | 10000 | ml |
| `number.violet_pool_controller_ph_plus_canister_volume` | pH+ Canister Volume | 🛢️ `mdi:barrel` | 100 | 50000 | 100 | 20000 | ml |
| `number.violet_pool_controller_flocculant_canister_volume` | Flocculant Canister Volume | 🛢️ `mdi:barrel` | 100 | 50000 | 100 | 20000 | ml |

**Feature Dependency:**
- `chlorine_canister_volume`: Requires feature **"Chlorine Control"**
- `ph_minus_canister_volume`, `ph_plus_canister_volume`: Requires feature **"pH Control"**
- `flocculant_canister_volume`: Requires feature **"Flocculant Dosing"**

---

## 🌡️ Climate Entities

### Thermostats (2 Entities)

| Entity ID | Name | Icon | Description |
|-----------|------|------|-------------|
| `climate.violet_pool_controller_heater` | Heater | ♨️ `mdi:radiator` | Heater thermostat |
| `climate.violet_pool_controller_solar` | Solar | ☀️ `mdi:solar-power` | Solar thermostat |

**Feature Dependency:**
- `heater`: Requires feature **"Heater"**
- `solar`: Requires feature **"Solar Absorber"**

**Features:**
- Set temperature
- Select mode (Off/Heat)
- Use schedules
- Create automations

---

## 🏷️ Entity Naming Convention

### Structure

```
{entity_type}.violet_pool_controller_{device_key}
```

**Examples:**
- `sensor.violet_pool_controller_pH_value`
- `switch.violet_pool_controller_pump`
- `climate.violet_pool_controller_heater`

### Multi-Controller

With multiple controllers, the device ID is inserted:

```
{entity_type}.violet_pool_controller_{device_id}_{device_key}
```

**Examples:**
- `sensor.violet_pool_controller_1_ph_value` (Controller 1)
- `sensor.violet_pool_controller_2_ph_value` (Controller 2)
- `switch.violet_pool_controller_1_pump` (Controller 1)
- `switch.violet_pool_controller_2_pump` (Controller 2)

### Change Device ID

You can change the device ID in the integration:

1. Settings → Devices & Services
2. Violet Pool Controller → "..."
3. Change configuration
4. Adjust device ID
5. Restart

⚠️ **Note:** Changing the device ID creates new entities! The old entities remain in the registry.

---

## 🎨 Icon Optimizations (March 2026)

### Top 10 Improvements

| Rank | Icon Change | Reason |
|------|-------------|--------|
| 🥇 | `mdi:flask` → **`mdi:ph`** | Dedicated pH icon instead of flask |
| 🥈 | `mdi:water-percent` → **`mdi:water-sync`** | Overflow instead of percentage |
| 🥉 | `mdi:refresh` → **`mdi:autorenew`** | Auto-renew for cycle |
| 4 | `mdi:pump-on` → **`mdi:water-pump`** | Water pump exists |
| 5 | `mdi:radiator-disabled` → **`mdi:radiator`** | Simpler heater icon |
| 6 | `mdi:lightbulb-on` → **`mdi:lightbulb`** | Standard lightbulb |
| 7 | `mdi:heat-exchange` → **`mdi:radiator`** | Clearer heat exchanger |
| 8 | `mdi:pool-thermometer` → **`mdi:pool`** | Simpler pool icon |
| 9 | `mdi:water-opacity` → **`mdi:water`** | Water instead of turbidity |
| 10 | `mdi:gauge-full` → **`mdi:gauge`** | Standard gauge display |

### All Icon Changes

- **68+ icons optimized**
- **All changed to MDI**
- **Consistent icon set**
- **No broken icons**

📖 **Details:** [Icon Reference](Icon-Reference)

---

## 📖 Next Steps

Now that you know all entities:

1. 🤖 **Create automations**: [Services Guide](Services)
2. 🎨 **Set up dashboard**: [Dashboard Guide](Home)
3. 🐛 **Solve problems**: [Troubleshooting](Troubleshooting)

---

## ❓ FAQ

### Missing entities?

1. **Check feature:**
   - Settings → Devices & Services → Violet Pool Controller
   - "..." → Change configuration
   - Enable feature

2. **Restart Home Assistant:**
   - Settings → System → Restart

3. **Clear browser cache:**
   - Ctrl + Shift + Delete

### Missing icon?

1. **Clear browser cache:**
   - Ctrl + Shift + Delete

2. **Restart Home Assistant:**
   - Settings → System → Restart

3. **Check entity registry:**
   - Settings → Devices & Services → Entities
   - Search for entity

### Rename an entity?

1. Settings → Devices & Services → Entities
2. Search for entity
3. "..." → Rename entity
4. Enter new name

⚠️ **Note:** Renaming affects automations!

---

## 🔗 Useful Links

- 🎨 [Icon Reference](Icon-Reference) - All icons in detail
- 📖 [Configuration Guide](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md)
- 🐛 [Troubleshooting](Troubleshooting)
- 🤖 [Services Guide](Services)

---

**🎉 You now know all entities!**

Good luck creating automations and dashboards!