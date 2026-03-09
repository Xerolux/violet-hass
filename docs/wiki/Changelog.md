# Changelog – Versionshistorie

> Alle wichtigen Änderungen am Violet Pool Controller Addon.

---

## 🆕 März 2026 - Version 1.x

### 🔒 Sicherheit & Haftung (NEU!)

**Umfassender Disclaimer und Sicherheitshinweise**

#### ✨ Neue Funktionen

- **Haftungsausschluss im Setup-Flow:**
  - Verbindlicher Disclaimer beim Einrichten der Integration
  - Muss bestätigt werden um fortzufahren
  - Bilingual (Deutsch & Englisch)

- **Erweiterte Dokumentation:**
  - Umfassende Sicherheitshinweise in beiden Sprachen
  - Detaillierte Benutzer-Verantwortlichkeiten
  - Referenz zu Hersteller-Dokumentationen
  - Checklisten für sicheren Betrieb

- **Prominente Platzierung:**
  - Disclaimer in Setup-Prozess integriert
  - Sicherheit an erster Stelle in allen Dokumentationen
  - Degressive Warnungen in Wiki

#### 📄 Geänderte Dateien

**Code:**
- `custom_components/violet_pool_controller/config_flow.py`
  - `_get_disclaimer_text()` Methode erweitert
  - Umfassender bilingualer Disclaimer
  - Verbindliche Bestätigung erforderlich

**Dokumentation:**
- `docs/help/configuration-guide.de.md`
  - Neue Sektion: "Sicherheit & Haftung"
  - Checklisten für Compliance
  - Rechtliche Hinweise

- `docs/help/configuration-guide.en.md`
  - Spiegelt deutsche Version
  - Konsistente Struktur

#### 🔐 Inhalt

**Haftungsausschluss deckt ab:**
- ⚠️ Alle Sicherheitsrisiken bei der Nutzung
- 🔒 Verantwortlichkeiten des Benutzers
- ⚖️ Gewährleistungsausschluss
- 📖 Verweise auf Dokumentationen
- 🏗️ Einhaltung von Normen (VDE, DIN)
- 🧪 Chemische Sicherheit
- ⚡ Elektrische Sicherheit
- 🔒 Betriebliche Sicherheit

#### 📖 Dokumentation

- [Konfigurationshilfe (DE)](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md)
- [Konfigurationshilfe (EN)](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.en.md)

---

### 🎨 Icon-Optimierung (NEU!)

**Alle Icons optimiert und zu MDI gewechselt**

#### ✨ Zusammenfassung

- **68+ Icons optimiert**
- **100% zu Material Design Icons (MDI) gewechselt**
- **Konsistentes, professionelles Icon-Set**
- **Keine defekten Icons mehr**

#### 🔍 Analyse

**Problem:**
- Nicht existente Icons verwendet (z.B. `mdi:pump-on`, `mdi:overflow`)
- Inkonsistente Icon-Stile (solid, outline, gemischt)
- Fehlende Icons bei einigen Entities
- Verwirrung bei Benutzern

