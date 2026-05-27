# Violet Pool Controller API - Referenzdokument

> Software 1.1.9 | Stand 05/2026 | violet-poolController-api v0.0.18

## Inhaltsverzeichnis

1. [Verbindung & Initialisierung](#1-verbindung--initialisierung)
2. [Lese-Befehle (READ-ONLY)](#2-lese-befehle-read-only)
3. [Schreib-Befehle (WRITE)](#3-schreib-befehle-write)
4. [Dosierung](#4-dosierung)
5. [Pumpensteuerung](#5-pumpensteuerung)
6. [Beleuchtung & DMX](#6-beleuchtung--dmx)
7. [PV-Überschuss](#7-pv-überschuss)
8. [Temperatursteuerung](#8-temperatursteuerung)
9. [Schaltregeln (Digital Input Rules)](#9-schaltregeln-digital-input-rules)
10. [Erweiterungsmodule (EXT1/EXT2)](#10-erweiterungsmodule-ext1ext2)
11. [Kalibrierung](#11-kalibrierung)
12. [Fehlercodes](#12-fehlercodes)
13. [Gerätestates dekodieren](#13-gerätestates-dekodieren)
14. [Controller-Endpoints (Raw)](#14-controller-endpoints-raw)
15. [Response-Format](#15-response-format)
16. [Rate Limiting & Prioritäten](#16-rate-limiting--prioritäten)

---

## 1. Verbindung & Initialisierung

```python
import aiohttp
from violet_poolcontroller_api import VioletPoolAPI

async with aiohttp.ClientSession() as session:
    api = VioletPoolAPI(
        host="192.168.178.55",     # IP oder Hostname
        session=session,            # aiohttp Session (Pflicht)
        username="Basti",          # Optional: Basic Auth
        password="sebi2634",       # Optional: Basic Auth
        use_ssl=False,             # HTTPS verwenden
        verify_ssl=True,           # SSL-Zertifikat prüfen
        timeout=10,                # Request-Timeout in Sekunden
        max_retries=3,             # Max. Wiederholungen bei Fehlern
        dosing_standalone=False,   # True = nur Dosiermodul, kein Basismodul
    )
```

### Properties (read-only)

| Property | Typ | Beschreibung |
|----------|-----|-------------|
| `api.timeout` | `float` | Aktuelles Timeout in Sekunden |
| `api.max_retries` | `int` | Max. Wiederholungsversuche |
| `api.dosing_standalone` | `bool` | Dosier-Standalone-Modus aktiv |

---

## 2. Lese-Befehle (READ-ONLY)

### 2.1 `get_readings()` - Alle Sensordaten

```python
data = await api.get_readings()
```

- **Endpoint**: `GET /getReadings?ALL`
- **Rückgabe**: `dict[str, Any]` - Alle Sensorwerte, Ausgänge, Systemdaten
- **Wichtige Keys** (Beispiele vom Live-System):

| Key | Beispielwert | Beschreibung |
|-----|-------------|-------------|
| `PUMP` | `0` | Pumpe Aus (0=Aus, 1=Ein, 2=Auto-Aktiv, 4=Manuell) |
| `DOS_6_FLOC` | `0` | Flockmittel-Dosierung (0=Aus) |
| `DOS_6_FLOC_STATE` | `[]` | Aktive Status-Flags als Liste |
| `DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML` | `4` | Tagesdosiermenge in ml |
| `DOS_6_FLOC_TOTAL_CAN_AMOUNT_ML` | `19996` | Kanisterinhalt in ml |
| `DOS_6_FLOC_REMAINING_RANGE` | `>99d` | Reichweite |
| `DOS_6_FLOC_RUNTIME` | `00h 00m 10s` | Letzte Laufzeit |
| `HEATER`, `SOLAR`, `LIGHT` | `0` | Ausgänge |
| `date`, `time` | `27.05.2026`, `23:31:29` | Controller-Uhrzeit |

### 2.2 `get_specific_readings(categories)` - Teilabfrage

```python
data = await api.get_specific_readings(["PUMP", "date", "time"])
```

- **Endpoint**: `GET /getReadings?key1,key2,...`
- **Parameter**: `categories: list[str] | tuple[str, ...]`
- **Rückgabe**: `dict[str, Any]`
- **Unterstützt Partial Matching**: `_value` liefert alle *-value Keys
- **Verfügbare Gruppen**: `ADC`, `DOSAGE`, `RUNTIMES`, `PUMPPRIOSTATE`, `BACKWASH`, `SYSTEM`, `INPUT1`-`INPUT4`, `date`, `time`

### 2.3 `get_output_states()` - Ausgangsstates

```python
states = await api.get_output_states()
```

- **Endpoint**: `GET /getOutputstates`
- **Rückgabe**: `dict[str, dict[str, int]]` - Pro Ausgang ein Dict mit ~150 Status-Flags
- **Wichtige Flags pro Ausgang**:

| Flag | Wert | Bedeutung |
|------|------|-----------|
| `MANUAL_DOSING` | 0/4 | Manuelle Dosierung aktiv |
| `MANUAL_SWITCHING` | 0/2/4/6 | Manuelle Schaltung |
| `PV_SURPLUS` | 0/1 | PV-Überschuss aktiv |
| `BLOCKED_BY_BACKWASH` | 0/1 | Durch Rückspülung blockiert |
| `BACKWASH_RULE` | 0/1 | Rückspülregel aktiv |
| `PUMP_RULE_*` | 0/1 | Pumpenregeln 1-8 |
| `FLOC_DOSING_CONTROLLER` | 0/1 | Flockmittel-Dosierregler aktiv |

### 2.4 `get_hardware_profile()` - Hardware-Erkennung

```python
profile = await api.get_hardware_profile()
# {'base_module': True, 'dosing_module': True,
#  'extension_module_1': False, 'extension_module_2': False,
#  'modules_detected': ['base', 'dosing'],
#  'standalone_dosing': False}
```

- **Rückgabe**: `dict[str, bool | list[str]]`
- **Module**: `base_module`, `dosing_module`, `extension_module_1`, `extension_module_2`
- **Erkennung** über `SYSTEM_*_alive_count` Keys (0 = nicht verbunden)

### 2.5 `get_config(parameters)` - Konfiguration lesen

```python
config = await api.get_config(["system_info"])
```

- **Endpoint**: `GET /getConfig?key1,key2,...`
- **Parameter**: `parameters: list[str] | tuple[str, ...]`
- **Rückgabe**: `dict[str, Any]`

### 2.6 `get_history(hours, sensor)` - Historische Daten

```python
history = await api.get_history(hours=24, sensor="ALL")
```

- **Endpoint**: `GET /getHistory?hours=24&sensor=ALL`
- **Parameter**:

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `hours` | `int` | `24` | Stunden zurück |
| `sensor` | `str` | `"ALL"` | Sensor oder `"ALL"` |

### 2.7 `get_weather_data()` - Wetterdaten

```python
weather = await api.get_weather_data()
```

- **Endpoint**: `GET /getWeatherdata`
- **Hinweis**: Gibt 404 auf dem Test-Controller zurück (möglicherweise nicht konfiguriert)

### 2.8 `get_overall_dosing()` - Dosierstatistik

```python
dosing = await api.get_overall_dosing()
```

- **Endpoint**: `GET /getOverallDosing`
- **Hinweis**: Kann Internal Server Error zurückgeben (Controller-abhängig)

---

## 3. Schreib-Befehle (WRITE)

### 3.1 `set_switch_state(key, action, duration, last_value)` - Universeller Schalter

```python
result = await api.set_switch_state("PUMP", "ON", duration=3600, last_value=2)
```

- **Endpoint**: `GET /setFunctionManually?{AUSGANG},{SCHALTZUSTAND},{WERT_1},{WERT_2}`
- **Für DOS_-Keys**: `POST /triggerManualDosing` (automatisch erkannt)
- **Parameter**:

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `key` | `str` | Pflicht | Gerätekey (z.B. `"PUMP"`, `"DOS_6_FLOC"`) |
| `action` | `str` | Pflicht | `"ON"`, `"OFF"`, `"AUTO"`, `"PUSH"`, `"LOCK"`, `"UNLOCK"` |
| `duration` | `float \| None` | `None` | Dauer in Sekunden |
| `last_value` | `float \| None` | `None` | Zusatzwert (z.B. Geschwindigkeit) |

- **Rückgabe**: `{"success": bool, "response": str, "output": str, "message": str}`
- **Standalone-Modus**: Blockiert Basis-Modul-Funktionen (PUMP, HEATER, SOLAR etc.)

### 3.2 `set_config(config)` - Konfiguration schreiben

```python
result = await api.set_config({"key1": "value1", "key2": "value2"})
```

- **Endpoint**: `POST /setConfig`
- **Parameter**: `config: Mapping[str, Any]`
- **Payload wird automatisch bereinigt** (Sanitizer)

### 3.3 `set_output_test_mode(output, mode, duration)` - Ausgangs-Testmodus

```python
result = await api.set_output_test_mode(output="PUMP", mode="SWITCH", duration=120)
```

- **Endpoint**: `POST /setOutputTestmode`
- **Parameter**:

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `output` | `str` | Pflicht | Ausgangs-ID |
| `mode` | `str` | `"SWITCH"` | Testmodus |
| `duration` | `int` | `120` | Dauer in Sekunden (intern in ms konvertiert) |

---

## 4. Dosierung

### 4.1 `manual_dosing(dosing_type, duration)` - Dosierung starten

```python
# Flockmittel 60 Sekunden dosieren
result = await api.manual_dosing("Flockmittel", 60)
# {'success': True, 'response': 'MANDOS_STARTED\nOK', 'output': 'OK'}
```

- **Endpoint**: `POST /triggerManualDosing`
- **Parameter**:

| Parameter | Typ | Beschreibung |
|-----------|-----|-------------|
| `dosing_type` | `str` | Siehe Tabelle unten |
| `duration` | `int` | Dauer in Sekunden |

**Verfügbare Dosier-Typen**:

| dosing_type | Device Key | Output Index | Beschreibung |
|-------------|-----------|-------------|-------------|
| `"Chlor"` | `DOS_1_CL` | 0 | Chlor-Dosierung |
| `"Elektrolyse"` | `DOS_2_ELO` | 1 | Elektrolyse |
| `"pH-"` | `DOS_4_PHM` | 3 | pH-Senker |
| `"pH+"` | `DOS_5_PHP` | 4 | pH-Heber |
| `"Flockmittel"` | `DOS_6_FLOC` | 5 | Flockmittel |

**POST-Formulardaten** (wird automatisch erstellt):

```
action=DOSSTART
output=5              # DOS_6_FLOC → Index 5
runtime=60            # Sekunden
from=1
runtime_formatted=01:00   # MM:SS
```

### 4.2 Dosierung stoppen

```python
result = await api.set_switch_state("DOS_6_FLOC", "OFF")
# {'success': True, 'response': 'MANDOS_STOPPED\nOK', 'output': 'OK'}
```

- Sendet `action=DOSSTOP` statt `DOSSTART`
- Funktioniert für alle `DOS_*` Keys

### 4.3 `set_dosing_parameters(parameters)` - Dosierparameter ändern

```python
result = await api.set_dosing_parameters({
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": 5,
    "DOS_6_FLOC_RUNTIME": "00h 00m 15s",
})
```

- **Endpoint**: `POST /setDosingParameters` (JSON)
- **Parameter**: `Mapping[str, Any]`

---

## 5. Pumpensteuerung

### 5.1 `set_pump_speed(speed, duration)` - Pumpe mit Geschwindigkeit

```python
result = await api.set_pump_speed(speed=2, duration=3600)
```

- **Endpoint**: `GET /setFunctionManually?PUMP,ON,3600,2`
- **Parameter**:

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `speed` | `int` | Pflicht | 1=ECO, 2=Normal, 3=Boost (geclamppt) |
| `duration` | `int` | `0` | Sekunden (0=permanent) |

### 5.2 `control_pump(action, speed, duration)` - Pumpe steuern

```python
# Pumpe EIN mit Speed 3
await api.control_pump("ON", speed=3, duration=0)

# Pumpe AUS (mit Timer)
await api.control_pump("OFF", duration=600)

# Pumpe auf Automatik
await api.control_pump("AUTO")
```

- **Parameter**:

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `action` | `str` | Pflicht | `"ON"`, `"OFF"`, `"AUTO"` |
| `speed` | `int \| None` | `None` | 1-3 (nur bei ON) |
| `duration` | `int` | `0` | Sekunden |

---

## 6. Beleuchtung & DMX

### 6.1 `set_light_color_pulse()` - Farbimpuls

```python
result = await api.set_light_color_pulse()
```

- **Endpoint**: `GET /setFunctionManually?LIGHT,COLOR,0,0`

### 6.2 `set_switch_state("LIGHT", action)` - Licht Ein/Aus

```python
await api.set_switch_state("LIGHT", "ON")
await api.set_switch_state("LIGHT", "OFF")
await api.set_switch_state("LIGHT", "AUTO")
```

- **Endpoint**: `GET /setFunctionManually?LIGHT,{action},0,0`

### 6.3 `set_switch_state("DMX_SCENE{n}", action)` - Einzelszene

```python
await api.set_switch_state("DMX_SCENE1", "ON")
await api.set_switch_state("DMX_SCENE3", "OFF")
```

- **Endpoint**: `GET /setFunctionManually?DMX_SCENE{n},{action},0,0`
- **Szenen**: `DMX_SCENE1` bis `DMX_SCENE12`

### 6.4 `set_all_dmx_scenes(action)` - Alle Szenen gleichzeitig

```python
result = await api.set_all_dmx_scenes("ALLOFF")   # Alle aus
result = await api.set_all_dmx_scenes("ALLON")    # Alle an
result = await api.set_all_dmx_scenes("ALLAUTO")  # Alle auf Auto
```

- **Sendet 12 parallele Requests** via `asyncio.gather`
- **Rückgabe**: `{"success": bool, "response": str}` (kombiniert)

---

## 7. PV-Überschuss

### 7.1 `set_pv_surplus(active, pump_speed)` - PV-Modus steuern

```python
# PV-Überschuss aktivieren mit Speed 2
await api.set_pv_surplus(active=True, pump_speed=2)
# → GET /setFunctionManually?PVSURPLUS,ON,2,0

# PV-Überschuss deaktivieren
await api.set_pv_surplus(active=False)
# → GET /setFunctionManually?PVSURPLUS,OFF,0,0
```

- **WICHTIG**: Speed geht in WERT_1 (Position 3), nicht WERT_2
- **Template**: `PVSURPLUS,{action},{speed},0` (Manual Section 26.3)
- **Parameter**:

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `active` | `bool` | Pflicht | PV-Überschuss aktivieren/deaktivieren |
| `pump_speed` | `int \| None` | `None` | Pumpenstufe |

---

## 8. Temperatursteuerung

### 8.1 `set_device_temperature(climate_key, temperature)` - Solltemperatur

```python
await api.set_device_temperature("HEATER", 28.0)   # Heizung auf 28°C
await api.set_device_temperature("SOLAR", 30.0)     # Solar auf 30°C
```

- **Endpoint**: `GET /setTargetValues?target={climate_key}_TARGET_TEMP&value={temp}`
- **Parameter**:

| Parameter | Typ | Beschreibung |
|-----------|-----|-------------|
| `climate_key` | `str` | `"HEATER"` oder `"SOLAR"` |
| `temperature` | `float` | Zieltemperatur in °C |

### 8.2 `set_ph_target(value)` - pH-Sollwert

```python
await api.set_ph_target(7.2)
```

- **Endpoint**: `GET /setTargetValues?target=pH&value=7.2`

### 8.3 `set_orp_target(value)` - Redox-Sollwert

```python
await api.set_orp_target(750)
```

- **Endpoint**: `GET /setTargetValues?target=ORP&value=750`

### 8.4 `set_min_chlorine_level(value)` - Mindest-Chlorgehalt

```python
await api.set_min_chlorine_level(0.5)
```

- **Endpoint**: `GET /setTargetValues?target=MinChlorine&value=0.5`

### 8.5 `set_target_value(key, value)` - Generischer Zielwert

```python
await api.set_target_value("HEATER_TARGET_TEMP", 28.0)
```

- **Endpoint**: `GET /setTargetValues?target={key}&value={value}`

---

## 9. Schaltregeln (Digital Input Rules)

### 9.1 `trigger_digital_input_rule(rule_key)` - Regel auslösen

```python
await api.trigger_digital_input_rule("DIRULE_1")
```

- **Endpoint**: `GET /setFunctionManually?DIRULE_1,PUSH,0,0`
- **Regeln**: `DIRULE_1` bis `DIRULE_7`

### 9.2 `set_digital_input_rule_lock(rule_key, locked)` - Regel sperren/entsperren

```python
await api.set_digital_input_rule_lock("DIRULE_1", locked=True)   # Sperren
await api.set_digital_input_rule_lock("DIRULE_3", locked=False)  # Entsperren
```

- **Endpoint**: `GET /setFunctionManually?DIRULE_{n},LOCK,0,0`
- **Endpoint**: `GET /setFunctionManually?DIRULE_{n},UNLOCK,0,0`

---

## 10. Erweiterungsmodule (EXT1/EXT2)

### 10.1 Relais schalten

```python
# EXT1 - Erweiterungsmodul 1
await api.set_switch_state("EXT1_1", "ON", duration=3600)   # Relais 1.1 EIN
await api.set_switch_state("EXT1_8", "OFF")                  # Relais 1.8 AUS

# EXT2 - Erweiterungsmodul 2
await api.set_switch_state("EXT2_5", "ON", duration=3600)   # Relais 2.5 EIN
await api.set_switch_state("EXT2_3", "AUTO")                # Relais 2.3 Auto
```

- **Endpoint**: `GET /setFunctionManually?EXT{1|2}_{1-8},{action},{duration},0`
- **Verfügbar**: `EXT1_1` bis `EXT1_8`, `EXT2_1` bis `EXT2_8` (je nach Modul)
- **Im Standalone-Dosiermodus** werden EXT-Readings herausgefiltert

---

## 11. Kalibrierung

### 11.1 `get_calibration_raw_values()` - Rohwerte

```python
raw = await api.get_calibration_raw_values()
```

- **Endpoint**: `GET /getCalibRawValues`

### 11.2 `get_calibration_history(sensor)` - Kalibrierhistorie

```python
history = await api.get_calibration_history("pH")
```

- **Endpoint**: `GET /getCalibHistory?sensor={sensor}`
- **Rückgabe**: `list[dict]` mit `timestamp`, `value`, `type`

### 11.3 `restore_calibration(sensor, timestamp)` - Kalibrierung wiederherstellen

```python
await api.restore_calibration("pH", "1704110400000")
```

- **Endpoint**: `POST /restoreOldCalib`

---

## 12. Fehlercodes

### 12.1 Error-Benachrichtigungen dekodieren

Fehlercodes werden VOM Controller an externe Systeme gepusht (HTTP GET/POST).

```python
# Einzelnen Fehlercode dekodieren
result = VioletPoolAPI.parse_error_notification("0173")
# {'code': '0173', 'severity': 'WARNING',
#  'message': 'Flockmittel: Kanister Restinhalt niedrig',
#  'is_alarm': False, 'is_warning': True, 'is_info': False}

# Mehrere Fehler aus Notification-Payload
results = VioletPoolAPI.parse_multiple_errors({
    "ERRORCODE": "0120,0173",
    "SUBJECT": "Multi-Fehler"
})
# [{'code': '0120', ...}, {'code': '0173', ...}]
```

- **Statische Methoden** - keine API-Verbindung nötig
- **Fallback**: Unbekannte Codes → WARNING + SUBJECT-Text

### 12.2 Alle Fehlercodes (Manual Section 27.2)

#### System (0000-0012)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0000 | INFO | Testnachricht |
| 0001 | INFO | Statusnachricht |
| 0002 | ALARM | Hardwareproblem (COM-Link zum Carrier fehlerhaft) |
| 0005 | INFO | Wartungsarbeiten am Cloud-Server |
| 0008 | WARNING | CPU-Temperatur hoch (> 83°C) |
| 0009 | ALARM | CPU-Temperatur zu hoch (> 95°C) |
| 0010 | INFO | Update steht zur Installation bereit. Keine Aktion erforderlich. |
| 0011 | INFO | Update steht zur Installation bereit. Installation erforderlich. |
| 0012 | INFO | Update steht zur Installation bereit. Installation erforderlich. |

#### Filter/Zirkulation (0020-0027)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0020 | ALARM | Filterdrucküberwachung (Druck zu niedrig) |
| 0021 | ALARM | Filterdrucküberwachung (Druck zu hoch) |
| 0022 | WARNING | Messwasserüberwachung (Anströmung fehlt) |
| 0023 | WARNING | Messwasserüberwachung (Anströmung zu hoch) |
| 0024 | ALARM | Zirkulationsüberwachung (Zirkulation fehlt) |
| 0025 | ALARM | Zirkulationsüberwachung (Zirkulation zu hoch) |
| 0026 | ALARM | Filterpumpen-Frostschutz nicht verfügbar - Sensorfehler |
| 0027 | ALARM | Absorber-Frostschutz nicht verfügbar - Sensorfehler |

#### Wärmetauscher (0030-0031)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0030 | WARNING | Wärmetauscher Temperatur zu hoch |
| 0031 | ALARM | Wärmetauscher ÜberTemperatur-Schutz nicht verfügbar - Sensorfehler |

#### Rückspülung/Nachspeisung (0040-0054)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0040 | WARNING | Rückspülung wurde ausgelassen |
| 0041 | INFO | Nachspeisung fehlgeschlagen |
| 0042 | INFO | Nachspeisung fehlgeschlagen |
| 0050 | ALARM | Fehler bei Wassernachspeisung / Schwimmerschalter |
| 0051 | ALARM | Fehler bei Wassernachspeisung / Schwimmerschalter |
| 0052 | ALARM | Fehler bei Wassernachspeisung / Schwimmerschalter |
| 0053 | ALARM | Fehler bei Wassernachspeisung / Magnetventil öffnet nicht |
| 0054 | ALARM | Fehler bei Wassernachspeisung / Magnetventil schließt nicht |

#### Überlaufbehälter (0060-0062)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0060 | ALARM | Überlaufbehältersteuerung: Fehler bei Wassernachspeisung |
| 0061 | WARNING | Überlaufbehältersteuerung: Trockenlaufschutz ausgelöst |
| 0062 | WARNING | Überlaufbehälter: Pegelmessung fehlerhaft |

#### Temperatur-/Analog-/Schaltregeln (0071-0098)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0071-0078 | INFO | Temperatursteuerung, Schaltprogramm 1-8 ausgelöst |
| 0081-0088 | INFO | Analogregeln, Schaltprogramm 1-8 ausgelöst |
| 0091-0098 | INFO | Schaltregeln, Schaltprogramm 1-8 ausgelöst |

#### Temperatursensoren (0101-0112)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0101-0112 | WARNING | Temperatursensor 1-12: Fehler bei Messwerterfassung |

#### Chlor-Dosierung (0120-0125)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0120 | WARNING | Chlor-Dosierung: Redox Grenzwert erreicht |
| 0121 | WARNING | Chlor-Dosierung: Chlor Grenzwert erreicht |
| 0122 | WARNING | Chlor-Dosierung: max. Tagesdosierleistung erreicht |
| 0123 | WARNING | Chlor-Kanister Restinhalt niedrig |
| 0124 | WARNING | Chlor-Kanister leer |
| 0125 | WARNING | Leermeldekontakt: Chlor-Kanister |

#### Elektrolyse (0130-0134)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0130 | WARNING | Elektrolyse: Redox Grenzwert erreicht |
| 0131 | WARNING | Elektrolyse: Chlor Grenzwert erreicht |
| 0132 | WARNING | Elektrolyse: maximale Tagesproduktion erreicht |
| 0133 | WARNING | Elektrolyse: Restlaufzeitwarnung für Zelle |
| 0134 | WARNING | Elektrolyse: maximale Gesamt-Betriebszeit erreicht |

#### pH- Dosierung (0150-0155)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0150 | WARNING | pH-minus Dosierung: pH Grenzwert erreicht |
| 0152 | WARNING | pH-minus Dosierung: max. Tagesdosierleistung erreicht |
| 0153 | WARNING | pH-minus Dosierung: Kanister Restinhalt niedrig |
| 0154 | WARNING | pH-minus Dosierung: Kanister leer |
| 0155 | WARNING | Leermeldekontakt: pH-minus Kanister |

#### pH+ Dosierung (0160-0165)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0160 | WARNING | pH-plus Dosierung: pH Grenzwert erreicht |
| 0162 | WARNING | pH-plus Dosierung: max. Tagesdosierleistung erreicht |
| 0163 | WARNING | pH-plus Dosierung: Kanister Restinhalt niedrig |
| 0164 | WARNING | pH-plus Dosierung: Kanister leer |
| 0165 | WARNING | Leermeldekontakt: pH-plus Kanister |

#### Flockmittel (0173-0175)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0173 | WARNING | Flockmittel: Kanister Restinhalt niedrig |
| 0174 | WARNING | Flockmittel: Kanister leer |
| 0175 | WARNING | Leermeldekontakt: Flockmittel Kanister |

#### Kalibrierung (0180-0182)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0180 | INFO | Erinnerung: pH-Elektrode kalibrieren |
| 0181 | INFO | Erinnerung: Redox-Elektrode kalibrieren |
| 0182 | INFO | Erinnerung: Chlor-Elektrode kalibrieren |

#### Hardware-Module (0200-0209)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0200 | WARNING | Dosiermodul: nicht mehr verbunden (abgesteckt) |
| 0201 | WARNING | Dosiermodul: Kommunikation verloren |
| 0203 | WARNING | Relais-Erweiterung 1: nicht mehr verbunden (abgesteckt) |
| 0204 | WARNING | Relais-Erweiterung 1: Kommunikation verloren |
| 0206 | WARNING | Relais-Erweiterung 2: nicht mehr verbunden (abgesteckt) |
| 0207 | WARNING | Relais-Erweiterung 2: Kommunikation verloren |
| 0208 | ALARM | Zweites Dosiermodul erkannt. Wird ignoriert. |
| 0209 | ALARM | Falsch codierte Relais Erweiterung erkannt. |

---

## 13. Gerätestates dekodieren

### 13.1 VioletState-Klasse

```python
from violet_poolcontroller_api import VioletState

state = VioletState(raw_state=2, device_key="PUMP")
state.mode        # "auto"
state.is_active   # True
state.description # "Auto - Active"
state.display_mode # "Automatik (Aktiv)" (Deutsch)
state.icon        # "mdi:autorenew"
```

### 13.2 State-Mapping (Rohwert → Bedeutung)

| Rohwert | Mode | Active | Beschreibung |
|---------|------|--------|-------------|
| `0` | auto | False | Auto - Standby |
| `1` | manual | True | Manual ON |
| `2` | auto | True | Auto - Active |
| `3` | auto | True | Auto - Active (Timer) |
| `4` | manual | True | Manual ON (Forced) |
| `5` | auto | False | Auto - Waiting |
| `6` | manual | False | Manual OFF |
| `ON` | manual | True | Manual ON |
| `OFF` | manual | False | Manual OFF |
| `AUTO` | auto | None | Auto Mode |

### 13.3 Zusammengesetzte States (Pipe-Separated)

```python
# Beispiel: "3|PUMP_ANTI_FREEZE"
state = VioletState("3|PUMP_ANTI_FREEZE")
state.mode        # "frost_protection"
state.is_active   # True
state.description # "Frost Protection Active"
```

### 13.4 DOS_*_STATE - Status-Flags als Liste

```python
# readings["DOS_6_FLOC_STATE"] == ["MANUAL_DOSING"]
# → Flockmittel dosiert gerade manuell
```

---

## 14. Controller-Endpoints (Raw)

### Lese-Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|-------------|
| `/getReadings` | GET | Alle Daten (`?ALL` oder `?key1,key2`) |
| `/getOutputstates` | GET | Ausgangs-Status-Flags |
| `/getConfig` | GET | Konfiguration (`?key1,key2`) |
| `/getHistory` | GET | Historie (`?hours=24&sensor=ALL`) |
| `/getWeatherdata` | GET | Wetterdaten |
| `/getOverallDosing` | GET | Dosierstatistik |
| `/getCalibRawValues` | GET | Kalibrier-Rohwerte |
| `/getCalibHistory` | GET | Kalibrierhistorie (`?sensor=...`) |
| `/debughttp.htm` | GET | Debug-Seite (Live-Request-Logging) |

### Schreib-Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|-------------|
| `/setFunctionManually` | GET | Universeller Schaltbefehl (`?AUSGANG,ACTION,WERT1,WERT2`) |
| `/triggerManualDosing` | POST | Dosierung starten/stoppen (Form-Data) |
| `/setTargetValues` | GET | Zielwerte setzen (`?target=...&value=...`) |
| `/setDosingParameters` | POST JSON | Dosierparameter ändern |
| `/setConfig` | POST | Konfiguration schreiben |
| `/setOutputTestmode` | POST | Testmodus aktivieren |
| `/restoreOldCalib` | POST | Kalibrierung wiederherstellen |

### Befehlsformat `/setFunctionManually` (Manual Section 26.2)

```
{AUSGANG},{SCHALTZUSTAND},{WERT_1},{WERT_2}
```

| AUSGANG | SCHALTZUSTAND | WERT_1 | WERT_2 | Section |
|---------|--------------|--------|--------|---------|
| `PUMP` | ON/OFF/AUTO | Dauer (sec) | Speed (1-3) | 26.2.1 |
| `EXT{1\|2}_{1-8}` | ON/OFF/AUTO | Dauer (sec) | 0 | 26.2.2 |
| `LIGHT` | ON/OFF/AUTO/COLOR | 0 | 0 | 26.2.3 |
| `DMX_SCENE{1-12}` | ON/OFF/AUTO | 0 | 0 | 26.2.3 |
| `ALLON/ALLOFF/ALLAUTO` | (kein State) | 0 | 0 | 26.2.3 |
| `DIRULE_{1-7}` | PUSH/LOCK/UNLOCK | 0 | 0 | 26.2.4 |
| `PVSURPLUS` | ON/OFF | Speed | 0 | 26.3 |
| `HEATER/SOLAR/BACKWASH/...` | ON/OFF/AUTO | Dauer | 0 | 26.2 |

---

## 15. Response-Format

### `/setFunctionManually` - Text/Plain (mehrzeilig)

```
Zeile 1: OK oder ERROR
Zeile 2: Ausgangsname (z.B. "PUMP", "DOS_6_FLOC")
Zeile 3+: Info-Text (z.B. "MANUELL EIN", "Drehzahl 2")
```

**Geparstes Ergebnis**:
```python
{
    "success": True,
    "response": "OK\nPUMP\nMANUELL EIN\nDrehzahl 2",
    "output": "PUMP",
    "message": "MANUELL EIN\nDrehzahl 2"
}
```

### `/triggerManualDosing` - Text/Plain

```
# Dosierung gestartet:
MANDOS_STARTED\nOK

# Dosierung gestoppt:
MANDOS_STOPPED\nOK
```

### `/setFunctionManually` bei DOS_* Keys (Fehler)

```
ERROR\nDOS_1_CL\nTHIS IS A DOSING OUTPUT! ARE YOU NUTS?
```

→ Deshalb wird für DOS_* Keys automatisch `/triggerManualDosing` verwendet.

### JSON-Endpoints

`/getReadings`, `/getOutputstates`, `/getConfig` etc. liefern JSON.

### Error-Notification (Push vom Controller)

```
# HTTP GET oder POST an konfigurierte URL:
ERRORCODE=0173&SUBJECT=Flockmittel%3A+Kanister+Restinhalt+niedrig
```

---

## 16. Rate Limiting & Prioritäten

### Rate Limiter

| Konstante | Wert | Beschreibung |
|-----------|------|-------------|
| `API_RATE_LIMIT_REQUESTS` | 10 | Max Requests pro Window |
| `API_RATE_LIMIT_WINDOW` | 1.0s | Window-Dauer |
| `API_RATE_LIMIT_BURST` | 3 | Burst-Requests erlaubt |
| `API_RATE_LIMIT_RETRY_AFTER` | 0.1s | Wartezeit bei Limit |

### Prioritäten (niedriger = wichtiger)

| Priorität | Wert | Verwendung |
|-----------|------|-----------|
| CRITICAL | 1 | Zustandsänderungen, Dosierung |
| HIGH | 2 | Zielwerte |
| NORMAL | 3 | Reguläre Datenabfragen |
| LOW | 4 | Historie, Statistiken |

### Circuit Breaker

- **Schwellwert**: 5 aufeinanderfolgende Fehler
- **Half-Open nach**: 60 Sekunden
- **Reset**: Bei erfolgreicher Anfrage

---

## Schaltfunktionen - Übersicht

| Key | Label | Unterstützt |
|-----|-------|------------|
| `PUMP` | Filterpumpe | Speed, Timer |
| `SOLAR` | Solarabsorber | Timer |
| `HEATER` | Heizung | Timer |
| `LIGHT` | Beleuchtung | Color Pulse |
| `ECO` | Eco-Modus | - |
| `BACKWASH` | Rückspülung | Timer |
| `BACKWASHRINSE` | Nachspülung | Timer |
| `REFILL` | Wassernachspeisung | Timer |
| `PVSURPLUS` | PV-Überschuss | Speed |
| `DOS_1_CL` | Chlor-Dosierung | Dosierung |
| `DOS_2_ELO` | Elektrolyse | Dosierung |
| `DOS_4_PHM` | pH- Senker | Dosierung |
| `DOS_5_PHP` | pH+ Heber | Dosierung |
| `DOS_6_FLOC` | Flockmittel | Dosierung |
| `EXT1_1` bis `EXT1_8` | Erweiterung 1.1-1.8 | Timer |
| `EXT2_1` bis `EXT2_8` | Erweiterung 2.1-2.8 | Timer |
| `DMX_SCENE1` bis `DMX_SCENE12` | DMX Szenen 1-12 | - |
| `DIRULE_1` bis `DIRULE_7` | Schaltregeln 1-7 | Lock/Unlock |
| `OMNI_DC0` bis `OMNI_DC5` | Omni DC0-DC5 | - |
