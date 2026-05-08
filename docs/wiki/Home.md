# 🏊 Violet Pool Controller – Home Assistant Integration

**English** | **[Deutsch](Home.de)**

> **The complete documentation** for the Violet Pool Controller add-on.
> From installation to uninstallation – with all features, states, services, and automations.

---

## 📢 Latest Changes (March 2026)

### ✨ New Features & Improvements

#### 🔒 Safety & Liability (NEW!)
- **Comprehensive disclaimer**: Liability disclaimer for safety and usage
- **German & English**: Complete safety notices in both languages
- **Setup integration**: Mandatory liability disclaimer in the configuration process
- 📖 [Configuration Guide (DE)](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md)
- 📖 [Configuration Guide (EN)](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.en.md)

#### 🎨 Icon Optimization (NEW!)
- **68+ icons optimized**: All entities now with consistent, professional MDI icons
- **Better recognition**: Special icons instead of generic symbols
- **Examples**:
  - pH value: `mdi:ph` instead of `mdi:flask`
  - Pool water: `mdi:pool`
  - Overflow tank: `mdi:water-sync`
  - Heat exchanger: `mdi:radiator`
  - Backwash: `mdi:autorenew`
  - Flocculant: `mdi:water`
- 📖 [Icon Reference](Icon-Reference) | 📊 [All Icons](https://github.com/Xerolux/violet-hass/blob/main/ICON_UPGRADE_SUMMARY.md)

---

## What is the Violet Pool Controller Add-on?

The **Violet Pool Controller Home Assistant Integration** connects [Home Assistant](https://www.home-assistant.io/) with the [Violet Pool Controller](https://www.pooldigital.de/) by PoolDigital GmbH & Co. KG. It enables complete local control and monitoring of your pool system – **no cloud, no subscription required**.

| Feature | Details |
|---------|---------|
| **Protocol** | HTTP/HTTPS, local polling |
| **HA Minimum Version** | 2026.5.0 |
| **Tested up to** | 2026.x (current) |
| **Python** | 3.14.2+ |
| **Version** | 1.0.5 |
| **License** | MIT |
| **Languages** | DE, EN, ES, FR, IT, NL, PL, PT, RU, ZH |

---

## Core Features

```
┌─────────────────────────────────────────────────────────┐
│              VIOLET POOL CONTROLLER ADD-ON               │
├──────────────┬──────────────┬──────────────┬────────────┤
│    Pump      │   Heating    │    Solar     │  Dosing    │
│  (3 stages)  │ (Thermostat) │ (PV Surplus) │ pH/Cl/ORP  │
├──────────────┼──────────────┼──────────────┼────────────┤
│   Lighting   │    Cover     │  Digital I/O │ Diagnostics│
│ (DMX 1-8)    │   (Cover)    │  (DI1-DI8)   │  Download  │
├──────────────┴──────────────┴──────────────┴────────────┤
│  100% local · Multi-Controller · SSL/TLS · Rate Limiting │
└─────────────────────────────────────────────────────────┘
```

### Platforms & Entities

| Platform | Entities | Examples |
|----------|----------|----------|
| **Sensor** | Temperatures, pH, ORP, chlorine, conductivity, AI1–AI8, error codes | `sensor.violet_water_temperature` |
| **Binary Sensor** | Digital inputs DI1–DI8, alarms, connection status | `binary_sensor.violet_di1` |
| **Switch** | Pump, heater, solar, pH±, chlorine, flocculant, DMX 1–8, relays 1–8 | `switch.violet_pump` |
| **Climate** | Pool heater (thermostat), solar heater | `climate.violet_heater` |
| **Cover** | Pool cover | `cover.violet_cover` |
| **Number** | Temperature setpoints, pH target, ORP target, dosing parameters | `number.violet_target_ph` |

---

## Quick Navigation

### I'm new here

1. **[Installation & Setup](Installation-and-Setup)** – Install via HACS or manually
2. **[Configuration](Configuration)** – Set up the integration
3. **[Entities](Entities)** – All sensors, switches, climate
4. **[Understanding Sensors](Sensors)** – What data do I get?
5. **[Device States](Device-States)** – What do the 7 states mean?

### I want to automate

1. **[Services Reference](Services)** – All available services
2. **[Automation Examples](Automations)** – Copy-paste YAML examples
3. **[Control Pump](Services#-service-control_pump)** – Speed control
4. **[Dosing](Services#-service-smart_dosing)** – Intelligent chemical dosing

### I have a problem

1. **[Troubleshooting](Troubleshooting)** – Common problems & solutions
2. **[Download Diagnostics](Diagnostics)** – JSON export for bug reports
3. **[Advanced Logging](Erweiterte-Protokollierung)** – Diagnostic tools & log export
4. **[Error Codes](Error-Codes)** – Controller error codes explained
5. **[FAQ](FAQ)** – 50+ common questions
6. **[GitHub Issues](https://github.com/Xerolux/violet-hass/issues)** – Bug reports

### I want to use multiple controllers

→ **[Multi-Controller Guide](Multi-Controller)** – Manage multiple pools

### I want to contribute

→ **[Contributing Guide](Contributing)** – Pull requests, tests, style guide

---

## Architecture Overview

```
Home Assistant
    │
    ├── VioletPoolDataUpdateCoordinator (polling, 10s default)
    │       │
    │       ├── VioletPoolAPI (aiohttp, rate-limited, retry-logic, SSL)
    │       │       │
    │       │       └── Violet Pool Controller (HTTP/HTTPS)
    │       │               GET /getReadings?ALL
    │       │               GET /setFunctionManually?{payload}
    │       │               POST /setConfig
    │       │
    │       └── Entities (sensors, switches, climate, cover, number)
    │
    ├── Services (control_pump, smart_dosing, manage_pv_surplus, ...)
    │
    └── Diagnostics (download diagnostics data via HA UI)
```

### Security Features

- **Rate Limiting**: Token bucket algorithm prevents controller overload
- **Input Sanitization**: Protection against XSS, SQL injection, command injection
- **SSL/TLS**: Certificate verification enabled by default
- **Auto-Recovery**: Exponential backoff (10s → 300s), max 10 attempts
- **Thread Safety**: Two documented locks without nesting

---

## Supported Controller Features

| Feature | Selectable in Setup | Description |
|---------|---------------------|-------------|
| Pump Control | Always | 3-stage pump with automatic mode |
| Heating | Optional | Thermostat with target temperature |
| Standalone Dosing | Optional | Isolates dosing features, blocks main devices |
| Solar | Optional | Solar collector + PV surplus |
| pH Dosing | Optional | pH- and pH+ dosing pumps |
| Chlorine Dosing | Optional | Chlorine dosing pump |
| Flocculant | Optional | Flocculant dosing |
| DMX Lighting | Optional | 8 controllable scenes |
| Digital Inputs | Optional | DI1–DI8 for sensors/switches |
| Cover | Optional | Pool cover with position |
| Extension Relays | Optional | 8 additional relays |
| Backwash | Optional | Automatic backwash |
| PV Surplus | Optional | Use solar surplus |

---

## HA 2026 Compatibility

This integration is fully compatible with Home Assistant 2026.x:

| Issue | Status | Fix |
|-------|--------|-----|
| `ZeroconfServiceInfo` removed | ✅ Fixed | `AsyncServiceInfo` from `homeassistant.components.zeroconf` |
| `IssueSeverity` from `components.repairs` removed | ✅ Fixed | Moved to `homeassistant.helpers.issue_registry` |

---

## 🔐 Safety Notices

⚠️ **IMPORTANT**: This integration controls real pool equipment!

- ✅ Read the **liability disclaimer** in the setup process carefully
- ✅ Make sure you understand all safety mechanisms
- ✅ Always keep manual emergency shutoffs available
- ✅ Personally monitor your system regularly
- ✅ Observe the safety data sheets for all chemicals used
- ✅ Follow your pool manufacturer's documentation

> 📖 **Details**: [Safety & Liability](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md#-sicherheit--haftung)

---

## Links & Resources

| Resource | Link |
|----------|------|
| GitHub Repository | https://github.com/Xerolux/violet-hass |
| Issues & Bugs | https://github.com/Xerolux/violet-hass/issues |
| HACS | https://hacs.xyz/ |
| Home Assistant | https://www.home-assistant.io/ |
| PoolDigital | https://www.pooldigital.de/ |
| Community Forum | https://community.home-assistant.io/ |
| Discord | https://discord.gg/Qa5fW2R |
| Buy Me a Coffee | https://buymeacoffee.com/xerolux |

---

*This wiki documents version **1.0.5** of the Violet Pool Controller add-on.*
*Last updated: 2026-04-01*