**Lösung:**
- Alle Icons gegen verifizierte MDI-Icons ausgetauscht
- Konsistent zu soliden Icons gewechselt
- Spezielle Icons für spezielle Funktionen (z.B. `mdi:ph` für pH)
- Alle Icons in [MDI Library](https://pictogrammers.com/library/mdi/) verifiziert

#### 📊 Top 10 Icon-Verbesserungen

| Platz | Icon-Wechsel | Grund |
|-------|--------------|--------|
| 🥇 | `mdi:flask` → **`mdi:ph`** | Echtes pH-Icon statt Flasche |
| 🥈 | `mdi:water-percent` → **`mdi:water-sync`** | Überlauf statt Prozent |
| 🥉 | `mdi:refresh` → **`mdi:autorenew`** | Autorenew für Zyklus |
| 4 | `mdi:pump-on` → **`mdi:water-pump`** | Wasserpumpe existiert |
| 5 | `mdi:radiator-disabled` → **`mdi:radiator`** | Heizkörper einfacher |
| 6 | `mdi:lightbulb-on` → **`mdi:lightbulb`** | Glühbirne Standard |
| 7 | `mdi:heat-exchange` → **`mdi:radiator`** | Wärmetauscher klarer |
| 8 | `mdi:pool-thermometer` → **`mdi:pool`** | Pool einfacher |
| 9 | `mdi:water-opacity` → **`mdi:water`** | Wasser statt Trübung |
| 10 | `mdi:gauge-full` → **`mdi:gauge`** | Messanzeige Standard |

#### 📄 Geänderte Dateien

**Code:**
- `custom_components/violet_pool_controller/const_sensors.py`
  - TEMP_SENSORS (6 Icons)
  - WATER_CHEM_SENSORS (3 Icons)
  - ANALOG_SENSORS (7 Icons)
  - SYSTEM_SENSORS (7 Icons)
  - STATUS_SENSORS (7 Icons)
  - DOSING_STATE_SENSORS (5 Icons)

- `custom_components/violet_pool_controller/const_features.py`
  - BINARY_SENSORS (11+ Icons)
  - SWITCHES (11+ Icons)
  - SELECT_CONTROLS (8 Icons)
  - SETPOINT_DEFINITIONS (11 Icons)

**Dokumentation:**
- `docs/wiki/Icon-Reference.md` (NEU)
- `docs/wiki/Entities.md` (Aktualisiert)

#### 🎨 Alle Icon-Änderungen

**Temperatursensoren (6):**
- `onewire1_value`: `mdi:pool-thermometer` → `mdi:pool`
- `onewire2_value`: `mdi:thermometer-lines` → `mdi:thermometer`
- `onewire3_value`: `mdi:solar-power-variant` → `mdi:solar-power`
- `onewire4_value`: `mdi:heat-exchange` → `mdi:pipe-valve`
- `onewire5_value`: `mdi:heat-exchange` → `mdi:radiator`
- `onewire6_value`: `mdi:water-boiler-auto` → `mdi:water-boiler`

**Wasserchemie (3):**
- `pH_value`: `mdi:flask` → `mdi:ph` ⭐
- `orp_value`: `mdi:lightning-bolt` → `mdi:lightning-bolt-circle`
- `pot_value`: `mdi:water-opacity` → `mdi:water-plus`

**Analogsensoren (7):**
- `ADC1_value`: `mdi:gauge-full` → `mdi:gauge`
- `ADC2_value`: `mdi:water-percent` → `mdi:water-sync`
- `ADC3_value`: `mdi:arrow-left-right` → `mdi:swap-horizontal`
- `ADC4_value`: `mdi:gauge-full` → `mdi:gauge`
- `ADC5_value`: `mdi:wave-sine` → `mdi:sine-wave`
- `IMP1_value`: `mdi:pipe-valve-open` → `mdi:pipe-valve`
- `IMP2_value`: `mdi:pump` → `mdi:water-pump`

**System-Sensoren (7):**
- `CPU_TEMP`: `mdi:thermometer-high` → `mdi:thermometer-alert`
- `CPU_TEMP_CARRIER`: `mdi:chip` → `mdi:motherboard`
- `CPU_UPTIME`: `mdi:clock-outline` → `mdi:clock-time-eight`
- `SYSTEM_CPU_TEMPERATURE`: `mdi:thermometer` → `mdi:thermometer-check`
- `SYSTEM_CARRIER_CPU_TEMPERATURE`: `mdi:memory` → `mdi:memory`
- `SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE`: `mdi:memory` → `mdi:memory-lan`
- `SYSTEM_memoryusage`: `mdi:memory` → `mdi:memory-lan`

**Status-Sensoren (7):**
- `PUMP`: `mdi:pump` → `mdi:pump`
- `HEATER`: `mdi:radiator` → `mdi:radiator`
- `SOLAR`: `mdi:solar-power` → `mdi:solar-power`
- `BACKWASH`: `mdi:refresh` → `mdi:autorenew`
- `LIGHT`: `mdi:lightbulb` → `mdi:lightbulb`
- `PVSURPLUS`: `mdi:solar-power` → `mdi:solar-power`
- `FW`: `mdi:package` → `mdi:package-variant`

**Dosier-Sensoren (5):**
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

#### 📚 Referenz

- [Icon-Referenz](Icon-Reference) - Alle Icons im Detail
- [Icon Upgrade Summary](https://github.com/Xerolux/violet-hass/blob/main/ICON_UPGRADE_SUMMARY.md) - Detaillierte Analyse

---

## 🐛 Bug Fixes

### März 2026

#### Icons fehlten

**Problem:**
- Filterpumpe hatte kein Symbol
- Überlaufbehälter, Wärmetauscher, Solar State, Refill State, PV Surplus fehlten
- Icons wurden in Home Assistant nicht angezeigt

**Ursache:**
- Nicht existente MDI-Icons verwendet:
  - `mdi:pump-on` - existiert nicht
  - `mdi:overflow` - existiert nicht
  - `mdi:heat-exchange` - existiert nicht
  - `mdi:solar-power-variant-outline` - existiert nicht
  - `mdi:water-plus` (ursprünglich) - existiert nicht
  - `mdi:radiator-disabled` - existiert nicht
  - `mdi:lightbulb-on` - existiert nicht
  - Und viele mehr...

**Lösung:**
- Alle Icons gegen existierende MDI-Icons ausgetauscht
- Verifiziert in der [MDI Library](https://pictogrammers.com/library/mdi/)
- Konsistentes Set eingeführt

**Status:** ✅ Gelöst

---

## 🔄 Migration

### Von älteren Versionen aktualisieren

#### Icons

Wenn du von einer älteren Version aktualisierst:

1. **Home Assistant neu starten:**
   ```
   Einstellungen → System → Neustart
   ```

2. **Browser-Cache leeren:**
   ```
   STRG + UMSCHALT + ENTF
   ```

3. **Entity-Registry aktualisieren:**
   - Icons aktualisieren sich automatisch
   - Keine manuelle Arbeit nötig

#### Disclaimer

Wenn du von einer Version ohne Disclaimer aktualisierst:

1. **Integration entfernen:**
   ```
   Einstellungen → Geräte & Dienste → Violet Pool Controller → "..." → Entfernen
   ```

2. **Integration neu hinzufügen:**
   ```
   Einstellungen → Geräte & Dienste → + Integration hinzufügen
   ```

3. **Disclaimer bestätigen:**
   - Lies den gesamten Text
   - Setze das Häkchen
   - Klicke auf "Bestätigen"

4. **Konfiguration übernehmen:**
   - Alle Einstellungen bleiben erhalten
   - Feature-Auswahl wird übernommen

---

## [1.0.3-beta.1] – 2026-03-02 🟡 BETA

### Versionsschritt Alpha → Beta

- Alle bekannten HA 2026 Kompatibilitätsfehler behoben.
- Diagnosedaten-Download Feature fertiggestellt.
- Dokumentation (README + Wiki) vollständig überarbeitet und aktualisiert.

---

## [1.0.3-alpha.2] – 2026-03-02 🔴 ALPHA

### Bugfixes (HA 2026 Kompatibilität)

- **ZeroconfServiceInfo entfernt**: `ZeroconfServiceInfo` wurde aus `homeassistant.components.zeroconf` entfernt. Import in `config_flow.py` und `tests/test_discovery.py` auf `AsyncServiceInfo` umgestellt.
- **Repairs-Imports verschoben**: `IssueSeverity`, `async_create_issue` und `async_delete_issue` wurden aus `homeassistant.components.repairs` in `homeassistant.helpers.issue_registry` verschoben. Import in `device.py` entsprechend aktualisiert.

### Neue Features

- **Diagnosedaten-Download**: Neues `diagnostics.py` Modul hinzugefügt. Über die Geräteseite in HA kann jetzt eine JSON-Datei mit vollständigen Debug-Informationen heruntergeladen werden (Konfiguration, Gerätestatus, Verbindungsmetriken, aktuelle Messwerte, Poll-Statistiken). Passwörter werden automatisch geschwärzt.

### Dokumentation

- **README bereinigt**: README.md auf das Wesentliche (Features + Schnellstart + Wiki-Links) reduziert. Alle Details wurden in das Wiki ausgelagert.
- **Wiki aktualisiert**: Home-Seite, Sidebar und Changelog auf Version 1.0.3-alpha.2 aktualisiert.
- **Neue Wiki-Seite Diagnostics**: Vollständige Dokumentation der Diagnosedaten-Funktion.

---

## [1.0.3-alpha.1] – 2026-02-28 🔴 ALPHA

### Neue Features

- **Quality Scale Progress:** Dokumentation des Fortschritts zur Quality Scale hinzugefügt (Gold Level ~85% abgeschlossen).

### Verbesserungen

- **Code Quality:** Type Hints vervollständigt (Bronze Level 100% abgeschlossen).
- **Fehlerbehebung:** Behebung von Config Flow Handler Problemen.
- **HA 2026 Kompatibilität:** Fixes für Home Assistant 2026 Kompatibilität und Abschluss von Gold Level Tests.
- **ZeroConf Discovery:** Fixes für ZeroConf Discovery (100% Tests erfolgreich).

### Dokumentation

- **Enhanced Documentation:** Verbesserte Fehlerbehandlung, Diagnostics und Dokumentation (Silver Level 100% abgeschlossen).

### Kompatibilität
- Getestet auf Home Assistant 2025.12.0+
- Vorbereitet für 2026.x Versionen
- aiohttp>=3.10.0 erforderlich

---

## [1.0.2] – 2026-02-26 ✅ STABLE

### Neue Features

**Diagnostic Service**
- Neuer Service: `export_diagnostic_logs`
- Exportiere bis zu 10.000 Log-Zeilen für Troubleshooting
- Optional in Datei speichern für Support-Tickets
- Mit Timestamps und flexibler Zeilenanzahl
- Export enthält nun auch installierte Komponenten und Home Assistant System-Infos.

### Verbesserungen

**Fehlerbehandlung**
- Bessere Recovery-Mechanismen bei Verbindungsverlust
- Erweiterte Logging-Fähigkeiten

**Wiki & Dokumentation**
- Aktualisierte Services-Dokumentation
- Neue Log-Export-Tipps in Troubleshooting
- Erweiterte SSL/TLS-Dokumentation

### Kompatibilität
- Getestet auf Home Assistant 2025.12.0+
- Vorbereitet für 2026.x Versionen
- aiohttp>=3.10.0 erforderlich

---

## [1.0.1] – 2026-02-22 ✅ STABLE

### Kritische Bugfixes

**Contact Sensor State Class**
- Sensoren gaben String-Werte (`'RELEASED'`/`'TRIGGERED'`) mit numerischer `state_class` zurück
- Fix: Runtime-Override in `VioletSensor.state_class` Property

**Weitere kritische Fixes in diesem Release:**
- Verbesserungen der Sensor-Anzeige
- Korrekturen bei Konfigurations-Updates
- Session-Management verbessert

### Upgraden auf 1.0.1

**HACS:**
1. HACS → Integrationen
2. „Violet Pool Controller" → Aktualisieren
3. Home Assistant neu starten

**Manuell:**
```bash
cd /config/custom_components
rm -rf violet_pool_controller
# ZIP von GitHub Release extrahieren
```

---

## [1.0.0] – 2026-02-22 ✅ STABLE

### Erstes stabiles Release!

#### Neue Features
- Vollständige Home Assistant Integration für Violet Pool Controller
- Multi-Controller Support (mehrere Pools gleichzeitig)
- Automatische Bereichszuweisung (Areas)

#### Plattformen
- **Sensor**: Temperaturen, pH, ORP, Chlor, Leitfähigkeit, AI1–AI8, Fehlercodes
- **Binary Sensor**: Digitaleingänge DI1–DI8, Alarme, Verbindungsstatus
- **Switch**: Pumpe, Heizung, Solar, pH±, Chlor, Flockmittel, DMX 1–8, Relais 1–8
- **Climate**: Poolheizung, Solarheizung (Thermostat)
- **Cover**: Poolabdeckung mit Position
- **Number**: Sollwerte für Temperatur, pH, ORP, Dosierung

#### Services
- `control_pump` – Pumpensteuerung mit Geschwindigkeit
- `smart_dosing` – Intelligente Chemikaliendosierung
- `manage_pv_surplus` – PV-Überschuss-Management
- `control_dmx_scenes` – DMX-Beleuchtungsszenen
- `set_light_color_pulse` – Lichtfarb-Pulse
- `manage_digital_rules` – Digitale Eingangsregeln
- `test_output` – Diagnose-Testmodus

#### Sicherheit
- Token-Bucket Rate Limiting
- Input Sanitization (XSS, SQL-Injection, Command-Injection)
- SSL/TLS Zertifikats-Verifikation (Standard: aktiv)
- Thread-Safe Locking mit dokumentierter Reihenfolge

#### Auto-Recovery
- Exponentielles Backoff: 10s → 300s
- Max. 10 Wiederholungsversuche
- Intelligentes Fehler-Logging (Throttling alle 5 Minuten)

#### Übersetzungen
- DE, EN, ES, FR, IT, NL, PL, PT, RU, ZH

---

## [0.2.1-beta.1] – 2025-11-20 🧪 BETA

### Multi-Controller Support

#### Neu
- Controller-Name-Feld beim Setup
- Automatische Bereichszuweisung (`suggested_area`)
- Verbesserte visuelle Trennung im Dashboard

#### Technisch
- Neue Konstante: `CONF_CONTROLLER_NAME`
- Device-Info verwendet `controller_name`
- Entry-Title zeigt Controller-Name

#### Abwärtskompatibilität
- Bestehende Installationen funktionieren weiter
- Default-Name: „Violet Pool Controller"

---

## [0.2.0] – 2025-10-15 🧪 BETA

### Große Umstrukturierung

#### Änderungen
- Modulare Konstanten (`const_api.py`, `const_devices.py`, `const_sensors.py`, `const_features.py`)
- Rate Limiter als separates Modul (`utils_rate_limiter.py`)
- Input Sanitizer (`utils_sanitizer.py`)
- Fehlercode-Mapping (`error_codes.py`)

#### Neue Entities
- Kalibrierungsverlauf-Sensoren
- Analogeingänge AI1–AI8
- Erweiterungs-Relais 1–8

---

## [0.1.0] – 2025-08-01 🧪 ALPHA

### Erster öffentlicher Release

#### Features
- Grundlegende HTTP-API-Kommunikation
- Sensor-Entities für Temperaturen und Chemiewerte
- Einfache Switch-Entities für Pumpe und Heizung
- Config Flow für Setup

---

## Breaking Changes

### 1.0.0 → 1.0.1

Keine Breaking Changes. Direktes Upgrade möglich.

### 0.2.x → 1.0.0

- Mindest-HA-Version: **2025.12.0** (vorher 2024.12.0)
- Python: **3.12+** erforderlich
- Type Annotations: `X | None` statt `Optional[X]`

### 0.1.x → 0.2.x

- Konstanten reorganisiert (Import aus `const.py` weiterhin möglich)
- Entity-IDs können sich geändert haben (Neuinstallation empfohlen)

---

## Upgrade-Anleitung

### Via HACS (empfohlen)

1. HACS → Integrationen
2. Violet Pool Controller finden
3. „Aktualisieren" klicken
4. HA neu starten
5. Einstellungen → Geräte & Dienste → Integration prüfen

### Manuell

```bash
# Backup erstellen!
cp -r /config/custom_components/violet_pool_controller \
       /config/backup_violet_$(date +%Y%m%d)

# Neue Version installieren
cd /config/custom_components
rm -rf violet_pool_controller
# ZIP entpacken oder git pull

# HA neu starten
```

---

## Links

- [GitHub Releases](https://github.com/Xerolux/violet-hass/releases)
- [Vollständiger Changelog auf GitHub](https://github.com/Xerolux/violet-hass/blob/main/docs/CHANGELOG.md)
- [Bug melden](https://github.com/Xerolux/violet-hass/issues/new?template=bug_report.md)
- [Feature anfragen](https://github.com/Xerolux/violet-hass/issues/new?template=feature_request.md)

---

*Zurück: [API-Referenz](API-Reference) | Zurück: [Home](Home)*
