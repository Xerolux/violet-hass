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


> **Verwandle deinen Pool in einen Smart Pool!** Diese umfassende Home Assistant Integration bietet vollständige Kontrolle und Überwachung deines Violet Pool Controllers.

![Violet Home Assistant Integration][logo]

## 📋 Inhaltsverzeichnis

- [🌟 Features](#-features)
- [⚡ Schnellstart](#-schnellstart) 
- [📦 Installation](#-installation)
- [⚙️ Konfiguration](#️-konfiguration)
- [🧩 Verfügbare Entitäten](#-verfügbare-entitäten)
- [🤖 Automatisierungen](#-automatisierungen)
- [🚨 Fehlerbehebung](#-fehlerbehebung)
- [💝 Unterstützung](#-unterstützung)

---

## 🌟 Features

### 🎯 **Kernfunktionen**
- **🌡️ Intelligente Klimasteuerung** - Heizung & Solar mit Zeitplanung
- **🧪 Automatische Chemie-Dosierung** - pH & Chlor mit Sicherheitsgrenzen  
- **🏊 Smarte Abdeckungssteuerung** - Wetterabhängige Automatisierung
- **💧 Filter-Management** - Automatische Rückspülung & Wartung
- **💡 LED-Beleuchtung** - Vollständige RGB/DMX-Steuerung
- **📱 Mobile-Ready** - Kontrolle von überall über HA App
- **🔧 100% Lokal** - Keine Cloud erforderlich, vollständige Privatsphäre

### 📊 **Überwachung & Sensoren**
- **Wasserchemie**: pH, Redox (ORP), Chlorgehalt mit Trend-Tracking
- **Temperaturen**: Pool, Umgebung, Solar-Kollektor
- **System-Status**: Pumpen, Heizung, Filterdruck, Wasserstände  
- **Anlagen-Gesundheit**: Laufzeit, Fehlererkennung, Wartungsalarme

### 🤖 **Smart Automation**
- **Energie-Optimierung**: PV-Überschuss-Modus für Solarheizung
- **Wetter-Integration**: Automatische Reaktionen auf Umweltbedingungen
- **Wartungsplanung**: Intelligente Zyklen für alle Anlagenteile
- **Sicherheitssysteme**: Notabschaltungen & Überlaufschutz
- **Custom Scenes**: Pool-Party, Eco, Winter & Urlaubs-Modi

---

## ⚡ Schnellstart

### 1. Vorbereitung
- ✅ Home Assistant 2024.6+ installiert (getestet mit 2024.12.0 und 2025.1.4)
- ✅ HACS installiert ([Anleitung](https://hacs.xyz/docs/setup/download))
- ✅ Violet Pool Controller im Netzwerk erreichbar
- ✅ Controller-IP-Adresse bekannt (z.B. 192.168.1.100)

### 2. Installation (2 Minuten)
```
HACS → Integrationen → Custom Repository hinzufügen:
Repository: https://github.com/xerolux/violet-hass
Kategorie: Integration
```

### 3. Konfiguration (3 Minuten)
```
Einstellungen → Geräte & Dienste → Integration hinzufügen → "Violet Pool Controller"
Host eingeben → Features auswählen → Fertig!
```

**🎉 Geschafft!** Dein Pool ist jetzt smart und bereit für Automatisierungen.

---

## 📦 Installation

### 🚀 **HACS Installation (Empfohlen)**

**Schritt 1: Repository hinzufügen**
1. HACS öffnen → ⋮ (drei Punkte) → "Benutzerdefinierte Repositorys"
2. URL: `https://github.com/xerolux/violet-hass`
3. Kategorie: "Integration" → "Hinzufügen"

**Schritt 2: Integration installieren**
1. Nach "Violet Pool Controller" suchen
2. "Herunterladen" klicken
3. Home Assistant neu starten

### 🔧 **Manuelle Installation**

<details>
<summary>Für Entwickler & Fortgeschrittene (Klicken zum Erweitern)</summary>

```bash
# Option 1: Git Clone
cd /config/custom_components/
git clone https://github.com/xerolux/violet-hass.git violet_pool_controller

# Option 2: Download
wget https://github.com/xerolux/violet-hass/archive/main.zip
unzip main.zip
mv violet-hass-main/custom_components/violet_pool_controller /config/custom_components/

# Neustart erforderlich
```
</details>

---

## ⚙️ Konfiguration

### 🎯 **Basis-Setup**

Die Konfiguration erfolgt komplett über die UI – kein YAML nötig!

**Integration hinzufügen:**
```
Einstellungen → Geräte & Dienste → Integration hinzufügen → "Violet Pool Controller"
```

### 📋 **Konfigurationsoptionen**

| Einstellung | Beispiel | Beschreibung |
|-------------|----------|--------------|
| **Host** | `192.168.1.100` | IP-Adresse des Controllers |
| **Username/Password** | `admin` / `••••` | Optional für Basic Auth |
| **SSL verwenden** | ☑ | Bei HTTPS-Nutzung aktivieren |
| **Abfrageintervall** | `30s` | Update-Frequenz (10–300 s) |
| **Pool-Größe** | `50 m³` | Für Dosierungsberechnungen |
| **Pool-Typ & Desinfektion** | `outdoor`, `chlorine` | Optimiert Default-Werte |

### 🎛️ **Feature- & Sensor-Auswahl**

Der Einrichtungsassistent führt dich durch zwei Auswahllisten:

1. **Aktive Features** – nur Komponenten aktivieren, die auch verkabelt sind (z. B. Heizung, Solar, PV-Überschuss, digitale Eingänge).
2. **Dynamische Sensoren** – beim ersten Start werden alle Sensoren des Controllers gelesen und gruppiert. Du kannst per Mehrfachauswahl entscheiden, welche Werte in Home Assistant landen sollen.

> 💡 Keine Auswahl getroffen? Dann erstellt die Integration automatisch alle verfügbaren Sensoren (voll kompatibel zu bestehenden Installationen).

### 🧰 Erweiterte Optionen

Über *Einstellungen → Geräte & Dienste → Violet Pool Controller → Konfigurieren* kannst du jederzeit nachjustieren:

- Abfrageintervall, Timeout und Retry-Limits
- Aktive Features (z. B. PV-Überschuss nur im Sommer)
- Sensor-Gruppen (praktisch, wenn du die Anzeige auf die wichtigsten Werte reduzieren willst)

Alle Änderungen werden ohne Neustart übernommen.

---

## 🖥️ Lovelace Dashboard

Damit du sofort loslegen kannst, liegt ein fertiges Dashboard bei:

- YAML-Datei: [`Dashboard/pool-dashboard.yaml`](Dashboard/pool-dashboard.yaml)
- Vorschau-Bild: ![Pool Dashboard Vorschau](screenshots/pool-dashboard.svg)

**Installation:**

1. Datei `Dashboard/pool-dashboard.yaml` nach `/config/` kopieren.
2. Optional: `screenshots/pool-dashboard.svg` nach `/config/www/violet-hass/` legen, damit das Dashboard das Vorschaubild findet.
3. In Home Assistant → *Einstellungen → Dashboards* → ⋮ → *Dashboard aus YAML importieren*.
4. Falls deine Entitäten anders heißen (z. B. wegen mehrerer Controller), per Suchen/Ersetzen in der YAML-Datei anpassen.

Das Dashboard nutzt ausschließlich Standard-Karten – keine zusätzlichen Custom-Cards nötig.

---

## 🧩 Verfügbare Entitäten

Die Integration erstellt automatisch alle relevanten Entitäten basierend auf deiner Controller-Konfiguration:

### 🌡️ **Klimasteuerung**
```yaml
climate.pool_heater          # Hauptheizung mit Thermostat
climate.pool_solar           # Solar-Kollektor Management
```

### 📊 **Sensoren** 
```yaml
# Wasserchemie
sensor.pool_temperature      # Aktuelle Wassertemperatur  
sensor.pool_ph_value         # pH-Wert (6.0-8.5)
sensor.pool_orp_value        # Redoxpotential (mV)
sensor.pool_chlorine_level   # Freies Chlor (mg/l)

# System-Status
sensor.filter_pressure       # Filtersystem-Druck
sensor.water_level          # Pool-Wasserstand
sensor.pump_runtime         # Pumpen-Laufzeit heute
sensor.energy_consumption   # Energieverbrauch
```

### 💡 **Schalter & Steuerungen**
```yaml
# Hauptkomponenten
switch.pool_pump            # Filterpumpe (variable Geschwindigkeit)
switch.pool_heater          # Heizung Ein/Aus
switch.pool_solar           # Solar-Zirkulation
switch.pool_lighting        # Pool-Beleuchtung

# Chemie-Dosierung  
switch.ph_dosing_minus      # pH- Dosierpumpe
switch.ph_dosing_plus       # pH+ Dosierpumpe
switch.chlorine_dosing      # Chlor-Dosierung

# Wartung & Extras
switch.backwash             # Rückspül-Zyklus
switch.pool_cover           # Abdeckung
switch.pv_surplus_mode      # Solar-Überschuss-Modus
```

---

## 🤖 Automatisierungen

### 🎯 **Custom Services**

Die Integration bietet spezialisierte Services für erweiterte Automatisierung:

<details>
<summary><strong>🔧 Kern-Services</strong> (Klicken zum Erweitern)</summary>

#### `violet_pool_controller.control_pump`
Pumpe in Automatikmodus schalten:
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.pool_pump
data:
  action: auto
```

#### `violet_pool_controller.manage_pv_surplus`
Solar-Überschuss-Modus aktivieren:
```yaml
service: violet_pool_controller.manage_pv_surplus
target:
  entity_id: switch.pv_surplus_mode
data:
  mode: activate
  pump_speed: 2   # Geschwindigkeitsstufe 1-3
```
</details>

<details>
<summary><strong>🧪 Chemie-Services</strong> (Klicken zum Erweitern)</summary>

#### `violet_pool_controller.smart_dosing`
Manuelle Dosierung auslösen:
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.ph_dosing_minus
data:
  dosing_type: "pH-"
  action: manual_dose
  duration: 30  # Dosierdauer in Sekunden
```
</details>

### 📋 **Beispiel-Automatisierungen**

#### 🌡️ **Intelligente Poolheizung mit Solar-Unterstützung**

```yaml
# Heize Pool wenn Solarkollektor > 35°C und Pool < 28°C
- alias: "Pool: Solarheizung bei Sonne"
  trigger:
    - platform: numeric_state
      entity_id: sensor.solar_temp
      above: 35
  condition:
    - condition: numeric_state
      entity_id: sensor.pool_temperature
      below: 28
    - condition: state
      entity_id: switch.pool_pump
      state: "on"
  action:
    - service: climate.turn_on
      target:
        entity_id: climate.pool_heater
    - service: climate.set_temperature
      target:
        entity_id: climate.pool_heater
      data:
        temperature: 28
```

#### 🧪 **Automatische pH-Korrektur**

```yaml
# pH-Plus dosieren wenn pH < 7.0
- alias: "Pool: pH zu niedrig - dosiere pH+"
  trigger:
    - platform: numeric_state
      entity_id: sensor.pool_ph_value
      below: 7.0
      for:
        minutes: 5
  condition:
    - condition: state
      entity_id: switch.pool_pump
      state: "on"
  action:
    - service: switch.turn_on
      target:
        entity_id: switch.ph_dosing_plus
    - wait_template: "{{ states('sensor.pool_ph_value') | float > 7.2 }}"
      timeout:
        minutes: 30
    - service: switch.turn_off
      target:
        entity_id: switch.ph_dosing_plus
```

#### ⚡ **Energie-Optimierung mit PV-Überschuss**

```yaml
# Aktiviere PV-Überschuss-Modus bei hohem Solarertrag
- alias: "Pool: PV-Überschuss nutzen"
  trigger:
    - platform: numeric_state
      entity_id: sensor.pv_power_export
      above: 2000  # Watt
  action:
    - service: violet_pool_controller.manage_pv_surplus
      target:
        entity_id: switch.pv_surplus_mode
      data:
        mode: activate
        pump_speed: 2
```

#### 🌧️ **Abdeckung schließen bei Regen**

```yaml
- alias: "Pool: Abdeckung bei Regen schließen"
  trigger:
    - platform: state
      entity_id: weather.pools_weather
      to: "rainy"
  action:
    - service: cover.close_cover
      target:
        entity_id: cover.pool_cover
```

### 📋 **Automation Blueprints**

**Installation:**
```
Einstellungen → Automatisierungen & Szenen → Blueprints → Blueprint importieren
```

**Verfügbare Blueprints:**
- 🌡️ **Intelligente Temperatursteuerung** - Tag/Nacht-Modi mit Solar-Priorität
- 🧪 **pH-Management** - Automatische Dosierung mit Sicherheitsgrenzen
- ⚡ **Energie-Optimierung** - PV-Überschuss-Nutzung
- 🌧️ **Wetter-Reaktionen** - Abdeckung bei Regen/Wind
- 🏊 **Pool-Modi** - Party, Eco, Winter & Urlaubs-Automatisierungen

---

## 🚨 Fehlerbehebung

### ⚡ **Häufige Probleme & Lösungen**

| Problem | Schnelle Lösung |
|---------|-----------------|
| **Keine Verbindung** | IP-Adresse & Firewall prüfen |
| **SSL-Fehler** | "SSL verwenden" Setting anpassen |
| **Entitäten fehlen** | Controller-Features & Integration neu laden |
| **Langsame Updates** | Abfrageintervall verringern (min. 10s) |

### 🔍 **Detaillierte Lösungen**

#### ❌ **"Failed to connect" - Keine Verbindung möglich**

**Symptome:**
- Integration zeigt "Nicht verfügbar"
- Log-Meldung: "Connection refused" oder "Timeout"

**Lösungsschritte:**
1. **Konnektivität prüfen:**
   ```bash
   ping 192.168.1.100
   curl http://192.168.1.100/getReadings?ALL
   ```
2. **Firewall prüfen:**
   - Stelle sicher, dass Port 80 (HTTP) oder 443 (HTTPS) nicht blockiert ist
   - Home Assistant Host muss Zugriff auf Controller-Subnetz haben
3. **Controller-Status prüfen:**
   - Controller-WebUI erreichbar? (http://192.168.1.100)
   - Licht am Controller leuchtet?

#### 🔐 **SSL_Zertifiziert-Fehler**

**Symptome:**
- Log-Meldung: "SSL: CERTIFICATE_VERIFY_FAILED"
- Integration kann bei "SSL verwenden" nicht aktiviert werden

**Lösung:**
- Option 1: **"SSL verwenden" deaktivieren** (für selbstsignierte Zertifikate)
- Option 2: **"Zertifikat verifizieren" deaktivieren** im Config-Flow
- Option 3: Eigene CA-Zertifikate in HA importieren (Fortgeschritten)

#### 📊 **Sensoren zeigen "Unbekannt" oder falsche Werte**

**Mögliche Ursachen:**
1. **Feature nicht aktiviert:**
   - Gehe zu: *Einstellungen → Geräte & Dienste → Violet Pool Controller → Konfigurieren*
   - Prüfe unter "Aktive Features" ob das korrekte Feature aktiviert ist
   - Speichern und Integration neu laden

2. **Falsche Sensor-Auswahl:**
   - Beim Setup wurde die Gruppe des Sensors abgewählt
   - Lösung: Neu konfigurieren und alle relevanten Sensor-Gruppen auswählen

3. **Controller-Fehler:**
   - Prüfe Controller-Logs: http://192.168.1.100/logs
   - Restart des Controllers: Strom für 30 Sekunden entfernen

#### ⏱️ **Entitäten aktualisieren nicht (stale values)**

**Ursache:** Abfrageintervall zu hoch oder Controller antwortet nicht

**Lösung:**
1. **Abfrageintervall reduzieren:**
   - Gehe zu: *Einstellungen → Geräte & Dienste → Violet Pool Controller → Konfigurieren*
   - "Abfrageintervall" auf 15-30 Sekunden setzen
   - Speichern

2. **Timeout anpassen:**
   - "Timeout" auf 10-15 Sekunden erhöhen
   - Besonders bei langsamen Netzwerken

3. **Manueller Refresh:**
   ```
   Einstellungen → Geräte & Dienste → Violet Pool Controller → ⋮ → Neu laden
   ```

#### 🐛 **Integration startet nicht (Setup: Failed)**

**Debug-Schritte:**

1. **Logs prüfen:**
   ```bash
   tail -100 /config/home-assistant.log | grep violet
   ```

2. **Config Exportieren:**
   ```
   Einstellungen → Geräte & Dienste → Violet Pool Controller → ⋮ → Diagnosedaten exportieren
   ```

3. **Vollständiger Neustart:**
   - Integration entfernen
   - HA neu starten
   - Integration neu einrichten

### 🔍 **Werkzeuge zur Fehlersuche**

#### **Diagnostic Export Service**

Nutze den integrierten Diagnostic-Service:

```yaml
service: violet_pool_controller.export_diagnostic_logs
data:
  device_id:
    - "deine_controller_id"
  save_to_file: true
```

Dieser erstellt eine detaillierte Log-Datei mit:
- ✅ Konfiguration
- ✅ Alle Sensorwerte
- ✅ Aktive Fehler
- ✅ Laufzeiten
- ✅ Historie der letzten 24h

#### **Weitere Diagnose-Services**

Die Integration bietet zusätzliche Services zur gezielten Fehleranalyse:

- `violet_pool_controller.get_connection_status`: Detaillierte Verbindungsmetriken und Gesundheitsstatus.
- `violet_pool_controller.get_error_summary`: Zusammenfassung aktueller Fehler mit Lösungsvorschlägen.
- `violet_pool_controller.test_connection`: Direkter Verbindungstest zum Controller mit Latenzmessung.
- `violet_pool_controller.clear_error_history`: Löscht die Fehlerhistorie nach erfolgreicher Behebung.

#### **Live API-Test**

Teste die API-Verbindung direkt:

```bash
# Alle Readings abrufen
curl http://192.168.1.100/getReadings?ALL | jq

# Konfiguration prüfen
curl http://192.168.1.100/getConfig?TARGET_PH,TARGET_ORP

# Manuelles Schalten testen
curl "http://192.168.1.100/setFunctionManually?PUMP=ON"
```

#### **Log-Level erhöhen**

Für detaillierte Logs:

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.violet_pool_controller: debug
```

**Wichtige Log-Meldungen:**
- `ERROR` - Kritische Fehler die die Funktion beeinträchtigen
- `WARNING` - Probleme die automatisch behoben wurden
- `DEBUG` - Detaillierte Information für Fehlersuche
- `INFO` - Normale Operations-Meldungen

### 📞 **Support erhalten**

Wenn du keine Lösung findest:

1. **GitHub Issues** - [Bug melden][issues]
   - Wähle passendes Template aus
   - Logs anhängen (`!secret` entfernen!)
   - HA-Version und Integrations-Version angeben

2. **Community** - [Discord][discord] | [Forum][forum]
   - Andere Nutzer haben vielleicht ähnliche Probleme gehabt
   - Suche nach Fehlercodes und Fehlermeldungen

3. **Direkt Kontakt** - [git@xerolux.de](mailto:git@xerolux.de)
   - Für geschäftliche Anfragen
   - Support-Priorität für Sponsoren

### 📚 **Bekannte Probleme & Workarounds**

| Issue | Status | Workaround |
|-------|--------|-----------|
| **Cover öffnet nicht vollständig** | Bekannt | Manuell in App korrigieren, dann Neu laden |
| **pH-Wert springt** | Controller-Bug | Sensor kalibrieren (Controller-WebUI) |
| **Heizung schaltet nicht ein** | Feature-Abhängig | Prüfe ob "heating" Feature aktiviert |
| **PV-Überschuss nicht verfügbar** | Hardware-Abhängig | Requires compatible PV inverter |

---

## 💝 Unterstützung

Diese Integration wird in meiner Freizeit entwickelt. Wenn sie dir hilft, zeige etwas Liebe:

[![GitHub Sponsor](https://img.shields.io/github/sponsors/xerolux?logo=github&style=for-the-badge&color=blue)](https://github.com/sponsors/xerolux)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-xerolux-blue?logo=ko-fi&style=for-the-badge)](https://ko-fi.com/xerolux)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-xerolux-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://www.buymeacoffee.com/xerolux)

**Andere Unterstützungsmöglichkeiten:**
- ⭐ Repository auf GitHub sternen
- 📢 Mit anderen Pool-Besitzern teilen  
- 🐛 Bugs melden & Verbesserungen vorschlagen
- 📝 Code oder Dokumentation beitragen
- 💬 Anderen in Community-Foren helfen

---

## 🏊 Über den Violet Pool Controller

![Violet Pool Controller][pbuy]

Der **VIOLET Pool Controller** von [PoolDigital GmbH & Co. KG](https://www.pooldigital.de/) ist ein Premium Smart Pool Automation System aus deutscher Entwicklung.

**Warum Violet?**
- 🔧 **Komplette Pool-Verwaltung** - Alles aus einer Hand
- 📱 **Smart Home Ready** - JSON API für nahtlose Integration  
- 🛡️ **Sicherheit First** - Mehrfache Schutz- & Überwachungssysteme
- ⚡ **Energieeffizient** - Intelligente Planung & PV-Integration
- 🇩🇪 **Made in Germany** - Premium Qualität & Support

**Bezugsquellen:**
- **Offizieller Shop:** [pooldigital.de](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart)
- **Community:** [PoolDigital Forum](http://forum.pooldigital.de/)

---

## 🤝 Mitwirken

Beiträge sind herzlich willkommen! Ob Bug-Fixes, neue Features, Dokumentation oder Tests:

---

---

<div align="center">

**Made with ❤️ for the Home Assistant & Pool Community**

*Transform your pool into a smart pool - because life's too short for manual pool maintenance!* 🏊‍♀️🤖

[![GitHub][github-shield]][github] [![Discord][discord-shield]][discord] [![Email](https://img.shields.io/badge/email-git%40xerolux.de-blue?style=for-the-badge&logo=gmail)](mailto:git@xerolux.de) [![Tesla](https://img.shields.io/badge/Tesla-Referral-red?style=for-the-badge&logo=tesla)](https://ts.la/sebastian564489)

</div>

---

<!-- Links -->
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
[logo]: https://github.com/xerolux/violet-hass/raw/main/custom_components/violet_pool_controller/logo.png
[pbuy]: https://github.com/xerolux/violet-hass/raw/main/screenshots/violetbm.jpg
[github]: https://github.com/xerolux/violet-hass
[github-shield]: https://img.shields.io/badge/GitHub-xerolux/violet--hass-blue?style=for-the-badge&logo=github
[issues]: https://github.com/xerolux/violet-hass/issues
