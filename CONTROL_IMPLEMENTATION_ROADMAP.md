# Control Implementation Roadmap - Violet Pool Controller Addon

**Goal**: Addon als vollständiger Controller-Ersatz via HTTP API

---

## PHASE 1: CORE OUTPUTS (setFunctionManually)

### 1.1 PUMP Control
**API Command**: `setFunctionManually?PUMP,ON,{RPM}` / `setFunctionManually?PUMP,OFF`

**Controllable**:
- ON/OFF (state 4 = manual ON, state 6 = manual OFF)
- RPM Levels: 0, 1, 2, 3
- Anti-Freeze: Auto-select RPM based on temp

**Service**: `control_pump`
- Speed selection (0-3)
- Force OFF
- Eco mode
- Boost mode
- Auto mode

**Entities**:
- Switch: PUMP (ON/OFF)
- Select: PUMP_SPEED (Level 0-3)
- Climate: For temperature setpoint (optional)

---

### 1.2 HEATER Control
**API Command**: `setFunctionManually?HEATER,ON` / `setFunctionManually?HEATER,OFF`

**Controllable**:
- ON/OFF (state 4/6)
- Target Temperature (via CONFIG.HEATER_target_temp via setConfig)
- Postrun (electric type only)

**Service**: Existing `control_heater` or enhance
- ON/OFF
- Set target temp
- Postrun duration

**Entities**:
- Switch: HEATER (ON/OFF)
- Number: HEATER_TARGET_TEMP
- Climate: Thermostat (temp + ON/OFF)

---

### 1.3 SOLAR Control
**API Command**: `setFunctionManually?SOLAR,ON` / `setFunctionManually?SOLAR,OFF`

**Controllable**:
- ON/OFF (state 4/6)
- Target Temperature
- Forced Flush (trigger every X hours)

**Service**: Existing or new
- ON/OFF
- Set target temp
- Manual flush trigger

**Entities**:
- Switch: SOLAR (ON/OFF)
- Number: SOLAR_TARGET_TEMP
- Binary Sensor: SOLAR_FLUSH_ACTIVE

---

### 1.4 COVER Control
**API Command**: `setFunctionManually?COVER,OPEN` / `setFunctionManually?COVER,CLOSE` / `setFunctionManually?COVER,STOP`

**Controllable**:
- OPEN
- CLOSE
- STOP (pause mid-movement)

**Entities**:
- Cover: COVER (open/close/stop)
- Binary Sensor: COVER_MOVEMENT_ACTIVE
- Select: COVER_MODE (if dual-mode)

---

### 1.5 BACKWASH Control
**API Command**: `setFunctionManually?BACKWASH,RUN` / `setFunctionManually?BACKWASH,ABORT`

**Controllable**:
- RUN (start sequence)
- ABORT (stop sequence)
- Observe state machine

**Entities**:
- Switch: BACKWASH (RUN/STOP)
- Binary Sensor: BACKWASH_ACTIVE
- Sensor: BACKWASH_STEP (current step in sequence)

---

## PHASE 2: DOSING SYSTEMS (6 Systems)

### 2.1 Manual Dosing Trigger
**API Endpoint**: `/triggerManualDosing?index={0-5},runtime={seconds}`

**Dosing Systems**:
- 0 = Chlorine (DOS_1_CL)
- 1 = Electrolysis (DOS_2_ELO)
- 2 = pH-Minus (DOS_4_PHM)
- 3 = pH-Plus (DOS_5_PHP)
- 4 = Flocculant (DOS_6_FLOC)
- 5 = H2O2 (DOS_1_H2O2)

**Service**: `smart_dosing`
- Manual dosing per system
- Runtime setting (seconds)
- Immediate execution

**Entities**:
- Switch: DOS_{name} (ON=manual active, OFF=auto mode)
- Number: DOS_{name}_MANUAL_RUNTIME
- Sensor: DOS_{name}_DAILY_AMOUNT_ML
- Sensor: DOS_{name}_REMAINING_RANGE

---

### 2.2 Dosing Configuration (setConfig)
**Configurable Keys**:
```
CONFIG.DOSAGE_chlorine_use (0/1)
CONFIG.DOSAGE_chlorine_set_ppm
CONFIG.DOSAGE_chlorine_daytime_on (HH:MM)
CONFIG.DOSAGE_chlorine_daytime_off (HH:MM)
CONFIG.DOSAGE_chlorine_max_daily_ml
CONFIG.DOSAGE_electrolysis_use (0/1)
CONFIG.DOSAGE_electrolysis_set_ppm
... (same pattern for pH-, pH+, FLOC, H2O2)
```

