# Device States (0–6)

> Das **wichtigste Konzept** der Integration! Hier lernst du, was die 7 Device States bedeuten und wie du sie in Automatisierungen nutzt.

---

## Die 7 Device States

Der Violet Controller unterscheidet 7 Betriebszustände für jedes steuerbare Gerät:

| State | Konstante | Status | Typ | Beschreibung |
|-------|-----------|--------|-----|--------------|
| **0** | `AUTO_OFF` | OFF | Automatik | Automatik aktiv – Gerät läuft nicht (Bedingungen nicht erfüllt) |
| **1** | `MANUAL_ON` | ON | Manuell | Benutzer hat manuell eingeschaltet |
| **2** | `AUTO_ON` | ON | Automatik | Automatik aktiv – Gerät läuft (Bedingungen erfüllt) |
| **3** | `AUTO_TIMER` | ON | Automatik | Automatik mit Zeitsteuerung – Gerät läuft gerade |
| **4** | `MANUAL_FORCED` | ON | Manuell | Manuell erzwungen – ignoriert alle Automatik-Regeln |
| **5** | `AUTO_WAITING` | OFF | Automatik | Automatik aktiv – wartet auf Bedingungen (z.B. Sicherheitsintervall) |
| **6** | `MANUAL_OFF` | OFF | Manuell | Benutzer hat manuell ausgeschaltet |

---

## State-Gruppen

### Geräte-Status (ON/OFF)

```
┌──────────────────────────────────────────┐
│             GERÄT LÄUFT (ON)             │
│  State 1 (MANUAL_ON)                     │
│  State 2 (AUTO_ON)                       │
│  State 3 (AUTO_TIMER)                    │
│  State 4 (MANUAL_FORCED)                 │
├──────────────────────────────────────────┤
│          GERÄT LÄUFT NICHT (OFF)         │
│  State 0 (AUTO_OFF)                      │
│  State 5 (AUTO_WAITING)                  │
│  State 6 (MANUAL_OFF)                    │
└──────────────────────────────────────────┘
```

### Steuerungstyp (Automatik vs. Manuell)

```
┌──────────────────────────────────────────┐
│          AUTOMATIK-MODUS                 │
│  State 0 – Bereit, wartet               │
│  State 2 – Läuft nach Programm          │
│  State 3 – Läuft nach Zeitplan          │
│  State 5 – Wartet auf Bedingungen       │
├──────────────────────────────────────────┤
│          MANUELL-MODUS                   │
│  State 1 – Manuell ein                  │
│  State 4 – Erzwungen ein                │
│  State 6 – Manuell aus                  │
└──────────────────────────────────────────┘
```

---

## Visualisierung in Home Assistant

| State | Icon-Farbe | Bedeutung |
|-------|-----------|-----------|
| 0 (AUTO_OFF) | Blau | Bereit im Automatik-Modus |
| 1 (MANUAL_ON) | Orange | Manuell eingeschaltet |
| 2 (AUTO_ON) | Grün | Läuft automatisch |
| 3 (AUTO_TIMER) | Grün | Läuft per Zeitplan |
| 4 (MANUAL_FORCED) | Orange | Erzwungen eingeschaltet |
| 5 (AUTO_WAITING) | Blau | Automatik wartet |
| 6 (MANUAL_OFF) | Rot | Manuell ausgeschaltet |

---

## Detaillierte Erklärung jedes States

### State 0 – AUTO_OFF (Automatik, Bereit)

Der Controller läuft im **Automatik-Modus**, aber das Gerät ist aktuell **nicht aktiv** – weil die Bedingungen (Temperatur, Zeit, etc.) noch nicht erfüllt sind.

```
Beispiel Pumpe: Tagesprogramm läuft, aber geplante Zeit noch nicht erreicht.
→ Gerät startet automatisch, wenn Bedingung erfüllt.
```

**In HA**: Schalter zeigt `off`, Attribut `violet_state = "0"`

---

### State 1 – MANUAL_ON (Manuell An)

Der Benutzer hat das Gerät **manuell eingeschaltet**. Automatik-Regeln sind übersteuert.

```
Beispiel: Benutzer schaltet Pumpe manuell ein für Poolreinigung.
→ Läuft bis manuell ausgeschaltet oder auf AUTO zurückgestellt.
```

