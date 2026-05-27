# 🏊 Violet Pool Controller Home Assistant - Complete Wiki

> **Everything you need to know about the Violet Pool Controller Addon for Home Assistant** - From installation to uninstallation, with detailed explanations of all features, states, and services.

---

## 📑 Table of Contents

1. [Installation & Setup](#-installation--setup)
2. [Configuration](#-configuration)
3. [Devices & Entities](#-devices--entities)
4. [Device States Explained](#-device-states-explained)
5. [Services & Automations](#-services--automations)
6. [Sensors & Measurements](#-sensors--measurements)
7. [Switches & Controls](#-switches--controls)
8. [Error Handling & Troubleshooting](#-error-handling--troubleshooting)
9. [Updates & Upgrades](#-updates--upgrades)
10. [Uninstallation](#-uninstallation)
11. [FAQ & Frequently Asked Questions](#-faq--frequently-asked-questions)
12. [Security & Best Practices](#-security--best-practices)

---

## 📦 Installation & Setup

### System Requirements

- **Home Assistant Version**: 2025.12.0 or newer
- **Python**: 3.12+
- **Network**: Violet Pool Controller accessible on the local network
- **Storage**: Minimal (integration requires <10 MB)

### HACS Installation (Recommended)

**Step 1: Open HACS**
1. Home Assistant → Settings
2. Devices & Services → HACS (Custom Repositories)
3. ⋮ (Menu) → Custom Repositories

**Step 2: Add Repository**
```
URL: https://github.com/xerolux/violet-hass
Category: Integration
```

**Step 3: Install Integration**
1. Search for "Violet Pool Controller"
2. Click "Install"
3. **Restart Home Assistant**

**Step 4: Enable Integration**
1. Settings → Devices & Services
2. "Add Integration"
3. Search for "Violet Pool Controller" and add it
4. Enter Host IP (e.g. 192.168.1.100)

### Manual Installation

For developers or without HACS:

```bash
# Clone repository
cd /config/custom_components/
git clone https://github.com/xerolux/violet-hass.git violet_pool_controller

# Or download ZIP and extract
cd /config
unzip violet-hass-main.zip
mv violet-hass-main/custom_components/violet_pool_controller .
```

**Then restart Home Assistant:**
- Web UI: ⋮ → System Controls → Restart Home Assistant
- Docker: `docker restart homeassistant`

### Initial Setup

#### Step 1: Start Configuration Flow

1. Settings → Devices & Services → "Add Integration"
2. Select "Violet Pool Controller"
3. Enter "Host IP Address" (e.g. `192.168.1.100`)

#### Step 2: Authentication (Optional)

If your controller requires username/password:
- Enter username (usually `admin`)
- Enter password
- **Enable SSL/TLS**: If using HTTPS

#### Step 3: Select Features

The wizard shows the following options:

- **Heater**: Do you use a heater?
- **Solar**: Do you have a solar thermal collector?
- **Digital Inputs**: DI1-DI8 configured?
- **PV Surplus**: Solar system with surplus mode?
- **Additional Features**: Backwash, dosing, etc.

> **Tip**: Only enable features you actually use = better performance!

#### Step 4: Sensor Selection

The integration checks your controller for available sensors and offers them for selection:

- **Water Chemistry**: pH, ORP, Chlorine
- **Temperatures**: Pool, Ambient, Solar
- **System Status**: Pressure, Water levels
- **Runtime Statistics**: Pumps, heaters, etc.

> **Default**: If nothing is selected → all sensors will be created

#### Step 5: Polling Interval

- **Suggested**: 30 seconds
- **Minimum**: 10 seconds
- **Maximum**: 300 seconds
- **Recommended for large pools**: 20-30 seconds

---

## ⚙️ Configuration

### Configuration Options

After installation you can fine-tune the integration:

**Settings → Devices & Services → Violet Pool Controller → ⋮ (Menu) → Options**

| Option | Example | Description |
|--------|---------|-------------|
| **Host/IP Address** | `192.168.1.100` | IP of the Violet controller |
| **Port** | `8080` | HTTP port (default: 80) |
| **Polling Interval** | `30` | Update frequency in seconds |
| **Timeout** | `10` | Request timeout in seconds |
| **Use SSL/TLS** | ☑ | Enable HTTPS |
| **Verify SSL Certificate** | ☑ | Certificate validation |
| **Username** | `admin` | Only if required |
| **Password** | `****` | Only if required |

### Advanced Options

#### SSL/TLS Configuration

**Enable SSL:**
- Necessary when controller uses HTTPS
- Installed certificate will be validated

**Disable SSL certificate verification:**
- ⚠️ **Only for self-signed certificates!**
- Only in trusted networks
- Home Assistant will show a warning

```yaml
# Example: Configuration with self-signed certificate
Host: 192.168.1.100
Use SSL: ☑
Verify SSL Certificate: ☐
```

#### Timeout Settings

- **Total timeout**: 10 seconds (default)
- **Connection timeout**: 8 seconds (80% of total time)
- **Socket timeout**: 8 seconds

> These values are optimized. Only adjust if you experience connection issues.

#### Pool Configuration (Optional)

In the configuration flow you can enter:
- **Pool Size**: e.g. 50 m³
- **Pool Type**: Indoor/Outdoor
- **Disinfectant**: Chlorine/Bromine/etc.

These influence the default values for dosing.

### Feature Groups

The integration supports the following feature groups:

| Feature | Description | Options |
|---------|-------------|---------|
| **Pump** | Filter pump with speed control | Off/On/Auto, 3 speed levels |
| **Heater** | Heater with thermostat | Off/Heat/Auto, Setpoint (°C) |
| **Solar** | Solar thermal collector | Off/Heat/Auto, Setpoint (°C) |
| **Dosing** | Chemical dosing | pH-, pH+, Chlorine, Flocculant |
| **Backwash** | Filter backwash | Manual, with timer |
| **Lighting** | Pool lighting | On/Off, DMX scenes, Colors |
| **Cover** | Pool cover | Open/Close, Position tracking |
| **PV Surplus** | Solar surplus usage | Auto, 3 speed levels |
| **Digital Inputs** | DI1-DI8 | Binary sensors, Rules |

---

## 🖥️ Devices & Entities

### What is an Entity?

An **entity** is a controllable or measurable element in Home Assistant:
- **Sensors**: Measurements (temperature, pressure)
- **Switches**: Controllable (pump, heater)
- **Climate**: Heater with thermostat
- **Cover**: Cover with position

### Naming Scheme

Entities automatically receive unique names:

```
{domain}.{device_name}_{feature_name}
```

**Examples:**
- `sensor.violet_pool_temperature` → Water temperature
- `switch.violet_pump` → Filter pump
- `climate.violet_heater` → Heater with thermostat
- `cover.violet_pool_cover` → Pool cover

### Multi-Controller Operation

When multiple controllers are connected:

```
{domain}.{device_name_1}_{feature_name}
{domain}.{device_name_2}_{feature_name}
```

Names are extended with `_2`, `_3`, etc.

### Organizing Entities

Home Assistant automatically displays entities by device. You can also organize them manually:

1. Settings → Devices & Services → Devices
2. Select your Violet device
3. Move or rename entities

---

## 🎯 Device States Explained

### The 7 Device States (0-6)

The Violet controller has 7 different states for devices. These are **very important to understand**:

| State | Name | Description | Manual/Auto | Status | Explanation |
|-------|------|-------------|-------------|--------|-------------|
| **0** | AUTO_OFF | Auto - Off | Auto | ⛔ OFF | Automatic active, device not running |
| **1** | MANUAL_ON | Manual On | Manual | ✅ ON | Manually turned on |
| **2** | AUTO_ON | Auto - On | Auto | ✅ ON | Automatic active, device running |
| **3** | AUTO_TIMER | Auto - Timer | Auto | ✅ ON | Automatic with timer control, active |
| **4** | MANUAL_FORCED | Manual Forced | Manual | ✅ ON | Manually turned on, forced |
| **5** | AUTO_WAITING | Auto - Waiting | Auto | ⛔ OFF | Automatic active, waiting for conditions |
| **6** | MANUAL_OFF | Manual Off | Manual | ⛔ OFF | Manually turned off |

### State Visualization in Home Assistant

Depending on the state, different icons and colors are displayed:

**Automatic Mode:**
- 🟢 **Green** (Auto - Active): States 2, 3
- 🔵 **Blue** (Auto - Ready): States 0, 5

**Manual Mode:**
- 🟠 **Orange** (Manual On): States 1, 4
- 🔴 **Red** (Manual Off): State 6

### Special States

#### State 3 with Additional Info: `3|PUMP_ANTI_FREEZE`

States can include additional information separated by `|`:

```
3|PUMP_ANTI_FREEZE    → Automatic with frost protection active
2|BLOCKED_BY_TEMP     → Automatic running, but blocked by temperature
```

**The number is important**, the additional info is explanatory.

### State Transitions

Typical transitions:

```
6 (Manual Off)
  ↓
1 (Manual On)       → User manually turns on
  ↓
6 (Manual Off)      → User manually turns off

---

0 (Auto - Off)
  ↓
2 (Auto - On)       → Automatic detects condition
  ↓
3 (Auto - Timer)    → Timer control takes effect
  ↓
0 (Auto - Off)      → Condition met or condition changed
```

### Using States in Automations

**Example: Check if pump is running**

```yaml
automation:
  - alias: "Check Pump Status"
    trigger:
      - platform: state
        entity_id: switch.violet_pump
        to: "on"
    action:
      - service: notify.notify
        data:
          message: "Pump is now running!"
```

**Example: React to Manual Status**

```yaml
automation:
  - alias: "Notification on manual heater"
    trigger:
      - platform: template
        value_template: "{{ state_attr('switch.violet_heater', 'violet_state') in ['1', '4'] }}"
    action:
      - service: notify.notify
        data:
          message: "Heater is running in manual mode!"
```

---

## 🤖 Services & Automations

### Available Services

The integration provides specialized services for advanced automation. These are significantly more powerful than simple on/off switches.

### 🔧 Service: `control_pump` - Pump Control

**Description**: Advanced pump control with speed and modes

**Available actions:**
- `speed_control` - Speed (1-3) with timer
- `force_off` - Force turn off
- `eco_mode` - Energy saving (reduced speed)
- `boost_mode` - Maximum performance
- `auto` - Return to automatic

**Example: Start pump at speed 2**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pump
data:
  action: speed_control
  speed: 2
  duration: 3600  # 1 hour
```

**Example: Pump in eco mode for 30 minutes**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pump
data:
  action: eco_mode
  duration: 1800
```

**Parameters:**

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `action` | Text | See above | - | Action to perform |
| `speed` | Number | 1-3 | 2 | Pump speed |
| `duration` | Number | 0-86400 | 0 | Duration in seconds (0=unlimited) |

### 🧪 Service: `smart_dosing` - Smart Dosing

**Description**: Manual or automatic dosing of chemicals

**Available chemicals:**
- `pH-` (Acid/Reduction)
- `pH+` (Base/Increase)
- `Chlorine` (Disinfectant)
- `Flocculant` (Filter aid)

**Available actions:**
- `manual_dose` - Manual dose
- `auto` - Start automatic dosing
- `stop` - Stop dosing

**Example: Dose chlorine for 30 seconds**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.chlorine_dosing
data:
  dosing_type: "Chlorine"
  action: manual_dose
  duration: 30
```

**Example: pH adjustment with safety**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.ph_dosing_minus
data:
  dosing_type: "pH-"
  action: manual_dose
  duration: 15
  safety_override: false  # Observe safety checks
```

**Parameters:**

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `dosing_type` | Text | See above | - | Which chemical? |
| `action` | Text | See above | - | Action to perform |
| `duration` | Number | 5-300 | 30 | Dosing duration in seconds |
| `safety_override` | Boolean | true/false | false | Ignore safety intervals |

### ☀️ Service: `manage_pv_surplus` - PV Surplus Management

**Description**: Use solar system surplus for pool heating

**Modes:**
- `activate` - Enable PV mode
- `deactivate` - Disable PV mode
- `auto` - Automatic management

**Example: PV surplus with speed 3**
```yaml
service: violet_pool_controller.manage_pv_surplus
target:
  entity_id: switch.pv_surplus_mode
data:
  mode: activate
  pump_speed: 3
```

**Parameters:**

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `mode` | Text | activate/deactivate/auto | - | Mode |
| `pump_speed` | Number | 1-3 | 2 | Pump speed |

### 💡 Service: `control_dmx_scenes` - DMX Lighting

**Description**: Control pool lighting scenes

**Available actions:**
- `all_on` - Turn on all scenes
- `all_off` - Turn off all scenes
- `all_auto` - Automatic
- `sequence` - Play scenes in sequence
- `party_mode` - Activate party mode

**Example: Turn off all lights**
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: all_off
```

**Example: Party mode with scene switching**
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: sequence
  sequence_delay: 3  # 3 seconds between scenes
```

### 🔍 Service: `test_output` - Diagnostics

**Description**: Test outputs for diagnostics and maintenance

**Parameters:**
- `output` - Which output? (PUMP, HEATER, SOLAR, etc.)
- `mode` - SWITCH, ON, or OFF
- `duration` - Test duration (1-900 seconds)

**Example: Test pump for 2 minutes**
```yaml
service: violet_pool_controller.test_output
target:
  device_id: <device_id>
data:
  output: PUMP
  mode: "ON"
  duration: 120
```

### Automation Blueprints

Ready-made automation templates are included in the project:

**Installation:**
1. Settings → Automations & Scenes → Blueprints
2. "Import Blueprint"
3. Enter repository URL

**Available Blueprints:**
- 🌡️ Smart Temperature Control
- 🧪 pH Management
- ⚡ Energy Optimization
- 🌧️ Weather Automation
- 🏊 Pool Modes (Party, Eco, Winter)

---

## 📊 Sensors & Measurements

### Water Chemistry Sensors

These sensors measure water quality:

| Sensor | Unit | Range | Normal Value | Description |
|--------|------|-------|-------------|-------------|
| **pH Value** | pH | 6.0-8.5 | 7.0-7.4 | Acidity (7=neutral) |
| **Redox Potential (ORP)** | mV | 400-800 | 650-750 | Disinfection effectiveness |
| **Chlorine** | mg/l | 0-5 | 1.0-3.0 | Free chlorine |
| **Conductivity** | µS/cm | 0-2000 | ~1200 | Salt content |

### Temperature Sensors

| Sensor | Unit | Range | Description |
|--------|------|-------|-------------|
| **Pool Temperature** | °C | 0-50 | Current water temperature |
| **Solar Temperature** | °C | 0-80 | Solar thermal collector temperature |
| **Ambient Temperature** | °C | -20-60 | Outside temperature |

### System Sensors

| Sensor | Unit | Description |
|--------|------|-------------|
| **Filter Pressure** | bar | Pressure in filter system (0.5-2.5) |
| **Water Levels** | % | Pool water level |
| **Pump Runtime** | h | Total runtime today |
| **Heater Runtime** | h | Total runtime |
| **Energy Consumption** | kWh | Today's power consumption |

### Analog Inputs (AI1-AI8)

If available: `sensor.violet_ai1` through `sensor.violet_ai8`
- General-purpose measurement inputs (0-10V or 4-20mA)
- Custom sensors can be connected

### Digital Inputs (DI1-DI8)

Binary sensors for switches, contacts, push buttons:
- `binary_sensor.violet_di1` through `binary_sensor.violet_di8`
- On/Off states

### Error Codes Sensor

`sensor.violet_system_error_codes` shows current errors:

```
[]                      → No errors
[101, 205]             → Multiple errors (e.g. sensor, pressure errors)
```

### Calibration History

`sensor.violet_calibration_history` contains calibration data:
- Date and time
- Calibrated sensor (pH, ORP, etc.)
- Calibration values

---

## 🎚️ Switches & Controls

### The 3-State Switch Logic

All devices are **3-state switches** with the following states:
1. **On** (ON)
2. **Off** (OFF)
3. **Automatic** (AUTO)

```
Switch: On → Off → Automatic → On ...
```

Home Assistant also displays the internal **state** (0-6):

```
Display: On/Off/Automatic (Internal: State 1/6/0)
```

### Switch Types

#### 1. Binary Switches (On/Off only)
- Pool cover
- Backwash
- Some extension relays

**Commands:**
```yaml
service: switch.turn_on
target:
  entity_id: switch.violet_backwash

service: switch.turn_off
target:
  entity_id: switch.violet_backwash
```

#### 2. 3-State Switches (On/Off/Auto)
- Pump
- Heater
- Solar
- Dosing
- DMX scenes

**Commands:**
```yaml
# Turn on
service: switch.turn_on
target:
  entity_id: switch.violet_pump

# Turn off
service: switch.turn_off
target:
  entity_id: switch.violet_pump

# Automatic
service: violet_pool_controller.turn_auto
target:
  entity_id: switch.violet_pump
```

### Available Switches

#### Main Components

| Switch | Function | States | Special Features |
|--------|----------|--------|------------------|
| **Pump** | Filter pump | On/Off/Auto | 3 speed levels |
| **Heater** | Main heater | On/Off/Auto | With thermostat |
| **Solar** | Solar thermal | On/Off/Auto | With thermostat |
| **Lighting** | Pool light | On/Off/Auto | DMX scenes possible |

#### Chemical Dosing

| Switch | Chemical | Duration | Safety |
|--------|----------|----------|--------|
| **pH- Dosing** | Acid | 5-300s | Minimum interval |
| **pH+ Dosing** | Base | 5-300s | Minimum interval |
| **Chlorine Dosing** | Chlorine | 5-300s | Overdose protection |
| **Flocculant** | Filter aid | 5-300s | With pump sync |

#### Maintenance & Special Outputs

| Switch | Function | Usage |
|--------|----------|-------|
| **Backwash** | Filter cleaning | Automatic/Manual |
| **Backwash Rinse** | Rinsing | After backwash |
| **Cover** | Pool cover | Open/Close/Stop |
| **PV Surplus** | Solar usage | With speed control |

#### Extension Relays (EXT1-EXT8, EXT2-EXT8)

Additional outputs for custom devices:
- `switch.violet_ext1_1` through `switch.violet_ext1_8`
- `switch.violet_ext2_1` through `switch.violet_ext2_8`

Configurable for any purpose.

#### DMX Scenes (SCENE 1-12)

Predefined lighting scenarios:
- `switch.violet_dmx_scene1` through `switch.violet_dmx_scene12`

Activate scenes individually or via service for sequences.

---

## 🌡️ Climate Controls

Special entities for heater and solar with temperature control:

### Heater (climate.violet_heater)

**HVAC Modes:**
- `off` - Off
- `heat` - Heating
- `auto` - Automatic

**Current Temperature:** Pool temperature
**Setpoint:** Enter target temperature (e.g. 28°C)

**Example: Heat to 28°C**
```yaml
service: climate.set_temperature
target:
  entity_id: climate.violet_heater
data:
  temperature: 28
  hvac_mode: heat
```

### Solar (climate.violet_solar)

**HVAC Modes:**
- `off` - Off
- `heat` - Solar heating
- `auto` - Automatic

**Special feature:** Only active when collector > pool water

**Example: Solar automatic at 30°C**
```yaml
service: climate.set_temperature
target:
  entity_id: climate.violet_solar
data:
  temperature: 30
  hvac_mode: auto
```

---

## 📱 Home Assistant Integration

### Lovelace Dashboard

A pre-built dashboard is included:
- File: `Dashboard/pool-dashboard.yaml`
- Copy to `/config/`
- Import in HA → Settings → Dashboards

**The dashboard contains:**
- 🌡️ Current temperatures
- 📊 Water chemistry monitors
- 🎚️ Quick access to devices
- 📈 Statistics and trends

### Creating a Custom Dashboard

```yaml
title: My Pool Dashboard
views:
  - title: Overview
    cards:
      - type: glance
        title: Current Values
        entities:
          - sensor.violet_pool_temperature
          - sensor.violet_pool_ph_value
          - sensor.violet_pool_chlorine_level

      - type: entities
        title: Controls
        entities:
          - switch.violet_pump
          - switch.violet_heater
          - switch.violet_solar

      - type: thermostat
        entity: climate.violet_heater
```

### Creating Automations

**Simple Automation: Activate heater when temperature is too low**

```yaml
automation:
  - alias: "Pool too cold - Heating"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_temperature
        below: 25
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 27
          hvac_mode: heat
      - service: notify.notify
        data:
          message: "Pool is too cold, heater is being activated"
```

**Complex Automation: Smart Dosing**

```yaml
automation:
  - alias: "Automatic pH Management"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_ph_value
        above: 7.6
    action:
      - service: violet_pool_controller.smart_dosing
        target:
          entity_id: switch.ph_dosing_minus
        data:
          dosing_type: "pH-"
          action: manual_dose
          duration: 20
      - service: notify.notify
        data:
          message: "pH too high, pH- is being dosed"
```

---

## 🚨 Error Handling & Troubleshooting

### Common Errors and Solutions

#### ❌ "Connection to controller failed"

**Causes:**
- Controller not reachable on the network
- Wrong IP address
- Firewall blocking
- Controller is turned off

**Solutions:**
```bash
# 1. Ping test
ping 192.168.1.100

# 2. Direct HTTP test
curl http://192.168.1.100/getReadings?ALL

# 3. Test in HA
Settings → Devices & Services → Violet → ⋮ → Reload
```

#### ❌ "SSL Certificate Error"

**Symptom:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
1. Settings → Devices & Services → Violet → ⋮ → Options
2. Disable "Verify SSL Certificate"
3. ⚠️ Only for self-signed certificates!

#### ❌ "Timeout - Request takes too long"

**Causes:**
- Network overloaded
- Controller not responsive
- Too many sensors queried

**Solutions:**
1. Increase polling interval (e.g. 45 seconds)
2. Enable fewer sensors
3. Check network stability

#### ❌ "Entities are constantly 'unavailable'"

**Causes:**
- Coordinator error
- Polling interval too short
- Sensor problem on the controller

**Solutions:**
```yaml
# Reload integration
service: homeassistant.reload_config_entry
target:
  device_id: <device_id>

# Or manually:
# Settings → Devices & Services → Violet → ⋮ → Reload
```

### Enabling Debug Mode

For more detailed logs:

1. Edit `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.violet_pool_controller: debug
```

2. Restart Home Assistant

3. Check logs:
```bash
tail -f /config/home-assistant.log | grep violet_pool_controller
```

### Checking Logs

Home Assistant → Settings → System → Logs

Important messages:
- `INFO` - Information (Normal)
- `WARNING` - Warnings (Pay attention)
- `ERROR` - Errors (Investigate!)

### Error Codes from the Controller

The controller sends error codes. These can be found in `error_codes.py`:

**Common errors:**
- `101` - Sensor error (pH, ORP, etc.)
- `205` - Pressure too high
- `301` - Water level too low
- `401` - Temperature sensor defective

Use `sensor.violet_system_error_codes` for monitoring.

### Support & Help

- 🐛 **GitHub Issues**: [xerolux/violet-hass/issues](https://github.com/xerolux/violet-hass/issues)
- 💬 **Discord**: [Community Server](https://discord.gg/Qa5fW2R)
- 📧 **Email**: git@xerolux.de
- 📖 **Wiki**: [Complete Documentation](https://github.com/xerolux/violet-hass/wiki)

---

## 📈 Updates & Upgrades

### Automatic Updates with HACS

HACS automatically checks for updates:

1. HACS → Integrations
2. Find "Violet Pool Controller"
3. If update available: 🔵 dot next to name
4. Click "Update"
5. Restart Home Assistant

### Manual Updates

```bash
cd /config/custom_components/violet_pool_controller
git pull origin main
# Restart Home Assistant
```

### Reading the Changelog

Before each update you should check the changelog:
- 📝 [CHANGELOG.md](docs/CHANGELOG.md)
- 🚨 Possible breaking changes?
- ✨ New features?
- 🐛 Fixed bugs?

### Checking Version

**Current version in HA:**
1. Settings → Devices & Services → Violet
2. Select "Violet Pool Controller"
3. Version displayed in the top right

**Or in the terminal:**
```bash
grep '"version"' /config/custom_components/violet_pool_controller/manifest.json
```

### Backup Before Update

Always create a backup:
```bash
# Home Assistant Backup
Settings → System → Backups → Create

# Or manually
cp -r /config/custom_components/violet_pool_controller /backup/
```

### Troubleshooting After Update

If problems occur after an update:

1. **Completely restart Home Assistant** (not just reload)
   - Settings → System → System Controls → Restart

2. **Reload integration**
   - Settings → Devices & Services → Violet → ⋮ → Reload

3. **If problems persist, revert to the old version**
   ```bash
   cd /config/custom_components/violet_pool_controller
   git checkout <version>
   # Example: git checkout v0.2.0
   ```

---

## 🗑️ Uninstallation

### Complete Removal

#### Step 1: Remove Integration from Home Assistant

1. Settings → Devices & Services
2. Select "Violet Pool Controller"
3. ⋮ (Menu) → "Remove"
4. Accept confirmation

#### Step 2: Delete Files

```bash
# Delete integration directory
rm -rf /config/custom_components/violet_pool_controller
```

#### Step 3: Remove HACS Entry (Optional)

1. HACS → Integrations
2. Select "Violet Pool Controller"
3. ⋮ → "Remove Repository"

#### Step 4: Restart Home Assistant

```bash
# Web UI: ⋮ → System Controls → Restart
# Docker: docker restart homeassistant
```

### Preserving Data

If you want to reuse the configuration:

1. **Export automations:**
   - Settings → Automations
   - Open each automation
   - Copy YAML

2. **Export dashboards:**
   - Settings → Dashboards
   - Export dashboard YAML

3. **Save entity aliases:**
   ```bash
   # Backup Home Assistant files
   cp -r /config/.storage /backup/
   ```

### Migration to a New System

If you are moving to a new Home Assistant system:

1. **Create backup** (as above)
2. **Start new system**
3. **Install integration**
4. **Restore backup** (if needed)
5. **Recreate automations/dashboards** (use saved YAMLs)

---

## ❓ FAQ & Frequently Asked Questions

### General

**Q: Do I need a cloud connection?**
A: No! The addon is 100% local. No internet, no cloud service required.

**Q: Can I control multiple controllers?**
A: Yes! The integration supports multi-controller. Each gets unique entities.

**Q: Is the addon secure?**
A: Yes! It uses local network communication with optional SSL/TLS and input sanitization.

**Q: What Home Assistant version is required at minimum?**
A: Home Assistant 2025.12.0 or newer (older versions are not supported).

### Installation & Setup

**Q: How do I find my controller's IP address?**
A:
1. Open your router admin interface (usually 192.168.1.1)
2. Show connected devices
3. Search for "Violet" or similar
4. Note the IP

Or in the terminal:
```bash
ping violet.local    # If mDNS is enabled
```

**Q: Can I connect to the controller via HTTPS?**
A: Yes! Enable "Use SSL" in the options. SSL certificate validation can be disabled.

**Q: Does this work with self-signed certificates?**
A: Yes, but disable "Verify SSL Certificate" in the options (only for trusted networks!).

### Features & Operation

**Q: What does "Automatic" mean compared to "Manual"?**
A:
- **Automatic**: Controller regulates independently (e.g. based on temperatures)
- **Manual**: You control directly, auto rules are ignored

**Q: Can I adjust the pump speed?**
A: Yes! The pump has 3 speed levels (1, 2, 3). Use the `control_pump` service to select them.

**Q: How do I dose chemicals safely?**
A: Use the `smart_dosing` service:
- Small amounts (15-30 seconds)
- Observe intervals between dosing
- Always check sensor values

**Q: Can I save scenes?**
A: Yes! With automation you can save switch combinations:
```yaml
scene.create
entities:
  switch.violet_pump: "on"
  switch.violet_heater: "off"
  climate.violet_heater: { temperature: 28 }
```

### Troubleshooting

**Q: My sensors show "unavailable" - why?**
A: Coordinator error (usually a connection issue). Solutions:
1. Increase polling interval (30-45s)
2. Reload integration
3. Enable fewer sensors

**Q: The controller responds very slowly?**
A:
1. Check network utilization
2. Increase polling interval
3. Check controller CPU load
4. Too many sensors?

**Q: Why are some sensors not showing?**
A:
1. Not enabled in the setup flow?
2. Controller doesn't have this sensor
3. Feature is not configured
4. Solution: Reload integration

### Performance & Optimization

**Q: What polling interval should I use?**
A:
- **20-30s**: Standard (good balance)
- **10-15s**: For fast reactions (higher load)
- **45-60s**: For less critical pools

**Q: Creating new automations all the time is boring!**
A: Use Blueprints! These are pre-made automation templates:
- Settings → Automations → Blueprints
- "Import Blueprint" → Enter repository URL

**Q: Can I reduce logging?**
A: Yes! In Home Assistant `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.violet_pool_controller: warning  # Warnings only
```

### Services & Automations

**Q: How do I call a service?**
A: Several options:

1. **Developer Tools:**
   - Settings → Developer Tools → Services
   - Select service, fill in, test

2. **YAML in automation:**
   ```yaml
   service: violet_pool_controller.control_pump
   target:
     entity_id: switch.violet_pump
   data:
     action: speed_control
     speed: 2
   ```

3. **UI Automation Builder:**
   - Settings → Automations → Create

**Q: Can I trigger an automation on a schedule?**
A: Yes!
```yaml
trigger:
  - platform: time
    at: "08:00:00"  # Every morning at 8:00 AM
action:
  - service: switch.turn_on
    target:
      entity_id: switch.violet_pump
```

**Q: Can I react to weather forecasts?**
A: Yes! With the Weather integration:
```yaml
trigger:
  - platform: template
    value_template: "{{ state_attr('weather.my_weather', 'precipitation') > 5 }}"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.violet_pool_cover
```

---

## 🔒 Security & Best Practices

### Security Basics

#### 1. Network Security

✅ **Recommended:**
- Controller in private network
- Firewall protects access
- Local communication only
- Enable SSL/TLS

❌ **Not recommended:**
- Expose controller to the internet
- Use default password
- On public WiFi

#### 2. Authentication

If your controller requires a password:
- Use a **strong password** (min. 12 characters)
- Use **Home Assistant .env file**:

```bash
# /config/.env
VIOLET_PASSWORD=YourStrongPassword
```

```yaml
# In integration configuration
password: !env_var VIOLET_PASSWORD
```

#### 3. Input Validation

The integration automatically validates:
- XSS protection (HTML escaping)
- SQL injection protection
- Command injection protection
- Path traversal protection

### Best Practices

#### 1. Regular Backups

```bash
# Weekly backup
Home Assistant → Settings → System → Backups → Create
```

#### 2. Monitor Logs

Regularly check for:
- Unexpected errors
- Communication issues
- Unusual states

#### 3. Calibrate Sensors

Especially pH and ORP should be calibrated regularly:
- **Monthly**: pH and ORP
- **Weekly**: Chlorine (with test kit)
- **2x daily**: Visual inspection

#### 4. Test Automations

New automations should:
1. Be tested with short duration
2. Be tested with notifications
3. Then go into production

**Example: Test automation**
```yaml
automation:
  - alias: "TEST - Pump for 10s"
    trigger:
      - platform: state
        entity_id: input_boolean.test_pump
        to: "on"
    action:
      - service: violet_pool_controller.control_pump
        target:
          entity_id: switch.violet_pump
        data:
          action: speed_control
          speed: 1
          duration: 10
      - service: notify.notify
        data:
          message: "TEST: Pump starting for 10s"
```

#### 5. Schedule Maintenance

Once per quarter:
- **Hardware check**: Inspect sensors
- **Software update**: Update addon
- **Backup test**: Test backup restore
- **Config review**: Review automations

#### 6. Set Up Monitoring

Monitor critical metrics:
- Controller error codes
- Sensor availability
- Connection stability

```yaml
automation:
  - alias: "Error Alert"
    trigger:
      - platform: state
        entity_id: sensor.violet_system_error_codes
    condition:
      - condition: template
        value_template: "{{ states('sensor.violet_system_error_codes') != '[]' }}"
    action:
      - service: notify.notify
        data:
          title: "⚠️ Pool Error!"
          message: "{{ states('sensor.violet_system_error_codes') }}"
```

### SSL/TLS Configuration (Advanced)

#### With Self-Signed Certificate

```yaml
# Integration settings
Host: 192.168.1.100
Port: 8443
Use SSL: ☑
Verify SSL Certificate: ☐  # WARNING: Insecure!
```

**More secure: Import certificate into Home Assistant**

```bash
# Export certificate from controller
openssl s_client -connect 192.168.1.100:8443 -showcerts

# Import into Home Assistant
# (Advanced configuration required)
```

### Troubleshooting Security Issues

#### Fixing SSL Errors

```
SSL: CERTIFICATE_VERIFY_FAILED
```

Possible solutions:
1. Validate certificate:
   ```bash
   openssl s_client -connect 192.168.1.100:8443
   ```

2. Enable debugging:
   ```yaml
   logger:
     logs:
       aiohttp: debug
   ```

3. As a last resort, disable SSL validation (⚠️ only temporarily)

---

## 📚 Additional Resources

- **Official GitHub**: https://github.com/xerolux/violet-hass
- **Home Assistant Docs**: https://www.home-assistant.io/
- **HACS**: https://hacs.xyz/
- **Violet Controller**: https://www.pooldigital.de/
- **Community Forum**: https://community.home-assistant.io/

---

## 📝 Version History

| Version | Date | Highlights |
|---------|------|-----------|
| **1.0.1** | 2025-12-02 | Bug fixes, type errors resolved |
| **1.0.0** | 2025-11-20 | 3-state switch support, 147 sensors |
| **0.1.0** | 2024-XX-XX | Initial release |

---

**Made with ❤️ for the Home Assistant & Pool Community**

*Transform your pool into a smart pool - because life's too short for manual pool maintenance!* 🏊‍♀️🤖
