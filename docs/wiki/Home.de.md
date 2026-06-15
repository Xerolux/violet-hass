> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Home)**

---

# 🏊 Violet Pool Controller – Home Assistant Integration


> **Die komplette Dokumentation** für das Violet Pool Controller Addon.
> Von der Installation bis zur Deinstallation – mit allen Features, States, Services und Automatisierungen.

---

## 📢 Letzte Änderungen (v2.0.0-beta.7)

### ✨ Neue Funktionen & Verbesserungen

#### 🧪 H2O2-Dosierung
- **H2O2-Unterstützung**: Teilt den `DOS_1_CL`-Ausgang mit Chlor (Auswahl über `from=3`).
- Neue Service-Option `h2o2` bei `manual_dosing_http`, `configure_dosing`, `set_dosing_target`, `set_dosing_daytime`, `set_dosing_max_daily`, `enable_dosing`.
- Entsprechende Fehlercodes `0142`–`0145` hinterlegt.

#### ⚡ Omni-DC-Ausgänge
- 6 neue schaltbare Ausgänge (`OMNI_DC0`–`OMNI_DC5`) als Switches, Select-Steuerung und Runtime-Sensoren.

#### 🧰 OMNI DC + DIRULE-Switches
- `DIRULE_1`–`DIRULE_8` Digitalregel-Schalter jetzt im UI verfügbar.
- Alle Erweiterungsrelais (`EXT1_1`–`EXT2_8`) über Select-Entities konfigurierbar.

#### 🧯 Korrigierte State-Zuordnung
- **Korrektur**: State `2` (`AUTO_PRIO_OFF`) wird jetzt korrekt als **AUS** erkannt (zuvor fälschlich AN).
- **Korrektur**: Alle Auto-States werden im Select korrekt auf `AUTO` abgebildet.
- Siehe [Gerätezustände](Device-States.de) für die korrigierte Tabelle.

#### 📊 Neue Sensor-Kategorien
- **Laufzeit-Sensoren**: Tägliche Laufzeiten pro Ausgang für Pumpe, Solar, Heizung, Licht, Rückspülung, Refill, ECO, Dosierkanäle, Erweiterungsrelais, OMNI-DC-Motoren, Pumpen-RPM-Stufen.
- **Dosierstatistik**: Tägliche Dosiermenge (ml) und verbleibende Kanistermenge (ml) für jeden Dosierkanal.
- **Composite-State-Sensoren**: `PUMPSTATE`, `HEATERSTATE`, `SOLARSTATE` tragen den vollen `BLOCKED_BY_*`- / `WAITING_FOR_*`-Detail-String.
- **Hardware-Binary-Sensoren**: Basismodul, Dosiermodul, beide Erweiterungsmodule, Standalone-Modus, DMX-Modul, Digitalregel-Modul.
- **Overflow/Rückspül/Bad-AI-Binary-Sensoren**: Überfüllung, Trockenlauf, Refill, Rückspül-Verzögerung, Bad-AI-Überwachung.

#### 🔧 HTTP-Control- & Regel-Service (Phase 2–4)
- Neue Services: `control_heater_http`, `control_solar_http`, `control_cover_http`, `control_backwash_http`, `manual_dosing_http`, `configure_dosing`, `set_dosing_target`, `set_dosing_daytime`, `set_dosing_max_daily`, `enable_dosing`, `configure_temp_rule`, `configure_analog_rule`, `configure_switching_rule`, `configure_timer_rule`, `enable_rule`, `control_extension_relay`, `configure_sensor_calibration`.
- Siehe [Services](Services.de) für die vollständige Referenz.

---

## Was ist das Violet Pool Controller Addon?

