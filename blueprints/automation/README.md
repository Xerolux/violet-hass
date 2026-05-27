# 🔧 Violet Pool Controller Blueprints - Installation & Setup

## 📋 Overview
The blueprints provide pre-built automations for the Violet Pool Controller integration:

- **🌡️ Temperature Control**: Smart heater and solar control
- **🧪 pH Control**: Automatic pH value correction with dosing
- **🏊 Cover Control**: Weather-based cover automation
- **🔄 Backwash Control**: Automatic filter cleaning

## 📥 Blueprint Installation

### Method 1: Directly via Home Assistant UI (Recommended)

1. **Import Blueprint:**
   ```
   Settings → Automations & Scenes → Blueprints → Import Blueprint
   ```

2. **Enter URLs:**
   ```
   Temperature: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_temperature_control.yaml
   pH Control: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_ph_control.yaml
   Cover: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_cover_control.yaml
   Backwash: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_backwash_control.yaml
   ```

### Method 2: Manual Installation

1. **Create folder:**
   ```bash
   mkdir -p config/blueprints/automation/violet_pool_controller/
   ```

2. **Copy files:**
   ```bash
   # In Home Assistant config directory
   cd config/blueprints/automation/violet_pool_controller/
   
   # Download blueprints
   wget https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_temperature_control.yaml
   wget https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_ph_control.yaml
   wget https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_cover_control.yaml
   wget https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_backwash_control.yaml
   ```

3. **Restart Home Assistant**

## 🌡️ Temperature Control Blueprint

### Required Entities:
- ✅ **Pool Temperature Sensor** (sensor.violet_onewire1_value)
- ✅ **Pool Heater** (climate.violet_heater)
- 🔧 **Solar Absorber** (climate.violet_solar) - Optional
- 🔧 **Outside Temperature Sensor** - Optional
- 🔧 **Solar Power Sensor** - Optional

### Setup Steps:

1. **Create Blueprint:**
   ```
   Settings → Automations & Scenes → Blueprints
   → "Violet Pool - Smart Temperature Control" → Use This Blueprint
   ```

2. **Configuration:**
   ```yaml
   Pool Temperature Sensor: sensor.violet_onewire1_value
   Pool Heater: climate.violet_heater
   Solar Absorber: climate.violet_solar        # Optional
   Target Temperature Day: 26°C
   Target Temperature Night: 24°C
   Day Start Time: 07:00
   Night Start Time: 22:00
   Energy Saving Mode: On
   ```

## 🧪 pH Control Blueprint

### Required Helpers:
1. **Input Number for Dosing Counter:**
   ```
   Settings → Devices & Services → Helpers → Create Helper → Number
   Name: Pool pH Dosing Counter
   Entity ID: input_number.pool_ph_dosing_counter
   Min: 0, Max: 50, Step: 1, Initial: 0
   ```

### Setup Steps:
```yaml
pH Sensor: sensor.violet_ph_value
pH Setpoint: number.violet_ph_setpoint
pH- Dosing: switch.violet_dos_4_phm
pH+ Dosing: switch.violet_dos_5_php
pH Tolerance: ±0.2
Max. Dosing per Day: 10
```

## 🏊 Cover Control Blueprint

### Required Entities:
- ✅ **Pool Cover** (cover.violet_cover)
- ✅ **Pool Temperature Sensor** (sensor.violet_onewire1_value)
- ✅ **Outside Temperature Sensor** (sensor.openweather_temperature)
- ✅ **Weather Entity** (weather.openweathermap)
- 🔧 **Pump Entity** (switch.violet_pump) - Optional

### Setup Steps:

1. **Create Blueprint:**
   ```yaml
   Pool Cover: cover.violet_cover
   Pool Temperature Sensor: sensor.violet_onewire1_value
   Outside Temperature Sensor: sensor.openweather_temperature
   Weather Entity: weather.openweathermap
   ```

2. **Time Control:**
   ```yaml
   Auto Open Time: 08:00
   Weekend Open Time: 10:00
   Auto Close Time: 22:00
   ```

3. **Weather Control:**
   ```yaml
   Weather-Based Control: On
   Rain Threshold: 70%
   Wind Speed Threshold: 25 km/h
   ```

4. **Temperature Control:**
   ```yaml
   Temperature-Based Control: On
   Minimum Outside Temperature: 5°C
   Max Temperature Difference: 15°C
   ```

### Features:
- ✅ **Automatic Open/Close** based on schedule
- ✅ **Weather Protection** during rain/wind/storms
- ✅ **Temperature Protection** at low temperatures
- ✅ **Pump Interlock** (no closing while pump is running)
- ✅ **Weekend Mode** (later opening)
- ✅ **Manual Override** with pause function

