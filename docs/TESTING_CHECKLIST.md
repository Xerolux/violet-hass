# Testing Checklist for Violet Pool Controller Integration

## ✅ Automated Checks (Already performed)

- [x] **Ruff Linting**: No code quality issues
- [x] **MyPy Type Checking**: All type errors resolved
- [x] **Python Syntax**: All `.py` files syntactically correct
- [x] **manifest.json**: Valid JSON, all required fields present
- [x] **services.yaml**: Valid YAML, 7 services defined
- [x] **Translations**: 10 languages (de, en, es, fr, it, nl, pl, pt, ru, zh)
- [x] **Platforms**: All 6 platforms present

## 🧪 Manual Tests in Home Assistant

### 1. Installation & Setup

```bash
# In your Home Assistant installation:
cd /config/custom_components/
git clone https://github.com/Xerolux/violet-hass.git violet_pool_controller
# or manually copy the violet_pool_controller folder

# Restart Home Assistant
```

#### To test:
- [ ] Integration appears in "Add Integration"
- [ ] Configuration flow starts without errors
- [ ] IP address/hostname can be entered
- [ ] Connection to controller successful
- [ ] Features can be selected

### 2. Entity Verification

After successful configuration, the following entities should be available:

#### Sensors (sensor.*)
- [ ] Temperature sensors (Water, Pool, Solar, etc.)
- [ ] Water chemistry (pH, ORP, Chlorine)
- [ ] System diagnostics
- [ ] Analog inputs

#### Binary Sensors (binary_sensor.*)
- [ ] Digital inputs
- [ ] System alarms

#### Switches (switch.*)
- [ ] Pump (ON/OFF/AUTO)
- [ ] Heater (ON/OFF/AUTO)
- [ ] Solar (ON/OFF/AUTO)
- [ ] Dosing (Chlorine, pH-, pH+, Flocculant)
- [ ] DMX scenes
- [ ] Extension relays

#### Climate (climate.*)
- [ ] Heater thermostat
- [ ] Solar thermostat
- [ ] Temperature setpoints adjustable
- [ ] HVAC modes work

#### Cover (cover.*)
- [ ] Pool cover
- [ ] Open/Close/Stop commands

#### Number (number.*)
- [ ] Temperature setpoints
- [ ] pH/ORP setpoints

### 3. Testing Services

Go to **Developer Tools > Services** and test:

#### control_pump
```yaml
service: violet_pool_controller.control_pump
data:
  action: "on"
  speed: 75
```
- [ ] Pump turns on
- [ ] Speed is set
- [ ] Status update visible in entity

#### smart_dosing
```yaml
service: violet_pool_controller.smart_dosing
data:
  dosing_type: "chlorine"
  action: "manual"
  duration: 30
```
- [ ] Dosing starts
- [ ] Timer runs
- [ ] Safety lock is set

#### manage_pv_surplus
```yaml
service: violet_pool_controller.manage_pv_surplus
data:
  mode: "on"
```
- [ ] PV mode activated
- [ ] Status update visible

#### control_dmx_scenes
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  scene: "scene1"
  action: "on"
```
- [ ] DMX scene activated
- [ ] Lights respond

### 4. API Communication

#### Rate Limiting
- [ ] Rapid consecutive requests are throttled
- [ ] No 429 "Too Many Requests" errors
- [ ] Exponential backoff works

#### Error Handling
- [ ] Controller offline → Entities become "unavailable"
- [ ] Network errors are logged
- [ ] Auto-recovery after reconnection

#### Optimistic Updates
- [ ] Switches show new status immediately (optimistic)
- [ ] After API response, status is updated
- [ ] Attributes `optimistic_state` and `pending_update` present

### 5. State Interpretation

#### 3-State Switches (ON/OFF/AUTO)
Test with various raw values:
- [ ] "1", 1, "ON" → Status ON
- [ ] "0", 0, "OFF" → Status OFF
- [ ] "2", "AUTO", "A" → Status AUTO
- [ ] String states are correctly interpreted

#### Cover States
- [ ] "OPEN", "open", "1" → Cover open
- [ ] "CLOSED", "closed", "0" → Cover closed
- [ ] Intermediate positions detected

### 6. Logging & Debugging

Check Home Assistant logs (`/config/home-assistant.log`):

```bash
grep -i "violet" /config/home-assistant.log | tail -50
```

Watch for:
- [ ] No ERROR or CRITICAL messages
- [ ] INFO level shows normal operations
- [ ] DEBUG level (when enabled) shows details
- [ ] No Python tracebacks

### 7. Performance

- [ ] Coordinator update every 30s (default)
- [ ] CPU load < 5% normal
- [ ] Memory usage stable
- [ ] No memory leaks during long-term operation (24h+)

### 8. Edge Cases

#### Missing Data
- [ ] Empty API response → Default values
- [ ] Missing sensor keys → No crashes
- [ ] None values are handled

#### Invalid Inputs
- [ ] Too high temperature → Clamping/Warning
- [ ] Negative duration → Validation
- [ ] Invalid action → Error message

#### Concurrent Requests
- [ ] Multiple switches simultaneously → Queuing
- [ ] Rate limiter prevents overload
- [ ] No race conditions

### 9. Config Flow

#### Initial Setup
- [ ] IP/hostname validation
- [ ] Connection test works
- [ ] Feature discovery shows available features

#### Options Flow
- [ ] Update interval changeable
- [ ] Features can be enabled/disabled
- [ ] Changes are applied immediately

#### Migration
- [ ] Old configs are migrated (if present)
- [ ] No data loss

### 10. Translations

Change the language in Home Assistant and check:
- [ ] Entity names translated
- [ ] Service descriptions translated
- [ ] Error messages translated
- [ ] Config flow texts translated

## 🐛 Bug Reporting

If errors occur, collect:

1. **Home Assistant Version**
   ```bash
   cat /config/.HA_VERSION
   ```

2. **Integration Version**
   ```bash
   cat /config/custom_components/violet_pool_controller/manifest.json | grep version
   ```

3. **Relevant Logs**
   ```bash
   grep -i "violet" /config/home-assistant.log > violet_debug.log
   ```

4. **Config Entry Data** (from .storage/core.config_entries)

5. **API Response Sample** (anonymized)

## ✨ Type Fixes in This Update

The following type errors have been resolved:

1. ✅ Optional parameters in `utils_sanitizer.py`
2. ✅ Float/Int type mismatch in `utils_rate_limiter.py`
3. ✅ Dict return types in `const_devices.py`
4. ✅ Template string type in `api.py`
5. ✅ Attribute dict typing in `switch.py`
6. ✅ None checks in `sensor.py`
7. ✅ Temperature return type in `climate.py`
8. ✅ Safety interval cast in `services.py`

All MyPy type errors (except expected import-not-found) are resolved!
