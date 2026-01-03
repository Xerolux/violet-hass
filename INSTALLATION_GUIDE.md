# Violet Pool Controller - Installation Guide

## Installation via HACS (empfohlen)

### Schritt 1: HACS Custom Repository hinzufügen

1. Öffne HACS in Home Assistant
2. Klicke auf die 3 Punkte (⋮) oben rechts
3. Wähle "Custom repositories"
4. Füge hinzu:
   - **Repository**: `https://github.com/PoolDigitalGmbH/violet-hass`
   - **Category**: Integration
5. Klicke "Add"

### Schritt 2: Integration installieren

1. Gehe zu HACS → Integrations
2. Suche nach "Violet Pool Controller"
3. Klicke "Download"
4. Starte Home Assistant neu

### Schritt 3: Integration konfigurieren

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke **+ Integration hinzufügen**
3. Suche nach "Violet Pool Controller"
4. Gib die Verbindungsdaten ein:
   - **Controller URL**: `http://192.168.178.55` (oder deine IP)
   - **Benutzername**: `Basti` (dein Controller-Benutzer)
   - **Passwort**: `dein-passwort`
   - **Update-Intervall**: 30 Sekunden (Standard)

5. Klicke **Weiter**

### Schritt 4: Features auswählen

Wähle die Features aus, die dein Pool hat:
- ✅ **Pump** (Filterpumpe)
- ✅ **Solar** (Solarheizung)
- ✅ **Heater** (Heizung)
- ✅ **Chlorine Control** (Chlor-Dosierung)
- ✅ **pH Control** (pH-Dosierung)
- ⬜ **Backwash** (Rückspülung) - falls vorhanden
- ⬜ **Cover** (Poolabdeckung) - falls vorhanden
- ⬜ **Light** (Beleuchtung) - falls vorhanden
- ⬜ **DMX Scenes** (DMX-Beleuchtung) - falls vorhanden

### Schritt 5: Sensoren auswählen (optional)

Die Integration erkennt automatisch alle verfügbaren Sensoren. Du kannst auswählen, welche du nutzen möchtest:
- Temperatursensoren (OneWire 1-12)
- Wasser-Chemie (pH, ORP, Chlor)
- Analog-Eingänge (ADC1-6)
- System-Sensoren (CPU, Memory, Uptime)
- Digital-Eingänge (DI1-12)

### Schritt 6: Fertig!

Die Integration erstellt jetzt alle Entities:
- **Switches**: `switch.violet_pump`, `switch.violet_solar`, etc.
- **Sensors**: `sensor.violet_pool_temperature`, `sensor.violet_ph_value`, etc.
- **Climate**: `climate.violet_heater`, `climate.violet_solar`
- **Number**: `number.violet_ph_setpoint`, `number.violet_orp_setpoint`, etc.
- **Binary Sensors**: `binary_sensor.violet_input_1`, etc.

---

## Manuelle Installation

### Schritt 1: Repository klonen

```bash
cd /config/custom_components
git clone https://github.com/PoolDigitalGmbH/violet-hass.git violet_pool_controller
```

### Schritt 2: Dependencies installieren

Die Integration nutzt nur `aiohttp`, das bereits in Home Assistant enthalten ist.

### Schritt 3: Home Assistant neu starten

```bash
ha core restart
```

### Schritt 4: Integration konfigurieren

Folge den Schritten 3-6 von oben.

---

## Erste Schritte nach der Installation

### 1. Entities prüfen

Gehe zu **Einstellungen** → **Geräte & Dienste** → **Violet Pool Controller**

Du solltest sehen:
- **1 Gerät**: Violet Pool Controller
- **~50+ Entities**: Je nach ausgewählten Features

### 2. Dashboard erstellen

Erstelle ein neues Dashboard für deinen Pool:

**Beispiel-Karten:**

```yaml
# Poolübersicht
type: entities
title: Pool Übersicht
entities:
  - entity: sensor.violet_pool_temperature
    name: Beckenwasser
  - entity: sensor.violet_outdoor_temperature
    name: Außentemperatur
  - entity: sensor.violet_solar_temperature
    name: Solarabsorber
  - entity: sensor.violet_ph_value
    name: pH-Wert
  - entity: sensor.violet_orp_value
    name: Redox
  - entity: sensor.violet_chlorine_level
    name: Chlor

# Steuerung
type: entities
title: Pool Steuerung
entities:
  - entity: switch.violet_pump
    name: Filterpumpe
  - entity: switch.violet_solar
    name: Solar
  - entity: switch.violet_heater
    name: Heizung
  - entity: climate.violet_heater
    name: Heizung Sollwert

# System-Info
type: entities
title: System
entities:
  - entity: sensor.violet_firmware_version
  - entity: sensor.violet_cpu_uptime
  - entity: sensor.violet_cpu_temperature
  - entity: sensor.violet_memory_used
```

### 3. Automatisierungen erstellen

**Beispiel: Pumpe bei Frostgefahr einschalten**

