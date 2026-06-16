> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Home.de)**

---

# 🏊 Violet Pool Controller – Home Assistant Integration


> **The complete documentation** for the Violet Pool Controller add-on.
> From installation to uninstallation – with all features, states, services, and automations.

---

## 📢 Latest Changes (v2.0.0)

### ✨ New Features & Improvements

#### 🧪 H2O2 Dosing
- **H2O2 dosing support**: Shares `DOS_1_CL` output with chlorine (selected via `from=3`).
- New service option `h2o2` for `manual_dosing_http`, `configure_dosing`, `set_dosing_target`, `set_dosing_daytime`, `set_dosing_max_daily`, `enable_dosing`.
- Corresponding error codes `0142`–`0145` mapped.

#### ⚡ Omni DC Outputs
- 6 new switchable outputs (`OMNI_DC0`–`OMNI_DC5`) exposed as switches, select controls and runtime sensors.

#### 🛠️ OMNI DC + DIRULE Switches
- `DIRULE_1`–`DIRULE_8` digital-input rule switches now exposed in the UI.
- All extension relays (`EXT1_1`–`EXT2_8`) configurable via select entities.

#### 🧯 Corrected State Mapping
- **Fixed**: State `2` (`AUTO_PRIO_OFF`) is now correctly **OFF** (was previously reported as ON).
- **Fixed**: All auto states map to `AUTO` mode in select entities.
- See [Device States](Device-States) for the corrected table.

#### 📊 New Sensor Categories
- **Runtime sensors**: Per-output daily runtimes for pump, solar, heater, light, backwash, refill, ECO, dosing channels, extension relays, OMNI DC motors, pump RPM levels.
- **Dosing statistics**: Daily dosing amount (ml) and remaining canister amount (ml) for every dosing channel.
- **Composite state sensors**: `PUMPSTATE`, `HEATERSTATE`, `SOLARSTATE` carry the full `BLOCKED_BY_*` / `WAITING_FOR_*` detail string.
- **Hardware binary sensors**: Base module, dosing module, both extension modules, standalone mode, DMX module, digital-rules module.
- **Overflow/backwash/bathing AI binary sensors**: overfill, dry-run, refill, backwash-delay, bathing-AI surveillance.

#### 🔧 HTTP Control & Rule-Management Services (Phase 2–4)
- New services: `control_heater_http`, `control_solar_http`, `control_cover_http`, `control_backwash_http`, `manual_dosing_http`, `configure_dosing`, `set_dosing_target`, `set_dosing_daytime`, `set_dosing_max_daily`, `enable_dosing`, `configure_temp_rule`, `configure_analog_rule`, `configure_switching_rule`, `configure_timer_rule`, `enable_rule`, `control_extension_relay`, `configure_sensor_calibration`.
- See [Services](Services) for the full reference.

---

## What is the Violet Pool Controller Add-on?

