# Violet Pool Controller – Vollständige API-Referenz

> **Revision:** 14-07-2024 (getReadings Spec) · Stand Integration: 1.0.7-alpha.3  
> Alle Werte die gelesen (`GET /getReadings?ALL`) und geschrieben (`GET /setFunctionManually`, `POST /setConfig`) werden können.

---

## Inhaltsverzeichnis

1. [LESEN – Alle Sensoren / Werte](#lesen--alle-sensoren--werte)
   - [Systeminfos](#1-systeminfos)
   - [Analogsensoren](#2-analogsensoren)
   - [Impuls-Eingänge](#3-impuls-eingänge)
   - [Temperatursensoren (1-Wire)](#4-temperatursensoren-1-wire)
   - [Wasserparameter](#5-wasserparameter)
   - [Dosierung – Chlor (DOS_1_CL)](#6-dosierung--chlor-dos_1_cl)
   - [Dosierung – Elektrolyse (DOS_2_ELO)](#7-dosierung--elektrolyse-dos_2_elo)
   - [Dosierung – pH- (DOS_4_PHM)](#8-dosierung--ph--dos_4_phm)
   - [Dosierung – pH+ (DOS_5_PHP)](#9-dosierung--ph-dos_5_php)
   - [Dosierung – Flockmittel (DOS_6_FLOC)](#10-dosierung--flockmittel-dos_6_floc)
   - [Digitale Eingänge (INPUT 1–12)](#11-digitale-eingänge-input-112)
   - [Kanister-Leersensoren](#12-kanister-leersensoren)
   - [Schaltregeln (1–7)](#13-schaltregeln-17)
   - [DMX-Lichtszenen (1–12)](#14-dmx-lichtszenen-112)
   - [Ausgänge – Pumpe](#15-ausgänge--pumpe)
   - [Ausgänge – Pumpen-Stufen RPM 0–3](#16-ausgänge--pumpen-stufen-rpm-03)
   - [Ausgänge – Solar](#17-ausgänge--solar)
   - [Ausgänge – Heizung](#18-ausgänge--heizung)
   - [Ausgänge – Beleuchtung](#19-ausgänge--beleuchtung)
   - [Ausgänge – Nachfüllung](#20-ausgänge--nachfüllung)
   - [Ausgänge – Eco-Modus](#21-ausgänge--eco-modus)
   - [Ausgänge – Rückspülung](#22-ausgänge--rückspülung)
   - [Ausgänge – Rückspülnachspülung](#23-ausgänge--rückspülnachspülung)
   - [Abdeckung (Cover)](#24-abdeckung-cover)
   - [Erweiterungsmodul 1 (EXT1_1–EXT1_8)](#25-erweiterungsmodul-1-ext1_1ext1_8)
   - [Erweiterungsmodul 2 (EXT2_1–EXT2_8)](#26-erweiterungsmodul-2-ext2_1ext2_8)
   - [Überlaufbehälter-Zustände](#27-überlaufbehälter-zustände)
   - [Rückspül-Zusatzinfos](#28-rückspül-zusatzinfos)
   - [Bade-KI (Bathing AI)](#29-bade-ki-bathing-ai)
   - [PV-Überschuss](#30-pv-überschuss)
2. [SCHREIBEN – Steuerung & Services](#schreiben--steuerung--services)
   - [Schalter (Switch) – ON / OFF / AUTO](#schalter-switch--on--off--auto)
   - [Modus-Auswahl (Select)](#modus-auswahl-select)
   - [Sollwerte (Number)](#sollwerte-number)
   - [Klima (Climate)](#klima-climate)
   - [Abdeckung (Cover)](#abdeckung-cover-steuerung)
   - [Services / Aktionen](#services--aktionen)
3. [Status-Codes Ausgänge](#status-codes-ausgänge)
4. [Zeitstempel-Formate](#zeitstempel-formate)

---

## LESEN – Alle Sensoren / Werte

**Endpunkt:** `GET http://<IP>/getReadings?ALL`  
**Antwort:** JSON-Objekt mit allen Schlüssel-Wert-Paaren

---

### 1. Systeminfos

| Schlüssel | Beschreibung | Format | Einheit |
|-----------|-------------|--------|---------|
| `date` | Systemdatum (inkl. Zeitzone) | TT.MM.YYYY | – |
| `time` | Systemzeit (inkl. Zeitzone) | HH:MM:SS | – |
| `CPU_TEMP` | CPU-Temperatur (System) | FLOAT | °C |
| `CPU_TEMP_CARRIER` | CPU-Temperatur (Carrier-Board) | FLOAT | °C |
| `CPU_UPTIME` | Systemlaufzeit seit letztem Boot | DD HH MM | – |
| `SYSTEM_MEMORY` | Gesamter Systemspeicher belegt | FLOAT | MB |
| `SYSTEM_memoryusage` | Speicher belegt durch App | FLOAT | MB |
| `SYSTEM_dosagemodule_cpu_temperature` | CPU-Temperatur Dosiermodul | FLOAT | °C |
| `SW_VERSION` | Software-Version VIOLET App | STRING (X.X.X) | – |
| `SW_VERSION_CARRIER` | Firmware-Version VIOLET Carrier | STRING (X.X.X) | – |

---

### 2. Analogsensoren

| Schlüssel | Beschreibung | Format | Einheit |
|-----------|-------------|--------|---------|
| `ADC1_value` | Analogsensor 1 (Filterdruck) | FLOAT | bar |
| `ADC2_value` | Analogsensor 2 (Überlaufbehälter-Füllstand) | FLOAT | cm |
| `ADC3_value` | Analogsensor 3 (4–20mA) | FLOAT | m³/h |
| `ADC4_value` | Analogsensor 4 (4–20mA) | FLOAT | – |
| `ADC5_value` | Analogsensor 5 (0–10V) | FLOAT | V |

> Dezimalstellen werden gemäß GUI-Konfiguration geliefert.

---

### 3. Impuls-Eingänge

| Schlüssel | Beschreibung | Format | Einheit |
|-----------|-------------|--------|---------|
| `IMP1_value` | Impuls-Eingang 1 (Dosieranströmung) | FLOAT | cm/s (Echo) oder 0.0/1.0 (Näherungsschalter) |
| `IMP2_value` | Impuls-Eingang 2 (Pumpen-Durchfluss) | FLOAT | m³/h |

> Bei „Echo-Sensor": gemessener Wert in cm/sec.  
> Bei „Näherungsschalter": `0.0` = offen, `1.0` = geschlossen.

---

### 4. Temperatursensoren (1-Wire)

**Alle 12 Sensoren folgen demselben Muster** – Nummern 1 bis 12:

| Schlüssel | Beschreibung | Format | Einheit |
|-----------|-------------|--------|---------|
| `onewire{N}_state` | Fehlerstatus des Sensors | STRING | – |
| `onewire{N}_rcode` | ROM-Code des Sensors | STRING | – |
| `onewire{N}_value` | Aktueller Messwert | FLOAT | °C |
| `onewire{N}_value_max` | Heutiger Maximalwert (Reset 00:00) | FLOAT | °C |
| `onewire{N}_value_min` | Heutiger Minimalwert (Reset 00:00) | FLOAT | °C |

**Mögliche `_state` Werte:**
- `OK` – Sensor in Ordnung
- `CRC_FAULT` – Protokollfehler
- `DATA_MISSMATCH` – Protokollfehler
- `NOT_CONNECTED` – Konfiguriert, aber nicht angeschlossen
- `NO_SENSOR_CONFIGURED` – Kein Sensor konfiguriert

**Vollständige Schlüsselliste (N = 1–12):**

| N | Sensor (DE) | `_value` | `_value_max` | `_value_min` |
|---|------------|----------|-------------|-------------|
| 1 | Wassertemperatur | `onewire1_value` | `onewire1_value_max` | `onewire1_value_min` |
| 2 | Außentemperatur | `onewire2_value` | `onewire2_value_max` | `onewire2_value_min` |
| 3 | Solarabsorber | `onewire3_value` | `onewire3_value_max` | `onewire3_value_min` |
| 4 | Absorber-Rücklauf | `onewire4_value` | `onewire4_value_max` | `onewire4_value_min` |
| 5 | Wärmetauscher Einlauf | `onewire5_value` | `onewire5_value_max` | `onewire5_value_min` |
| 6 | Wärmetauscher Auslauf | `onewire6_value` | `onewire6_value_max` | `onewire6_value_min` |
| 7 | Temperatursensor 7 | `onewire7_value` | `onewire7_value_max` | `onewire7_value_min` |
| 8 | Temperatursensor 8 | `onewire8_value` | `onewire8_value_max` | `onewire8_value_min` |
| 9 | Temperatursensor 9 | `onewire9_value` | `onewire9_value_max` | `onewire9_value_min` |
| 10 | Temperatursensor 10 | `onewire10_value` | `onewire10_value_max` | `onewire10_value_min` |
| 11 | Temperatursensor 11 | `onewire11_value` | `onewire11_value_max` | `onewire11_value_min` |
| 12 | Temperatursensor 12 | `onewire12_value` | `onewire12_value_max` | `onewire12_value_min` |

---

### 5. Wasserparameter

| Schlüssel | Beschreibung | Format | Einheit |
|-----------|-------------|--------|---------|
| `orp_value` | Aktueller ORP-Wert | FLOAT (1 Dez.) | mV |
| `orp_value_max` | Heutiges Maximum (Reset 00:00) | FLOAT | mV |
| `orp_value_min` | Heutiges Minimum (Reset 00:00) | FLOAT | mV |
| `pH_value` | Aktueller pH-Wert | FLOAT (2 Dez.) | – |
| `pH_value_max` | Heutiges Maximum (Reset 00:00) | FLOAT | – |
| `pH_value_min` | Heutiges Minimum (Reset 00:00) | FLOAT | – |
| `pot_value` | Aktueller Chlorgehalt | FLOAT (2 Dez.) | mg/l |
| `pot_value_max` | Heutiges Maximum (Reset 00:00) | FLOAT | mg/l |
| `pot_value_min` | Heutiges Minimum (Reset 00:00) | FLOAT | mg/l |

---

### 6. Dosierung – Chlor (DOS_1_CL)

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `DOS_1_CL` | Aktueller Zustand Chlor-Dosierausgang | INTEGER (0–6) |
| `DOS_1_CL_DAILY_DOSING_AMOUNT_ML` | Heutige Dosiermenge in ml (Reset 00:00) | INTEGER |
| `DOS_1_CL_LAST_CAN_RESET` | Zeitstempel letzter Kanister-Reset | Unix Epoch (ms) |
| `DOS_1_CL_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `DOS_1_CL_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `DOS_1_CL_RUNTIME` | Tageslaufzeit Chlor-Dosierung | HH:MM:SS |
| `DOS_1_CL_STATE` | Liste möglicher Blockierungen | LIST\[STRING\] |
| `DOS_1_CL_TOTAL_CAN_AMOUNT_ML` | Verbleibende Kanistermenge in ml | INTEGER |
| `DOS_1_CL_TYPE` | Regelungsart (0 = ORP, 1 = ORP+Cl) | INTEGER |
| `DOS_1_CL_USE` | Aktiviert in Systemkonfig (0/1) | INTEGER |

**Mögliche `DOS_1_CL_STATE` Einträge:**
`BLOCKED_BY_OMNI_POS`, `BLOCKED_BY_MAX_AMOUNT`, `BLOCKED_BY_OUTSIDE_TEMP`, `BLOCKED_BY_TRESHOLDS`, `BLOCKED_BY_PUMP`, `BLOCKED_BY_FLOW`, `WAITING_FOR_PUMP`, `WAITING_FOR_FLOW`, `DOSING`, `DOSING_PAUSED`, `MANUAL_DOSING`

---

### 7. Dosierung – Elektrolyse (DOS_2_ELO)

Gleiche Schlüssel wie DOS_1_CL, Präfix `DOS_2_ELO_`:

| Schlüssel | Beschreibung |
|-----------|-------------|
| `DOS_2_ELO` | Aktueller Zustand Elektrolyse-Ausgang |
| `DOS_2_ELO_DAILY_DOSING_AMOUNT_ML` | Heutige Dosiermenge (ml) |
| `DOS_2_ELO_LAST_CAN_RESET` | Zeitstempel letzter Kanister-Reset |
| `DOS_2_ELO_LAST_OFF` | Zeitstempel letztes Ausschalten |
| `DOS_2_ELO_LAST_ON` | Zeitstempel letztes Einschalten |
| `DOS_2_ELO_RUNTIME` | Tageslaufzeit |
| `DOS_2_ELO_STATE` | Liste möglicher Blockierungen |
| `DOS_2_ELO_TOTAL_CAN_AMOUNT_ML` | Verbleibende Kanistermenge (ml) |
| `DOS_2_ELO_TYPE` | Regelungsart |
| `DOS_2_ELO_USE` | Aktiviert (0/1) |

---

### 8. Dosierung – pH- (DOS_4_PHM)

Gleiche Schlüssel wie DOS_1_CL, Präfix `DOS_4_PHM_`:

| Schlüssel | Beschreibung |
|-----------|-------------|
| `DOS_4_PHM` | Aktueller Zustand pH- Dosierausgang |
| `DOS_4_PHM_DAILY_DOSING_AMOUNT_ML` | Heutige Dosiermenge (ml) |
| `DOS_4_PHM_LAST_CAN_RESET` | Zeitstempel letzter Kanister-Reset |
| `DOS_4_PHM_LAST_OFF` | Zeitstempel letztes Ausschalten |
| `DOS_4_PHM_LAST_ON` | Zeitstempel letztes Einschalten |
| `DOS_4_PHM_RUNTIME` | Tageslaufzeit |
| `DOS_4_PHM_STATE` | Liste möglicher Blockierungen |
| `DOS_4_PHM_TOTAL_CAN_AMOUNT_ML` | Verbleibende Kanistermenge (ml) |
| `DOS_4_PHM_TYPE` | Regelungsart |
| `DOS_4_PHM_USE` | Aktiviert (0/1) |

---

### 9. Dosierung – pH+ (DOS_5_PHP)

Gleiche Schlüssel wie DOS_1_CL, Präfix `DOS_5_PHP_`:

| Schlüssel | Beschreibung |
|-----------|-------------|
| `DOS_5_PHP` | Aktueller Zustand pH+ Dosierausgang |
| `DOS_5_PHP_DAILY_DOSING_AMOUNT_ML` | Heutige Dosiermenge (ml) |
| `DOS_5_PHP_LAST_CAN_RESET` | Zeitstempel letzter Kanister-Reset |
| `DOS_5_PHP_LAST_OFF` | Zeitstempel letztes Ausschalten |
| `DOS_5_PHP_LAST_ON` | Zeitstempel letztes Einschalten |
| `DOS_5_PHP_RUNTIME` | Tageslaufzeit |
| `DOS_5_PHP_STATE` | Liste möglicher Blockierungen |
| `DOS_5_PHP_TOTAL_CAN_AMOUNT_ML` | Verbleibende Kanistermenge (ml) |
| `DOS_5_PHP_TYPE` | Regelungsart |
| `DOS_5_PHP_USE` | Aktiviert (0/1) |

---

### 10. Dosierung – Flockmittel (DOS_6_FLOC)

Gleiche Schlüssel wie DOS_1_CL, Präfix `DOS_6_FLOC_`:

| Schlüssel | Beschreibung |
|-----------|-------------|
| `DOS_6_FLOC` | Aktueller Zustand Flockmittel-Ausgang |
| `DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML` | Heutige Dosiermenge (ml) |
| `DOS_6_FLOC_LAST_CAN_RESET` | Zeitstempel letzter Kanister-Reset |
| `DOS_6_FLOC_LAST_OFF` | Zeitstempel letztes Ausschalten |
| `DOS_6_FLOC_LAST_ON` | Zeitstempel letztes Einschalten |
| `DOS_6_FLOC_RUNTIME` | Tageslaufzeit |
| `DOS_6_FLOC_STATE` | Liste möglicher Blockierungen |
| `DOS_6_FLOC_TOTAL_CAN_AMOUNT_ML` | Verbleibende Kanistermenge (ml) |
| `DOS_6_FLOC_TYPE` | Regelungsart |
| `DOS_6_FLOC_USE` | Aktiviert (0/1) |

---

### 11. Digitale Eingänge (INPUT 1–12)

| Schlüssel | Beschreibung | Format | Werte |
|-----------|-------------|--------|-------|
| `INPUT1` | Zustand Digitaleingang 1 | INTEGER | `0` = offen / `1` = geschlossen |
| `INPUT2` | Zustand Digitaleingang 2 | INTEGER | s.o. |
| `INPUT3` | Zustand Digitaleingang 3 | INTEGER | s.o. |
| `INPUT4` | Zustand Digitaleingang 4 | INTEGER | s.o. |
| `INPUT5` | Zustand Digitaleingang 5 | INTEGER | s.o. |
| `INPUT6` | Zustand Digitaleingang 6 | INTEGER | s.o. |
| `INPUT7` | Zustand Digitaleingang 7 | INTEGER | s.o. |
| `INPUT8` | Zustand Digitaleingang 8 | INTEGER | s.o. |
| `INPUT9` | Zustand Digitaleingang 9 | INTEGER | s.o. |
| `INPUT10` | Zustand Digitaleingang 10 | INTEGER | s.o. |
| `INPUT11` | Zustand Digitaleingang 11 | INTEGER | s.o. |
| `INPUT12` | Zustand Digitaleingang 12 | INTEGER | s.o. |

---

### 12. Kanister-Leersensoren

| Schlüssel | Beschreibung | Format | Werte |
|-----------|-------------|--------|-------|
| `INPUT_CE1` | Kanister-Leersensor 1 | INTEGER | `0` = offen / `1` = geschlossen |
| `INPUT_CE2` | Kanister-Leersensor 2 | INTEGER | s.o. |
| `INPUT_CE3` | Kanister-Leersensor 3 | INTEGER | s.o. |
| `INPUT_CE4` | Kanister-Leersensor 4 | INTEGER | s.o. |

---

### 13. Schaltregeln (1–7)

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_1` | Zustand Schaltregel 1 | INTEGER |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_2` | Zustand Schaltregel 2 | INTEGER |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_3` | Zustand Schaltregel 3 | INTEGER |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_4` | Zustand Schaltregel 4 | INTEGER |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_5` | Zustand Schaltregel 5 | INTEGER |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_6` | Zustand Schaltregel 6 | INTEGER |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_7` | Zustand Schaltregel 7 | INTEGER |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH1` | Verbleibende Laufzeit Regel 1 (s) | FLOAT |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH2` | Verbleibende Laufzeit Regel 2 (s) | FLOAT |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH3` | Verbleibende Laufzeit Regel 3 (s) | FLOAT |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH4` | Verbleibende Laufzeit Regel 4 (s) | FLOAT |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH5` | Verbleibende Laufzeit Regel 5 (s) | FLOAT |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH6` | Verbleibende Laufzeit Regel 6 (s) | FLOAT |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH7` | Verbleibende Laufzeit Regel 7 (s) | FLOAT |

**Mögliche Zustands-Codes (RULE):**
- `0` = Inaktiv
- `1` = Aktiv
- `5` = Blockiert (durch Regel)
- `6` = Blockiert (manuell)

> Stopwatch: negativer Wert = Laufzeit abgelaufen.

---

### 14. DMX-Lichtszenen (1–12)

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `DMX_SCENE1` | Zustand DMX-Lichtszene 1 | INTEGER |
| `DMX_SCENE2` | Zustand DMX-Lichtszene 2 | INTEGER |
| `DMX_SCENE3` | Zustand DMX-Lichtszene 3 | INTEGER |
| `DMX_SCENE4` | Zustand DMX-Lichtszene 4 | INTEGER |
| `DMX_SCENE5` | Zustand DMX-Lichtszene 5 | INTEGER |
| `DMX_SCENE6` | Zustand DMX-Lichtszene 6 | INTEGER |
| `DMX_SCENE7` | Zustand DMX-Lichtszene 7 | INTEGER |
| `DMX_SCENE8` | Zustand DMX-Lichtszene 8 | INTEGER |
| `DMX_SCENE9` | Zustand DMX-Lichtszene 9 | INTEGER |
| `DMX_SCENE10` | Zustand DMX-Lichtszene 10 | INTEGER |
| `DMX_SCENE11` | Zustand DMX-Lichtszene 11 | INTEGER |
| `DMX_SCENE12` | Zustand DMX-Lichtszene 12 | INTEGER |

**Mögliche Zustands-Codes:**
- `0` = AUTO (nicht an)
- `1` = AUTO (an)
- `4` = MANUELL (an)
- `6` = MANUELL (aus)

---

### 15. Ausgänge – Pumpe

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `PUMP` | Aktueller Zustand Pumpen-Ausgang | INTEGER (0–6) |
| `PUMP_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `PUMP_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `PUMP_RUNTIME` | Tageslaufzeit | HH MM SS |

---

### 16. Ausgänge – Pumpen-Stufen RPM 0–3

Gleiche Struktur für alle 4 Stufen (N = 0, 1, 2, 3):

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `PUMP_RPM_0` | Zustand PUMP_STOP (Stufe 0) | INTEGER (0–6) |
| `PUMP_RPM_0_LAST_OFF` | Zeitstempel letztes Ausschalten | – |
| `PUMP_RPM_0_LAST_ON` | Zeitstempel letztes Einschalten | – |
| `PUMP_RPM_0_RUNTIME` | Tageslaufzeit | HH MM SS |
| `PUMP_RPM_1` | Zustand Pumpe Stufe 1 | INTEGER (0–6) |
| `PUMP_RPM_1_LAST_OFF` | Zeitstempel letztes Ausschalten | – |
| `PUMP_RPM_1_LAST_ON` | Zeitstempel letztes Einschalten | – |
| `PUMP_RPM_1_RUNTIME` | Tageslaufzeit | HH MM SS |
| `PUMP_RPM_2` | Zustand Pumpe Stufe 2 | INTEGER (0–6) |
| `PUMP_RPM_2_LAST_OFF` | Zeitstempel letztes Ausschalten | – |
| `PUMP_RPM_2_LAST_ON` | Zeitstempel letztes Einschalten | – |
| `PUMP_RPM_2_RUNTIME` | Tageslaufzeit | HH MM SS |
| `PUMP_RPM_3` | Zustand Pumpe Stufe 3 | INTEGER (0–6) |
| `PUMP_RPM_3_LAST_OFF` | Zeitstempel letztes Ausschalten | – |
| `PUMP_RPM_3_LAST_ON` | Zeitstempel letztes Einschalten | – |
| `PUMP_RPM_3_RUNTIME` | Tageslaufzeit | HH MM SS |

> `_LAST_OFF` und `_LAST_ON` bei RPM-Stufen werden immer als `00:00:00` geliefert (nicht genutzt).

---

### 17. Ausgänge – Solar

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `SOLAR` | Aktueller Zustand Solar-Ausgang | INTEGER (0–6) |
| `SOLAR_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `SOLAR_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `SOLAR_RUNTIME` | Tageslaufzeit | HH MM SS |

---

### 18. Ausgänge – Heizung

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `HEATER` | Aktueller Zustand Heizungs-Ausgang | INTEGER (0–6) |
| `HEATER_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `HEATER_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `HEATER_RUNTIME` | Tageslaufzeit | HH MM SS |
| `HEATER_POSTRUN_TIME` | Verbleibende Nachlaufzeit in Sekunden | FLOAT oder `NONE` |

---

### 19. Ausgänge – Beleuchtung

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `LIGHT` | Aktueller Zustand Beleuchtungs-Ausgang | INTEGER (0–6) |
| `LIGHT_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `LIGHT_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `LIGHT_RUNTIME` | Tageslaufzeit | HH MM SS |

---

### 20. Ausgänge – Nachfüllung

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `REFILL` | Aktueller Zustand Nachfüll-Ausgang | INTEGER (0–6) |
| `REFILL_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `REFILL_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `REFILL_RUNTIME` | Tageslaufzeit | HH MM SS |

---

### 21. Ausgänge – Eco-Modus

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `ECO` | Aktueller Zustand Eco-Modus-Ausgang | INTEGER (0–6) |
| `ECO_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `ECO_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `ECO_RUNTIME` | Tageslaufzeit | HH MM SS |

---

### 22. Ausgänge – Rückspülung

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `BACKWASH` | Zustand Rückspül-Ausgang | INTEGER (0–6) |
| `BACKWASH_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `BACKWASH_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `BACKWASH_RUNTIME` | Tageslaufzeit | HH MM SS |

---

### 23. Ausgänge – Rückspülnachspülung

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `BACKWASHRINSE` | Zustand Nachspül-Ausgang | INTEGER (0–6) |
| `BACKWASHRINSE_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `BACKWASHRINSE_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `BACKWASHRINSE_RUNTIME` | Tageslaufzeit | HH MM SS |

---

### 24. Abdeckung (Cover)

| Schlüssel | Beschreibung | Format | Mögliche Werte |
|-----------|-------------|--------|----------------|
| `COVER_STATE` | Aktueller Abdeckungszustand | STRING | `OPEN`, `CLOSED`, `OPENING`, `CLOSING`, `STOPPED` |

---

### 25. Erweiterungsmodul 1 (EXT1_1–EXT1_8)

Gleiche Struktur für alle 8 Relais (N = 1–8):

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `EXT1_1` | Zustand Erweiterung 1.1 | INTEGER (0–6) |
| `EXT1_1_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT1_1_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT1_1_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT1_2` | Zustand Erweiterung 1.2 | INTEGER (0–6) |
| `EXT1_2_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT1_2_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT1_2_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT1_3` | Zustand Erweiterung 1.3 | INTEGER (0–6) |
| `EXT1_3_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT1_3_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT1_3_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT1_4` | Zustand Erweiterung 1.4 | INTEGER (0–6) |
| `EXT1_4_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT1_4_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT1_4_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT1_5` | Zustand Erweiterung 1.5 | INTEGER (0–6) |
| `EXT1_5_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT1_5_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT1_5_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT1_6` | Zustand Erweiterung 1.6 | INTEGER (0–6) |
| `EXT1_6_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT1_6_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT1_6_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT1_7` | Zustand Erweiterung 1.7 | INTEGER (0–6) |
| `EXT1_7_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT1_7_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT1_7_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT1_8` | Zustand Erweiterung 1.8 | INTEGER (0–6) |
| `EXT1_8_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT1_8_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT1_8_RUNTIME` | Tageslaufzeit | HH MM SS |

---

### 26. Erweiterungsmodul 2 (EXT2_1–EXT2_8)

Gleiche Struktur wie Modul 1, Präfix `EXT2_`:

| Schlüssel | Beschreibung | Format |
|-----------|-------------|--------|
| `EXT2_1` | Zustand Erweiterung 2.1 | INTEGER (0–6) |
| `EXT2_1_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT2_1_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT2_1_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT2_2` | Zustand Erweiterung 2.2 | INTEGER (0–6) |
| `EXT2_2_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT2_2_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT2_2_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT2_3` | Zustand Erweiterung 2.3 | INTEGER (0–6) |
| `EXT2_3_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT2_3_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT2_3_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT2_4` | Zustand Erweiterung 2.4 | INTEGER (0–6) |
| `EXT2_4_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT2_4_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT2_4_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT2_5` | Zustand Erweiterung 2.5 | INTEGER (0–6) |
| `EXT2_5_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT2_5_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT2_5_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT2_6` | Zustand Erweiterung 2.6 | INTEGER (0–6) |
| `EXT2_6_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT2_6_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT2_6_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT2_7` | Zustand Erweiterung 2.7 | INTEGER (0–6) |
| `EXT2_7_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT2_7_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT2_7_RUNTIME` | Tageslaufzeit | HH MM SS |
| `EXT2_8` | Zustand Erweiterung 2.8 | INTEGER (0–6) |
| `EXT2_8_LAST_OFF` | Zeitstempel letztes Ausschalten | Unix Epoch (s) |
| `EXT2_8_LAST_ON` | Zeitstempel letztes Einschalten | Unix Epoch (s) |
| `EXT2_8_RUNTIME` | Tageslaufzeit | HH MM SS |

---

### 27. Überlaufbehälter-Zustände

| Schlüssel | Beschreibung | Format | Werte |
|-----------|-------------|--------|-------|
| `OVERFLOW_DRYRUN_STATE` | Trockenlauf erkannt (Pumpe gestoppt) | STRING | `ON` / `OFF` |
| `OVERFLOW_OVERFILL_STATE` | Überfüllung erkannt (Pumpe eingeschaltet) | STRING | `ON` / `OFF` |
| `OVERFLOW_REFILL_STATE` | Nachfüllung ausgelöst | STRING | `ON` / `OFF` |

---

### 28. Rückspül-Zusatzinfos

| Schlüssel | Beschreibung | Format | Details |
|-----------|-------------|--------|---------|
| `BACKWASH_DELAY_RUNNING` | Rückspülung verzögert (z.B. manuelle Pumpe) | STRING | `NO` = kein Delay / `YES` = verzögert |
| `BACKWASH_DELAY_TIMESTAMP` | Zeitstempel seit wann Delay aktiv | Unix Epoch (s) | `0` wenn kein Timer |
| `BACKWASH_LAST_AUTO_RUN` | Zeitstempel letzter Auto-Rückspülvorgang | Unix Epoch (s) | – |
| `BACKWASH_LAST_MANUAL_RUN` | Zeitstempel letzter manueller Rückspülvorgang | Unix Epoch (s) | – |
| `BACKWASH_OMNI_MOVING` | OMNI-Ventil in Bewegung | STRING | `YES` / `NO` |
| `BACKWASH_OMNI_STATE` | Fehlerstatus OMNI-Ventil | STRING | `OK` / `BLOCKED_BY_Z1Z2` |
| `BACKWASH_STEP` | Aktueller Schritt im Rückspülprozess | INTEGER | 0–6 |
| `BACKWASH_STATE` | Aktueller Rückspülzustand | STRING | Siehe unten |

**Mögliche `BACKWASH_STATE` Werte:**
```
NEXT_BW_IN 2          → verbleibende Tage bis zur nächsten Rückspülung
BW_DELAYED_SINCE ...  → Rückspülung verzögert seit
BW_RUNNING            → Rückspülprozess gestartet
BW_RUNNING_SINCE 123  → Rückspülung läuft seit N Sekunden (Pumpe EIN)
BWR_RUNNING_SINCE 34  → Nachspülung läuft seit N Sekunden (Pumpe EIN)
BW_DONE               → Rückspülung abgeschlossen
```

---

### 29. Bade-KI (Bathing AI)

| Schlüssel | Beschreibung | Format | Werte |
|-----------|-------------|--------|-------|
| `BATHING_AI_SURVEILLANCE_STATE` | Überwacht Pegelveränderung im Überlaufbehälter | STRING | `YES` = aktiv / `NO` = zurückgesetzt |
| `BATHING_AI_START_LEVEL` | Startpegel beim Beginn der Überwachung | FLOAT | – |
| `BATHING_AI_LAST_LEVEL` | Aktueller Pegel im Überlaufbehälter | FLOAT | – |
| `BATHING_AI_PUMP_STATE` | Hat die Bade-KI die Pumpe eingeschaltet? | STRING | `ON` / `OFF` |
| `BATHING_AI_PUMP_TIMESTAMP` | Zeitstempel wann Bade-KI die Pumpe einschaltete | Unix Epoch (s) | – |

---

### 30. PV-Überschuss

| Schlüssel | Beschreibung | Format | Werte |
|-----------|-------------|--------|-------|
| `PVSURPLUS` | PV-Überschuss-Zustand und Auslöser | INTEGER | `0` = Aus / `1` = Ein (Digital-Eingang) / `2` = Ein (HTTP-Request) |

---

---

## SCHREIBEN – Steuerung & Services

**Endpunkt:** `GET http://<IP>/setFunctionManually?{payload}`  
**Konfiguration:** `POST http://<IP>/setConfig`

---

### Schalter (Switch) – ON / OFF / AUTO

Alle Schalter unterstützen 3 Betriebsmodi:

| HA-Aktion | Controller-Wert | Bedeutung |
|-----------|----------------|-----------|
| `turn_on` | `4` | MANUELL EIN (erzwungen) |
| `turn_off` | `6` | MANUELL AUS |
| Automatikmodus | `0` / `1` | AUTO (Controller entscheidet) |

**Verfügbare Schalter:**

| HA-Entity | Schlüssel | Beschreibung |
|-----------|-----------|-------------|
| Filterpumpe | `PUMP` | Hauptpumpe |
| Solar | `SOLAR` | Solarabsorber |
| Heizung | `HEATER` | Heizung |
| Beleuchtung | `LIGHT` | Poolbeleuchtung |
| Dosierung pH+ | `DOS_5_PHP` | pH+ Dosierung |
| Dosierung pH- | `DOS_4_PHM` | pH- Dosierung |
| Chlor-Dosierung | `DOS_1_CL` | Chlor-Dosierung |
| Flockmittel | `DOS_6_FLOC` | Flockmittel-Dosierung |
| PV-Überschuss | `PVSURPLUS` | PV-Überschuss-Modus |
| Rückspülung | `BACKWASH` | Rückspülung |
| Nachspülung | `BACKWASHRINSE` | Rückspülnachspülung |
| Erweiterung 1.1 | `EXT1_1` | Relais Modul 1, Platz 1 |
| Erweiterung 1.2 | `EXT1_2` | Relais Modul 1, Platz 2 |
| Erweiterung 1.3 | `EXT1_3` | Relais Modul 1, Platz 3 |
| Erweiterung 1.4 | `EXT1_4` | Relais Modul 1, Platz 4 |
| Erweiterung 1.5 | `EXT1_5` | Relais Modul 1, Platz 5 |
| Erweiterung 1.6 | `EXT1_6` | Relais Modul 1, Platz 6 |
| Erweiterung 1.7 | `EXT1_7` | Relais Modul 1, Platz 7 |
| Erweiterung 1.8 | `EXT1_8` | Relais Modul 1, Platz 8 |
| Erweiterung 2.1 | `EXT2_1` | Relais Modul 2, Platz 1 |
| Erweiterung 2.2 | `EXT2_2` | Relais Modul 2, Platz 2 |
| Erweiterung 2.3 | `EXT2_3` | Relais Modul 2, Platz 3 |
| Erweiterung 2.4 | `EXT2_4` | Relais Modul 2, Platz 4 |
| Erweiterung 2.5 | `EXT2_5` | Relais Modul 2, Platz 5 |
| Erweiterung 2.6 | `EXT2_6` | Relais Modul 2, Platz 6 |
| Erweiterung 2.7 | `EXT2_7` | Relais Modul 2, Platz 7 |
| Erweiterung 2.8 | `EXT2_8` | Relais Modul 2, Platz 8 |
| DMX-Szene 1 | `DMX_SCENE1` | DMX-Lichtszene 1 |
| DMX-Szene 2 | `DMX_SCENE2` | DMX-Lichtszene 2 |
| DMX-Szene 3 | `DMX_SCENE3` | DMX-Lichtszene 3 |
| DMX-Szene 4 | `DMX_SCENE4` | DMX-Lichtszene 4 |
| DMX-Szene 5 | `DMX_SCENE5` | DMX-Lichtszene 5 |
| DMX-Szene 6 | `DMX_SCENE6` | DMX-Lichtszene 6 |
| DMX-Szene 7 | `DMX_SCENE7` | DMX-Lichtszene 7 |
| DMX-Szene 8 | `DMX_SCENE8` | DMX-Lichtszene 8 |
| DMX-Szene 9 | `DMX_SCENE9` | DMX-Lichtszene 9 |
| DMX-Szene 10 | `DMX_SCENE10` | DMX-Lichtszene 10 |
| DMX-Szene 11 | `DMX_SCENE11` | DMX-Lichtszene 11 |
| DMX-Szene 12 | `DMX_SCENE12` | DMX-Lichtszene 12 |
| Schaltregel 1 | `DIRULE_1` | Digitale Schaltregel 1 |
| Schaltregel 2 | `DIRULE_2` | Digitale Schaltregel 2 |
| Schaltregel 3 | `DIRULE_3` | Digitale Schaltregel 3 |
| Schaltregel 4 | `DIRULE_4` | Digitale Schaltregel 4 |
| Schaltregel 5 | `DIRULE_5` | Digitale Schaltregel 5 |
| Schaltregel 6 | `DIRULE_6` | Digitale Schaltregel 6 |
| Schaltregel 7 | `DIRULE_7` | Digitale Schaltregel 7 |

---

### Modus-Auswahl (Select)

Dropdown-Steuerung für den Betriebsmodus – Optionen: `off` / `on` / `auto`

| Select-Entity | Schlüssel | Beschreibung |
|--------------|-----------|-------------|
| Pumpen-Modus | `pump_mode` | Betriebsmodus Pumpe |
| Heizungs-Modus | `heater_mode` | Betriebsmodus Heizung |
| Solar-Modus | `solar_mode` | Betriebsmodus Solar |
| Beleuchtungs-Modus | `light_mode` | Betriebsmodus Beleuchtung |
| Chlor-Dosiermodus | `dos_cl_mode` | Betriebsmodus Chlor-Dosierung |
| pH- Dosiermodus | `dos_phm_mode` | Betriebsmodus pH- Dosierung |
| pH+ Dosiermodus | `dos_php_mode` | Betriebsmodus pH+ Dosierung |
| PV-Überschuss-Modus | `pvsurplus_mode` | Betriebsmodus PV-Überschuss |
| Rückspül-Modus | `backwash_mode` | Betriebsmodus Rückspülung |
| Nachspül-Modus | `backwashrinse_mode` | Betriebsmodus Nachspülung |
| Flockmittel-Modus | `dos_floc_mode` | Betriebsmodus Flockmittel |
| Erweiterung 1.1 Modus | `ext1_1_mode` | Modus Relais Modul 1.1 |
| … | … | (Gleiche Struktur EXT1_2–EXT2_8) |
| Erweiterung 2.8 Modus | `ext2_8_mode` | Modus Relais Modul 2.8 |

---

### Sollwerte (Number)

Einstellbare Zielwerte über Number-Entities:

| Number-Entity | Einheit | Bereich | Beschreibung |
|--------------|---------|---------|-------------|
| pH-Sollwert | – | 6.5–8.5 | Ziel-pH-Wert |
| ORP-Sollwert | mV | 100–900 | Ziel-Redoxpotential |
| Chlor-Sollwert | mg/l | 0.1–5.0 | Ziel-Chlorgehalt |
| Heizungs-Zieltemperatur | °C | 10–40 | Solltemperatur Heizung |
| Solar-Zieltemperatur | °C | 10–50 | Solltemperatur Solar |
| Pumpen-Stufe | – | 1–3 | Pumpendrehzahl-Stufe |
| Chlor-Kanistervolumen | ml | 0–50000 | Verbleibende Chlormenge |
| pH- Kanistervolumen | ml | 0–50000 | Verbleibende pH- Menge |
| pH+ Kanistervolumen | ml | 0–50000 | Verbleibende pH+ Menge |
| Flockmittel-Kanistervolumen | ml | 0–50000 | Verbleibende Flockmittelmenge |

---

### Klima (Climate)

Thermostat-Steuerung für Heizung und Solar:

| Climate-Entity | HVAC-Modi | Beschreibung |
|---------------|-----------|-------------|
| Pool-Heizung | `off`, `heat`, `auto` | Heizungsregelung mit Temperaturvorgabe |
| Solar-Heizung | `off`, `heat`, `auto` | Solar-Regelung mit Temperaturvorgabe |

---

### Abdeckung (Cover) – Steuerung

| Aktion | Beschreibung |
|--------|-------------|
| `open_cover` | Abdeckung öffnen |
| `close_cover` | Abdeckung schließen |
| `stop_cover` | Abdeckung stoppen |

---

### Services / Aktionen

Aufrufbar unter `violet_pool_controller.*` in HA:

#### `control_pump` – Pumpensteuerung

| Parameter | Pflicht | Optionen | Beschreibung |
|-----------|---------|----------|-------------|
| `action` | ✓ | `speed_control`, `force_off`, `eco_mode`, `boost_mode`, `auto` | Steueraktion |
| `speed` | – | 1–3 | Pumpenstufe (nur bei `speed_control`) |
| `duration` | – | 0–86400 s | Laufzeit in Sekunden |

#### `smart_dosing` – Dosiersteuerung

| Parameter | Pflicht | Optionen | Beschreibung |
|-----------|---------|----------|-------------|
| `dosing_type` | ✓ | `pH-`, `pH+`, `Chlorine`, `Flocculant` | Chemikalie |
| `action` | ✓ | `manual_dose`, `auto`, `stop` | Dosieraktion |
| `duration` | – | 5–300 s | Dosierdauer |
| `safety_override` | – | `true`/`false` | Sicherheitsintervall überschreiben |

#### `manage_pv_surplus` – PV-Überschuss

| Parameter | Pflicht | Optionen | Beschreibung |
|-----------|---------|----------|-------------|
| `mode` | ✓ | `activate`, `deactivate`, `auto` | Modus |
| `pump_speed` | – | 1–3 | Pumpenstufe im PV-Modus |

#### `control_dmx_scenes` – DMX-Szenensteuerung

| Parameter | Pflicht | Optionen | Beschreibung |
|-----------|---------|----------|-------------|
| `action` | ✓ | `all_on`, `all_off`, `all_auto`, `sequence`, `party_mode` | Szenen-Aktion |
| `sequence_delay` | – | 1–60 s | Verzögerung zwischen Szenen |

#### `set_light_color_pulse` – Lichtpuls

| Parameter | Pflicht | Bereich | Beschreibung |
|-----------|---------|---------|-------------|
| `pulse_count` | – | 1–10 | Anzahl Farbpulse |
| `pulse_interval` | – | 100–2000 ms | Intervall zwischen Pulsen |

#### `manage_digital_rules` – Schaltregeln

| Parameter | Pflicht | Optionen | Beschreibung |
|-----------|---------|----------|-------------|
| `rule_key` | ✓ | `DIRULE_1`–`DIRULE_7` | Regel-Identifier |
| `action` | ✓ | `trigger`, `lock`, `unlock` | Regelaktion |

#### `test_output` – Ausgangstest

| Parameter | Pflicht | Beschreibung |
|-----------|---------|-------------|
| `device_id` | ✓ | Zielgerät |
| `output` | ✓ | Ausgangs-ID (z.B. `PUMP`, `HEATER`, `EXT1_1`) |
| `mode` | – | `SWITCH`, `ON`, `OFF` |
| `duration` | – | 1–900 s |

#### `export_diagnostic_logs` – Diagnose-Export

| Parameter | Beschreibung |
|-----------|-------------|
| `device_id` | Zielgerät |
| `lines` | Anzahl Logzeilen (10–10000, Standard: 100) |
| `include_timestamps` | Zeitstempel einschließen |
| `save_to_file` | In `/config/` speichern |

#### `get_connection_status` – Verbindungsstatus
#### `get_error_summary` – Fehlerzusammenfassung  
#### `test_connection` – Verbindungstest
#### `clear_error_history` – Fehlerverlauf löschen

Alle 4 Services benötigen nur `device_id` als Pflichtparameter.

---

## Status-Codes Ausgänge

Gilt für: `PUMP`, `SOLAR`, `HEATER`, `LIGHT`, `REFILL`, `ECO`, `BACKWASH`, `BACKWASHRINSE`, `DOS_*`, `EXT*`, `DMX_SCENE*`, `PUMP_RPM_*`

| Code | Zustand | Bedeutung |
|------|---------|-----------|
| `0` | AUTO – Standby | Automatik, derzeit aus |
| `1` | AUTO – Ein | Automatik, derzeit ein |
| `2` | AUTO – Prio AUS | Automatik, durch Regel deaktiviert |
| `3` | AUTO – Prio EIN | Automatik, durch Notfallregel aktiviert |
| `4` | MANUELL EIN | Manuell eingeschaltet (erzwungen) |
| `5` | AUS durch Regel | Durch Notfallregel ausgeschaltet |
| `6` | MANUELL AUS | Manuell ausgeschaltet |

> Zusammengesetzte Zustände möglich, z.B. `"3|PUMP_ANTI_FREEZE"` – enthält numerischen Code und Detailbeschreibung.

**Detailbeschreibungen (Suffix nach `|`):**

| Code | Bedeutung (DE) |
|------|---------------|
| `PUMP_ANTI_FREEZE` | Frostschutz |
| `BLOCKED_BY_OUTSIDE_TEMP` | Blockiert (Außentemperatur) |
| `BLOCKED_BY_TRESHOLDS` | Blockiert (Schwellenwerte) |
| `TRESHOLDS_REACHED` | Schwellenwerte erreicht |
| `BLOCKED_BY_PUMP` | Blockiert (Pumpe aus) |
| `BLOCKED_BY_FLOW` | Blockiert (Durchfluss) |
| `BLOCKED_BY_SOLAR` | Blockiert (Solar) |
| `BLOCKED_BY_HEATER` | Blockiert (Heizung) |
| `WAITING_FOR_PUMP` | Warte auf Pumpe |
| `WAITING_FOR_FLOW` | Warte auf Durchfluss |
| `DOSING` | Dosierung |
| `DOSING_PAUSED` | Dosierung pausiert |
| `MANUAL_DOSING` | Manuelle Dosierung |

---

## Zeitstempel-Formate

| Format | Beispiel | Verwendung |
|--------|---------|-----------|
| Unix Epoch (Sekunden) | `1748390400` | LAST_ON, LAST_OFF, BW-Timestamps |
| Unix Epoch (Millisekunden) | `1748390400000` | DOS_*_LAST_CAN_RESET |
| HH:MM:SS | `04:33:12` | Laufzeiten (RUNTIME) |
| HH MM SS | `04h 33m 12s` | Laufzeiten bei Ausgängen |
| TT.MM.YYYY | `28.05.2026` | date |
| HH:MM:SS | `14:30:00` | time |
| DD HH MM | `2d 14h 30m` | CPU_UPTIME |

---

*Erstellt aus der offiziellen getReadings-Spezifikation (Rev. 14-07-2024) und dem Integrations-Quellcode v1.0.7-alpha.3*
