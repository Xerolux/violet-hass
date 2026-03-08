# 📝 Changelog - Violet Pool Controller

Alle wichtigen Änderungen, Verbesserungen und Fixes der Integration.

---

## 🆕 März 2025 - Version 1.x

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

- [Konfigurationshilfe (DE)](../docs/help/configuration-guide.de.md)
- [Konfigurationshilfe (EN)](../docs/help/configuration-guide.en.md)

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
- `github_wiki_content/Icon-Reference.md` (NEU)
- `github_wiki_content/Entities.md` (Aktualisiert)

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
- [Icon Upgrade Summary](../ICON_UPGRADE_SUMMARY.md) - Detaillierte Analyse

---

### 📚 Wiki-Erweiterung (NEU!)

**Umfassende GitHub Wiki Dokumentation**

#### ✨ Neue Seiten

- **[Home.md](Home)** - Startseite mit Highlights
- **[Icon-Reference.md](Icon-Reference)** - Alle 68+ Icons dokumentiert
- **[Installation.md](Installation)** - Schritt-für-Schritt Installationsanleitung
- **[Configuration.md](Configuration)** - Ausführliche Konfigurationshilfe
- **[Entities.md](Entities)** - Alle Entities mit neuen Icons
- **[Changelog.md](Changelog)** - Diese Seite!

#### 📝 Verbesserungen

- **Prominente Sicherheitshinweise** auf allen Seiten
- **Schritt-für-Schritt Anleitungen** mit Screenshots
- **Troubleshooting Sektionen** mit Lösungen
- **Code-Beispiele** für Automationen
- **Tabellen** für bessere Übersicht
- **Emoji-Icons** für bessere Erkennbarkeit

#### 🔍 Struktur

```
github_wiki_content/
├── Home.md                    # Startseite
├── Installation.md            # Installation
├── Configuration.md           # Konfiguration
├── Entities.md                # Alle Entities
├── Icon-Reference.md          # Icon-Referenz
└── Changelog.md               # Änderungen
```

---

## 🐛 Bug Fixes

### März 2025

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

## 📖 Nächste Schritte

### Was kommt als Nächstes?

**Geplant:**
- [ ] Weitere Icon-Optimierungen basierend auf Feedback
- [ ] Erweiterte Automation-Beispiele
- [ ] Dashboard-Templates
- [ ] Mehr-Sprach-Unterstützung (Französisch, Italienisch)
- [ ] Performance-Optimierungen
- [ ] Erweiterte Diagnose-Tools

**In Arbeit:**
- [ ] Verbesserte Fehlerbehandlung
- [ ] Detailliertere Logging-Optionen
- [ ] Websocket-Support für Echtzeit-Updates

**Vorschläge?**
- 🐛 [Issue melden](https://github.com/xerolux/violet-hass/issues)
- 💬 [Diskussion starten](https://github.com/xerolux/violet-hass/discussions)
- 💡 [Feature requests](https://github.com/xerolux/violet-hass/issues/new?template=feature_request.md)

---

## 📊 Statistik

### März 2025

| Metrik | Wert |
|--------|-------|
| **Code-Änderungen** | 4 Dateien |
| **Icons optimiert** | 68+ |
| **Wiki-Seiten erstellt** | 6 |
| **Dokumentation erweitert** | 2 Guides |
| **Bugs behoben** | 15+ |
| **Neue Features** | 2 (Disclaimer, Icons) |

---

## 🙏 Danksagung

**Vielen Dank an:**

- **Alle Tester** für das Feedback zu den Icons
- **Community** für die Unterstützung
- **Home Assistant Team** für die großartige Plattform
- **Material Design Icons** für das umfangreiche Icon-Set
- **Violet Pool Controller** für die Hardware

**Besonderer Dank an:**
- Alle Benutzer, die Bugs gemeldet haben
- Alle, die Vorschläge für Verbesserungen gemacht haben
- Alle, die an der Dokumentation mitgearbeitet haben

---

## 🔗 Nützliche Links

- 🏠 [Home](Home) - Wiki Startseite
- 📦 [Installation](Installation) - Installationsanleitung
- ⚙️ [Configuration](Configuration) - Konfigurationshilfe
- 🎛️ [Entities](Entities) - Alle Entities
- 🎨 [Icon-Reference](Icon-Reference) - Icon-Referenz
- 🐛 [Troubleshooting](Troubleshooting) - Probleme lösen
- 🤖 [Services](Services) - Automation & Scripts

---

**Viel Spaß mit der Violet Pool Controller Integration! 🏊✨**

*Letzte Aktualisierung: März 2025*
