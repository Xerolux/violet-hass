# 🛠️ Helper Setup Guide für Pool Blueprints

## 📋 Übersicht
Die Blueprints benötigen spezielle **Helper-Entities** um Zähler und Zeitstempel zu speichern. Diese müssen **vor** der Blueprint-Nutzung erstellt werden.

## 🧪 Helper für pH-Kontrolle

### `input_number.pool_ph_dosing_counter`
**Zweck:** Zählt die täglichen pH-Dosierungen zur Sicherheit

#### Schritt-für-Schritt Erstellung:

1. **Helper-Menü öffnen:**
   ```
   Settings → Devices & Services → Helpers → Create Helper
   ```

2. **"Number" auswählen**

3. **Konfiguration eingeben:**
   ```yaml
   Name: Pool pH Dosing Counter
   Entity ID: input_number.pool_ph_dosing_counter
   Icon: mdi:counter
   Minimum value: 0
   Maximum value: 50
   Step: 1
   Initial value: 0
   Unit of measurement: Dosierungen
   Display mode: Box
   ```

4. **"Create" klicken**

### Verwendung im Blueprint:
- Zählt jede pH+ und pH- Dosierung
- Verhindert mehr als X Dosierungen pro Tag (Sicherheit)
- Reset um Mitternacht automatisch auf 0

---

## 🔄 Helper für Rückspül-Kontrolle

### `input_datetime.pool_last_backwash`
**Zweck:** Speichert Zeitpunkt der letzten Rückspülung

#### Schritt-für-Schritt Erstellung:

1. **Helper-Menü öffnen:**
   ```
   Settings → Devices & Services → Helpers → Create Helper
   ```

2. **"Date and/or time" auswählen**

3. **Konfiguration eingeben:**
   ```yaml
   Name: Pool Last Backwash
   Entity ID: input_datetime.pool_last_backwash
   Icon: mdi:calendar-clock
   Has date: ✓ (aktiviert)
   Has time: ✓ (aktiviert)
   ```

4. **"Create" klicken**

### `input_number.pool_pump_runtime_hours` (Optional)
**Zweck:** Zählt Pumpenlaufzeit für laufzeitbasierte Rückspülung

#### Schritt-für-Schritt Erstellung:

1. **"Number" Helper erstellen**

2. **Konfiguration eingeben:**
   ```yaml
   Name: Pool Pump Runtime Hours
   Entity ID: input_number.pool_pump_runtime_hours
   Icon: mdi:pump
   Minimum value: 0
   Maximum value: 500
   Step: 0.1
   Initial value: 0
   Unit of measurement: h
   Display mode: Box
   ```

### Verwendung im Blueprint:
- **Last Backwash:** Berechnet Tage seit letzter Rückspülung
- **Runtime Hours:** Triggert Rückspülung nach X Stunden Pumpenlauf
- Wird automatisch nach Rückspülung zurückgesetzt

---

## 📱 Alle Helper auf einen Blick

### Schnell-Erstellung via YAML (Advanced)

Für erfahrene Nutzer - diese Konfiguration in `configuration.yaml` einfügen:

{% raw %}
```yaml
# Pool Helper Entities
input_number:
  pool_ph_dosing_counter:
    name: "Pool pH Dosing Counter"
    min: 0
    max: 50
    step: 1
    initial: 0
    unit_of_measurement: "Dosierungen"
    icon: mdi:counter

  pool_pump_runtime_hours:
    name: "Pool Pump Runtime Hours"
    min: 0
    max: 500
    step: 0.1
    initial: 0
    unit_of_measurement: "h"
    icon: mdi:pump

input_datetime:
  pool_last_backwash:
    name: "Pool Last Backwash"
    has_date: true
    has_time: true
    icon: mdi:calendar-clock
```
{% endraw %}

Nach dem Hinzufügen: **Home Assistant neustarten**

---

## 🎛️ Helper im Dashboard anzeigen (Optional)

### Lovelace Card für Pool Status:

```yaml
type: entities
title: Pool Automatisierung
entities:
  - entity: input_number.pool_ph_dosing_counter
    name: pH-Dosierungen heute
  - entity: input_datetime.pool_last_backwash
    name: Letzte Rückspülung
  - entity: input_number.pool_pump_runtime_hours
    name: Pumpenlaufzeit
show_header_toggle: false
```

---

## ⚙️ Erweiterte Automatisierungen (Optional)

### Automatischer Runtime Counter:

Wenn du die Pumpenlaufzeit automatisch zählen möchtest:

{% raw %}
```yaml
# Automation für Pump Runtime Counter
automation:
  - alias: "Pool Pump Runtime Counter"
    trigger:
      - platform: state
        entity_id: switch.violet_pump
        to: 'off'
        for:
          minutes: 1
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: 'off'
    action:
      - service: input_number.set_value
        target:
          entity_id: input_number.pool_pump_runtime_hours
        data:
          value: >
            {% set runtime = states('input_number.pool_pump_runtime_hours') | float %}
            {% set last_on = states.switch.violet_pump.last_changed %}
            {% set duration = (now() - last_on).total_seconds() / 3600 %}
            {{ runtime + duration }}
```
{% endraw %}

### Täglicher Reset der pH-Dosierungen:

```yaml
# Automation für täglichen Reset
automation:
  - alias: "Reset pH Dosing Counter Daily"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: input_number.set_value
        target:
          entity_id: input_number.pool_ph_dosing_counter
        data:
          value: 0
```

---

## 🚨 Troubleshooting

### Helper nicht sichtbar:
```bash
# Developer Tools → States → Suchen nach:
input_number.pool_ph_dosing_counter
input_datetime.pool_last_backwash
input_number.pool_pump_runtime_hours
```

### Blueprint-Fehler wegen fehlenden Helpers:
```
Template error: input_number.pool_ph_dosing_counter not found
```
**Lösung:** Helper wie oben beschrieben erstellen

### Helper zurücksetzen:
```yaml
# Via Developer Tools → Services
service: input_number.set_value
target:
  entity_id: input_number.pool_ph_dosing_counter
data:
  value: 0
```

### YAML-Methode funktioniert nicht:
- Helper über UI erstellen (einfacher)
- Nach YAML-Änderungen HA neustarten
- Syntax-Fehler in configuration.yaml prüfen

---

## 💡 Warum sind Helper notwendig?

### Datenpersistenz:
- **Ohne Helper:** Daten gehen bei HA-Neustart verloren
- **Mit Helper:** Werte bleiben dauerhaft gespeichert

### Sicherheit:
- **pH-Counter:** Verhindert Überdosierung
- **Last Backwash:** Verhindert zu häufige Rückspülung

### Intelligenz:
- **Runtime Counter:** Ermöglicht laufzeitbasierte Automatisierung
- **Timestamp:** Berechnung von Intervallen

Die Helper sind essentiell für sichere und intelligente Pool-Automatisierung! 🏊‍♂️
