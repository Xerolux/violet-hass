# Entity Reference - Violet Pool Controller Integration

Complete list of all entities created by the Violet Pool Controller integration, organized by type and functionality.

## Table of Contents

- [Climate Entities](#climate-entities)
- [Cover Entities](#cover-entities)
- [Sensor Entities](#sensor-entities)
- [Switch Entities](#switch-entities)
- [Binary Sensor Entities](#binary-sensor-entities)
- [Number Entities](#number-entities)
- [Select Entities](#select-entities)

---

## Climate Entities

### `climate.{device_name}_heater`

**Type:** Thermostat
**Device Class:** HEATER
**Icon:** mdi:radiator

Controls the pool heating system with temperature target and scheduling.

**Attributes:**
- `current_temperature` - Current water temperature (°C)
- `temperature` - Target temperature (°C)
- `hvac_action` - Current action: heating, idle, off
- `hvac_modes` - Available modes: heat, off

**Services:**
- `climate.set_temperature` - Set target temperature
- `climate.turn_on` / `climate.turn_off` - Enable/disable heating
- `climate.set_hvac_mode` - Change operation mode

**State Mapping:**
- `0` = OFF
- `1` = ON (Manual)
- `2` = AUTO

---

### `climate.{device_name}_solar`

**Type:** Thermostat
**Device Class:** HEATER
**Icon:** mdi:solar-power

Manages solar collector circulation and heat exchange.

**Attributes:**
- `current_temperature` - Solar collector temperature (°C)
- `temperature` - Maximum solar temperature (°C)
- `hvac_action` - Current action: cooling, idle, off
- `hvac_modes` - Available modes: heat, off

**Services:**
- `climate.set_temperature` - Set max solar temperature
- `climate.turn_on` / `climate.turn_off` - Enable solar circulation

**State Mapping:**
- `0` = OFF
- `1` = ON (Manual)
- `6` = AUTO (Solar priority)

---

## Cover Entities

### `cover.{device_name}_cover`

**Type:** Cover
**Device Class:** SHUTTER
**Icon:** mdi:window-shutter

Controls the automatic pool cover system.

**Attributes:**
- `current_state` - Position: open, closed, opening, closing, stopped
- `position` - 0 (closed) to 100 (open)

**Services:**
- `cover.open_cover` - Open the cover
- `cover.close_cover` - Close the cover
- `cover.stop_cover` - Stop cover movement
- `cover.set_cover_position` - Set specific position (0-100)

**State Values:**
- `OPEN` - Cover is fully open
- `CLOSED` - Cover is fully closed
- `OPENING` - Cover is moving to open position
- `CLOSING` - Cover is moving to closed position
- `STOPPED` - Cover movement was interrupted

---

## Sensor Entities

### Water Chemistry Sensors

#### `sensor.{device_name}_water_temp`

**Type:** Sensor
**Device Class:** TEMPERATURE
**Unit:** °C
**Icon:** mdi:thermometer-water

Current pool water temperature from primary sensor.

#### `sensor.{device_name}_solar_temp`

**Type:** Sensor
**Device Class:** TEMPERATURE
**Unit:** °C
**Icon:** mdi:solar-power-thermometer

Solar collector temperature for heat exchange optimization.

#### `sensor.{device_name}_ph_value`

**Type:** Sensor
**Device Class:** PH
**Unit:** pH
**Icon:** mdi:acid

Water pH level (normal range: 7.0-7.6).

#### `sensor.{device_name}_orp_value`

**Type:** Sensor
**Device Class:** None
**Unit:** mV
**Icon:** mdi:flash

Redox potential (ORP) for water quality monitoring (target: 650-750 mV).

#### `sensor.{device_name}_chlorine_level`

**Type:** Sensor
**Device Class:** None
**Unit:** mg/L
**Icon:** mdi:chemistry

Free chlorine concentration (target: 0.3-0.6 mg/L).

---

### System Status Sensors

#### `sensor.{device_name}_pump_state`

**Type:** Sensor
**Device Class:** ENUM
**Icon:** mdi:pump

Current pump operation state.

**States:**
- `0` = OFF
- `1` = ON (Manual)
- `2` = AUTO (Speed 1)
- `3` = AUTO (Speed 2)
- `4` = AUTO (Speed 3)

#### `sensor.{device_name}_pump_rpm_0`

**Type:** Sensor
**Device Class:** None
**Unit:** RPM
**Icon:** mdi:speedometer

Current pump speed in revolutions per minute.

#### `sensor.{device_name}_pump_runtime`

**Type:** Sensor
**Device Class:** DURATION
**Unit:** hours
**Icon:** mdi:clock-outline

Total pump runtime today (format: "HHh MMm SSs").

---

### Pressure & Flow Sensors

#### `sensor.{device_name}_filter_pressure`

**Type:** Sensor
**Device Class:** PRESSURE
**Unit:** bar
**Icon:** mdi:gauge

Filter system pressure (monitor for clogging).

#### `sensor.{device_name}_water_level`

**Type:** Sensor
**Device Class:** None
**Unit:** %
**Icon:** mdi:water

Current pool water level percentage.

---

### Energy & Environment Sensors

#### `sensor.{device_name}_system_cpu_temp`

**Type:** Sensor
**Device Class:** TEMPERATURE
**Unit:** °C
**Icon:** mdi:chip

Controller internal CPU temperature.

#### `sensor.{device_name}_system_memory`

**Type:** Sensor
**Device Class:** DATA_SIZE
**Unit:** MB
**Icon:** mdi:memory

Controller memory usage.

#### `sensor.{device_name}_load_avg`

**Type:** Sensor
**Device Class:** None
**Unit:** %
**Icon:** mdi:cpu-64-bit

Controller system load average.

---

## Switch Entities

### Main Equipment Switches

#### `switch.{device_name}_pump`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:pump

Controls the circulation pump with variable speed.

**Services:**
- `switch.turn_on` / `switch.turn_off` - Basic control
- `violet_pool_controller.turn_auto` - Set to AUTO mode
- `violet_pool_controller.set_pump_speed` - Set speed level (1-3)

**Speed Levels:**
- `1` = Low (silent mode)
- `2` = Medium (standard)
- `3` = High (maximum flow)

#### `switch.{device_name}_heater`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:radiator

Controls the electric heater.

**Services:**
- `switch.turn_on` / `switch.turn_off` - Manual control
- `violet_pool_controller.turn_auto` - Enable automatic control

#### `switch.{device_name}_solar`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:solar-power

Controls solar circulation pump.

#### `switch.{device_name}_light`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:lightbulb

Pool lighting control.

---

### Chemical Dosing Switches

#### `switch.{device_name}_ph_dosing_minus`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:beaker-minus

pH minus (acid) dosing pump.

**Services:**
- `switch.turn_on` / `switch.turn_off` - Basic control
- `violet_pool_controller.manual_dosing` - Manual dose

#### `switch.{device_name}_ph_dosing_plus`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:beaker-plus

pH plus (base) dosing pump.

#### `switch.{device_name}_chlorine_dosing`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:flask

Chlorine dosing pump.

---

### Maintenance Switches

#### `switch.{device_name}_backwash`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:autorenew

Filter backwash control.

#### `switch.{device_name}_refill`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:water-pump

Auto-fill water level control.

---

### Energy Optimization

#### `switch.{device_name}_pv_surplus`

**Type:** Switch
**Device Class:** OUTLET
**Icon:** mdi:solar-power

PV surplus mode for energy-optimized heating.

**Services:**
- `violet_pool_controller.set_pv_surplus` - Configure PV surplus mode

**Parameters:**
- `active` - Enable/disable mode
- `pump_speed` - Speed level (1-3)

---

## Binary Sensor Entities

### Equipment Status

#### `binary_sensor.{device_name}_pump_state`

**Type:** Binary Sensor
**Device Class:** RUNNING
**Icon:** mdi:pump

Pump ON/OFF status (derived from state).

#### `binary_sensor.{device_name}_heater_state`

**Type:** Binary Sensor
**Device Class:** RUNNING
**Icon:** mdi:radiator

Heater ON/OFF status.

#### `binary_sensor.{device_name}_solar_state`

**Type:** Binary Sensor
**Device Class:** RUNNING
**Icon:** mdi:solar-power

Solar system ON/OFF status.

---

### Safety Sensors

#### `binary_sensor.{device_name}_backwash_state`

**Type:** Binary Sensor
**Device Class:** RUNNING
**Icon:** mdi:autorenew

Backwash in progress.

#### `binary_sensor.{device_name}_refill_state`

**Type:** Binary Sensor
**Device Class:** PROBLEM
**Icon:** mdi:water-alert

Water refill active.

---

## Number Entities

### Target Values

#### `number.{device_name}_ph_target`

**Type:** Number
**Device Class:** None
**Unit:** pH
**Icon:** mdi:acid

Target pH value for automatic dosing (range: 6.0-8.5, default: 7.2).

#### `number.{device_name}_orp_target`

**Type:** Number
**Device Class:** None
**Unit:** mV
**Icon:** mdi:flash

Target redox potential (range: 200-900 mV, default: 700 mV).

#### `number.{device_name}_chlorine_target`

**Type:** Number
**Device Class:** None
**Unit:** mg/L
**Icon:** mdi:chemistry

Target chlorine level (range: 0.1-5.0 mg/L, default: 0.6 mg/L).

---

### Temperature Setpoints

#### `number.{device_name}_pool_temp_target`

**Type:** Number
**Device Class:** TEMPERATURE
**Unit:** °C
**Icon:** mdi:thermometer

Target pool water temperature (range: 10-40°C, default: 28°C).

#### `number.{device_name}_solar_temp_max`

**Type:** Number
**Device Class:** TEMPERATURE
**Unit:** °C
**Icon:** mdi:solar-power-thermometer

Maximum solar collector temperature (range: 20-60°C, default: 45°C).

---

## Select Entities

### Pump Speed Modes

#### `select.{device_name}_pump_speed`

**Type:** Select
**Icon:** mdi:speedometer

Pump speed preset selection.

**Options:**
- `0` = OFF
- `1` = Speed 1 (Low - Silent)
- `2` = Speed 2 (Medium - Standard)
- `3` = Speed 3 (High - Maximum)

---

### Operation Modes

#### `select.{device_name}_chlorine_mode`

**Type:** Select
**Icon:** mdi:chemistry

Chlorine dosing operation mode.

**Options:**
- `0` = OFF
- `1` = AUTO
- `4` = MANUAL (ON)
- `6` = AUTO (Priority)

---

## Naming Convention

Entity names follow this pattern:

```
{entity_type}.{device_name}_{sensor_name}
```

**Examples:**
- `sensor.pool_water_temp`
- `switch.pool_pump`
- `climate.pool_heater`

Where `{device_name}` is configured during integration setup (default: "pool" or custom).

---

## Entity Categories

### Configuration (for UI)

All entities include proper `entity_category`:
- **CONFIG** - Number entities for settings
- **DIAGNOSTIC** - System status sensors
- None - Main controls and sensors

### Device Class

Most entities have appropriate `device_class` for:
- Automatic icon selection
- Correct state display
- Proper unit handling

---

## Attribute Examples

### Climate Entity Attributes

```json
{
  "current_temperature": 26.5,
  "temperature": 28.0,
  "hvac_action": "idle",
  "hvac_modes": ["heat", "off"],
  "min_temp": 10,
  "max_temp": 40,
  "target_temp_step": 0.5,
  "preset_modes": ["none", "away", "eco"]
}
```

### Pump Entity Attributes

```json
{
  "current_state": 2,
  "rpm": 1200,
  "power": 450,
  "runtime_today": "06h 23m 12s",
  "last_on": "2026-02-28T14:30:00",
  "last_off": "2026-02-28T16:45:00"
}
```

---

*For the latest entity list and features, check your controller's capabilities via the API:*
```bash
curl http://{controller_ip}/getReadings?ALL | jq
```
