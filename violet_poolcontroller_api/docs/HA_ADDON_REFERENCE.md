# Violet Pool Controller - HA Addon Reference
# Complete reference for building a Home Assistant integration/addon
# Controller: VIOLET Pool Controller, Firmware 1.1.9
# API Library: violet-poolcontroller-api (Python, async)

## 1. CONNECTION & AUTH

- Base URL: http://{host}  (default port 80)
- Auth: HTTP Basic Auth (username + password)
- All requests must use aiohttp with `auth=aiohttp.BasicAuth(user, password)`

## 2. CRITICAL API RULES

1. **POST /setConfig uses form-encoded, NOT JSON**
   - MUST pass `data={"key": "value"}` (dict) to aiohttp
   - DO NOT pass `data="key=value"` (string) - this sends text/plain with EMPTY body!
   - DO NOT use `json={"key": "value"}` - controller ignores JSON body
   - Correct Content-Type: `application/x-www-form-urlencoded`

2. **Controller returns "PLEASE_WAIT"** - this is NORMAL, the change is still applied!
   - Always verify changes with a subsequent GET /getConfig?key

3. **No /setTargetValues or /setDosingParameters endpoints** - they return 404 on fw 1.1.9
   - All writes go through POST /setConfig (form-encoded)

4. **No /getWeatherdata** on standalone firmware - returns 404

5. **Circuit breaker recommended** - controller can become unresponsive if flooded with requests
   - Max ~10 requests/second, use rate limiter

## 3. ENDPOINTS

### Read Endpoints (all GET, return JSON unless noted)

| Endpoint | Response | Description |
|----------|----------|-------------|
| `/getReadings?ALL` | JSON dict | ALL sensor values, states, temperatures |
| `/getReadings?key1,key2` | JSON dict | Specific readings only |
| `/getOutputstates` | JSON | Output state flags (bitmask) |
| `/getConfig?key1,key2` | JSON dict | Configuration values |
| `/getHistory?hours=24&sensor=ALL` | JSON | Temperature history |
| `/getOverallDosing` | JSON | Dosing statistics |
| `/getCalibRawValues` | JSON | Live calibration raw values (PH, ORP, POT, flow, etc.) |
| `/getCalibHistory?calibrations_ph.log` | Text (pipe-separated) | pH calibration log |
| `/getCalibHistory?calibrations_orp.log` | Text (pipe-separated) | ORP calibration log |
| `/getCalibHistory?calibrations_pot.log` | Text (pipe-separated) | Chlorine calibration log |
| `/getLog?actions&{page}` | Text (pipe-separated) | Action log (paginated, 0-based) |
| `/getLog?switching&{page}` | Text (pipe-separated) | Switching log |
| `/getLog?onewire&{page}` | Text (pipe-separated) | 1-Wire sensor log |
| `/getLog?downloadActionsLog` | File download | Full action log |
| `/getNotifications?ALL` | JSON dict | Notification history |
| `/getServiceStates` | JSON | Service states (Tunnel, FTP, SAMBA) |

