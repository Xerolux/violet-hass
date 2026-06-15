> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Device-States)**

---

# Gerätezustände (0–6)

> Das **wichtigste Konzept** der Integration! Jeder steuerbare Ausgang (Pumpe, Heizung, Solar, Licht, Dosierkanäle, Erweiterungsrelais, DMX-Szenen, …) meldet über `/getReadings` einen von 7 numerischen Zustandscodes. Hier ist erklärt, was sie bedeuten und wie man sie in Automatisierungen verwendet.

> Quelle: `OutputState`-Enum in `violet_poolcontroller_api/const_devices.py` (Handbuch-Kapitel 26.1).

---

## Die 7 Ausgangs-Zustandscodes

| Code | Enum-Konstante       | AN/AUS | Modus    | Beschreibung |
|------|-----------------------|--------|----------|--------------|
| **0** | `AUTO_OFF`           | AUS    | Auto     | Automatik aktiv, Gerät im Standby (Bedingungen nicht erfüllt) |
| **1** | `AUTO_ON`            | AN     | Auto     | Automatik aktiv, Gerät läuft (Zeitplan / Bedingungen erfüllt) |
| **2** | `AUTO_PRIO_OFF`      | AUS    | Auto     | Automatik, aber durch Regel blockiert (Priorität AUS) |
| **3** | `AUTO_PRIO_ON`       | AN     | Auto     | Automatik, durch Notfallregel erzwungen (Priorität AN) |
| **4** | `MANUAL_ON`          | AN     | Manuell  | Benutzer hat den Ausgang manuell AN geschaltet (erzwungen) |
| **5** | `EMERGENCY_OFF`      | AUS    | Auto     | Durch Notfall-Regel abgeschaltet |
| **6** | `MANUAL_OFF`         | AUS    | Manuell  | Benutzer hat den Ausgang manuell AUS geschaltet |

> ⚠️ **Ältere Wiki-Versionen hatten diese States falsch zugeordnet** (z. B. State 1 als `MANUAL_ON`). Die obige Tabelle ist die einzig korrekte und wird durch das `OutputState`-Enum im gesamten Code erzwungen.

---

## Boolesche Vereinfachung

```
┌──────────────────────────────────────────┐
│             GERÄT LÄUFT (AN)             │
│   State 1  – AUTO_ON                     │
│   State 3  – AUTO_PRIO_ON (Notfall)      │
│   State 4  – MANUAL_ON (erzwungen)       │
├──────────────────────────────────────────┤
│           GERÄT LÄUFT NICHT (AUS)        │
│   State 0  – AUTO_OFF (Standby)          │
│   State 2  – AUTO_PRIO_OFF (Regelblock)  │
│   State 5  – EMERGENCY_OFF (Notfall)     │
│   State 6  – MANUAL_OFF                  │
└──────────────────────────────────────────┘
```

Das ist der Wert, den `OutputState.is_on` zurückgibt und den `switch`-/`binary_sensor`-Entitäten als primären `on`/`off`-Zustand exponieren.

---

## Modus-Klassifizierung

| Modus        | States  | Bedeutung |
|--------------|---------|-----------|
| **Auto**     | 0, 1, 2, 3, 5 | Der Controller entscheidet auf Basis von Regeln/Zeitplänen |
| **Manuell**  | 4, 6          | Benutzer-Override – Automatikregeln ausgesetzt |
| **Notfall**  | 3, 5          | Eine Notfall-Regel ist gerade aktiv |

Verwenden Sie die Helper-Eigenschaften `is_on`, `is_manual`, `is_emergency` (oder die Klasse `VioletState`) statt die Zahlen direkt zu vergleichen.

---

## PVSURPLUS-Ausnahme

Der `PVSURPLUS`-Ausgang verwendet ein eigenes 0–2-Schema (Handbuch 26.3), **nicht** 0–6:

| Code | Enum-Konstante   | AN/AUS | Bedeutung |
|------|-------------------|--------|-----------|
| **0** | `OFF`            | AUS    | PV-Überschuss-Modus inaktiv |
| **1** | `ON_BY_INPUT`    | AN     | Durch Digitaleingang aktiviert |
| **2** | `ON_BY_HTTP`     | AN     | Per HTTP-Anforderung aktiviert |

---

## DMX-Szenen

DMX-Szenen verwenden nur eine Teilmenge der 0–6-Codes (Enum `DmxSceneState`):

| Code | Bedeutung |
|------|-----------|
| 0 | `AUTO_OFF` – Szene inaktiv |
| 1 | `AUTO_ON` – Szene per Zeitplan aktiv |
| 4 | `MANUAL_ON` – Szene manuell an |
| 6 | `MANUAL_OFF` – Szene manuell aus |

---

## Digitaleingangs-Regeln (DIRULE_1..8)

