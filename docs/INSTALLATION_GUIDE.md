# Violet Pool Controller - Installation Guide

## Installation via HACS (recommended)

### Step 1: Add HACS Custom Repository

1. Open HACS in Home Assistant
2. Click the 3 dots (⋮) in the top right
3. Select "Custom repositories"
4. Add:
   - **Repository**: `https://github.com/PoolDigitalGmbH/violet-hass`
   - **Category**: Integration
5. Click "Add"

### Step 2: Install Integration

1. Go to HACS → Integrations
2. Search for "Violet Pool Controller"
3. Click "Download"
4. Restart Home Assistant

### Step 3: Configure Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Violet Pool Controller"
4. Enter connection details:
   - **Controller URL**: `http://192.168.178.55` (or your IP)
   - **Username**: `Basti` (your controller username)
   - **Password**: `your-password`
   - **Update Interval**: 30 seconds (default)

5. Click **Next**

### Step 4: Select Features

Select the features your pool has:
- ✅ **Pump** (filter pump)
- ✅ **Solar** (solar heating)
- ✅ **Heater** (heating)
- ✅ **Chlorine Control** (chlorine dosing)
- ✅ **pH Control** (pH dosing)
- ⬜ **Backwash** - if available
- ⬜ **Cover** (pool cover) - if available
- ⬜ **Light** (lighting) - if available
- ⬜ **DMX Scenes** (DMX lighting) - if available

### Step 5: Select Sensors (optional)

The integration automatically detects all available sensors. You can choose which ones to use:
- Temperature sensors (OneWire 1-12)
- Water chemistry (pH, ORP, Chlorine)
- Analog inputs (ADC1-6)
- System sensors (CPU, Memory, Uptime)
- Digital inputs (DI1-12)

### Step 6: Done!

The integration will now create all entities:
- **Switches**: `switch.violet_pump`, `switch.violet_solar`, etc.
- **Sensors**: `sensor.violet_pool_temperature`, `sensor.violet_ph_value`, etc.
- **Climate**: `climate.violet_heater`, `climate.violet_solar`
- **Number**: `number.violet_ph_setpoint`, `number.violet_orp_setpoint`, etc.
- **Binary Sensors**: `binary_sensor.violet_input_1`, etc.

---

## Manual Installation

### Step 1: Clone Repository

```bash
cd /config/custom_components
git clone https://github.com/PoolDigitalGmbH/violet-hass.git violet_pool_controller
```

### Step 2: Install Dependencies

The integration only uses `aiohttp`, which is already included in Home Assistant.

### Step 3: Restart Home Assistant

```bash
ha core restart
```

### Step 4: Configure Integration

Follow steps 3-6 from above.

---

## First Steps After Installation

### 1. Check Entities

Go to **Settings** → **Devices & Services** → **Violet Pool Controller**

You should see:
- **1 Device**: Violet Pool Controller
- **~50+ Entities**: Depending on selected features

### 2. Create Dashboard

Create a new dashboard for your pool:

**Example Cards:**

```yaml
# Pool Overview
type: entities
title: Pool Overview
entities:
  - entity: sensor.violet_pool_temperature
    name: Pool Water
  - entity: sensor.violet_outdoor_temperature
    name: Outdoor Temperature
  - entity: sensor.violet_solar_temperature
    name: Solar Absorber
  - entity: sensor.violet_ph_value
    name: pH Value
  - entity: sensor.violet_orp_value
    name: Redox
  - entity: sensor.violet_chlorine_level
    name: Chlorine

# Controls
type: entities
title: Pool Controls
entities:
  - entity: switch.violet_pump
    name: Filter Pump
  - entity: switch.violet_solar
    name: Solar
  - entity: switch.violet_heater
    name: Heater
  - entity: climate.violet_heater
    name: Heater Setpoint

# System Info
type: entities
title: System
entities:
  - entity: sensor.violet_firmware_version
  - entity: sensor.violet_cpu_uptime
  - entity: sensor.violet_cpu_temperature
  - entity: sensor.violet_memory_used
```

### 3. Create Automations

**Example: Turn on pump when frost is detected**

