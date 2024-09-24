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

![Violet Home Assistant Integration][logo]

## Table of Contents
* [Screenshots](#screenshots)
* [Install](#install)
* [Configuration](#configuration-is-done-in-the-ui)
* [Common Problems/Errors and Solutions](#common-problems-errors-and-solutions)
* [Getting Support for this Integration](#getting-support-for-this-integration)
* [Supporting this Integration](#supporting-this-integration)
* [Contributing](#contributing)
* [A Brief Description of the Violet Pool Controller](#a-brief-description-of-the-violet-pool-controller)
* [Changelog](#changelog)
* [Credits](#credits)

## Install

To install the Violet Pool Controller via HACS, follow these steps:

1. Open HACS in your Home Assistant interface.
2. Click on the three dots in the top-right corner.
3. Select "Custom repositories" from the dropdown menu.
4. Add the following URL as a custom Git repository:  
   `https://github.com/Xerolux/violet-hass.git`
5. Choose "Integration" as the category for the repository.
6. Once the repository is added, go to "Integrations" in HACS.
7. Search for "Violet Pool Controller" and download the integration.
8. Restart Home Assistant to apply the changes.
9. After restarting, navigate to **Settings > Integrations** and add the "Violet Pool Controller" integration.

## Configuration is Done in the UI

1. Configure the IP address to match your pool controller (e.g., `http://192.168.x.xxx/getReadings?ALL`).
2. Optionally, adjust the polling frequency for fetching data. However, remember that Violet updates data every 10 seconds.

## Common Problems/Errors and Solutions

(Include common issues and their resolutions here...)

## Getting Support for this Integration

If you encounter any issues or need help, please raise an [issue on GitHub][issues]. This ensures that others can benefit from the solution too.

## Supporting this Integration

If you'd like to support this integration or show your appreciation, you can:

<a href="https://www.buymeacoffee.com/xerolux" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## Contributing

Contributions are always welcome! If you'd like to contribute, please read the [Contribution Guidelines](CONTRIBUTING.md).

## A Brief Description of the Violet Pool Controller

![Violet Home Assistant Integration][pbuy]

VIOLET is designed as a smart all-in-one solution for pool control, capable of managing small to fully equipped pool installations. It controls filtration, heating/solar heating, lighting (ON/OFF or DMX-enabled), backwashing, overflow tank control, water level regulation, pool cover, additional water features, and dosing.

In case of errors (e.g., sensor failure, pump running dry, faulty refill valve, etc.), notifications can be sent via email, push, or HTTP request. The configuration and operation of VIOLET are entirely browser-based, accessible via any device. Integrated statistics, log files, remote access, and a simple JSON API enable easy integration with smart home systems.

* [pooldigital.de shop](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart)
* [pooldigital.de forum](http://forum.pooldigital.de/)

## Credits

This project was generated using the [integration blueprint][integration_blueprint] from [@Ludeeus](https://github.com/ludeeus).

## Screenshots

![Violet Home Assistant Integration][screens1]  
![Violet Home Assistant Integration][screens2]

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
