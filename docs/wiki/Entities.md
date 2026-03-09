# 🎛️ Entities - Violet Pool Controller

## Übersicht aller verfügbaren Entities

Diese Seite listet alle Entities auf, die von der Violet Pool Controller Integration erstellt werden. Alle Icons wurden im **März 2026 optimiert** und verwenden jetzt konsistente, professionelle MDI-Icons.

---

## 📊 Statistik

| Metrik | Wert |
|--------|-------|
| **Gesamtzahl Entities** | 150+ |
| **Kategorien** | 8 |
| **Icons optimiert** | 68+ |
| **Icon-Set** | Material Design Icons (MDI) |
| **Status** | Alle verifiziert & funktionierend |

---

## 📋 Inhaltsverzeichnis

1. [Sensoren](#-sensoren)
2. [Binary Sensoren](#-binary-sensoren)
3. [Switches](#-switches)
4. [Select Controls](#-select-controls)
5. [Number Entities (Setpoints)](#-number-entities-setpoints)
6. [Climate Entities](#-climate-entities)
7. [Entity-Namenskonvention](#-entity-namenskonvention)
8. [Multi-Controller](#-multi-controller)

---

## 🌡️ Sensoren

### Temperatursensoren (6 Entities)

| Entity-ID | Name | Icon | Einheit | Beschreibung |
|-----------|------|------|---------|-------------|
| `sensor.violet_pool_controller_onewire1_value` | Beckenwasser | 🏊 `mdi:pool` | °C | Pool-Wassertemperatur |
| `sensor.violet_pool_controller_onewire2_value` | Außentemperatur | 🌡️ `mdi:thermometer` | °C | Außenlufttemperatur |
| `sensor.violet_pool_controller_onewire3_value` | Solarabsorber | ☀️ `mdi:solar-power` | °C | Solar-Kollektor-Temperatur |
| `sensor.violet_pool_controller_onewire4_value` | Absorber-Rücklauf | 🔧 `mdi:pipe-valve` | °C | Rücklauftemperatur mit Ventil |
| `sensor.violet_pool_controller_onewire5_value` | Wärmetauscher | ♨️ `mdi:radiator` | °C | Wärmetauscher-Temperatur |
| `sensor.violet_pool_controller_onewire6_value` | Heizungs-Speicher | 🚿 `mdi:water-boiler` | °C | Speichertemperatur |

**Feature-Abhängigkeit:**
- `onewire1_value`, `onewire2_value`: Immer verfügbar
- `onewire3_value`, `onewire4_value`: Benötigt Feature **"Solarabsorber"**
- `onewire5_value`, `onewire6_value`: Benötigt Feature **"Heizung"**

### Wasserchemie-Sensoren (3 Entities)

| Entity-ID | Name | Icon | Einheit | Beschreibung |
|-----------|------|------|---------|-------------|
| `sensor.violet_pool_controller_ph_value` | pH-Wert | ⚗️ `mdi:ph` | pH | **Spezielles pH-Icon!** |
| `sensor.violet_pool_controller_orp_value` | Redoxpotential | ⚡ `mdi:lightning-bolt-circle` | mV | Redoxpotential mit Kreis |
| `sensor.violet_pool_controller_pot_value` | Chlorgehalt | 🧪 `mdi:water-plus` | mg/l | Chlorgehalt im Wasser |

**Feature-Abhängigkeit:**
- `pH_value`: Benötigt Feature **"pH-Kontrolle"**
- `orp_value`, `pot_value`: Benötigt Feature **"Chlor-Kontrolle"**

### Analogsensoren (7 Entities)

| Entity-ID | Name | Icon | Einheit | Beschreibung |
|-----------|------|------|---------|-------------|
| `sensor.violet_pool_controller_adc1_value` | Filterdruck | 🌡️ `mdi:gauge` | bar | Druckanzeige |
| `sensor.violet_pool_controller_adc2_value` | Überlaufbehälter | 💧 `mdi:water-sync` | cm | Überlauf-Wasserspiegel |
| `sensor.violet_pool_controller_adc3_value` | Durchflussmesser | ↔️ `mdi:swap-horizontal` | m³/h | Durchfluss-Pfeile |
| `sensor.violet_pool_controller_adc4_value` | Analogsensor 4 | 📊 `mdi:gauge` | - | Universeller Sensor (4-20mA) |
| `sensor.violet_pool_controller_adc5_value` | Analogsensor 5 | 〰️ `mdi:sine-wave` | V | Universeller Sensor (0-10V) |
| `sensor.violet_pool_controller_imp1_value` | Flow-Switch | 🔧 `mdi:pipe-valve` | cm/s | Durchfluss-Schalter |
| `sensor.violet_pool_controller_imp2_value` | Pumpen-Durchfluss | 💧 `mdi:water-pump` | m³/h | Volumenstrom |

**Feature-Abhängigkeit:** Alle Analogsensoren werden automatisch erstellt wenn Daten verfügbar.

### System-Sensoren (7 Entities)

| Entity-ID | Name | Icon | Einheit | Beschreibung |
|-----------|------|------|---------|-------------|
| `sensor.violet_pool_controller_cpu_temp` | CPU Temperatur | 🔥 `mdi:thermometer-alert` | °C | Temp mit Warnung |
| `sensor.violet_pool_controller_cpu_temp_carrier` | Carrier Board | 🖥️ `mdi:motherboard` | °C | Hauptplatine |
| `sensor.violet_pool_controller_cpu_uptime` | System Uptime | ⏰ `mdi:clock-time-eight` | - | Uhrzeit-Anzeige |
| `sensor.violet_pool_controller_system_cpu_temperature` | System CPU | 🌡️ `mdi:thermometer-check` | °C | Temp-Check |
| `sensor.violet_pool_controller_system_carrier_cpu_temperature` | Carrier CPU | 💾 `mdi:memory` | °C | Speicher-Chip |
| `sensor.violet_pool_controller_system_dosagemodule_cpu_temperature` | Dosiermodul CPU | 💾 `mdi:memory-lan` | °C | LAN-Speicher |
| `sensor.violet_pool_controller_system_memoryusage` | Memory Usage | 💾 `mdi:memory-lan` | % | Speichernutzung |

**Feature-Abhängigkeit:** Immer verfügbar.

### Status-Sensoren (7 Entities)

| Entity-ID | Name | Icon | Einheit | Beschreibung |
|-----------|------|------|---------|-------------|
| `sensor.violet_pool_controller_pump` | Pumpen-Status | ⚙️ `mdi:pump` | - | Pumpen-Status |
| `sensor.violet_pool_controller_heater` | Heizungs-Status | ♨️ `mdi:radiator` | - | Heizkörper-Status |
| `sensor.violet_pool_controller_solar` | Solar-Status | ☀️ `mdi:solar-power` | - | Solar-Status |
| `sensor.violet_pool_controller_backwash` | Rückspül-Status | 🔄 `mdi:autorenew` | - | Autorenew-Zyklus |
| `sensor.violet_pool_controller_light` | Beleuchtung Status | 💡 `mdi:lightbulb` | - | Lampen-Status |
| `sensor.violet_pool_controller_pvsurplus` | PV-Überschuss | ☀️ `mdi:solar-power` | - | PV-Überschuss |
| `sensor.violet_pool_controller_fw` | Firmware | 📦 `mdi:package-variant` | - | Firmware-Version |

**Feature-Abhängigkeit:**
- `heater`: Benötigt Feature **"Heizung"**
- `solar`: Benötigt Feature **"Solarabsorber"**
- `backwash`: Benötigt Feature **"Rückspülung"**
- `light`: Benötigt Feature **"LED-Beleuchtung"**
- `pvsurplus`: Benötigt Feature **"PV-Überschuss"**

### Dosier-Sensoren (5 Entities)

| Entity-ID | Name | Icon | Einheit | Beschreibung |
|-----------|------|------|---------|-------------|
| `sensor.violet_pool_controller_dos_1_cl_state` | Chlor Status | 🧪 `mdi:flask-outline` | - | Chlor-Dosierung |
| `sensor.violet_pool_controller_dos_2_elo_state` | Elektrolyse | ⚡ `mdi:lightning-bolt` | - | Elektrolyse-Status |
| `sensor.violet_pool_controller_dos_4_phm_state` | pH- Status | 🧪 `mdi:flask-minus` | - | pH-Minus Dosierung |
| `sensor.violet_pool_controller_dos_5_php_state` | pH+ Status | 🧪 `mdi:flask-plus` | - | pH-Plus Dosierung |
| `sensor.violet_pool_controller_dos_6_floc_state` | Flockung | 💧 `mdi:water` | - | Flockmittel-Status |

**Feature-Abhängigkeit:**
- `DOS_1_CL_STATE`, `DOS_2_ELO_STATE`: Benötigt Feature **"Chlor-Kontrolle"**
- `DOS_4_PHM_STATE`, `DOS_5_PHP_STATE`: Benötigt Feature **"pH-Kontrolle"**
- `DOS_6_FLOC_STATE`: Benötigt Feature **"Flockungsmittel-Dosierung"**

---

## 📊 Binary Sensoren

### Core Operational States (7 Entities)

| Entity-ID | Name | Icon | Device Class | Beschreibung |
|-----------|------|------|--------------|-------------|
| `binary_sensor.violet_pool_controller_pump` | Pump State | 💧 `mdi:water-pump` | running | Pumpe läuft |
| `binary_sensor.violet_pool_controller_solar` | Solar State | ☀️ `mdi:solar-power` | running | Solar aktiv |
| `binary_sensor.violet_pool_controller_heater` | Heater State | ♨️ `mdi:radiator` | running | Heizung aktiv |
| `binary_sensor.violet_pool_controller_light` | Light State | 💡 `mdi:lightbulb` | - | Licht an |
| `binary_sensor.violet_pool_controller_backwash` | Backwash State | 🔄 `mdi:autorenew` | running | Rückspülung läuft |
| `binary_sensor.violet_pool_controller_refill` | Refill State | 💧 `mdi:water` | running | Nachfüllen aktiv |
| `binary_sensor.violet_pool_controller_pvsurplus` | PV Surplus | ☀️ `mdi:solar-power` | - | PV-Überschuss |

### Diagnostic Problem Sensors (5 Entities)

| Entity-ID | Name | Icon | Device Class | Beschreibung |
|-----------|------|------|--------------|-------------|
| `binary_sensor.violet_pool_controller_circulation_state` | Circulation Issue | ⚠️ `mdi:water-alert` | problem | Zirkulations-Problem |
| `binary_sensor.violet_pool_controller_electrode_flow_state` | Electrode Flow Issue | ✅ `mdi:water-check` | problem | Elektroden-Fluss |
| `binary_sensor.violet_pool_controller_pressure_state` | Pressure Issue | 🌡️ `mdi:gauge` | problem | Druck-Problem |
| `binary_sensor.violet_pool_controller_can_range_state` | Can Range Issue | 🍾 `mdi:bottle-tonic` | problem | Kanister-Problem |

### Additional Binary Sensors

| Entity-ID | Name | Icon | Device Class | Beschreibung |
|-----------|------|------|--------------|-------------|
| `binary_sensor.violet_pool_controller_eco` | ECO Mode | 🍃 `mdi:leaf` | - | Eco-Modus aktiv |
| `binary_sensor.violet_pool_controller_input_{1-12}` | Digital Input {1-12} | 🔌 `mdi:electric-switch` | - | Digitale Eingänge |
| `binary_sensor.violet_pool_controller_input_ce{1-4}` | Digital Input CE{1-4} | 🔌 `mdi:electric-switch` | - | Digitale Eingänge CE |

**Feature-Abhängigkeit:**
- `INPUT_{1-12}`, `INPUT_CE{1-4}`: Benötigt Feature **"Digitale Eingänge"**

---

## 🔌 Switches

### Main Control Switches (11 Entities)

| Entity-ID | Name | Icon | Beschreibung |
|-----------|------|------|-------------|
| `switch.violet_pool_controller_pump` | Filterpumpe | 💧 `mdi:water-pump` | Pumpe ein/aus |
| `switch.violet_pool_controller_solar` | Solarabsorber | ☀️ `mdi:solar-power` | Solar ein/aus |
| `switch.violet_pool_controller_heater` | Heizung | ♨️ `mdi:radiator` | Heizung ein/aus |
| `switch.violet_pool_controller_light` | Beleuchtung | 💡 `mdi:lightbulb` | Licht ein/aus |
| `switch.violet_pool_controller_dos_5_php` | Dosierung pH+ | 🧪 `mdi:flask-plus` | pH+ dosieren |
| `switch.violet_pool_controller_dos_4_phm` | Dosierung pH- | 🧪 `mdi:flask-minus` | pH- dosieren |
| `switch.violet_pool_controller_dos_1_cl` | Chlor-Dosierung | 🧪 `mdi:flask-outline` | Chlor dosieren |
| `switch.violet_pool_controller_dos_6_floc` | Flockmittel | 💧 `mdi:water` | Flockung dosieren |
| `switch.violet_pool_controller_pvsurplus` | PV-Überschuss | ☀️ `mdi:solar-power` | PV-Modus |
| `switch.violet_pool_controller_backwash` | Rückspülung | 🔄 `mdi:autorenew` | Rückspülung starten |
| `switch.violet_pool_controller_backwashrinse` | Nachspülung | 🔄 `mdi:autorenew` | Nachspülung starten |

### DMX Scene Switches (12 Entities)

| Entity-ID | Name | Icon | Beschreibung |
|-----------|------|------|-------------|
| `switch.violet_pool_controller_dmx_scene{1-12}` | DMX Szene {1-12} | 💡 `mdi:lightbulb-multiple` | Lichtszenen steuern |

**Feature-Abhängigkeit:** Benötigt Feature **"LED-Beleuchtung"**

### Extension Switches (16 Entities)

| Entity-ID | Name | Icon | Beschreibung |
|-----------|------|------|-------------|
| `switch.violet_pool_controller_ext1_{1-8}` | Extension 1.{1-8} | 🔌 `mdi:toggle-switch-outline` | Erweiterung 1 |
| `switch.violet_pool_controller_ext2_{1-8}` | Extension 2.{1-8} | 🔌 `mdi:toggle-switch-outline` | Erweiterung 2 |

**Feature-Abhängigkeit:** Benötigt Feature **"Erweiterungsausgänge"**

### Digital Rule Switches (7 Entities)

| Entity-ID | Name | Icon | Beschreibung |
|-----------|------|------|-------------|
| `switch.violet_pool_controller_dirule_{1-7}` | Schaltregel {1-7} | 📜 `mdi:script-text` | Schaltregeln steuern |

**Feature-Abhängigkeit:** Benötigt Feature **"Digitale Eingänge"**

---

## 🎛️ Select Controls

### Mode Selects (8 Entities)

| Entity-ID | Name | Icon | Optionen | Beschreibung |
|-----------|------|------|----------|-------------|
| `select.violet_pool_controller_pump_mode` | Pumpen-Modus | 💧 `mdi:water-pump` | Aus/Ein/Auto | Pumpe: Aus/Ein/Auto |
| `select.violet_pool_controller_heater_mode` | Heizungs-Modus | ♨️ `mdi:radiator` | Aus/Ein/Auto | Heizung: Aus/Ein/Auto |
| `select.violet_pool_controller_solar_mode` | Solar-Modus | ☀️ `mdi:solar-power` | Aus/Ein/Auto | Solar: Aus/Ein/Auto |
| `select.violet_pool_controller_light_mode` | Licht-Modus | 💡 `mdi:lightbulb` | Aus/Ein/Auto | Licht: Aus/Ein/Auto |
| `select.violet_pool_controller_dos_cl_mode` | Chlor-Modus | 🧪 `mdi:flask-outline` | Aus/Manu/Auto | Chlor-Dosierung |
| `select.violet_pool_controller_dos_phm_mode` | pH-Modus | 🧪 `mdi:flask-minus` | Aus/Manu/Auto | pH-Minus-Dosierung |
| `select.violet_pool_controller_dos_php_mode` | pH+ Modus | 🧪 `mdi:flask-plus` | Aus/Manu/Auto | pH-Plus-Dosierung |
| `select.violet_pool_controller_pvsurplus_mode` | PV-Modus | ☀️ `mdi:solar-power` | Aus/Ein/Auto | PV-Überschuss-Modus |

**Feature-Abhängigkeit:**
- `pump_mode`: Benötigt Feature **"Filterpumpe"**
- `heater_mode`: Benötigt Feature **"Heizung"**
- `solar_mode`: Benötigt Feature **"Solarabsorber"**
- `light_mode`: Benötigt Feature **"LED-Beleuchtung"**
- `dos_cl_mode`: Benötigt Feature **"Chlor-Kontrolle"**
- `dos_phm_mode`, `dos_php_mode`: Benötigt Feature **"pH-Kontrolle"**
- `pvsurplus_mode`: Benötigt Feature **"PV-Überschuss"**

---

## 🔢 Number Entities (Setpoints)

### Chemistry Setpoints (3 Entities)

| Entity-ID | Name | Icon | Min | Max | Schritt | Standard | Einheit |
|-----------|------|------|-----|-----|---------|----------|---------|
| `number.violet_pool_controller_ph_setpoint` | pH Sollwert | ⚗️ `mdi:ph` | 6.8 | 7.8 | 0.1 | 7.2 | pH |
| `number.violet_pool_controller_orp_setpoint` | Redox Sollwert | ⚡ `mdi:lightning-bolt-circle` | 600 | 800 | 10 | 700 | mV |
| `number.violet_pool_controller_chlorine_setpoint` | Chlor Sollwert | 🧪 `mdi:water-plus` | 0.2 | 2.0 | 0.1 | 0.6 | mg/l |

**Feature-Abhängigkeit:**
- `ph_setpoint`: Benötigt Feature **"pH-Kontrolle"**
- `orp_setpoint`, `chlorine_setpoint`: Benötigt Feature **"Chlor-Kontrolle"**

### Temperature Setpoints (2 Entities)

| Entity-ID | Name | Icon | Min | Max | Schritt | Standard | Einheit |
|-----------|------|------|-----|-----|---------|----------|---------|
| `number.violet_pool_controller_heater_target_temp` | Heizung Zieltemperatur | ♨️ `mdi:radiator` | 20.0 | 35.0 | 0.5 | 28.0 | °C |
| `number.violet_pool_controller_solar_target_temp` | Solar Zieltemperatur | ☀️ `mdi:solar-power` | 20.0 | 40.0 | 0.5 | 30.0 | °C |

**Feature-Abhängigkeit:**
- `heater_target_temp`: Benötigt Feature **"Heizung"**
- `solar_target_temp`: Benötigt Feature **"Solarabsorber"**

### Pump Speed (1 Entity)

| Entity-ID | Name | Icon | Min | Max | Schritt | Standard | Einheit |
|-----------|------|------|-----|-----|---------|----------|---------|
| `number.violet_pool_controller_pump_speed` | Pumpengeschwindigkeit | ⚙️ `mdi:pump` | 1 | 3 | 1 | 2 | - |

**Feature-Abhängigkeit:** Benötigt Feature **"Filterpumpe"**

### Canister Volumes (4 Entities)

| Entity-ID | Name | Icon | Min | Max | Schritt | Standard | Einheit |
|-----------|------|------|-----|-----|---------|----------|---------|
| `number.violet_pool_controller_chlorine_canister_volume` | Chlor Kanister Volumen | 🛢️ `mdi:barrel` | 100 | 50000 | 100 | 10000 | ml |
| `number.violet_pool_controller_ph_minus_canister_volume` | pH- Kanister Volumen | 🛢️ `mdi:barrel` | 100 | 50000 | 100 | 10000 | ml |
| `number.violet_pool_controller_ph_plus_canister_volume` | pH+ Kanister Volumen | 🛢️ `mdi:barrel` | 100 | 50000 | 100 | 20000 | ml |
| `number.violet_pool_controller_flocculant_canister_volume` | Flockulant Kanister Volumen | 🛢️ `mdi:barrel` | 100 | 50000 | 100 | 20000 | ml |

**Feature-Abhängigkeit:**
- `chlorine_canister_volume`: Benötigt Feature **"Chlor-Kontrolle"**
- `ph_minus_canister_volume`, `ph_plus_canister_volume`: Benötigt Feature **"pH-Kontrolle"**
- `flocculant_canister_volume`: Benötigt Feature **"Flockungsmittel-Dosierung"**

---

## 🌡️ Climate Entities

### Thermostats (2 Entities)

| Entity-ID | Name | Icon | Beschreibung |
|-----------|------|------|-------------|
| `climate.violet_pool_controller_heater` | Heizung | ♨️ `mdi:radiator` | Heizungs-Thermostat |
| `climate.violet_pool_controller_solar` | Solar | ☀️ `mdi:solar-power` | Solar-Thermostat |

**Feature-Abhängigkeit:**
- `heater`: Benötigt Feature **"Heizung"**
- `solar`: Benötigt Feature **"Solarabsorber"**

**Funktionen:**
- Temperatur einstellen
- Modus wählen (Aus/Heizen)
- Zeitpläne nutzen
- Automationen erstellen

---

## 🏷️ Entity-Namenskonvention

### Struktur

```
{entity_type}.violet_pool_controller_{device_key}
```

**Beispiele:**
- `sensor.violet_pool_controller_pH_value`
- `switch.violet_pool_controller_pump`
- `climate.violet_pool_controller_heater`

### Multi-Controller

Bei mehreren Controllern wird die Geräte-ID eingefügt:

```
{entity_type}.violet_pool_controller_{device_id}_{device_key}
```

**Beispiele:**
- `sensor.violet_pool_controller_1_ph_value` (Controller 1)
- `sensor.violet_pool_controller_2_ph_value` (Controller 2)
- `switch.violet_pool_controller_1_pump` (Controller 1)
- `switch.violet_pool_controller_2_pump` (Controller 2)

### Device ID ändern

Du kannst die Geräte-ID in der Integration ändern:

1. Einstellungen → Geräte & Dienste
2. Violet Pool Controller → "..."
3. Konfiguration ändern
4. Geräte-ID anpassen
5. Neustarten

⚠️ **Achtung:** Die Geräte-ID zu ändern creates neue Entities! Die alten Entities bleiben in der Registry erhalten.

---

## 🎨 Icon-Optimierungen (März 2026)

### Top 10 Verbesserungen

| Platz | Icon-Wechsel | Grund |
|-------|--------------|--------|
| 🥇 | `mdi:flask` → **`mdi:ph`** | Echtes pH-Icon statt Flasche |
| 🥈 | `mdi:water-percent` → **`mdi:water-sync`** | Überlauf statt Prozent |
| 🥉 | `mdi:refresh` → **`mdi:autorenew`** | Autorenew für Zyklus |
| 4 | `mdi:pump-on` → **`mdi:water-pump`** | Wasserpumpe existiert |
| 5 | `mdi:radiator-disabled` → **`mdi:radiator`** | Heizkörper einfacher |
| 6 | `mdi:lightbulb-on` → **`mdi:lightbulb`** | Glühbirne Standard |
| 7 | `mdi:heat-exchange` → **`mdi:radiator`** | Wärmetauscher klarer |
| 8 | `mdi:pool-thermometer` → **`mdi:pool`** | Pool einfacher |
| 9 | `mdi:water-opacity` → **`mdi:water`** | Wasser statt Trübung |
| 10 | `mdi:gauge-full` → **`mdi:gauge`** | Messanzeige Standard |

### Alle Icon-Änderungen

- **68+ Icons optimiert**
- **Alle zu MDI geändert**
- **Konsistentes Icon-Set**
- **Keine defekten Icons mehr**

📖 **Details:** [Icon-Referenz](Icon-Reference)

---

## 📖 Nächste Schritte

Nachdem du alle Entities kennst:

1. 🤖 **Automationen erstellen**: [Services Guide](Services)
2. 🎨 **Dashboard einrichten**: [Dashboard Guide](Home)
3. 🐛 **Probleme lösen**: [Troubleshooting](Troubleshooting)

---

## ❓ FAQ

### Entities fehlen?

1. **Feature prüfen:**
   - Einstellungen → Geräte & Dienste → Violet Pool Controller
   - "..." → Konfiguration ändern
   - Feature aktivieren

2. **Home Assistant neu starten:**
   - Einstellungen → System → Neustart

3. **Browser-Cache leeren:**
   - STRG + UMSCHALT + ENTF

### Icon fehlt?

1. **Browser-Cache leeren:**
   - STRG + UMSCHALT + ENTF

2. **Home Assistant neu starten:**
   - Einstellungen → System → Neustart

3. **Entity-Registry prüfen:**
   - Einstellungen → Geräte & Dienste → Entities
   - Suche nach Entity

### Entity umbenennen?

1. Einstellungen → Geräte & Dienste → Entities
2. Entity suchen
3. "..." → Entity umbenennen
4. Neuen Namen eingeben

⚠️ **Achtung:** Umbenennen wirkt sich auf Automationen aus!

---

## 🔗 Nützliche Links

- 🎨 [Icon-Referenz](Icon-Reference) - Alle Icons im Detail
- 📖 [Konfigurationshilfe](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md)
- 🐛 [Troubleshooting](Troubleshooting)
- 🤖 [Services Guide](Services)

---

**🎉 Du kennst jetzt alle Entities!**

Viel Erfolg beim Erstellen von Automationen und Dashboards!
