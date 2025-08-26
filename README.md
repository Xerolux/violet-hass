[![GitHub Release][releases-shield]][releases]
[![downloads][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacs-badge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymeacoffee-badge]][buymeacoffee]
Use my Tesla referral link: [Referral Link](https://ts.la/sebastian564489)

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

# 🏊 Violet Pool Controller for Home Assistant

Transform your pool into a smart pool! This comprehensive Home Assistant integration provides complete control and monitoring of your **Violet Pool Controller**, bringing intelligent pool automation directly to your smart home ecosystem.

![Violet Home Assistant Integration][logo]

## ✨ What Makes This Special?

🎯 **Complete Pool Automation** - Monitor and control every aspect of your pool  
🌡️ **Smart Climate Control** - Intelligent heating and solar management  
🧪 **Chemical Balance** - Automated pH and chlorine monitoring/dosing  
🏊 **Cover Management** - Weather-aware automatic cover control  
💧 **Filter Maintenance** - Automatic backwash scheduling  
📱 **Mobile Ready** - Full control from anywhere via Home Assistant app  
🔧 **No Cloud Required** - 100% local control and privacy  

## 📊 Features Overview

### 🔍 **Comprehensive Monitoring**
- **Water Chemistry:** pH, Redox (ORP), Chlorine levels with trend tracking
- **Temperature Sensors:** Pool water, ambient air, solar collector temperatures  
- **System Status:** Pump operation, heater status, filter pressure, water levels
- **Equipment Health:** Runtime tracking, error detection, maintenance alerts

### 🎛️ **Intelligent Controls**
- **Climate Management:** Dual-zone heating (heater + solar) with scheduling
- **Chemical Dosing:** Automated pH+/pH- and chlorine dosing with safety limits
- **Pump Control:** Variable speed control, energy-efficient scheduling
- **Lighting:** Full RGB/DMX lighting control with scenes and automation
- **Cover Operation:** Weather-responsive automatic cover management
- **Filtration:** Smart backwash cycles based on pressure and runtime

### 🤖 **Smart Automation Features**
- **Energy Optimization:** PV-surplus mode for solar-powered heating
- **Weather Integration:** Automatic responses to rain, wind, temperature
- **Maintenance Scheduling:** Automated backwash, water testing, equipment cycles
- **Safety Systems:** Emergency shutdowns, overflow protection, chemical limits
- **Custom Scenes:** Pool party mode, eco mode, winter mode, vacation mode

## 📱 Screenshots

<!-- Coming Soon: Pool Dashboard, Climate Control, Chemical Management -->
*Screenshots will be added in the next release*

## 📦 Installation

### 🚀 HACS Installation (Recommended)

The integration is available through HACS (Home Assistant Community Store):

1. **Install HACS** if you haven't already ([HACS Installation Guide](https://hacs.xyz/docs/setup/download))
2. **Open HACS** in your Home Assistant interface
3. **Add Custom Repository:**
   - Click the three dots (⋮) in the top-right corner
   - Select "Custom repositories"
   - Add: `https://github.com/xerolux/violet-hass`
   - Category: "Integration"
   - Click "Add"
4. **Install Integration:**
   - Search for "Violet Pool Controller"
   - Click "Download"
   - Restart Home Assistant

### 🔧 Manual Installation (Advanced Users)

For developers or advanced users who prefer manual installation:

```bash
# Method 1: Git Clone
cd /config/custom_components/
git clone https://github.com/xerolux/violet-hass.git violet_pool_controller

# Method 2: Download and Extract
wget https://github.com/xerolux/violet-hass/archive/main.zip
unzip main.zip
mv violet-hass-main/custom_components/violet_pool_controller /config/custom_components/
```

**Then restart Home Assistant**

## ⚙️ Configuration

Configuration is done entirely through the Home Assistant UI - no YAML editing required!

### 🚀 Quick Setup

1. **Add Integration:**
   ```
   Settings → Devices & Services → Add Integration → "Violet Pool Controller"
   ```

2. **Connection Settings:**
   ```yaml
   Host: 192.168.1.100          # Your controller's IP
   Username: admin               # If authentication enabled
   Password: your-password       # If authentication enabled
   Use SSL: ☐/☑                # Check if using HTTPS
   Device Name: Pool Controller  # Friendly name
   Polling Interval: 30s         # How often to update (10-300s)
   ```

3. **Pool Configuration:**
   ```yaml
   Pool Size: 50 m³             # Your pool volume
   Pool Type: Outdoor Pool      # Indoor/Outdoor/Whirlpool/etc.
   Disinfection: Chlorine       # Your sanitization method
   ```

4. **Feature Selection:**
   Select which components you want to enable:
   - ✅ Heating Control
   - ✅ Solar Management  
   - ✅ pH Control
   - ✅ Chlorine Control
   - ✅ Cover Control
   - ✅ Backwash System
   - ✅ LED Lighting
   - ✅ PV Surplus Mode
   - ☐ Extension Outputs (if applicable)
   - ☐ Digital Inputs (if applicable)

### 🔧 Advanced Configuration

Access advanced options through:
```
Settings → Devices & Services → Violet Pool Controller → Configure
```

**Performance Tuning:**
- **Polling Interval:** 10-60s (balance between responsiveness and system load)
- **Timeout Duration:** 5-30s (increase for slower networks)
- **Retry Attempts:** 1-5 (increase for unstable connections)

**Feature Management:**
- Enable/disable specific features as needed
- Customize entity names and icons
- Set up notification preferences

## 🧩 Available Entities

The integration creates entities dynamically based on your controller's capabilities and selected features:

### 🌡️ **Climate Entities**
```yaml
climate.pool_heater          # Main pool heater control
climate.pool_solar           # Solar collector management  
```
**Features:** Temperature setting, mode control (heat/auto/off), scheduling integration

### 🔍 **Sensors**
```yaml
sensor.pool_temperature      # Current water temperature
sensor.pool_ph_value         # Current pH level (6.0-8.5)
sensor.pool_orp_value        # Redox potential (mV)
sensor.pool_chlorine_level   # Free chlorine (mg/l)
sensor.filter_pressure       # Filter system pressure
sensor.water_level          # Pool water level
sensor.outside_temperature   # Ambient air temperature
sensor.solar_collector_temp  # Solar heating temperature
# ... and many more based on your setup
```

### 💡 **Switches**
```yaml
switch.pool_pump            # Main filtration pump
switch.pool_heater          # Pool heater on/off
switch.pool_solar           # Solar circulation  
switch.pool_lighting        # Pool lights
switch.backwash             # Filter backwash cycle
switch.ph_dosing_minus      # pH- dosing pump
switch.ph_dosing_plus       # pH+ dosing pump  
switch.chlorine_dosing      # Chlorine dosing system
switch.pv_surplus_mode      # Solar excess utilization
# ... plus any configured extension outputs
```

### 🛡️ **Binary Sensors**
```yaml
binary_sensor.pump_running     # Pump operation status
binary_sensor.heater_active    # Heater operation status  
binary_sensor.cover_closed     # Cover position sensor
binary_sensor.maintenance_mode # Maintenance mode indicator
# ... plus digital input sensors if configured
```

### 🏊 **Cover**
```yaml
cover.pool_cover            # Automatic pool cover control
```
**Features:** Open/close/stop, position feedback, weather integration

### 🔢 **Number Entities (Setpoints)**
```yaml
number.ph_setpoint          # Target pH value (6.8-7.8)
number.orp_setpoint         # Target redox value (600-800 mV)  
number.chlorine_setpoint    # Target chlorine level (0.2-2.0 mg/l)
```

## 🔧 Custom Services

The integration provides specialized services for advanced automation:

### 🎯 **Core Control Services**

#### `violet_pool_controller.turn_auto`
Switch any controllable device to automatic mode:
```yaml
service: violet_pool_controller.turn_auto
target:
  entity_id: switch.pool_pump
data:
  auto_delay: 30  # Optional: delay in seconds
```

#### `violet_pool_controller.set_pv_surplus`
Activate solar energy surplus mode:
```yaml
service: violet_pool_controller.set_pv_surplus  
target:
  entity_id: switch.pv_surplus_mode
data:
  pump_speed: 2   # Speed level 1-3
```

### 🧪 **Chemical Management Services**

#### `violet_pool_controller.manual_dosing`
Trigger manual chemical dosing:
```yaml
service: violet_pool_controller.manual_dosing
target:
  entity_id: switch.ph_dosing_minus
data:
  duration_seconds: 30  # Dosing duration
```

#### `violet_pool_controller.set_ph_target`
Set pH target value:
```yaml
service: violet_pool_controller.set_ph_target
target:
  entity_id: number.ph_setpoint
data:
  target_value: 7.2
```

#### `violet_pool_controller.set_chlorine_target`
Set chlorine target level:
```yaml
service: violet_pool_controller.set_chlorine_target
target:
  entity_id: number.chlorine_setpoint  
data:
  target_value: 1.0  # mg/l
```

### 🔄 **Maintenance Services**

#### `violet_pool_controller.trigger_backwash`
Start filter backwash cycle:
```yaml
service: violet_pool_controller.trigger_backwash
target:
  entity_id: switch.backwash
data:
  duration: 120  # Optional: duration in seconds
```

#### `violet_pool_controller.start_water_analysis`
Initiate comprehensive water testing:
```yaml
service: violet_pool_controller.start_water_analysis
target:
  entity_id: sensor.pool_ph_value  # Any pool entity for device identification
```

#### `violet_pool_controller.set_maintenance_mode`
Enable/disable maintenance mode:
```yaml
service: violet_pool_controller.set_maintenance_mode
target:
  entity_id: binary_sensor.maintenance_mode
data:
  enable: true  # true to enable, false to disable
```

## 🤖 Automation Blueprints

Get started quickly with our pre-built automation blueprints:

### 📥 **Installation**
Import blueprints directly in Home Assistant:
```
Settings → Automations & Scenes → Blueprints → Import Blueprint
```

**Blueprint URLs:**
```
Temperature Control: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_temperature_control.yaml
pH Management: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_ph_control.yaml
Cover Control: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_cover_control.yaml
Backwash Automation: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_backwash_control.yaml
```

### 🌡️ **Smart Temperature Control**
- **Day/Night Scheduling:** Different temperatures for active and quiet hours
- **Solar Priority:** Automatically use solar heating when available
- **Weather Integration:** Adjust heating based on weather forecasts
- **Energy Optimization:** PV-surplus mode for maximum efficiency

### 🧪 **Intelligent pH Management**
- **Automatic Dosing:** Maintain perfect pH levels (6.8-7.8) automatically
- **Safety Limits:** Maximum dosing limits to prevent over-treatment
- **Pump Integration:** Only dose when filtration is active
- **Smart Scheduling:** Avoid dosing during high-usage periods

### 🏊 **Weather-Aware Cover Control**
- **Time-Based Operation:** Automatic open/close based on schedule
- **Weather Protection:** Close automatically for rain, wind, storms
- **Temperature Management:** Close when too cold to retain heat
- **Pump Integration:** Safety interlocks prevent conflicts

### 🔄 **Predictive Backwash System**
- **Pressure-Based:** Automatic backwash when filter pressure is high
- **Time-Based:** Scheduled backwash cycles for optimal filtration
- **Runtime-Based:** Backwash after specific pump operating hours
- **Safety Features:** Water level checks and pump sequencing

### 🛠️ **Required Helpers for Blueprints**
Some blueprints need helper entities - create these first:

```yaml
# For pH Control Blueprint
input_number.pool_ph_dosing_counter:
  min: 0
  max: 50
  step: 1
  initial: 0
  unit_of_measurement: "doses"

# For Backwash Blueprint  
input_datetime.pool_last_backwash:
  has_date: true
  has_time: true

input_number.pool_pump_runtime_hours:
  min: 0
  max: 500
  step: 0.1
  unit_of_measurement: "h"
```

Create these in: `Settings → Devices & Services → Helpers → Create Helper`

## 📊 Dashboard Examples

### 🎛️ **Pool Control Dashboard**
```yaml
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.pool_heater
    name: Pool Temperature
  - type: entities
    entities:
      - entity: sensor.pool_ph_value
        name: pH Level
      - entity: sensor.pool_chlorine_level  
        name: Chlorine
      - entity: sensor.filter_pressure
        name: Filter Pressure
  - type: horizontal-stack
    cards:
      - type: button
        entity: switch.pool_pump
        name: Pump
      - type: button  
        entity: switch.pool_lighting
        name: Lights
      - type: button
        entity: cover.pool_cover
        name: Cover
```

### 📈 **Chemical Monitoring Card**
```yaml
type: history-graph
entities:
  - entity: sensor.pool_ph_value
    name: pH Level
  - entity: sensor.pool_chlorine_level
    name: Chlorine (mg/l)
  - entity: sensor.pool_orp_value
    name: Redox (mV)
hours_to_show: 168  # 1 week
refresh_interval: 30
```

## 🚨 Troubleshooting

### ⚡ **Quick Fixes**

**Connection Issues:**
```bash
# Test connectivity
ping 192.168.1.100

# Check HA logs
tail -f /config/home-assistant.log | grep violet_pool_controller

# Verify controller API
curl http://192.168.1.100/getReadings?ALL
```

**Common Solutions:**
- ✅ **Wrong IP Address:** Verify controller IP in router settings
- ✅ **SSL Mismatch:** Ensure "Use SSL" matches controller configuration  
- ✅ **Firewall Blocking:** Temporarily disable firewall for testing
- ✅ **Outdated Firmware:** Update controller firmware via PoolDigital
- ✅ **Network Issues:** Check VLAN/subnet configuration

### 🔍 **Detailed Diagnostics**

**Enable Debug Logging:**
```yaml
# Add to configuration.yaml
logger:
  default: warning
  logs:
    custom_components.violet_pool_controller: debug
```

**Entity Issues:**
- **Missing Entities:** Check feature selection in integration settings
- **Not Updating:** Verify polling interval and controller responsiveness
- **Wrong Values:** Confirm sensor calibration on controller

**Performance Issues:**
- **Slow Updates:** Increase polling interval (30-60 seconds)
- **High CPU Usage:** Reduce number of enabled features
- **Memory Issues:** Check Home Assistant system resources

### 📞 **Getting Help**

1. **Check Logs First:** Most issues show up in Home Assistant logs
2. **Update Everything:** Ensure latest versions of HA and integration
3. **Test Basic Connectivity:** Verify network connection to controller
4. **GitHub Issues:** Report bugs with full details and logs
5. **Community Forum:** Ask questions and share experiences
6. **PoolDigital Forum:** Hardware-specific questions

## 🎓 **Advanced Usage**

### 🔗 **Integration with Other Systems**

**Grafana Monitoring:**
```yaml
# Long-term data storage and analysis
# Connect HA database to Grafana for professional dashboards
```

**Node-RED Automation:**
```yaml
# Complex automation flows
# Advanced conditional logic and external service integration  
```

**Telegram/Discord Notifications:**
```yaml
# Pool status alerts and maintenance reminders
# Custom notification rules and escalation
```

### 🏗️ **Custom Development**

**REST API Integration:**
```python
# Access controller data directly
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get('http://192.168.1.100/getReadings?ALL') as resp:
        data = await resp.json()
```

**MQTT Bridge:**
```yaml
# Publish pool data to MQTT for integration with other systems
# Useful for industrial monitoring or custom applications
```

## 💝 Supporting This Project

This integration is developed and maintained in my free time. If it adds value to your smart pool setup, consider showing some love:

[![GitHub Sponsor](https://img.shields.io/github/sponsors/xerolux?logo=github&style=for-the-badge&color=blue)](https://github.com/sponsors/xerolux)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-xerolux-blue?logo=ko-fi&style=for-the-badge)](https://ko-fi.com/xerolux)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-xerolux-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://www.buymeacoffee.com/xerolux)

**Other Ways to Support:**
- ⭐ **Star this repository** on GitHub
- 🐛 **Report bugs** and suggest improvements
- 📢 **Share** with other pool owners
- 📝 **Contribute** code or documentation
- 💬 **Help others** in the community forums

## 🤝 Contributing

We welcome contributions from the community! Whether it's:

- 🐛 **Bug fixes** and improvements
- ✨ **New features** and enhancements  
- 📚 **Documentation** updates
- 🧪 **Testing** on different controller models
- 🌍 **Translations** to other languages

**Getting Started:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)  
6. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🏊 About the Violet Pool Controller

![Violet Pool Controller][pbuy]

The **VIOLET Pool Controller** by [PoolDigital GmbH & Co. KG](https://www.pooldigital.de/) is a premium, German-engineered smart pool automation system. It's designed for pool owners who want professional-grade control and monitoring without the complexity.

**Key Capabilities:**
- 🔧 **Complete Pool Management:** Filtration, heating, lighting, chemical dosing
- 📱 **Remote Access:** Control from anywhere via web interface or API
- 🌐 **Smart Home Ready:** JSON API for seamless integration
- 🛡️ **Safety First:** Multiple protection systems and monitoring
- 📊 **Advanced Analytics:** Detailed logging and performance tracking
- ⚡ **Energy Efficient:** Smart scheduling and PV integration

**Where to Get One:**
- **Official Shop:** [pooldigital.de](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart)
- **Community Support:** [PoolDigital Forum](http://forum.pooldigital.de/)
- **Technical Docs:** Available with purchase

*This integration is community-developed and not officially endorsed by PoolDigital, but it's designed to work seamlessly with their excellent hardware.*

## 📋 Changelog

### Version 0.1.0 (Current Development)
- ✨ Initial release with comprehensive pool control
- 🌡️ Climate control for heating and solar systems  
- 🧪 Chemical monitoring and automated dosing
- 🏊 Pool cover integration with weather awareness
- 🔄 Intelligent backwash automation
- 📱 Full Home Assistant UI integration
- 🤖 Smart automation blueprints
- 🌍 Multi-language support (EN/DE)

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 🎖️ Credits & Acknowledgments

**Special Thanks:**
- 🏗️ **[@Ludeeus](https://github.com/ludeeus)** - Integration Blueprint template
- 🏠 **Home Assistant Team** - Amazing platform and developer tools
- 🏊 **PoolDigital** - Excellent controller hardware and API
- 🌍 **Community Contributors** - Testing, feedback, and improvements
- ☕ **Coffee Supporters** - Fuel for late-night coding sessions

**Built With:**
- 🐍 **Python 3.11+** - Core integration language
- 🏠 **Home Assistant 2024.6+** - Smart home platform
- 📡 **aiohttp** - Async HTTP client for API communication
- 🧪 **pytest** - Testing framework
- 🔧 **VS Code + Dev Containers** - Development environment

---

## 📞 Connect & Support

[![GitHub][github-shield]][github]
[![Discord][discord-shield]][discord]  
[![Community Forum][forum-shield]][forum]
[![Email](https://img.shields.io/badge/email-git%40xerolux.de-blue?style=for-the-badge&logo=gmail)](mailto:git@xerolux.de)

---

**Made with ❤️ for the Home Assistant and Pool Automation Community**

*Transform your pool into a smart pool - because life's too short for manual pool maintenance!* 🏊‍♀️🤖

---

<!-- Links -->
[integration_blueprint]: https://github.com/ludeeus/integration_blueprint
[buymeacoffee]: https://www.buymeacoffee.com/xerolux
[buymeacoffee-badge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/xerolux/violet-hass.svg?style=for-the-badge
[commits]: https://github.com/xerolux/violet-hass/commits/main
[hacs]: https://hacs.xyz
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[logo]: https://github.com/xerolux/violet-hass/raw/main/logo.png
[picture]: https://github.com/xerolux/violet-hass/raw/main/picture.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/xerolux/violet-hass.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Xerolux%20(%40xerolux)-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/xerolux/violet-hass.svg?style=for-the-badge
[releases]: https://github.com/xerolux/violet-hass/releases
[user_profile]: https://github.com/xerolux
[issues]: https://github.com/xerolux/violet-hass/issues
[github]: https://github.com/xerolux/violet-hass
[github-shield]: https://img.shields.io/badge/GitHub-xerolux/violet--hass-blue?style=for-the-badge&logo=github
[pbuy]: https://github.com/xerolux/violet-hass/raw/main/screenshots/violetbm.jpg
[downloads-shield]: https://img.shields.io/github/downloads/xerolux/violet-hass/latest/total.svg?style=for-the-badge
Use my Tesla referral link: [Referral Link](https://ts.la/sebastian564489)
