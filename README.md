# 🏊 Violet Pool Controller für Home Assistant

[![GitHub Release][releases-shield]][releases]
[![Downloads][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![HACS][hacs-badge]][hacs]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]
[![Buy Me A Coffee][buymeacoffee-badge]][buymeacoffee]
[![Tesla](https://img.shields.io/badge/Tesla-Referral-red?style=for-the-badge&logo=tesla)](https://ts.la/sebastian564489)

[![Release Management](https://github.com/Xerolux/violet-hass/actions/workflows/release.yml/badge.svg)](https://github.com/Xerolux/violet-hass/actions/workflows/release.yml)

> **Verwandle deinen Pool in einen Smart Pool!** Vollständige lokale Steuerung und Überwachung deines Violet Pool Controllers – ohne Cloud, ohne Abonnement.

![Violet Home Assistant Integration][logo]

---

## 🌟 Features

| Kategorie | Was ist enthalten |
|-----------|-------------------|
| **🌡️ Klimasteuerung** | Heizung & Solar mit Thermostat und Zeitplanung |
| **🧪 Chemie-Dosierung** | Automatisches pH & Chlor mit Sicherheitsgrenzen |
| **💧 Filter & Pumpe** | 3-Stufen-Pumpe, automatische Rückspülung |
| **🏊 Abdeckung** | Wetterabhängige Cover-Automatisierung |
| **💡 LED / DMX** | 8 steuerbare Szenen, RGB-Beleuchtung |
| **📊 Überwachung** | pH, ORP, Temperaturen, Druck, Durchfluss, Laufzeiten |
| **⚡ Energie** | PV-Überschuss-Modus für Solarheizung |
| **🔒 Sicherheit** | 100% lokal, SSL/TLS, Rate Limiting, Input Sanitization |
| **🔧 Multi-Controller** | Mehrere Pools in einer HA-Instanz |

---

## ⚡ Schnellstart

**1. HACS – Integration hinzufügen**
```
HACS → Integrationen → ⋮ → Benutzerdefinierte Repositories
URL: https://github.com/xerolux/violet-hass  |  Kategorie: Integration
→ "Violet Pool Controller" herunterladen → HA neu starten
```

**2. Integration einrichten**
```
Einstellungen → Geräte & Dienste → Integration hinzufügen → "Violet Pool Controller"
Host-IP eingeben → Features auswählen → Fertig!
```

**3. Fertig!** 🎉 Dein Pool ist jetzt smart.

> Detaillierte Anleitung → **[Installation & Setup][wiki-install]**

---

## 📖 Dokumentation (Wiki)

Die vollständige Dokumentation befindet sich im **[Wiki][wiki]**:

| Bereich | Seiten |
|---------|--------|
| 🚀 **Erste Schritte** | [Installation & Setup][wiki-install] · [Konfiguration][wiki-config] · [Multi-Controller][wiki-multi] |
| 📊 **Entities** | [Sensoren][wiki-sensors] · [Schalter][wiki-switches] · [Klima][wiki-climate] · [Device States][wiki-states] |
| ⚙️ **Automatisierung** | [Services Referenz][wiki-services] · [Automatisierungs-Beispiele][wiki-automations] |
| 🔧 **Betrieb** | [Troubleshooting][wiki-trouble] · [Diagnosedaten][wiki-diag] · [Fehler-Codes][wiki-errors] · [FAQ][wiki-faq] |
| 🔐 **Sicherheit** | [Security & SSL][wiki-security] · [Erweiterte Protokollierung][wiki-logging] |
| 👩‍💻 **Entwicklung** | [Contributing][wiki-contributing] · [API Referenz][wiki-api] · [Changelog][wiki-changelog] |

---

## 🔑 Voraussetzungen

- Home Assistant **2025.12.0+** (getestet bis 2026.x)
- HACS ([Installationsanleitung](https://hacs.xyz/docs/setup/download))
- Violet Pool Controller im lokalen Netzwerk erreichbar
- Python 3.12+

---

## 💝 Unterstützung

Diese Integration wird in meiner Freizeit entwickelt:

[![GitHub Sponsor](https://img.shields.io/github/sponsors/xerolux?logo=github&style=for-the-badge&color=blue)](https://github.com/sponsors/xerolux)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-xerolux-blue?logo=ko-fi&style=for-the-badge)](https://ko-fi.com/xerolux)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-xerolux-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://www.buymeacoffee.com/xerolux)

- ⭐ Repository auf GitHub sternen
- 🐛 [Bugs melden][issues]
- 📢 Mit anderen Pool-Besitzern teilen
- 💬 Anderen in [Community][forum] & [Discord][discord] helfen

---

## 🏊 Über den Violet Pool Controller

![Violet Pool Controller][pbuy]

Der **VIOLET Pool Controller** von [PoolDigital GmbH & Co. KG](https://www.pooldigital.de/) ist ein Premium Smart Pool Automation System aus deutscher Entwicklung – mit JSON API für nahtlose Home Assistant Integration.

- **Offizieller Shop:** [pooldigital.de](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart)
- **Community:** [PoolDigital Forum](http://forum.pooldigital.de/)

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
