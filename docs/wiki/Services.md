# 🤖 Services & Automatisierungen

Alle verfügbaren Services für erweiterte Automatisierung deines Pools.

## Übersicht aller Services

| Service | Funktion | Parameter |
|---------|----------|-----------|
| **control_pump** | Pumpensteuerung | action, speed, duration |
| **smart_dosing** | Chemikalien dosieren | dosing_type, action, duration |
| **manage_pv_surplus** | Solar-Überschuss | mode, pump_speed |
| **control_dmx_scenes** | Lichter-Szenen | action, sequence_delay |
| **set_light_color_pulse** | Farbpulse | pulse_count, pulse_interval |
| **manage_digital_rules** | Digital-Input Regeln | rule_key, action |
| **test_output** | Diagnose | output, mode, duration |

---

## 🔧 Service: control_pump - Pumpensteuerung

**Beschreibung**: Erweiterte Pumpensteuerung mit Geschwindigkeit und Modi

### Verfügbare Aktionen
- `speed_control` - Geschwindigkeit (1-3) einstellen
- `force_off` - Erzwungenes Ausschalten
- `eco_mode` - Energiesparen-Modus
- `boost_mode` - Maximale Leistung
- `auto` - Zurück zu Automatik

### Beispiele

**Pumpe mit Geschwindigkeit 2 starten**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pump
data:
  action: speed_control
  speed: 2
  duration: 3600  # 1 Stunde
```

**Eco-Modus für 30 Minuten**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pump
data:
  action: eco_mode
  duration: 1800
```

**Boost-Mode (maximale Leistung)**
```yaml
service: violet_pool_controller.control_pump
target:
  entity_id: switch.violet_pump
data:
  action: boost_mode
  duration: 600  # 10 Minuten
```

---

## 🧪 Service: smart_dosing - Intelligente Dosierung

**Beschreibung**: Manuelle oder automatische Dosierung von Chemikalien

### Parameter

| Parameter | Typ | Bereich | Beschreibung |
|-----------|-----|--------|-------------|
| `dosing_type` | Text | pH-, pH+, Chlor, Flockmittel | Welche Chemikalie? |
| `action` | Text | manual_dose, auto, stop | Aktion |
| `duration` | Zahl | 5-300 | Sekunden |
| `safety_override` | Boolean | true/false | Sicherheit ignorieren? |

### Beispiele

**30 Sekunden Chlor dosieren**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.chlorine_dosing
data:
  dosing_type: "Chlor"
  action: manual_dose
  duration: 30
```

**pH-Ausgleich mit Sicherheitschecks**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.ph_dosing_minus
data:
  dosing_type: "pH-"
  action: manual_dose
  duration: 15
  safety_override: false
```

**Automatische Dosierung aktivieren**
```yaml
service: violet_pool_controller.smart_dosing
target:
  entity_id: switch.chlorine_dosing
data:
  dosing_type: "Chlor"
  action: auto
```

---

## ☀️ Service: manage_pv_surplus - PV-Überschuss

**Beschreibung**: Nutze Solaranlagen-Überschuss für Poolheizung

### Parameter

| Parameter | Typ | Bereich | Default | Beschreibung |
|-----------|-----|--------|---------|-------------|
| `mode` | Text | activate/deactivate/auto | - | Modus |
| `pump_speed` | Zahl | 1-3 | 2 | Pumpengeschwindigkeit |

### Beispiele

**PV-Surplus mit Stufe 3**
```yaml
service: violet_pool_controller.manage_pv_surplus
target:
  entity_id: switch.pv_surplus_mode
data:
  mode: activate
  pump_speed: 3
```

**PV-Surplus deaktivieren**
```yaml
service: violet_pool_controller.manage_pv_surplus
target:
  entity_id: switch.pv_surplus_mode
data:
  mode: deactivate
```

---

## 💡 Service: control_dmx_scenes - DMX Lighting

**Beschreibung**: Steuere Pool-Beleuchtungs-Szenen

### Aktionen
- `all_on` - Alle Lichter an
- `all_off` - Alle Lichter aus
- `all_auto` - Automatik
- `sequence` - Szenen-Sequenz
- `party_mode` - Party-Modus

### Beispiele

**Alle Lichter ausschalten**
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: all_off
```

**Party-Modus mit 3-Sekunden-Wechsel**
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: sequence
  sequence_delay: 3
```

---

## 🔍 Service: test_output - Diagnose

**Beschreibung**: Teste Ausgänge für Diagnose

### Parameter
- `output` - Welcher Ausgang (PUMP, HEATER, SOLAR, etc.)
- `mode` - SWITCH, ON, OFF
- `duration` - 1-900 Sekunden

### Beispiel

**Pumpe 2 Minuten testen**
```yaml
service: violet_pool_controller.test_output
target:
  device_id: <device_id>
data:
  output: PUMP
  mode: "ON"
  duration: 120
```

---

## Developer Tools nutzen

Testen kannst du Services direkt im Developer Tools:

1. **Entwickler Tools** → **Services**
2. Service wählen (z.B. `violet_pool_controller.control_pump`)
3. Target und Daten eingeben
4. **"SERVICE AUFRUFEN"** klicken
5. Ergebnis im Service-Log sehen

---

## Nächste Schritte

- 📖 Lies: [Automations](Automations) - Praktische Beispiele
- 🎯 States: [Device-States](Device-States) - States verstehen
- 🚨 Fehler: [Troubleshooting](Troubleshooting) - Service-Fehler lösen
