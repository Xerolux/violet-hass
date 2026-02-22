# 🎯 Device States erklärt

Dies ist eine der **wichtigsten Seiten**! Hier lernst du, was die 7 Device States (0-6) bedeuten.

## Die 7 Device States

Der Violet Controller nutzt 7 verschiedene States. Jeder State hat eine spezifische Bedeutung:

| State | Name | Deutsch | Typ | Status | Beschreibung |
|-------|------|---------|-----|--------|-------------|
| **0** | AUTO_OFF | Automatik - Aus | Auto | ⛔ OFF | Automatik aktiv, Gerät läuft nicht (bereit) |
| **1** | MANUAL_ON | Manuell An | Manuell | ✅ ON | Benutzer hat manuell eingeschaltet |
| **2** | AUTO_ON | Automatik - An | Auto | ✅ ON | Automatik aktiv, Gerät läuft (Bedingungen erfüllt) |
| **3** | AUTO_TIMER | Automatik - Timer | Auto | ✅ ON | Automatik mit Zeitsteuerung, gerade aktiv |
| **4** | MANUAL_FORCED | Manuell erzwungen | Manuell | ✅ ON | Manuell eingeschaltet, erzwungener Modus |
| **5** | AUTO_WAITING | Automatik - Wartend | Auto | ⛔ OFF | Automatik läuft, wartet aber auf Bedingungen |
| **6** | MANUAL_OFF | Manuell Aus | Manuell | ⛔ OFF | Benutzer hat manuell ausgeschaltet |

## Verständnis der States

### Status-Gruppen

**Geräte die LAUFEN (ON):**
- State 1 (Manuell An)
- State 2 (Automatik - An)
- State 3 (Automatik - Timer)
- State 4 (Manuell erzwungen)

**Geräte die NICHT LAUFEN (OFF):**
- State 0 (Automatik - Bereit)
- State 5 (Automatik - Wartend)
- State 6 (Manuell Aus)

### Manuell vs. Automatik

**Manueller Modus:**
- States 1, 4, 6
- Der Benutzer kontrolliert direkt
- Automatik-Regeln werden ignoriert

**Automatik-Modus:**
- States 0, 2, 3, 5
- Der Controller regelt selbstständig
- Basiert auf Bedingungen (Temperatur, Zeit, Sensoren)

## Praktische Beispiele

### Pumpe-Beispiel

```
Normalbetrieb:
  State 0 → Automatik, Pumpe aus (noch nicht nötig)
  State 2 → Automatik, Pumpe läuft (Bedingung erfüllt)
  State 0 → Automatik, Pumpe aus (Bedingung vorbei)

Manueller Betrieb:
  State 6 → Manuell aus (Benutzer schaltet aus)
  State 1 → Manuell an (Benutzer schaltet an)
  State 0 → Automatik (Benutzer gibt Kontrolle zurück)
```

### Heizer-Beispiel

```
Mit Temperaturregelung:
  State 0 → Heizer aus (Pool hat Solltemperatur)
  State 2 → Heizer läuft (Pool zu kalt)
  State 3 → Heizer mit Timer (zeitgesteuert)
  
Mit Fehler:
  State 5 → Wartet (Fehler verhindert Start)
  State 0 → Behoben (Fehler weg)
```

## Visualisierung in Home Assistant

Die States werden in Home Assistant mit **Icons und Farben** angezeigt:

### Automatik-Modus
- 🟢 **Grün** (Automatik - Aktiv): States 2, 3
  - Gerät läuft, Automatik funktioniert
- 🔵 **Blau** (Automatik - Bereit): States 0, 5
  - Bereit zu starten, wartet auf Bedingungen

### Manuell-Modus
- 🟠 **Orange** (Manuell An): States 1, 4
  - Benutzer hat eingeschaltet
- 🔴 **Rot** (Manuell Aus): State 6
  - Benutzer hat ausgeschaltet

