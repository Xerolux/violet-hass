> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Entities)**

---

# 🎛️ Entitäten - Violet Pool Controller

Vollständige Referenz aller Entitäten, die die Integration erzeugen kann. Entitäten werden dynamisch basierend auf den im Setup aktivierten Features und den vom Controller gemeldeten Daten angelegt.

> Quelle: `const_features.py`, `const_sensors.py`, `const_devices.py`. Entity-IDs verwenden den Präfix `violet_pool_controller` (bzw. `violet_pool_controller_<device_id>` bei Multi-Controller — siehe [Multi-Controller](Multi-Controller.de)).

---

## 📋 Inhaltsverzeichnis

1. [Sensoren](#-sensoren)
2. [Binary-Sensoren](#-binary-sensoren)
3. [Switches](#-switches)
4. [Light-Entitäten (DMX)](#-light-entitäten-dmx)
5. [Select-Steuerungen](#-select-steuerungen)
6. [Number-Entitäten (Sollwerte)](#-number-entitäten-sollwerte)
7. [Climate-Entitäten](#-climate-entitäten)
8. [Cover-Entität](#-cover-entität)
9. [Namenskonvention](#-namenskonvention)

---

## 🌡️ Sensoren

Alle Sensor-Definitionen liegen in `const_sensors.py`. Sensoren werden automatisch erstellt, wenn das entsprechende Reading in `/getReadings` vorhanden und das Feature aktiviert ist.

### Temperatur-Sensoren (1-Wire 1–12)

| Entity-ID-Suffix | Name | Einheit | Feature |
|------------------|------|---------|---------|
| `onewire1_value` | Beckenwasser | °C | immer |
| `onewire2_value` | Außentemperatur | °C | immer |
| `onewire3_value` | Solarkollektor | °C | solar |
| `onewire4_value` | Absorber-Rücklauf | °C | solar |
| `onewire5_value` | Wärmetauscher | °C | heating |
| `onewire6_value` | Heizungs-Speicher | °C | heating |
| `onewire7_value` – `onewire12_value` | Temperatursensor 7–12 | °C | immer |

### Wasserchemie-Sensoren

| Entity-ID-Suffix | Name | Einheit | Feature |
|------------------|------|---------|---------|
| `pH_value` | pH-Wert | pH | ph_control |
| `orp_value` | ORP-Wert | mV | chlorine_control |
| `pot_value` | Chlor-Wert | mg/l | chlorine_control |

### Analoge Sensoren (ADC / IMP)

| Entity-ID-Suffix | Name | Einheit |
|------------------|------|---------|
| `ADC1_value` | Filterdruck | bar |
| `ADC2_value` | Überlaufbehälter | cm |
| `ADC3_value` | Durchflussmesser (4-20 mA) | m³/h |
| `ADC4_value` | Analoger Sensor 4 (4-20 mA) | – |
| `ADC5_value` | Analoger Sensor 5 (0-10 V) | V |
| `IMP1_value` | Dosier-Zulauf | cm/s |
| `IMP2_value` | Pumpen-Durchfluss | m³/h |

### System-Sensoren

| Entity-ID-Suffix | Name | Einheit |
|------------------|------|---------|
| `SYSTEM_cpu_temperature` | CPU-Temperatur | °C |
| `SYSTEM_carrier_cpu_temperature` | Carrier-CPU-Temperatur | °C |
| `SYSTEM_dosagemodule_cpu_temperature` | Dosiermodul-CPU-Temperatur | °C |
| `SYSTEM_memoryusage` | Systemspeicher-Auslastung | – |
| `CPU_UPTIME` | Geräte-Laufzeit | – |
| `LOAD_AVG` | CPU-Last-Durchschnitt | – |
| `pump_rs485_pwr` | RS485-Pumpenleistung | W |
| `DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH1..8` | DI-Regel Restzeit | s |

### Status-Sensoren

| Entity-ID-Suffix | Name | Feature |
|------------------|------|---------|
| `PUMP` | Pumpenstatus | filter_control |
| `HEATER` | Heizungsstatus | heating |
| `SOLAR` | Solarstatus | solar |
| `BACKWASH` | Rückspülstatus | backwash |
| `BACKWASHRINSE` | Spülstatus | backwash |
| `LIGHT` | Lichtstatus | led_lighting |
| `REFILL` | Nachspeisestatus | water_refill |
| `ECO` | ECO-Status | – |
| `PVSURPLUS` | PV-Überschuss-Status | pv_surplus |
| `FW` | Firmware-Version | – |

### Composite-State-Sensoren

Diese tragen den vollen `"3|PUMP_ANTI_FREEZE"`-String mit `BLOCKED_BY_*`- / `WAITING_FOR_*`-Detail-Codes (siehe [Gerätezustände](Device-States.de)).

| Entity-ID-Suffix | Name | Feature |
|------------------|------|---------|
| `PUMPSTATE` | Pumpen-Detailstatus | filter_control |
| `HEATERSTATE` | Heizungs-Detailstatus | heating |
| `SOLARSTATE` | Solar-Detailstatus | solar |

### Dosier-Status-Sensoren

| Entity-ID-Suffix | Name | Feature |
|------------------|------|---------|
| `DOS_1_CL_STATE` | Chlor-Dosierstatus | chlorine_control |
| `DOS_2_ELO_STATE` | Elektrolyse-Status | chlorine_control |
| `DOS_4_PHM_STATE` | pH--Dosierstatus | ph_control |
| `DOS_5_PHP_STATE` | pH+-Dosierstatus | ph_control |
| `DOS_6_FLOC_STATE` | Flockungs-Status | flocculation |

### Laufzeit-Sensoren (täglich pro Ausgang)

Jeder Ausgang hat einen `*_RUNTIME`-Sensor mit der heutigen Laufzeit (ohne Einheit). Die Integration erzeugt diese für:

`PUMP`, `SOLAR`, `HEATER`, `LIGHT`, `BACKWASH`, `BACKWASHRINSE`, `ECO`, `REFILL`,
`DOS_1_CL`, `DOS_2_ELO`, `DOS_3_ELO_REV`, `DOS_4_PHM`, `DOS_5_PHP`, `DOS_6_FLOC`,
`EXT1_1`–`EXT1_8`, `EXT2_1`–`EXT2_8` (16 Erweiterungsrelais),
`OMNI_DC0`–`OMNI_DC5` (6 OMNI-Motoren),
`PUMP_RPM_0`–`PUMP_RPM_3` (4 RPM-Stufenlaufzeiten).

### Dosierstatistik-Sensoren

Für jeden Dosierkanal (`DOS_1_CL`, `DOS_2_ELO`, `DOS_4_PHM`, `DOS_5_PHP`, `DOS_6_FLOC`) wird bereitgestellt:

| Entity-ID-Suffix | Beschreibung | Einheit |
|------------------|--------------|---------|
| `*_DAILY_DOSING_AMOUNT_ML` | Tagesverbrauch | ml |
| `*_TOTAL_CAN_AMOUNT_ML`    | Verbleibende Kanistermenge | ml |

### Pumpen-RPM-Sensoren

| Entity-ID-Suffix | Beschreibung | Einheit |
|------------------|--------------|---------|
| `PUMP_RPM_0`–`PUMP_RPM_3` | RPM-Stufen-Statuscode (0-6) | – |
| `PUMP_RPM_0_VALUE`–`PUMP_RPM_3_VALUE` | Gemessene Drehzahl | RPM |

---

## 📊 Binary-Sensoren

### Kern-Betriebszustände

| Entity-ID-Suffix | Name | Device Class | Feature |
|------------------|------|--------------|---------|
| `PUMP` | Pumpenstatus | running | filter_control |
| `SOLAR` | Solarstatus | running | solar |
| `HEATER` | Heizungsstatus | running | heating |
| `LIGHT` | Lichtstatus | – | led_lighting |
| `BACKWASH` | Rückspülstatus | running | backwash |
| `REFILL` | Nachspeisestatus | running | water_refill |
| `ECO` | ECO-Modus | – | – |
| `PVSURPLUS` | PV-Überschuss | – | pv_surplus |

### Diagnose-Problemsensoren

| Entity-ID-Suffix | Name | Device Class |
|------------------|------|--------------|
| `CIRCULATION_STATE` | Zirkulationsproblem | problem |
| `ELECTRODE_FLOW_STATE` | Elektroden-Durchflussproblem | problem |
| `PRESSURE_STATE` | Druckproblem | problem |
| `CAN_RANGE_STATE` | Kanister-Problem | problem |

### Hardware-Modul-Sensoren

| Entity-ID-Suffix | Name |
|------------------|------|
| `HW_BASE_MODULE` | Hardware: Basismodul |
| `HW_DOSING_MODULE` | Hardware: Dosiermodul |
| `HW_EXTENSION_MODULE_1` | Hardware: Erweiterungsmodul 1 |
| `HW_EXTENSION_MODULE_2` | Hardware: Erweiterungsmodul 2 |
| `HW_STANDALONE_MODE` | Hardware: Standalone-Dosiereinheit |
| `HW_DMX_MODULE` | Hardware: DMX-Modul |
| `HW_DIRULE_MODULE` | Hardware: Digitalregel-Modul |

### Überlauf / Rückspülung / Bad-AI

| Entity-ID-Suffix | Name | Device Class |
|------------------|------|--------------|
| `OVERFLOW_OVERFILL_STATE` | Überlauf überfüllt | problem |
| `OVERFLOW_DRYRUN_STATE` | Überlauf Trockenlauf | problem |
| `OVERFLOW_REFILL_STATE` | Überlauf Nachspeisung | – |
| `BACKWASH_DELAY_RUNNING` | Rückspülverzögerung aktiv | – |
| `BATHING_AI_SURVEILLANCE_STATE` | Bad-AI-Überwachung | – |

### Digitale Eingänge

| Entity-ID-Suffix | Name | Feature |
|------------------|------|---------|
| `INPUT1`–`INPUT12` | Digitaler Eingang 1–12 | digital_inputs |
| `INPUT_CE1`–`INPUT_CE4` | Digitaler Eingang CE1–CE4 | digital_inputs |

---

## 🔌 Switches

> Alle Switches sind 3-state (Off / On / Auto). Siehe [Gerätezustände](Device-States.de) für die 0-6-Codes.

### Kern-Switches

| Entity-ID-Suffix | Name | Feature |
|------------------|------|---------|
| `PUMP` | Filterpumpe | filter_control |
| `SOLAR` | Solarkollektor | solar |
| `HEATER` | Heizung | heating |
| `LIGHT` | Beleuchtung | led_lighting |
| `DOS_5_PHP` | Dosierung pH+ | ph_control |
| `DOS_4_PHM` | Dosierung pH- | ph_control |
| `DOS_1_CL` | Chlor-Dosierung | chlorine_control |
| `DOS_2_ELO` | Elektrolyse-Dosierung | chlorine_control |
| `DOS_6_FLOC` | Flockung | flocculation |
| `PVSURPLUS` | PV-Überschuss | pv_surplus |
| `BACKWASH` | Rückspülung | backwash |
| `BACKWASHRINSE` | Spülung | backwash |
| `REFILL` | Wassernachspeisung | water_refill |
| `ECO` | ECO-Modus | – |

### Erweiterungsrelais-Switches (16)

| Entity-ID-Suffix | Name | Feature |
|------------------|------|---------|
| `EXT1_1`–`EXT1_8` | Erweiterung 1.1–1.8 | extension_outputs |
| `EXT2_1`–`EXT2_8` | Erweiterung 2.1–2.8 | extension_outputs |

### Digitalregel-Switches (8)

| Entity-ID-Suffix | Name | Feature |
|------------------|------|---------|
| `DIRULE_1`–`DIRULE_8` | Schaltregel 1–8 | digital_inputs |

### OMNI-DC-Ausgangs-Switches (6)

| Entity-ID-Suffix | Name | Feature |
|------------------|------|---------|
| `OMNI_DC0`–`OMNI_DC5` | Omni DC0–DC5 | extension_outputs |

---

## 💡 Light-Entitäten (DMX)

Die 12 DMX-Szenen werden als **LightEntity** (nicht als Switch) bereitgestellt, damit sie sauber in HA-Dashboards und die Light-Domain integriert werden.

| Entity-ID-Suffix | Name | Feature |
|------------------|------|---------|
| `DMX_SCENE1`–`DMX_SCENE12` | DMX-Szene 1–12 | led_lighting |

---

## 🎛️ Select-Steuerungen

Jeder steuerbare Ausgang hat eine passende `*_mode`-Select-Entität mit den Optionen **Off / On / Auto** (oder **Off / Manual / Auto** bei Dosierkanälen).

| Entity-ID-Suffix | Name | Backend-Ausgang |
|------------------|------|-----------------|
| `pump_mode` | Pumpenmodus | PUMP |
| `heater_mode` | Heizungsmodus | HEATER |
| `solar_mode` | Solarmodus | SOLAR |
| `light_mode` | Lichtmodus | LIGHT |
| `dos_cl_mode` | Chlor-Dosiermodus | DOS_1_CL |
| `dos_elo_mode` | Elektrolyse-Dosiermodus | DOS_2_ELO |
| `dos_phm_mode` | pH--Dosiermodus | DOS_4_PHM |
| `dos_php_mode` | pH+-Dosiermodus | DOS_5_PHP |
| `dos_floc_mode` | Flockungsmodus | DOS_6_FLOC |
| `pvsurplus_mode` | PV-Überschuss-Modus | PVSURPLUS |
| `backwash_mode` | Rückspülmodus | BACKWASH |
| `backwashrinse_mode` | Spülmodus | BACKWASHRINSE |
| `refill_mode` | Nachspeisemodus | REFILL |
| `eco_mode` | ECO-Modus (nur Lesen) | ECO |
| `ext1_1_mode`–`ext2_8_mode` | Erweiterung 1.1–2.8 Modus (16) | EXT*_* |
| `omni_dc0_mode`–`omni_dc5_mode` | Omni DC0–DC5 Modus (6) | OMNI_DC* |

---

## 🔢 Number-Entitäten (Sollwerte)

### Chemie-Sollwerte

| Entity-ID-Suffix | Name | Min | Max | Step | Default | Einheit |
|------------------|------|-----|-----|------|---------|---------|
| `ph_setpoint` | pH-Sollwert | 6.8 | 7.8 | 0.1 | 7.2 | pH |
| `orp_setpoint` | ORP-Sollwert | 400 | 900 | 5 | 700 | mV |
| `chlorine_setpoint` | Chlor-Sollwert | 0.05 | 5.0 | 0.05 | 0.6 | mg/l |

### Temperatur-Sollwerte

| Entity-ID-Suffix | Name | Min | Max | Step | Default | Einheit |
|------------------|------|-----|-----|------|---------|---------|
| `heater_target_temp` | Heizung Solltemperatur | 20.0 | 35.0 | 0.5 | 28.0 | °C |
| `solar_target_temp` | Solar Solltemperatur | 20.0 | 40.0 | 0.5 | 30.0 | °C |

### Pumpengeschwindigkeit

| Entity-ID-Suffix | Name | Min | Max | Step | Default |
|------------------|------|-----|-----|------|---------|
| `pump_speed` | Pumpengeschwindigkeit | 1 | 3 | 1 | 2 |

### Kanistervolumina

| Entity-ID-Suffix | Name | Min | Max | Step | Default | Einheit |
|------------------|------|-----|-----|------|---------|---------|
| `chlorine_canister_volume` | Chlor-Kanistervolumen | 100 | 50000 | 100 | 10000 | ml |
| `ph_minus_canister_volume` | pH--Kanistervolumen | 100 | 50000 | 100 | 10000 | ml |
| `ph_plus_canister_volume` | pH+-Kanistervolumen | 100 | 50000 | 100 | 20000 | ml |
| `flocculant_canister_volume` | Flockungs-Kanistervolumen | 100 | 50000 | 100 | 20000 | ml |

---

## 🌡️ Climate-Entitäten

| Entity-ID-Suffix | Name | Feature | HVAC-Modi |
|------------------|------|---------|-----------|
| `heater` | Heizung | heating | off, heat, auto |
| `solar` | Solar | solar | off, heat, auto |

---

## 🏊 Cover-Entität

| Entity-ID-Suffix | Name | Feature | Kommandos |
|------------------|------|---------|-----------|
| `cover` | Poolabdeckung | cover_control | open, close, stop |

Die Cover-Entität liest `COVER_STATE` und meldet `OPEN`, `OPENING`, `CLOSED`, `CLOSING`, `STOPPED` (siehe `CoverState`-Enum).

---

## 🏷️ Namenskonvention

### Struktur

```
{entity_type}.violet_pool_controller_{device_key}
```

Beispiele:
- `sensor.violet_pool_controller_ph_value`
- `switch.violet_pool_controller_pump`
- `climate.violet_pool_controller_heater`
- `light.violet_pool_controller_dmx_scene1`
- `select.violet_pool_controller_pump_mode`
- `number.violet_pool_controller_ph_setpoint`

### Multi-Controller

Bei mehreren Controllern wird die pro-Controller eindeutige ID (`{api_url}_{device_id}`) angehängt:

```
{entity_type}.violet_pool_controller_{device_id}_{device_key}
```

Siehe [Multi-Controller-Anleitung](Multi-Controller.de) für Details.

---

## ❓ FAQ

### Entitäten fehlen?

1. **Feature aktivieren**: Settings → Devices & Services → Violet Pool Controller → "..." → Konfiguration ändern → Feature aktivieren.
2. **Home Assistant neu starten**: Settings → System → Restart.
3. **Einen Polling-Zyklus warten** (Default: 10 s), bis Sensoren befüllt sind.
4. **Controller prüfen**: Manche Sensoren erscheinen nur, wenn der Controller das entsprechende Reading liefert (z. B. `DOS_2_ELO_*` benötigt ein Elektrolyse-Modul).

### Entität umbenennen?

Settings → Devices & Services → Entities → Suche → "..." → Entität umbenennen.

> ⚠️ Das Umbenennen wirkt sich auf bestehende Automatisierungen aus.

---

**Weiter:** [Sensoren](Sensors.de) | [Schalter](Switches.de) | [Gerätezustände](Device-States.de) | [Services](Services.de)