**In HA**: Schalter zeigt `on`, Attribut `violet_state = "1"`

---

### State 2 – AUTO_ON (Automatik, An)

Der Controller läuft im Automatik-Modus und das Gerät ist **aktiv** – weil alle Bedingungen erfüllt sind.

```
Beispiel Heizung: Pool-Temperatur < Sollwert → Heizung läuft automatisch.
→ Hört automatisch auf, wenn Sollwert erreicht.
```

**In HA**: Schalter zeigt `on`, Attribut `violet_state = "2"`

---

### State 3 – AUTO_TIMER (Automatik, Timer)

Gerät läuft automatisch aufgrund einer **Zeitsteuerung** im Controller.

```
Beispiel: Pumpe läuft täglich 08:00–12:00 Uhr per Timer-Programm.
→ Stoppt automatisch am Zeitplan-Ende.
```

**In HA**: Schalter zeigt `on`, Attribut `violet_state = "3"`

---

### State 4 – MANUAL_FORCED (Manuell, Erzwungen)

Das Gerät wurde **erzwungen eingeschaltet** und ignoriert alle Sicherheits- und Automatik-Einschränkungen.

```
Beispiel: Heizung wird trotz Temperaturgrenzen forciert eingeschaltet.
→ Nur für Wartung/Tests! Vorsichtig verwenden!
```

**In HA**: Schalter zeigt `on`, Attribut `violet_state = "4"`

> **Warnung**: State 4 kann Sicherheitsprüfungen überspringen. Nur für autorisierte Wartungsarbeiten verwenden!

---

### State 5 – AUTO_WAITING (Automatik, Wartend)

Der Controller möchte das Gerät einschalten, **wartet aber** auf eine Bedingung:
- Sicherheitsintervall (z.B. 5 Minuten nach Dosierung)
- Fehler muss behoben werden
- Andere Abhängigkeit nicht erfüllt

```
Beispiel Dosierung: Chlor wurde dosiert, Controller wartet
Sicherheitsintervall ab bevor er wieder startet.
```

**In HA**: Schalter zeigt `off`, Attribut `violet_state = "5"`

---

### State 6 – MANUAL_OFF (Manuell, Aus)

Der Benutzer hat das Gerät **manuell ausgeschaltet**. Automatik-Regeln sind übersteuert.

```
Beispiel: Pool wird für Winter-Pause ausgeschaltet.
→ Gerät startet nicht automatisch bis zurück auf AUTO.
```

**In HA**: Schalter zeigt `off`, Attribut `violet_state = "6"`

---

## Composite States (States mit Zusatzinfo)

Manche States enthalten einen **Pipe-Separator (`|`)** mit zusätzlichem Kontext:

```
Format: {STATE_ZAHL}|{BESCHREIBUNG}

Beispiele:
  "3|PUMP_ANTI_FREEZE"        → State 3, Frostschutz aktiv
  "2|BLOCKED_BY_TEMP"         → State 2, aber durch Temperatur blockiert
  "5|SAFETY_INTERVAL"         → State 5, Sicherheitsintervall läuft
  "1|HIGH_PRESSURE_WARNING"   → State 1, Hochdruckwarnung
```

**Wichtig**: Die **Zahl vor dem `|`** bestimmt den State! Der Text dahinter ist nur Kontext-Information.

In Home Assistant wird der vollständige String als Entity-State gespeichert:
```yaml
# Beispiel Entity-Attribut
violet_state: "3|PUMP_ANTI_FREEZE"
# Der Binary-Status (on/off) basiert auf der Zahl: 3 → ON
```

---

## States in Home Assistant nutzen

### State-Wert lesen

```yaml
# Template: Aktuellen State lesen
{{ states('switch.violet_pump') }}        # → "on" oder "off"
{{ state_attr('switch.violet_pump', 'violet_state') }}  # → "2" oder "3|PUMP_ANTI_FREEZE"
```

### Auf State-Änderungen reagieren

```yaml
automation:
  - alias: "Benachrichtigung bei manueller Pumpen-Steuerung"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('switch.violet_pump', 'violet_state') in ['1', '4', '6'] }}
    action:
      - service: notify.mobile_app_mein_handy
        data:
          title: "Pool"
          message: "Pumpe ist im manuellen Modus!"
```

### State-Gruppen in Kondition prüfen