The **Violet Pool Controller Home Assistant Integration** connects [Home Assistant](https://www.home-assistant.io/) with the [Violet Pool Controller](https://www.pooldigital.de/) by PoolDigital GmbH & Co. KG. It enables complete local control and monitoring of your pool system – **no cloud, no subscription required**.

| Feature | Details |
|---------|---------|
| **Protocol** | HTTP/HTTPS, local polling |
| **HA Minimum Version** | 2026.5.0 |
| **Tested up to** | 2026.5.x / 2026.6.x |
| **Python** | Managed by Home Assistant 2026.5.0+ |
| **Integration Version** | 2.0.0 |
| **API Package** | violet-poolController-api ≥ 0.0.33 (PyPI) |
| **License** | AGPL-3.0-or-later |
| **Quality Scale** | Platinum |
| **Languages** | DE, EN, ES, FR, IT, NL, PL, PT, RU, ZH |

---

## Core Features

```
┌─────────────────────────────────────────────────────────┐
│              VIOLET POOL CONTROLLER ADD-ON               │
├──────────────┬──────────────┬──────────────┬────────────┤
│    Pump      │   Heating    │    Solar     │  Dosing    │
│ (3 speeds)   │ (Thermostat) │ (PV Surplus) │ pH/Cl/ORP  │
├──────────────┼──────────────┼──────────────┼────────────┤
│   Lighting   │    Cover     │  Digital I/O │ Diagnostics│
│ (DMX 1-12)   │   (Cover)    │ (DI1-DI12)   │  Download  │
├──────────────┼──────────────┼──────────────┼────────────┤
│ EXT1.1-2.8   │ OMNI_DC0-5   │ DIRULE_1-8   │ H2O2-Dos.  │
├──────────────┴──────────────┴──────────────┴────────────┤
│  100% local · Multi-Controller · SSL/TLS · Rate Limiting │
└─────────────────────────────────────────────────────────┘
```

### Platforms & Entities

| Platform | Entities | Examples |
|----------|----------|----------|
| **Sensor** | Temperatures (1-Wire 1-12), pH, ORP, chlorine, analog (ADC1-5, IMP1-2), runtimes, dosing statistics, composite states, system | `sensor.violet_pool_controller_onewire1_value` |
| **Binary Sensor** | Core states (PUMP/SOLAR/HEATER/...), digital inputs DI1-DI12, CE1-CE4, hardware modules, overflow/backwash/bathing-AI | `binary_sensor.violet_pool_controller_pump` |
| **Switch** | Pump, heater, solar, pH±, chlorine, electrolysis, flocculant, light, backwash, rinse, refill, ECO, PV surplus, EXT1.1-2.8, OMNI_DC0-5, DIRULE_1-8 | `switch.violet_pool_controller_pump` |
| **Light** | DMX scenes 1–12 (exposed as `LightEntity`) | `light.violet_pool_controller_dmx_scene1` |
| **Climate** | Pool heater (thermostat), solar heater | `climate.violet_pool_controller_heater` |
| **Cover** | Pool cover | `cover.violet_pool_controller_cover` |
| **Number** | Temperature setpoints, pH/ORP/chlorine target, pump speed, canister volumes | `number.violet_pool_controller_ph_setpoint` |
| **Select** | Mode selects (Off/On/Auto) for all switches, rules, extensions and OMNI outputs | `select.violet_pool_controller_pump_mode` |

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
    │       │       │   → PyPI package "violet-poolController-api"
    │       │       │     (developed in this monorepo, usable standalone)
    │       │       │
    │       │       └── Violet Pool Controller (HTTP/HTTPS)
    │       │               GET /getReadings?ALL
    │       │               GET /setFunctionManually?{payload}
    │       │               POST /triggerManualDosing (dosing outputs)
    │       │               POST /setConfig
    │       │
    │       └── Entities (sensors, switches, climate, cover, number, select)
    │
    ├── Services (control_pump, smart_dosing, manage_pv_surplus, ...)
    │
    └── Diagnostics (download diagnostics data via HA UI)
```

The HTTP client is maintained in this repository under `violet_poolcontroller_api/` and
published to PyPI — see **[Python API Package](API-Package)** for standalone usage.

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
| Filter Pump (`filter_control`) | Always | 3-speed pump with automatic mode |
| Heater (`heating`) | Optional, default ON | Thermostat with target temperature |
| Solar Absorber (`solar`) | Optional, default ON | Solar collector + PV surplus |
| pH Control (`ph_control`) | Optional, default ON | pH- and pH+ dosing pumps |
| Chlorine Control (`chlorine_control`) | Optional, default ON | Chlorine dosing, electrolysis, H2O2 |
| Flocculant Dosing (`flocculation`) | Optional, default ON | Flocculant dosing pump |
| Cover Control (`cover_control`) | Optional, default ON | Pool cover with open/close/stop |
| Backwash (`backwash`) | Optional, default ON | Automatic backwash + rinse |
| PV Surplus (`pv_surplus`) | Optional, default ON | Use solar surplus |
| LED Lighting (`led_lighting`) | Optional, default ON | DMX scenes 1–12 |
| Water Level (`water_level`) | Optional, default OFF | Skimmer / level monitoring |
| Water Refill (`water_refill`) | Optional, default OFF | Automatic water refill |
| Digital Inputs (`digital_inputs`) | Optional, default OFF | DI1-DI12 + CE1-CE4 + rules |
| Extension Outputs (`extension_outputs`) | Optional, default OFF | EXT1.1-2.8 + OMNI_DC0-5 |

> 💡 **Standalone Dosing** mode can be activated during setup to isolate the dosing features when the controller is used without a base module.

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

*This wiki documents version **2.0.0** of the Violet Pool Controller integration.*
*Last updated: 2026-06-15*
