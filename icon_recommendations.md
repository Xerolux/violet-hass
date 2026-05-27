# Optimized Icon Selection for Violet Pool Controller

Based on the official MDI library: https://pictogrammers.com/library/mdi/

## Top 10 MOST IMPORTANT Improvements ⭐

| Entity | Name | Current | ✅ Optimized | Reason |
|--------|------|---------|--------------|--------|
| `pH_value` | pH Value | `mdi:flask` | **`mdi:ph`** | There's a dedicated pH icon! |
| `onewire1_value` | Pool Water | `mdi:pool` | **`mdi:pool-thermometer`** | Pool + temperature perfectly combined |
| `ADC2_value` | Overflow Tank | `mdi:water-percent` | **`mdi:overflow`** | Overflow icon exists! |
| `onewire4_value` | Absorber Return | `mdi:pipe` | **`mdi:pipe-valve`** | With valve for return line |
| `DOS_6_FLOC_STATE` | Flocculation | `mdi:flask` | **`mdi:water-opacity`** | Water turbidity = flocculation |
| `SYSTEM_CPU_TEMPERATURE` | System CPU | `mdi:chip` | **`mdi:thermometer-check`** | Temp check is clearer |
| `ADC3_value` | Flow Meter | `mdi:pump` | **`mdi:swap-horizontal`** | Arrows indicate flow |
| `onewire5_value` | Heat Exchanger | `mdi:radiator` | **`mdi:heat-exchange`** | Dedicated icon |
| `CPU_TEMP` | CPU Temperature | `mdi:chip` | **`mdi:thermometer-alert`** | Chip + warning |
| `IMP1_value` | Flow Switch | `mdi:water-pump` | **`mdi:pipe-wrench`** | Pipe + mechanics |

## Detailed Analysis of All Categories

### 🌡️ TEMPERATURE SENSORS

| Entity | Name | Current | New | Alternatives |
|--------|------|---------|-----|--------------|
| `onewire1_value` | Pool Water | `mdi:pool` | **`mdi:pool-thermometer`** | `mdi:water-thermometer` |
| `onewire2_value` | Outdoor Temperature | `mdi:thermometer` | **`mdi:thermometer-lines`** | `mdi:weather-sunny` |
| `onewire3_value` | Solar Absorber | `mdi:solar-power` | **`mdi:solar-power-variant`** | `mdi:solar-panel` |
| `onewire4_value` | Absorber Return | `mdi:pipe` | **`mdi:pipe-valve`** | `mdi:pipe-wrench` |
| `onewire5_value` | Heat Exchanger | `mdi:radiator` | **`mdi:heat-exchange`** | `mdi:radiator` |
| `onewire6_value` | Heating Storage | `mdi:water-boiler` | **`mdi:tank-standpad`** | `mdi:barrel` |

### 🧪 WATER CHEMISTRY

| Entity | Name | Current | New | Alternatives |
|--------|------|---------|-----|--------------|
| `pH_value` | pH Value | `mdi:flask` | **`mdi:ph`** ⭐ | `mdi:science` |
| `orp_value` | Redox Potential | `mdi:flash` | **`mdi:lightning-bolt-circle`** | `mdi:lightning-bolt-outline` |
| `pot_value` | Chlorine Level | `mdi:test-tube` | **`mdi:water-plus`** | `mdi:water-check` |

### 📊 ANALOG SENSORS

| Entity | Name | Current | New | Alternatives |
|--------|------|---------|-----|--------------|
| `ADC1_value` | Filter Pressure | `mdi:gauge` | **`mdi:gauge-full`** | `mdi:speedometer` |
| `ADC2_value` | Overflow Tank | `mdi:water-percent` | **`mdi:overflow`** ⭐ | `mdi:water-alert` |
| `ADC3_value` | Flow Meter | `mdi:pump` | **`mdi:swap-horizontal`** | `mdi:arrow-left-right` |
| `ADC4_value` | Analog Sensor 4 | `mdi:gauge` | **`mdi:gauge-low`** | `mdi:chart-line` |
| `ADC5_value` | Analog Sensor 5 | `mdi:gauge` | **`mdi:chart-bell-curve`** | `mdi:sine-wave` |
| `IMP1_value` | Flow Switch | `mdi:water-pump` | **`mdi:pipe-wrench`** | `mdi:pipe-valve` |
| `IMP2_value` | Pump Flow Rate | `mdi:pump` | **`mdi:water-pump`** | `mdi:pump` |