Zustandscodes für `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_n` (Enum `RuleState`):

| Code | Konstante               | Bedeutung |
|------|--------------------------|-----------|
| 0    | `INACTIVE`              | Regel inaktiv |
| 1    | `ACTIVE`                | Regel gerade aktiv |
| 5    | `BLOCKED_BY_RULE`       | Durch andere Regel blockiert |
| 6    | `BLOCKED_MANUALLY`      | Manuell blockiert |

---

## Zusammengesetzte / Pipe-getrennte Zustände

Einige Readings (z. B. `PUMPSTATE`, `HEATERSTATE`, `SOLARSTATE`) liefern zusammengesetzte Werte mit `|`-Trenner. Der numerische Präfix ist der State-Code aus der Tabelle oben; der Suffix trägt zusätzlichen Kontext.

| Beispiel                          | Numeric state | Kontext |
|-----------------------------------|---------------|---------|
| `"3\|PUMP_ANTI_FREEZE"`           | 3 (AUTO_PRIO_ON) | Frostschutz aktiv |
| `"2\|BLOCKED_BY_OUTSIDE_TEMP"`    | 2 (AUTO_PRIO_OFF) | Durch Außentemperatur-Regel blockiert |
| `"5\|BLOCKED_BY_PUMP_OFF"`        | 5 (EMERGENCY_OFF) | Dosierung pausiert, Pumpe aus |

Die Integration extrahiert den numerischen Präfix automatisch; der Suffix bleibt im Entitäts-Attribut erhalten und taucht im Composite-State-Sensor (`PUMPSTATE`, `HEATERSTATE`, `SOLARSTATE`) auf.

### Vollständige Liste der Detail-Codes

Die Integration kennt diese Block/Warte-Gründe (definiert in `DOSING_STATE_DESCRIPTIONS`):

- **Frost**: `PUMP_ANTI_FREEZE`
- **Schwellwerte**: `BLOCKED_BY_TRESHOLDS`, `BLOCKED_BY_THRESHOLDS`, `BLOCKED_BY_CL_TRESHOLDS`, `BLOCKED_BY_CL_THRESHOLDS`, `THRESHOLDS_REACHED`, `THRESHOLDS_REACHED_CL`
- **Pumpenabhängigkeit**: `BLOCKED_BY_PUMP`, `BLOCKED_BY_PUMP_OFF`, `BLOCKED_BY_PUMP_DELAY`, `BLOCKED_BY_START_DELAY`, `BLOCKED_BY_POSTRUN`, `BLOCKED_BY_HEATER_OFF_DELAY`
- **Durchfluss/Zirkulation**: `BLOCKED_BY_FLOW`, `BLOCKED_BY_MISSING_FLOW`, `BLOCKED_BY_MISSING_CIRCULATION`, `WAITING_FOR_PUMP`, `WAITING_FOR_FLOW`
- **Andere Subsysteme**: `BLOCKED_BY_SOLAR`, `BLOCKED_BY_HEATER`, `BLOCKED_BY_BACKWASH`, `BLOCKED_BY_OUTSIDE_TEMP`, `BLOCKED_BY_MAXTEMP`, `BLOCKED_BY_BOILER_TEMP`, `BLOCKED_BY_MAX_AMOUNT`
- **Hardware**: `BLOCKED_BY_MISSING_MODULE`, `BLOCKED_BY_SENSOR_FAULT`
- **Regeln/Overrides**: `BLOCKED_BY_EMERGENCY_CONTROL_RULE`, `BLOCKED_BY_ESC`, `BLOCKED_BY_MANUAL_OFF`, `BLOCKED_BY_UPDATE`, `BLOCKED_BY_RULE`
- **OmniTronic Mehrwegeventil**: `BLOCKED_BY_OMNI`, `BLOCKED_BY_OMIN` (Firmware-Typo), `BLOCKED_BY_OMNI_POS`, `BLOCKED_BY_Z1Z2`
- **Elektrolyse**: `BLOCKED_BY_POLEREVERSAL` (Firmware-Typo)
- **Wartezustände**: `WAITING_FOR_DOSAGECONTROLLERS`, `WAITING_FOR_HEATER_POSTRUN`, `WAITING_FOR_PREFILL`, `WAITING_FOR_STARTTIME`
- **Aktive Dosierung**: `DOSING`, `DOSING_PAUSED`, `MANUAL_DOSING`

---

## States in Home Assistant verwenden

### Rohzustand auslesen

```yaml
{{ states('switch.violet_pool_controller_pump') }}                       # "on" / "off"
{{ state_attr('switch.violet_pool_controller_pump', 'violet_state') }}   # "2" oder "3|PUMP_ANTI_FREEZE"
```

### State-Gruppen prüfen

