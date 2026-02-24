# Sensoren & Messwerte

> Vollständige Dokumentation aller Sensor-Entities – von Wasserchemie bis Systemdiagnose.

---

## Sensor-Übersicht

Die Integration erstellt automatisch Sensor-Entities basierend auf den aktivierten Features und den verfügbaren Daten des Controllers.

### Wasserchemie-Sensoren

| Entity-ID | Name | Einheit | Bereich | Beschreibung |
|-----------|------|---------|---------|--------------|
| `sensor.violet_ph_value` | pH-Wert | – | 6.0–8.0 | Aktueller pH-Wert des Poolwassers |
| `sensor.violet_orp_value` | ORP/Redox | mV | 200–900 | Oxidations-Reduktions-Potential |
| `sensor.violet_chlorine` | Freies Chlor | mg/L | 0.1–3.0 | Freier Chlorgehalt |
| `sensor.violet_conductivity` | Leitfähigkeit | µS/cm | – | Elektrische Leitfähigkeit (Salzgehalt) |

**Optimale Wasserwerte:**

```
┌────────────────────────────────────────────────────────┐
│                  IDEALE POOL-WASSERWERTE                │
├─────────────────┬──────────┬──────────┬────────────────┤
│ Parameter       │ Minimum  │ Optimal  │ Maximum        │
├─────────────────┼──────────┼──────────┼────────────────┤
│ pH              │ 7.0      │ 7.2–7.4  │ 7.6            │
│ ORP/Redox       │ 600 mV   │ 650–750  │ 800 mV         │
│ Freies Chlor    │ 0.2 mg/L │ 0.5–1.0  │ 2.0 mg/L       │
│ Leitfähigkeit   │ –        │ Boden-   │ –              │
│                 │          │ abhängig │                │
└─────────────────┴──────────┴──────────┴────────────────┘
```

### Temperatur-Sensoren

| Entity-ID | Name | Einheit | Beschreibung |
|-----------|------|---------|--------------|
| `sensor.violet_water_temperature` | Wassertemperatur | °C | Pool-Wassertemperatur |
| `sensor.violet_solar_temperature` | Solar-Temperatur | °C | Temperatur des Solarkollektors |
| `sensor.violet_ambient_temperature` | Außentemperatur | °C | Umgebungstemperatur |
| `sensor.violet_heater_temperature` | Heizer-Temperatur | °C | Wärmetauscher-Temperatur |

### Analoge Eingänge (AI1–AI8)

| Entity-ID | Beschreibung |
|-----------|--------------|
| `sensor.violet_ai1` | Analogeingang 1 (konfigurierbar) |
| `sensor.violet_ai2` | Analogeingang 2 (konfigurierbar) |
| ... | ... |
| `sensor.violet_ai8` | Analogeingang 8 (konfigurierbar) |

Analoge Eingänge können für externe Sensoren verwendet werden (Drucksensor, Durchflussmesser, etc.). Die Einheit hängt vom angeschlossenen Sensor ab.

---

## System-Sensoren

### Diagnose & Status

| Entity-ID | Name | Typ | Beschreibung |
|-----------|------|-----|--------------|
| `sensor.violet_system_error_codes` | Fehler-Codes | String | Aktuelle Fehlercodes (leer = kein Fehler) |
| `sensor.violet_pump_runtime` | Pumpen-Laufzeit | h | Gesamte Betriebsstunden der Pumpe |
| `sensor.violet_filter_runtime` | Filter-Laufzeit | h | Betriebsstunden seit letzter Rückspülung |
| `sensor.violet_last_calibration` | Letzte Kalibrierung | Datum | Datum der letzten Sensor-Kalibrierung |
| `sensor.violet_firmware_version` | Firmware-Version | String | Controller-Firmware-Version |

### Kalibrierungshistorie

Die Integration parst automatisch die Kalibrierungshistorie vom Controller:

| Entity-ID | Beschreibung |
|-----------|--------------|
| `sensor.violet_ph_calibration_date` | Letztes pH-Kalibrierungsdatum |
| `sensor.violet_orp_calibration_date` | Letztes ORP-Kalibrierungsdatum |
| `sensor.violet_chlorine_calibration_date` | Letztes Chlor-Kalibrierungsdatum |

---

## Sensor-Kalibrierung

### Kalibrierungsintervalle

| Sensor | Empfohlenes Intervall | Methode |
|--------|----------------------|---------|
| **pH** | Monatlich | Pufferlösung pH 7.0 & pH 4.0 |
| **ORP/Redox** | Mit pH-Kalibrierung | ORP-Referenzlösung |
| **Freies Chlor** | Wöchentlich prüfen | Fotometer/Teststreifen |
| **Temperaturen** | Jährlich | Referenzthermometer |

### Kalibrierung fehlerhafter Werte erkennen