## 🔄 Backwash Control Blueprint

### Required Entities:
- ✅ **Backwash Switch** (switch.violet_backwash)
- ✅ **Pump Switch** (switch.violet_pump)
- 🔧 **Rinse Switch** (switch.violet_backwashrinse) - Optional
- 🔧 **Filter Pressure Sensor** (sensor.violet_adc1_value) - Optional

### Required Helpers:
1. **Input Datetime for last backwash:**
   ```
   Settings → Helpers → Create Helper → Date and/or time
   Name: Pool Last Backwash
   Entity ID: input_datetime.pool_last_backwash
   Has date: ✓, Has time: ✓
   ```

2. **Input Number for pump runtime (optional):**
   ```
   Name: Pool Pump Runtime Hours
   Entity ID: input_number.pool_pump_runtime_hours
   Min: 0, Max: 500, Step: 0.1, Unit: h
   ```

### Setup Steps:

1. **Basic Configuration:**
   ```yaml
   Backwash Switch: switch.violet_backwash
   Pump Switch: switch.violet_pump
   Rinse Switch: switch.violet_backwashrinse
   Filter Pressure Sensor: sensor.violet_adc1_value
   ```

2. **Automation:**
   ```yaml
   Pressure-Based Backwash: On
   Maximum Filter Pressure: 1.5 bar
   Scheduled Backwash: On
   Backwash Interval: 7 days
   Backwash Time: 03:00
   ```

3. **Parameters:**
   ```yaml
   Backwash Duration: 120s
   Rinse Duration: 30s
   Pump Stop Before Backwash: 30s
   Pump Start After Backwash: 60s
   ```

### Features:
- ✅ **Pressure-Based Trigger** at high filter pressure
- ✅ **Schedule-Based Backwash** at intervals
- ✅ **Runtime-Based Trigger** after pump hours
- ✅ **Automatic Rinse Cycle**
- ✅ **Water Level Check** before backwash
- ✅ **Safe Pump Control** with wait times

## 📱 Setting Up Notifications

### Mobile App Notification:

1. **Find service:**
   ```
   Developer Tools → Services → Search: "notify"
   → notify.mobile_app_your_phone_name
   ```

2. **Enter in Blueprint:**
   ```
   Notification Service: notify.mobile_app_iphone
   ```

### Telegram/Discord/Slack:
```
notify.telegram_bot
notify.discord_webhook  
notify.slack_webhook
```

## 💡 Example Notifications

### Temperature Control:
- 🌅 "Pool Temperature: Day temperature set to 26°C"
- ☀️ "Solar Heating activated (1500W), target: 26°C"
- 🔥 "Pool Heater activated: 23.5°C → 26°C (Δ2.5°C)"

### pH Control:
- 🔻 "pH Correction: 7.6 → 7.2, pH-Minus dosed for 30s"
- ⚠️ "pH Dosing stopped: Max. 10 dosing cycles reached"

### Cover Control:
- 🌧️ "Weather Protection: Cover closed due to rain"
- 🌡️ "Temperature Protection: Outside 3°C, cover closed"

### Backwash:
- 🔄 "Automatic Backwash: Filter pressure 1.8 bar (Max: 1.5)"
- ✅ "Backwash completed: 120s Backwash + 30s Rinse"

## 🚨 Troubleshooting

### Blueprint not visible:
```bash
# Check logs:
tail -f config/home-assistant.log | grep blueprint

# File permissions:
chmod 644 config/blueprints/automation/violet_pool_controller/*.yaml

# Restart HA
```

### Entities not found:
- Integration correctly installed?
- Entities visible in Developer Tools?
- Feature enabled in integration?

### Notifications not working:
- Service name correct? (with notify. prefix)
- Mobile app installed and logged in?
- Test via Developer Tools → Services

### Automation not running:
- Trigger conditions met?
- Entities available (not "unavailable")?
- Mode: single - only one execution at a time

## 🔧 Customization

### Adding Custom Triggers:
```yaml
# Add to Blueprint YAML:
- platform: state
  entity_id: input_boolean.my_custom_trigger
  to: 'on'
  id: custom_trigger
```

### Adjusting Times:
```yaml
# Different check intervals:
- platform: time_pattern
  minutes: /15  # Every 15 minutes instead of 30
```

### Additional Conditions:
```yaml
# e.g. only when someone is home:
- condition: state
  entity_id: person.homeowner
  state: 'home'
```

The blueprints are modular and can be customized individually!
