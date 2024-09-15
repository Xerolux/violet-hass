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
* [A brief description of the Violet Controller](#a-brief-description-of-the-violet-pool-controller)
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


## A brief description of the ProCon.IP pool controller

![Violet Home Assistant Integration][pbuy]

VIOLET ist als smarte Komplettlösung zur Poolsteuerung konzipiert, die sowohl für kleinere Schwimmbad-Installationen z.B. nur die Filter-, Heizungs- / Absorber- und Beleuchtungs-Steuerung (EIN/AUS oder DMX fähig) übernehmen kann, als auch für technisch voll ausgestattete Becken eine ganzheitliche Lösung zur Steuerung aller üblichen, zusätzlichen Komponenten wie Rückspülen, Überlaufbehälter-Steuerung (Rinnenbecken), Wasserstands-Regelung (Skimmer-Becken), Pool-Abdeckung (Cover), zusätzliche Wasserattraktionen und natürlich auch die Dosierung übernimmt. Alle Funktionen greifen dabei, sofern notwendig, intelligent ineinander, um eine sinnvolle und effiziente Steuerung des kompletten Schwimmbades zu ermöglichen. Im Fehlerfall (z.B. Ausfall von Sensoren, Trockenlauf der Filterpumpe, Nachspeiseventil defekt, leer werdenden Stellmittel-Kanistern und vielem mehr) können entsprechende Benachrichtigungen per Email, Push oder HTTP Request versendet werden, um zeitnahes und zielgerichtetes Handeln zu ermöglichen, ohne permanent vor Ort einzelne Geräte oder Füllstände immer wieder kontrollieren zu müssen.

Die Konfiguration und Bedienung von VIOLET erfolgt vollständig browserbasiert (Web-App) und kann mit jedem PC, MAC, Tablet oder Smartphone erfolgen. Integrierte Statistiken (mit Daten-Export für beliebige Zeiträume, in Excel-konformes Format), ein Logfile, das alle Schaltvorgänge und Konfigurationsänderungen protokolliert, Fernzugriffs-Funktion (über die VIOLET von überall auf der Welt erreichbar ist) und viele weitere Features runden den Funktionsumfang ab. Zur einfachen Integration von VIOLET in Hausautomationssysteme / Smart Home (wie ioBroker, Loxone, KNX, FHEM, IP-Symcon), können alle Messwerte / Schaltzustände über eine einfache JSON-API ausgelesen werden.

* [pooldigital.de shop](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart/)
* [pooldigital.de forum](http://forum.pooldigital.de/)


## Changelog

### Version 0.0.1 (2024-09-14)
First Release

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
[screens1]: https://github.com/xerolux/violet-hass/raw/main/screenshots/screens1.png
[screens2]: https://github.com/xerolux/violet-hass/raw/main/screenshots/screens2.png
[buy]: https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart
[pbuy]: https://github.com/xerolux/violet-hass/raw/main/screenshots/violetbm.jpg
