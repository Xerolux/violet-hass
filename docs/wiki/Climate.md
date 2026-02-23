# Klima & Heizung – Climate Entities

> Thermostat-Steuerung für Pool-Heizung und Solaranlage.

---

## Überblick

Die Climate-Entities bieten eine vollwertige Thermostat-Schnittstelle für:
- **Pool-Heizung** (Wärmepumpe, Gas, Elektrisch)
- **Solar-Heizung** (Solarkollektor mit Differenzregelung)

---

## Climate Entities

| Entity | Beschreibung | Standard-Sollwert |
|--------|-------------|-------------------|
| `climate.violet_heater` | Pool-Hauptheizung | 28°C |
| `climate.violet_solar` | Solar-Heizkreis | 30°C |

---

## HVAC-Modi

Jede Climate-Entity unterstützt drei Modi:

| Modus | Beschreibung | Wann nutzen? |
|-------|-------------|--------------|
| `off` | Heizung komplett aus | Nicht-Badesaison |
| `heat` | Auf Solltemperatur heizen | Aktive Nutzung |
| `auto` | Controller regelt automatisch | Normalfall |

---

## Solltemperatur einstellen

### Via Home Assistant UI

Klicke auf die Climate-Entity → Temperatur-Regler verwenden.

### Via Service

```yaml
service: climate.set_temperature
target:
  entity_id: climate.violet_heater
data:
  temperature: 28
  hvac_mode: heat
```

### Via Number-Entity (Alternative)

```yaml
service: number.set_value
target:
  entity_id: number.violet_target_pool_temperature
data:
  value: 28
```

---

## Verfügbare Number-Entities für Sollwerte

| Entity | Beschreibung | Bereich |
|--------|-------------|---------|
| `number.violet_target_pool_temperature` | Pool-Solltemperatur | 10–40°C |
| `number.violet_target_solar_temperature` | Solar-Maximaltemperatur | 20–60°C |
| `number.violet_target_ph` | pH-Sollwert | 6.0–8.0 |
| `number.violet_target_orp` | ORP-Sollwert | 200–900 mV |

---

## Automatisierungen

### Temperatur nach Wochentag anpassen

```yaml
automation:
  - alias: "Wochenend-Pool aufheizen"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: time
        weekday:
          - sat
          - sun
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 30
          hvac_mode: heat

  - alias: "Wochentag Pool Eco-Modus"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 26
          hvac_mode: auto
```

### Heizung bei Schlechtwetter deaktivieren

```yaml
automation:
  - alias: "Heizung bei Regen aus"
    trigger:
      - platform: state
        entity_id: weather.home
        to: "rainy"
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.violet_heater
        data:
          hvac_mode: "off"
```

### Solar-Überschuss für Heizung nutzen

```yaml
automation:
  - alias: "PV-Überschuss für Pool nutzen"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_export_power
        above: 2000
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.violet_heater
        data:
          hvac_mode: heat
      - service: violet_pool_controller.manage_pv_surplus
        data:
          mode: activate
          pump_speed: 2
```

### Temperatur-Ziel basierend auf Wetter

```yaml
automation:
  - alias: "Soll-Temperatur an Außentemperatur anpassen"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outside_temperature
        above: 25
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 28

  - alias: "Kühle Tage: Temperatur erhöhen"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outside_temperature
        below: 18
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 30
```

---

## Solar-Differenzregelung

Die Solar-Heizung arbeitet mit einer **Differenzregelung**:

```
Solar einschalten wenn:
  T_Solar > T_Pool + Differenz (z.B. 5°C)

Solar ausschalten wenn:
  T_Solar < T_Pool + Hysterese (z.B. 2°C)
```

Die Solar-Climate-Entity zeigt die aktuelle Solar-Maximaltemperatur als Sollwert.

**Template-Sensor für Solar-Differenz:**

```yaml
template:
  - sensor:
      - name: "Solar-Pool Temperaturdifferenz"
        unit_of_measurement: "°C"
        state: >
          {{ (states('sensor.violet_solar_temperature') | float(0) -
              states('sensor.violet_water_temperature') | float(0)) | round(1) }}
```

---

## PV-Surplus Integration

Kombiniere Solar-Anlage mit Pool-Heizung:

```yaml
automation:
  - alias: "Optimale PV-Nutzung"
    trigger:
      - platform: time_pattern
        minutes: "/15"
    condition:
      - condition: template
        value_template: >
          {{ states('sensor.solar_production_power') | float(0) > 1500 }}
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ states('sensor.violet_water_temperature') | float(0) < 30 }}
            sequence:
              - service: climate.set_temperature
                target:
                  entity_id: climate.violet_heater
                data:
                  temperature: 30
                  hvac_mode: heat
          - conditions:
              - condition: template
                value_template: >
                  {{ states('sensor.violet_water_temperature') | float(0) >= 30 }}
            sequence:
              - service: climate.set_hvac_mode
                target:
                  entity_id: climate.violet_heater
                data:
                  hvac_mode: "off"
```

---

## Dashboard-Karte

```yaml
# Thermostat-Karte für Pool-Heizung
type: thermostat
entity: climate.violet_heater
name: Pool Heizung

# Kombinierte Karte mit Temperaturen
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.violet_heater
  - type: entities
    title: Temperaturen
    entities:
      - sensor.violet_water_temperature
      - sensor.violet_solar_temperature
      - entity: sensor.outside_temperature
        name: Außentemperatur
```

---

## Attribute der Climate-Entity

| Attribut | Beschreibung |
|----------|-------------|
| `current_temperature` | Aktuelle Wassertemperatur |
| `target_temperature` | Eingestellte Solltemperatur |
| `hvac_mode` | Aktueller Modus (off/heat/auto) |
| `hvac_action` | Aktuelle Aktion (idle/heating) |
| `min_temp` | Minimale Solltemperatur |
| `max_temp` | Maximale Solltemperatur |

---

## Troubleshooting

### Climate zeigt falsche Temperatur

Die Current Temperature der Climate-Entity wird vom Wassertemperatur-Sensor bezogen. Prüfe `sensor.violet_water_temperature`.

### Heizung schaltet nicht ein

1. HVAC-Mode prüfen (muss `heat` sein)
2. Aktuelle Temperatur < Solltemperatur?
3. Heizungs-Switch (`switch.violet_heater`) prüfen
4. Fehler-Codes checken → [Error-Codes](Error-Codes)

### Solltemperatur wird nicht übernommen

1. Kurz warten (nächster Polling-Zyklus)
2. Integration neu laden
3. Logs prüfen auf API-Fehler

---

*Zurück: [Schalter](Switches) | Weiter: [Services](Services)*
