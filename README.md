[![GitHub Release][releases-shield]][releases]
[![releases][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacs-badge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymeacoffee-badge]][buymeacoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

# Violet Pool Controller for Home Assistant

This custom integration allows you to monitor and control your pool equipment using the Violet Pool Controller in Home Assistant. It includes sensors, binary sensors, switches, climate controls, and cover entities to track various pool metrics and perform essential operations.

![Violet Home Assistant Integration][logo]

## Features

* **Sensors:** Monitor various parameters such as water temperature, pH levels, redox potential, chlorine levels, filter pressure, and more
* **Binary Sensors:** Track the status of critical systems like pumps, solar, heater, and system connectivity
* **Switches:** Control your pool equipment, such as the pump, lights, eco mode, dosing systems, and backwash function
* **Climate Controls:** Manage pool heating and solar absorber temperature
* **Cover Controls:** Operate your pool cover directly from Home Assistant
* **Number Entities:** Set target values for pH, redox, and chlorine levels

## Table of Contents

* [Screenshots](#screenshots)
* [Installation](#installation)
* [Configuration](#configuration)
* [Entities](#entities)
* [Services](#services)
* [Common Problems and Solutions](#common-problems-and-solutions)
* [Getting Support](#getting-support)
* [Supporting this Integration](#supporting-this-integration)
* [Contributing](#contributing)
* [About the Violet Pool Controller](#about-the-violet-pool-controller)
* [Changelog](#changelog)
* [Credits](#credits)

## Screenshots

<!-- You should add some actual screenshots here -->

## Installation

### HACS Installation (Recommended)

1. Open HACS in your Home Assistant interface
2. Click on the three dots in the top-right corner
3. Select "Custom repositories"
4. Add `https://github.com/Xerolux/violet-hass.git` as a custom Git repository
5. Choose "Integration" as the category
6. Click "Add"
7. Search for "Violet Pool Controller" in the HACS integrations and click "Download"
8. Restart Home Assistant

### Manual Installation (Advanced Users)

1. Copy the `violet_pool_controller` folder from this repository into your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

Configuration is done entirely through the Home Assistant UI. After installation:

1. Go to **Settings > Devices & Services > Integrations**
2. Click "+ Add Integration"
3. Search for "Violet Pool Controller" and select it
4. A configuration dialog will appear. Enter the following information:

   * **Host:** The IP address or hostname of your Violet Pool Controller (e.g., `192.168.1.100`). *Do not* include `http://` or `https://`
   * **Username:** Your Violet Pool Controller username (if authentication is enabled). Leave blank if not required
   * **Password:** Your Violet Pool Controller password (if authentication is enabled). Leave blank if not required
   * **Use SSL:** Check this box if your Violet Pool Controller uses HTTPS (SSL/TLS) for secure communication. Leave unchecked for HTTP
   * **Device ID:** A unique numeric identifier for this controller (default: 1). Use different IDs if you have multiple Violet Pool Controllers
   * **Device Name:** Give your Violet Pool Controller a descriptive name
   * **Polling Interval (seconds):** How often Home Assistant should fetch data from the controller (default: 60 seconds). Adjust this based on your needs and network performance
   * **Timeout Duration (seconds):** Maximum time to wait for API responses (default: 10 seconds)
   * **Retry Attempts:** Number of times to retry connecting to the device on failure (default: 3)

5. Click "Submit". If the connection is successful, you'll proceed to the pool setup step
6. Configure your pool settings:
   * **Pool Size:** Enter your pool volume in cubic meters
   * **Pool Type:** Select your pool type (outdoor, indoor, whirlpool, natural, combination)
   * **Disinfection Method:** Choose your disinfection method (chlorine, salt, bromine, active oxygen, UV, ozone)

7. Click "Submit" to proceed to the feature selection step
8. Select which features you want to enable for your pool controller
9. Click "Submit" to complete the setup. Your pool controller's entities will appear in Home Assistant

## 🧩 Entities

The integration dynamically creates entities depending on the available API data and your selected features.

### 🔍 Sensors
- Water Temperature  
- pH Level  
- Redox Potential  
- Chlorine Level  
- Filter Pressure  
- Water Level  
- Additional sensors (if provided by the API)

### 💡 Switches
- Pump  
- Lighting  
- Heating  
- Dosing (Chlorine, pH+, pH-)  
- Backwash  
- PV Surplus  
- Additional switches based on API data

### 🌡️ Climate Entities
- Heater  
- Solar Absorber

### 🛡️ Cover Entities
- Pool Cover

### 🔢 Number Entities
- pH Target Value  
- Redox Target Value  
- Chlorine Target Values (Min/Max)

## ⚙️ Services

The integration provides the following custom services:

### `violet_pool_controller.turn_auto`
Set a Violet Pool Controller switch to AUTO mode.

| Parameter | Type | Description |
|-----------|------|-------------|
| entity_id | string | Entity ID of the switch |
| auto_delay | integer | Optional: Auto delay in seconds (0-3600) |

### `violet_pool_controller.set_pv_surplus`
Enable PV surplus mode with a specific pump speed.

| Parameter | Type | Description |
|-----------|------|-------------|
| entity_id | string | Entity ID of the PV surplus switch |
| pump_speed | integer | Pump speed (1-3) |

### `violet_pool_controller.manual_dosing`
Trigger manual dosing for a specified duration.

| Parameter | Type | Description |
|-----------|------|-------------|
| entity_id | string | Entity ID of the dosing switch |
| duration_seconds | integer | Duration in seconds (1-3600) |

### `violet_pool_controller.set_temperature_target`
Set the target temperature for heating or solar absorber.

| Parameter | Type | Description |
|-----------|------|-------------|
| entity_id | string | Entity ID of the climate entity |
| temperature | float | Target temperature (20-40°C) |

### `violet_pool_controller.set_ph_target`
Set the pH target value for dosing.

| Parameter | Type | Description |
|-----------|------|-------------|
| entity_id | string | Entity ID of the pH number entity |
| target_value | float | Target pH value (6.8-7.8) |

### `violet_pool_controller.set_chlorine_target`
Set the chlorine target value (as redox value) for dosing.

| Parameter | Type | Description |
|-----------|------|-------------|
| entity_id | string | Entity ID of the chlorine number entity |
| target_value | float | Target chlorine level (0.1-3.0 mg/l) |

### `violet_pool_controller.trigger_backwash`
Manually start a backwash process.

| Parameter | Type | Description |
|-----------|------|-------------|
| entity_id | string | Entity ID of the backwash switch |
| duration | integer | Optional: Duration in seconds (0-900) |

### `violet_pool_controller.start_water_analysis`
Initiate a water analysis process.

| Parameter | Type | Description |
|-----------|------|-------------|
| entity_id | string | Optional: Entity ID to identify the device |

### `violet_pool_controller.set_maintenance_mode`
Enable or disable maintenance mode.

| Parameter | Type | Description |
|-----------|------|-------------|
| entity_id | string | Optional: Entity ID to identify the device |
| enable | boolean | Whether to enable (True) or disable (False) maintenance mode |

## 🛠️ Developer Notes

### 🔄 Data Retrieval
Data is retrieved via the Violet Pool Controller API using a coordinated update mechanism to avoid excessive API requests.

### 🚨 Error Handling
Comprehensive error handling with exponential backoff is implemented for improved reliability.

### 🧱 Entity Structure
Entities are modular and dynamically created based on available data and selected features.

## Common Problems and Solutions

### Connection Errors

* Double-check the IP address/hostname, username, and password
* Ensure your Home Assistant instance can reach the Violet Pool Controller on your network. Try pinging the controller from the machine running Home Assistant
* Verify that the `use_ssl` setting is correct
* Temporarily disable any firewalls on your Home Assistant machine or the Violet Pool Controller to rule out firewall issues
* Increase the timeout or retry attempts in the configuration options

### "Unexpected response structure" or "Firmware version not found" Errors

* These usually indicate an issue with the API response from the Violet Pool Controller
* Ensure your controller's firmware is up-to-date. Check the PoolDigital website or forums for firmware updates
* Verify the IP address entered

### Entities Not Updating

* Check the Home Assistant logs (Settings > System > Logs) for any errors related to `violet_pool_controller`
* Try restarting Home Assistant
* Ensure the polling interval is not set too low (a very low polling interval can overload the controller)
* Verify that your Data Update Coordinator is set up

### Entities Not Showing

* Check that you have enabled the relevant features in the integration settings
* Verify that your controller supports the features you're trying to use
* Check the Home Assistant logs for any errors related to entity initialization

## Getting Support

If you encounter any problems or have questions, please:

1. **Check the Home Assistant Logs:** Look for error messages related to `violet_pool_controller`. This often provides valuable clues
2. **Consult this README:** Review the troubleshooting steps above
3. **Create an Issue:** If you can't resolve the issue, open an issue on the [GitHub repository][issues]. Provide as much detail as possible, including:
   * Home Assistant version
   * Integration version (from `manifest.json`)
   * Relevant log entries (from Settings > System > Logs)
   * Steps to reproduce the problem
   * Screenshots, if applicable
4. **PoolDigital Forum:** For questions specifically about the Violet Pool Controller *hardware or firmware*, the [PoolDigital forum](http://forum.pooldigital.de/) is a good resource

## Supporting this Integration

If you find this integration useful, consider supporting its development:

[![GitHub Sponsor](https://img.shields.io/github/sponsors/xerolux?logo=github&style=flat-square&color=blue)](https://github.com/sponsors/xerolux)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-xerolux-blue?logo=ko-fi&style=flat-square)](https://ko-fi.com/xerolux)
[![Patreon](https://img.shields.io/badge/Patreon-Xerolux-red?logo=patreon&style=flat-square)](https://patreon.com/Xerolux)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-xerolux-yellow?logo=buy-me-a-coffee&style=flat-square)](https://www.buymeacoffee.com/xerolux)
[![Tesla Referral](https://img.shields.io/badge/Tesla%20Referral-Sebastian-FF0000?logo=tesla&style=flat-square)](https://ts.la/sebastian564489)

## Contributing

Contributions are welcome! If you want to contribute, please:

1. **Fork the repository**
2. **Create a new branch** for your feature or bug fix
3. **Make your changes**
4. **Submit a pull request**

Please follow the coding style and conventions used in the existing code.

## About the Violet Pool Controller

![Violet Pool Controller][pbuy]

VIOLET is a smart all-in-one pool control system from PoolDigital. It's designed to manage various aspects of pool operation, including:

* Filtration
* Heating/Solar Heating
* Lighting (ON/OFF and DMX)
* Backwashing
* Overflow Tank Control
* Water Level Regulation
* Pool Cover Control
* Additional Water Features
* Dosing

VIOLET provides notifications (email, push, HTTP request) for errors, and its browser-based interface allows access from any device. It also offers integrated statistics, log files, remote access, and a JSON API for integration with smart home systems.

* **Shop:** [pooldigital.de shop](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart)
* **Forum:** [pooldigital.de forum](http://forum.pooldigital.de/)

## Changelog

A detailed changelog will be created when the project is officially published.

## Credits

This project was generated using the [integration blueprint][integration_blueprint] from [@Ludeeus](https://github.com/ludeeus). Thanks to the Home Assistant community for providing a great platform and resources for developers!

---

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
[screens1]: https://github.com/xerolux/violet-hass/raw/main/screenshots/overview.png
[screens2]: https://github.com/xerolux/violet-hass/raw/main/screenshots/screens2.png
[buy]: https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart
[pbuy]: https://github.com/xerolux/violet-hass/raw/main/screenshots/violetbm.jpg
[downloads-shield]: https://img.shields.io/github/downloads/xerolux/violet-hass/latest/total.svg?style=for-the-badge
