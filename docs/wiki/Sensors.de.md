> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Sensors)**

---

# Sensoren & Messwerte

> Vollständige Dokumentation aller Sensor-Entities – von der Wasserchemie bis zur Systemdiagnose.

> Entity-IDs verwenden den Präfix `violet_pool_controller` (bzw. `violet_pool_controller_<device_id>` bei Multi-Controller). Die folgenden Suffixe werden an diesen Präfix angehängt.

---

## Sensor-Überblick

Die Integration erzeugt Sensor-Entities dynamisch basierend auf den aktivierten Features und den von `/getReadings` gemeldeten Werten. Siehe [Entitäten](Entities.de) für die vollständige Suffix-Liste.

### Wasserchemie-Sensoren

| Suffix | Name | Einheit | Typischer Bereich |
|--------|------|---------|-------------------|
| `pH_value` | pH-Wert | pH | 6.0–8.0 |
| `orp_value` | ORP / Redox | mV | 200–900 |
| `pot_value` | Freies Chlor | mg/l | 0.1–3.0 |

**Optimale Wasserwerte:**

```
┌────────────────────────────────────────────────────────┐
│                IDEALE POOL-WASSERWERTE                  │
├─────────────────┬──────────┬──────────┬────────────────┤
│ Parameter       │ Minimum  │ Optimal  │ Maximum        │
├─────────────────┼──────────┼──────────┼────────────────┤
│ pH              │ 7.0      │ 7.2–7.4  │ 7.6            │
│ ORP/Redox       │ 600 mV   │ 650–750  │ 800 mV         │
│ Freies Chlor    │ 0.2 mg/L │ 0.5–1.0  │ 2.0 mg/L       │
└─────────────────┴──────────┴──────────┴────────────────┘
```

### Temperatur-Sensoren (1-Wire 1–12)

| Suffix | Name | Einheit | Feature |
|--------|------|---------|---------|
| `onewire1_value` | Beckenwasser | °C | immer |
| `onewire2_value` | Außentemperatur | °C | immer |
| `onewire3_value` | Solarkollektor | °C | solar |
| `onewire4_value` | Absorber-Rücklauf | °C | solar |
| `onewire5_value` | Wärmetauscher | °C | heating |
| `onewire6_value` | Heizungs-Speicher | °C | heating |
| `onewire7_value` … `onewire12_value` | Temperatursensor 7–12 | °C | immer |

### Analoge Sensoren

| Suffix | Name | Einheit |
|--------|------|---------|
| `ADC1_value` | Filterdruck | bar |
| `ADC2_value` | Überlaufbehälter | cm |
| `ADC3_value` | Durchflussmesser (4-20 mA) | m³/h |
| `ADC4_value` | Analoger Sensor 4 (4-20 mA) | – |
| `ADC5_value` | Analoger Sensor 5 (0-10 V) | V |
| `IMP1_value` | Dosier-Zulauf | cm/s |
| `IMP2_value` | Pumpen-Durchfluss | m³/h |

Analog-Eingänge können mit externen Sensoren verbunden werden (Druckaufnehmer, Durchflussmesser, Füllstandssonde, …). Die Einheit hängt vom angeschlossenen Sensor ab.

---

## System- & Diagnose-Sensoren

### System-Sensoren

| Suffix | Name | Einheit |
|--------|------|---------|
| `SYSTEM_cpu_temperature` | CPU-Temperatur | °C |
| `SYSTEM_carrier_cpu_temperature` | Carrier-CPU-Temperatur | °C |
| `SYSTEM_dosagemodule_cpu_temperature` | Dosiermodul-CPU-Temperatur | °C |
| `SYSTEM_memoryusage` | Systemspeicher-Auslastung | – |
| `CPU_UPTIME` | Geräte-Laufzeit | – |
| `LOAD_AVG` | CPU-Last-Durchschnitt | – |
| `pump_rs485_pwr` | RS485-Pumpenleistung | W |

