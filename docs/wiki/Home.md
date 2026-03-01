# Violet Pool Controller – Home Assistant Integration

> **Die komplette Dokumentation** für das Violet Pool Controller Addon.
> Von der Installation bis zur Deinstallation – mit allen Features, States, Services und Automatisierungen.

---

## Was ist das Violet Pool Controller Addon?

Das **Violet Pool Controller Home Assistant Integration** verbindet [Home Assistant](https://www.home-assistant.io/) mit dem [Violet Pool Controller](https://www.pooldigital.de/) von PoolDigital GmbH & Co. KG. Es ermöglicht vollständige lokale Steuerung und Überwachung deiner Poolanlage – **ohne Cloud, ohne Abonnement**.

| Feature | Details |
|---------|---------|
| **Protokoll** | HTTP/HTTPS, lokales Polling |
| **HA-Mindestversion** | 2025.12.0 |
| **Python** | 3.12+ |
| **Version** | 1.0.3-alpha.1 |
| **Lizenz** | MIT |
| **Sprachen** | DE, EN, ES, FR, IT, NL, PL, PT, RU, ZH |

---

## Kernfunktionen

```
┌─────────────────────────────────────────────────────────┐
│              VIOLET POOL CONTROLLER ADDON               │
├──────────────┬──────────────┬──────────────┬────────────┤
│   Pumpe      │   Heizung    │   Solar      │ Dosierung  │
│  (3 Stufen)  │ (Thermostat) │ (PV-Surplus) │ pH/Cl/ORP  │
├──────────────┼──────────────┼──────────────┼────────────┤
│   Beleucht.  │   Abdeckung  │  Digit. I/O  │ Kalibrierung│
│ (DMX 1-8)   │  (Cover)     │  (DI1-DI8)   │ History    │
├──────────────┴──────────────┴──────────────┴────────────┤
│  100% lokal · Multi-Controller · SSL/TLS · Rate Limiting │
└─────────────────────────────────────────────────────────┘
```

### Plattformen & Entities

| Plattform | Entities | Beispiele |
|-----------|----------|-----------|
| **Sensor** | Temperaturen, pH, ORP, Chlor, Leitfähigkeit, AI1–AI8, Fehler-Codes | `sensor.violet_water_temperature` |
| **Binary Sensor** | Digitale Eingänge DI1–DI8, Alarme, Verbindungsstatus | `binary_sensor.violet_di1` |
| **Switch** | Pumpe, Heizer, Solar, pH±, Chlor, Flockmittel, DMX 1–8, Relais 1–8 | `switch.violet_pump` |
| **Climate** | Poolheizung (Thermostat), Solar-Heizung | `climate.violet_heater` |
| **Cover** | Poolabdeckung | `cover.violet_cover` |
| **Number** | Temperatursollwerte, pH-Ziel, ORP-Ziel, Dosierparameter | `number.violet_target_ph` |

---

## Schnell-Navigation

### Ich bin neu hier

1. **[Installation & Setup](Installation-and-Setup)** – HACS oder manuell installieren
2. **[Konfiguration](Configuration)** – Integration einrichten
3. **[Sensoren verstehen](Sensors)** – Welche Daten bekomme ich?
4. **[Device States](Device-States)** – Was bedeuten die 7 States?

### Ich will automatisieren

1. **[Services Referenz](Services)** – Alle verfügbaren Services
2. **[Automatisierungs-Beispiele](Automations)** – Copy-paste YAML-Beispiele
3. **[Pumpe steuern](Services#-service-control_pump)** – Geschwindigkeitssteuerung
4. **[Dosierung](Services#-service-smart_dosing)** – Chemikalien intelligent dosieren

### Ich habe ein Problem

1. **[Troubleshooting](Troubleshooting)** – Häufige Probleme & Lösungen
2. **[Erweiterte Protokollierung](Erweiterte-Protokollierung)** – Diagnose-Tools & Log-Export
3. **[Fehler-Codes](Error-Codes)** – Controller-Fehlercodes erklärt
4. **[FAQ](FAQ)** – 50+ häufige Fragen
5. **[GitHub Issues](https://github.com/Xerolux/violet-hass/issues)** – Bug-Reports

### Ich will mehrere Controller

→ **[Multi-Controller Guide](Multi-Controller)** – Mehrere Pools verwalten

### Ich will beitragen

→ **[Contributing Guide](Contributing)** – Pull Requests, Tests, Style Guide

---

## Architektur-Überblick

```
Home Assistant
    │
    ├── VioletPoolDataUpdateCoordinator (polling, 20s default)
    │       │
    │       ├── VioletPoolAPI (aiohttp, rate-limited, retry-logic)
    │       │       │
    │       │       └── Violet Pool Controller (HTTP/HTTPS)
    │       │               GET /getReadings?ALL
    │       │               GET /setFunctionManually?{payload}
    │       │               POST /setConfig
    │       │
    │       └── Entities (sensors, switches, climate, cover, number)
    │
    └── Services (control_pump, smart_dosing, manage_pv_surplus, ...)
```

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
| Pumpensteuerung | Immer | 3-Stufen-Pumpe mit Automatik |
| Heizung | Optional | Thermostat mit Solltemperatur |
| Solar | Optional | Solarkollektor + PV-Überschuss |
| pH-Dosierung | Optional | pH- und pH+ Dosierpumpen |
| Chlor-Dosierung | Optional | Chlor-Dosierpumpe |
| Flockmittel | Optional | Flockungsmittel-Dosierung |
| DMX-Beleuchtung | Optional | 8 Szenen steuerbar |
| Digitale Eingänge | Optional | DI1–DI8 für Sensoren/Schalter |
| Abdeckung | Optional | Pool-Cover mit Position |
| Erweiterungs-Relais | Optional | 8 zusätzliche Relais |
| Rückspülung | Optional | Automatische Rückspülung |
| PV-Überschuss | Optional | Solaranlage nutzen |

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

*Diese Wiki dokumentiert Version **1.0.3-alpha.1** des Violet Pool Controller Addons.*
*Zuletzt aktualisiert: 2026-02-28*
