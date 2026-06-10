# 🏊 Violet Pool Controller for Home Assistant

**English** | **[Deutsch](README.de.md)**

[![GitHub Release][releases-shield]][releases]
[![Downloads][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![HACS][hacs-badge]][hacs]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]
[![GitHub Sponsor](https://img.shields.io/github/sponsors/xerolux?logo=github&style=for-the-badge&color=blue)](https://github.com/sponsors/xerolux)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-xerolux-blue?logo=ko-fi&style=for-the-badge)](https://ko-fi.com/xerolux)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-xerolux-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://www.buymeacoffee.com/xerolux)
[![PayPal](https://img.shields.io/badge/PayPal-xerolux-blue?logo=paypal&style=for-the-badge)](https://paypal.me/xerolux)
[![Tesla Referral](https://img.shields.io/badge/Tesla-Referral-red?logo=tesla&style=for-the-badge)](https://ts.la/sebastian564489)

[![Release Management](https://github.com/Xerolux/violet-hass/actions/workflows/release.yml/badge.svg)](https://github.com/Xerolux/violet-hass/actions/workflows/release.yml)

> **Turn your pool into a smart pool!** Complete local control and monitoring of your Violet Pool Controller – no cloud, no subscription.

![Violet Home Assistant Integration][logo]

---

## 🌟 Features

| Category | What's Included |
|----------|----------------|
| **🌡️ Climate Control** | Heater & solar with thermostat and scheduling |
| **🧪 Chemical Dosing** | Automatic pH & chlorine with safety limits (standalone dosing supported) |
| **💧 Filter & Pump** | 3-speed pump, automatic backwash |
| **🏊 Cover** | Weather-dependent cover automation |
| **💡 LED / DMX** | 8 controllable scenes, RGB lighting |
| **📊 Monitoring** | pH, ORP, temperatures, pressure, flow rate, runtime |
| **⚡ Energy** | PV surplus mode for solar heating |
| **🔒 Security** | 100% local, SSL/TLS, rate limiting, input sanitization |
| **🔧 Multi-Controller** | Multiple pools in a single HA instance |

---

## ⚡ Quick Start

**1. HACS – Add Integration**

<a href="https://my.home-assistant.io/redirect/hacs_repository/?repository=https%3A%2F%2Fgithub.com%2FXerolux%2Fviolet-hass&owner=Xerolux&category=Integration" target="_blank" rel="noopener noreferrer"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store." /></a>

```
HACS → Integrations → ⋮ → Custom Repositories
URL: https://github.com/xerolux/violet-hass  |  Category: Integration
→ Download "Violet Pool Controller" → Restart HA
```

**2. Set Up Integration**
```
Settings → Devices & Services → Add Integration → "Violet Pool Controller"
Enter host IP (and adjust port if different from 80) → Select features → Done!
```

**3. Ready!** 🎉 Your pool is now smart.

> Detailed guide → **[Installation & Setup][wiki-install]**

---

## 📖 Documentation (Wiki)

The full documentation is available in the **[Wiki][wiki]**:

| Section | Pages |
|---------|-------|
| 🚀 **Getting Started** | [Installation & Setup][wiki-install] · [Configuration][wiki-config] · [Multi-Controller][wiki-multi] |
| 📊 **Entities** | [Sensors][wiki-sensors] · [Switches][wiki-switches] · [Climate][wiki-climate] · [Device States][wiki-states] |
| ⚙️ **Automation** | [Services Reference][wiki-services] · [Automation Examples][wiki-automations] |
| 🔧 **Operation** | [Troubleshooting][wiki-trouble] · [Diagnostics][wiki-diag] · [Error Codes][wiki-errors] · [FAQ][wiki-faq] |
| 🔐 **Security** | [Security & SSL][wiki-security] · [Advanced Logging][wiki-logging] |
| 👩‍💻 **Development** | [Contributing][wiki-contributing] · [API Reference][wiki-api] · [Changelog][wiki-changelog] |

---

## 🔑 Requirements

- Home Assistant **2026.5.0+** (tested up to 2026.x)
- HACS ([Installation guide](https://hacs.xyz/docs/setup/download))
- Violet Pool Controller accessible on your local network
- Python 3.14.2+

---

## 💝 Support

This integration is developed in my spare time:

[![GitHub Sponsor](https://img.shields.io/github/sponsors/xerolux?logo=github&style=for-the-badge&color=blue)](https://github.com/sponsors/xerolux)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-xerolux-blue?logo=ko-fi&style=for-the-badge)](https://ko-fi.com/xerolux)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-xerolux-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://www.buymeacoffee.com/xerolux)

- ⭐ Star the repository on GitHub
- 🐛 [Report bugs][issues]
- 📢 Share with other pool owners
- 💬 Help others in the [Community][forum] & [Discord][discord]

---

## 🏊 About the Violet Pool Controller

![Violet Pool Controller][pbuy]

The **VIOLET Pool Controller** by [PoolDigital GmbH & Co. KG](https://www.pooldigital.de/) is a premium smart pool automation system developed in Germany – with a JSON API for seamless Home Assistant integration.

- **Official Shop:** [pooldigital.de](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart)
- **Community:** [PoolDigital Forum](http://forum.pooldigital.de/)
- **API Package:** [violet-poolController-api](https://pypi.org/project/violet-poolController-api/) on PyPI ([GitHub](https://github.com/Xerolux/violet-poolController-api))



## **Disclaimer:**
*This is an unofficial, community-driven project. It is not affiliated with, endorsed by, or associated with PoolDigital GmbH & Co. KG in any way. "VIOLET" and any related trademarks are the property of their respective owners.*

⚠️ **WARNING - USE AT YOUR OWN RISK:**
*This software interacts with physical hardware and automation systems that control water chemistry (pH, Chlorine/ORP) and electrical equipment (pumps, heaters). A bug, network issue, or incorrect configuration could result in hardware damage, unsafe water conditions, or other hazards. By using this software, you acknowledge and agree that you are solely responsible for any damage, injury, or loss of property that may occur. Please always monitor your pool's chemistry and hardware independently.*

---

<div align="center">

**Made with ❤️ for the Home Assistant & Pool Community**

[![GitHub][github-shield]][github] [![Discord][discord-shield]][discord] [![Email](https://img.shields.io/badge/email-git%40xerolux.de-blue?style=for-the-badge&logo=gmail)](mailto:git@xerolux.de)

</div>

---

<!-- Wiki Links -->
[wiki]: https://github.com/Xerolux/violet-hass/wiki
[wiki-install]: https://github.com/Xerolux/violet-hass/wiki/Installation-and-Setup
[wiki-config]: https://github.com/Xerolux/violet-hass/wiki/Configuration
[wiki-multi]: https://github.com/Xerolux/violet-hass/wiki/Multi-Controller
[wiki-sensors]: https://github.com/Xerolux/violet-hass/wiki/Sensors
[wiki-switches]: https://github.com/Xerolux/violet-hass/wiki/Switches
[wiki-climate]: https://github.com/Xerolux/violet-hass/wiki/Climate
[wiki-states]: https://github.com/Xerolux/violet-hass/wiki/Device-States
[wiki-services]: https://github.com/Xerolux/violet-hass/wiki/Services
[wiki-automations]: https://github.com/Xerolux/violet-hass/wiki/Automations
[wiki-trouble]: https://github.com/Xerolux/violet-hass/wiki/Troubleshooting
[wiki-diag]: https://github.com/Xerolux/violet-hass/wiki/Diagnostics
[wiki-errors]: https://github.com/Xerolux/violet-hass/wiki/Error-Codes
[wiki-faq]: https://github.com/Xerolux/violet-hass/wiki/FAQ
[wiki-security]: https://github.com/Xerolux/violet-hass/wiki/Security
[wiki-logging]: https://github.com/Xerolux/violet-hass/wiki/Erweiterte-Protokollierung
[wiki-contributing]: https://github.com/Xerolux/violet-hass/wiki/Contributing
[wiki-api]: https://github.com/Xerolux/violet-hass/wiki/API-Reference
[wiki-changelog]: https://github.com/Xerolux/violet-hass/wiki/Changelog

<!-- Badge Links -->
[releases-shield]: https://img.shields.io/github/release/xerolux/violet-hass.svg?style=for-the-badge
[releases]: https://github.com/xerolux/violet-hass/releases
[downloads-shield]: https://img.shields.io/github/downloads/xerolux/violet-hass/latest/total.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/xerolux/violet-hass.svg?style=for-the-badge
[commits]: https://github.com/xerolux/violet-hass/commits/main
[license-shield]: https://img.shields.io/github/license/xerolux/violet-hass.svg?style=for-the-badge
[hacs]: https://hacs.xyz
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[buymeacoffee]: https://www.buymeacoffee.com/xerolux
[buymeacoffee-badge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[logo]: https://github.com/xerolux/violet-hass/raw/main/custom_components/violet_pool_controller/brand/logo.png
[pbuy]: https://github.com/xerolux/violet-hass/raw/main/screenshots/violetbm.jpg
[github]: https://github.com/xerolux/violet-hass
[github-shield]: https://img.shields.io/badge/GitHub-xerolux/violet--hass-blue?style=for-the-badge&logo=github
[issues]: https://github.com/xerolux/violet-hass/issues
