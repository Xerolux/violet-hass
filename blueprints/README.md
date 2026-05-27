# 🛠️ Helper Setup Guide for Pool Blueprints

**Version:** 1.0.5 (2026-04-22)

## 📋 Overview
The blueprints require special **Helper entities** to store counters and timestamps. These must be created **before** using the blueprints.

## 🧪 Helpers for pH Control

### `input_number.pool_ph_dosing_counter`
**Purpose:** Counts daily pH dosing cycles as a safety measure

#### Step-by-Step Creation:

1. **Open Helper menu:**
   ```
   Settings → Devices & Services → Helpers → Create Helper
   ```

2. **Select "Number"**

3. **Enter configuration:**
   ```yaml
   Name: Pool pH Dosing Counter
   Entity ID: input_number.pool_ph_dosing_counter
   Icon: mdi:counter
   Minimum value: 0
   Maximum value: 50
   Step: 1
   Initial value: 0
   Unit of measurement: Dosing cycles
   Display mode: Box
   ```

4. **Click "Create"**

### Usage in Blueprint:
- Counts every pH+ and pH- dosing cycle
- Prevents more than X dosing cycles per day (safety)
- Automatically resets to 0 at midnight

---

## 🔄 Helpers for Backwash Control

### `input_datetime.pool_last_backwash`
**Purpose:** Stores the timestamp of the last backwash

#### Step-by-Step Creation:

1. **Open Helper menu:**
   ```
   Settings → Devices & Services → Helpers → Create Helper
   ```

2. **Select "Date and/or time"**

3. **Enter configuration:**
   ```yaml
   Name: Pool Last Backwash
   Entity ID: input_datetime.pool_last_backwash
   Icon: mdi:calendar-clock
   Has date: ✓ (enabled)
   Has time: ✓ (enabled)
   ```

4. **Click "Create"**

### `input_number.pool_pump_runtime_hours` (Optional)
**Purpose:** Counts pump runtime for runtime-based backwash control

#### Step-by-Step Creation:

1. **Create a "Number" Helper**

2. **Enter configuration:**
   ```yaml
   Name: Pool Pump Runtime Hours
   Entity ID: input_number.pool_pump_runtime_hours
   Icon: mdi:pump
   Minimum value: 0
   Maximum value: 500
   Step: 0.1
   Initial value: 0
   Unit of measurement: h
   Display mode: Box
   ```

### Usage in Blueprint:
- **Last Backwash:** Calculates days since last backwash
- **Runtime Hours:** Triggers backwash after X hours of pump runtime
- Automatically resets after backwash

---

## 📱 All Helpers at a Glance

### Quick Creation via YAML (Advanced)

For experienced users - add this configuration to your `configuration.yaml`:

{% raw %}
```yaml
# Pool Helper Entities
input_number:
  pool_ph_dosing_counter:
    name: "Pool pH Dosing Counter"
    min: 0
    max: 50
    step: 1
    initial: 0
    unit_of_measurement: "Dosing cycles"
    icon: mdi:counter

  pool_pump_runtime_hours:
    name: "Pool Pump Runtime Hours"
    min: 0
    max: 500
    step: 0.1
    initial: 0
    unit_of_measurement: "h"
    icon: mdi:pump

input_datetime:
  pool_last_backwash:
    name: "Pool Last Backwash"
    has_date: true
    has_time: true
    icon: mdi:calendar-clock
```
{% endraw %}

After adding: **Restart Home Assistant**

---

## 🎛️ Display Helpers on Dashboard (Optional)

### Lovelace Card for Pool Status:

```yaml
type: entities
title: Pool Automation
entities:
  - entity: input_number.pool_ph_dosing_counter
    name: pH Dosing today
  - entity: input_datetime.pool_last_backwash
    name: Last Backwash
  - entity: input_number.pool_pump_runtime_hours
    name: Pump Runtime
show_header_toggle: false
```

---

## ⚙️ Advanced Automations (Optional)

### Automatic Runtime Counter:

If you want to count pump runtime automatically:

{% raw %}
```yaml
# Automation for Pump Runtime Counter
automation:
  - alias: "Pool Pump Runtime Counter"
    trigger:
      - platform: state
        entity_id: switch.violet_pump
        to: 'off'
        for:
          minutes: 1
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: 'off'
    action:
      - service: input_number.set_value
        target:
          entity_id: input_number.pool_pump_runtime_hours
        data:
          value: >
            {% set runtime = states('input_number.pool_pump_runtime_hours') | float %}
            {% set last_on = states.switch.violet_pump.last_changed %}
            {% set duration = (now() - last_on).total_seconds() / 3600 %}
            {{ runtime + duration }}
```
{% endraw %}

### Daily Reset of pH Dosing Counter:

```yaml
# Automation for daily reset
automation:
  - alias: "Reset pH Dosing Counter Daily"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: input_number.set_value
        target:
          entity_id: input_number.pool_ph_dosing_counter
        data:
          value: 0
```

---

## 🚨 Troubleshooting

### Helper not visible:
```bash
# Developer Tools → States → Search for:
input_number.pool_ph_dosing_counter
input_datetime.pool_last_backwash
input_number.pool_pump_runtime_hours
```

### Blueprint error due to missing helpers:
```
Template error: input_number.pool_ph_dosing_counter not found
```
**Solution:** Create the helpers as described above

### Resetting a helper:
```yaml
# Via Developer Tools → Services
service: input_number.set_value
target:
  entity_id: input_number.pool_ph_dosing_counter
data:
  value: 0
```

### YAML method not working:
- Create helpers via UI (easier)
- Restart HA after YAML changes
- Check configuration.yaml for syntax errors

---

## 💡 Why Are Helpers Necessary?

### Data Persistence:
- **Without helpers:** Data is lost on HA restart
- **With helpers:** Values are permanently stored

### Safety:
- **pH Counter:** Prevents overdosing
- **Last Backwash:** Prevents too-frequent backwashing

### Intelligence:
- **Runtime Counter:** Enables runtime-based automation
- **Timestamp:** Calculation of intervals

Helpers are essential for safe and smart pool automation! 🏊‍♂️

---

## 📝 Version Notes

### Version 1.0.5 (2026-04-22)
- ✅ All blueprints updated with version information
- ✅ Entity selectors optimized for better integration support
- ✅ Notes about required helpers added to blueprint descriptions
- ⚠️ **Important:** `pool_backwash_control.yaml` additionally requires a separate script for the backwash cycle (see blueprint comments)

### Available Blueprints
1. **pool_temperature_control.yaml** - Smart temperature control with solar support
2. **pool_ph_control.yaml** - Automatic pH value control with dosing
3. **pool_cover_control.yaml** - Weather-dependent cover control
4. **pool_backwash_control.yaml** - Automatic backwash (requires additional script)

### Installation
1. Open Home Assistant → Settings → Automations & Scenes → Blueprints
2. Click "Import Blueprint"
3. Enter the URL of the desired blueprint (e.g. `https://github.com/xerolux/violet-hass/blob/main/blueprints/automation/pool_temperature_control.yaml`)
4. Create and configure the blueprint
