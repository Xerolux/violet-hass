# Schalter & Steuerung – Switch-Entities

> Vollständige Dokumentation aller Switch-Entities des Violet Pool Controllers.

---

## Überblick

Alle Schalter des Violet Pool Controllers sind **3-State Switches**: Sie kennen nicht nur `Ein` und `Aus`, sondern auch `Automatik`. Der tatsächliche Betriebszustand wird als **State 0–6** gespeichert.

| Zustand (State) | Bedeutung | Switch-Anzeige |
|-----------------|-----------|----------------|
| `0` – AUTO_OFF | Automatik, gerade aus | `off` |
| `1` – MANUAL_ON | Manuell eingeschaltet | `on` |
| `2` – AUTO_ON | Automatik, gerade an | `on` |
| `3` – AUTO_TIMER | Automatik mit Timer, an | `on` |
| `4` – FORCED_ON | Erzwungen an | `on` |
| `5` – AUTO_WAITING | Automatik, wartet auf Bedingung | `off` |
| `6` – MANUAL_OFF | Manuell ausgeschaltet | `off` |

> Detaillierte State-Erklärung: [Device States](Device-States)

---

## Alle Switch-Entities

### Pumpe

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_pump` | Hauptfilterpumpe (3 Geschwindigkeitsstufen) |

**Besonderheit:** Die Pumpe unterstützt 4 Geschwindigkeitsstufen (0–3). Für Geschwindigkeitssteuerung nutze den [Service `control_pump`](Services#-service-control_pump).

```yaml
# Einfaches Ein/Aus
service: switch.turn_on
target:
  entity_id: switch.violet_pump

# Geschwindigkeit mit Service
service: violet_pool_controller.control_pump
data:
  action: speed_control
  speed: 2
  duration: 3600
```

---

### Heizung

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_heater` | Pool-Heizung |

> Für Thermostat-Steuerung mit Solltemperatur: [Climate Entities](Climate)

```yaml
service: switch.turn_on
target:
  entity_id: switch.violet_heater
```

---

### Solar

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_solar` | Solarkollektor |

```yaml
# Nur einschalten wenn Solartemperatur > Beckenwasser
automation:
  trigger:
    platform: template
    value_template: >
      {{ states('sensor.violet_solar_temperature') | float(0) >
         states('sensor.violet_water_temperature') | float(0) + 3 }}
  action:
    service: switch.turn_on
    target:
      entity_id: switch.violet_solar
```

---

### Dosier-Pumpen

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_ph_minus` | pH-Senker Dosierpumpe |
| `switch.violet_ph_plus` | pH-Heber Dosierpumpe |
| `switch.violet_chlorine` | Chlor-Dosierpumpe |
| `switch.violet_flocculant` | Flockmittel-Dosierpumpe |

