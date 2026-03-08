# Optimierte Icon-Auswahl für Violet Pool Controller

Basierend auf der offiziellen MDI-Bibliothek: https://pictogrammers.com/library/mdi/

## Top 10 WICHTIGSTE Verbesserungen ⭐

| Entity | Name | Aktuell | ✅ Optimiert | Grund |
|--------|------|---------|--------------|-------|
| `pH_value` | pH-Wert | `mdi:flask` | **`mdi:ph`** | Es gibt ein echtes pH-Icon! |
| `onewire1_value` | Beckenwasser | `mdi:pool` | **`mdi:pool-thermometer`** | Pool + Temperatur perfekt kombiniert |
| `ADC2_value` | Überlaufbehälter | `mdi:water-percent` | **`mdi:overflow`** | Overflow-Icon existiert! |
| `onewire4_value` | Absorber-Rücklauf | `mdi:pipe` | **`mdi:pipe-valve`** | Mit Ventil für Rücklauf |
| `DOS_6_FLOC_STATE` | Flockung | `mdi:flask` | **`mdi:water-opacity`** | Wasser-Trübung = Flockung |
| `SYSTEM_CPU_TEMPERATURE` | System CPU | `mdi:chip` | **`mdi:thermometer-check`** | Temp-Check ist klarer |
| `ADC3_value` | Durchflussmesser | `mdi:pump` | **`mdi:swap-horizontal`** | Pfeile zeigen Durchfluss |
| `onewire5_value` | Wärmetauscher | `mdi:radiator` | **`mdi:heat-exchange`** | Spezielles Icon |
| `CPU_TEMP` | CPU Temperatur | `mdi:chip` | **`mdi:thermometer-alert`** | Chip + Warnung |
| `IMP1_value` | Flow-Switch | `mdi:water-pump` | **`mdi:pipe-wrench`** | Rohr + Mechanik |

## Detailanalyse aller Kategorien

### 🌡️ TEMPERATUR-SENSOREN

| Entity | Name | Aktuell | Neu | Alternativen |
|--------|------|---------|-----|--------------|
| `onewire1_value` | Beckenwasser | `mdi:pool` | **`mdi:pool-thermometer`** | `mdi:water-thermometer` |
| `onewire2_value` | Außentemperatur | `mdi:thermometer` | **`mdi:thermometer-lines`** | `mdi:weather-sunny` |
| `onewire3_value` | Solarabsorber | `mdi:solar-power` | **`mdi:solar-power-variant`** | `mdi:solar-panel` |
| `onewire4_value` | Absorber-Rücklauf | `mdi:pipe` | **`mdi:pipe-valve`** | `mdi:pipe-wrench` |
| `onewire5_value` | Wärmetauscher | `mdi:radiator` | **`mdi:heat-exchange`** | `mdi:radiator` |
| `onewire6_value` | Heizungs-Speicher | `mdi:water-boiler` | **`mdi:tank-standpad`** | `mdi:barrel` |

### 🧪 WASSERCHEMIE

| Entity | Name | Aktuell | Neu | Alternativen |
|--------|------|---------|-----|--------------|
| `pH_value` | pH-Wert | `mdi:flask` | **`mdi:ph`** ⭐ | `mdi:science` |
| `orp_value` | Redoxpotential | `mdi:flash` | **`mdi:lightning-bolt-circle`** | `mdi:lightning-bolt-outline` |
| `pot_value` | Chlorgehalt | `mdi:test-tube` | **`mdi:water-plus`** | `mdi:water-check` |

### 📊 ANALOGE SENSOREN

| Entity | Name | Aktuell | Neu | Alternativen |
|--------|------|---------|-----|--------------|
| `ADC1_value` | Filterdruck | `mdi:gauge` | **`mdi:gauge-full`** | `mdi:speedometer` |
| `ADC2_value` | Überlaufbehälter | `mdi:water-percent` | **`mdi:overflow`** ⭐ | `mdi:water-alert` |
| `ADC3_value` | Durchflussmesser | `mdi:pump` | **`mdi:swap-horizontal`** | `mdi:arrow-left-right` |
| `ADC4_value` | Analogsensor 4 | `mdi:gauge` | **`mdi:gauge-low`** | `mdi:chart-line` |
| `ADC5_value` | Analogsensor 5 | `mdi:gauge` | **`mdi:chart-bell-curve`** | `mdi:sine-wave` |
| `IMP1_value` | Flow-Switch | `mdi:water-pump` | **`mdi:pipe-wrench`** | `mdi:pipe-valve` |
| `IMP2_value` | Pumpen-Durchfluss | `mdi:pump` | **`mdi:water-pump`** | `mdi:pump` |

