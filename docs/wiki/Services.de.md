> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Services)**

---

# 🤖 Services & Automatisierungen

Alle verfügbaren Services für erweiterte Automatisierung deines Pools.

## Übersicht aller Services

Die Integration registriert **30+ Services** in vier Phasen:

### Phase 1 — Kern-Steuerung & Diagnose
| Service | Funktion | Parameter |
|---------|----------|-----------|
| `control_pump` | Pumpensteuerung | action, speed, duration |
| `smart_dosing` | Chemikalien dosieren | dosing_type, action, duration, safety_override |
| `manage_pv_surplus` | Solar-Überschuss | mode, pump_speed |
| `control_dmx_scenes` | Lichter-Szenen | device_id, action, sequence_delay |
| `set_light_color_pulse` | Farbpulse | pulse_count, pulse_interval |
| `manage_digital_rules` | Digital-Input Regeln | rule_key, action |
| `test_output` | Diagnose | device_id, output, mode, duration |
| `export_diagnostic_logs` | Log-Export | device_id, lines, include_* |
| `get_connection_status` | Verbindungsstatus | device_id |
| `get_error_summary` | Fehler-Zusammenfassung | device_id, include_history |
| `test_connection` | Verbindung testen | device_id |
| `clear_error_history` | Fehlerhistorie löschen | device_id |

### Phase 2 — HTTP-Control-Services
| Service | Funktion |
|---------|----------|
| `control_heater_http` | Heizung mit Sollwert (on/off + target_temperature) |
| `control_solar_http` | Solar-System steuern |
| `control_cover_http` | open / close / stop |
| `control_backwash_http` | run / abort |
| `manual_dosing_http` | Manuelle Dosierung (chlorine / electrolysis / ph_minus / ph_plus / flocculant / **h2o2**), Laufzeit 1–3600 s |

### Phase 2.5 — Dosierungs-Konfiguration
| Service | Funktion |
|---------|----------|
| `configure_dosing` | Beliebigen Dosier-Config-Parameter setzen |
| `set_dosing_target` | Dosier-Sollwert (0–100) |
| `set_dosing_daytime` | Tageszeit-Fenster (HH:MM) |
| `set_dosing_max_daily` | Max. Tagesmenge (10–10000 ml) |
| `enable_dosing` | Dosier-System aktivieren / deaktivieren |

### Phase 3 — Regel-Management
| Service | Funktion |
|---------|----------|
| `configure_temp_rule` | Temperatur-Regel konfigurieren (TEMPRULE_1–8) |
| `configure_analog_rule` | Analoge Schwellwert-Regel (ANALOGRULE_1–8) |
| `configure_switching_rule` | Digital-Input-Regel (SWITCHINGRULE_1–8) |
| `configure_timer_rule` | Zeitbasierte Regel (TIMERRULE_1–8) |
| `enable_rule` | Beliebige Regel aktivieren / deaktivieren |

### Phase 4 — System-Konfiguration
| Service | Funktion |
|---------|----------|
| `control_extension_relay` | Erweiterungsrelais (relay_id 1–8, action, state, duration) |
| `configure_sensor_calibration` | Sensor-Kalibrierung (sensor_id 1–12, offset, multiplier, min/max) |

> **Dosier-Systeme** der Phase 2/2.5: `chlorine`, `electrolysis`, `ph_minus`, `ph_plus`, `flocculant`, `h2o2`.

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
| `dosing_type` | Text | pH-, pH+, Chlor, Elektrolyse, Flockmittel | Welche Chemikalie? |
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

## 📋 Service: manage_digital_rules - Digital-Input Regeln

**Beschreibung**: Verwalte Automatisierungsregeln für digitale Eingänge

### Parameter

| Parameter | Werte | Beschreibung |
|-----------|-------|-------------|
| `rule_key` | DIRULE_1 bis DIRULE_7 | Welche Regel? |
| `action` | trigger, lock, unlock | Aktion ausführen |

### Beispiele