### Write Endpoints

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/setConfig` | POST | form-encoded | Universal config write |
| `/setLanConfig` | POST | form-encoded | Network config (triggers restart) |
| `/setTimezone` | POST | form-encoded | Timezone change (triggers restart) |
| `/setFunctionManually?{CMD}` | GET | - | Switch outputs on/off/auto |
| `/triggerManualDosing` | POST | form-encoded | Start/stop manual dosing |
| `/restoreOldCalib` | POST | form-encoded | Restore old calibration |
| `/setOutputTestmode?{CMD}` | GET | - | Test mode for pump speeds |
| `/reboot` | GET | - | Reboot controller |

### Service Toggle Endpoints (GET)

| Enable | Disable | Description |
|--------|---------|-------------|
| `/enableTUNNEL` | `/disableTUNNEL` | SSH tunnel |
| `/enableFTP` | `/disableFTP` | FTP server |
| `/enableSAMBA` | `/disableSAMBA` | SAMBA share |
| `/enableSUPPORTTUNNEL` | `/disableSUPPORTTUNNEL` | Support tunnel |

## 4. /getReadings?ALL RESPONSE STRUCTURE

Key fields returned (JSON dict):

### Temperatures
| Key | Type | Description |
|-----|------|-------------|
| `onewire1_value` through `onewire12_value` | float | Temperature sensor values (°C) |
| `NAMES_onewire1` through `NAMES_onewire12` | string | Sensor names |

### Water Chemistry
| Key | Type | Description |
|-----|------|-------------|
| `PH` | float | Current pH value |
| `ORP` | float | Current Redox value (mV) |
| `CHLORINE` | float | Current chlorine value (ppm) |
| `PH_target` | float | pH setpoint |
| `ORP_target` | float | Redox setpoint |

### Device States (numeric: 0-6)
| Key | Type | Description |
|-----|------|-------------|
| `PUMP` | int/str | Filter pump state |
| `SOLAR` | int/str | Solar absorber state |
| `HEATER` | int/str | Heater state |
| `LIGHT` | int/str | Lighting state |
| `BACKWASH` | int/str | Backwash state |
| `REFILL` | int/str | Water refill state |
| `PVSURPLUS` | int/str | PV surplus state |
| `ECO` | int/str | Eco mode state |
| `OVERFLOW` | int/str | Overflow state |
| `COVER` | int/str | Cover state |

### Device State Values (3-state logic)
| Value | Mode | Active | Description |
|-------|------|--------|-------------|
| 0 | auto | False | Auto - Standby |
| 1 | auto | True | Auto - Active (Scheduled) |
| 2 | auto | False | Auto - Priority OFF (Rule Blocked) |
| 3 | auto | True | Auto - Priority ON (Emergency Rule) |
| 4 | manual | True | Manual ON (Forced) |
| 5 | auto | False | Rule OFF (Emergency Rule) |
| 6 | manual | False | Manual OFF |

### Pump Details
| Key | Type | Description |
|-----|------|-------------|
| `PUMP_speed` | int | Current pump speed (1-3) |
| `PUMP_RPM_1`, `PUMP_RPM_2`, `PUMP_RPM_3` | int | Pump RPM per speed |
| `PUMP_capacity_1`, `PUMP_capacity_2`, `PUMP_capacity_3` | float | m³/h per speed |

### Flow & Impulse
| Key | Type | Description |
|-----|------|-------------|
| `IMP1_value` | float | Flow rate (cm/s) from impulse input 1 |
| `ANALOG_adc1` through `ANALOG_adc4` | float | Analog input values |

### Runtime & Statistics
| Key | Type | Description |
|-----|------|-------------|
| `RUNTIMES_PUMP_today` | int | Pump runtime today (min) |
| `RUNTIMES_PUMP_total` | int | Total pump runtime |
| `RUNTIMES_SOLAR_today` | int | Solar runtime today |
| `RUNTIMES_BACKWASH_next` | string | Next backwash date |
| `DOSAGE_*_today` | float | Daily dosing amounts |
| `DOSAGE_*_total` | float | Total dosing amounts |

### System
| Key | Type | Description |
|-----|------|-------------|
| `date` | string | Current date (DD.MM.YYYY) |
| `time` | string | Current time (HH:MM:SS) |
| `SYSTEM_uptime` | int | Uptime in seconds |

## 5. SWITCH CONTROL - /setFunctionManually

Format: `GET /setFunctionManually?{OUTPUT},{ACTION},{VALUE1},{VALUE2}`

### Switchable Outputs
| Output | Actions | Value1 | Value2 | Notes |
|--------|---------|--------|--------|-------|
| `PUMP` | ON/OFF/AUTO | duration (sec) | speed (1-3) | Speed only with ON |
| `SOLAR` | ON/OFF/AUTO | duration (sec) | 0 | |
| `HEATER` | ON/OFF/AUTO | duration (sec) | 0 | |
| `LIGHT` | ON/OFF/AUTO/COLOR/PUSH | 0 | 0 | COLOR triggers DMX scene |
| `BACKWASH` | ON/OFF/AUTO | duration (sec) | 0 | |
| `BACKWASHRINSE` | ON/OFF/AUTO | duration (sec) | 0 | |
| `REFILL` | ON/OFF/AUTO | duration (sec) | 0 | |
| `PVSURPLUS` | ON/OFF/AUTO | speed (1-3) | 0 | |
| `ECO` | ON/OFF/AUTO | 0 | 0 | |
| `EXT1_1` through `EXT2_8` | ON/OFF/AUTO | duration (sec) | 0 | Extension relays |
| `DMX_SCENE1` through `DMX_SCENE12` | ON/OFF/PUSH | 0 | 0 | DMX scenes |
| `DIRULE_1` through `DIRULE_7` | ON/OFF/LOCK/UNLOCK | 0 | 0 | Digital input rules |
| `OMNI_DC0` through `OMNI_DC5` | ON/OFF/AUTO | duration | value | Omni DC outputs |

### Cover Control
| Output | Action | Notes |
|--------|--------|-------|
| `COVER_OPEN` | - | Open cover |
| `COVER_CLOSE` | - | Close cover |
| `COVER_STOP` | - | Stop cover |

Cover uses: `GET /setFunctionManually?COVER_OPEN` (no extra params)

### Response Format (text/plain)
```
OK
{OUTPUT_NAME}
{Status text}
```
or
```
ERROR
{OUTPUT_NAME}
{Error text}
```

### IMPORTANT: DOS_* outputs CANNOT use /setFunctionManually!
Returns: `ERROR\nDOS_1_CL\nTHIS IS A DOSING OUTPUT! ARE YOU NUTS?`
Use `/triggerManualDosing` instead for dosing outputs.

## 6. DOSAGE CONTROL

### 6.1 Enable/Disable Dosage Functions
POST /setConfig with form-encoded data:
```python
# Enable
await session.post(url + "/setConfig", data={"DOSAGE_phminus_use": "1"})
# Disable
await session.post(url + "/setConfig", data={"DOSAGE_phminus_use": "0"})
```

| Dosing Type | Enable Key | Config Prefix |
|-------------|-----------|---------------|
| pH- | `DOSAGE_phminus_use` | `DOSAGE_phminus_*` |
| pH+ | `DOSAGE_phplus_use` | `DOSAGE_phplus_*` |
| Chlor | `DOSAGE_chlorine_use` | `DOSAGE_chlorine_*` |
| Elektrolyse | `DOSAGE_electrolysis_use` | `DOSAGE_electrolysis_*` |
| Flockmittel | `DOSAGE_floc_use` | `DOSAGE_floc_*` |
| H2O2 | `DOSAGE_h2o2_use` | `DOSAGE_h2o2_*` |

### 6.2 Setpoint Keys (Sollwerte)
| Dosing Type | Setpoint Key | Example |
|-------------|-------------|---------|
| pH- | `DOSAGE_phminus_setpoint` | 7.05 |
| pH+ | `DOSAGE_phplus_setpoint` | 7.10 |
| Chlor (ORP) | `DOSAGE_chlorine_setpoint_orp` | 825 |
| Elektrolyse (ORP) | `DOSAGE_electrolysis_setpoint_orp` | 700 |

### 6.3 Chlorine Limits
| Key | Description |
|-----|-------------|
| `DOSAGE_chlorine_lowerval_cl` | Min. Chlorwert (ppm) |
| `DOSAGE_chlorine_upperval_cl_day` | Max. Chlorwert Tag |
| `DOSAGE_chlorine_upperval_cl_night` | Max. Chlorwert Nacht |

### 6.4 All Dosing Config Keys (per type, replace {prefix})

| Key | Type | Description |
|-----|------|-------------|
| `DOSAGE_{prefix}_use` | int (0/1) | Enable/disable |
| `DOSAGE_{prefix}_setpoint` | float | pH/Chlor setpoint |
| `DOSAGE_{prefix}_flowrate` | int | Pump flowrate (ms/rotation) |
| `DOSAGE_{prefix}_can_content` | int | Canister content (ml) |
| `DOSAGE_{prefix}_limits_maxdaily` | int | Max daily dosing (ml) |
| `DOSAGE_{prefix}_limits_can_amount` | int | Canister amount for warnings |
| `DOSAGE_{prefix}_limits_startdelay` | string (HH:MM) | Start delay |
| `DOSAGE_{prefix}_dosing_start` | string (HH:MM) | Dosing start time (Floc only) |
| `DOSAGE_{prefix}_mandos_time` | string (HH:MM) | Manual dosing duration |
| `DOSAGE_{prefix}_empty_switch_use` | int | Empty switch enable |
| `DOSAGE_{prefix}_empty_switch_type` | int | Empty switch type |
| `DOSAGE_{prefix}_FEM_messageoptions` | int | Notification bitmask |

### 6.5 Manual Dosing (Start/Stop)
POST /triggerManualDosing with form-encoded:

**Start:**
```
POST /triggerManualDosing
Content-Type: application/x-www-form-urlencoded

