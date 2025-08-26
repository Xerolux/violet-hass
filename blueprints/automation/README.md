# 🔧 Violet Pool Controller Blueprints - Installation & Setup

## 📋 Übersicht
Die Blueprints bieten vorgefertigte Automatisierungen für die Violet Pool Controller Integration:

- **Temperatursteuerung**: Intelligente Heizungs- und Solarsteuerung
- **pH-Kontrolle**: Automatische pH-Wert Korrektur mit Dosierung

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

3. **Erweiterte Optionen:**
   ```yaml
   Außentemperatursensor: sensor.openweather_temperature
   Solarleistungssensor: sensor.solar_power
   Minimale Solarleistung: 1000W
   Max. Temperaturdifferenz: 2.0°C
   ```

## 🧪 pH-Kontrolle Blueprint

### Benötigte Entities:
- ✅ **pH-Sensor** (sensor.violet_ph_value)
- ✅ **pH-Sollwert** (number.violet_ph_setpoint)
- ✅ **pH-Minus Dosierung** (switch.violet_dos_4_phm)
- ✅ **pH-Plus Dosierung** (switch.violet_dos_5_php)

### Voraussetzungen - Input Number Helper erstellen:

1. **Helper erstellen:**
   ```
   Settings → Devices & Services → Helpers → Create Helper → Number
   ```

2. **Konfiguration:**
   ```yaml
   Name: Pool pH Dosing Counter
   Entity ID: input_number.pool_ph_dosing_counter
   Minimum: 0
   Maximum: 50
   Step: 1
   Initial Value: 0
   Unit: Dosierungen
   ```

### Setup-Schritte:

1. **Blueprint erstellen:**
   ```
   Settings → Automations & Scenes → Blueprints
   → "Violet Pool - Intelligente pH-Kontrolle" → Use This Blueprint
   ```

2. **Basis-Konfiguration:**
   ```yaml
   pH-Sensor: sensor.violet_ph_value
   pH-Sollwert: number.violet_ph_setpoint
   pH- Dosierung: switch.violet_dos_4_phm
   pH+ Dosierung: switch.violet_dos_5_php
   pH-Toleranz: ±0.2
   ```

3. **Sicherheitseinstellungen:**
   ```yaml
   Dosierdauer pH-: 30s
   Dosierdauer pH+: 30s
   Max. Dosierungen pro Tag: 10
   Wartezeit zwischen Dosierungen: 60min
   ```

4. **Pumpen-Integration:**
   ```yaml
   Pumpen-Check aktivieren: Ein
   Filterpumpe: binary_sensor.violet_pump_state
   ```

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

### Beispiel Telegram/Discord:
```
notify.telegram_bot
notify.discord_webhook
```

## ⚙️ Erweiterte Konfiguration

### Anpassung der Trigger:
```yaml
# Temperatur-Blueprint
- Überprüfung alle 30 Minuten
- Bei Temperaturänderung (5min Verzögerung)
- Bei Solar-Änderung (2min Verzögerung)

# pH-Blueprint  
- Überprüfung alle 15 Minuten
- Bei pH-Änderung (10min Verzögerung)
- Bei Pumpen-Start (5min Verzögerung)
```

### Sicherheitsfeatures:
- ✅ **Tägliche Dosier-Limits**
- ✅ **Mindest-Wartezeiten**
- ✅ **Pumpen-Abhängigkeit**
- ✅ **Sensor-Verfügbarkeits-Check**
- ✅ **Automatischer Counter-Reset**

## 🚨 Troubleshooting

### Häufige Probleme:

**Blueprint nicht sichtbar:**
```bash
# Home Assistant Logs prüfen:
tail -f config/home-assistant.log | grep blueprint

#