```yaml
# Gerät AN (States 1, 3, 4)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pool_controller_pump', 'violet_state')
         | regex_replace('\|.*', '') | int(default=-1) in [1, 3, 4] }}

# Gerät im MANUELL-Modus (States 4, 6)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pool_controller_pump', 'violet_state')
         | regex_replace('\|.*', '') | int(default=-1) in [4, 6] }}

# Gerät unter NOTFALL-Regel (States 3, 5)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pool_controller_pump', 'violet_state')
         | regex_replace('\|.*', '') | int(default=-1) in [3, 5] }}
```

### Benachrichtigung bei manuellem Eingriff

```yaml
automation:
  - alias: "Pumpe im manuellen Modus"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('switch.violet_pool_controller_pump', 'violet_state')
             | regex_replace('\|.*', '') | int(default=-1) in [4, 6] }}
        for: "00:05:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Pool"
          message: "Die Pumpe wurde in den manuellen Modus geschaltet"
```

### Frostschutz erkennen

```yaml
automation:
  - alias: "Pumpen-Frostschutz aktiv"
    trigger:
      - platform: template
        value_template: >
          {{ 'PUMP_ANTI_FREEZE' in
             (state_attr('switch.violet_pool_controller_pump', 'violet_state') | string) }}
    action:
      - service: notify.mobile_app
        data:
          message: "Frostschutz aktiviviert – Pumpe läuft automatisch"
```

---

## Visualisierung in Home Assistant

| State | Icon-Farbe | Übersetzungsschlüssel |
|-------|-----------|------------------------|
| 0 (AUTO_OFF)         | Blau    | `auto_inactive` |
| 1 (AUTO_ON)          | Grün    | `auto_active` |
| 2 (AUTO_PRIO_OFF)    | Blau    | `auto_inactive` |
| 3 (AUTO_PRIO_ON)     | Cyan    | `frost_protection` (bei `PUMP_ANTI_FREEZE`) / `auto_active` |
| 4 (MANUAL_ON)        | Orange  | `manual_on` |
| 5 (EMERGENCY_OFF)    | Lila    | `error` |
| 6 (MANUAL_OFF)       | Rot     | `manual_off` |

Quelle: `STATE_ICONS`, `STATE_COLORS`, `STATE_TRANSLATIONS` in `const_devices.py`.

---

## Typische State-Folgen

### Täglicher Pumpenzeitplan

```
06:00  [0] AUTO_OFF       – Zeitplan noch nicht aktiv
08:00  [1] AUTO_ON        – Zeitplan startet Pumpe
12:00  [0] AUTO_OFF       – Zeitplan endet, Standby
16:00  [1] AUTO_ON        – Temperaturbedingung erfüllt
18:00  [0] AUTO_OFF       – Sollwert erreicht
```

### Manueller Eingriff

```
[1] AUTO_ON       – Laufet per Zeitplan
[4] MANUAL_ON     – Benutzer erzwingt AN
[6] MANUAL_OFF    – Benutzer schaltet AUS
[1] AUTO_ON       – Über select-Entität zurück auf AUTO
```

### Chlor-Dosierung mit Sicherheitsintervall

```
[0] AUTO_OFF       – Bereit
[1] AUTO_ON        – Chlor niedrig → Dosierung
[5] EMERGENCY_OFF  – Sicherheitsintervall / blockiert weil Pumpe aus
[2] AUTO_PRIO_OFF  – Max. Tagesmenge erreicht
[0] AUTO_OFF       – Wieder bereit
```

---

## State-Probleme beheben

### State bleibt auf `6` (MANUAL_OFF)

**Ursache:** Ausgang wurde manuell abgeschaltet; Automatikregeln ist umgangen.
**Lösung:** Die passende `select.*_mode`-Entität zurück auf `Auto` stellen oder den Switch-Service aufrufen.

### State wechselt schnell zwischen 0 und 1

**Ursache:** Eine Regelbedingung oszilliert am Schwellwert.
**Lösung:** Hysterese der Regel am Controller erhöhen oder Polling-Interval vergrößern.

### State bleibt lange auf `5` (EMERGENCY_OFF)

**Ursache:** Offener Fehler oder nicht erfüllte Abhängigkeit (z. B. Pumpe aus, Durchfluss fehlt, Max. Tagesmenge erreicht).
**Lösung:** `sensor.violet_pool_controller_*_state` und Seite [Fehlercodes](Error-Codes.de) prüfen.

### State bleibt auf `2` (AUTO_PRIO_OFF)

**Ursache:** Eine höher priorisierte Regel blockiert den Ausgang (z. B. Außentemperatur, Pumpe aus).
**Lösung:** Den `*STATE`-Composite-Sensor auf `BLOCKED_BY_*`-Suffix prüfen.

---

**Weiter:** [Sensoren](Sensors.de) | [Schalter](Switches.de) | [Services](Services.de)
