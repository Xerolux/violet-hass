# Changelog – Version History

> All important changes to the Violet Pool Controller add-on.

---

## 🆕 March 2026 - Version 1.x

### ⚠️ BREAKING CHANGE

**Home Assistant 2026.5.0+ is now required!**
Due to core platform changes (specifically the removal of `ZeroconfServiceInfo` from `homeassistant.components.zeroconf`), this integration now requires Home Assistant version 2026.5.0 or newer. If you are running an older version, please upgrade Home Assistant before installing this update.



### 🔒 Safety & Liability (NEW!)

**Comprehensive disclaimer and safety notices**

#### ✨ New Features

- **Liability disclaimer in setup flow:**
  - Mandatory disclaimer during integration setup
  - Must be confirmed to proceed
  - Bilingual (German & English)

- **Extended documentation:**
  - Comprehensive safety notices in both languages
  - Detailed user responsibilities
  - References to manufacturer documentation
  - Checklists for safe operation

- **Prominent placement:**
  - Disclaimer integrated into setup process
  - Safety first in all documentation
  - Progressive warnings in wiki

#### 📄 Changed Files

**Code:**
- `custom_components/violet_pool_controller/config_flow.py`
  - `_get_disclaimer_text()` method extended
  - Comprehensive bilingual disclaimer
  - Mandatory confirmation required

**Documentation:**
- `docs/help/configuration-guide.de.md`
  - New section: "Safety & Liability"
  - Compliance checklists
  - Legal notices

- `docs/help/configuration-guide.en.md`
  - Mirrors German version
  - Consistent structure

#### 🔐 Content

**Disclaimer covers:**
- ⚠️ All safety risks during use
- 🔒 User responsibilities
- ⚖️ Warranty disclaimer
- 📖 References to documentation
- 🏗️ Standards compliance (VDE, DIN)
- 🧪 Chemical safety
- ⚡ Electrical safety
- 🔒 Operational safety

#### 📖 Documentation

- [Configuration Guide (DE)](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md)
- [Configuration Guide (EN)](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.en.md)

---

### 🎨 Icon Optimization (NEW!)

**All icons optimized and switched to MDI**

#### ✨ Summary

- **68+ icons optimized**
- **100% switched to Material Design Icons (MDI)**
- **Consistent, professional icon set**
- **No more broken icons**

#### 🔍 Analysis

**Problem:**
- Non-existent icons used (e.g. `mdi:pump-on`, `mdi:overflow`)
- Inconsistent icon styles (solid, outline, mixed)
- Missing icons on some entities
- User confusion

