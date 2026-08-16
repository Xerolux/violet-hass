# 🏊 Violet Pool Controller für Home Assistant

**[English](README.md)** | **Deutsch**

**[Projektseite](https://xerolux.github.io/violet-hass/)** · **[Dokumentation](https://xerolux.github.io/violet-hass/docs/#/home)** · **[Releases](https://github.com/Xerolux/violet-hass/releases)**

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

> **Verwandle deinen Pool in einen Smart Pool!** Vollständige lokale Steuerung und Überwachung deines Violet Pool Controllers – ohne Cloud, ohne Abonnement.

![Violet Home Assistant Integration][logo]

---

## 🌟 Features

| Kategorie | Was ist enthalten |
|-----------|-------------------|
| **🌡️ Klimasteuerung** | Heizung & Solar mit Thermostat und Zeitplanung |
| **🧪 Chemie-Dosierung** | Automatisches pH & Chlor mit Sicherheitsgrenzen (Standalone Dosierung möglich) |
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

<a href="https://my.home-assistant.io/redirect/hacs_repository/?repository=https%3A%2F%2Fgithub.com%2FXerolux%2Fviolet-hass&owner=Xerolux&category=Integration" target="_blank" rel="noopener noreferrer"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store." /></a>

```
HACS → Integrationen → ⋮ → Benutzerdefinierte Repositories
URL: https://github.com/xerolux/violet-hass  |  Kategorie: Integration
→ "Violet Pool Controller" herunterladen → HA neu starten
```

**2. Integration einrichten**
```
Einstellungen → Geräte & Dienste → Integration hinzufügen → "Violet Pool Controller"
Host-IP eingeben (und Port anpassen, falls abweichend von 80) → Features auswählen → Fertig!
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
| 🎨 **Dashboards** | [Dashboards & Pool-Karten][wiki-dashboards] |
| ⚙️ **Automatisierung** | [Services Referenz][wiki-services] · [Automatisierungs-Beispiele][wiki-automations] |
| 🔧 **Betrieb** | [Troubleshooting][wiki-trouble] · [Diagnosedaten][wiki-diag] · [Fehler-Codes][wiki-errors] · [FAQ][wiki-faq] |
| 🔐 **Sicherheit** | [Security & SSL][wiki-security] · [Erweiterte Protokollierung][wiki-logging] |
| 👩‍💻 **Entwicklung** | [Contributing][wiki-contributing] · [API Referenz][wiki-api] · [Changelog][wiki-changelog] |

---

## 🔑 Voraussetzungen

- Home Assistant **2026.8.0+** (getestet bis 2026.x)
- HACS ([Installationsanleitung](https://hacs.xyz/docs/use/download/download/))
- Violet Pool Controller im lokalen Netzwerk erreichbar
- Python-Laufzeit wird von Home Assistant 2026.8.0+ bereitgestellt
- Standalone-API-Paket unterstützt Python 3.12+

---

## 🐍 Python-API-Paket

[![PyPI](https://img.shields.io/pypi/v/violet-poolController-api?style=for-the-badge&logo=pypi)](https://pypi.org/project/violet-poolController-api/)
[![Python Versions](https://img.shields.io/pypi/pyversions/violet-poolController-api?style=for-the-badge&logo=python)](https://pypi.org/project/violet-poolController-api/)

Der HTTP-Client hinter dieser Integration wird **in diesem Repo** entwickelt und als
[`violet-poolController-api`](https://pypi.org/project/violet-poolController-api/) auf PyPI
veröffentlicht — auch eigenständig ohne Home Assistant nutzbar:

```bash
pip install violet-poolController-api
```

```python
import aiohttp
from violet_poolcontroller_api.api import VioletPoolAPI

async with aiohttp.ClientSession() as session:
    api = VioletPoolAPI(host="192.168.1.50", session=session,
                        username="user", password="geheim")
    readings = await api.get_readings()          # alle ~400 Werte
    print(readings["pH_value"], readings["orp_value"])
    await api.manual_dosing("Chlor", 60)         # 60s manuelle Dosierung
```

**Eingebaute Sicherheit & Robustheit:** Token-Bucket-Rate-Limiting, Circuit Breaker, Retry mit
Backoff, Input-Sanitization, SSL/TLS-Verifikation, Standalone-Dosing-Modus.

📦 Vollständige API-Doku: [API-Referenz](https://github.com/Xerolux/violet-poolController-api/blob/main/docs/API_REFERENCE.md) ·
[Paket-README](https://github.com/Xerolux/violet-poolController-api/blob/main/README.md) ·
[Changelog](https://github.com/Xerolux/violet-poolController-api/blob/main/CHANGELOG.md)

---

## Repository-Struktur

Dieses Repository enthält die Home-Assistant-Integration. Der API-Client liegt in einem
eigenen Repository ([`violet-poolController-api`](https://github.com/Xerolux/violet-poolController-api),
veröffentlicht auf [PyPI](https://pypi.org/project/violet-poolController-api/)) und wird als Abhängigkeit installiert.

| Verzeichnis | Beschreibung |
|-------------|--------------|
| `custom_components/violet_pool_controller/` | Home-Assistant-Integration ([HACS](https://hacs.xyz/)) |
| `tests/` | HA-Integrationstests |
| `docs/` | Dokumentation & Wiki-Quellen |
| `Dashboard/` | Fertige Lovelace-Dashboards & -Karten ([Anleitung][wiki-dashboards]) |

**Releases:** Die HA-Integration wird über `v*`-Tags released (HACS). Das API-Paket wird
unabhängig im eigenen Repository über `api-v*`-Tags released (automatischer PyPI-Upload + GitHub-Release).

Details: [ARCHITECTURE.md](./ARCHITECTURE.md)

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
- **API Package:** [violet-poolController-api](https://pypi.org/project/violet-poolController-api/) auf PyPI ([GitHub](https://github.com/Xerolux/violet-poolController-api))

---

<div align="center">

**Made with ❤️ for the Home Assistant & Pool Community**

[![GitHub][github-shield]][github] [![Discord][discord-shield]][discord] [![Email](https://img.shields.io/badge/email-git%40xerolux.de-blue?style=for-the-badge&logo=gmail)](mailto:git@xerolux.de)

</div>

---

<!-- Wiki Links -->
[wiki]: https://xerolux.github.io/violet-hass/docs/#/home
[wiki-install]: https://xerolux.github.io/violet-hass/docs/#/installation
[wiki-config]: https://xerolux.github.io/violet-hass/docs/#/configuration
[wiki-multi]: https://xerolux.github.io/violet-hass/docs/#/multi-controller
[wiki-dashboards]: https://xerolux.github.io/violet-hass/docs/#/dashboards
[wiki-sensors]: https://xerolux.github.io/violet-hass/docs/#/sensors
[wiki-switches]: https://xerolux.github.io/violet-hass/docs/#/switches
[wiki-climate]: https://xerolux.github.io/violet-hass/docs/#/climate
[wiki-states]: https://xerolux.github.io/violet-hass/docs/#/states
[wiki-services]: https://xerolux.github.io/violet-hass/docs/#/services
[wiki-automations]: https://xerolux.github.io/violet-hass/docs/#/automations
[wiki-trouble]: https://xerolux.github.io/violet-hass/docs/#/troubleshooting
[wiki-diag]: https://xerolux.github.io/violet-hass/docs/#/diagnostics
[wiki-errors]: https://xerolux.github.io/violet-hass/docs/#/error-codes
[wiki-faq]: https://xerolux.github.io/violet-hass/docs/#/faq
[wiki-security]: https://xerolux.github.io/violet-hass/docs/#/security
[wiki-logging]: https://xerolux.github.io/violet-hass/docs/#/logging
[wiki-contributing]: https://xerolux.github.io/violet-hass/docs/#/contributing
[wiki-api]: https://xerolux.github.io/violet-hass/docs/#/api
[wiki-changelog]: https://xerolux.github.io/violet-hass/docs/#/changelog

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
