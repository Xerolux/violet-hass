# Multi-Controller – Managing Multiple Pools

> Manage multiple Violet Pool Controllers simultaneously in a single Home Assistant installation.

---

## Overview

The Violet Pool Controller integration supports **unlimited controllers** in a single Home Assistant instance. Each controller gets its own coordinator, own entities, and its own area.

```
Home Assistant
├── Outdoor Pool (192.168.1.55)
│   ├── sensor.outdoor_pool_water_temperature
│   ├── switch.outdoor_pool_pump
│   └── climate.outdoor_pool_heater
│
├── Hot Tub (192.168.1.56)
│   ├── sensor.hot_tub_water_temperature
│   ├── switch.hot_tub_pump
│   └── climate.hot_tub_heater
│
└── Kids Pool (192.168.1.57)
    ├── sensor.kids_pool_water_temperature
    └── switch.kids_pool_pump
```

---

## Setup: Adding Multiple Controllers

### Step 1: Set Up the First Integration

If not already done: Follow [Installation & Setup](Installation-and-Setup).

### Step 2: Add Additional Controllers

1. **Settings** → **Devices & Services**
2. Click **"Add Integration"** (bottom right)
3. Search for **"Violet Pool Controller"**
4. Enter the connection details of the second controller
5. **Important:** Assign a **unique controller name**

### Step 3: Assign Unique Names

| Example | Good | Bad |
|---------|------|-----|
| Outdoor area | `Outdoor Pool` | `Pool` |
| Hot tub | `Hot Tub` | `Violet Pool Controller` |
| Kids pool | `Kids Pool` | `Pool 1` |

> **Tip:** The controller name becomes an area in Home Assistant and a prefix in entity names. Short, descriptive names are ideal.

---

## Technical Implementation

### Entity IDs

Each entity has a unique ID based on the `entry_id`:

```
{entry_id}_{entity_key}
```

Examples:
- `sensor.outdoor_pool_water_temperature`
- `sensor.hot_tub_water_temperature`
- `switch.outdoor_pool_pump`
- `switch.hot_tub_pump`

### Device Identifiers

```python
# Unique per IP + Device-ID
(DOMAIN, f"{api_url}_{device_id}")
```

### Automatic Area Assignment

Home Assistant automatically creates areas based on `suggested_area`:

```
📍 Outdoor Pool
  ├─ Pool Water Temperature
  ├─ pH Value
  ├─ Filter Pump
  └─ ...

📍 Hot Tub
  ├─ Pool Water Temperature
  ├─ pH Value
  ├─ Filter Pump
  └─ ...
```

---

## Dashboard Configuration

### Tabs for Each Pool

```yaml
# Lovelace configuration with tabs
views:
  - title: Outdoor Pool
    path: outdoor_pool
    cards:
      - type: entities
        title: Outdoor Pool – Sensors
        entities:
          - sensor.outdoor_pool_water_temperature
          - sensor.outdoor_pool_ph_value
          - sensor.outdoor_pool_orp_value
      - type: thermostat
        entity: climate.outdoor_pool_heater

  - title: Hot Tub
    path: hot_tub
    cards:
      - type: entities
        title: Hot Tub – Sensors
        entities:
          - sensor.hot_tub_water_temperature
          - sensor.hot_tub_ph_value
```

### Overview Card for All Pools

```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.outdoor_pool_water_temperature
        name: Outdoor Pool Temp.
      - type: entity
        entity: sensor.hot_tub_water_temperature
        name: Hot Tub Temp.

  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.outdoor_pool_ph_value
        name: Outdoor Pool pH
      - type: entity
        entity: sensor.hot_tub_ph_value
        name: Hot Tub pH
```

---

## Automations with Multiple Controllers

### Compare pH Values and Alert

```yaml
automation:
  - alias: "Multi-Pool: pH Comparison"
    trigger:
      - platform: numeric_state
        entity_id:
          - sensor.outdoor_pool_ph_value
          - sensor.hot_tub_ph_value
        below: 7.0
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool pH Alert"
          message: >
            Outdoor Pool: {{ states('sensor.outdoor_pool_ph_value') }} pH
            Hot Tub: {{ states('sensor.hot_tub_ph_value') }} pH
```

### Control All Pumps Simultaneously

```yaml
automation:
  - alias: "All pumps off at night"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.outdoor_pool_pump
            - switch.hot_tub_pump
            - switch.kids_pool_pump
```

### Cross-Pool Average Values

```yaml
# Template sensor for average temperature
template:
  - sensor:
      - name: "All Pools Average Temperature"
        unit_of_measurement: "°C"
        state: >
          {{ (
            states('sensor.outdoor_pool_water_temperature') | float(0) +
            states('sensor.hot_tub_water_temperature') | float(0)
          ) / 2 | round(1) }}
```

---

## Network Configuration

### Recommendations

| Aspect | Recommendation |
|--------|---------------|
| **IP Addresses** | Use static IPs (DHCP reservation) |
| **Network** | All controllers in the same subnet |
| **Polling Interval** | With 3+ controllers: 30-60 seconds |
| **SSL** | Consistent setting (all SSL or none) |

### DHCP Reservation (Router)

```
Home Network → Network → Network Connections → Device → Assign static IP
```

---

## Best Practices

### Naming

```
Good:
- "Outdoor Pool"       → sensor.outdoor_pool_*
- "Hot Tub"            → sensor.hot_tub_*
- "Pool Ground Floor"  → sensor.pool_ground_floor_*

Avoid:
- "Pool 1"             → too generic
- "Violet Pool"        → default name, not unique
```

### Performance

- **Stagger** polling times with different intervals
- With 2-3 controllers: 20-30s interval
- With 4+ controllers: 30-60s interval recommended

### Backup

Before adding additional controllers:
```
Settings → System → Backups → Create Backup
```

---

## Upgrade & Migration

### Rename Existing Installation

How to change the controller name after setup:

1. **Settings** → **Devices & Services**
2. Select "Violet Pool Controller"
3. Click on **Device Name** → Edit

> **Note:** This only changes the display name. For new entity IDs: Remove and re-add the integration.

### Migration from Single to Multi-Controller

1. Create a backup
2. Note all automations
3. Add second integration
4. Update automations with new entity IDs

---

## Troubleshooting

### Problem: Entities have identical names

**Cause:** Both controllers have the same name.

**Solution:**
1. Settings → Devices & Services
2. Rename controllers (unique names!)

### Problem: Controller does not appear in separate area

**Solution:** Check whether `controller_name` is correctly set in the config entry.

```
Settings → Devices & Services → [Integration] → Configure
```

### Problem: Too many API requests

**Solution:** Increase polling interval:
```
Settings → Devices & Services → Violet Pool Controller → Configure
→ Polling interval: 45 seconds
```

### Problem: One controller offline, others working

This is normal behavior! Each controller is independent. The failed controller shows `unavailable`, the others continue working.

---

## Support

- **GitHub Issues:** https://github.com/Xerolux/violet-hass/issues
- **Wiki:** [Troubleshooting](Troubleshooting)
- **FAQ:** [FAQ](FAQ)

---

*Last updated: 2026-02-23*