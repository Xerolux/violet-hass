> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Entities.de)**

---

# 🎛️ Entities - Violet Pool Controller

Complete reference of every entity the integration can create. Entities are created dynamically based on the features you enable during setup and the data the controller reports.

> Source of truth: `const_features.py`, `const_sensors.py`, `const_devices.py`. Entity IDs use the prefix `violet_pool_controller` (or `violet_pool_controller_<device_id>` for multi-controller setups — see [Multi-Controller](Multi-Controller)).

---

## 📋 Table of Contents

1. [Sensors](#-sensors)
2. [Binary Sensors](#-binary-sensors)
3. [Switches](#-switches)
4. [Light Entities (DMX)](#-light-entities-dmx)
5. [Select Controls](#-select-controls)
6. [Number Entities (Setpoints)](#-number-entities-setpoints)
7. [Climate Entities](#-climate-entities)
8. [Cover Entity](#-cover-entity)
9. [Entity Naming Convention](#-entity-naming-convention)

---

## 🌡️ Sensors

All sensor definitions live in `const_sensors.py`. Sensors are created automatically when the corresponding reading is present in `/getReadings` and the feature is enabled.

### Temperature Sensors (1-Wire 1–12)

| Entity ID suffix | Name | Unit | Feature |
|------------------|------|------|---------|
| `onewire1_value` | Pool Water | °C | always |
| `onewire2_value` | Outside Temperature | °C | always |
| `onewire3_value` | Solar Absorber | °C | solar |
| `onewire4_value` | Absorber Return | °C | solar |
| `onewire5_value` | Heat Exchanger | °C | heating |
| `onewire6_value` | Heater Storage | °C | heating |
| `onewire7_value` – `onewire12_value` | Temperature Sensor 7–12 | °C | always |

### Water Chemistry Sensors

| Entity ID suffix | Name | Unit | Feature |
|------------------|------|------|---------|
| `pH_value` | pH Value | pH | ph_control |
| `orp_value` | ORP Value | mV | chlorine_control |
| `pot_value` | Chlorine Level | mg/l | chlorine_control |

### Analog Sensors (ADC / IMP)

| Entity ID suffix | Name | Unit |
|------------------|------|------|
| `ADC1_value` | Filter Pressure | bar |
| `ADC2_value` | Overflow Tank | cm |
| `ADC3_value` | Flow Meter (4-20 mA) | m³/h |
| `ADC4_value` | Analog Sensor 4 (4-20 mA) | – |
| `ADC5_value` | Analog Sensor 5 (0-10 V) | V |
| `IMP1_value` | Dosing Inflow | cm/s |
| `IMP2_value` | Pump Flow Rate | m³/h |

### System Sensors

| Entity ID suffix | Name | Unit |
|------------------|------|------|
| `SYSTEM_cpu_temperature` | CPU Temperature | °C |
| `SYSTEM_carrier_cpu_temperature` | Carrier CPU Temperature | °C |
| `SYSTEM_dosagemodule_cpu_temperature` | Dosing Module CPU Temperature | °C |
| `SYSTEM_memoryusage` | System Memory Usage | – |
| `CPU_UPTIME` | Device Uptime | – |
| `LOAD_AVG` | CPU Load Average | – |
| `pump_rs485_pwr` | RS485 Pump Power | W |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH1..8` | DI Rule Remaining Time | s |

### Status Sensors

| Entity ID suffix | Name | Feature |
|------------------|------|---------|
| `PUMP` | Pump Status | filter_control |
| `HEATER` | Heater Status | heating |
| `SOLAR` | Solar Status | solar |
| `BACKWASH` | Backwash Status | backwash |
| `BACKWASHRINSE` | Backwash Rinse Status | backwash |
| `LIGHT` | Lighting Status | led_lighting |
| `REFILL` | Refill Status | water_refill |
| `ECO` | ECO Status | – |
| `PVSURPLUS` | PV Surplus Status | pv_surplus |
| `FW` | Firmware Version | – |

### Composite State Sensors

These carry the full `"3|PUMP_ANTI_FREEZE"` style string with `BLOCKED_BY_*` / `WAITING_FOR_*` detail codes (see [Device States](Device-States)).

| Entity ID suffix | Name | Feature |
|------------------|------|---------|
| `PUMPSTATE` | Pump Detail Status | filter_control |
| `HEATERSTATE` | Heater Detail Status | heating |
| `SOLARSTATE` | Solar Detail Status | solar |

### Dosing State Sensors

| Entity ID suffix | Name | Feature |
|------------------|------|---------|
| `DOS_1_CL_STATE` | Chlorine Dosing Status | chlorine_control |
| `DOS_2_ELO_STATE` | Electrolysis Status | chlorine_control |
| `DOS_4_PHM_STATE` | pH- Dosing Status | ph_control |
| `DOS_5_PHP_STATE` | pH+ Dosing Status | ph_control |
| `DOS_6_FLOC_STATE` | Flocculation Status | flocculation |

### Runtime Sensors (per-output daily runtime)

Each output exposes a `*_RUNTIME` sensor carrying today's runtime (no unit). The integration creates these for:

`PUMP`, `SOLAR`, `HEATER`, `LIGHT`, `BACKWASH`, `BACKWASHRINSE`, `ECO`, `REFILL`,
`DOS_1_CL`, `DOS_2_ELO`, `DOS_3_ELO_REV`, `DOS_4_PHM`, `DOS_5_PHP`, `DOS_6_FLOC`,
`EXT1_1`–`EXT1_8`, `EXT2_1`–`EXT2_8` (16 extension relays),
`OMNI_DC0`–`OMNI_DC5` (6 OMNI motors),
`PUMP_RPM_0`–`PUMP_RPM_3` (4 RPM level runtimes).

### Dosing Statistics Sensors

For every dosing channel (`DOS_1_CL`, `DOS_2_ELO`, `DOS_4_PHM`, `DOS_5_PHP`, `DOS_6_FLOC`) the integration exposes:

| Entity ID suffix | Description | Unit |
|------------------|-------------|------|
| `*_DAILY_DOSING_AMOUNT_ML` | Daily dosing consumption | ml |
| `*_TOTAL_CAN_AMOUNT_ML`    | Remaining canister amount | ml |

### Pump RPM Sensors

| Entity ID suffix | Description | Unit |
|------------------|-------------|------|
| `PUMP_RPM_0`–`PUMP_RPM_3` | RPM level state code (0-6) | – |
| `PUMP_RPM_0_VALUE`–`PUMP_RPM_3_VALUE` | Measured RPM | RPM |

---

## 📊 Binary Sensors

### Core Operational States

| Entity ID suffix | Name | Device Class | Feature |
|------------------|------|--------------|---------|
| `PUMP` | Pump State | running | filter_control |
| `SOLAR` | Solar State | running | solar |
| `HEATER` | Heater State | running | heating |
| `LIGHT` | Light State | – | led_lighting |
| `BACKWASH` | Backwash State | running | backwash |
| `REFILL` | Refill State | running | water_refill |
| `ECO` | ECO Mode | – | – |
| `PVSURPLUS` | PV Surplus | – | pv_surplus |

### Diagnostic Problem Sensors

| Entity ID suffix | Name | Device Class |
|------------------|------|--------------|
| `CIRCULATION_STATE` | Circulation Issue | problem |
| `ELECTRODE_FLOW_STATE` | Electrode Flow Issue | problem |
| `PRESSURE_STATE` | Pressure Issue | problem |
| `CAN_RANGE_STATE` | Can Range Issue | problem |

### Hardware Module Sensors

| Entity ID suffix | Name |
|------------------|------|
| `HW_BASE_MODULE` | Hardware: Base Module |
| `HW_DOSING_MODULE` | Hardware: Dosing Module |
| `HW_EXTENSION_MODULE_1` | Hardware: Extension Module 1 |
| `HW_EXTENSION_MODULE_2` | Hardware: Extension Module 2 |
| `HW_STANDALONE_MODE` | Hardware: Standalone Dosing Unit |
| `HW_DMX_MODULE` | Hardware: DMX Module |
| `HW_DIRULE_MODULE` | Hardware: Digital Rules Module |

### Overflow / Backwash / Bathing AI

| Entity ID suffix | Name | Device Class |
|------------------|------|--------------|
| `OVERFLOW_OVERFILL_STATE` | Overflow Overfill | problem |
| `OVERFLOW_DRYRUN_STATE` | Overflow Dry Run | problem |
| `OVERFLOW_REFILL_STATE` | Overflow Refill | – |
| `BACKWASH_DELAY_RUNNING` | Backwash Delay Active | – |
| `BATHING_AI_SURVEILLANCE_STATE` | Bathing AI Surveillance | – |

### Digital Inputs

| Entity ID suffix | Name | Feature |
|------------------|------|---------|
| `INPUT1`–`INPUT12` | Digital Input 1–12 | digital_inputs |
| `INPUT_CE1`–`INPUT_CE4` | Digital Input CE1–CE4 | digital_inputs |

---

## 🔌 Switches

> All switches are 3-state (Off / On / Auto). See [Device States](Device-States) for the underlying 0-6 codes.

### Core Switches

| Entity ID suffix | Name | Feature |
|------------------|------|---------|
| `PUMP` | Filter Pump | filter_control |
| `SOLAR` | Solar Absorber | solar |
| `HEATER` | Heater | heating |
| `LIGHT` | Lighting | led_lighting |
| `DOS_5_PHP` | Dosing pH+ | ph_control |
| `DOS_4_PHM` | Dosing pH- | ph_control |
| `DOS_1_CL` | Chlorine Dosing | chlorine_control |
| `DOS_2_ELO` | Electrolysis Dosing | chlorine_control |
| `DOS_6_FLOC` | Flocculant | flocculation |
| `PVSURPLUS` | PV Surplus | pv_surplus |
| `BACKWASH` | Backwash | backwash |
| `BACKWASHRINSE` | Rinse | backwash |
| `REFILL` | Water Refill | water_refill |
| `ECO` | ECO Mode | – |

### Extension Relay Switches (16)

| Entity ID suffix | Name | Feature |
|------------------|------|---------|
| `EXT1_1`–`EXT1_8` | Extension 1.1–1.8 | extension_outputs |
| `EXT2_1`–`EXT2_8` | Extension 2.1–2.8 | extension_outputs |

### Digital Input Rule Switches (8)

| Entity ID suffix | Name | Feature |
|------------------|------|---------|
| `DIRULE_1`–`DIRULE_8` | Switching Rule 1–8 | digital_inputs |

### OMNI DC Output Switches (6)

| Entity ID suffix | Name | Feature |
|------------------|------|---------|
| `OMNI_DC0`–`OMNI_DC5` | Omni DC0–DC5 | extension_outputs |

---

## 💡 Light Entities (DMX)

The 12 DMX scenes are exposed as **LightEntity** (not switches) so they integrate cleanly with HA dashboards and the light domain.

| Entity ID suffix | Name | Feature |
|------------------|------|---------|
| `DMX_SCENE1`–`DMX_SCENE12` | DMX Scene 1–12 | led_lighting |

---

## 🎛️ Select Controls

Each controllable output has a matching `*_mode` select entity with the options **Off / On / Auto** (or **Off / Manual / Auto** for dosing channels).

| Entity ID suffix | Name | Backed output |
|------------------|------|---------------|
| `pump_mode` | Pump Mode | PUMP |
| `heater_mode` | Heater Mode | HEATER |
| `solar_mode` | Solar Mode | SOLAR |
| `light_mode` | Light Mode | LIGHT |
| `dos_cl_mode` | Chlorine Dosing Mode | DOS_1_CL |
| `dos_elo_mode` | Electrolysis Dosing Mode | DOS_2_ELO |
| `dos_phm_mode` | pH- Dosing Mode | DOS_4_PHM |
| `dos_php_mode` | pH+ Dosing Mode | DOS_5_PHP |
| `dos_floc_mode` | Flocculant Mode | DOS_6_FLOC |
| `pvsurplus_mode` | PV Surplus Mode | PVSURPLUS |
| `backwash_mode` | Backwash Mode | BACKWASH |
| `backwashrinse_mode` | Rinse Mode | BACKWASHRINSE |
| `refill_mode` | Refill Mode | REFILL |
| `eco_mode` | ECO Mode (read-only) | ECO |
| `ext1_1_mode`–`ext2_8_mode` | Extension 1.1–2.8 Mode (16) | EXT*_* |
| `omni_dc0_mode`–`omni_dc5_mode` | Omni DC0–DC5 Mode (6) | OMNI_DC* |

---

## 🔢 Number Entities (Setpoints)

### Chemistry Setpoints

| Entity ID suffix | Name | Min | Max | Step | Default | Unit |
|------------------|------|-----|-----|------|---------|------|
| `ph_setpoint` | pH Setpoint | 6.8 | 7.8 | 0.1 | 7.2 | pH |
| `orp_setpoint` | ORP Setpoint | 400 | 900 | 5 | 700 | mV |
| `chlorine_setpoint` | Chlorine Setpoint | 0.05 | 5.0 | 0.05 | 0.6 | mg/l |

### Temperature Setpoints

| Entity ID suffix | Name | Min | Max | Step | Default | Unit |
|------------------|------|-----|-----|------|---------|------|
| `heater_target_temp` | Heater Target Temperature | 20.0 | 35.0 | 0.5 | 28.0 | °C |
| `solar_target_temp` | Solar Target Temperature | 20.0 | 40.0 | 0.5 | 30.0 | °C |

### Pump Speed

| Entity ID suffix | Name | Min | Max | Step | Default |
|------------------|------|-----|-----|------|---------|
| `pump_speed` | Pump Speed | 1 | 3 | 1 | 2 |

### Canister Volumes

| Entity ID suffix | Name | Min | Max | Step | Default | Unit |
|------------------|------|-----|-----|------|---------|------|
| `chlorine_canister_volume` | Chlorine Canister Volume | 100 | 50000 | 100 | 10000 | ml |
| `ph_minus_canister_volume` | pH- Canister Volume | 100 | 50000 | 100 | 10000 | ml |
| `ph_plus_canister_volume` | pH+ Canister Volume | 100 | 50000 | 100 | 20000 | ml |
| `flocculant_canister_volume` | Flocculant Canister Volume | 100 | 50000 | 100 | 20000 | ml |

---

## 🌡️ Climate Entities

| Entity ID suffix | Name | Feature | HVAC Modes |
|------------------|------|---------|------------|
| `heater` | Heater | heating | off, heat, auto |
| `solar` | Solar | solar | off, heat, auto |

---

## 🏊 Cover Entity

| Entity ID suffix | Name | Feature | Commands |
|------------------|------|---------|----------|
| `cover` | Pool Cover | cover_control | open, close, stop |

The cover entity reads `COVER_STATE` and reports `OPEN`, `OPENING`, `CLOSED`, `CLOSING`, `STOPPED` (see `CoverState` enum).

---

## 🏷️ Entity Naming Convention

### Structure

```
{entity_type}.violet_pool_controller_{device_key}
```

Examples:
- `sensor.violet_pool_controller_ph_value`
- `switch.violet_pool_controller_pump`
- `climate.violet_pool_controller_heater`
- `light.violet_pool_controller_dmx_scene1`
- `select.violet_pool_controller_pump_mode`
- `number.violet_pool_controller_ph_setpoint`

### Multi-Controller

When several controllers are configured, the per-controller unique id (`{api_url}_{device_id}`) is appended:

```
{entity_type}.violet_pool_controller_{device_id}_{device_key}
```

See [Multi-Controller Guide](Multi-Controller) for details.

---

## ❓ FAQ

### Missing entities?

1. **Enable the feature**: Settings → Devices & Services → Violet Pool Controller → "..." → Change configuration → enable feature.
2. **Restart Home Assistant**: Settings → System → Restart.
3. **Wait one polling cycle** (default: 10 s) for sensors to populate.
4. **Check controller**: Some sensors only appear when the controller reports the corresponding reading (e.g. `DOS_2_ELO_*` requires an electrolysis module).

### Rename an entity?

Settings → Devices & Services → Entities → search → "..." → Rename entity.

> ⚠️ Renaming affects existing automations.

---

**Next:** [Sensors](Sensors) | [Switches](Switches) | [Device States](Device-States) | [Services](Services)
