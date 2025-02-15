[![GitHub Release][releases-shield]][releases]
[![releases][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacs-badge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymeacoffee-badge]][buymeacoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

# Violet Pool Controller HACS Home Assistant Addon

This custom integration allows you to monitor and control your pool equipment using the Violet Pool Controller in Home Assistant. It includes sensors, binary sensors, and switches to track various pool metrics and perform essential operations.

![Violet Home Assistant Integration][logo]

## Features

*   **Sensors:** Monitor various parameters such as water flow, temperature, pump power, pH levels, and more.
*   **Binary Sensors:** Track the status of critical systems like pumps, solar, heater, and system connectivity.
*   **Switches:** Control your pool equipment, such as the pump, lights, eco mode, and dosing systems.

## Table of Contents

*   [Screenshots](#screenshots)
*   [Installation](#installation)
*   [Configuration](#configuration)
*   [Common Problems/Errors and Solutions](#common-problemserrors-and-solutions)
*   [Getting Support](#getting-support)
*   [Supporting this Integration](#supporting-this-integration)
*   [Contributing](#contributing)
*   [About the Violet Pool Controller](#about-the-violet-pool-controller)
*   [Changelog](#changelog)
*   [Credits](#credits)

## Installation

1.  **HACS Installation (Recommended):**
    *   Open HACS in your Home Assistant interface.
    *   Click on the three dots in the top-right corner.
    *   Select "Custom repositories."
    *   Add `https://github.com/Xerolux/violet-hass.git` as a custom Git repository.
    *   Choose "Integration" as the category.
    *   Click "Add".
    *   Search for "Violet Pool Controller" in the HACS integrations and click "Download".
    *   Restart Home Assistant.

2.  **Manual Installation (Advanced Users):**
    *   Copy the `violet_pool_controller` folder from this repository into your Home Assistant's `custom_components` directory.
    *   Restart Home Assistant.

## Configuration

Configuration is done entirely through the Home Assistant UI.  After installation:

1.  Go to **Settings > Devices & Services > Integrations**.
2.  Click "+ Add Integration".
3.  Search for "Violet Pool Controller" and select it.
4.  A configuration dialog will appear.  Enter the following information:

    *   **Host:** The IP address or hostname of your Violet Pool Controller (e.g., `192.168.1.100`).  *Do not* include `http://` or `https://`.
    *   **Username:** Your Violet Pool Controller username (if authentication is enabled).  Leave blank if not required.
    *   **Password:** Your Violet Pool Controller password (if authentication is enabled).  Leave blank if not required.
    *   **Polling Interval (seconds):** How often Home Assistant should fetch data from the controller (default: 10 seconds).  Adjust this based on your needs and network performance.
    *   **Use SSL:** Check this box if your Violet Pool Controller uses HTTPS (SSL/TLS) for secure communication.  Leave unchecked for HTTP.
    *   **Device ID:**  A unique numeric identifier for this controller (default: 1).  Use different IDs if you have multiple Violet Pool Controllers.
    *    **Device Name:** Give your Violet Pool Controller a descriptive name.
    *   **Retry Attempts:** Number of times to retry connecting to the device on failure (default: 3).

5.  Click "Submit".  If the connection is successful, the integration will be set up, and your pool controller's entities will appear in Home Assistant.

## Common Problems/Errors and Solutions

*   **Connection Errors:**
    *   Double-check the IP address/hostname, username, and password.
    *   Ensure your Home Assistant instance can reach the Violet Pool Controller on your network.  Try pinging the controller from the machine running Home Assistant.
    *   Verify that the `use_ssl` setting is correct.
    *   Temporarily disable any firewalls on your Home Assistant machine or the Violet Pool Controller to rule out firewall issues.
    *  Increase the timeout or retry attempts in the configuration options.

*   **"Unexpected response structure" or "Firmware version not found" Errors:**
    * These usually indicate an issue with the API response from the Violet Pool Controller.
    * Ensure your controller's firmware is up-to-date.  Check the PoolDigital website or forums for firmware updates.
    * Verify the IP address entered.

*   **Entities Not Updating:**
    *   Check the Home Assistant logs (Settings > System > Logs) for any errors related to `violet_pool_controller`.
    *   Try restarting Home Assistant.
    *   Ensure the polling interval is not set too low (a very low polling interval can overload the controller).
    *   Verify that your Data Update Coordinator is set up.

*  **Entities Not Showing**
    *   Check the naming of the sensors and that the coordinator contains data.

## Getting Support

If you encounter any problems or have questions, please:

1.  **Check the Home Assistant Logs:**  Look for error messages related to `violet_pool_controller`.  This often provides valuable clues.
2.  **Consult this README:**  Review the troubleshooting steps above.
3.  **Create an Issue:** If you can't resolve the issue, open an issue on the [GitHub repository][issues].  Provide as much detail as possible, including:
    *   Home Assistant version.
    *   Integration version (from `manifest.json`).
    *   Relevant log entries (from Settings > System > Logs).
    *   Steps to reproduce the problem.
    *   Screenshots, if applicable.
4.  **PoolDigital Forum:** For questions specifically about the Violet Pool Controller *hardware or firmware*, the [PoolDigital forum](http://forum.pooldigital.de/) is a good resource.

## Supporting this Integration

If you find this integration useful, consider supporting its development:

<a href="https://www.buymeacoffee.com/xerolux" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## Contributing

Contributions are welcome!  If you want to contribute, please:

1.  **Fork the repository.**
2.  **Create a new branch** for your feature or bug fix.
3.  **Make your changes.**
4.  **Submit a pull request.**

Please follow the coding style and conventions used in the existing code.

## About the Violet Pool Controller

![Violet Pool Controller][pbuy]

VIOLET is a smart all-in-one pool control system from PoolDigital.  It's designed to manage various aspects of pool operation, including:

*   Filtration
*   Heating/Solar Heating
*   Lighting (ON/OFF and DMX)
*   Backwashing
*   Overflow Tank Control
*   Water Level Regulation
*   Pool Cover Control
*   Additional Water Features
*   Dosing

VIOLET provides notifications (email, push, HTTP request) for errors, and its browser-based interface allows access from any device.  It also offers integrated statistics, log files, remote access, and a JSON API for integration with smart home systems.

*   **Shop:** [pooldigital.de shop](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart)
*   **Forum:** [pooldigital.de forum](http://forum.pooldigital.de/)

## Changelog
A Changelog will be created when the project is officially published.

## Credits

This project was generated using the [integration blueprint][integration_blueprint] from [@Ludeeus](https://github.com/ludeeus).  Thanks to the Home Assistant community for providing a great platform and resources for developers!

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