```yaml
automation:
  - alias: "Pool: Frost Protection"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_outdoor_temperature
        below: 2
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "off"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_pump
      - service: notify.mobile_app
        data:
          message: "Frost protection activated! Pump turned on at {{ states('sensor.violet_outdoor_temperature') }}°C"
```

**Example: Automatic solar heating control**

```yaml
automation:
  - alias: "Pool: Solar Auto"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.violet_solar_temperature') | float >
             states('sensor.violet_pool_temperature') | float + 3 }}
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_solar
```

---

## Advanced Configuration

### Adjust Update Interval

Default: 30 seconds

How to change:
1. **Settings** → **Devices & Services**
2. Click on "Violet Pool Controller"
3. Click **Configure**
4. Change "Update Interval"

**Recommendations:**
- **10-20 seconds**: If you need fast responses
- **30-60 seconds**: Normal operation (recommended)
- **120+ seconds**: Minimal load

### Rate Limiting

The integration automatically protects your controller:
- **Max. 10 requests per second**
- **Burst limit: 3 requests**
- **Priority Queue**: Important commands (switches) are prioritized

### Enable Logging

For debugging:

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.violet_pool_controller: debug
```

---

## Troubleshooting

### Problem: "Connection refused"

**Solution:**
- Check controller IP address
- Make sure controller is on the same network
- Test: `curl http://192.168.178.55/getReadings?ALL`

### Problem: "Authentication failed"

**Solution:**
- Check username and password
- Controller only supports Basic Auth
- Test: `curl -u "username:password" http://192.168.178.55/getReadings?ALL`

### Problem: Entities missing

**Solution:**
1. Go to **Configure**
2. Select **Re-select Features**
3. Activate missing features
4. Click **Reload**

### Problem: Values not updating

**Solution:**
- Check update interval
- Check logs: `tail -f /config/home-assistant.log | grep violet`
- Check controller reachability

### Problem: Switches not toggling

**Solution:**
- Check if controller is in **MANUAL** mode (not AUTO)
- Some outputs may be blocked by controller rules
- Check controller web interface for error messages

---

## Services

The integration provides the following services:

### `violet_pool_controller.control_pump`

Advanced pump control:

```yaml
service: violet_pool_controller.control_pump
data:
  speed: 2        # 1, 2, or 3
  duration: 3600  # seconds (optional)
  mode: "boost"   # "boost", "eco", "force_off", "auto"
```

### `violet_pool_controller.smart_dosing`

Manual dosing:

```yaml
service: violet_pool_controller.smart_dosing
data:
  dosing_type: "Chlor"  # "Chlor", "pH-", "pH+", "Flocculant"
  duration: 10          # seconds
```

**⚠️ WARNING:** Controller blocks direct dosing-ON commands for safety reasons!

### `violet_pool_controller.control_dmx_scenes`

Control DMX scenes:

```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  scene: 1     # 1-12
  state: "on"  # "on", "off", "auto"
```

---

## Supported Features

| Feature | Sensor | Switch | Climate | Number | Cover |
|---------|--------|--------|---------|--------|-------|
| Pump | ✅ | ✅ | - | - | - |
| Solar | ✅ | ✅ | ✅ | ✅ | - |
| Heater | ✅ | ✅ | ✅ | ✅ | - |
| Chlorine Dosing | ✅ | ✅ | - | ✅ | - |
| pH Dosing | ✅ | ✅ | - | ✅ | - |
| Backwash | ✅ | ✅ | - | - | - |
| Pool Cover | ✅ | - | - | - | ✅ |
| Lighting | ✅ | ✅ | - | - | - |
| DMX Scenes | ✅ | ✅ | - | - | - |
| Temperatures | ✅ | - | - | - | - |
| Water Chemistry | ✅ | - | - | ✅ | - |
| Digital Inputs | ✅ | - | - | - | - |
| System Info | ✅ | - | - | - | - |

---

## Support & Links

- **GitHub**: https://github.com/PoolDigitalGmbH/violet-hass
- **Issues**: https://github.com/PoolDigitalGmbH/violet-hass/issues
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License

MIT License - see [LICENSE](LICENSE)

**Note:** This integration is not officially endorsed by PoolDigital GmbH & Co. KG.