output_index={0-5}&time={duration_in_minutes}&action=START
```

**Stop:**
```
POST /triggerManualDosing
Content-Type: application/x-www-form-urlencoded

output_index={0-5}&time=0&action=STOP
```

**Output Index Map:**
| Index | Output | Dosing Type |
|-------|--------|-------------|
| 0 | DOS_1_CL | Chlor |
| 1 | DOS_2_ELO | Elektrolyse |
| 3 | DOS_4_PHM | pH- |
| 4 | DOS_5_PHP | pH+ |
| 5 | DOS_6_FLOC | Flockmittel |

**Response (text/plain):**
```
MANDOS_STARTED\nOK
```
or
```
MANDOS_STOPPED\nOK
```

## 7. TEMPERATURE CONTROL

### Set Device Temperature (Setpoints)
POST /setConfig with form-encoded:
```python
# Solar max temperature
data={"SOLAR_maxtemp": "28"}

# Heater target temperature
data={"HEATER_set_temp": "26"}
```

| Device | Key | Description |
|--------|-----|-------------|
| Solar | `SOLAR_maxtemp` | Max pool temp for solar (°C) |
| Heater | `HEATER_set_temp` | Heater target temp (°C) |

### Temperature Sensor Config
| Key | Type | Description |
|-----|------|-------------|
| `NAMES_onewire{1-12}` | string | Sensor name |
| `ROMCODE_onewire{1-12}` | string | 1-Wire ROM code assignment |
| `OFFSET_{romcode}` | float | Temperature calibration offset |

## 8. CALIBRATION

### Calibration Raw Values (GET /getCalibRawValues)
| Field | Type | Description |
|-------|------|-------------|
| `PH` | float | Current pH reading |
| `ORP` | float | Current Redox reading (mV) |
| `POT_WO_ZEROPOINTOFFSET` | float | Chlorine without zeropoint offset |
| `POT_READABLE_UNCOMP` | float | Uncompensated chlorine (ppm) |
| `IMP1_value` | float | Flow rate (cm/s) |
| `DOS_MODULE_PRESENT` | int | Dosing module connected (0=yes, !=0=no) |
| `epoch` | int | Unix timestamp |
| `date` | string | Date |
| `time` | string | Time |
| `POT_ZEROPOINT` | float | Current zeropoint voltage |
| `POT_ZEROPOINT_OFFSET` | float | Zeropoint offset |
| `onewire1_value` | float | Temperature sensor 1 |

### Calibration Config Keys (POST /setConfig)

**pH 2-point:**
| Key | Description |
|-----|-------------|
| `CALIBRATION_ph_gain` | Gain factor (0.1-3.0) |
| `CALIBRATION_ph_offset` | Offset in mV (±60) |
| `CALIBRATION_ph_last` | Date/time string |
| `CALIBRATION_ph_last_epoch` | Unix timestamp |
| `CALIBRATION_ph_electrode_state` | "UNCHANGED" or "NEW_ELECTRODE" |
| `CALIBRATION_ph_HW_gain` | Hardware gain (CID=2) |
| `CALIBRATION_ph_HW_offset` | Hardware offset (CID=2) |

**ORP 1-point:**
| Key | Description |
|-----|-------------|
| `CALIBRATION_orp_gain` | Gain (always 1.0) |
| `CALIBRATION_orp_offset` | Offset in mV (±100) |
| `CALIBRATION_orp_last` | Date/time string |
| `CALIBRATION_orp_last_epoch` | Unix timestamp |

**Chlorine (POT) 2-point:**
| Key | Description |
|-----|-------------|
| `CALIBRATION_pot_gain` | Gain factor |
| `CALIBRATION_pot_offset` | Offset |
| `CALIBRATION_pot_zeropoint` | Zero-point voltage (mV) |
| `CALIBRATION_pot_zeropoint_last_epoch` | Epoch of last zeropoint |
| `CALIBRATION_pot_zeropoint_offset` | Zeropoint offset (0 on new calib) |
| `CALIBRATION_pot_calib_flow` | Flow at calibration (cm/s) |
| `CALIBRATION_pot_calib_temp` | Temperature at calibration |
| `CALIBRATION_pot_flow_compensation` | Flow compensation factor |

### Restore Calibration
POST /restoreOldCalib with form-encoded:
```
calDate={unix_timestamp}&which={ph|orp|pot}
```

## 9. REMINDERS

| Key | Type | Description |
|-----|------|-------------|
| `REMINDER_ph_calibration` | int | Days until pH calib reminder (0=off, 7,14,30,60,90,120,150,180) |
| `REMINDER_ph_firedate` | string | Date (DD.MM.YYYY) or "0" |
| `REMINDER_orp_calibration` | int | Days until ORP calib reminder |
| `REMINDER_orp_firedate` | string | Date or "0" |
| `REMINDER_pot_calibration` | int | Days until Chlorine calib reminder (0,7,14,21) |
| `REMINDER_pot_firedate` | string | Date or "0" |

## 10. COMPLETE CONFIG KEY REFERENCE

### Function Control
| Key | Type | Description |
|-----|------|-------------|
| `MENU_control_0` | string (block/none) | Filterpumpe visibility |
| `MENU_control_1` | string | Solar visibility |
| `MENU_control_2` | string | Heater visibility |
| `MENU_control_3` | string | Eco mode visibility |
| `MENU_control_4` | string | Backwash visibility |
| `MENU_control_5` | string | Refill visibility |
| `MENU_control_6` | string | Light visibility |
| `MENU_control_7` | string | Cover visibility |
| `MENU_control_8` | string | Weather visibility |
| `PUMP_type` | int (0/1/2) | 0=Standard, 1=Speed, 2=RS485 |
| `SOLAR_maxtemp` | float | Solar max temperature |
| `HEATER_set_temp` | float | Heater target temperature |

### Network (POST /setLanConfig, NOT /setConfig!)
| Key | Type | Description |
|-----|------|-------------|
| `NET_dhcp` | int (0/1) | DHCP enabled |
| `NET_ip` | string | Static IP |
| `NET_sub` | string | Subnet mask |
| `NET_gate` | string | Gateway |
| `NET_dns` | string | DNS server |
| `NET_wifi_use` | int (0/1) | WiFi DirectAccess |
| `NET_wifi_ssid` | string | WiFi SSID |
| `NET_wifi_pass` | string | WiFi password |

### Timezone (POST /setTimezone, triggers restart!)
| Key | Type | Description |
|-----|------|-------------|
| `NET_tz` | string | Timezone string |
| `GUI_language` | string | Language file (e.g. "de") |
| `GUI_color` | string | Color scheme |
| `GUI_accesslevel` | int (0-3) | Access level |

### Impulse & Analog Inputs
| Key | Type | Description |
|-----|------|-------------|
| `IMPULS_input1_use` | int (0/1) | Impulse input 1 enabled |
| `IMPULS_input1_echo_or_switch` | int (0/1) | Echo/switch mode |
| `IMPULS_input1_pulses_per_liter` | float | Pulses per liter |
| `IMPULS_input1_diameter_cell` | float | Cell diameter |
| `ANALOG_adc{1-4}_use` | int | Analog input enabled |
| `ANALOG_adc{1-4}_label` | string | Input label |

### Rules (Timer, Temp, Switching, Analog)
| Key Pattern | Description |
|-------------|-------------|
| `TIMERRULE_{1-8}_{field}` | Timer rules |
| `TEMPRULE_{1-8}_{field}` | Temperature rules |
| `SWITCHINGRULE_{1-8}_{field}` | Switching rules |
| `ANALOGRULE_{1-8}_{field}` | Analog rules |

Rule fields: `_active`, `_output`, `_action`, `_time`, `_days`, `_temp_min`, `_temp_max`, `_value`

### DMX Lighting
| Key | Type | Description |
|-----|------|-------------|
| `LIGHT_pattern{1-12}_enabled` | int | DMX scene enabled |
| `LIGHT_pattern{1-12}_{channel}` | int (0-255) | DMX channel values |

### Extensions
| Key | Type | Description |
|-----|------|-------------|
| `EXTENSION_1_active` | int (0/1) | Extension relay bank 1 |
| `EXTENSION_2_active` | int (0/1) | Extension relay bank 2 |
| `NAMES_EXT{1-2}_{1-8}` | string | Extension relay names |

### Backup & System
| Key | Type | Description |
|-----|------|-------------|
| `BACKUP_auto` | int (0/1) | Auto backup |
| `BACKUP_target` | int | Backup target (SD/USB/Cloud) |
| `SYSTEM_name` | string | Controller name |

## 11. /getReadings SPECIFIC GROUPS (for optimized polling)

Instead of `?ALL`, fetch specific groups to reduce traffic:
- `ADC` - Analog inputs
- `DOSAGE` - Dosing values
- `RUNTIMES` - Runtime counters
- `PUMPPRIOSTATE` - Pump priority states
- `BACKWASH` - Backwash status
- `SYSTEM` - System info
- `INPUT1`, `INPUT2`, `INPUT3`, `INPUT4` - Digital inputs
- `date`, `time` - Current date/time

## 12. ERROR CODES (controller pushes these via HTTP)

Format: `ERRORCODE=NNNN&SUBJECT=text`
Severity: `INFO`, `WARNING`, `ALARM`

Key codes:
- 0000: Test message (INFO)
- 0002: Hardware problem (ALARM)
- 0020-0025: Filter/circulation monitoring (ALARM)
- 0026-0027: Frost protection sensor error (ALARM)
- 0030-0031: Heat exchanger (WARNING/ALARM)
- 0040-0042: Backwash/refill issues
- 0050-0054: Water level errors (ALARM)
- 0060-0062: Overflow tank errors
- 0101-0112: Temperature sensor errors (WARNING)
- 0120-0125: Chlorine dosing warnings
- 0130-0134: Electrolysis warnings
- 0150-0155: pH- dosing warnings
- 0160-0165: pH+ dosing warnings
- 0173-0175: Flocculant warnings
- 0180-0182: Calibration reminders (INFO)
- 0200-0209: Hardware module errors

## 13. SUGGESTED HA ENTITIES

### Sensors
- `sensor.pool_ph` - pH value
- `sensor.pool_orp` - Redox value (mV)
- `sensor.pool_chlorine` - Chlorine value (ppm)
- `sensor.pool_temperature_{1-12}` - Temperature sensors
- `sensor.pool_flow` - Flow rate (cm/s)
- `sensor.pool_ph_setpoint` - pH target
- `sensor.pool_orp_setpoint` - ORP target

### Switches
- `switch.pool_pump` - Filter pump on/off
- `switch.pool_solar` - Solar on/off
- `switch.pool_heater` - Heater on/off
- `switch.pool_light` - Light on/off
- `switch.pool_backwash` - Backwash on/off
- `switch.pool_refill` - Water refill on/off
- `switch.pool_pv_surplus` - PV surplus on/off

### Select / Number
- `select.pool_pump_speed` - Pump speed (1-3)
- `number.pool_ph_setpoint` - pH target (6.0-8.2)
- `number.pool_orp_setpoint` - ORP target (300-925)
- `number.pool_solar_max_temp` - Solar max temp
- `number.pool_heater_target_temp` - Heater target temp

### Binary Sensors
- `binary_sensor.pool_pump_active` - Pump running
- `binary_sensor.pool_solar_active` - Solar active
- `binary_sensor.pool_heater_active` - Heater active
- `binary_sensor.pool_dosing_phminus` - pH- dosing active
- `binary_sensor.pool_dosing_chlorine` - Chlorine dosing active

### Switches (Dosage Enable)
- `switch.dosage_phminus` - pH- enabled
- `switch.dosage_phplus` - pH+ enabled
- `switch.dosage_chlorine` - Chlorine enabled
- `switch.dosage_electrolysis` - Electrolysis enabled
- `switch.dosage_floc` - Flocculant enabled
- `switch.dosage_h2o2` - H2O2 enabled

### Buttons
- `button.pool_backwash_start` - Start backwash
- `button.pool_cover_open` - Open cover
- `button.pool_cover_close` - Close cover
- `button.pool_cover_stop` - Stop cover
- `button.pool_dmx_scene_{1-12}` - Trigger DMX scene

### Diagnostics
- `sensor.pool_pump_runtime_today` - Pump runtime today
- `sensor.pool_dosage_phminus_today` - pH- dosed today
- `sensor.pool_dosage_chlorine_today` - Chlorine dosed today
- `sensor.pool_next_backwash` - Next backwash date
- `sensor.pool_last_ph_calibration` - Last pH calibration
- `sensor.pool_last_orp_calibration` - Last ORP calibration
- `sensor.pool_last_chlorine_calibration` - Last chlorine calibration

## 14. API LIBRARY USAGE EXAMPLES

```python
from violet_poolcontroller_api import VioletPoolAPI

