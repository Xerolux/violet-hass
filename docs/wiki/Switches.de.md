> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Switches)**

---

# Schalter & Steuerung – Switch-Entities

> Vollständige Dokumentation aller Switch-Entities des Violet Pool Controllers.

> **Die Entity-IDs in dieser Wiki sind Beispiele.** Eine Entity-ID leitet sich
> aus dem Namen ab, den du dem Controller im Config-Flow gegeben hast: ein
> Controller namens „Pool" erzeugt `switch.pool_pump`, nicht
> `switch.violet_pool_controller_pump`. Home Assistant schreibt eine ID nach
> der ersten Registrierung außerdem nie um, ältere Installationen tragen also
> möglicherweise noch anders geschriebene IDs. **Sieh deine eigenen in
> Entwicklerwerkzeuge → Zustände nach**, bevor du eine Automatisierung
> kopierst.
>
> Auch die hier gezeigten Wertebereiche und Options-Bezeichnungen sind die
> aktuellen Standardwerte, keine Zusage. Maßgeblich sind der Code
> (`temperature_range()` in `climate.py`, `const_sensors.py`, `select.py`) und
> die Attribute der Entität in den Entwicklerwerkzeugen.

---

## Überblick

Alle Schalter des Violet Pool Controllers sind **3-State Switches**: Sie kennen nicht nur `Ein` und `Aus`, sondern auch `Automatik`. Der tatsächliche Betriebszustand wird als **State 0–6** gespeichert (siehe [Gerätezustände](Device-States.de) für die vollständige Referenz).

| State | Konstante       | Switch-Anzeige | Beschreibung |
|-------|-----------------|----------------|--------------|
| `0`   | `AUTO_OFF`      | `off`          | Automatik, Standby |
| `1`   | `AUTO_ON`       | `on`           | Automatik, Zeitplan / läuft |
| `2`   | `AUTO_PRIO_OFF` | `off`          | Automatik, durch Regel blockiert |
| `3`   | `AUTO_PRIO_ON`  | `on`           | Automatik, durch Notfallregel erzwungen |
| `4`   | `MANUAL_ON`     | `on`           | Manuell AN (erzwungen) |
| `5`   | `EMERGENCY_OFF` | `off`          | Durch Notfall-Regel abgeschaltet |
| `6`   | `MANUAL_OFF`    | `off`          | Manuell AUS |

> ⚠️ **Ältere Wiki-Versionen hatten diese States falsch zugeordnet**. Die obige Tabelle ist die einzig korrekte und wird durch das `OutputState`-Enum im `violet_poolcontroller_api`-Paket (`const_devices.py`) erzwungen.

---

## Alle Switch-Entities

### Pumpe

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_pool_controller_pump` | Hauptfilterpumpe (3 Geschwindigkeitsstufen) |

**Besonderheit:** Die Pumpe unterstützt 4 Geschwindigkeitsstufen (0–3). Für Geschwindigkeitssteuerung nutze den [Service `control_pump`](Services#-service-control_pump).

```yaml
# Einfaches Ein/Aus
service: switch.turn_on
target:
  entity_id: switch.violet_pool_controller_pump

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
| `switch.violet_pool_controller_heater` | Pool-Heizung |

> Für Thermostat-Steuerung mit Solltemperatur: [Climate Entities](Climate)

```yaml
service: switch.turn_on
target:
  entity_id: switch.violet_pool_controller_heater
```

---

### Solar

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_pool_controller_solar` | Solarkollektor |

```yaml
# Nur einschalten wenn Solartemperatur > Beckenwasser
automation:
  trigger:
    platform: template
    value_template: >
      {{ states('sensor.violet_pool_controller_solar_temperature') | float(0) >
         states('sensor.violet_pool_controller_pool_temperature') | float(0) + 3 }}
  action:
    service: switch.turn_on
    target:
      entity_id: switch.violet_pool_controller_solar
```

---

### Dosier-Pumpen

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_pool_controller_dos_4_phm` | pH-Senker-Dosierpumpe |
| `switch.violet_pool_controller_dos_5_php` | pH-Heber-Dosierpumpe |
| `switch.violet_pool_controller_dos_1_cl` | Chlor-Dosierpumpe |
| `switch.violet_pool_controller_dos_2_elo` | Elektrolyse-Dosierung |
| `switch.violet_pool_controller_dos_6_floc` | Flockmittel-Dosierpumpe |