## State-Übergänge

### Typischer Tagesablauf (Pumpe)

```
Morgens:
  [6] Manuell Aus ← Nacht, Benutzer hat ausgeschaltet
        ↓
  [0] Automatik - Bereit ← Benutzer schaltet auf Auto
        ↓
  [2] Automatik - An ← Programmierte Zeit erreicht
        ↓
  [0] Automatik - Bereit ← Programmierte Dauer vorbei

Notfall (manuelles Eingreifen):
  [2] Automatik - An ← Pumpe läuft normal
        ↓
  [1] Manuell An ← Benutzer schaltet manuell ein (ignoriert Auto)
        ↓
  [0] Automatik ← Benutzer gibt Kontrolle zurück

```

## State mit Zusatzinformationen

Manchmal haben States einen **Zusatz durch `|`-Separator**:

```
3|PUMP_ANTI_FREEZE       → State 3, aber Frostschutz ist aktiv
2|BLOCKED_BY_TEMP        → State 2, aber blockiert durch Temperatur
1|HIGH_PRESSURE_WARNING  → State 1, aber hoher Druck-Warnung
```

**Die Ziffer (0-6) ist ausschlaggebend!** Die Zusatzinfo erklärt nur den Kontext.

## States in Automatisierungen nutzen

### Einfache Überprüfung

```yaml
automation:
  - alias: "Überprüfe Pumpen-Status"
    trigger:
      - platform: state
        entity_id: switch.violet_pump
    action:
      - service: notify.notify
        data:
          message: "Pumpen-State: {{ states('switch.violet_pump') }}"
```

### State-spezifische Logik

```yaml
automation:
  - alias: "Warnung bei manuellem Betrieb"
    trigger:
      - platform: template
        value_template: "{{ state_attr('switch.violet_pump', 'violet_state') in ['1', '4', '6'] }}"
    action:
      - service: notify.notify
        data:
          message: "⚠️ Pumpe im manuellen Modus!"
```

### State-Attribute prüfen

```yaml
automation:
  - alias: "Nur bei AUTO-Modus aktiv"
    condition:
      - condition: template
        value_template: "{{ state_attr('switch.violet_pump', 'mode') == 'auto' }}"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.violet_pump
```

## State-Debugging

Möchtest du die States prüfen?

### Developer Tools nutzen
1. **Entwickler Tools** → **States**
2. Nach `violet_pump` suchen
3. Den **State und die Attribute** sehen

### Logs prüfen
```bash
tail -f /config/home-assistant.log | grep violet_pool_controller
```

### YAML-Template prüfen
1. **Entwickler Tools** → **Templates**
2. Template eingeben:
```yaml
Aktueller Pump-State: {{ states('switch.violet_pump') }}
Pump-Attribute: {{ state_attr('switch.violet_pump', 'violet_state') }}
```

## Häufige State-Probleme

### Problem: State ist immer "6" (Manuell Aus)

**Ursachen:**
- Manueller Schalter ist AUS
- Vergangenheit (sollte Auto sein)

**Lösung:**
```yaml
service: violet_pool_controller.turn_auto
target:
  entity_id: switch.violet_pump
```

### Problem: State wechselt ständig

**Ursachen:**
- Automatik-Bedingungen sind instabil
- Temperatur pendelt am Grenzwert

**Lösung:**
- Größerer Hysterese-Bereich einstellen
- Abfrageintervall erhöhen

### Problem: State bleibt bei 5 (Wartend)

**Ursachen:**
- Fehler oder Blockade am Controller
- Sicherheitsintervall läuft

**Lösung:**
- Controller-Fehlercodes prüfen
- Warten lassen

## Nächste Schritte

- 📖 Lies: [[Switches]] - 3-State Schalter verstehen
- 🤖 Services: [[Services]] - Automatisierte Kontrolle
- 🚨 Fehler: [[Troubleshooting]] - States debuggen
