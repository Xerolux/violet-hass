# 🏊 Violet Pool Controller Home Assistant - Komplette Wiki

> **Alles, was du über das Violet Pool Controller Addon für Home Assistant wissen musst** - Von der Installation bis zur Deinstallation, mit detaillierten Erklärungen aller Funktionen, States und Services.

---

## 📑 Inhaltsverzeichnis

1. [Installation & Setup](#-installation--setup)
2. [Konfiguration](#-konfiguration)
3. [Geräte & Entitäten](#-geräte--entitäten)
4. [Device States erklärt](#-device-states-erklärt)
5. [Services & Automatisierungen](#-services--automatisierungen)
6. [Sensoren & Messwerte](#-sensoren--messwerte)
7. [Schalter & Steuerungen](#-schalter--steuerungen)
8. [Fehlerbehandlung & Troubleshooting](#-fehlerbehandlung--troubleshooting)
9. [Updates & Upgrades](#-updates--upgrades)
10. [Deinstallation](#-deinstallation)
11. [FAQ & Häufige Fragen](#-faq--häufige-fragen)
12. [Sicherheit & Best Practices](#-sicherheit--best-practices)

---

## 📦 Installation & Setup

### Systemanforderungen

- **Home Assistant Version**: 2025.12.0 oder neuer
- **Python**: 3.12+
- **Netzwerk**: Violet Pool Controller im lokalen Netzwerk erreichbar
- **Speicher**: Minimal (Integration benötigt <10 MB)

### HACS Installation (Empfohlen)

**Schritt 1: HACS öffnen**
1. Home Assistant → Einstellungen
2. Geräte & Dienste → HACS (Custom Repositories)
3. ⋮ (Menü) → Benutzerdefinierte Repositories

**Schritt 2: Repository hinzufügen**
```
URL: https://github.com/xerolux/violet-hass
Kategorie: Integration
```

**Schritt 3: Integration installieren**
1. Nach "Violet Pool Controller" suchen
2. "Installieren" klicken
3. **Home Assistant neu starten**

**Schritt 4: Integration aktivieren**
1. Einstellungen → Geräte & Dienste
2. "Integration hinzufügen"
3. "Violet Pool Controller" suchen und hinzufügen
4. Host IP eingeben (z.B. 192.168.1.100)

### Manuelle Installation

Für Entwickler oder ohne HACS:

```bash
# Repository klonen
cd /config/custom_components/
git clone https://github.com/xerolux/violet-hass.git violet_pool_controller

# Oder ZIP herunterladen und entpacken
cd /config
unzip violet-hass-main.zip
mv violet-hass-main/custom_components/violet_pool_controller .
```

**Danach Home Assistant neu starten:**
- Web-UI: ⋮ → Systemsteuerelemente → Home Assistant neu starten
- Docker: `docker restart homeassistant`

### Erstes Setup

#### Schritt 1: Konfigurationsflow starten

1. Einstellungen → Geräte & Dienste → "Integration hinzufügen"
2. "Violet Pool Controller" auswählen
3. "Host IP-Adresse" eingeben (z.B. `192.168.1.100`)

#### Schritt 2: Authentifizierung (optional)

Falls dein Controller Benutzername/Passwort erfordert:
- Benutzername eingeben (normalerweise `admin`)
- Passwort eingeben
- **SSL/TLS aktivieren**: Wenn HTTPS verwendet wird

#### Schritt 3: Features auswählen

Der Assistent zeigt folgende Optionen:

- **Heizung**: Nutzt du einen Heizer?
- **Solar**: Solarthermie-Kollektor vorhanden?
- **Digitale Eingänge**: DI1-DI8 konfiguriert?
- **PV-Überschuss**: Solaranlage mit Überschuss-Modus?
- **Weitere Features**: Rückspülung, Dosierung, etc.

> **Tipp**: Nur wirklich verwendete Features aktivieren = bessere Performance!

#### Schritt 4: Sensor-Auswahl

Die Integration prüft deinen Controller auf verfügbare Sensoren und bietet diese zum Auswählen:

- **Wasserchemie**: pH, ORP, Chlorin
- **Temperaturen**: Pool, Umgebung, Solar
- **Systemzustände**: Druck, Wasserstände
- **Laufzeitstatistiken**: Pumpen, Heizer, etc.

> **Standard**: Wenn nichts ausgewählt → alle Sensoren werden angelegt

#### Schritt 5: Abfrage-Intervall

- **Vorschlag**: 30 Sekunden
- **Minimum**: 10 Sekunden
- **Maximum**: 300 Sekunden
- **Empfehlung für große Pools**: 20-30 Sekunden

---

## ⚙️ Konfiguration

### Konfigurationsoptionen

Nach der Installation kannst du die Integration feinabstimmen:

**Einstellungen → Geräte & Dienste → Violet Pool Controller → ⋮ (Menü) → Optionen**

| Option | Beispiel | Beschreibung |
|--------|----------|-------------|
| **Host/IP-Adresse** | `192.168.1.100` | IP des Violet Controllers |
| **Port** | `8080` | HTTP-Port (Standard: 80) |
| **Abfrageintervall** | `30` | Update-Frequenz in Sekunden |
| **Timeout** | `10` | Request-Timeout in Sekunden |
| **SSL/TLS verwenden** | ☑ | HTTPS aktivieren |
| **SSL-Zertifikat prüfen** | ☑ | Zertifikat-Validierung |
| **Username** | `admin` | Nur wenn erforderlich |
| **Passwort** | `****` | Nur wenn erforderlich |

### Erweiterte Optionen

#### SSL/TLS Konfiguration

**SSL aktivieren:**
- Notwendig wenn Controller HTTPS nutzt
- Gesetztes Zertifikat wird validiert

**SSL-Zertifikat prüfen deaktivieren:**
- ⚠️ **Nur für selbsignierte Zertifikate!**
- Nur in vertrauenswürdigen Netzwerken
- Home Assistant zeigt Warnung

```yaml
# Beispiel: Konfiguration mit selbsigniertem Zertifikat
Host: 192.168.1.100
SSL verwenden: ☑
SSL-Zertifikat prüfen: ☐
```

#### Timeout-Einstellungen

- **Gesamtlaufzeit**: 10 Sekunden (Standard)
- **Verbindungs-Timeout**: 8 Sekunden (80% der Gesamtzeit)
- **Socket-Timeout**: 8 Sekunden

> Diese Werte sind optimiert. Nur bei Verbindungsproblemen anpassen.

#### Pool-Konfiguration (optional)

Im Konfigurationsflow kannst du eingeben:
- **Pool-Größe**: z.B. 50 m³
- **Pool-Typ**: Außen/Innen
- **Desinfektionsmittel**: Chlor/Brom/etc.

Diese beeinflussen die Standardwerte für Dosierungen.

### Feature-Gruppen

Die Integration unterstützt folgende Feature-Gruppen:

| Feature | Beschreibung | Optionen |
|---------|-------------|----------|
| **Pumpe** | Filterpumpe mit Geschwindigkeit | Aus/Ein/Auto, 3 Geschwindigkeitsstufen |
| **Heizer** | Heizung mit Thermostaten | Aus/Heat/Auto, Sollwert (°C) |
| **Solar** | Solarthermie-Kollektor | Aus/Heat/Auto, Sollwert (°C) |
| **Dosierung** | Chemische Dosierungen | pH-, pH+, Chlor, Flockmittel |
| **Rückspülung** | Filterrückspülung | Manuell, mit Timer |
| **Beleuchtung** | Pool-Beleuchtung | On/Off, DMX-Szenen, Farben |
| **Abdeckung** | Pool-Abdeckung | Auf/Zu, Position-Tracking |
| **PV-Überschuss** | Solar-Überschuss-Nutzer | Auto, 3 Geschwindigkeitsstufen |
| **Digitale Eingänge** | DI1-DI8 | Binary Sensors, Regeln |

---

## 🖥️ Geräte & Entitäten

### Was ist eine Entität?

Eine **Entität** ist ein steuerbares oder messbares Element in Home Assistant:
- **Sensoren**: Messwerte (Temperatur, Druck)
- **Schalter**: Steuerbar (Pumpe, Heizer)
- **Klima**: Heizung mit Thermostat
- **Abdeckung**: Cover mit Position

### Benennungsschema

Entitäten erhalten automatisch eindeutige Namen:

```
{domain}.{device_name}_{feature_name}
```

**Beispiele:**
- `sensor.violet_pool_temperature` → Wassertemperatur
- `switch.violet_pump` → Filterpumpe
- `climate.violet_heater` → Heizung mit Thermostat
- `cover.violet_pool_cover` → Pool-Abdeckung

### Multi-Controller Betrieb

Wenn mehrere Controller angebunden sind:

```
{domain}.{device_name_1}_{feature_name}
{domain}.{device_name_2}_{feature_name}
```

Die Namen werden mit `_2`, `_3` usw. erweitert.

### Entitäten organisieren

Home Assistant zeigt Entitäten automatisch nach Geräten. Du kannst diese auch manuell organisieren:

1. Einstellungen → Geräte & Dienste → Geräte
2. Dein Violet-Gerät auswählen
3. Entitäten verschieben oder umbenennen

---

## 🎯 Device States erklärt

### Die 7 Device States (0-6)

Der Violet Controller hat 7 verschiedene Zustände für Geräte. Diese sind **sehr wichtig zum Verstehen**:

| State | Name | Deutsch | Manuell/Auto | Status | Beschreibung |
|-------|------|---------|-------------|--------|-------------|
| **0** | AUTO_OFF | Automatik - Aus | Auto | ⛔ OFF | Automatik aktiv, Gerät läuft nicht |
| **1** | MANUAL_ON | Manuell An | Manuell | ✅ ON | Manuell eingeschaltet |
| **2** | AUTO_ON | Automatik - An | Auto | ✅ ON | Automatik aktiv, Gerät läuft |
| **3** | AUTO_TIMER | Automatik - Timer | Auto | ✅ ON | Automatik mit Zeitsteuerung, aktiv |
| **4** | MANUAL_FORCED | Manuell erzwungen | Manuell | ✅ ON | Manuell eingeschaltet, erzwungen |
| **5** | AUTO_WAITING | Automatik - Wartend | Auto | ⛔ OFF | Automatik aktiv, wartet auf Bedingungen |
| **6** | MANUAL_OFF | Manuell Aus | Manuell | ⛔ OFF | Manuell ausgeschaltet |

### State-Visualisierung in Home Assistant

Je nach State werden unterschiedliche Icons und Farben angezeigt:

**Automatik-Modus:**
- 🟢 **Grün** (Auto - Aktiv): States 2, 3
- 🔵 **Blau** (Auto - Bereit): States 0, 5

**Manuell-Modus:**
- 🟠 **Orange** (Manuell An): States 1, 4
- 🔴 **Rot** (Manuell Aus): State 6

### Besondere States

#### State 3 mit Zusatzinfo: `3|PUMP_ANTI_FREEZE`

States können mit Zusatzinformationen durch `|` getrennt sein:

```
3|PUMP_ANTI_FREEZE    → Automatik mit Frostschutz aktiv
2|BLOCKED_BY_TEMP     → Automatik läuft, aber blockiert durch Temperatur
```

**Die Ziffer ist wichtig**, die Zusatzinfo ist erklärend.

### State-Übergänge

Typische Übergänge:

```
6 (Manuell Aus)
  ↓
1 (Manuell An)      → Benutzer schaltet manuell ein
  ↓
6 (Manuell Aus)     → Benutzer schaltet manuell aus

---

0 (Auto - Aus)
  ↓
2 (Auto - An)       → Automatik erkennt Bedingung
  ↓
3 (Auto - Timer)    → Zeitsteuerung tritt in Kraft
  ↓
0 (Auto - Aus)      → Bedingung erfüllt oder Bedingung verändert
```

### State in Automatisierungen nutzen

**Beispiel: Überprüfe, ob Pumpe läuft**

```yaml
automation:
  - alias: "Überprüfe Pumpen-Status"
    trigger:
      - platform: state
        entity_id: switch.violet_pump
        to: "on"
    action:
      - service: notify.notify
        data:
          message: "Pumpe läuft jetzt!"
```

**Beispiel: Reagiere auf Manuell-Status**

```yaml
automation:
  - alias: "Benachrichtigung bei manuellem Heizer"
    trigger:
      - platform: template
        value_template: "{{ state_attr('switch.violet_heater', 'violet_state') in ['1', '4'] }}"
    action:
      - service: notify.notify
        data:
          message: "Heizer läuft im manuellen Modus!"
```

---

## 🤖 Services & Automatisierungen

### Verfügbare Services

Die Integration bietet spezialisierte Services für erweiterte Automatisierung. Diese sind deutlich leistungsfähiger als einfache An/Aus-Schalter.

### 🔧 Service: `control_pump` - Pumpen-Steuerung

**Beschreibung**: Erweiterte Pumpensteuerung mit Geschwindigkeit und Modi

**Verfügbare Aktionen:**
- `speed_control` - Geschwindigkeit (1-3) mit Timer
- `force_off` - Erzwungenes Ausschalten
- `eco_mode` - Energiesparen (reduzierte Geschwindigkeit)
- `boost_mode` - Maximale Leistung
- `auto` - Zurück zu Automatik

**Beispiel: Pumpe mit Geschwindigkeit 2 starten**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pump
data:
  action: speed_control
  speed: 2
  duration: 3600  # 1 Stunde
```

**Beispiel: Pumpe 30 Min im Eco-Modus**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pump
data:
  action: eco_mode
  duration: 1800
```

**Parameter:**

| Parameter | Typ | Bereich | Standard | Beschreibung |
|-----------|-----|--------|---------|-------------|
| `action` | Text | Siehe oben | - | Aktion durchführen |
| `speed` | Zahl | 1-3 | 2 | Pumpengeschwindigkeit |
| `duration` | Zahl | 0-86400 | 0 | Dauer in Sekunden (0=unbegrenzt) |

### 🧪 Service: `smart_dosing` - Intelligente Dosierung

**Beschreibung**: Manuelle oder automatische Dosierung von Chemikalien

**Verfügbare Chemikalien:**
- `pH-` (Säure/Reduktion)
- `pH+` (Lauge/Erhöhung)
- `Chlor` (Desinfektionsmittel)
- `Flockmittel` (Filterverbesserer)

**Verfügbare Aktionen:**
- `manual_dose` - Manuell dosieren
- `auto` - Automatische Dosierung starten
- `stop` - Dosierung stoppen

**Beispiel: 30 Sekunden Chlor dosieren**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.chlorine_dosing
data:
  dosing_type: "Chlor"
  action: manual_dose
  duration: 30
```

**Beispiel: pH-Ausgleich mit Sicherheit**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.ph_dosing_minus
data:
  dosing_type: "pH-"
  action: manual_dose
  duration: 15
  safety_override: false  # Sicherheitschecks beachten
```

**Parameter:**

| Parameter | Typ | Bereich | Standard | Beschreibung |
|-----------|-----|--------|---------|-------------|
| `dosing_type` | Text | Siehe oben | - | Welche Chemikalie? |
| `action` | Text | Siehe oben | - | Aktion durchführen |
| `duration` | Zahl | 5-300 | 30 | Dosierdauer in Sekunden |
| `safety_override` | Boolean | true/false | false | Sicherheitsintervalle ignorieren |

### ☀️ Service: `manage_pv_surplus` - PV-Überschuss-Management

**Beschreibung**: Nutze Solaranlagen-Überschuss für Poolheizung

**Modi:**
- `activate` - PV-Modus aktivieren
- `deactivate` - PV-Modus deaktivieren
- `auto` - Automatische Verwaltung

**Beispiel: PV-Surplus mit Geschwindigkeit 3**
```yaml
service: violet_pool_controller.manage_pv_surplus
target:
  entity_id: switch.pv_surplus_mode
data:
  mode: activate
  pump_speed: 3
```

**Parameter:**

| Parameter | Typ | Bereich | Default | Beschreibung |
|-----------|-----|--------|---------|-------------|
| `mode` | Text | activate/deactivate/auto | - | Modus |
| `pump_speed` | Zahl | 1-3 | 2 | Pumpengeschwindigkeit |

### 💡 Service: `control_dmx_scenes` - DMX Lighting

**Beschreibung**: Steuere Pool-Beleuchtungs-Szenen

**Verfügbare Aktionen:**
- `all_on` - Alle Szenen einschalten
- `all_off` - Alle Szenen ausschalten
- `all_auto` - Automatik
- `sequence` - Szenen nacheinander abspielen
- `party_mode` - Party-Modus aktivieren

**Beispiel: Alle Lichter ausschalten**
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: all_off
```

**Beispiel: Party-Modus mit Szenen-Wechsel**
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: sequence
  sequence_delay: 3  # 3 Sekunden zwischen Szenen
```

### 🔍 Service: `test_output` - Diagnose

**Beschreibung**: Teste Ausgänge für Diagnose und Wartung

**Parameter:**
- `output` - Welcher Ausgang? (PUMP, HEATER, SOLAR, etc.)
- `mode` - SWITCH, ON, oder OFF
- `duration` - Test-Laufzeit (1-900 Sekunden)

**Beispiel: Pumpe 2 Min testen**
```yaml
service: violet_pool_controller.test_output
target:
  device_id: <device_id>
data:
  output: PUMP
  mode: "ON"
  duration: 120
```

### Automation Blueprints

Fertige Automatisierungs-Vorlagen sind im Projekt enthalten:

**Installation:**
1. Einstellungen → Automatisierungen & Szenen → Blueprints
2. "Blueprint importieren"
3. Repository-URL eingeben

**Verfügbare Blueprints:**
- 🌡️ Intelligente Temperatursteuerung
- 🧪 pH-Management
- ⚡ Energie-Optimierung
- 🌧️ Wetter-Automatisierung
- 🏊 Pool-Modi (Party, Eco, Winter)

---

## 📊 Sensoren & Messwerte

### Wasserchemie-Sensoren

Diese Sensoren messen die Wasserqualität:

| Sensor | Einheit | Bereich | Normalwert | Beschreibung |
|--------|--------|--------|-----------|-------------|
| **pH-Wert** | pH | 6.0-8.5 | 7.0-7.4 | Säuregehalt (7=neutral) |
| **Redoxpotential (ORP)** | mV | 400-800 | 650-750 | Desinfektionswirkung |
| **Chlorin** | mg/l | 0-5 | 1.0-3.0 | Freies Chlor |
| **Leitfähigkeit** | µS/cm | 0-2000 | ~1200 | Salzgehalt |

### Temperatur-Sensoren

| Sensor | Einheit | Bereich | Beschreibung |
|--------|--------|--------|-------------|
| **Pool-Temperatur** | °C | 0-50 | Aktuelle Wassertemperatur |
| **Solar-Temperatur** | °C | 0-80 | Temperatur Solarthermie-Kollektor |
| **Umgebungstemperatur** | °C | -20-60 | Außentemperatur |

### System-Sensoren

| Sensor | Einheit | Beschreibung |
|--------|--------|-------------|
| **Filterdruck** | bar | Druck im Filtersystem (0.5-2.5) |
| **Wasserstände** | % | Poolwasser-Niveau |
| **Pumpen-Laufzeit** | h | Gesamtlaufzeit heute |
| **Heizer-Laufzeit** | h | Gesamte Laufzeit |
| **Energieverbrauch** | kWh | Heutige Strombilanz |

### Analog-Eingänge (AI1-AI8)

Falls vorhanden: `sensor.violet_ai1` bis `sensor.violet_ai8`
- Allgemeine Messeingänge (0-10V oder 4-20mA)
- Benutzerdefinierte Sensoren anschließbar

### Digital-Eingänge (DI1-DI8)

Binäre Sensoren für Schalter, Kontakte, Drucktaster:
- `binary_sensor.violet_di1` bis `binary_sensor.violet_di8`
- On/Off Zustände

### Fehler-Codes Sensor

`sensor.violet_system_error_codes` zeigt aktuelle Fehler:

```
[]                      → Keine Fehler
[101, 205]             → Mehrere Fehler (z.B. Sensor-, Druckfehler)
```

### Kalibrierungs-Historie

`sensor.violet_calibration_history` enthält Kalibrierungsdaten:
- Datum und Uhrzeit
- Kalibriert Sensor (pH, ORP, etc.)
- Kalibrierungswerte

---

## 🎚️ Schalter & Steuerungen

### Die 3-State Schalter-Logik

Alle Geräte sind **3-State Schalter** mit den Zuständen:
1. **Ein** (ON)
2. **Aus** (OFF)
3. **Automatik** (AUTO)

```
Schalter: Ein → Aus → Automatik → Ein ...
```

Home Assistant zeigt zusätzlich den inneren **State** an (0-6):

```
Anzeige: Ein/Aus/Automatik (Intern: State 1/6/0)
```

### Schalter-Typen

#### 1. Binäre Schalter (nur Ein/Aus)
- Pool-Abdeckung
- Rückspülung
- Einige Extension-Relays

**Befehle:**
```yaml
service: switch.turn_on
target:
  entity_id: switch.violet_backwash

service: switch.turn_off
target:
  entity_id: switch.violet_backwash
```

#### 2. 3-State Schalter (Ein/Aus/Auto)
- Pumpe
- Heizer
- Solar
- Dosierungen
- DMX-Szenen

**Befehle:**
```yaml
# Einschalten
service: switch.turn_on
target:
  entity_id: switch.violet_pump

# Ausschalten
service: switch.turn_off
target:
  entity_id: switch.violet_pump

# Automatik
service: violet_pool_controller.turn_auto
target:
  entity_id: switch.violet_pump
```

### Verfügbare Schalter

#### Hauptkomponenten

| Schalter | Funktion | States | Besonderheiten |
|----------|----------|--------|-----------------|
| **Pumpe** | Filterpumpe | Ein/Aus/Auto | 3 Geschwindigkeiten |
| **Heizer** | Hauptheizung | Ein/Aus/Auto | Mit Thermostat |
| **Solar** | Solarthermie | Ein/Aus/Auto | Mit Thermostat |
| **Beleuchtung** | Pool-Licht | Ein/Aus/Auto | DMX-Szenen möglich |

#### Chemie-Dosierung

| Schalter | Chemikalien | Dauer | Sicherheit |
|----------|------------|-------|-----------|
| **pH- Dosierung** | Säure | 5-300s | Minimalintervall |
| **pH+ Dosierung** | Lauge | 5-300s | Minimalintervall |
| **Chlor Dosierung** | Chlorin | 5-300s | Überdosis-Schutz |
| **Flockmittel** | Filterhelfer | 5-300s | Mit Pumpen-Sync |

#### Wartung & Sonderausgänge

| Schalter | Funktion | Verwendung |
|----------|----------|-----------|
| **Rückspülung** | Filterreinigung | Automatisch/Manuell |
| **Rückspül-Rinse** | Nachspülung | Nach Rückspülung |
| **Abdeckung** | Pool-Cover | Auf/Zu/Stopp |
| **PV-Überschuss** | Solar-Nutzung | Mit Geschwindigkeit |

#### Extension Relays (EXT1-EXT8, EXT2-EXT8)

Zusätzliche Ausgänge für benutzerdefinierte Geräte:
- `switch.violet_ext1_1` bis `switch.violet_ext1_8`
- `switch.violet_ext2_1` bis `switch.violet_ext2_8`

Konfigurierbar für beliebige Verwendung.

#### DMX Szenen (SCENE 1-12)

Vordefinierte Lichtszenarios:
- `switch.violet_dmx_scene1` bis `switch.violet_dmx_scene12`

Aktiviere Szenen einzeln oder via Service für Sequenzen.

---

## 🌡️ Klima-Steuerungen (Climate)

Spezielle Entitäten für Heizung und Solar mit Temperaturregelung:

### Heizer (climate.violet_heater)

**HVAC-Modi:**
- `off` - Aus
- `heat` - Heizen
- `auto` - Automatik

**Aktuelle Temperatur:** Pool-Temperatur
**Sollwert:** Zieltemperatur eingeben (z.B. 28°C)

**Beispiel: Auf 28°C heizen**
```yaml
service: climate.set_temperature
target:
  entity_id: climate.violet_heater
data:
  temperature: 28
  hvac_mode: heat
```

### Solar (climate.violet_solar)

**HVAC-Modi:**
- `off` - Aus
- `heat` - Solarheizung
- `auto` - Automatik

**Besonderheit:** Nur aktiv wenn Kollektor > Poolwasser

**Beispiel: Solar auf 30°C automatisch**
```yaml
service: climate.set_temperature
target:
  entity_id: climate.violet_solar
data:
  temperature: 30
  hvac_mode: auto
```

---

## 📱 Home Assistant Integration

### Lovelace Dashboard

Ein vorgefertigtes Dashboard liegt bei:
- Datei: `Dashboard/pool-dashboard.yaml`
- Kopiere nach `/config/`
- Importiere in HA → Einstellungen → Dashboards

**Das Dashboard enthält:**
- 🌡️ Aktuelle Temperaturen
- 📊 Wasserchemie-Monitore
- 🎚️ Schnellzugriff auf Geräte
- 📈 Statistiken und Trends

### Eigenes Dashboard erstellen

```yaml
title: Mein Pool Dashboard
views:
  - title: Übersicht
    cards:
      - type: glance
        title: Aktuelle Werte
        entities:
          - sensor.violet_pool_temperature
          - sensor.violet_pool_ph_value
          - sensor.violet_pool_chlorine_level

      - type: entities
        title: Steuerung
        entities:
          - switch.violet_pump
          - switch.violet_heater
          - switch.violet_solar

      - type: thermostat
        entity: climate.violet_heater
```

### Automatisierungen erstellen

**Einfache Automation: Heizer aktivieren wenn Temperatur zu niedrig**

```yaml
automation:
  - alias: "Pool zu kalt - Heizen"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_temperature
        below: 25
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 27
          hvac_mode: heat
      - service: notify.notify
        data:
          message: "Pool ist zu kalt, Heizung wird aktiviert"
```

**Komplexe Automation: Intelligente Dosierung**

```yaml
automation:
  - alias: "Automatisches pH-Management"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_ph_value
        above: 7.6
    action:
      - service: violet_pool_controller.smart_dosing
        target:
          entity_id: switch.ph_dosing_minus
        data:
          dosing_type: "pH-"
          action: manual_dose
          duration: 20
      - service: notify.notify
        data:
          message: "pH zu hoch, pH- wird dosiert"
```

---

## 🚨 Fehlerbehandlung & Troubleshooting

### Häufige Fehler und Lösungen

#### ❌ "Verbindung zum Controller fehlgeschlagen"

**Ursachen:**
- Controller nicht im Netzwerk erreichbar
- Falsche IP-Adresse
- Firewall blockiert
- Controller ausgeschaltet

**Lösungen:**
```bash
# 1. Ping testen
ping 192.168.1.100

# 2. Direkter HTTP-Test
curl http://192.168.1.100/getReadings?ALL

# 3. In HA testen
Einstellungen → Geräte & Dienste → Violet → ⋮ → Neu laden
```

#### ❌ "SSL-Zertifikat-Fehler"

**Symptom:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Lösung:**
1. Einstellungen → Geräte & Dienste → Violet → ⋮ → Optionen
2. "SSL-Zertifikat prüfen" deaktivieren
3. ⚠️ Nur für selbsignierte Zertifikate!

#### ❌ "Timeout - Request dauert zu lange"

**Ursachen:**
- Netzwerk überlastet
- Controller nicht responsive
- Zu viele Sensoren abgefragt

**Lösungen:**
1. Abfrageintervall erhöhen (z.B. 45 Sekunden)
2. Weniger Sensoren aktivieren
3. Netzwerk-Stabilität prüfen

#### ❌ "Entitäten sind ständig 'unavailable'"

**Ursachen:**
- Koordinator-Fehler
- Zu kurzes Abfrageintervall
- Sensor-Problem am Controller

**Lösungen:**
```yaml
# Integration neu laden
service: homeassistant.reload_config_entry
target:
  device_id: <device_id>

# Oder manuell:
# Einstellungen → Geräte & Dienste → Violet → ⋮ → Neu laden
```

### Debug-Modus aktivieren

Für detailliertere Logs:

1. `configuration.yaml` bearbeiten:
```yaml
logger:
  logs:
    custom_components.violet_pool_controller: debug
```

2. Home Assistant neu starten

3. Logs prüfen:
```bash
tail -f /config/home-assistant.log | grep violet_pool_controller
```

### Logs prüfen

Home Assistant → Einstellungen → System → Protokolle

Wichtige Meldungen:
- `INFO` - Informationen (Normal)
- `WARNING` - Warnungen (Beachten)
- `ERROR` - Fehler (Untersuchen!)

### Fehler-Codes vom Controller

Der Controller sendet Fehlercodes. Diese finden sich in `error_codes.py`:

**Häufige Fehler:**
- `101` - Sensor-Fehler (pH, ORP, etc.)
- `205` - Druck zu hoch
- `301` - Wasser-Level zu niedrig
- `401` - Temperatur-Sensor defekt

Nutze `sensor.violet_system_error_codes` zur Überwachung.

### Support & Hilfe

- 🐛 **GitHub Issues**: [xerolux/violet-hass/issues](https://github.com/xerolux/violet-hass/issues)
- 💬 **Discord**: [Community-Server](https://discord.gg/Qa5fW2R)
- 📧 **E-Mail**: git@xerolux.de
- 📖 **Wiki**: [Komplette Dokumentation](https://github.com/xerolux/violet-hass/wiki)

---

## 📈 Updates & Upgrades

### Automatische Updates mit HACS

HACS prüft automatisch auf Updates:

1. HACS → Integrationen
2. "Violet Pool Controller" finden
3. Wenn Update verfügbar: 🔵 Punkt neben Name
4. "Aktualisieren" klicken
5. Home Assistant neu starten

### Manuelle Updates

```bash
cd /config/custom_components/violet_pool_controller
git pull origin main
# Home Assistant neu starten
```

### Changelog lesen

Vor jedem Update solltest du den Changelog prüfen:
- 📝 [CHANGELOG.md](docs/CHANGELOG.md)
- 🚨 Mögliche Breaking Changes?
- ✨ Neue Features?
- 🐛 Behobene Bugs?

### Version überprüfen

**Aktuelle Version in HA:**
1. Einstellungen → Geräte & Dienste → Violet
2. "Violet Pool Controller" auswählen
3. Version oben rechts angezeigt

**Oder im Terminal:**
```bash
grep '"version"' /config/custom_components/violet_pool_controller/manifest.json
```

### Backup vor Update

Immer sichern:
```bash
# Home Assistant Backup
Einstellungen → System → Sicherungen → Erstellen

# Oder manuell
cp -r /config/custom_components/violet_pool_controller /backup/
```

### Troubleshooting nach Update

Wenn nach Update Probleme auftreten:

1. **Home Assistant komplett neu starten** (nicht nur Reload)
   - Einstellungen → System → Systemsteuerelemente → Neu starten

2. **Integration neu laden**
   - Einstellungen → Geräte & Dienste → Violet → ⋮ → Neu laden

3. **Bei Problemen zurück zur alten Version**
   ```bash
   cd /config/custom_components/violet_pool_controller
   git checkout <version>
   # Beispiel: git checkout v0.2.0
   ```

---

## 🗑️ Deinstallation

### Vollständige Entfernung

#### Schritt 1: Integration aus Home Assistant entfernen

1. Einstellungen → Geräte & Dienste
2. "Violet Pool Controller" auswählen
3. ⋮ (Menü) → "Entfernen"
4. Bestätigung akzeptieren

#### Schritt 2: Dateien löschen

```bash
# Integrations-Verzeichnis löschen
rm -rf /config/custom_components/violet_pool_controller
```

#### Schritt 3: HACS-Eintrag entfernen (optional)

1. HACS → Integrationen
2. "Violet Pool Controller" auswählen
3. ⋮ → "Repository entfernen"

#### Schritt 4: Home Assistant neu starten

```bash
# Web-UI: ⋮ → Systemsteuerelemente → Neu starten
# Docker: docker restart homeassistant
```

### Daten erhalten

Falls du die Konfiguration wiederverwenden möchtest:

1. **Automatisierungen exportieren:**
   - Einstellungen → Automatisierungen
   - Jede Automatisierung öffnen
   - YAML kopieren

2. **Dashboards exportieren:**
   - Einstellungen → Dashboards
   - Dashboard-YAML exportieren

3. **Entitäts-Aliases speichern:**
   ```bash
   # Home Assistant Dateien sichern
   cp -r /config/.storage /backup/
   ```

### Migration zu neuem System

Falls du zu einem neuen Home Assistant System wechselst:

1. **Backup erstellen** (wie oben)
2. **Neues System starten**
3. **Integration installieren**
4. **Backup einspielen** (falls benötigt)
5. **Automatisierungen/Dashboards neu erstellen** (nutze gesicherte YAMLs)

---

## ❓ FAQ & Häufige Fragen

### Allgemein

**F: Benötige ich eine Cloud-Anbindung?**
A: Nein! Das Addon ist 100% lokal. Kein Internet, kein Cloud-Service erforderlich.

**F: Kann ich mehrere Controller ansteuern?**
A: Ja! Die Integration unterstützt Multi-Controller. Jeder bekommt eindeutige Entitäten.

**F: Ist das Addon sicher?**
A: Ja! Es nutzt lokale Netzwerk-Kommunikation mit optionalem SSL/TLS und Input-Sanitization.

**F: Welche Home Assistant Version ist minimal erforderlich?**
A: Home Assistant 2025.12.0 oder neuer (Ältere Versionen werden nicht unterstützt).

### Installation & Setup

**F: Wie finde ich die IP-Adresse meines Controllers?**
A:
1. Router-Admin-Interface öffnen (meist 192.168.1.1)
2. Verbundene Geräte anzeigen
3. "Violet" oder ähnlich suchen
4. Notiere die IP

Oder im Terminal:
```bash
ping violet.local    # Falls mDNS aktiviert
```

**F: Kann ich den Controller über HTTPS ansprechen?**
A: Ja! Aktiviere "SSL verwenden" in den Optionen. SSL-Zertifikat-Validierung kann deaktiviert werden.

**F: Funktioniert das mit selbsigniertem Zertifikat?**
A: Ja, aber deaktiviere "SSL-Zertifikat prüfen" in den Optionen (nur für vertrauenswürdige Netzwerke!).

### Funktionen & Bedienung

**F: Was bedeutet "Automatik" im Gegensatz zu "Manuell"?**
A:
- **Automatik**: Controller regelt selbstständig (z.B. nach Temperaturen)
- **Manuell**: Du stellst direkt ein, Auto-Regeln werden ignoriert

**F: Kann ich den Pumpe-Geschwindigkeit einstellen?**
A: Ja! Die Pumpe hat 3 Geschwindigkeitsstufen (1, 2, 3). Mit Service `control_pump` kannst du diese wählen.

**F: Wie dosiere ich Chemikalien sicher?**
A: Nutze den `smart_dosing` Service:
- Kleine Mengen (15-30 Sekunden)
- Abstand zwischen Dosierungen beachten
- Immer den Sensor-Wert kontrollieren

**F: Kann ich Szenen speichern?**
A: Ja! Mit Automation kannst du Schalter-Kombinationen speichern:
```yaml
scene.create
entities:
  switch.violet_pump: "on"
  switch.violet_heater: "off"
  climate.violet_heater: { temperature: 28 }
```

### Fehlersuche

**F: Meine Sensoren zeigen "unavailable" - Warum?**
A: Koordinator-Fehler (meist Verbindungsproblem). Lösungen:
1. Abfrageintervall erhöhen (30-45s)
2. Integration neu laden
3. Weniger Sensoren aktivieren

**F: Der Controller antwortet sehr langsam?**
A:
1. Netzwerk-Auslastung prüfen
2. Abfrageintervall erhöhen
3. CPU-Last des Controllers prüfen
4. Zu viele Sensoren?

**F: Warum werden manche Sensoren nicht angezeigt?**
A:
1. Nicht im Setup-Flow aktiviert?
2. Controller besitzt diesen Sensor nicht
3. Feature ist nicht konfiguriert
4. Lösung: Integration neu laden

### Performance & Optimierung

**F: Welches Abfrageintervall sollte ich nutzen?**
A:
- **20-30s**: Standard (gute Balance)
- **10-15s**: Für schnelle Reaktionen (höhere Last)
- **45-60s**: Für weniger wichtige Pools

**F: Ständig neue Automatisierungen erstellen - langweilig!**
A: Nutze Blueprints! Diese sind vorgefertigte Automatisierungs-Vorlagen:
- Einstellungen → Automatisierungen → Blueprints
- "Blueprint importieren" → Repository-URL eingeben

**F: Kann ich Logging reduzieren?**
A: Ja! In Home Assistant `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.violet_pool_controller: warning  # Nur Warnungen
```

### Services & Automatisierungen

**F: Wie rufe ich einen Service auf?**
A: Mehrere Möglichkeiten:

1. **Developer Tools:**
   - Einstellungen → Developer Tools → Services
   - Service auswählen, ausfüllen, testen

2. **YAML in Automatisierung:**
   ```yaml
   service: violet_pool_controller.control_pump
   target:
     entity_id: switch.violet_pump
   data:
     action: speed_control
     speed: 2
   ```

3. **UI Automation Builder:**
   - Einstellungen → Automatisierungen → Erstellen

**F: Kann ich eine Automatisierung zeitgesteuert auslösen?**
A: Ja!
```yaml
trigger:
  - platform: time
    at: "08:00:00"  # Jeden Morgen 8:00 Uhr
action:
  - service: switch.turn_on
    target:
      entity_id: switch.violet_pump
```

**F: Kann ich auf Wettervorhersagen reagieren?**
A: Ja! Mit der Weather-Integration:
```yaml
trigger:
  - platform: template
    value_template: "{{ state_attr('weather.my_weather', 'precipitation') > 5 }}"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.violet_pool_cover
```

---

## 🔒 Sicherheit & Best Practices

### Sicherheits-Grundlagen

#### 1. Netzwerk-Sicherheit

✅ **Empfohlen:**
- Controller im privaten Netzwerk
- Firewall schützt Zugriff
- Nur lokale Kommunikation
- SSL/TLS aktivieren

❌ **Nicht empfohlen:**
- Controller ins Internet exposieren
- Standardpasswort verwenden
- Auf öffentlichen WLAN

#### 2. Authentifizierung

Falls dein Controller Passwort erfordert:
- **Starkes Passwort** verwenden (min. 12 Zeichen)
- **Home Assistant .env-Datei** nutzen:

```bash
# /config/.env
VIOLET_PASSWORD=DeinStarkesPasswort
```

```yaml
# In Integration-Konfiguration
password: !env_var VIOLET_PASSWORD
```

#### 3. Input-Validation

Die Integration validiert automatisch:
- XSS-Schutz (HTML-Escaping)
- SQL-Injection-Schutz
- Command-Injection-Schutz
- Path-Traversal-Schutz

### Best Practices

#### 1. Regelmäßige Backups

```bash
# Wöchentliches Backup
Home Assistant → Einstellungen → System → Sicherungen → Erstellen
```

#### 2. Logs überwachen

Regelmäßig prüfen auf:
- Unerwartete Fehler
- Kommunikationsprobleme
- Ungewöhnliche States

#### 3. Sensoren kalibrieren

Besonders pH und ORP sollten regelmäßig kalibriert werden:
- **Monatlich**: pH und ORP
- **Wöchentlich**: Chlor (mit Testkit)
- **2x täglich**: Sichtprüfung

#### 4. Automatisierungen testen

Neue Automatisierungen sollten:
1. Mit kurzer Dauer testen
2. Mit Benachrichtigungen testen
3. Dann in Produktion gehen

**Beispiel: Test-Automatisierung**
```yaml
automation:
  - alias: "TEST - Pumpe für 10s"
    trigger:
      - platform: state
        entity_id: input_boolean.test_pump
        to: "on"
    action:
      - service: violet_pool_controller.control_pump
        target:
          entity_id: switch.violet_pump
        data:
          action: speed_control
          speed: 1
          duration: 10
      - service: notify.notify
        data:
          message: "TEST: Pumpe startet für 10s"
```

#### 5. Wartung planen

Einmal pro Quartal:
- **Hardware-Check**: Sensoren prüfen
- **Software-Update**: Addon aktualisieren
- **Backup-Test**: Backup einspielen testen
- **Config-Review**: Automatisierungen überprüfen

#### 6. Monitoring einrichten

Überwache kritische Metriken:
- Fehler-Codes des Controllers
- Sensor-Verfügbarkeit
- Verbindungs-Stabilität

```yaml
automation:
  - alias: "Fehler-Alarm"
    trigger:
      - platform: state
        entity_id: sensor.violet_system_error_codes
    condition:
      - condition: template
        value_template: "{{ states('sensor.violet_system_error_codes') != '[]' }}"
    action:
      - service: notify.notify
        data:
          title: "⚠️ Pool-Fehler!"
          message: "{{ states('sensor.violet_system_error_codes') }}"
```

### SSL/TLS Konfiguration (Erweitert)

#### Mit Self-Signed Zertifikat

```yaml
# Integration-Einstellungen
Host: 192.168.1.100
Port: 8443
SSL verwenden: ☑
SSL-Zertifikat prüfen: ☐  # ACHTUNG: Unsicher!
```

**Sicherer: Zertifikat in Home Assistant importieren**

```bash
# Zertifikat vom Controller exportieren
openssl s_client -connect 192.168.1.100:8443 -showcerts

# In Home Assistant importieren
# (Erweiterte Konfiguration erforderlich)
```

### Fehlersuche bei Sicherheitsproblemen

#### SSL-Fehler beheben

```
SSL: CERTIFICATE_VERIFY_FAILED
```

Mögliche Lösungen:
1. Zertifikat validieren:
   ```bash
   openssl s_client -connect 192.168.1.100:8443
   ```

2. Debugging aktivieren:
   ```yaml
   logger:
     logs:
       aiohttp: debug
   ```

3. Notfalls SSL-Validation deaktivieren (⚠️ nur temporär)

---

## 📚 Weitere Ressourcen

- **Offizieller GitHub**: https://github.com/xerolux/violet-hass
- **Home Assistant Docs**: https://www.home-assistant.io/
- **HACS**: https://hacs.xyz/
- **Violet Controller**: https://www.pooldigital.de/
- **Community Forum**: https://community.home-assistant.io/

---

## 📝 Versionshistorie

| Version | Datum | Highlights |
|---------|-------|-----------|
| **1.0.1** | 2025-12-02 | Bug Fixes, Type Errors behoben |
| **1.0.0** | 2025-11-20 | 3-State Switch Support, 147 Sensoren |
| **0.1.0** | 2024-XX-XX | Initial Release |

---

**Made with ❤️ for the Home Assistant & Pool Community**

*Transform your pool into a smart pool - because life's too short for manual pool maintenance!* 🏊‍♀️🤖