**Entities**:
- Select: DOS_{name}_ENABLED (ON/OFF via config)
- Number: DOS_{name}_TARGET_VALUE
- Time: DOS_{name}_DAYTIME_START
- Time: DOS_{name}_DAYTIME_END
- Number: DOS_{name}_MAX_DAILY_ML

---

## PHASE 3: RULE MANAGEMENT (4 Types × 8 Rules)

### 3.1 Temperature Rules (TEMPRULE_1-8)
**Config Keys**:
```
CONFIG.TEMPRULE_1_prog_use (0/1)
CONFIG.TEMPRULE_1_prog_sensor_1 (1-8)
CONFIG.TEMPRULE_1_prog_sensor_2 (0=absolute, 1-8)
CONFIG.TEMPRULE_1_prog_logic (">=", "<=")
CONFIG.TEMPRULE_1_prog_diffval (setpoint)
CONFIG.TEMPRULE_1_prog_hystval (hysteresis)
CONFIG.TEMPRULE_1_prog_runtime_on (HH:MM)
CONFIG.TEMPRULE_1_prog_runtime_off (HH:MM)
CONFIG.TEMPRULE_1_prog_output_1/2/3 (output name)
CONFIG.TEMPRULE_1_prog_output_1/2/3_state (0-6)
```

**Service**: `manage_digital_rules` (enhance for all types)

**Entities**:
- Switch: TEMPRULE_1_ENABLED
- Select: TEMPRULE_1_SENSOR_PRIMARY
- Select: TEMPRULE_1_SENSOR_SECONDARY
- Select: TEMPRULE_1_LOGIC
- Number: TEMPRULE_1_DIFF_VALUE
- Number: TEMPRULE_1_HYST_VALUE
- Time: TEMPRULE_1_RUNTIME_ON
- Time: TEMPRULE_1_RUNTIME_OFF

---

### 3.2 Analog Rules (ANALOGRULE_1-8)
**Config Keys**:
```
CONFIG.ANALOGRULE_1_prog_use
CONFIG.ANALOGRULE_1_prog_input (AI1-AI8)
CONFIG.ANALOGRULE_1_prog_logic
CONFIG.ANALOGRULE_1_prog_value (threshold)
CONFIG.ANALOGRULE_1_prog_hyst (hysteresis)
CONFIG.ANALOGRULE_1_prog_runtime_on/off
CONFIG.ANALOGRULE_1_prog_output_1/2/3
CONFIG.ANALOGRULE_1_prog_output_1/2/3_state
```

**Entities**: (Similar to Temperature Rules)

---

### 3.3 Switching Rules (SWITCHINGRULE_1-8)
**Config Keys**:
```
CONFIG.SWITCHINGRULE_1_prog_use
CONFIG.SWITCHINGRULE_1_prog_input (DI1-DI12)
CONFIG.SWITCHINGRULE_1_prog_contact (0=NO, 1=NC)
CONFIG.SWITCHINGRULE_1_prog_output (single output)
CONFIG.SWITCHINGRULE_1_prog_action_on (1 or 3)
CONFIG.SWITCHINGRULE_1_prog_action_off (0 or 6)
CONFIG.SWITCHINGRULE_1_prog_timeout (seconds)
```

**Entities**:
- Switch: SWITCHINGRULE_1_ENABLED
- Select: SWITCHINGRULE_1_INPUT
- Select: SWITCHINGRULE_1_CONTACT_TYPE
- Select: SWITCHINGRULE_1_OUTPUT
- Select: SWITCHINGRULE_1_ACTION_ON
- Select: SWITCHINGRULE_1_ACTION_OFF
- Number: SWITCHINGRULE_1_TIMEOUT

---

### 3.4 Timer Rules (TIMERRULE_1-8)
**Config Keys**:
```
CONFIG.TIMERRULE_1_prog_use
CONFIG.TIMERRULE_1_prog_on_time (HH:MM)
CONFIG.TIMERRULE_1_prog_off_time (HH:MM)
CONFIG.TIMERRULE_1_prog_on_weekdays (bitmask 0-127)
CONFIG.TIMERRULE_1_prog_output_1/2/3
CONFIG.TIMERRULE_1_prog_output_1/2/3_state
```

**Entities**:
- Switch: TIMERRULE_1_ENABLED
- Time: TIMERRULE_1_ON_TIME
- Time: TIMERRULE_1_OFF_TIME
- Select: TIMERRULE_1_WEEKDAYS (multi-select)
- Sensor: TIMERRULE_1_NEXT_TRIGGER

---

## PHASE 4: CONFIGURATION & SYSTEM

### 4.1 Sensor Calibration
**API Endpoint**: `/getCalibRawValues` (read raw ADC values)