### Status-Sensoren

`PUMP`, `HEATER`, `SOLAR`, `BACKWASH`, `BACKWASHRINSE`, `LIGHT`, `REFILL`, `ECO`, `PVSURPLUS`, `FW` – jeweils den lesbaren Status des zugehörigen Ausgangs.

### Composite-State-Sensoren (mit Detail-Codes)

`PUMPSTATE`, `HEATERSTATE`, `SOLARSTATE` tragen den vollen zusammengesetzten Wert wie `"3|PUMP_ANTI_FREEZE"` oder `"2|BLOCKED_BY_OUTSIDE_TEMP"`. Siehe [Gerätezustände](Device-States.de#zusammengesetzte--pipe-getrennte-zustände) für die vollständige Liste der Detail-Codes.

### Dosier-Status-Sensoren

`DOS_1_CL_STATE`, `DOS_2_ELO_STATE`, `DOS_4_PHM_STATE`, `DOS_5_PHP_STATE`, `DOS_6_FLOC_STATE`.

---

## Laufzeiten & Statistik

### Laufzeit-Sensoren pro Ausgang

Jeder Ausgang hat einen `*_RUNTIME`-Sensor mit der heutigen Laufzeit:

- `PUMP_RUNTIME`, `SOLAR_RUNTIME`, `HEATER_RUNTIME`, `LIGHT_RUNTIME`
- `BACKWASH_RUNTIME`, `BACKWASHRINSE_RUNTIME`, `ECO_RUNTIME`, `REFILL_RUNTIME`
- `DOS_1_CL_RUNTIME`, `DOS_2_ELO_RUNTIME`, `DOS_3_ELO_REV_RUNTIME`, `DOS_4_PHM_RUNTIME`, `DOS_5_PHP_RUNTIME`, `DOS_6_FLOC_RUNTIME`
- `EXT1_1_RUNTIME`–`EXT2_8_RUNTIME` (16 Erweiterungsrelais)
- `OMNI_DC0_RUNTIME`–`OMNI_DC5_RUNTIME` (6 OMNI-Motoren)
- `PUMP_RPM_0_RUNTIME`–`PUMP_RPM_3_RUNTIME` (4 RPM-Stufen)

### Dosierstatistik

Für jeden Dosierkanal:

| Suffix | Beschreibung | Einheit |
|--------|--------------|---------|
| `*_DAILY_DOSING_AMOUNT_ML` | Tagesverbrauch | ml |
| `*_TOTAL_CAN_AMOUNT_ML`    | Verbleibende Kanistermenge | ml |

### Pumpen-RPM-Sensoren

| Suffix | Beschreibung | Einheit |
|--------|--------------|---------|
| `PUMP_RPM_0`–`PUMP_RPM_3` | RPM-Stufen-Statuscode (0-6) | – |
| `PUMP_RPM_0_VALUE`–`PUMP_RPM_3_VALUE` | Gemessene Drehzahl | RPM |

### Digitalregel-Stoppuhr

`DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH1..8` – verbleibende Timer (Sekunden) für jede Schaltregel.

---

## Sensorkalibrierung

### Empfohlene Kalibrierintervalle

| Sensor | Intervall | Methode |
|--------|-----------|---------|
| **pH** | Monatlich | Pufferlösung pH 7.0 & pH 4.0 |
| **ORP/Redox** | Zusammen mit pH | ORP-Referenzlösung |
| **Freies Chlor** | Wöchentlich prüfen | Photometer / Teststreifen |
| **Temperaturen** | Jährlich | Referenzthermometer |

### Kalibrierung per Service

Die Integration stellt `configure_sensor_calibration` bereit (Sensor-ID 1–12, Offset, Multiplikator, min/max). Siehe [Services](Services.de#-service-configure_sensor_calibration).

### Kalibrierungsdrift erkennen

```yaml
automation:
  - alias: "pH-Warnung"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        above: 7.6
        for: "00:15:00"
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        below: 7.0
        for: "00:15:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Pool-Warnung"
          message: "pH außerhalb des Bereichs: {{ states('sensor.violet_pool_controller_ph_value') }}"
```

---

## Sensoren in Automatisierungen

### Komplette Wasserchemie-Überwachung

```yaml
automation:
  - alias: "Pool-Wasserchemie-Monitor"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        below: 7.0
        id: ph_low
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        above: 7.6
        id: ph_high
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_pot_value
        below: 0.3
        id: chlorine_low
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_orp_value
        below: 600
        id: orp_low
    action:
      - service: notify.mobile_app
        data:
          title: "Pool-Alarm"
          message: >
            {% if trigger.id == 'ph_low' %}pH zu niedrig: {{ states('sensor.violet_pool_controller_ph_value') }}
            {% elif trigger.id == 'ph_high' %}pH zu hoch: {{ states('sensor.violet_pool_controller_ph_value') }}
            {% elif trigger.id == 'chlorine_low' %}Chlor zu niedrig: {{ states('sensor.violet_pool_controller_pot_value') }} mg/l
            {% elif trigger.id == 'orp_low' %}ORP zu niedrig: {{ states('sensor.violet_pool_controller_orp_value') }} mV
            {% endif %}
```

### Solarsteuerung nach Temperaturdifferenz

```yaml
automation:
  - alias: "Solar starten, wenn Kollektor wärmer als Becken"
    trigger:
      - platform: template
        value_template: >
          {{ (states('sensor.violet_pool_controller_onewire3_value') | float(0)) -
             (states('sensor.violet_pool_controller_onewire1_value') | float(0)) > 5 }}
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_pool_controller_solar
```

---

## Template-Sensoren

```yaml
template:
  - sensor:
      - name: "Pool-Hygienestatus"
        state: >
          {% set ph = states('sensor.violet_pool_controller_ph_value') | float(0) %}
          {% set chlor = states('sensor.violet_pool_controller_pot_value') | float(0) %}
          {% set orp = states('sensor.violet_pool_controller_orp_value') | float(0) %}
          {% if 7.0 <= ph <= 7.4 and chlor >= 0.3 and orp >= 650 %}Optimal
          {% elif 6.8 <= ph <= 7.6 and chlor >= 0.2 %}Akzeptabel
          {% else %}Handeln erforderlich{% endif %}
        icon: >
          {% if this.state == 'Optimal' %}mdi:check-circle
          {% elif this.state == 'Akzeptabel' %}mdi:alert-circle
          {% else %}mdi:alert{% endif %}

      - name: "Pool Temperaturdifferenz Solar"
        unit_of_measurement: "°C"
        state: >
          {{ ((states('sensor.violet_pool_controller_onewire3_value') | float(0)) -
              (states('sensor.violet_pool_controller_onewire1_value') | float(0))) | round(1) }}
```

---

## Sensorprobleme beheben

| Problem | Mögliche Ursache | Lösung |
|---------|------------------|--------|
| Sensor zeigt `unavailable` | Controller nicht erreichbar | Verbindung prüfen |
| Sensor zeigt `unknown` | Sensor nicht vorhanden / Feature deaktiviert | Feature im Setup aktivieren |
| Falscher Wert | Sensor nicht kalibriert | Kalibrierung durchführen |
| Wert schwankt | Sensor verschmutzt / Messrauschen | Sensor reinigen, Hysterese erhöhen |
| Negativer Wert | Sensorkabel defekt | Kabel/Sensor prüfen |
| `DOS_2_ELO_*` fehlt | Kein Elektrolyse-Modul verbaut | Hardware prüfen |

---

**Weiter:** [Schalter & Steuerung](Switches.de) | [Klima & Heizung](Climate.de) | [Services](Services.de)