> **Sicherheitshinweis:** Dosier-Pumpen direkt über Switch zu steuern ist möglich, aber für präzise Dosierung nutze den [Service `smart_dosing`](Services.de#-service-smart_dosing) oder [`manual_dosing_http`](Services.de#-service-manual_dosing_http). Dosier-Ausgänge verwenden `POST /triggerManualDosing`, nicht `/setFunctionManually`.

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

Die DMX-Szenen 1–12 werden als **Light-Entities** (nicht als Switches) bereitgestellt:

| Entity | Beschreibung |
|--------|-------------|
| `light.violet_pool_controller_dmx_scene1` … `light.violet_pool_controller_dmx_scene12` | DMX-Szene 1–12 |

Steuerung über die Standard-Light-Domain:

```yaml
# Beleuchtung bei Sonnenuntergang einschalten
automation:
  - alias: "Pool Beleuchtung Sonnenuntergang"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.violet_pool_controller_dmx_scene1
```

Für koordinierte Szenensteuerung nutze den [Service `control_dmx_scenes`](Services.de#-service-control_dmx_scenes) (all_on / all_off / all_auto / sequence / party_mode).

### Weitere Kern-Switches

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_pool_controller_pvsurplus` | PV-Überschuss-Ausgang (verwendet 0–2-Schema, siehe [Gerätezustände](Device-States.de#pvsurplus-ausnahme)) |
| `switch.violet_pool_controller_backwash` | Rückspülzyklus |
| `switch.violet_pool_controller_backwashrinse` | Spülzyklus |
| `switch.violet_pool_controller_refill` | Wassernachspeisung |
| `switch.violet_pool_controller_eco` | ECO-Modus |

---

### Erweiterungs-Relais

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_pool_controller_ext1_1` bis `switch.violet_pool_controller_ext1_8` | Erweiterungsmodul 1, Relais 1–8 |
| `switch.violet_pool_controller_ext2_1` bis `switch.violet_pool_controller_ext2_8` | Erweiterungsmodul 2, Relais 1–8 |

> **Feature:** erfordert aktiviertes "Erweiterungs-Ausgänge".

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
        entity_id: switch.violet_pool_controller_pump
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_pool_controller_ext1_1
```

### OMNI-DC-Ausgänge (6)

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_pool_controller_omni_dc0` … `switch.violet_pool_controller_omni_dc5` | OMNI-DC-Motor-Ausgänge 0–5 |

OMNI-DC-Ausgänge werden typischerweise für OmniTronic-Mehrwegeventil-Positionen oder DC-Motorsteuerung verwendet.

### Digitalregel-Switches (8)

| Entity | Beschreibung |
|--------|-------------|
| `switch.violet_pool_controller_dirule_1` … `switch.violet_pool_controller_dirule_8` | Schaltregeln 1–8 |

> **Feature:** erfordert aktiviertes "Digitale Eingänge". Für volle Kontrolle nutze [`manage_digital_rules`](Services.de#-service-manage_digital_rules) oder die dedizierten Regel-Services ([`configure_switching_rule`](Services.de#-service-configure_switching_rule), [`enable_rule`](Services.de#-service-enable_rule)).

---

## Switch-Steuerung via UI

### 3-State Toggle

In der Home Assistant UI zeigt jeder Switch:
- **Grün (ON)**: Gerät aktiv — States `1`, `3`, `4`
- **Grau (OFF)**: Gerät inaktiv — States `0`, `2`, `5`, `6`

Für volle Off/On/Auto-Steuerung nutze die passende `select.*_mode`-Entität (z. B. `select.violet_pool_controller_pump_mode`).

### Zustandsdetails ansehen

Auf die Entität klicken → **Attribute**. Ein Schalter liefert:

| Attribut | Bedeutung |
|---|---|
| `raw_state` | Der Rohzustand des Controllers, z. B. `"3"` oder zusammengesetzt `"3\|PUMP_ANTI_FREEZE"` |
| `mode` | Lesbarer Betriebsmodus |
| `status_description` | Lesbare Beschreibung des aktuellen Zustands |
| `runtime` | Laufzeit, sofern der Controller `<KEY>_RUNTIME` meldet |
| `pending_update` | Vorhanden, solange ein optimistischer Wert auf die nächste Abfrage wartet |

Pumpe, Heizung, Solar, Dosierung und Rückspülung ergänzen gerätespezifische
Attribute (Stufe, Kanisterfüllstand, Restreichweite und so weiter).

> Ein Attribut `violet_state` gibt es nicht — der Rohwert heißt `raw_state` —
> und `last_changed` ist eine Home-Assistant-Zustandseigenschaft, kein Attribut
> dieser Integration.

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
          {% set state = states('switch.violet_pool_controller_pump') %}
          {% set raw = state_attr('switch.violet_pool_controller_pump', 'raw_state') | int(-1) %}
          {% if raw == 0 %} Automatik - Bereitschaft
          {% elif raw == 1 %} Automatik - aktiv
          {% elif raw == 2 %} Automatik - durch Regel blockiert
          {% elif raw == 3 %} Automatik - durch Notfallregel eingeschaltet
          {% elif raw == 4 %} Manuell an
          {% elif raw == 5 %} Durch Notfallregel aus
          {% elif raw == 6 %} Manuell aus
          {% else %} Unbekannt
          {% endif %}
```

### Ein Gerät auf Automatik zurücksetzen

> **`switch.turn_off` setzt ein Gerät NICHT auf Automatik.** Es sendet
> **Manuell AUS (Zustand 6)** und hält das Gerät damit dauerhaft aus – der
> eigene Zeitplan und die Regeln des Controllers schalten es nie wieder ein.
> Ein Skript, das mit `switch.turn_off` „alles auf Automatik" stellt, legt den
> Pool still.

Nutze stattdessen die Modus-Auswahl; sie ist die einzige Steuerung, die
`AUTO` erreichen kann:

```yaml
script:
  alle_automatik:
    alias: "Alle Geräte auf Automatik zurücksetzen"
    sequence:
      - action: select.select_option
        target:
          entity_id:
            - select.violet_pool_controller_pump_mode
            - select.violet_pool_controller_heater_mode
            - select.violet_pool_controller_solar_mode
        data:
          option: auto
```

Die genaue Bezeichnung der Option zuerst in **Entwicklerwerkzeuge → Zustände**
nachsehen: sie stammt aus der Übersetzung deiner Home-Assistant-Sprache.

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
      {{ 'PUMP_ANTI_FREEZE' in state_attr('switch.violet_pool_controller_pump', 'raw_state') | string }}
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