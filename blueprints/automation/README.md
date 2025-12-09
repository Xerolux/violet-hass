# 🔧 Violet Pool Controller Blueprints - Installation & Setup

## 📋 Übersicht
Die Blueprints bieten vorgefertigte Automatisierungen für die Violet Pool Controller Integration:

- **🌡️ Temperatursteuerung**: Intelligente Heizungs- und Solarsteuerung
- **🧪 pH-Kontrolle**: Automatische pH-Wert Korrektur mit Dosierung
- **🏊 Abdeckungssteuerung**: Wetterbasierte Cover-Automatik
- **🔄 Rückspülungssteuerung**: Automatische Filter-Reinigung
- **🔔 Modus-Benachrichtigungen**: Überwachung und Alerts für ON/OFF/AUTO Modi

## ⚡ Schnell-Installation (One-Click)

**Klicken Sie auf die Buttons unten für automatische Installation:**

| Blueprint | Beschreibung | Installation |
|-----------|--------------|--------------|
| **🌡️ Temperatur** | Intelligente Heizungs- und Solarsteuerung | [![Zu My Home Assistant öffnen](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Xerolux/violet-hass/main/blueprints/automation/pool_temperature_control.yaml) |
| **🧪 pH-Kontrolle** | Automatische pH-Wert Korrektur | [![Zu My Home Assistant öffnen](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Xerolux/violet-hass/main/blueprints/automation/pool_ph_control.yaml) |
| **🏊 Abdeckung** | Wetterbasierte Cover-Automatik | [![Zu My Home Assistant öffnen](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Xerolux/violet-hass/main/blueprints/automation/pool_cover_control.yaml) |
| **🔄 Rückspülung** | Automatische Filter-Reinigung | [![Zu My Home Assistant öffnen](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Xerolux/violet-hass/main/blueprints/automation/pool_backwash_control.yaml) |
| **🔔 Modus-Benachrichtigungen** | Überwachung der ON/OFF/AUTO Modi | [![Zu My Home Assistant öffnen](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/Xerolux/violet-hass/main/blueprints/automation/pool_mode_notifications.yaml) |

> **💡 Hinweis:** Die Buttons öffnen direkt Ihre Home Assistant Instanz und importieren den Blueprint automatisch!

---

## 📥 Installation der Blueprints

### Methode 1: Direkt über Home Assistant UI (Empfohlen)

1. **Blueprint importieren:**
   ```
   Settings → Automations & Scenes → Blueprints → Import Blueprint
   ```

2. **URLs eingeben:**
   ```
   Temperatur: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_temperature_control.yaml
   pH-Kontrolle: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_ph_control.yaml
   Abdeckung: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_cover_control.yaml
   Rückspülung: https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_backwash_control.yaml
   ```

### Methode 2: Manuelle Installation

1. **Ordner erstellen:**
   ```bash
   mkdir -p config/blueprints/automation/violet_pool_controller/
   ```

2. **Dateien kopieren:**
   ```bash
   # In Home Assistant config Verzeichnis
   cd config/blueprints/automation/violet_pool_controller/
   
   # Blueprints herunterladen
   wget https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_temperature_control.yaml
   wget https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_ph_control.yaml
   wget https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_cover_control.yaml
   wget https://github.com/xerolux/violet-hass/raw/main/blueprints/automation/pool_backwash_control.yaml
   ```

3. **Home Assistant neustarten**

## 🌡️ Temperatursteuerung Blueprint

### Benötigte Entities:
- ✅ **Pool-Temperatursensor** (sensor.violet_onewire1_value)
- ✅ **Pool-Heizung** (climate.violet_heater)
- 🔧 **Solarabsorber** (climate.violet_solar) - Optional
- 🔧 **Außentemperatursensor** - Optional
- 🔧 **Solarleistungssensor** - Optional

### Setup-Schritte:

1. **Blueprint erstellen:**
   ```
   Settings → Automations & Scenes → Blueprints
   → "Violet Pool - Intelligente Temperatursteuerung" → Use This Blueprint
   ```

2. **Konfiguration:**
   ```yaml
   Pool-Temperatursensor: sensor.violet_onewire1_value
   Pool-Heizung: climate.violet_heater
   Solarabsorber: climate.violet_solar        # Optional
   Zieltemperatur Tag: 26°C
   Zieltemperatur Nacht: 24°C
   Tagesbeginn: 07:00
   Nachtbeginn: 22:00
   Energiesparmodus: Ein
   ```

## 🧪 pH-Kontrolle Blueprint

### Benötigte Helper:
1. **Input Number für Dosier-Counter:**
   ```
   Settings → Devices & Services → Helpers → Create Helper → Number
   Name: Pool pH Dosing Counter
   Entity ID: input_number.pool_ph_dosing_counter
   Min: 0, Max: 50, Step: 1, Initial: 0
   ```

### Setup-Schritte:
```yaml
pH-Sensor: sensor.violet_ph_value
pH-Sollwert: number.violet_ph_setpoint
pH- Dosierung: switch.violet_dos_4_phm
pH+ Dosierung: switch.violet_dos_5_php
pH-Toleranz: ±0.2
Max. Dosierungen pro Tag: 10
```

## 🏊 Abdeckungssteuerung Blueprint

### Benötigte Entities:
- ✅ **Pool-Abdeckung** (cover.violet_cover)
- ✅ **Pool-Temperatursensor** (sensor.violet_onewire1_value)
- ✅ **Außentemperatursensor** (sensor.openweather_temperature)
- ✅ **Wetter-Entity** (weather.openweathermap)
- 🔧 **Pumpen-Entity** (switch.violet_pump) - Optional

### Setup-Schritte:

1. **Blueprint erstellen:**
   ```yaml
   Pool-Abdeckung: cover.violet_cover
   Pool-Temperatursensor: sensor.violet_onewire1_value
   Außentemperatursensor: sensor.openweather_temperature
   Wetter-Entity: weather.openweathermap
   ```

2. **Zeitsteuerung:**
   ```yaml
   Automatisches Öffnen: 08:00
   Öffnungszeit Wochenende: 10:00
   Automatisches Schließen: 22:00
   ```

3. **Wettersteuerung:**
   ```yaml
   Wetterbasierte Steuerung: Ein
   Regenschwelle: 70%
   Windschwelle: 25 km/h
   ```

4. **Temperatursteuerung:**
   ```yaml
   Temperaturbasierte Steuerung: Ein
   Minimale Außentemperatur: 5°C
   Max. Temperaturdifferenz: 15°C
   ```

### Features:
- ✅ **Automatisches Öffnen/Schließen** nach Zeitplan
- ✅ **Wetterschutz** bei Regen/Wind/Sturm
- ✅ **Temperaturschutz** bei niedrigen Temperaturen
- ✅ **Pumpen-Verriegelung** (kein Schließen bei laufender Pumpe)
- ✅ **Wochenend-Modus** (späteres Öffnen)
- ✅ **Manuelle Übersteuerung** mit Pause-Funktion

## 🔄 Rückspülungssteuerung Blueprint

### Benötigte Entities:
- ✅ **Rückspül-Switch** (switch.violet_backwash)
- ✅ **Pumpen-Switch** (switch.violet_pump)
- 🔧 **Nachspül-Switch** (switch.violet_backwashrinse) - Optional
- 🔧 **Filterdruck-Sensor** (sensor.violet_adc1_value) - Optional

### Benötigte Helper:
1. **Input Datetime für letzte Rückspülung:**
   ```
   Settings → Helpers → Create Helper → Date and/or time
   Name: Pool Last Backwash
   Entity ID: input_datetime.pool_last_backwash
   Has date: ✓, Has time: ✓
   ```

2. **Input Number für Pumpenlaufzeit (optional):**
   ```
   Name: Pool Pump Runtime Hours
   Entity ID: input_number.pool_pump_runtime_hours
   Min: 0, Max: 500, Step: 0.1, Unit: h
   ```

### Setup-Schritte:

1. **Basis-Konfiguration:**
   ```yaml
   Rückspül-Switch: switch.violet_backwash
   Pumpen-Switch: switch.violet_pump
   Nachspül-Switch: switch.violet_backwashrinse
   Filterdruck-Sensor: sensor.violet_adc1_value
   ```

2. **Automatisierung:**
   ```yaml
   Druckbasierte Rückspülung: Ein
   Maximaler Filterdruck: 1.5 bar
   Geplante Rückspülung: Ein
   Rückspül-Intervall: 7 Tage
   Rückspül-Uhrzeit: 03:00
   ```

3. **Parameter:**
   ```yaml
   Rückspül-Dauer: 120s
   Nachspül-Dauer: 30s
   Pumpen-Stopp vor Rückspülung: 30s
   Pumpen-Start nach Rückspülung: 60s
   ```

### Features:
- ✅ **Druckbasierte Auslösung** bei hohem Filterdruck
- ✅ **Zeitbasierte Rückspülung** nach Intervallen
- ✅ **Laufzeitbasierte Auslösung** nach Pumpenstunden
- ✅ **Automatischer Nachspül-Zyklus**
- ✅ **Wasserstands-Prüfung** vor Rückspülung
- ✅ **Sichere Pumpensteuerung** mit Wartezeiten

## 📱 Benachrichtigungen einrichten

### Mobile App Benachrichtigung:

1. **Service ermitteln:**
   ```
   Developer Tools → Services → Suche: "notify"
   → notify.mobile_app_dein_handy_name
   ```

2. **In Blueprint eingeben:**
   ```
   Benachrichtigungs-Service: notify.mobile_app_iphone
   ```

### Telegram/Discord/Slack:
```
notify.telegram_bot
notify.discord_webhook  
notify.slack_webhook
```

## 💡 Beispiel-Benachrichtigungen

### Temperatursteuerung:
- 🌅 "Pool-Temperatur: Tagestemperatur auf 26°C gesetzt"
- ☀️ "Solar-Heizung aktiviert (1500W), Ziel: 26°C"
- 🔥 "Pool-Heizung aktiviert: 23.5°C → 26°C (Δ2.5°C)"

### pH-Kontrolle:
- 🔻 "pH-Korrektur: 7.6 → 7.2, pH-Minus für 30s dosiert"
- ⚠️ "pH-Dosierung gestoppt: Max. 10 Dosierungen erreicht"

### Abdeckungssteuerung:
- 🌧️ "Wetter-Schutz: Abdeckung wegen Regen geschlossen"
- 🌡️ "Temperatur-Schutz: Außen 3°C, Abdeckung geschlossen"

### Rückspülung:
- 🔄 "Automatische Rückspülung: Filterdruck 1.8 bar (Max: 1.5)"
- ✅ "Rückspülung abgeschlossen: 120s Backwash + 30s Rinse"

## 🚨 Troubleshooting

### Blueprint nicht sichtbar:
```bash
# Logs prüfen:
tail -f config/home-assistant.log | grep blueprint

# Dateiberechtigungen:
chmod 644 config/blueprints/automation/violet_pool_controller/*.yaml

# HA neustarten
```

### Entities nicht gefunden:
- Integration korrekt installiert?
- Entities in Developer Tools sichtbar?
- Feature in Integration aktiviert?

### Benachrichtigungen funktionieren nicht:
- Service-Name korrekt? (mit notify. Prefix)
- Mobile App installiert und angemeldet?
- Test über Developer Tools → Services

### Automatisierung läuft nicht:
- Trigger-Conditions erfüllt?
- Entities verfügbar (nicht "unavailable")?
- Mode: single - nur eine Ausführung gleichzeitig

## 🔧 Anpassungen

### Eigene Trigger hinzufügen:
```yaml
# In Blueprint YAML ergänzen:
- platform: state
  entity_id: input_boolean.my_custom_trigger
  to: 'on'
  id: custom_trigger
```

### Zeiten anpassen:
```yaml
# Andere Überprüfungsintervalle:
- platform: time_pattern
  minutes: /15  # Alle 15 Minuten statt 30
```

### Zusätzliche Bedingungen:
```yaml
# Z.B. nur bei Anwesenheit:
- condition: state
  entity_id: person.homeowner
  state: 'home'
```

Die Blueprints sind modular aufgebaut und können individuell angepasst werden!
