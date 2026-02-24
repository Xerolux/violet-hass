# API-Referenz – Violet Pool Controller HTTP API

> Vollständige Dokumentation der Controller-API-Endpunkte und der Python-Client-Klasse.

---

## Überblick

Der Violet Pool Controller stellt eine **JSON-basierte HTTP API** bereit. Die Integration kommuniziert ausschließlich lokal – keine Cloud, kein externes Netzwerk erforderlich.

```
Home Assistant
    └── VioletPoolAPI (aiohttp)
            ├── GET  /getReadings?ALL        → Alle Sensordaten
            ├── GET  /setFunctionManually    → Outputs steuern
            ├── POST /setConfig              → Konfiguration setzen
            ├── GET  /getConfig              → Konfiguration lesen
            └── GET  /getHistory             → Verlauf abrufen
```

---

## Endpunkte

### GET `/getReadings?ALL`

Liest alle aktuellen Messwerte und Systemzustände.

**Request:**
```
GET http://192.168.1.55/getReadings?ALL
```

**Response (JSON):**
```json
{
  "PUMP": 2,
  "HEATER": 0,
  "SOLAR": 1,
  "WATER_TEMP": 26.5,
  "SOLAR_TEMP": 42.1,
  "PH_VALUE": 7.2,
  "ORP_VALUE": 720,
  "CHLORINE": 0.8,
  "AI1": 0.0,
  "DI1": 0,
  "ERROR_CODE": "0",
  ...
}
```

**Verwendung in HA:**
- Wird alle `scan_interval` Sekunden abgerufen
- Alle Sensor- und Switch-Entities werden aus dieser Antwort aktualisiert

---

### GET `/setFunctionManually`

Steuert Ausgänge und Funktionen des Controllers.

**Request:**
```
GET http://192.168.1.55/setFunctionManually?PUMP=1
GET http://192.168.1.55/setFunctionManually?HEATER=OFF
GET http://192.168.1.55/setFunctionManually?PH_MINUS=AUTO
```

**Parameter:**
| Parameter | Werte | Beschreibung |
|-----------|-------|-------------|
| `PUMP` | `0`–`3`, `ON`, `OFF`, `AUTO` | Pumpenstufe oder Modus |
| `HEATER` | `ON`, `OFF`, `AUTO` | Heizung |
| `SOLAR` | `ON`, `OFF`, `AUTO` | Solar |
| `PH_MINUS` | `ON`, `OFF`, `AUTO` | pH-Senker |
| `PH_PLUS` | `ON`, `OFF`, `AUTO` | pH-Heber |
| `CHLORINE` | `ON`, `OFF`, `AUTO` | Chlor |
| `FLOCCULANT` | `ON`, `OFF`, `AUTO` | Flockmittel |
| `DMX1`–`DMX8` | `ON`, `OFF`, `AUTO` | DMX-Szenen |
| `RELAY1`–`RELAY8` | `ON`, `OFF`, `AUTO` | Erweiterungs-Relais |

**Aktions-Konstanten:**

| Konstante | Wert | Bedeutung |
|-----------|------|-----------|
| `ACTION_ON` | `"1"` | Manuell einschalten |
| `ACTION_OFF` | `"6"` | Manuell ausschalten |
| `ACTION_AUTO` | `"AUTO"` | Auf Automatik setzen |
| `ACTION_ALLON` | `"ALLON"` | Alle ein |
| `ACTION_ALLOFF` | `"ALLOFF"` | Alle aus |
| `ACTION_ALLAUTO` | `"ALLAUTO"` | Alle automatisch |

---

### POST `/setConfig`

Setzt Konfigurationswerte des Controllers.

**Request:**
```
POST http://192.168.1.55/setConfig
Content-Type: application/x-www-form-urlencoded

TARGET_PH=7.2&TARGET_ORP=720
```

**Konfigurierbare Parameter:**
| Parameter | Typ | Bereich | Beschreibung |
|-----------|-----|---------|-------------|
| `TARGET_PH` | float | 6.0–8.0 | pH-Sollwert |
| `TARGET_ORP` | int | 200–900 | ORP-Sollwert in mV |
| `TARGET_MIN_CHLORINE` | float | 0.1–5.0 | Mindest-Chlorgehalt mg/l |
| `TARGET_POOL_TEMP` | float | 10–40 | Pool-Solltemperatur °C |
| `TARGET_SOLAR_TEMP` | float | 20–60 | Solar-Maximaltemperatur °C |

---

### GET `/getConfig`

Liest Konfigurationswerte.

**Request:**
```
GET http://192.168.1.55/getConfig?TARGET_PH,TARGET_ORP
```

**Response:**
```json
{
  "TARGET_PH": 7.2,
  "TARGET_ORP": 720
}
```

---

### GET `/getHistory`

Ruft Verlaufsdaten ab.

**Request:**
```
GET http://192.168.1.55/getHistory
```

---

### GET `/getCalibHistory`

Kalibrierungsverlauf abrufen.

**Request:**
```
GET http://192.168.1.55/getCalibHistory
```

**Response:** JSON-Array mit Kalibrierungseinträgen inklusive Datum, Sensortyp und Kalibrierwerten.

---

### GET `/setOutputTestmode`

Diagnose-Modus für Ausgänge.

**Request:**
```
GET http://192.168.1.55/setOutputTestmode?output=PUMP&mode=ON&duration=120
```