```yaml
# Prüfen ob Gerät ON ist (States 1,2,3,4)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pump', 'violet_state') | int(default=0) in [1, 2, 3, 4] }}

# Prüfen ob Gerät im Automatik-Modus ist (States 0,2,3,5)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pump', 'violet_state') | int(default=0) in [0, 2, 3, 5] }}

# Prüfen ob Gerät manuell gesteuert wird (States 1,4,6)
condition:
  - condition: template
    value_template: >
      {{ state_attr('switch.violet_pump', 'violet_state') | int(default=0) in [1, 4, 6] }}
```

---

## Typische State-Verläufe

### Normaler Tagesbetrieb (Pumpe)

```
06:00  [0] AUTO_OFF    – Automatik läuft, Pumpe wartet
08:00  [3] AUTO_TIMER  – Timer startet, Pumpe läuft
12:00  [0] AUTO_OFF    – Timer Ende, Pumpe stoppt
16:00  [2] AUTO_ON     – Temperatur-Bedingung erfüllt, Pumpe läuft
18:00  [0] AUTO_OFF    – Temperatur erreicht, Pumpe stoppt
```

### Manuelles Eingreifen

```
[2] AUTO_ON     – Pumpe läuft automatisch
[1] MANUAL_ON   – Benutzer schaltet manuell ein (Test/Reinigung)
[0] AUTO_OFF    – Benutzer gibt Kontrolle zurück ("AUTO" klicken)
[2] AUTO_ON     – Automatik übernimmt wieder
```

### Dosierungs-Ablauf

```
[0] AUTO_OFF    – Dosierung bereit
[2] AUTO_ON     – Chlor-Level niedrig → Dosierung startet
[5] AUTO_WAITING– Dosierung fertig, Sicherheitsintervall läuft (5 Min)
[0] AUTO_OFF    – Sicherheitsintervall vorbei, bereit für nächste Dosierung
```

### Fehlerfall (Heizung)

```
[2] AUTO_ON     – Heizung läuft
[5] AUTO_WAITING– Fehler erkannt, Heizung pausiert
[0] AUTO_OFF    – Fehler behoben, wartet auf nächste Bedingung
[2] AUTO_ON     – Normalzustand wiederhergestellt
```

---

## State-Debugging

### Über Developer Tools

1. **Entwicklerwerkzeuge → Zustände**
2. Nach `switch.violet_pump` suchen
3. State und Attribute prüfen

### Template-Konsole

```
Entwicklerwerkzeuge → Vorlage
```

```yaml
# Alle State-Infos auf einmal
Pumpe State: {{ states('switch.violet_pump') }}
Violet State: {{ state_attr('switch.violet_pump', 'violet_state') }}
Modus: {{ 'MANUELL' if state_attr('switch.violet_pump', 'violet_state') | int(0) in [1,4,6] else 'AUTOMATIK' }}
Läuft: {{ 'JA' if state_attr('switch.violet_pump', 'violet_state') | int(0) in [1,2,3,4] else 'NEIN' }}
```

### Logs prüfen

```bash
tail -f /config/home-assistant.log | grep violet_pool_controller
```

---

## Häufige State-Probleme

### Problem: State bleibt dauerhaft bei "6" (MANUAL_OFF)

**Ursache**: Gerät wurde manuell ausgeschaltet und auf "Manuell" belassen.

**Lösung**: In HA auf "AUTO" klicken, oder:
```yaml
service: switch.turn_on
target:
  entity_id: switch.violet_pump
# Schaltet auf Automatik zurück
```

---

### Problem: State wechselt ständig zwischen 0 und 2

**Ursache**: Automatik-Bedingungen pendeln am Grenzwert (z.B. Temperatur ±0.1°C).

**Lösung**:
- Hysterese im Controller erhöhen
- Abfrageintervall erhöhen (um Messrauschen zu reduzieren)

---

### Problem: State 5 (WAITING) dauert sehr lange

**Ursache**:
- Sicherheitsintervall nach Dosierung (5–10 Minuten normal)
- Fehler-Code am Controller

**Lösung**:
- Fehler-Codes prüfen: `sensor.violet_system_error_codes`
- Abwarten (Sicherheitsintervall ist beabsichtigt)
- Falls >30 Minuten: Controller neu starten

---

**Weiter:** [Sensoren](Sensors) | [Schalter](Switches) | [Services](Services)