**Solution:**
- All icons replaced with verified MDI icons
- Consistently switched to solid icons
- Special icons for specific functions (e.g. `mdi:ph` for pH)
- All icons verified in [MDI Library](https://pictogrammers.com/library/mdi/)

#### 📊 Top 10 Icon Improvements

| Rank | Icon Change | Reason |
|------|-------------|--------|
| 🥇 | `mdi:flask` → **`mdi:ph`** | Real pH icon instead of flask |
| 🥈 | `mdi:water-percent` → **`mdi:water-sync`** | Overflow instead of percent |
| 🥉 | `mdi:refresh` → **`mdi:autorenew`** | Autorenew for cycle |
| 4 | `mdi:pump-on` → **`mdi:water-pump`** | Water pump exists |
| 5 | `mdi:radiator-disabled` → **`mdi:radiator`** | Simpler radiator |
| 6 | `mdi:lightbulb-on` → **`mdi:lightbulb`** | Standard lightbulb |
| 7 | `mdi:heat-exchange` → **`mdi:radiator`** | Heat exchanger clearer |
| 8 | `mdi:pool-thermometer` → **`mdi:pool`** | Simpler pool |
| 9 | `mdi:water-opacity` → **`mdi:water`** | Water instead of turbidity |
| 10 | `mdi:gauge-full` → **`mdi:gauge`** | Standard gauge |

#### 📄 Changed Files

**Code:**
- `custom_components/violet_pool_controller/const_sensors.py`
  - TEMP_SENSORS (6 icons)
  - WATER_CHEM_SENSORS (3 icons)
  - ANALOG_SENSORS (7 icons)
  - SYSTEM_SENSORS (7 icons)
  - STATUS_SENSORS (7 icons)
  - DOSING_STATE_SENSORS (5 icons)

- `custom_components/violet_pool_controller/const_features.py`
  - BINARY_SENSORS (11+ icons)
  - SWITCHES (11+ icons)
  - SELECT_CONTROLS (8 icons)
  - SETPOINT_DEFINITIONS (11 icons)

**Documentation:**
- `docs/wiki/Icon-Reference.md` (NEW)
- `docs/wiki/Entities.md` (Updated)

#### 🎨 All Icon Changes

**Temperature Sensors (6):**
- `onewire1_value`: `mdi:pool-thermometer` → `mdi:pool`
- `onewire2_value`: `mdi:thermometer-lines` → `mdi:thermometer`
- `onewire3_value`: `mdi:solar-power-variant` → `mdi:solar-power`
- `onewire4_value`: `mdi:heat-exchange` → `mdi:pipe-valve`
- `onewire5_value`: `mdi:heat-exchange` → `mdi:radiator`
- `onewire6_value`: `mdi:water-boiler-auto` → `mdi:water-boiler`

**Water Chemistry (3):**
- `pH_value`: `mdi:flask` → `mdi:ph` ⭐
- `orp_value`: `mdi:lightning-bolt` → `mdi:lightning-bolt-circle`
- `pot_value`: `mdi:water-opacity` → `mdi:water-plus`

**Analog Sensors (7):**
- `ADC1_value`: `mdi:gauge-full` → `mdi:gauge`
- `ADC2_value`: `mdi:water-percent` → `mdi:water-sync`
- `ADC3_value`: `mdi:arrow-left-right` → `mdi:swap-horizontal`
- `ADC4_value`: `mdi:gauge-full` → `mdi:gauge`
- `ADC5_value`: `mdi:wave-sine` → `mdi:sine-wave`
- `IMP1_value`: `mdi:pipe-valve-open` → `mdi:pipe-valve`
- `IMP2_value`: `mdi:pump` → `mdi:water-pump`

**System Sensors (7):**
- `CPU_TEMP`: `mdi:thermometer-high` → `mdi:thermometer-alert`
- `CPU_TEMP_CARRIER`: `mdi:chip` → `mdi:motherboard`
- `CPU_UPTIME`: `mdi:clock-outline` → `mdi:clock-time-eight`
- `SYSTEM_CPU_TEMPERATURE`: `mdi:thermometer` → `mdi:thermometer-check`
- `SYSTEM_CARRIER_CPU_TEMPERATURE`: `mdi:memory` → `mdi:memory`
- `SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE`: `mdi:memory` → `mdi:memory-lan`
- `SYSTEM_memoryusage`: `mdi:memory` → `mdi:memory-lan`

**Status Sensors (7):**
- `PUMP`: `mdi:pump` → `mdi:pump`
- `HEATER`: `mdi:radiator` → `mdi:radiator`
- `SOLAR`: `mdi:solar-power` → `mdi:solar-power`
- `BACKWASH`: `mdi:refresh` → `mdi:autorenew`
- `LIGHT`: `mdi:lightbulb` → `mdi:lightbulb`
- `PVSURPLUS`: `mdi:solar-power` → `mdi:solar-power`
- `FW`: `mdi:package` → `mdi:package-variant`

**Dosing Sensors (5):**
- `DOS_1_CL_STATE`: `mdi:flask-empty` → `mdi:flask-outline`
- `DOS_2_ELO_STATE`: `mdi:lightning-bolt` → `mdi:lightning-bolt`
- `DOS_4_PHM_STATE`: `mdi:flask-empty-remove` → `mdi:flask-minus`
- `DOS_5_PHP_STATE`: `mdi:flask-empty-plus` → `mdi:flask-plus`
- `DOS_6_FLOC_STATE`: `mdi:water-opacity` → `mdi:water`

**Binary Sensors (11+):**
- `PUMP`: `mdi:pump-on` → `mdi:water-pump`
- `SOLAR`: `mdi:solar-power-variant-outline` → `mdi:solar-power`
- `HEATER`: `mdi:radiator-disabled` → `mdi:radiator`
- `LIGHT`: `mdi:lightbulb-on` → `mdi:lightbulb`
- `BACKWASH`: `mdi:refresh` → `mdi:autorenew`
- `REFILL`: `mdi:water-plus` → `mdi:water`
- `ECO`: `mdi:leaf` → `mdi:leaf`
- `PVSURPLUS`: `mdi:solar-power-variant` → `mdi:solar-power`
- `CIRCULATION_STATE`: `mdi:water-alert` → `mdi:water-alert`
- `ELECTRODE_FLOW_STATE`: `mdi:water-check` → `mdi:water-check`
- `PRESSURE_STATE`: `mdi:gauge` → `mdi:gauge`
- `CAN_RANGE_STATE`: `mdi:bottle-tonic` → `mdi:bottle-tonic`

**Switches (11+):**
- `PUMP`: `mdi:pump-on` → `mdi:water-pump`
- `SOLAR`: `mdi:solar-power-variant` → `mdi:solar-power`
- `HEATER`: `mdi:radiator` → `mdi:radiator`
- `LIGHT`: `mdi:lightbulb-on` → `mdi:lightbulb`
- `DOS_5_PHP`: `mdi:flask-plus` → `mdi:flask-plus`
- `DOS_4_PHM`: `mdi:flask-minus` → `mdi:flask-minus`
- `DOS_1_CL`: `mdi:flask` → `mdi:flask-outline`
- `DOS_6_FLOC`: `mdi:water-plus` → `mdi:water`
- `PVSURPLUS`: `mdi:solar-power-variant` → `mdi:solar-power`
- `BACKWASH`: `mdi:refresh` → `mdi:autorenew`
- `BACKWASHRINSE`: `mdi:refresh` → `mdi:autorenew`

**Select Controls (8):**
- `pump_mode`: `mdi:water-pump` → `mdi:water-pump`
- `heater_mode`: `mdi:radiator-disabled` → `mdi:radiator`
- `solar_mode`: `mdi:solar-power-variant` → `mdi:solar-power`
- `light_mode`: `mdi:lightbulb-on` → `mdi:lightbulb`
- `dos_cl_mode`: `mdi:flask-empty` → `mdi:flask-outline`
- `dos_phm_mode`: `mdi:flask-empty-remove` → `mdi:flask-minus`
- `dos_php_mode`: `mdi:flask-plus` → `mdi:flask-plus`
- `pvsurplus_mode`: `mdi:solar-power-variant` → `mdi:solar-power`

**Setpoints (11):**
- `ph_setpoint`: `mdi:flask` → `mdi:ph` ⭐
- `orp_setpoint`: `mdi:lightning-bolt` → `mdi:lightning-bolt-circle`
- `chlorine_setpoint`: `mdi:water-plus` → `mdi:water-plus`
- `heater_target_temp`: `mdi:radiator` → `mdi:radiator`
- `solar_target_temp`: `mdi:solar-power` → `mdi:solar-power`
- `pump_speed`: `mdi:pump` → `mdi:pump`
- `chlorine_canister_volume`: `mdi:keg` → `mdi:barrel`
- `ph_minus_canister_volume`: `mdi:keg` → `mdi:barrel`
- `ph_plus_canister_volume`: `mdi:keg` → `mdi:barrel`
- `flocculant_canister_volume`: `mdi:keg` → `mdi:barrel`

#### 📚 Reference

- [Icon Reference](Icon-Reference) - All icons in detail
- [Icon Upgrade Summary](https://github.com/Xerolux/violet-hass/blob/main/ICON_UPGRADE_SUMMARY.md) - Detailed analysis

---

## 🐛 Bug Fixes

### March 2026

#### Missing Icons

**Problem:**
- Filter pump had no icon
- Overflow tank, heat exchanger, solar state, refill state, PV surplus were missing
- Icons were not displayed in Home Assistant

**Cause:**
- Non-existent MDI icons used:
  - `mdi:pump-on` - does not exist
  - `mdi:overflow` - does not exist
  - `mdi:heat-exchange` - does not exist
  - `mdi:solar-power-variant-outline` - does not exist
  - `mdi:water-plus` (original) - does not exist
  - `mdi:radiator-disabled` - does not exist
  - `mdi:lightbulb-on` - does not exist
  - And many more...

**Solution:**
- All icons replaced with existing MDI icons
- Verified in the [MDI Library](https://pictogrammers.com/library/mdi/)
- Consistent icon set introduced

**Status:** ✅ Resolved

---

## 🔄 Migration

### Updating from Older Versions

#### Icons

If you are updating from an older version:

1. **Restart Home Assistant:**
   ```
   Settings → System → Restart
   ```

2. **Clear browser cache:**
   ```
   CTRL + SHIFT + DELETE
   ```

3. **Update entity registry:**
   - Icons update automatically
   - No manual work needed

#### Disclaimer

If you are updating from a version without the disclaimer:

1. **Remove integration:**
   ```
   Settings → Devices & Services → Violet Pool Controller → "..." → Remove
   ```

2. **Re-add integration:**
   ```
   Settings → Devices & Services → + Add Integration
   ```

3. **Confirm disclaimer:**
   - Read the entire text
   - Check the box
   - Click "Confirm"

4. **Retain configuration:**
   - All settings are preserved
   - Feature selection is retained

---

## [1.0.5] – 2026-04-22 🟢 STABLE

### Version 1.0.5 Release

- feat: add translation_key to HW_* hardware binary sensors (10 languages) (13f82dd)
- fix: add missing reconfigure step to strings.json (aa0b7d2)
- feat: implement automatic hardware detection with api 0.0.10 including standalone dosing (7930810)
- feat: implement automatic hardware detection with api 0.0.10 (708a146)
- feat: Update API to 0.0.6 and add standalone dosing config (c4199ed)
- feat: Update API to 0.0.8 and add standalone dosing config (4cb47ce)

---

## [1.0.4] – 2026-03-02 🟡 BETA

### Version Step Alpha → Beta

- All known HA 2026 compatibility errors fixed.
- Diagnostics download feature completed.
- Documentation (README + Wiki) completely revised and updated.

---

## [1.0.3-alpha.2] – 2026-03-02 🔴 ALPHA

### Bugfixes (HA 2026 Compatibility)

- **ZeroconfServiceInfo removed**: `ZeroconfServiceInfo` was removed from `homeassistant.components.zeroconf`. Import in `config_flow.py` and `tests/test_discovery.py` switched to `AsyncServiceInfo`.
- **Repairs imports moved**: `IssueSeverity`, `async_create_issue`, and `async_delete_issue` were moved from `homeassistant.components.repairs` to `homeassistant.helpers.issue_registry`. Import in `device.py` updated accordingly.

### New Features

- **Diagnostics Download**: New `diagnostics.py` module added. A JSON file with complete debug information can now be downloaded from the device page in HA (configuration, device status, connection metrics, current readings, poll statistics). Passwords are automatically redacted.

### Documentation

- **README cleaned up**: README.md reduced to essentials (features + quickstart + wiki links). All details moved to the wiki.
- **Wiki updated**: Home page, sidebar, and changelog updated to version 1.0.3-alpha.2.
- **New wiki page Diagnostics**: Complete documentation of the diagnostics feature.

---

## [1.0.3-alpha.1] – 2026-02-28 🔴 ALPHA

### New Features

- **Quality Scale Progress:** Documentation of progress toward Quality Scale added (Gold Level ~85% complete).

### Improvements

- **Code Quality:** Type hints completed (Bronze Level 100% complete).
- **Bug fixes:** Fixed config flow handler issues.
- **HA 2026 Compatibility:** Fixes for Home Assistant 2026 compatibility and completion of Gold Level tests.
- **ZeroConf Discovery:** Fixes for ZeroConf Discovery (100% tests passing).

### Documentation

- **Enhanced Documentation:** Improved error handling, diagnostics, and documentation (Silver Level 100% complete).

### Compatibility
- Tested on Home Assistant 2025.12.0+
- Prepared for 2026.x versions
- aiohttp>=3.10.0 required

---

## [1.0.2] – 2026-02-26 ✅ STABLE

### New Features

**Diagnostic Service**
- New service: `export_diagnostic_logs`
- Export up to 10,000 log lines for troubleshooting
- Optionally save to file for support tickets
- With timestamps and flexible line count
- Export now also includes installed components and Home Assistant system info.

### Improvements

**Error Handling**
- Better recovery mechanisms on connection loss
- Extended logging capabilities

**Wiki & Documentation**
- Updated services documentation
- New log export tips in troubleshooting
- Extended SSL/TLS documentation

### Compatibility
- Tested on Home Assistant 2025.12.0+
- Prepared for 2026.x versions
- aiohttp>=3.10.0 required

---

## [1.0.1] – 2026-02-22 ✅ STABLE

### Critical Bugfixes

**Contact Sensor State Class**
- Sensors returned string values (`'RELEASED'`/`'TRIGGERED'`) with numeric `state_class`
- Fix: Runtime override in `VioletSensor.state_class` property

**Other critical fixes in this release:**
- Improvements to sensor display
- Corrections to configuration updates
- Improved session management

### Upgrading to 1.0.1

**HACS:**
1. HACS → Integrations
2. "Violet Pool Controller" → Update
3. Restart Home Assistant

**Manually:**
```bash
cd /config/custom_components
rm -rf violet_pool_controller
# Extract ZIP from GitHub Release
```

---

## [1.0.0] – 2026-02-22 ✅ STABLE

### First Stable Release!

#### New Features
- Complete Home Assistant integration for Violet Pool Controller
- Multi-controller support (multiple pools simultaneously)
- Automatic area assignment

#### Platforms
- **Sensor**: Temperatures, pH, ORP, chlorine, conductivity, AI1–AI8, error codes
- **Binary Sensor**: Digital inputs DI1–DI8, alarms, connection status
- **Switch**: Pump, heater, solar, pH±, chlorine, flocculant, DMX 1–8, relays 1–8
- **Climate**: Pool heater, solar heater (thermostat)
- **Cover**: Pool cover with position
- **Number**: Setpoints for temperature, pH, ORP, dosing

#### Services
- `control_pump` – Pump control with speed
- `smart_dosing` – Intelligent chemical dosing
- `manage_pv_surplus` – PV surplus management
- `control_dmx_scenes` – DMX lighting scenes
- `set_light_color_pulse` – Light color pulses
- `manage_digital_rules` – Digital input rules
- `test_output` – Diagnostic test mode

#### Security
- Token bucket rate limiting
- Input sanitization (XSS, SQL injection, command injection)
- SSL/TLS certificate verification (default: on)
- Thread-safe locking with documented ordering

#### Auto-Recovery
- Exponential backoff: 10s → 300s
- Max 10 retry attempts
- Intelligent error logging (throttling every 5 minutes)

#### Translations
- DE, EN, ES, FR, IT, NL, PL, PT, RU, ZH

---

## [0.2.1-beta.1] – 2025-11-20 🧪 BETA

### Multi-Controller Support

#### New
- Controller name field during setup
- Automatic area assignment (`suggested_area`)
- Improved visual separation in dashboard

#### Technical
- New constant: `CONF_CONTROLLER_NAME`
- Device info uses `controller_name`
- Entry title shows controller name

#### Backward Compatibility
- Existing installations continue to work
- Default name: "Violet Pool Controller"

---

## [0.2.0] – 2025-10-15 🧪 BETA

### Major Restructuring

#### Changes
- Modular constants (`const_api.py`, `const_devices.py`, `const_sensors.py`, `const_features.py`)
- Rate limiter as separate module (`utils_rate_limiter.py`)
- Input sanitizer (`utils_sanitizer.py`)
- Error code mapping (`error_codes.py`)

#### New Entities
- Calibration history sensors
- Analog inputs AI1–AI8
- Extension relays 1–8

---

## [0.1.0] – 2025-08-01 🧪 ALPHA

### First Public Release

#### Features
- Basic HTTP API communication
- Sensor entities for temperatures and chemical values
- Simple switch entities for pump and heater
- Config flow for setup

---

## Breaking Changes

### 1.0.0 → 1.0.1

No breaking changes. Direct upgrade possible.

### 0.2.x → 1.0.0

- Minimum HA version: **2025.12.0** (previously 2024.12.0)
- Python: **3.12+** required
- Type annotations: `X | None` instead of `Optional[X]`

### 0.1.x → 0.2.x

- Constants reorganized (import from `const.py` still possible)
- Entity IDs may have changed (reinstallation recommended)

---

## Upgrade Guide

### Via HACS (Recommended)

1. HACS → Integrations
2. Find Violet Pool Controller
3. Click "Update"
4. Restart HA
5. Settings → Devices & Services → check integration

### Manually

```bash
# Create backup!
cp -r /config/custom_components/violet_pool_controller \
       /config/backup_violet_$(date +%Y%m%d)

# Install new version
cd /config/custom_components
rm -rf violet_pool_controller
# Extract ZIP or git pull

# Restart HA
```

---

## Links

- [GitHub Releases](https://github.com/Xerolux/violet-hass/releases)
- [Complete Changelog on GitHub](https://github.com/Xerolux/violet-hass/blob/main/docs/CHANGELOG.md)
- [Report a Bug](https://github.com/Xerolux/violet-hass/issues/new?template=bug_report.md)
- [Request a Feature](https://github.com/Xerolux/violet-hass/issues/new?template=feature_request.md)

---

*Back: [API Reference](API-Reference) | Back: [Home](Home)*