Das **Violet Pool Controller Home Assistant Integration** verbindet [Home Assistant](https://www.home-assistant.io/) mit dem [Violet Pool Controller](https://www.pooldigital.de/) von PoolDigital GmbH & Co. KG. Es ermöglicht vollständige lokale Steuerung und Überwachung deiner Poolanlage – **ohne Cloud, ohne Abonnement**.

| Feature | Details |
|---------|---------|
| **Protokoll** | HTTP/HTTPS, lokales Polling |
| **HA-Mindestversion** | 2026.5.0 |
| **Getestet bis** | 2026.5.x / 2026.6.x |
| **Python** | 3.14.2+ |
| **Integration-Version** | 2.0.0-beta.7 |
| **API-Paket** | violet-poolController-api ≥ 0.0.29 (PyPI) |
| **Lizenz** | AGPL-3.0-or-later |
| **Quality Scale** | Platinum |
| **Sprachen** | DE, EN, ES, FR, IT, NL, PL, PT, RU, ZH |

---

## Kernfunktionen

```
┌─────────────────────────────────────────────────────────┐
│              VIOLET POOL CONTROLLER ADDON                │
├──────────────┬──────────────┬──────────────┬────────────┤
│   Pumpe      │   Heizung    │   Solar      │ Dosierung  │
│ (3 Stufen)   │ (Thermostat) │ (PV-Surplus) │ pH/Cl/ORP  │
├──────────────┼──────────────┼──────────────┼────────────┤
│  Beleucht.   │  Abdeckung   │  Digit. I/O  │ Diagnose   │
│ (DMX 1-12)   │  (Cover)     │  (DI1-DI12)  │ Download   │
├──────────────┼──────────────┼──────────────┼────────────┤
│ EXT1.1-2.8   │ OMNI_DC0-5   │ DIRULE_1-8   │ H2O2-Dos.  │
├──────────────┴──────────────┴──────────────┴────────────┤
│  100% lokal · Multi-Controller · SSL/TLS · Rate Limiting │
└─────────────────────────────────────────────────────────┘
```

### Plattformen & Entities

| Plattform | Entities | Beispiele |
|-----------|----------|-----------|
| **Sensor** | Temperaturen (1-Wire 1-12), pH, ORP, Chlor, Analog (ADC1-5, IMP1-2), Laufzeiten, Dosierstatistik, Composite-States, System | `sensor.violet_pool_controller_onewire1_value` |
| **Binary Sensor** | Kern-States (PUMP/SOLAR/HEATER/...), Digitaleingänge DI1-DI12, CE1-CE4, Hardware-Module, Overflow/Rückspül/Bad-AI | `binary_sensor.violet_pool_controller_pump` |
| **Switch** | Pumpe, Heizung, Solar, pH±, Chlor, Elektrolyse, Flockung, Licht, Rückspülung, Spülung, Refill, ECO, PV-Surplus, EXT1.1-2.8, OMNI_DC0-5, DIRULE_1-8 | `switch.violet_pool_controller_pump` |
| **Light** | DMX-Szenen 1–12 (als `LightEntity`) | `light.violet_pool_controller_dmx_scene1` |
| **Climate** | Poolheizung (Thermostat), Solar-Heizung | `climate.violet_pool_controller_heater` |
| **Cover** | Poolabdeckung | `cover.violet_pool_controller_cover` |
| **Number** | Temperatursollwerte, pH/ORP/Chlor-Ziel, Pumpengeschwindigkeit, Kanistervolumen | `number.violet_pool_controller_ph_setpoint` |
| **Select** | Modus-Select (Off/On/Auto) für alle Switches, Regeln, Erweiterungen und OMNI-Ausgänge | `select.violet_pool_controller_pump_mode` |

---

## Schnell-Navigation

### Ich bin neu hier

1. **[Installation & Setup](Installation-and-Setup)** – HACS oder manuell installieren
2. **[Konfiguration](Configuration)** – Integration einrichten
3. **[Entities](Entities)** – Alle Sensoren, Schalter, Klima
4. **[Sensoren verstehen](Sensors)** – Welche Daten bekomme ich?
5. **[Device States](Device-States)** – Was bedeuten die 7 States?

### Ich will automatisieren

1. **[Services Referenz](Services)** – Alle verfügbaren Services
2. **[Automatisierungs-Beispiele](Automations)** – Copy-paste YAML-Beispiele
3. **[Pumpe steuern](Services#-service-control_pump)** – Geschwindigkeitssteuerung
4. **[Dosierung](Services#-service-smart_dosing)** – Chemikalien intelligent dosieren

### Ich habe ein Problem

1. **[Troubleshooting](Troubleshooting)** – Häufige Probleme & Lösungen
2. **[Diagnosedaten herunterladen](Diagnostics)** – JSON-Export für Bug-Reports
3. **[Erweiterte Protokollierung](Erweiterte-Protokollierung)** – Diagnose-Tools & Log-Export
4. **[Fehler-Codes](Error-Codes)** – Controller-Fehlercodes erklärt
5. **[FAQ](FAQ)** – 50+ häufige Fragen
6. **[GitHub Issues](https://github.com/Xerolux/violet-hass/issues)** – Bug-Reports

### Ich will mehrere Controller

→ **[Multi-Controller Guide](Multi-Controller)** – Mehrere Pools verwalten

### Ich will beitragen

→ **[Contributing Guide](Contributing)** – Pull Requests, Tests, Style Guide

---

## Architektur-Überblick

```
Home Assistant
    │
    ├── VioletPoolDataUpdateCoordinator (polling, 10s default)
    │       │
    │       ├── VioletPoolAPI (aiohttp, rate-limited, retry-logic, SSL)
    │       │       │   → PyPI-Paket "violet-poolController-api"
    │       │       │     (in diesem Monorepo entwickelt, auch standalone nutzbar)
    │       │       │
    │       │       └── Violet Pool Controller (HTTP/HTTPS)
    │       │               GET /getReadings?ALL
    │       │               GET /setFunctionManually?{payload}
    │       │               POST /triggerManualDosing (Dosierausgänge)
    │       │               POST /setConfig
    │       │
    │       └── Entities (sensors, switches, climate, cover, number, select)
    │
    ├── Services (control_pump, smart_dosing, manage_pv_surplus, ...)
    │
    └── Diagnostics (Diagnosedaten herunterladen via HA UI)
```

Der HTTP-Client wird in diesem Repository unter `violet_poolcontroller_api/` gepflegt und
auf PyPI veröffentlicht — siehe **[Python-API-Paket](API-Package.de)** für die
eigenständige Nutzung.

### Sicherheits-Features

- **Rate Limiting**: Token-Bucket-Algorithmus verhindert Controller-Überlastung
- **Input Sanitization**: Schutz vor XSS, SQL-Injection, Command-Injection
- **SSL/TLS**: Zertifikats-Verifikation standardmäßig aktiv
- **Auto-Recovery**: Exponentielles Backoff (10s → 300s), max. 10 Versuche
- **Thread Safety**: Zwei dokumentierte Locks ohne Verschachtelung

---

## Unterstützte Controller-Features

| Feature | Aktivierbar im Setup | Beschreibung |
|---------|---------------------|--------------|
| Filterpumpe (`filter_control`) | Immer | 3-Stufen-Pumpe mit Automatik |
| Heizung (`heating`) | Optional, Default AN | Thermostat mit Solltemperatur |
| Solarkollektor (`solar`) | Optional, Default AN | Solar + PV-Überschuss |
| pH-Kontrolle (`ph_control`) | Optional, Default AN | pH- und pH+ Dosierpumpen |
| Chlor-Kontrolle (`chlorine_control`) | Optional, Default AN | Chlor-Dosierung, Elektrolyse, H2O2 |
| Flockung (`flocculation`) | Optional, Default AN | Flockungsmittel-Dosierung |
| Cover-Steuerung (`cover_control`) | Optional, Default AN | Pool-Abdeckung mit Auf/Zu/Stopp |
| Rückspülung (`backwash`) | Optional, Default AN | Automatische Rückspülung + Spülung |
| PV-Überschuss (`pv_surplus`) | Optional, Default AN | Solar-Überschuss nutzen |
| LED-Beleuchtung (`led_lighting`) | Optional, Default AN | DMX-Szenen 1–12 |
| Wasserstand (`water_level`) | Optional, Default AUS | Skimmer / Füllstandsüberwachung |
| Wasser-Nachspeisung (`water_refill`) | Optional, Default AUS | Automatische Nachspeisung |
| Digitale Eingänge (`digital_inputs`) | Optional, Default AUS | DI1-DI12 + CE1-CE4 + Regeln |
| Erweiterungs-Ausgänge (`extension_outputs`) | Optional, Default AUS | EXT1.1-2.8 + OMNI_DC0-5 |

> 💡 **Standalone-Dosierung**-Modus lässt sich im Setup aktivieren, um die Dosier-Features zu isolieren, wenn der Controller ohne Basismodul betrieben wird.

---

## HA 2026 Kompatibilität

Diese Integration ist vollständig mit Home Assistant 2026.x kompatibel:

| Issue | Status | Fix |
|---------|--------|-----|
| `ZeroconfServiceInfo` entfernt | ✅ Behoben | `AsyncServiceInfo` aus `homeassistant.components.zeroconf` |
| `IssueSeverity` aus `components.repairs` entfernt | ✅ Behoben | Umzug nach `homeassistant.helpers.issue_registry` |

---

## 🔐 Sicherheitshinweise

⚠️ **WICHTIG**: Diese Integration steuert echte Poolausrüstung!

- ✅ Lies den **Haftungsausschluss** im Setup-Prozess sorgfältig
- ✅ Stelle sicher, dass du alle Sicherheitsmechanismen verstehst
- ✅ Halte jederzeit manuelle Not-Abschalter bereit
- ✅ Überwache deine Anlage regelmäßig persönlich
- ✅ Beachte die Sicherheitsdatenblätter aller verwendeten Chemikalien
- ✅ Befolge die Dokumentation deines Pool-Herstellers

> 📖 **Details**: [Sicherheit & Haftung](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md#-sicherheit--haftung)

---

## Links & Ressourcen

| Ressource | Link |
|-----------|------|
| GitHub Repository | https://github.com/Xerolux/violet-hass |
| Issues & Bugs | https://github.com/Xerolux/violet-hass/issues |
| HACS | https://hacs.xyz/ |
| Home Assistant | https://www.home-assistant.io/ |
| PoolDigital | https://www.pooldigital.de/ |
| Community Forum | https://community.home-assistant.io/ |
| Discord | https://discord.gg/Qa5fW2R |
| Buy Me a Coffee | https://buymeacoffee.com/xerolux |

---

*Diese Wiki dokumentiert Version **2.0.0-beta.7** der Violet Pool Controller Integration.*
*Zuletzt aktualisiert: 2026-06-15*
