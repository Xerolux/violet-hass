# Violet Pool Controller API - Referenzdokument

> Software 1.1.9 | Stand 05/2026 | violet-poolController-api v0.0.23

## Inhaltsverzeichnis

1. [Verbindung & Initialisierung](#1-verbindung--initialisierung)
2. [Lese-Befehle (READ-ONLY)](#2-lese-befehle-read-only)
3. [Schreib-Befehle (WRITE)](#3-schreib-befehle-write)
4. [Dosierung](#4-dosierung)
5. [Pumpensteuerung](#5-pumpensteuerung)
6. [Beleuchtung & DMX](#6-beleuchtung--dmx)
7. [PV-├£berschuss](#7-pv-├╝berschuss)
8. [Temperatursteuerung](#8-temperatursteuerung)
9. [Schaltregeln (Digital Input Rules)](#9-schaltregeln-digital-input-rules)
10. [Erweiterungsmodule (EXT1/EXT2)](#10-erweiterungsmodule-ext1ext2)
11. [Kalibrierung](#11-kalibrierung)
12. [Fehlercodes](#12-fehlercodes)
13. [Ger├ñtestates dekodieren](#13-ger├ñtestates-dekodieren)
14. [Konfigurations-Schl├╝ssel](#14-konfigurations-schl├╝ssel-getconfig--post-setconfig)
15. [Controller-Endpoints (Raw)](#15-controller-endpoints-raw)
16. [Response-Format](#16-response-format)
17. [Rate Limiting & Priorit├ñten](#17-rate-limiting--priorit├ñten)

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
        verify_ssl=True,           # SSL-Zertifikat pr├╝fen
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
- **R├╝ckgabe**: `dict[str, Any]` - Alle Sensorwerte, Ausg├ñnge, Systemdaten
- **Wichtige Keys** (Beispiele vom Live-System):

| Key | Beispielwert | Beschreibung |
|-----|-------------|-------------|
| `PUMP` | `0` | Pumpe Aus (0=Auto-Standby, 1=Auto-Ein, 2=Auto-Prio-AUS, 3=Auto-Prio-EIN, 4=Manuell-EIN, 5=Regel-AUS, 6=Manuell-AUS) |
| `DOS_6_FLOC` | `0` | Flockmittel-Dosierung (0=Aus) |
| `DOS_6_FLOC_STATE` | `[]` | Aktive Status-Flags als Liste |
| `DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML` | `4` | Tagesdosiermenge in ml |
| `DOS_6_FLOC_TOTAL_CAN_AMOUNT_ML` | `19996` | Kanisterinhalt in ml |
| `DOS_6_FLOC_REMAINING_RANGE` | `>99d` | Reichweite |
| `DOS_6_FLOC_RUNTIME` | `00h 00m 10s` | Letzte Laufzeit |
| `HEATER`, `SOLAR`, `LIGHT` | `0` | Ausg├ñnge |
| `date`, `time` | `27.05.2026`, `23:31:29` | Controller-Uhrzeit |

### 2.2 `get_specific_readings(categories)` - Teilabfrage

```python
data = await api.get_specific_readings(["PUMP", "date", "time"])
```

- **Endpoint**: `GET /getReadings?key1,key2,...`
- **Parameter**: `categories: list[str] | tuple[str, ...]`
- **R├╝ckgabe**: `dict[str, Any]`
- **Unterst├╝tzt Partial Matching**: `_value` liefert alle *-value Keys
- **Verf├╝gbare Gruppen**: `ADC`, `DOSAGE`, `RUNTIMES`, `PUMPPRIOSTATE`, `BACKWASH`, `SYSTEM`, `INPUT1`-`INPUT4`, `date`, `time`

### 2.3 `get_output_states()` - Ausgangsstates

```python
states = await api.get_output_states()
```

- **Endpoint**: `GET /getOutputstates`
- **R├╝ckgabe**: `dict[str, dict[str, int]]` - Pro Ausgang ein Dict mit ~150 Status-Flags
- **Wichtige Flags pro Ausgang**:

| Flag | Wert | Bedeutung |
|------|------|-----------|
| `MANUAL_DOSING` | 0/4 | Manuelle Dosierung aktiv |
| `MANUAL_SWITCHING` | 0/2/4/6 | Manuelle Schaltung |
| `PV_SURPLUS` | 0/1 | PV-├£berschuss aktiv |
| `BLOCKED_BY_BACKWASH` | 0/1 | Durch R├╝cksp├╝lung blockiert |
| `BACKWASH_RULE` | 0/1 | R├╝cksp├╝lregel aktiv |
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

- **R├╝ckgabe**: `dict[str, bool | list[str]]`
- **Module**: `base_module`, `dosing_module`, `extension_module_1`, `extension_module_2`
- **Erkennung** ├╝ber `SYSTEM_*_alive_count` Keys (0 = nicht verbunden)

### 2.5 `get_config(parameters)` - Konfiguration lesen

```python
config = await api.get_config(["system_info"])
```

- **Endpoint**: `GET /getConfig?key1,key2,...`
- **Parameter**: `parameters: list[str] | tuple[str, ...]`
- **R├╝ckgabe**: `dict[str, Any]`

### 2.6 `get_history(hours, sensor)` - Historische Daten

```python
history = await api.get_history(hours=24, sensor="ALL")
```

- **Endpoint**: `GET /getHistory?hours=24&sensor=ALL`
- **Parameter**:

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `hours` | `int` | `24` | Stunden zur├╝ck |
| `sensor` | `str` | `"ALL"` | Sensor oder `"ALL"` |

### 2.7 `get_weather_data()` - Wetterdaten

```python
weather = await api.get_weather_data()
```

- **Endpoint**: `GET /getWeatherdata`
- **Hinweis**: Gibt 404 auf dem Test-Controller zur├╝ck (m├Âglicherweise nicht konfiguriert)

### 2.8 `get_overall_dosing()` - Dosierstatistik

```python
dosing = await api.get_overall_dosing()
```

- **Endpoint**: `GET /getOverallDosing`
- **Hinweis**: Kann Internal Server Error zur├╝ckgeben (Controller-abh├ñngig)

---

## 3. Schreib-Befehle (WRITE)

### 3.1 `set_switch_state(key, action, duration, last_value)` - Universeller Schalter

```python
result = await api.set_switch_state("PUMP", "ON", duration=3600, last_value=2)
```

- **Endpoint**: `GET /setFunctionManually?{AUSGANG},{SCHALTZUSTAND},{WERT_1},{WERT_2}`
- **F├╝r DOS_-Keys**: `POST /triggerManualDosing` (automatisch erkannt)
- **Parameter**:

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `key` | `str` | Pflicht | Ger├ñtekey (z.B. `"PUMP"`, `"DOS_6_FLOC"`) |
| `action` | `str` | Pflicht | `"ON"`, `"OFF"`, `"AUTO"`, `"PUSH"`, `"LOCK"`, `"UNLOCK"` |
| `duration` | `float \| None` | `None` | Dauer in Sekunden |
| `last_value` | `float \| None` | `None` | Zusatzwert (z.B. Geschwindigkeit) |

- **R├╝ckgabe**: `{"success": bool, "response": str, "output": str, "message": str}`
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

**Verf├╝gbare Dosier-Typen**:

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
output=5              # DOS_6_FLOC ÔåÆ Index 5
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
- Funktioniert f├╝r alle `DOS_*` Keys

### 4.3 `set_dosing_parameters(parameters)` - Dosierparameter ├ñndern

```python
result = await api.set_dosing_parameters({
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": 5,
    "DOS_6_FLOC_RUNTIME": "00h 00m 15s",
})
```

- **Endpoint**: `POST /setConfig` (JSON) ÔÇö delegates to `set_config()`
- **Parameter**: `Mapping[str, Any]`
- **Hinweis**: `/setDosingParameters` existiert nicht auf dem Controller (FW 1.1.9), alle Dosierparameter werden ├╝ber `/setConfig` geschrieben

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

- **Sendet einen einzelnen Request** ÔÇö ALLON/ALLOFF/ALLAUTO sind globale Aktionen, ein Request an DMX_SCENE1 schaltet alle 12 Szenen + LIGHT gleichzeitig
- **R├╝ckgabe**: `{"success": bool, "response": str}`

---

## 7. PV-├£berschuss

### 7.1 `set_pv_surplus(active, pump_speed)` - PV-Modus steuern

```python
# PV-├£berschuss aktivieren mit Speed 2
await api.set_pv_surplus(active=True, pump_speed=2)
# ÔåÆ GET /setFunctionManually?PVSURPLUS,ON,2,0

# PV-├£berschuss deaktivieren
await api.set_pv_surplus(active=False)
# ÔåÆ GET /setFunctionManually?PVSURPLUS,OFF,0,0
```

- **WICHTIG**: Speed geht in WERT_1 (Position 3), nicht WERT_2
- **Template**: `PVSURPLUS,{action},{speed},0` (Manual Section 26.3)
- **Nur ON/OFF**: Die Spezifikation (Manual 26.3) dokumentiert f├╝r PVSURPLUS
  ausschlie├ƒlich `ON` und `OFF` ÔÇö ein `AUTO` existiert nicht (getReadings
  liefert f├╝r PVSURPLUS nur die Zust├ñnde 0/1/2). Wird `AUTO` an
  `set_switch_state("PVSURPLUS", ...)` ├╝bergeben, sendet die Bibliothek
  spezifikationskonform `OFF` (mit Warnung im Log); andere Aktionen werfen
  `VioletPoolAPIError`.
- **Speed-Bereich**: `pump_speed` wird auf den dokumentierten Bereich 1ÔÇô3
  begrenzt. Ohne Angabe ├╝bernimmt der Controller die in der GUI
  konfigurierte Drehzahl.
- **Parameter**:

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `active` | `bool` | Pflicht | PV-├£berschuss aktivieren/deaktivieren |
| `pump_speed` | `int \| None` | `None` | Pumpenstufe (1ÔÇô3) |

---

## 8. Temperatursteuerung

### 8.1 `set_device_temperature(climate_key, temperature)` - Solltemperatur

```python
await api.set_device_temperature("HEATER", 28.0)   # Heizung auf 28┬░C
await api.set_device_temperature("SOLAR", 30.0)     # Solar auf 30┬░C
```

- **Endpoint**: `POST /setConfig` ÔÇö delegates to `set_target_value()` ÔåÆ `set_config()`
- **Parameter**:

| Parameter | Typ | Beschreibung |
|-----------|-----|-------------|
| `climate_key` | `str` | `"HEATER"` oder `"SOLAR"` |
| `temperature` | `float` | Zieltemperatur in ┬░C |

### 8.2 `set_ph_target(value)` - pH-Sollwert

```python
await api.set_ph_target(7.2)
```

- **Endpoint**: `POST /setConfig` ÔÇö delegates to `set_target_value()` ÔåÆ `set_config()`

### 8.2 `set_ph_target(value)` - pH-Sollwert

```python
await api.set_ph_target(7.2)
```

- **Endpoint**: `POST /setConfig` ÔÇö delegates to `set_target_value()` ÔåÆ `set_config()`

### 8.3 `set_orp_target(value)` - Redox-Sollwert

```python
await api.set_orp_target(750)
```

- **Endpoint**: `POST /setConfig` ÔÇö delegates to `set_target_value()` ÔåÆ `set_config()`

### 8.4 `set_min_chlorine_level(value)` - Mindest-Chlorgehalt

```python
await api.set_min_chlorine_level(0.5)
```

- **Endpoint**: `POST /setConfig` ÔÇö delegates to `set_target_value()` ÔåÆ `set_config()`

### 8.5 `set_target_value(key, value)` - Generischer Zielwert

```python
await api.set_target_value("HEATER_TARGET_TEMP", 28.0)
```

- **Endpoint**: `POST /setConfig` ÔÇö delegates to `set_config({key: value})`
- **Hinweis**: `/setTargetValues` existiert nicht auf dem Controller (FW 1.1.9)

---

## 9. Schaltregeln (Digital Input Rules)

### 9.1 `trigger_digital_input_rule(rule_key)` - Regel ausl├Âsen

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
- **Verf├╝gbar**: `EXT1_1` bis `EXT1_8`, `EXT2_1` bis `EXT2_8` (je nach Modul)
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
- **R├╝ckgabe**: `list[dict]` mit `timestamp`, `value`, `type`

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

- **Statische Methoden** - keine API-Verbindung n├Âtig
- **Fallback**: Unbekannte Codes ÔåÆ WARNING + SUBJECT-Text

### 12.2 Alle Fehlercodes (Manual Section 27.2)

#### System (0000-0012)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0000 | INFO | Testnachricht |
| 0001 | INFO | Statusnachricht |
| 0002 | ALARM | Hardwareproblem (COM-Link zum Carrier fehlerhaft) |
| 0005 | INFO | Wartungsarbeiten am Cloud-Server |
| 0008 | WARNING | CPU-Temperatur hoch (> 83┬░C) |
| 0009 | ALARM | CPU-Temperatur zu hoch (> 95┬░C) |
| 0010 | INFO | Update steht zur Installation bereit. Keine Aktion erforderlich. |
| 0011 | INFO | Update steht zur Installation bereit. Installation erforderlich. |
| 0012 | INFO | Update steht zur Installation bereit. Installation erforderlich. |

#### Filter/Zirkulation (0020-0027)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0020 | ALARM | Filterdruck├╝berwachung (Druck zu niedrig) |
| 0021 | ALARM | Filterdruck├╝berwachung (Druck zu hoch) |
| 0022 | WARNING | Messwasser├╝berwachung (Anstr├Âmung fehlt) |
| 0023 | WARNING | Messwasser├╝berwachung (Anstr├Âmung zu hoch) |
| 0024 | ALARM | Zirkulations├╝berwachung (Zirkulation fehlt) |
| 0025 | ALARM | Zirkulations├╝berwachung (Zirkulation zu hoch) |
| 0026 | ALARM | Filterpumpen-Frostschutz nicht verf├╝gbar - Sensorfehler |
| 0027 | ALARM | Absorber-Frostschutz nicht verf├╝gbar - Sensorfehler |

#### W├ñrmetauscher (0030-0031)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0030 | WARNING | W├ñrmetauscher Temperatur zu hoch |
| 0031 | ALARM | W├ñrmetauscher ├£berTemperatur-Schutz nicht verf├╝gbar - Sensorfehler |

#### R├╝cksp├╝lung/Nachspeisung (0040-0054)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0040 | WARNING | R├╝cksp├╝lung wurde ausgelassen |
| 0041 | INFO | Nachspeisung fehlgeschlagen |
| 0042 | INFO | Nachspeisung fehlgeschlagen |
| 0050 | ALARM | Fehler bei Wassernachspeisung / Schwimmerschalter |
| 0051 | ALARM | Fehler bei Wassernachspeisung / Schwimmerschalter |
| 0052 | ALARM | Fehler bei Wassernachspeisung / Schwimmerschalter |
| 0053 | ALARM | Fehler bei Wassernachspeisung / Magnetventil ├Âffnet nicht |
| 0054 | ALARM | Fehler bei Wassernachspeisung / Magnetventil schlie├ƒt nicht |

#### ├£berlaufbeh├ñlter (0060-0062)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0060 | ALARM | ├£berlaufbeh├ñltersteuerung: Fehler bei Wassernachspeisung |
| 0061 | WARNING | ├£berlaufbeh├ñltersteuerung: Trockenlaufschutz ausgel├Âst |
| 0062 | WARNING | ├£berlaufbeh├ñlter: Pegelmessung fehlerhaft |

#### Temperatur-/Analog-/Schaltregeln (0071-0098)

| Code | Severity | Nachricht |
|------|----------|-----------|
| 0071-0078 | INFO | Temperatursteuerung, Schaltprogramm 1-8 ausgel├Âst |
| 0081-0088 | INFO | Analogregeln, Schaltprogramm 1-8 ausgel├Âst |
| 0091-0098 | INFO | Schaltregeln, Schaltprogramm 1-8 ausgel├Âst |

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
| 0133 | WARNING | Elektrolyse: Restlaufzeitwarnung f├╝r Zelle |
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

## 13. Ger├ñtestates dekodieren

### 13.1 VioletState-Klasse

```python
from violet_poolcontroller_api import VioletState

state = VioletState(raw_state=2, device_key="PUMP")
state.mode        # "auto"
state.is_active   # True
state.description # "Auto - Active"
state.display_mode # "Automatik (Aktiv)" (Default: Deutsch)
state.icon        # "mdi:autorenew"

# Sprache der Status-Texte (Default "de", verf├╝gbar: "de", "en"):
state.display_mode_for("en")            # "Auto (Active)" ÔÇô einmalig
VioletState(2, language="en").display_mode  # pro Instanz

from violet_poolcontroller_api import set_state_translation_language
set_state_translation_language("en")    # global f├╝r alle display_mode-Aufrufe
```

### 13.2 State-Mapping (Rohwert ÔåÆ Bedeutung)

| Rohwert | Mode | Active | Beschreibung |
|---------|------|--------|-------------|
| `0` | auto | False | Auto ÔÇô Standby (Automatik, derzeit aus) |
| `1` | auto | True | Auto ÔÇô Ein (Automatik, derzeit ein) |
| `2` | auto | False | Auto ÔÇô Prio AUS (durch Regel deaktiviert) |
| `3` | auto | True | Auto ÔÇô Prio EIN (Notfallregel aktiviert) |
| `4` | manual | True | MANUELL EIN (erzwungen) |
| `5` | auto | False | AUS durch Regel (Notfallregel) |
| `6` | manual | False | MANUELL AUS |
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
# ÔåÆ Flockmittel dosiert gerade manuell
```

---

## 14. Konfigurations-Schl├╝ssel (`/getConfig` / `POST /setConfig`)

Alle Konfigurationswerte werden ├╝ber `GET /getConfig?key1,key2` gelesen und ├╝ber `POST /setConfig` (form-encoded) geschrieben. Die Schl├╝ssel entsprechen den HTML-Element-IDs des Controller-WebUI.

### 14.1 Benutzer & Pool (`configuration.htm` CID=1,2)

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `USER_salutation` | int (0-2) | Anrede |
| `USER_firstname` | string | Vorname |
| `USER_lastname` | string | Nachname |
| `USER_birthday` | string (DD.MM.YYYY) | Geburtstag |
| `USER_street`, `USER_streetnr` | string | Stra├ƒe / Nr. |
| `USER_zip`, `USER_city` | string | PLZ / Ort |
| `USER_country` | string (ISO) | Land (z.B. "DE") |
| `USER_email` | string | E-Mail |
| `USER_pp_accepted_cloud` | int (0/1) | Datenschutz Cloud |
| `POOL_location` | int (0/1) | Standort (indoor/outdoor) |
| `POOL_type` | int (0/1) | Beckentyp |
| `POOL_cover` | int (0-4) | Abdeckungstyp |
| `POOL_surface` | float | Oberfl├ñche (m┬▓) |
| `POOL_volume` | float | Volumen (m┬│) |
| `POOL_usage` | float (0/0.25/0.50) | Nutzungsfaktor |

### 14.2 Benachrichtigungen (`configuration.htm` CID=3)

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `NOTIFY_email_enable` | int (0/1) | E-Mail aktiv |
| `NOTIFY_email_service` | int (0/1) | 0=VIOLET-Service, 1=SMTP |
| `NOTIFY_email_smtp_host` | string | SMTP-Host |
| `NOTIFY_email_smtp_port` | int | SMTP-Port |
| `NOTIFY_email_smtp_user` | string | SMTP-User |
| `NOTIFY_email_smtp_pass` | string | SMTP-Passwort |
| `NOTIFY_email_smtp_sender` | string | Absender-Adresse |
| `NOTIFY_email_sender_name` | string | Absender-Name |
| `NOTIFY_email{1-5}` | string | E-Mail-Empf├ñnger 1-5 |
| `NOTIFY_email{1-5}_active` | int (0/1) | Empf├ñnger aktiv |
| `NOTIFY_push_enable` | int (0/1) | Push aktiv |
| `NOTIFY_push_serviceprovider` | int (0/1) | 0=Pushover, 1=Telegram |
| `NOTIFY_push_user_key` | string | Pushover User Key |
| `NOTIFY_push_api_token` | string | Pushover API Token |
| `NOTIFY_push_sender_name` | string | Push-Absender-Name |
| `NOTIFY_telegram_user_id` | string | Telegram User ID |
| `NOTIFY_http_enable` | int (0/1) | HTTP-Benachrichtigung aktiv |
| `NOTIFY_http_baseurl` | string | HTTP Basis-URL |
| `NOTIFY_http_path` | string | HTTP Pfad |
| `NOTIFY_http_query` | string | HTTP Query-Parameter |
| `NOTIFY_http_type` | string (GET/POST) | HTTP-Methode |
| `NOTIFY_http_response_ok` | string | Erwartete OK-Antwort |
| `NOTIFY_http_response_error` | string | Erwartete Fehler-Antwort |
| `NOTIFY_dailystatus_enable` | int (0/1) | T├ñglicher Status aktiv |
| `NOTIFY_dailystatus_on` | string (HH:MM) | Sendezeitpunkt |
| `NOTIFY_FEM_messageoptions` | int | Message-Options Bitmask |

### 14.3 Funktionssteuerung (`configuration.htm` CID=4)

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `MENU_control_1` | string (none/block) | Filterpumpe aktiv |
| `PUMP_type` | int (0/1/2) | 0=Einstufig, 1=Drehzahl, 2=RS485 |
| `PUMP_pconsumtion_{0-3}` | float | Stromverbrauch pro Stufe (W) |
| `PUMP_capacity_{0-3}` | float | F├Ârdermenge pro Stufe (l/h) |
| `PUMP_RS485_model` | string | RS485 Pumpenmodell |
| `PUMP_RS485_slaveid` | int | RS485 Slave-ID |
| `PUMP_RS485_prog{1-3}_value` | float | RS485 Programmwert |
| `PUMP_RS485_prog{1-3}_mode` | string | RS485 Modus (RPM/PWR/HZ) |
| `MENU_control_2` | string (none/block) | Solar aktiv |
| `SOLAR_control_type` | int (1/2) | Solartyp |
| `SOLAR_dashboardsensor_{1-3}` | int | Sensor-Zuordnung (1-12) |
| `SOLAR_maxtemp` | float | Solarmaximaltemperatur (┬░C) |
| `MENU_control_3` | string (none/block) | Heizung aktiv |
| `HEATER_type` | int (0/1) | 0=Relais, 1=W├ñrmepumpe |
| `HEATER_set_temp` | float | Heizung Solltemperatur (┬░C) |
| `HEATER_dashboardsensor_{1-3}` | int | Sensor-Zuordnung (1-12) |
| `MENU_control_4` | string (none/block) | R├╝cksp├╝lung aktiv |
| `BACKWASH_type` | int (0/1) | R├╝cksp├╝ltyp |
| `BACKWASH_capacity` | float | Beh├ñltervolumen (l) |
| `MENU_control_5` | string (none/block) | Nachspeisung aktiv |
| `REFILL_capacity` | float | Nachspeisevolumen (l) |
| `REFILL_flowSurveillance_use` | int (0/1) | Durchfluss├╝berwachung (DI7) |
| `MENU_control_6` | string (none/block) | ├£berlauf aktiv |
| `OVERFLOW_footprint` | float | Grundfl├ñche |
| `OVERFLOW_fullat` | float | F├╝llstand voll |
| `OVERFLOW_refillcapacity` | float | Nachspeisevolumen |
| `MENU_control_7` | string (none/block) | Beleuchtung aktiv |
| `LIGHT_control_has_colorchange` | int (0/1) | Farbwechsel unterst├╝tzt |
| `LIGHT_control_max_rules` | int (1-12) | Anzahl Lichtregeln |
| `LIGHT_control_dmx` | int (0/1) | DMX aktiv |
| `LIGHT_control_max_dmx_pattern` | int (3/6/9/12) | Anzahl DMX-Muster |
| `MENU_control_8` | string (none/block) | Abdeckung aktiv |
| `COVER_control_type` | int (0/1) | 0=Vollst├ñndig, 1=Endschalter |
| `COVER_control_web_open` | int (0/1) | Web-UI ├ûffnen erlaubt |
| `COVER_control_web_close` | int (0/1) | Web-UI Schlie├ƒen erlaubt |
| `COVER_control_runtime` | int | Fahrzeit (sec) |
| `WEATHER_use` | int (0/1) | Wetter aktiv |
| `WEATHER_showindashboard` | int (0/1) | Im Dashboard anzeigen |
| `WEATHER_apikey` | string | OpenWeatherMap API-Key |
| `WEATHER_countrycode` | string | L├ñndercode |
| `WEATHER_citycode` | string | Stadtid |
| `WEATHER_cityname` | string | Stadtname |

### 14.4 Dosierung (`configuration.htm` CID=5 + `dosage.htm`)

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `MENU_dosage_1` | string (none/block) | Chlor-Dosierung aktiv |
| `DOSAGE_chlorine_flowrate` | int | Chlor Flie├ƒrate (ml/h) |
| `MENU_dosage_2` | string (none/block) | Elektrolyse aktiv |
| `DOSAGE_electrolysis_prodrate` | float | Produktionsrate (g/h) |
| `DOSAGE_electrolysis_dashboardsensor_1` | int | Sensor-Zuordnung (3-5) |
| `DOSAGE_cl_electrode_use` | int (0/1) | Chlor-Elektrode aktiv |
| `MENU_dosage_3` | string (none/block) | H2O2 aktiv |
| `DOSAGE_h2o2_flowrate` | float | H2O2 Flie├ƒrate |
| `MENU_dosage_4` | string (none/block) | pH- aktiv |
| `DOSAGE_phminus_flowrate` | float | pH- Flie├ƒrate |
| `MENU_dosage_5` | string (none/block) | pH+ aktiv |
| `DOSAGE_phplus_flowrate` | float | pH+ Flie├ƒrate |
| `MENU_dosage_6` | string (none/block) | Flockmittel aktiv |
| `DOSAGE_floc_flowrate` | float | Flockmittel Flie├ƒrate |

**Dosierparameter (aus `dosage.htm`):**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `DOSAGE_chlorine_setpoint_orp` | int | Chlor ORP-Sollwert (mV) |
| `DOSAGE_chlorine_setpoint_chlorine` | float | Chlor-Sollwert (mg/l) |
| `DOSAGE_chlorine_max_daily_output` | float | Max. Tagesmenge (ml) |
| `DOSAGE_electrolysis_setpoint_orp` | int | Elektrolyse ORP-Sollwert (mV) |
| `DOSAGE_electrolysis_setpoint_chlorine` | float | Elektrolyse Chlor-Sollwert |
| `DOSAGE_electrolysis_max_daily_output` | float | Max. Tagesproduktion |
| `DOSAGE_phminus_setpoint` | float | pH- Sollwert |
| `DOSAGE_phminus_max_daily_output` | float | pH- Max. Tagesmenge |
| `DOSAGE_phplus_setpoint` | float | pH+ Sollwert |
| `DOSAGE_phplus_max_daily_output` | float | pH+ Max. Tagesmenge |
| `DOSAGE_floc_dosing_interval` | int | Flockmittel Intervall (min) |
| `DOSAGE_floc_dosing_volume` | float | Flockmittel Menge pro Intervall |
| `DOSAGE_floc_max_daily_output` | float | Flockmittel Max. Tagesmenge |
| `DOSAGE_h2o2_setpoint` | float | H2O2 Sollwert |
| `DOSAGE_h2o2_max_daily_output` | float | H2O2 Max. Tagesmenge |

**Hinweis**: Die Schl├╝ssel `pH` und `ORP` sind ebenfalls g├╝ltige Config-Keys f├╝r die jeweiligen Sollwerte.

### 14.5 Sensoren & Kalibrierung (`configuration.htm` CID=6)

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `NAMES_onewire{1-12}` | string | Sensorname |
| `ROMCODE_onewire{1-12}` | string | ROM-Code Zuordnung |
| `OFFSET_{romcode}` | float | Kalibrierungs-Offset |
| `ONEWIRE_FEM_messageoptions` | int | Sensor-Warnung Bitmask |

### 14.5a Elektroden-Kalibrierung (`calibrations.htm` CID=1/3)

Alle Kalibrierungen werden ├╝ber `POST /setConfig` (form-encoded) gespeichert.

**pH 2-Punkt-Kalibrierung:**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `CALIBRATION_ph_gain` | float | Verst├ñrkungsfaktor (0.1ÔÇô3.0) |
| `CALIBRATION_ph_offset` | float | Offset in mV (┬▒60) |
| `CALIBRATION_ph_last` | string | Datum/Zeit der letzten Kalibrierung |
| `CALIBRATION_ph_last_epoch` | int | Unix-Timestamp |
| `CALIBRATION_ph_electrode_state` | string | `"UNCHANGED"` oder `"NEW_ELECTRODE"` |
| `REMINDER_ph_calibration` | int | Erinnerung in Tagen (0,7,14,30,60,90,120,150,180) |
| `REMINDER_ph_firedate` | string | Datum f├╝r Erinnerung (DD.MM.YYYY) oder `"0"` |
| `CALIBRATION_ph_HW_gain` | float | Hardware-Gain (CID=2) |
| `CALIBRATION_ph_HW_offset` | float | Hardware-Offset (CID=2) |

**Redox (ORP) 1-Punkt-Kalibrierung:**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `CALIBRATION_orp_gain` | float | Verst├ñrkung (immer 1.0) |
| `CALIBRATION_orp_offset` | float | Offset in mV (┬▒100) |
| `CALIBRATION_orp_last` | string | Datum/Zeit der letzten Kalibrierung |
| `CALIBRATION_orp_last_epoch` | int | Unix-Timestamp |
| `CALIBRATION_orp_electrode_state` | string | `"UNCHANGED"` oder `"NEW_ELECTRODE"` |
| `REMINDER_orp_calibration` | int | Erinnerung in Tagen |
| `REMINDER_orp_firedate` | string | Datum oder `"0"` |
| `CALIBRATION_orp_HW_gain` | float | Hardware-Gain (CID=2) |
| `CALIBRATION_orp_HW_offset` | float | Hardware-Offset (CID=2) |

**Potentiostat (Chlor) Kalibrierung:**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `CALIBRATION_pot_gain` | float | Verst├ñrkungsfaktor |
| `CALIBRATION_pot_offset` | float | Offset |
| `CALIBRATION_pot_last` | string | Datum/Zeit der letzten Kalibrierung |
| `CALIBRATION_pot_last_epoch` | int | Unix-Timestamp |
| `CALIBRATION_pot_electrode_state` | string | `"UNCHANGED"` oder `"NEW_ELECTRODE"` |
| `CALIBRATION_pot_calib_flow` | float | Anstr├Âmung bei Kalibrierung (cm/s) |
| `CALIBRATION_pot_calib_temp` | float | Temperatur bei Kalibrierung |
| `CALIBRATION_pot_zeropoint` | float | 0-Punkt Spannung (mV) |
| `CALIBRATION_pot_zeropoint_last_epoch` | int | Epoch des letzten 0-Punkt |
| `CALIBRATION_pot_zeropoint_offset` | float | 0-Punkt Offset (wird bei Kalib auf 0 gesetzt) |
| `CALIBRATION_pot_flow_compensation` | float | Anstr├Âmungskompensations-Faktor |
| `REMINDER_pot_calibration` | int | Erinnerung in Tagen (0,7,14,21) |
| `REMINDER_pot_firedate` | string | Datum oder `"0"` |
| `CALIBRATION_pot_HW_gain` | float | Hardware-Gain (CID=2) |
| `CALIBRATION_pot_HW_offset` | float | Hardware-Offset (CID=2) |

**Kalibrier-Rohwerte (`GET /getCalibRawValues`) liefert:**

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `PH` | float | Aktueller pH-Wert |
| `ORP` | float | Aktueller Redox-Wert (mV) |
| `POT_WO_ZEROPOINTOFFSET` | float | POT ohne 0-Punkt Offset |
| `POT_READABLE_UNCOMP` | float | Unkompensierter Chlorwert |
| `IMP1_value` | float | Anstr├Âmung (cm/s) |
| `PUMP_RPM_1/2/3` | int | Pumpenstatus pro Drehzahl |
| `PUMP` | int | Pumpenstatus |
| `DOS_MODULE_PRESENT` | int | Dosiermodul verbunden (0=ja, Ôëá0=nein) |
| `epoch` | int | Aktueller Unix-Timestamp |
| `date` | string | Aktuelles Datum |
| `time` | string | Aktuelle Zeit |
| `POT_ZEROPOINT` | float | Aktueller 0-Punkt |
| `POT_ZEROPOINT_LAST_EPOCH` | int | Epoch des letzten 0-Punkt |
| `POT_ZEROPOINT_OFFSET` | float | 0-Punkt Offset |
| `onewire1_value` | float | Temperatur Sensor 1 |
| `HW_RAW_PH` | float | Roh-Hardware pH (CID=2) |
| `HW_RAW_ORP` | float | Roh-Hardware ORP (CID=2) |
| `HW_RAW_POT` | float | Roh-Hardware POT (CID=2) |

**Kalibrierhistorie (`GET /getCalibHistory`):**

| Parameter | Format | Beschreibung |
|-----------|--------|-------------|
| `calibrations_ph.log` | pipe-separated | pH-Historie |
| `calibrations_orp.log` | pipe-separated | ORP-Historie |
| `calibrations_pot.log` | pipe-separated | Chlor-Historie |

**pH Log-Zeilenformat** (`date|time|offset|gain|slope_must|slope_is|offset_text|buffer1|mvraw1|buffer2|mvraw2|state|epoch`):
```
PH|28.05.2026|14:30|12.3|0.998|54.19|54.19|Offset: -12.3mV|7.01|123.4|4.01|234.5|UNCHANGED|1748431200
```

**ORP Log-Zeilenformat** (`date|time|offset|offset_text|buffer|mvraw|state|epoch`):
```
ORP|28.05.2026|14:30|5.2|Offset: -5.2mV|468.0|462.8|UNCHANGED|1748431200
```

**POT Log-Zeilenformat** (`date|time|offset|gain|mv_zeropoint|ppm|mv_probe|mv_per_ppm|temp|flow|state|epoch`):
```
POT|28.05.2026|14:30|-52.1|0.045|10540.2|0.60|250.3|7.2|22.5|45.0|UNCHANGED|1748431200
```

**Erinnerung speichern (`CID=1`):**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `REMINDER_FEM_messageoptions` | int | Benachrichtigungs-Methoden Bitmask |

**`POST /restoreOldCalib` (form-encoded):**

| Parameter | Beschreibung |
|-----------|-------------|
| `calDate` | Unix-Timestamp der wiederherzustellenden Kalibrierung |
| `which` | `"ph"`, `"orp"` oder `"pot"` |

**Testmodus f├╝r Anstr├Âmungskompensation:**

`GET /setOutputTestmode?{PUMP_RPM_1/2/3},SWITCH,120000`

### 14.6 Impulsz├ñhler & Analoge Eing├ñnge (`configuration.htm` CID=7)

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `IMPULS_input1_use` | int (0/1) | Impulseingang 1 aktiv |
| `IMPULS_input1_echo_or_switch` | int (0/1) | Echo/Schalter |
| `NAMES_impulscount{1-2}` | string | Impulsz├ñhler-Name |
| `IMPULS_input1_pulses_per_liter` | float | Impulse/Liter |
| `IMPULS_input1_diameter_cell` | float | Zelldurchmesser |
| `IMPULS_input2_use` | int (0/1) | Impulseingang 2 aktiv |
| `IMPULS_input2_signal` | int (0-2) | Signalart |
| `IMPULS_input2_pulses_per_liter` | float | Impulse/Liter |
| `IMPULS_input2_hz_per_ms` | float | Hz pro ms |
| `IMPULS_input2_hz_per_qm` | float | Hz pro m┬▓ |
| `IMPULS_input2_diameter_pipe` | float | Rohrdurchmesser |
| `ANALOG_adc{1-5}_use` | int (0/1) | ADC-Eingang aktiv |
| `NAMES_adc{1-5}` | string | ADC-Name |
| `ANALOG_adc{1-5}_units` | string | Einheit |
| `ANALOG_adc{1-5}_decimal` | int | Nachkommastellen |
| `ANALOG_adc{1-5}_offset` | float | Offset |
| `ANALOG_adc{1-5}_signal_min` | float | Signal Minimum (mA/mV) |
| `ANALOG_adc{1-5}_signal_max` | float | Signal Maximum (mA/mV) |
| `ANALOG_adc{1-5}_range_min` | float | Messbereich Minimum |
| `ANALOG_adc{1-5}_range_max` | float | Messbereich Maximum |

### 14.7 DMX-Lichtmuster (`configuration.htm` CID=8)

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `LIGHT_pattern{1-12}_name` | string | Mustername |
| `LIGHT_pattern{1-12}_channels` | string (CSV) | Aktive Kan├ñle (z.B. "1,3,5,EXT1_2") |
| `LIGHT_pattern{1-12}_values` | string (CSV) | Kanalwerte (0-255) |
| `LIGHT_pattern{1-12}_is_chained_to` | string (CSV) | Verkettete Muster |

### 14.8 Schaltregeln (`configuration.htm` CID=9 + `rules.htm`)

**Regel-Aktivierung:**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `MENU_rules_1` | string (none/block) | Zeitprogramme aktiv |
| `MENU_rules_2` | string (none/block) | Temperatur-Regeln aktiv |
| `MENU_rules_3` | string (none/block) | Schaltregeln aktiv |
| `MENU_rules_4` | string (none/block) | Analog-Regeln aktiv |
| `TIMERRULE_max_rules` | int (1-8) | Anzahl Zeitprogramme |
| `TEMPRULE_max_rules` | int (1-8) | Anzahl Temperatur-Regeln |
| `SWITCHINGRULE_max_rules` | int (1-7) | Anzahl Schaltregeln |
| `ANALOGRULE_max_rules` | int (1-8) | Anzahl Analog-Regeln |

**Zeitprogramme (TIMERRULE, 1-8):**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `TIMERRULE_prog{i}_on_type` | int | Start-Typ |
| `TIMERRULE_prog{i}_on_time` | string (HH:MM) | Start-Zeit |
| `TIMERRULE_prog{i}_on_weekdays` | int | Wochentage Bitmask |
| `TIMERRULE_prog{i}_off_type` | int | Stop-Typ |
| `TIMERRULE_prog{i}_off_time` | string (HH:MM) | Stop-Zeit |
| `TIMERRULE_prog{i}_off_timer` | string (HH:MM) | Timer-Dauer |
| `TIMERRULE_prog{i}_output_{1-3}` | string | Ausgang (PUMP, LIGHT, ECO, EXT*) |
| `TIMERRULE_prog{i}_output_{1-3}_state` | int (1/2) | 1=EIN, 2=AUS |

**Temperatur-Regeln (TEMPRULE, 1-4):**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `TEMPRULE_prog{i}_use` | int (0/1) | Regel aktiv |
| `TEMPRULE_prog{i}_runtime_on` | string (HH:MM) | Zeitfenster Start |
| `TEMPRULE_prog{i}_runtime_off` | string (HH:MM) | Zeitfenster Ende |
| `TEMPRULE_prog{i}_sensor_1` | int | Sensor 1 (1-12) |
| `TEMPRULE_prog{i}_sensor_2` | int | Sensor 2 (0=absolut, 1-12) |
| `TEMPRULE_prog{i}_logic` | string (>= / <=) | Vergleichsoperator |
| `TEMPRULE_prog{i}_diffval` | float | Einschalt-Differenz |
| `TEMPRULE_prog{i}_hystval` | float | Ausschalt-Differenz |
| `TEMPRULE_prog{i}_output_{1-3}` | string | Ausgang |
| `TEMPRULE_prog{i}_output_{1-3}_state` | int (1/2) | EIN/AUS |
| `TEMPRULE_prog{i}_FEM_messageoptions` | int | Benachrichtigung Bitmask |

**Schaltregeln (SWITCHINGRULE, 1-7):**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `SWITCHINGRULE_prog{i}_use` | int (0/1) | Regel aktiv |
| `SWITCHINGRULE_prog{i}_name` | string (max 16) | Regelname |
| `SWITCHINGRULE_prog{i}_input` | int (1-7) | Digitaleingang (DIN_1-7) |
| `SWITCHINGRULE_prog{i}_type` | int (0-3) | Regeltyp |
| `SWITCHINGRULE_prog{i}_runtime` | string (HHMMSS) | Timer-Dauer |
| `SWITCHINGRULE_prog{i}_blocks_dosage` | int (0/1) | Blockiert Dosierung |
| `SWITCHINGRULE_prog{i}_output_{1-3}` | string | Ausgang |
| `SWITCHINGRULE_prog{i}_output_{1-3}_state` | int (1/2) | EIN/AUS |
| `SWITCHINGRULE_prog{i}_FEM_messageoptions` | int | Benachrichtigung Bitmask |

**Analog-Regeln (ANALOGRULE, 1-4):**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `ANALOGRULE_prog{i}_use` | int (0/1) | Regel aktiv |
| `ANALOGRULE_prog{i}_depending_on` | string | Abh├ñngigkeit (PUMP, SOLAR, ...) |
| `ANALOGRULE_prog{i}_runtime_on` | string (HH:MM) | Zeitfenster Start |
| `ANALOGRULE_prog{i}_runtime_off` | string (HH:MM) | Zeitfenster Ende |
| `ANALOGRULE_prog{i}_sensor` | int (1-5) | ADC-Eingang |
| `ANALOGRULE_prog{i}_logic` | string (>= / <=) | Vergleichsoperator |
| `ANALOGRULE_prog{i}_value` | float | Schaltpunkt EIN |
| `ANALOGRULE_prog{i}_hyst` | float | Schaltpunkt AUS |
| `ANALOGRULE_prog{i}_delay` | int | Verz├Âgerung (sec) |
| `ANALOGRULE_prog{i}_output_{1-3}` | string | Ausgang |
| `ANALOGRULE_prog{i}_output_{1-3}_state` | int (1/2) | EIN/AUS |
| `ANALOGRULE_prog{i}_FEM_messageoptions` | int | Benachrichtigung Bitmask |

### 14.9 Erweiterungsmodule

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `EXTENSION_1_use` | int (0/1) | Erweiterung 1 aktiv |
| `EXTENSION_2_use` | int (0/1) | Erweiterung 2 aktiv |
| `NAMES_EXT{1-2}_{1-8}` | string | Relais-Name |

### 14.10 System & Netzwerk (`system.htm`)

**Netzwerk (CID=1) - speichert ├╝ber `POST /setLanConfig`:**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `NET_dhcp` | int (0/1) | DHCP aktiv (0=nein, 1=ja) |
| `NET_ip` | string (IP) | Statische IP-Adresse |
| `NET_sub` | string (IP) | Subnetzmaske |
| `NET_gate` | string (IP) | Gateway |
| `NET_dns` | string (IP) | DNS-Server |
| `NET_wifi_use` | int (0/1) | WiFi DirectAccess aktiv |
| `NET_wifi_ssid` | string (max 32) | WiFi SSID |
| `NET_wifi_pass` | string (max 32) | WiFi Passwort (min 8) |
| `NET_wifi_channel` | int (1-11) | WiFi Kanal |

**GUI & Zeitzone (CID=2) - speichert ├╝ber `POST /setConfig` bzw. `POST /setTimezone`:**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `GUI_language` | string | Sprachdatei (z.B. "de") |
| `GUI_color` | string | Farbschema (z.B. "blue_white") |
| `GUI_accesslevel` | int (0-3) | Zugriffsstufe |
| `NET_tz` | string | Zeitzone |

**Dienste (CID=3) - verwendet eigene Endpoints:**

| Schl├╝ssel/Endpoint | Typ | Beschreibung |
|-----------|-----|-------------|
| `tunnel_state` | int (0/1) | SSH-Tunnel (via `/enableTUNNEL`, `/disableTUNNEL`) |
| `support_tunnel_state` | int (0/1) | Support-Tunnel (via `/enableSUPPORTTUNNEL`, `/disableSUPPORTTUNNEL`) |
| `proftpd` | int (0/1) | FTP-Server (via `/enableFTP`, `/disableFTP`) |
| `samba` | int (0/1) | SAMBA (via `/enableSAMBA`, `/disableSAMBA`) |
| `sshd` | int (0/1) | SSH-Server (via `/enableSSH`, `/disableSSH`) |
| `shairport` | int (0/1) | AirPlay (via `/enableSHAIRPORT`, `/disableSHAIRPORT`) |
| `USER_pp_accepted` | int (0/1) | Datenschutz akzeptiert |

**System (CID=4) - Read-only:**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `SYSTEM_swversion` | string | Aktuelle Firmware-Version |
| `SYSTEM_availableversion` | string | Verf├╝gbare Version |
| `SYSTEM_updateavailable` | string | "block" = Update verf├╝gbar |
| `SYSTEM_carrierboard_swversion` | string | Carrier-Board Version |

**Backup (CID=5):**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `BACKUP_local_active` | string | SD-Backup (OFF/ALL/0-6 f├╝r Wochentag) |
| `BACKUP_local_time` | string (HH:MM) | SD-Backup Uhrzeit |
| `BACKUP_local_active_usb` | string | USB-Backup (OFF/ALL/0-6) |
| `BACKUP_local_time_usb` | string (HH:MM) | USB-Backup Uhrzeit |
| `BACKUP_cloud_active` | string | Cloud-Backup (OFF/0-6) |
| `BACKUP_cloud_time` | string (HH:MM) | Cloud-Backup Uhrzeit |
| `BACKUP_cloud_user` | string | Cloud-Benutzername |
| `BACKUP_is_usb_present` | string (YES/NO) | USB-Stick erkannt |

**Namen (CID=6):**

| Schl├╝ssel | Typ | Beschreibung |
|-----------|-----|-------------|
| `NAMES_act{1-18}` | string | Ausgangsname (Pump/Solar/Heater/...) |
| `NAMES_digitalinput{1-12}` | string | Digitaleingang-Name |
| `NAMES_onewire{1-12}` | string | Temperatursensor-Name |
| `NAMES_adc{1-5}` | string | Analogeingang-Name |
| `NAMES_impulscount{1-2}` | string | Impulsz├ñhler-Name |
| `NAMES_omni_dz{0-5}` | string | Omni DC-Name |
| `NAMES_EXT{1-2}_{1-8}` | string | Erweiterungs-Relais-Name |
| `NAMES_defaults_user_selectable` | int | Benutzerdefinierte Namen erlaubt |

---

## 15. Controller-Endpoints (Raw)

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
| `/getRomcodes` | GET | 1-Wire ROM-Codes und Status |
| `/getCloudData` | GET | Cloud-Account-Daten |
| `/getLog?actions&{page}` | GET | Aktions-Log (paginiert, pipe-separated) |
| `/getLog?switching&{page}` | GET | Schalt-Log (paginiert) |
| `/getLog?onewire&{page}` | GET | 1-Wire Sensor-Log (paginiert) |
| `/getLog?downloadActionsLog` | GET | Aktions-Log als Download |
| `/getNotifications?ALL` | GET | Benachrichtigungs-Historie (JSON) |
| `/getServiceStates` | GET | Dienst-Status (Tunnel, FTP, etc.) |
| `/getUpdateState` | GET | Update-Status |
| `/getUpdateHistory` | GET | Update-Historie |
| `/debughttp.htm` | GET | Debug-Seite (Live-Request-Logging) |

### Schreib- und Steuerungs-Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|-------------|
| `/setFunctionManually` | GET | Universeller Schaltbefehl (`?AUSGANG,ACTION,WERT1,WERT2`) |
| `/triggerManualDosing` | POST | Dosierung starten/stoppen (Form-Data) |
| `/setConfig` | POST | Konfiguration schreiben (form-encoded) |
| `/setLanConfig` | POST | Netzwerkkonfiguration (form-encoded) |
| `/setTimezone` | POST | Zeitzone ├ñndern (form-encoded, restart) |
| `/setOutputTestmode` | POST | Testmodus aktivieren |
| `/restoreOldCalib` | POST | Kalibrierung wiederherstellen |
| `/enableTUNNEL` | GET | SSH-Tunnel aktivieren |
| `/disableTUNNEL` | GET | SSH-Tunnel deaktivieren |
| `/enableFTP` | GET | FTP-Server aktivieren |
| `/disableFTP` | GET | FTP-Server deaktivieren |
| `/enableSAMBA` | GET | SAMBA aktivieren |
| `/disableSAMBA` | GET | SAMBA deaktivieren |
| `/enableSUPPORTTUNNEL` | GET | Support-Tunnel aktivieren |
| `/disableSUPPORTTUNNEL` | GET | Support-Tunnel deaktivieren |
| `/initUpdate` | GET | Update starten |
| `/doManualBackup` | GET | Manuelles Backup (SD/USB/Cloud) |
| `/restoreLocalBackup` | GET | Backup-Liste laden |
| `/doLocalRestore` | GET | Backup wiederherstellen |
| `/reboot` | GET | System neustarten |

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

## 16. Response-Format

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

ÔåÆ Deshalb wird f├╝r DOS_* Keys automatisch `/triggerManualDosing` verwendet.

### `/getLog` - Text/Plain (Logdaten)

Pipe-separated Format, paginiert ├╝ber `{page}` (0-basiert).

**Aktions-Log** (`/getLog?actions&0`):
```
2025-05-28|14:30:01|USERACTION|PUMP|MANUELL EIN|Drehzahl 2
2025-05-28|14:31:05|CONTROLTASK|DOS_1_CL|DOSIERUNG GESTARTET|50ml
LOAD_MORE
```

**Schalt-Log** (`/getLog?switching&0`):
```
2025-05-28|14:30:01|PUMP|ON|MANUELL
2025-05-28|14:31:05|DOS_1_CL|ON|AUTO
```

**1-Wire Sensor-Log** (`/getLog?onewire&0`):
```
2025-05-28|14:30:01|SENSOR_POOL|23.5|OK
2025-05-28|14:30:01|SENSOR_SOLAR|45.2|OK
```

Letzte Zeile `LOAD_MORE` = weitere Seiten vorhanden.

**Download**: `/getLog?downloadActionsLog` liefert das komplette Aktions-Log als Datei.

### `/getNotifications` - JSON (Benachrichtigungen)

`/getNotifications?ALL` liefert ein JSON-Objekt mit allen Benachrichtigungen:

```json
{
  "1": {
    "DATE": "2025-05-28",
    "TIME": "14:30:01",
    "SENSOR_ID": "SENSOR_POOL",
    "SENSOR_NAME": "Pool",
    "SENSOR_STATE_OR_VALUE": "ALARM",
    "TYPE": "ALERT",
    "TEXT": "Pool-Temperatur au├ƒerhalb des zul├ñssigen Bereichs!",
    "MAIL_STATE": "SENT",
    "MAIL_API_URL": "",
    "MAIL_API_RESPONSE": "200 OK",
    "SMTP_STATE": "NOT_REQUESTED",
    "PUSH_STATE": "SENT",
    "HTTP_STATE": "NOT_REQUESTED"
  }
}
```

**TYPE**: `WARNING` | `ALERT` | `REMINDER`

**MAIL_STATE / PUSH_STATE / HTTP_STATE**: `NOT_REQUESTED` | `SENT` | `PENDING` | `FAILED` | `REPEATED_ERROR`

### JSON-Endpoints

`/getReadings`, `/getOutputstates`, `/getConfig` etc. liefern JSON.

### Error-Notification (Push vom Controller)

```
# HTTP GET oder POST an konfigurierte URL:
ERRORCODE=0173&SUBJECT=Flockmittel%3A+Kanister+Restinhalt+niedrig
```

---

## 17. Rate Limiting & Priorit├ñten

### Rate Limiter

| Konstante | Wert | Beschreibung |
|-----------|------|-------------|
| `API_RATE_LIMIT_REQUESTS` | 10 | Max Requests pro Window |
| `API_RATE_LIMIT_WINDOW` | 1.0s | Window-Dauer |
| `API_RATE_LIMIT_BURST` | 3 | Burst-Requests erlaubt |
| `API_RATE_LIMIT_RETRY_AFTER` | 0.1s | Wartezeit bei Limit |

### Priorit├ñten (niedriger = wichtiger)

| Priorit├ñt | Wert | Verwendung |
|-----------|------|-----------|
| CRITICAL | 1 | Zustands├ñnderungen, Dosierung |
| HIGH | 2 | Zielwerte |
| NORMAL | 3 | Regul├ñre Datenabfragen |
| LOW | 4 | Historie, Statistiken |

### Circuit Breaker

- **Schwellwert**: 5 aufeinanderfolgende Fehler
- **Half-Open nach**: 60 Sekunden
- **Reset**: Bei erfolgreicher Anfrage

---

## Schaltfunktionen - ├£bersicht

| Key | Label | Unterst├╝tzt |
|-----|-------|------------|
| `PUMP` | Filterpumpe | Speed, Timer |
| `SOLAR` | Solarabsorber | Timer |
| `HEATER` | Heizung | Timer |
| `LIGHT` | Beleuchtung | Color Pulse |
| `ECO` | Eco-Modus | - |
| `BACKWASH` | R├╝cksp├╝lung | Timer |
| `BACKWASHRINSE` | Nachsp├╝lung | Timer |
| `REFILL` | Wassernachspeisung | Timer |
| `PVSURPLUS` | PV-├£berschuss | Speed |
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
