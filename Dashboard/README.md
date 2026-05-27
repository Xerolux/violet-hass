# 📊 Violet Pool Controller - Dashboard Templates

This directory contains ready-made dashboard configurations for intuitive and clear control of your Violet Pool Controller in Home Assistant.

**Version:** 1.0.5 (2026-04-22)

## 📁 Available Dashboards

### 1. `pool_control_card.yaml` - Full Control
**Recommended for:** Desktop, tablets, main dashboard

**Features:**
- ✅ Full ON/OFF/AUTO control for pump, heater, solar
- ✅ Pump speed control
- ✅ Temperature setpoints and display
- ✅ pH and chlorine control with dosing control
- ✅ Temperature gauges for pool, solar, ambient
- ✅ 24h history graph for water chemistry
- ✅ Advanced control (lighting, PV surplus, cover)
- ✅ System status and connection monitoring

### 2. `pool_control_compact.yaml` - Compact View
**Recommended for:** Mobile devices, quick access, overview pages

**Features:**
- ✅ Essential control elements
- ✅ Water quality at a glance
- ✅ Connection status
- ✅ Optimized for small screens

### 3. `pool_control_ultimate.yaml` - Ultimate Control (Advanced)
**Recommended for:** Power users, full control

**⚠️ Requires Custom Cards via HACS:**
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom)
- [Slider Entity Row](https://github.com/thomasloven/lovelace-slider-entity-row)
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod)

**Features:**
- ✅ Detailed status displays for all devices
- ✅ Advanced dosing control with canister volume
- ✅ Runtime and range displays
- ✅ Visual status indicators (colors, icons)
- ✅ Frost protection detection

### 4. `VIOLET_CARD_EXAMPLES.yaml` - Custom Card Examples
**Note:** Examples for a hypothetical "violet-pool-card" Custom Card

**Features:**
- ✅ Various card types (pump, heater, solar, dosing)
- ✅ Compact, overview, and panel modes
- ✅ Layout examples (horizontal, grid, vertical)

## 🚀 Installation

### Method 1: Manual Copy (Recommended)

1. **Open Dashboard**
   - Open your Home Assistant Dashboard
   - Click the three dots (⋮) in the top right
   - Select "Edit"

2. **Add New Card**
   - Click "+ Add Card"
   - Scroll down and select "Manual" or click "Show Code Editor"

3. **Paste Configuration**
   - Open the desired YAML file (`pool_control_card.yaml` or `pool_control_compact.yaml`)
   - Copy the entire contents
   - Paste it into the code editor

4. **Adjust Entity IDs**
   - All dashboards use `violet_pool_controller` as the entity prefix by default
   - Replace this with your actual device name
   - This is especially important if you:
     - Have multiple pool controllers
     - Assigned a different name during installation
     - Example: `my_pool` instead of `violet_pool_controller`
   - **Entity Naming Scheme:**
     - Switches: `switch.{device_name}_{key}` (e.g. `switch.violet_pool_controller_pump`)
     - Sensors: `sensor.{device_name}_{key}` (e.g. `sensor.violet_pool_controller_ph_value`)
     - Number: `number.{device_name}_{key}` (e.g. `number.violet_pool_controller_pump_speed`)
     - Climate: `climate.{device_name}_{key}` (e.g. `climate.violet_pool_controller_heater`)

5. **Save**
   - Click "Save"
   - Exit edit mode

### Method 2: YAML Dashboard (For Advanced Users)

If you are using a YAML-based dashboard:

1. Open your `ui-lovelace.yaml` or the corresponding dashboard file
2. Add the card configuration under `views` → `cards`
3. Adjust the entity IDs
4. Save and reload

## 🎨 Customization

### Finding Entity IDs

If you are unsure which entity IDs to use:

1. Go to **Developer Tools** → **States**
2. Search for `violet` or `pool`
3. Note the full entity IDs (e.g. `select.violet_pool_controller_pump_mode`)
4. Use these IDs in the dashboard configuration

### Customizing Icons

You can change the icons as you wish. Search for available icons at:
- [Material Design Icons](https://pictogrammers.com/library/mdi/)

Example:
```yaml
- entity: select.violet_pool_controller_pump_mode
  name: Pump
  icon: mdi:pump  # ← You can change the icon here
```

### Colors and Thresholds (Gauges)

The gauge cards use color thresholds. Adjust these to your preferences:

```yaml
severity:
  green: 24  # Green above 24°C
  yellow: 20  # Yellow from 20-24°C
  red: 10     # Red below 20°C
```

## 🔧 Troubleshooting

### "Entity Not Found" Error

**Problem:** One or more entities cannot be found.

**Solution:**
1. Check if the corresponding feature is enabled:
   - Go to **Settings** → **Devices & Services**
   - Click "Violet Pool Controller"
   - Select "Configure"
   - Enable the required features
2. Check the entity IDs as described above
3. Remove entities you don't need from the configuration

### Cards Not Displayed Correctly

**Problem:** Cards are too large/small or cluttered.

**Solution:**
1. Use `pool_control_compact.yaml` for mobile devices
2. Use `pool_control_card.yaml` for desktop/tablet
3. Adjust `hours_to_show` in the history graph (default: 24h)

### Missing Entities

**Problem:** Not all sensors/controls are displayed.

**Solution:**
1. Make sure the features are enabled in the integration
2. Wait for the next update cycle (default: every 10 seconds)
3. Check the logs: **Settings** → **System** → **Logs**

## 📱 Mobile Optimization

For the best mobile experience:

1. Use `pool_control_compact.yaml`
2. Create a separate dashboard specifically for mobile devices:
   - Go to **Settings** → **Dashboards**
   - Click "+ Add Dashboard"
   - Select "Mobile" as the name
   - Add only the compact card
3. Enable "Optimize for mobile app" in the dashboard settings

## 🎯 Advanced Features

### Linking Automations

You can combine dashboard elements with automations:

```yaml
# Example: Notification for low pH value
automation:
  - alias: "Pool: pH value too low"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        below: 7.0
    action:
      - service: notify.mobile_app
        data:
          message: "Pool pH value too low: {{ states('sensor.violet_pool_controller_ph_value') }}"
```

### Conditional Cards

Show cards only when certain conditions are met:

```yaml
type: conditional
conditions:
  - entity: select.violet_pool_controller_pump_mode
    state: "on"
card:
  type: entities
  entities:
    - entity: sensor.violet_pool_controller_pump_runtime
      name: Runtime since start
```

## 💡 Tips

1. **Grouping:** Entities are automatically grouped by function (control, water quality, system)
2. **Entity Categories:** Configuration elements (modes, setpoints) are categorized as "CONFIG"
3. **State Colors:** `state_color: true` colors entities based on their state
4. **Updates:** Dashboard templates are updated with integration updates

## 🆘 Support

If you encounter issues:
1. Check the [integration documentation](../README.md)
2. Create a [GitHub Issue](https://github.com/Xerolux/violet-hass/issues)
3. Share your dashboard configuration and error logs

## 📝 License

These dashboard templates are part of the Violet Pool Controller integration and are licensed under the same license.
