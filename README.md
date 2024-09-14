# Violet Pool Controller

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacs-badge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymeacoffee-badge]][buymeacoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

![Violet Home Assistant Integration][logo]



## Table of contents
* [Screenshots](#screenshots)
* [Install](#install)
* [Configuration](#configuration-is-done-in-the-ui)
* [Common problems/erros and the solution](#common-problemserrors-and-the-solution)
* [Getting support for this integration](#getting-support-for-this-integration)
* [Supporting this integration](#supporting-this-integration)
* [Contributing](#contributions-are-welcome)
* [Changelog](#changelog)
* [Credits](#credits)


## Install 

To install the Violet Pool Controller via HACS, follow these steps:

    Open HACS in your Home Assistant interface.
    Click on the three dots in the top-right corner.
    Select "Custom repositories" from the dropdown menu.
    Add the following URL as a custom Git repository:
    https://github.com/Xerolux/violet-hass.git
    Choose "Integration" as the category for the repository.
    Once the repository is added, go to "Integrations" in HACS.
    Search for "Violet Pool Controller" and download the integration.
    Restart Home Assistant to apply the changes.
    After restarting, navigate to Settings > Integrations and add the "Violet Pool Controller" integration.


## Configuration is done in the UI

Configure the IP address to match your pool controller (e.g., http://192.168.x.xxx/getReadings?ALL).

Optionally, adjust the polling frequency for fetching data. However, remember that Violet itself only updates data every 10 seconds.





## Common problems/errors and the solution



## Getting support for this integration
If you have trouble with this integration and want to get help, please raise an [issue on github][issues].
This way others can benefit from the solution, too.


## Contributions are welcome!
If you want to contribute to this project please read the [Contribution guidelines](CONTRIBUTING.md).


* [pooldigital.de forum](http://forum.pooldigital.de/)

## Changelog

### Version 0.0.1 (2024-09-14)
First Release

## Credits
This project was generated using the [integration blueprint][integration_blueprint] from [@Ludeeus](https://github.com/ludeeus).

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