api = VioletPoolAPI("192.168.178.55", "Basti", "sebi2634")
await api.connect()

# Read all values
readings = await api.get_readings("ALL")
ph = readings["PH"]
orp = readings["ORP"]

# Switch pump on at speed 2 for 3600 seconds
await api.set_switch_state("PUMP", "ON", duration=3600, last_value=2)

# Set pH setpoint
await api.set_ph_target(7.2)

# Set ORP setpoint
await api.set_orp_target(800)

# Enable/disable dosing
await api.set_dosage_enabled("Flockmittel", True)
await api.set_dosage_enabled("Flockmittel", False)
enabled = await api.is_dosage_enabled("Flockmittel")

# Manual dosing (start, duration in seconds)
await api.manual_dosing("Chlor", 60)

# Stop manual dosing (returns the channel to automatic mode)
await api.set_switch_state("DOS_1_CL", "OFF")

# Set solar max temperature
await api.set_device_temperature("SOLAR", 28)

# Set heater target temperature
await api.set_device_temperature("HEATER", 26)

# Generic config write
await api.set_config({"DOSAGE_chlorine_setpoint_orp": 825})

# Get log entries
log = await api.get_log("actions", page=0)
for line in log["lines"]:
    print(line)
if log["has_more"]:
    print("More pages available")