> **Sicherheitshinweis:** Dosier-Pumpen direkt über Switch zu steuern ist möglich, aber für präzise Dosierung nutze den [Service `smart_dosing`](Services#-service-smart_dosing).

```yaml
# Empfohlen: Service mit Zeitsteuerung
service: violet_pool_controller.smart_dosing
data:
  dosing_type: "pH-"
  action: manual_dose
  duration: 30
```

---

### DMX-Beleuchtung

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_dmx_scene_1` | DMX Szene 1 |
| `switch.violet_dmx_scene_2` | DMX Szene 2 |
| `switch.violet_dmx_scene_3` | DMX Szene 3 |
| `switch.violet_dmx_scene_4` | DMX Szene 4 |
| `switch.violet_dmx_scene_5` | DMX Szene 5 |
| `switch.violet_dmx_scene_6` | DMX Szene 6 |
| `switch.violet_dmx_scene_7` | DMX Szene 7 |
| `switch.violet_dmx_scene_8` | DMX Szene 8 |

```yaml
# Beleuchtung bei Sonnenuntergang einschalten
automation:
  - alias: "Pool Beleuchtung Sonnenuntergang"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_dmx_scene_1
```

---

### Erweiterungs-Relais

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_relay_1` bis `switch.violet_relay_8` | Frei konfigurierbare Relais |

Erweiterungs-Relais können für beliebige Geräte genutzt werden:
- Wasserfall-Pumpe
- Gegenstromanlage
- Luftbläser
- Beleuchtung (nicht-DMX)

```yaml
# Wasserfall nur wenn Pumpe läuft
automation:
  - alias: "Wasserfall mit Pumpe"
    trigger:
      - platform: state
        entity_id: switch.violet_pump
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_relay_1
```

---

## Switch-Steuerung via UI

### 3-State Toggle

In der Home Assistant UI zeigt jeder Switch:
- **Grün (ON)**: Gerät aktiv (States 1, 2, 3, 4)
- **Grau (OFF)**: Gerät inaktiv (States 0, 5, 6)

Klicken schaltet zwischen manuell-EIN und Automatik um.

### State-Details anzeigen

Klicke auf die Entity → **Attribute** zum Anzeigen:
- `raw_state`: Der numerische State 0–6
- `mode`: Aktueller Betriebsmodus
- `last_changed`: Letzter Zustandswechsel

---

## Automatisierung: Nützliche Patterns

### Tages-Zeitplan für Pumpe

```yaml
automation:
  - alias: "Pumpe Tagesprogramm"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 2

  - alias: "Pumpe Nacht Reduktion"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 1
```

### Switch-State in Template-Sensor auswerten

```yaml
template:
  - sensor:
      - name: "Pumpen-Modus"
        state: >
          {% set state = states('switch.violet_pump') %}
          {% set raw = state_attr('switch.violet_pump', 'raw_state') | int(-1) %}
          {% if raw == 0 %} Automatik aus
          {% elif raw == 1 %} Manuell an
          {% elif raw == 2 %} Automatik an
          {% elif raw == 3 %} Timer aktiv
          {% elif raw == 4 %} Zwang an
          {% elif raw == 5 %} Warten
          {% elif raw == 6 %} Manuell aus
          {% else %} Unbekannt
          {% endif %}
```

### Alle Schalter auf Automatik setzen

```yaml
script:
  alle_automatik:
    alias: "Alle Schalter auf Automatik"
    sequence:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.violet_pump
            - switch.violet_heater
            - switch.violet_solar
            - switch.violet_ph_minus
            - switch.violet_chlorine
```

---

## Composite States (Pipe-Separator)

Manche Switches zeigen zusammengesetzte States:

```
"3|PUMP_ANTI_FREEZE"
"2|SOLAR_DIFF_ACTIVE"
"4|MANUAL_OVERRIDE"
```

Das erste Segment (vor `|`) ist der numerische State (0–6).
Das zweite Segment gibt einen operationellen Modus an.

**In Automatisierungen prüfen:**

```yaml
condition:
  - condition: template
    value_template: >
      {{ 'PUMP_ANTI_FREEZE' in state_attr('switch.violet_pump', 'raw_state') | string }}
```

---

## Troubleshooting

### Switch zeigt immer `unavailable`

1. Controller erreichbar? → [Troubleshooting](Troubleshooting)
2. Feature im Setup aktiviert?
3. Integration neu laden: Einstellungen → Geräte & Dienste → Violet → Neu laden

### Switch reagiert nicht auf Steuerung

1. Prüfe ob Controller im manuellen Override-Modus
2. Prüfe Logs: Einstellungen → System → Protokoll
3. Rate-Limiting aktiv? Kurz warten und erneut versuchen

### Pumpe lässt sich nicht einschalten

Mögliche Ursachen:
- Frostschutz aktiv (`PUMP_ANTI_FREEZE` in State)
- Sicherheitsverriegelung aktiv (Fehlercode prüfen)
- Druckschalter-Fehler (Error Code 20/21)

→ Siehe [Fehler-Codes](Error-Codes) für Details

---

*Zurück: [Home](Home) | Weiter: [Climate & Heizung](Climate)*