**Parameter:**
| Parameter | Beschreibung |
|-----------|-------------|
| `output` | Ausgangs-Bezeichner (PUMP, HEATER, etc.) |
| `mode` | `SWITCH`, `ON`, oder `OFF` |
| `duration` | Testdauer in Sekunden (1–900) |

---

## Python Client: `VioletPoolAPI`

### Initialisierung

```python
from custom_components.violet_pool_controller.api import VioletPoolAPI
import aiohttp

async with aiohttp.ClientSession() as session:
    api = VioletPoolAPI(
        host="192.168.1.55",
        session=session,
        username="admin",        # Optional
        password="secret",       # Optional
        use_ssl=False,           # HTTPS verwenden
        verify_ssl=True,         # Zertifikat verifizieren
        timeout=10,              # Sekunden
        max_retries=3,           # Wiederholungsversuche
    )
```

### Methoden

#### `get_readings()`

```python
data: dict = await api.get_readings()
# Gibt alle aktuellen Messwerte zurück
```

#### `set_function_manually(key, value)`

```python
await api.set_function_manually("PUMP", "1")
await api.set_function_manually("HEATER", "OFF")
await api.set_function_manually("PH_MINUS", "AUTO")
```

#### `set_config(params)`

```python
await api.set_config({"TARGET_PH": 7.2, "TARGET_ORP": 720})
```

#### `get_config(keys)`

```python
config = await api.get_config(["TARGET_PH", "TARGET_ORP"])
```

#### `set_output_testmode(output, mode, duration)`

```python
await api.set_output_testmode(
    output="PUMP",
    mode="ON",
    duration=120
)
```

---

## Rate Limiting

Alle API-Aufrufe gehen durch den globalen Rate-Limiter:

```python
from custom_components.violet_pool_controller.utils_rate_limiter import get_global_rate_limiter

limiter = get_global_rate_limiter()
# Token-Bucket-Algorithmus
# Verhindert Controller-Überlastung
```

### Prioritäts-Stufen

| Priorität | Konstante | Verwendung |
|-----------|-----------|-----------|
| Hoch | `API_PRIORITY_HIGH` | Manuelle Steuerungsbefehle |
| Normal | `API_PRIORITY_NORMAL` | Reguläres Polling |
| Niedrig | `API_PRIORITY_LOW` | Hintergrund-Aufgaben |

---

## Fehlerbehandlung

### Exceptions

| Exception | Beschreibung |
|-----------|-------------|
| `VioletPoolAPIError` | Allgemeiner API-Fehler |
| `aiohttp.ClientTimeout` | Timeout überschritten |
| `aiohttp.ClientConnectionError` | Verbindung fehlgeschlagen |
| `json.JSONDecodeError` | Ungültige JSON-Antwort |

### Retry-Logik

```
Versuch 1:  Sofort
Versuch 2:  Exponentielles Backoff
Versuch 3:  Exponentielles Backoff
...
Max: DEFAULT_RETRY_ATTEMPTS (Standard: 3)
```

---

## Timeout-Konfiguration

```
Gesamt-Timeout:       DEFAULT_TIMEOUT_DURATION (Standard: 10s)
Verbindungs-Timeout:  80% des Gesamt-Timeouts (8s)
Socket-Timeout:       80% des Gesamt-Timeouts (8s)
```

---

## Authentifizierung

Der Controller unterstützt HTTP Basic Authentication:

```
Authorization: Basic base64(username:password)
```

Wenn kein Username/Passwort konfiguriert: Kein Auth-Header wird gesendet.

---

## SSL/TLS

```python
# Vollständige Verifikation (Standard)
api = VioletPoolAPI(host=..., use_ssl=True, verify_ssl=True)

# Selbstsigniertes Zertifikat (Heimnetz)
api = VioletPoolAPI(host=..., use_ssl=True, verify_ssl=False)

# Kein SSL (HTTP)
api = VioletPoolAPI(host=..., use_ssl=False)
```

---

## Daten-Typen in API-Antworten

| Datentyp | Beispielwert | Beschreibung |
|----------|-------------|-------------|
| Integer State | `2` | Device State 0–6 |
| Float | `26.5` | Temperatur, pH, etc. |
| String State | `"3\|PUMP_ANTI_FREEZE"` | Composite State |
| String | `"RELEASED"` | Digital-Eingang Status |
| Error Code | `"120"` | Fehlercode als String |

---

## Sensor-Schlüssel Referenz

Wichtige Schlüssel aus `/getReadings?ALL`:

| Schlüssel | Einheit | Beschreibung |
|-----------|---------|-------------|
| `WATER_TEMP` | °C | Beckenwasser-Temperatur |
| `SOLAR_TEMP` | °C | Solar-Kollektor Temperatur |
| `AIR_TEMP` | °C | Lufttemperatur |
| `PH_VALUE` | pH | pH-Wert |
| `ORP_VALUE` | mV | Redox-Potential |
| `CHLORINE` | mg/l | Chlorgehalt |
| `CONDUCTIVITY` | µS/cm | Leitfähigkeit |
| `PUMP` | 0–6 | Pumpenzustand |
| `HEATER` | 0–6 | Heizungszustand |
| `SOLAR` | 0–6 | Solarzustand |
| `DI1`–`DI8` | 0/1 | Digitaleingänge |
| `AI1`–`AI8` | V/mA | Analogeingänge |
| `ERROR_CODE` | string | Aktueller Fehlercode |

---

*Zurück: [Testing](Testing) | Weiter: [Changelog](Changelog)*