# Get notifications
notifications = await api.get_notifications()

await api.disconnect()
```

## 15. PYTHON PACKAGE INFO

- Package: `violet-poolcontroller-api`
- PyPI: https://pypi.org/project/violet-poolcontroller-api/
- Repo: https://github.com/Xerolux/violet-poolController-api
- Version: 0.0.23
- License: AGPL-3.0
- Python: >=3.12
- Dependencies: aiohttp

### Key Classes
- `VioletPoolAPI` - Main API client
- `VioletPoolAPIError` - Base exception
- `VioletState` - State interpreter (from const_devices)
- `CircuitBreaker` - Circuit breaker pattern

### Key Constants (from const_api.py)
- `SWITCH_FUNCTIONS` - All switchable outputs with labels
- `DOSING_FUNCTIONS` - Dosing type -> output key map
- `DOSING_CONFIG_PREFIX` - Dosing type -> config prefix map
- `DOSING_OUTPUT_INDEX` - Output key -> index for manual dosing
- `COVER_FUNCTIONS` - Cover control actions
- `ERROR_CODES` - Error code -> severity/message map
- `DEVICE_PARAMETERS` (const_devices.py) - Per-device capabilities
- `DEVICE_STATE_MAPPING` (const_devices.py) - State value -> mode/active map
