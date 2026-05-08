# ⚠️ IMPORTANT: Integration must be completely reinstalled!

## Problem
The current installation has `selected_sensors: []` saved in the config.
As a result, only ~108 entities are created instead of the expected ~156.

## Solution: Complete Reinstallation

### Step 1: Completely remove the integration
1. Open **Settings** → **Devices & Services**
2. Search for **Violet Pool Controller**
3. Click the **3 dots** (⋮) on the right
4. Select **Delete**
5. Confirm the deletion

### Step 2: Restart Home Assistant
1. Open **Developer Tools** → **YAML**
2. Click **Reload all YAML configuration**
3. OR: **Settings** → **System** → **Restart**

### Step 3: Add the integration again
1. Open **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for **"Violet Pool Controller"**
4. Click on it

### Step 4: Run through Setup

#### 4.1 Connection
- **IP Address**: 192.168.178.55 (or your IP)
- **Use SSL**: false (or true, depending on setup)
- **Username/Password**: (if required)
- **Device ID**: 1 (default)
- **Polling Interval**: 10 seconds (default)
- **Timeout**: 10 seconds
- **Retry Attempts**: 3
- Click **Next**

#### 4.2 Pool Setup
- **Pool Size**: 50 m³ (or your size)
- **Pool Type**: Outdoor pool, Indoor pool, etc.
- **Disinfection Method**: Chlorine, Salt, etc.
- Click **Next**

#### 4.3 Feature Selection
✅ **Activate the features you use**:
- [x] Heater control
- [x] Solar absorber
- [x] pH control
- [x] Chlorine management
- [x] Cover control (if available)
- [x] Backwash automation
- [x] Filter pump
- [ ] PV surplus (only if you have PV)
- [ ] LED lighting (only if available)
- [ ] Water refill (only if available)
- [ ] Digital inputs (only if used)
- [ ] Extension modules (only if available)

Click **Next**

#### 4.4 Sensor Selection
⚠️ **IMPORTANT**:

**Option A - ALL Sensors (Recommended):**
- Leave **ALL dropdown fields EMPTY**
- Do **NOT** select anything
- Simply click **Finish**
- → **ALL available sensors** will be created (~156 entities)

**Option B - Specific Sensors:**
- Select only the sensor groups you need
- For example: PUMP, SOLAR, HEATER, onewire1-12, etc.
- Click **Finish**

### Step 5: Verify Results

After setup you should see:
- **~156 entities** (with Option A - all sensors)
- **Firmware**: 1.1.8 (displayed correctly)
- **Pump Binary Sensor**: ON (if PUMP=3)
- **Pump Switch**: ON (if PUMP=3)
- **All temperature sensors** (onewire1-12)
- **Chemistry sensors** (pH, ORP, Chlorine)
- **System sensors** (CPU temp, Memory, etc.)
- **Runtime sensors**
- **Status sensors**

## Why Simply Reloading Does NOT Work

The problem is that the old config contains `selected_sensors: []`.
Even with the fix, this old config continues to be used.
Only a **reinstallation** creates a fresh config with `selected_sensors: None`.

## After Reinstallation

### Pump should display correctly:
- **PUMP**: 3 (value from API)
- **PUMP Binary Sensor**: ON (interpreted as STATE_MAP[3] = True)
- **PUMP Switch**: ON (interpreted as STATE_MAP[3] = True)
- **PUMPSTATE**: "3|PUMP_ANTI_FREEZE" (extended info)

### All sensors should be present:
- onewire1 through onewire12 (temperatures)
- pH_value, orp_value, pot_value
- PUMP_RUNTIME, SOLAR_RUNTIME, etc.
- CPU_TEMP, SYSTEM_MEMORY, etc.
- All DOS_* sensors
- All EXT1_*, EXT2_* sensors
- All timestamp sensors

---

**If you still have problems after reinstallation, please report them!**