```yaml
automation:
  - alias: "Pool: Frostschutz"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_outdoor_temperature
        below: 2
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "off"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_pump
      - service: notify.mobile_app
        data:
          message: "Frostschutz aktiviert! Pumpe eingeschaltet bei {{ states('sensor.violet_outdoor_temperature') }}°C"
```

**Beispiel: Solar-Heizung automatisch steuern**

```yaml
automation:
  - alias: "Pool: Solar Auto"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.violet_solar_temperature') | float >
             states('sensor.violet_pool_temperature') | float + 3 }}
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_solar
```

---

## Erweiterte Konfiguration

### Update-Intervall anpassen

Standard: 30 Sekunden

So ändern:
1. **Einstellungen** → **Geräte & Dienste**
2. Klicke auf "Violet Pool Controller"
3. Klicke **Konfigurieren**
4. Ändere "Update-Intervall"

**Empfehlungen:**
- **10-20 Sekunden**: Wenn du schnelle Reaktionen brauchst
- **30-60 Sekunden**: Normaler Betrieb (empfohlen)
- **120+ Sekunden**: Minimale Belastung

### Rate Limiting

Die Integration schützt deinen Controller automatisch:
- **Max. 10 Requests pro Sekunde**
- **Burst-Limit: 3 Requests**
- **Priority Queue**: Wichtige Befehle (Switches) werden priorisiert

### Logging aktivieren

Für Debugging:

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.violet_pool_controller: debug
```

---

## Troubleshooting

### Problem: "Connection refused"

**Lösung:**
- Prüfe IP-Adresse des Controllers
- Stelle sicher, dass Controller im gleichen Netzwerk ist
- Teste: `curl http://192.168.178.55/getReadings?ALL`

### Problem: "Authentication failed"

**Lösung:**
- Prüfe Benutzername und Passwort
- Controller erlaubt nur Basic Auth
- Teste: `curl -u "Benutzername:Passwort" http://192.168.178.55/getReadings?ALL`

### Problem: Entities fehlen

**Lösung:**
1. Gehe zu **Konfigurieren**
2. Wähle **Features neu auswählen**
3. Aktiviere fehlende Features
4. **Neu laden** klicken

### Problem: Werte werden nicht aktualisiert

**Lösung:**
- Prüfe Update-Intervall
- Schaue in die Logs: `tail -f /config/home-assistant.log | grep violet`
- Prüfe Controller-Erreichbarkeit

### Problem: Switches schalten nicht

**Lösung:**
- Prüfe ob Controller im **MANUAL** Modus ist (nicht AUTO)
- Manche Ausgänge können durch Controller-Regeln blockiert sein
- Schaue in Controller-Webinterface nach Fehlermeldungen

---

## Services

Die Integration stellt folgende Services bereit:

### `violet_pool_controller.control_pump`

Erweiterte Pumpen-Steuerung:

```yaml
service: violet_pool_controller.control_pump
data:
  speed: 2        # 1, 2, oder 3
  duration: 3600  # Sekunden (optional)
  mode: "boost"   # "boost", "eco", "force_off", "auto"
```

### `violet_pool_controller.smart_dosing`

Manuelle Dosierung:

```yaml
service: violet_pool_controller.smart_dosing
data:
  dosing_type: "Chlor"  # "Chlor", "pH-", "pH+", "Flockmittel"
  duration: 10          # Sekunden
```

**⚠️ WARNUNG:** Controller blockiert direkte Dosing-ON Befehle aus Sicherheitsgründen!

### `violet_pool_controller.control_dmx_scenes`

DMX-Szenen steuern:

```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  scene: 1     # 1-12
  state: "on"  # "on", "off", "auto"
```

---

## Unterstützte Features

| Feature | Sensor | Switch | Climate | Number | Cover |
|---------|--------|--------|---------|--------|-------|
| Pumpe | ✅ | ✅ | - | - | - |
| Solar | ✅ | ✅ | ✅ | ✅ | - |
| Heizung | ✅ | ✅ | ✅ | ✅ | - |
| Chlor-Dosierung | ✅ | ✅ | - | ✅ | - |
| pH-Dosierung | ✅ | ✅ | - | ✅ | - |
| Rückspülung | ✅ | ✅ | - | - | - |
| Poolabdeckung | ✅ | - | - | - | ✅ |
| Beleuchtung | ✅ | ✅ | - | - | - |
| DMX Scenes | ✅ | ✅ | - | - | - |
| Temperaturen | ✅ | - | - | - | - |
| Wasser-Chemie | ✅ | - | - | ✅ | - |
| Digital Inputs | ✅ | - | - | - | - |
| System-Info | ✅ | - | - | - | - |

---

## Support & Links

- **GitHub**: https://github.com/PoolDigitalGmbH/violet-hass
- **Issues**: https://github.com/PoolDigitalGmbH/violet-hass/issues
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Lizenz

MIT License - siehe [LICENSE](LICENSE)

**Hinweis:** Diese Integration ist nicht offiziell von PoolDigital GmbH & Co. KG unterstützt.