### 💻 SYSTEM SENSORS

| Entity | Name | Current | New | Alternatives |
|--------|------|---------|-----|--------------|
| `CPU_TEMP` | CPU Temperature | `mdi:chip` | **`mdi:thermometer-alert`** | `mdi:chip-alert` |
| `CPU_TEMP_CARRIER` | Carrier Board | `mdi:expansion-card` | **`mdi:motherboard`** | `mdi:server` |
| `CPU_UPTIME` | System Uptime | `mdi:clock` | **`mdi:clock-time-eight`** | `mdi:clock-check` |
| `SYSTEM_CPU_TEMPERATURE` | System CPU | `mdi:chip` | **`mdi:thermometer-check`** ⭐ | `mdi:check-circle` |
| `SYSTEM_CARRIER_CPU_TEMPERATURE` | Carrier CPU | `mdi:expansion-card` | **`mdi:memory`** | `mdi:sd` |
| `SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE` | Dosing Module CPU | `mdi:chip` | **`mdi:memory-lan`** | `mdi:harddisk` |
| `SYSTEM_memoryusage` | Memory Usage | `mdi:memory` | **`mdi:memory-lan`** | `mdi:database` |

### ⚡ STATUS SENSORS

| Entity | Name | Current | New | Alternatives |
|--------|------|---------|-----|--------------|
| `PUMP` | Pump Status | `mdi:pump` | **`mdi:pump-on`** | `mdi:water-pump` |
| `HEATER` | Heater Status | `mdi:radiator` | **`mdi:radiator-disabled`** | `mdi:radiator-off` |
| `SOLAR` | Solar Status | `mdi:solar-power` | **`mdi:solar-power-variant-outline`** | `mdi:solar-power-large` |
| `BACKWASH` | Backwash Status | `mdi:refresh` | **`mdi:autorenew`** | `mdi:rotate-right` |
| `LIGHT` | Lighting Status | `mdi:lightbulb` | **`mdi:lightbulb-on`** | `mdi:lightbulb-outline` |
| `PVSURPLUS` | PV Surplus | `mdi:solar-power-variant` | **`mdi:solar-power`** | `mdi:battery-charging` |
| `FW` | Firmware Version | `mdi:package-up` | **`mdi:package-variant-closed`** | `mdi:archive` |

### 🧪 DOSING SENSORS

| Entity | Name | Current | New | Alternatives |
|--------|------|---------|-----|--------------|
| `DOS_1_CL_STATE` | Chlorine Status | `mdi:flask-outline` | **`mdi:flask-empty-outline`** | `mdi:bottle-tonic-plus` |
| `DOS_2_ELO_STATE` | Electrolysis | `mdi:lightning-bolt` | **`mdi:current-ac`** | `mdi:flash` |
| `DOS_4_PHM_STATE` | pH- Status | `mdi:flask-minus` | **`mdi:flask-empty-minus`** | `mdi:bottle-tonic-minus` |
| `DOS_5_PHP_STATE` | pH+ Status | `mdi:flask-plus` | **`mdi:flask-empty-plus`** | `mdi:bottle-tonic-plus` |
| `DOS_6_FLOC_STATE` | Flocculation | `mdi:flask` | **`mdi:water-opacity`** ⭐ | `mdi:water-plus` |

## My Recommendation

### Option 1: Top 10 Upgrade (Recommended) ⭐
Apply only the **10 most important changes**:
- Maximum improvement
- Manageable effort
- Stays consistent with the rest

### Option 2: Complete Upgrade (Optional)
Change **all 40+ icons** to the optimized variants:
- Best possible icon selection
- Higher effort
- Perfectly consistent

### Option 3: Outline Style (Modern)
Switch to **outline variants** of the optimized icons:
- `mdi:pool` → `mdi:pool-outline`
- `mdi:ph` → `mdi:ph-outline` (if available)
- More modern, lighter look

## Next Steps

Which option would you like?
1. **Top 10 Upgrade** - I'll implement the 10 most important improvements
2. **Complete Upgrade** - I'll optimize all icons
3. **Outline Style** - Modern look with outline variants
4. **Combination** - Top 10 + outline for selected icons
