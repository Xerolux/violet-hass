# Multi-Controller Support Guide

## ✨ Feature Overview

The Violet Pool Controller Integration now supports **multiple controllers simultaneously** in a single Home Assistant instance!

## 🎯 What's New?

### 1. **Controller Name Field**
- When adding a controller, you can now assign a unique name
- Examples: "Pool 1", "Pool 2", "Main Pool", "Hot Tub", etc.
- Default: "Violet Pool Controller" (for backward compatibility)

### 2. **Automatic Area Assignment**
- Each controller automatically gets its own area
- All entities of a controller are grouped together
- Visual separation in the dashboard

### 3. **Unique Entity IDs**
- Each controller has a separate `entry_id`
- Entities: `{entry_id}_{entity_key}` - automatically unique
- No conflicts between controllers

## 📋 Setup Instructions

### Adding a Controller

1. **Go to:** Settings → Devices & Services
2. **Click:** "Add Integration"
3. **Search for:** "Violet Pool Controller"
4. **Important:** Assign a **unique controller name**
   - ✅ "Pool 1", "Outdoor Pool", "Hot Tub"
   - ❌ Don't use the same name: "Violet Pool Controller"

### Multiple Controllers

Repeat the process for each additional controller:

```
Controller 1:
  - Name: "Outdoor Pool"
  - IP: 192.168.178.55
  - Area: "Outdoor Pool" (automatic)

Controller 2:
  - Name: "Hot Tub"
  - IP: 192.168.178.56
  - Area: "Hot Tub" (automatic)
```

## 🏗️ Technical Details

### Modified Files

1. **const.py**
   - New constant: `CONF_CONTROLLER_NAME`
   - Default: `DEFAULT_CONTROLLER_NAME = "Violet Pool Controller"`

2. **config_flow.py**
   - New field in connection setup: `CONF_CONTROLLER_NAME`
   - Entry title now uses controller name

3. **__init__.py**
   - Extracts `controller_name` from config entry
   - Passes to device

4. **device.py**
   - Stores `controller_name`
   - `device_info` uses:
     - `name`: Controller name (instead of device name)
     - `suggested_area`: Controller name for auto-grouping

### Entity Structure

```python
# Config Entry Unique ID (already unique per IP+Device-ID)
f"{ip_address}-{device_id}"

# Device Identifier
(DOMAIN, f"{api_url}_{device_id}")

# Entity Unique ID (automatically unique through entry_id)
f"{config_entry.entry_id}_{entity_key}"
```

## 🎨 Dashboard Organization

### Automatic Areas

Home Assistant automatically creates areas based on `suggested_area`:

```
📍 Outdoor Pool
  ├─ 🌡️ Pool Water Temperature
  ├─ 💧 pH Value
  ├─ 💦 Filter Pump
  └─ ...

📍 Hot Tub
  ├─ 🌡️ Pool Water Temperature
  ├─ 💧 pH Value
  ├─ 💦 Filter Pump
  └─ ...
```

### Dashboard View

Each controller appears as a separate device:

```yaml
# Example Dashboard Card
type: entities
title: All Pool Controllers
entities:
  - entity: sensor.outdoorpool_water_temp
  - entity: sensor.hottub_water_temp
```

## ✅ Best Practices

### Naming

- ✅ **Descriptive names:** "Outdoor Pool", "Hot Tub", "Pool Ground Floor"
- ✅ **Short & concise:** Maximum 2-3 words
- ❌ **Not generic:** "Pool 1", "Pool 2" only when really necessary

### Network

- Each controller needs its **own IP address**
- Make sure all controllers are on the **same network**
- **Static IPs** (DHCP reservation) recommended

### Performance

- Each controller has its **own coordinator**
- Polling intervals are **independent** of each other
- With many controllers: increase polling interval (e.g. 15-30s)

## 🔧 Troubleshooting

### Problem: Entities have identical names

**Solution:** Use unique controller names during setup

### Problem: Controller doesn't appear in separate area

**Solution:** Check that `controller_name` is correctly set in:
- Settings → Devices & Services → [Your Integration]

### Problem: Entity IDs overlap

**Solution:** This should **not** happen since `entry_id` is automatically unique.
If it does: Remove and re-add the controller.

## 📊 Upgrading from Previous Versions

### Existing Installation

Existing installations keep the default name:
- Controller Name: "Violet Pool Controller"
- Area: "Violet Pool Controller"

### Renaming

How to change the controller name afterwards:

1. Settings → Devices & Services
2. Find "Violet Pool Controller"
3. Click on the device
4. Click "Rename" (gear icon)
5. Assign new name

**Note:** This only changes the display name, not the area.
For a new area: Remove the integration and re-add it.

## 🚀 New Possibilities

### Automations

{% raw %}
```yaml
# Example: Sync pH values across all pools
automation:
  - alias: "Pool pH Sync"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoorpool_ph_value
        below: 7.0
    action:
      - service: notify.mobile_app
        data:
          message: "Outdoor pool pH too low! Hot tub: {{ states('sensor.hottub_ph_value') }}"
```
{% endraw %}

### Dashboard with Tabs

```yaml
# Example: Tabs for each pool
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: button
        name: Outdoor Pool
        tap_action:
          action: navigate
          navigation_path: /lovelace/outdoorpool
      - type: button
        name: Hot Tub
        tap_action:
          action: navigate
          navigation_path: /lovelace/hottub
```

## 📝 Changelog

### v0.2.1-beta.1 (2025-11-20)

✨ **New Features:**
- Multi-controller support with unique names
- Automatic area assignment (`suggested_area`)
- Improved visual separation in the dashboard

🔧 **Technical Changes:**
- New config option: `CONF_CONTROLLER_NAME`
- Device info now uses `controller_name`
- Entry title shows controller name

🛡️ **Backward Compatibility:**
- Existing installations continue to work
- Default name: "Violet Pool Controller"

## 💡 Tips

1. **Plan ahead:** Think of a consistent naming scheme
2. **Use areas:** Dashboard organization becomes much easier
3. **Dashboard templates:** Create a template for one pool, copy it for more
4. **Automations:** Use template sensors for cross-pool comparisons

## 🆘 Support

For questions or issues:
- **GitHub Issues:** https://github.com/xerolux/violet-hass/issues
- **Documentation:** https://github.com/xerolux/violet-hass/blob/main/README.md