```yaml
# Automatisierung: Benachrichtigung wenn pH außer Bereich
automation:
  - alias: "pH-Warnung"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        above: 7.6
        for:
          minutes: 15
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        below: 7.0
        for:
          minutes: 15
    action:
      - service: notify.mobile_app
        data:
          title: "Pool-Warnung"
          message: "pH-Wert außer Bereich: {{ states('sensor.violet_ph_value') }}"
```

---

## Sensor-Attribute

Jeder Sensor enthält zusätzliche Attribute:

```yaml
# Beispiel: sensor.violet_ph_value Attribute
state: "7.3"
attributes:
  unit_of_measurement: ""
  device_class: null
  friendly_name: "pH-Wert"
  last_update: "2026-02-22T10:30:00+00:00"
  controller_ip: "192.168.1.100"
  raw_value: 7.3
```

---

## Sensoren in Automatisierungen

### Wasserchemie überwachen

```yaml
# Vollständige Wasserchemie-Überwachung
automation:
  - alias: "Pool Wasserchemie Monitor"
    trigger:
      # pH zu niedrig
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        below: 7.0
        id: ph_low
      # pH zu hoch
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        above: 7.6
        id: ph_high
      # Chlor zu niedrig
      - platform: numeric_state
        entity_id: sensor.violet_chlorine
        below: 0.3
        id: chlorine_low
      # ORP zu niedrig
      - platform: numeric_state
        entity_id: sensor.violet_orp_value
        below: 600
        id: orp_low
    action:
      - service: notify.mobile_app
        data:
          title: "Pool-Alarm"
          message: >
            {% if trigger.id == 'ph_low' %}
              pH zu niedrig: {{ states('sensor.violet_ph_value') }} (Soll: 7.0–7.4)
            {% elif trigger.id == 'ph_high' %}
              pH zu hoch: {{ states('sensor.violet_ph_value') }} (Soll: 7.0–7.4)
            {% elif trigger.id == 'chlorine_low' %}
              Chlor zu niedrig: {{ states('sensor.violet_chlorine') }} mg/L
            {% elif trigger.id == 'orp_low' %}
              ORP zu niedrig: {{ states('sensor.violet_orp_value') }} mV
            {% endif %}
```

### Temperatur-basierte Heizungssteuerung

```yaml
automation:
  - alias: "Pool Heizung bei Temperaturabfall"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_water_temperature
        below: 26.0
    condition:
      - condition: time
        after: "08:00:00"
        before: "20:00:00"
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.violet_heater
        data:
          hvac_mode: heat
```

### Solar-Steuerung nach Temperaturdifferenz

```yaml
automation:
  - alias: "Solar starten wenn Kollektor wärmer als Pool"
    trigger:
      - platform: template
        value_template: >
          {{
            (states('sensor.violet_solar_temperature') | float) -
            (states('sensor.violet_water_temperature') | float) > 5
          }}
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_solar
```

---

## Template-Sensoren

Du kannst eigene Template-Sensoren erstellen, um Daten zu kombinieren:

```yaml
# configuration.yaml oder templates.yaml
template:
  - sensor:
      - name: "Pool Hygienestatus"
        state: >
          {% set ph = states('sensor.violet_ph_value') | float(0) %}
          {% set chlor = states('sensor.violet_chlorine') | float(0) %}
          {% set orp = states('sensor.violet_orp_value') | float(0) %}
          {% if 7.0 <= ph <= 7.4 and chlor >= 0.3 and orp >= 650 %}
            Optimal
          {% elif 6.8 <= ph <= 7.6 and chlor >= 0.2 %}
            Akzeptabel
          {% else %}
            Handlungsbedarf
          {% endif %}
        icon: >
          {% if this.state == 'Optimal' %}mdi:check-circle
          {% elif this.state == 'Akzeptabel' %}mdi:alert-circle
          {% else %}mdi:alert{% endif %}

      - name: "Pool Temperaturdifferenz Solar"
        unit_of_measurement: "°C"
        state: >
          {{ (states('sensor.violet_solar_temperature') | float(0)) -
             (states('sensor.violet_water_temperature') | float(0)) | round(1) }}
```

---

## Sensor-Probleme beheben

| Problem | Mögliche Ursache | Lösung |
|---------|-----------------|--------|
| Sensor zeigt `unavailable` | Controller nicht erreichbar | Verbindung prüfen |
| Sensor zeigt `unknown` | Sensor am Controller nicht vorhanden/aktiviert | Feature im Setup aktivieren |
| Falscher Wert | Sensor nicht kalibriert | Kalibrierung durchführen |
| Wert springt unkontrolliert | Sensor verschmutzt | Sensor reinigen |
| Negativer Wert | Sensor-Kabel defekt | Kabel/Sensor prüfen |

---

**Weiter:** [Schalter & Steuerung](Switches) | [Klima & Heizung](Climate) | [Services](Services)