**Regel 1 auslösen**
```yaml
service: violet_pool_controller.manage_digital_rules
data:
  rule_key: DIRULE_1
  action: trigger
```

**Regel 2 sperren (deaktivieren)**
```yaml
service: violet_pool_controller.manage_digital_rules
data:
  rule_key: DIRULE_2
  action: lock
```

---

## 🎨 Service: set_light_color_pulse - Farb-Pulsing

**Beschreibung**: Sende Farbpuls-Befehle an die Pool-Beleuchtung

### Parameter

| Parameter | Standard | Bereich | Beschreibung |
|-----------|----------|---------|-------------|
| `pulse_count` | 1 | 1-10 | Anzahl der Pulse |
| `pulse_interval` | 500 | 100-2000 ms | Abstand zwischen Pulsen |

### Beispiel

**5 Farbpulse mit 1 Sekunde Abstand**
```yaml
service: violet_pool_controller.set_light_color_pulse
data:
  pulse_count: 5
  pulse_interval: 1000
```

---

## 📊 Service: export_diagnostic_logs - Log-Export (NEU)

**Beschreibung**: Exportiere Integrations-Logs für Troubleshooting und Support

### Parameter

| Parameter | Standard | Bereich | Beschreibung |
|-----------|----------|---------|-------------|
| `device_id` | - | - | Zielgerät (erforderlich) |
| `lines` | 100 | 10-10000 | Anzahl der Log-Zeilen |
| `include_timestamps` | true | true/false | Zeitstempel einschließen? |
| `save_to_file` | false | true/false | In `/config/` speichern? |

### Beispiele

**100 Log-Zeilen exportieren (Standard)**
```yaml
service: violet_pool_controller.export_diagnostic_logs
target:
  device_id: <device_id>
data:
  lines: 100
```

**500 Log-Zeilen mit Timestamps in Datei speichern**
```yaml
service: violet_pool_controller.export_diagnostic_logs
target:
  device_id: <device_id>
data:
  lines: 500
  include_timestamps: true
  save_to_file: true
```

---

## 🌐 Service: control_heater_http - Heizung per HTTP

**Beschreibung**: Pool-Heizung mit Solltemperatur per direktem HTTP-Kommando steuern.

```yaml
service: violet_pool_controller.control_heater_http
data:
  action: "on"
  target_temperature: 28
```

| Parameter | Bereich | Beschreibung |
|-----------|---------|--------------|
| `action` | on, off | Heizung-Aktion |
| `target_temperature` | 10–60 °C | Solltemperatur |

---

## ☀️ Service: control_solar_http - Solar per HTTP

```yaml
service: violet_pool_controller.control_solar_http
data:
  action: "on"
  target_temperature: 30
```

Gleiche Parameterstruktur wie `control_heater_http`.

---

## 🏊 Service: control_cover_http - Cover-Steuerung

```yaml
service: violet_pool_controller.control_cover_http
data:
  action: open   # open | close | stop
```

---

## 🔄 Service: control_backwash_http - Rückspülung per HTTP

```yaml
service: violet_pool_controller.control_backwash_http
data:
  action: run    # run | abort
```

---

## 🧪 Service: manual_dosing_http - Manuelle Dosierung per HTTP

**Beschreibung**: Dosierpumpe manuell per `POST /triggerManualDosing` auslösen. Unterstützt **alle sechs Dosiersysteme** inklusive H2O2.

```yaml
service: violet_pool_controller.manual_dosing_http
data:
  dosing_system: chlorine
  runtime_seconds: 30
```

| Parameter | Werte | Beschreibung |
|-----------|-------|--------------|
| `dosing_system` | chlorine, electrolysis, ph_minus, ph_plus, flocculant, **h2o2** | Erforderlich |
| `runtime_seconds` | 1–3600 | Erforderlich |

---

## ⚙️ Service: configure_dosing - Dosier-Konfiguration

Beliebigen Dosier-Config-Parameter (`config_key`) auf einen `value` setzen:

```yaml
service: violet_pool_controller.configure_dosing
data:
  dosing_system: ph_minus
  config_key: DOSAGE_phminus_setpoint
  value: "7.2"
```

---

## 🎯 Service: set_dosing_target - Dosier-Sollwert

```yaml
service: violet_pool_controller.set_dosing_target
data:
  dosing_system: chlorine
  target_value: 75
```

`target_value` Bereich: 0–100.

---

## 🕐 Service: set_dosing_daytime - Tageszeit-Fenster

```yaml
service: violet_pool_controller.set_dosing_daytime
data:
  dosing_system: ph_minus
  day_start: "07:00"
  day_end: "22:00"
```

---

## 📏 Service: set_dosing_max_daily - Max. Tagesmenge

```yaml
service: violet_pool_controller.set_dosing_max_daily
data:
  dosing_system: chlorine
  max_daily_ml: 500
```

`max_daily_ml` Bereich: 10–10000 ml.

---

## 🔌 Service: enable_dosing - Dosierung aktivieren / deaktivieren

```yaml
service: violet_pool_controller.enable_dosing
data:
  dosing_system: electrolysis
  enabled: true
```

---

## 🌡️ Service: configure_temp_rule - Temperatur-Regel (1–8)

Temperaturbasierte Automatisierungsregel konfigurieren (Handbuch 8.1). Jede Regel kann bis zu drei Ausgänge steuern (`output_1..3` + `output_*_state` 0–6).

```yaml
service: violet_pool_controller.configure_temp_rule
data:
  rule_id: 1
  enabled: true
  sensor_1: 1            # 1–8
  sensor_2: 0            # 0=absolut, 1–8=Sensor
  logic: ">="
  diff_value: 5
  hyst_value: 1
  runtime_on:  "07:00"
  runtime_off: "22:00"
  output_1: "PUMP"
  output_1_state: 1
```

---

## 📊 Service: configure_analog_rule - Analog-Eingangs-Regel (1–8)

```yaml
service: violet_pool_controller.configure_analog_rule
data:
  rule_id: 1
  enabled: true
  adc_input: 1
  logic: ">="
  threshold: 1.5
  hysteresis: 0.1
  output_1: "BACKWASH"
  output_1_state: 1
```

---

## 🔀 Service: configure_switching_rule - Digital-Input-Regel (1–8)

```yaml
service: violet_pool_controller.configure_switching_rule
data:
  rule_id: 1
  enabled: true
  di_input: 1            # 1–12
  contact_type: 0        # 0 = Öffner, 1 = Schließer
  output: "EXT1_1"
  action_on: 4
  action_off: 6
  timeout: 60
```

---

## ⏰ Service: configure_timer_rule - Timer-Regel (1–8)

```yaml
service: violet_pool_controller.configure_timer_rule
data:
  rule_id: 1
  enabled: true
  on_time: "08:00"
  off_time: "22:00"
  weekdays: 127          # Bitmaske 0–127 (Mo–So)
  output_1: "LIGHT"
  output_1_state: 4
```

---

## 🔧 Service: enable_rule - Regel aktivieren / deaktivieren

```yaml
service: violet_pool_controller.enable_rule
data:
  rule_type: temprule    # temprule | analogrule | switchingrule | timerrule
  rule_id: 1
  enabled: false
```

---

## 🔌 Service: control_extension_relay - Erweiterungsrelais

```yaml
service: violet_pool_controller.control_extension_relay
data:
  relay_id: 1            # 1–8
  action: "on"           # on | off | toggle
  # state: 4             # optional direkt 0–6 (überschreibt action)
  # duration: 3600       # optional Sekunden
```

---

## 🌡️ Service: configure_sensor_calibration - Sensor-Kalibrierung

```yaml
service: violet_pool_controller.configure_sensor_calibration
data:
  sensor_id: 1           # 1–12
  offset: -0.3           # -10 bis +10 °C
  multiplier: 1.0        # 0.5–2.0
  min_value: 0
  max_value: 100
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