### 💻 SYSTEM-SENSOREN

| Entity | Name | Aktuell | Neu | Alternativen |
|--------|------|---------|-----|--------------|
| `CPU_TEMP` | CPU Temperatur | `mdi:chip` | **`mdi:thermometer-alert`** | `mdi:chip-alert` |
| `CPU_TEMP_CARRIER` | Carrier Board | `mdi:expansion-card` | **`mdi:motherboard`** | `mdi:server` |
| `CPU_UPTIME` | System Uptime | `mdi:clock` | **`mdi:clock-time-eight`** | `mdi:clock-check` |
| `SYSTEM_CPU_TEMPERATURE` | System CPU | `mdi:chip` | **`mdi:thermometer-check`** ⭐ | `mdi:check-circle` |
| `SYSTEM_CARRIER_CPU_TEMPERATURE` | Carrier CPU | `mdi:expansion-card` | **`mdi:memory`** | `mdi:sd` |
| `SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE` | Dosiermodul CPU | `mdi:chip` | **`mdi:memory-lan`** | `mdi:harddisk` |
| `SYSTEM_memoryusage` | Memory Usage | `mdi:memory` | **`mdi:memory-lan`** | `mdi:database` |

### ⚡ STATUS-SENSOREN

| Entity | Name | Aktuell | Neu | Alternativen |
|--------|------|---------|-----|--------------|
| `PUMP` | Pumpen-Status | `mdi:pump` | **`mdi:pump-on`** | `mdi:water-pump` |
| `HEATER` | Heizungs-Status | `mdi:radiator` | **`mdi:radiator-disabled`** | `mdi:radiator-off` |
| `SOLAR` | Solar-Status | `mdi:solar-power` | **`mdi:solar-power-variant-outline`** | `mdi:solar-power-large` |
| `BACKWASH` | Rückspül-Status | `mdi:refresh` | **`mdi:autorenew`** | `mdi:rotate-right` |
| `LIGHT` | Beleuchtung Status | `mdi:lightbulb` | **`mdi:lightbulb-on`** | `mdi:lightbulb-outline` |
| `PVSURPLUS` | PV-Überschuss | `mdi:solar-power-variant` | **`mdi:solar-power`** | `mdi:battery-charging` |
| `FW` | Firmware Version | `mdi:package-up` | **`mdi:package-variant-closed`** | `mdi:archive` |

### 🧪 DOSIER-SENSOREN

| Entity | Name | Aktuell | Neu | Alternativen |
|--------|------|---------|-----|--------------|
| `DOS_1_CL_STATE` | Chlor Status | `mdi:flask-outline` | **`mdi:flask-empty-outline`** | `mdi:bottle-tonic-plus` |
| `DOS_2_ELO_STATE` | Elektrolyse | `mdi:lightning-bolt` | **`mdi:current-ac`** | `mdi:flash` |
| `DOS_4_PHM_STATE` | pH- Status | `mdi:flask-minus` | **`mdi:flask-empty-minus`** | `mdi:bottle-tonic-minus` |
| `DOS_5_PHP_STATE` | pH+ Status | `mdi:flask-plus` | **`mdi:flask-empty-plus`** | `mdi:bottle-tonic-plus` |
| `DOS_6_FLOC_STATE` | Flockung | `mdi:flask` | **`mdi:water-opacity`** ⭐ | `mdi:water-plus` |

## Meine Empfehlung

### Option 1: Top 10 Upgrade (Empfohlen) ⭐
Führe nur die **10 wichtigsten Änderungen** durch:
- Maximale Verbesserung
- Überschaubarer Aufwand
- Bleibt konsistent mit dem Rest

### Option 2: Komplettes Upgrade (Optional)
Ändere **alle 40+ Icons** zu den optimierten Varianten:
- Bestmögliche Icon-Auswahl
- Höherer Aufwand
- Perfekt konsistent

### Option 3: Outline-Stil (Modern)
Ändere zu **Outline-Varianten** der optimierten Icons:
- `mdi:pool` → `mdi:pool-outline`
- `mdi:ph` → `mdi:ph-outline` (falls verfügbar)
- Modernerer, leichterer Look

## Nächste Schritte

Welche Option möchtest du?
1. **Top 10 Upgrade** - Ich implementiere die 10 wichtigsten Verbesserungen
2. **Komplettes Upgrade** - Ich optimiere alle Icons
3. **Outline-Stil** - Moderner Look mit Outline-Varianten
4. **Kombination** - Top 10 + Outline für ausgewählte Icons