**Calibration Points**:
- ORP (400mV, 650mV)
- Chlorine (ppm)
- pH (7.0, 4.0 or 10.0)

**Service**: New `calibrate_sensors`
- Select sensor to calibrate
- Enter calibration points
- Save multipliers/offsets

**Entities**:
- Number: CALIB_ORP_400MV_ACTUAL
- Number: CALIB_ORP_650MV_ACTUAL
- Number: CALIB_PH_7_ACTUAL
- Number: CALIB_CL_PPM_ACTUAL
- Number: CALIB_POT_ZEROPOINT
- Sensor: CALIB_HISTORY

---

### 4.2 Extension Relays (EXT1_1-8, EXT2_1-8)
**API Command**: `setFunctionManually?EXT1_1,ON` / `setFunctionManually?EXT1_1,OFF`

**Configuration Keys**:
```
CONFIG.EXT1_1_name
CONFIG.EXT1_1_type (0=normal, 1=inverted)
CONFIG.EXT1_1_mode (0=manual, 1=auto)
CONFIG.SYSTEM_extension1_swversion
```

**Entities** (per relay):
- Switch: EXT1_1 (ON/OFF)
- Binary Sensor: EXT1_ALIVE (heartbeat monitoring)
- Sensor: EXT1_SW_VERSION

---

### 4.3 PV Surplus Mode
**API Command**: `setFunctionManually?PVSURPLUS,ON,{RPM}` / `setFunctionManually?PVSURPLUS,OFF`

**Configuration**:
```
CONFIG.PUMP_pvsurplus_use
CONFIG.PUMP_pvsurplus_rpm
CONFIG.HEATER_pvsurplus_use
CONFIG.HEATER_pvsurplus_set_temp
```

**Entities**:
- Switch: PVSURPLUS_PUMP (ON/OFF)
- Select: PVSURPLUS_PUMP_RPM
- Switch: PVSURPLUS_HEATER (ON/OFF)
- Number: PVSURPLUS_HEATER_TARGET_TEMP

---

## PHASE 5: MONITORING & DIAGNOSTICS

### 5.1 Error Code Reporting
**Entities**:
- Sensor: CONTROLLER_ERROR_CODES (list of active errors)
- Sensor: LAST_ERROR_CODE (latest error)
- Binary Sensor: CONTROLLER_ONLINE
- Sensor: CONTROLLER_SYSTEM_HEALTH (%)

---

### 5.2 System Status
**Entities**:
- Sensor: FIRMWARE_VERSION
- Sensor: UPTIME
- Sensor: CONNECTION_LATENCY_MS
- Binary Sensor: PUMP_ANTI_FREEZE_ACTIVE
- Binary Sensor: HEATER_POSTRUN_ACTIVE
- Binary Sensor: SOLAR_FLUSH_ACTIVE

---

## Implementation Priority

```
PHASE 1 (CORE - 2 weeks)
├── PUMP Control ✅
├── HEATER Control ✅
├── SOLAR Control ✅
├── COVER Control
├── BACKWASH Control
└── Error Code Sensor

PHASE 2 (DOSING - 2 weeks)
├── Manual Dosing Trigger (all 6 systems)
├── Dosing Configuration (setConfig)
└── Dosing Status Sensors

PHASE 3 (RULES - 3 weeks)
├── Temperature Rules (8 rules)
├── Analog Rules (8 rules)
├── Switching Rules (8 rules)
└── Timer Rules (8 rules)

PHASE 4 (SYSTEM - 2 weeks)
├── Calibration UI
├── Extension Relays
├── PV Surplus
└── System Configuration

PHASE 5 (POLISH - 1 week)
├── Dashboard/Lovelace templates
├── Automation examples
├── Error handling
└── Documentation
```

---

## API Endpoints Summary

```javascript
// Read
GET /getReadings?ALL              // All sensors
GET /getConfig?PUMP_,HEATER_,...  // Configuration
GET /getOutputstatesFinal         // Computed states
GET /getCalibRawValues            // Raw calibration values

// Write
GET /setFunctionManually?{...}    // Manual control
POST /setConfig                   // Configuration update
GET /triggerManualDosing?index=,runtime= // Dosing

// Status
GET /getStatus                    // System status
GET /getErrors                    // Error history
```

---

## Next Steps

1. **Start PHASE 1**: Implement PUMP/HEATER/SOLAR/COVER/BACKWASH control services
2. **Create HTTP client layer**: Wrapper for setFunctionManually & setConfig
3. **Build service schemas**: Voluptuous schemas for all services
4. **Test with real controller**: Verify API responses
