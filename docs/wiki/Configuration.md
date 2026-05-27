> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Configuration.de)**

---

# ⚙️ Configuration

> All configuration options explained – from basic setup to advanced settings.

---

## 🚨 SAFETY & LIABILITY (PLEASE READ FIRST!)

### ⚠️ IMPORTANT SAFETY NOTICES

**The Violet Pool Controller add-on controls real pool equipment:**

- ⚠️ **Pumps, heaters, and dosing systems can be remotely controlled**
- ⚠️ **Incorrect configuration can cause property damage**
- ⚠️ **Chemicals can be dangerous if mishandled**
- ⚠️ **Electrical systems must be installed in compliance with regulations**

### 🔒 YOUR RESPONSIBILITY

**Before configuring the integration:**

✅ **Read the complete liability disclaimer**: [📖 Configuration Guide (DE)](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md#-sicherheit--haftung)
✅ **Understand all safety mechanisms**
✅ **Keep manual emergency shutoffs available**
✅ **Observe all safety data sheets**
✅ **Consult a professional if unsure**

> **⚠️ Use is at your own responsibility and risk!**

---

## Configuration Overview

The Violet Pool Controller integration is configured entirely through the Home Assistant UI – no manual YAML configuration required.

```
Settings → Devices & Services → Violet Pool Controller → Options
```

---

## Connection Settings

### Host Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | String | – | IP address or hostname of the controller |
| `port` | Integer | 80 | TCP port (leave at 80 unless using a proxy) |
| `use_ssl` | Boolean | False | Use HTTPS instead of HTTP |
| `verify_ssl` | Boolean | True | Validate SSL certificate |

**Host Configuration Examples:**

```
HTTP (default):      Host: 192.168.1.100, Port: 80
HTTP Custom Port:    Host: 192.168.1.100, Port: 8080
HTTPS validated:     Host: 192.168.1.100, Port: 443 (verify_ssl=True)
HTTPS self-signed:   Host: 192.168.1.100, Port: 443 (verify_ssl=False)
Hostname:            Host: violet.local, Port: 80
```

> **Security notice**: Only use `verify_ssl=False` in trusted local networks!

### Authentication

| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | String | API username (leave empty if no auth) |
| `password` | String | API password |

Credentials are stored encrypted in the Home Assistant configuration.

---

## Poll Settings

### Polling Interval

```
Settings → Devices & Services → Violet → Options → Polling Interval
```

| Value | Behavior | Recommended For |
|-------|----------|-----------------|
| 10s | Very responsive, high controller load | Debugging |
| **20s** | **Standard recommendation** | Most users |
| 30s | Good balance | Multiple controllers |
| 45–60s | Low load, less responsive | Weak hardware/network |

The coordinator queries all sensors in a single request (`GET /getReadings?ALL`) to minimize controller load.

### Timeout

| Parameter | Default | Description |
|-----------|---------|-------------|
| `timeout` | 10s | Total request timeout |
| Connection timeout | 8s (80%) | Timeout for TCP connection setup |

Increase to 15–20s for slow networks.

### Retry Logic

| Parameter | Default | Description |
|-----------|---------|-------------|
| `retry_attempts` | 3 | Retries on error |
| Backoff | Exponential | 2s → 4s → 8s between attempts |

---

## Feature Configuration

### Enable/Disable Features

Features are configured in the setup flow and determine which entities are created:

```
Settings → Devices & Services → Violet → Options → Reconfigure Features
```

**Available Features:**

```
┌─────────────────────────────────────────────────────────┐
│                    FEATURE FLAGS                        │
├─────────────────┬───────────────────────────────────────┤
│ PUMP            │ Filter pump (always active)            │
│ HEATER          │ Pool heater / heat exchanger           │
│ SOLAR           │ Solar collector                        │
│ PV_SURPLUS      │ PV surplus mode                        │
│ DOSING_PH_MINUS │ pH- dosing pump                        │
│ DOSING_PH_PLUS  │ pH+ dosing pump                        │
│ DOSING_CHLORINE │ Chlorine dosing pump                   │
│ DOSING_FLOCCULANT│ Flocculant dosing pump                │
│ DMX             │ DMX lighting control (1–8)             │
│ DIGITAL_INPUTS  │ Digital inputs DI1–DI8                 │
│ COVER           │ Pool cover                             │
│ EXTENSION_RELAYS│ Extension relays REL1–REL8             │
│ BACKWASH        │ Backwash                               │
└─────────────────┴───────────────────────────────────────┘
```

---

## Logging Configuration

### Enable Debug Logging

In `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.violet_pool_controller: debug
    aiohttp: info
```

### Reduce Logging (Performance)

```yaml
logger:
  logs:
    custom_components.violet_pool_controller: warning
```

### Log Errors Only

```yaml
logger:
  logs:
    custom_components.violet_pool_controller: error
```

---

## Controller Name & Multi-Controller

For installations with multiple controllers, the **Controller Name** is important:

```
Settings → Add Integration → Controller Name: "Outdoor Pool"
```

| Recommendation | Example |
|----------------|---------|
| Unique & descriptive | `Outdoor Pool`, `Hot Tub`, `Indoor Pool` |
| Short (max. 2–3 words) | `Pool 1`, `Swimming Pond` |
| Not generic | ~~"Pool"~~, ~~"Controller"~~ |

The controller name determines:
- The **device name** in HA
- The **suggested area** (automatic grouping)
- The **entity prefix** (with unique naming)

→ More info: **[Multi-Controller Guide](Multi-Controller)**

---

## Dashboard Configuration

### Automatic Areas

Home Assistant automatically creates an area based on the controller name. All entities are assigned to this area.

### Recommended Dashboard Cards

**Sensor Overview:**
```yaml
type: entities
title: Pool Water Chemistry
entities:
  - entity: sensor.violet_water_temperature
    name: Water Temperature
  - entity: sensor.violet_ph_value
    name: pH Value
  - entity: sensor.violet_orp_value
    name: ORP/Redox
  - entity: sensor.violet_chlorine
    name: Chlorine Level
```

**Control Card:**
```yaml
type: glance
title: Pool Control
entities:
  - entity: switch.violet_pump
    name: Pump
  - entity: switch.violet_heater
    name: Heating
  - entity: switch.violet_solar
    name: Solar
  - entity: cover.violet_cover
    name: Cover
```

**Thermostat Card:**
```yaml
type: thermostat
entity: climate.violet_heater
name: Pool Heating
```

---

## Configuration Validation

The integration validates all inputs during setup and displays clear error messages:

| Error | Cause | Solution |
|-------|-------|----------|
| `cannot_connect` | Controller unreachable | Check IP/port |
| `invalid_auth` | Wrong password | Check credentials |
| `already_configured` | Same IP already configured | Remove existing integration |
| `ssl_error` | Certificate problem | Disable `verify_ssl` |

---

## Backup Configuration

### Create Backup (Before Changes)

```
Settings → System → Backups → Create Backup
```

### Export Configuration

The integration stores its configuration in:
```
/config/.storage/core.config_entries
```

This file is automatically backed up by HA backups.

---

## Reset & Reconfiguration

### Reconfigure Integration

1. **Settings → Devices & Services**
2. Select Violet Pool Controller
3. **"⋮" → "Reconfigure"** (or "Options")
4. Make changes
5. Save

### Remove and Re-add Integration Completely

1. **Settings → Devices & Services → Violet**
2. **"⋮" → "Delete"**
3. Re-add as during [initial installation](Installation-and-Setup)

> **Warning**: Deleting and recreating will regenerate entity IDs – you may need to update automations/dashboard cards!

---

## 🐛 Troubleshooting

### Cannot Establish Connection

**Error: "No connection to controller"**

**Solutions:**
1. **Check IP:**
   ```bash
   ping 192.168.1.100
   ```
2. **Check port:**
   ```bash
   # HTTP
   curl http://192.168.1.100
   # HTTPS
   curl https://192.168.1.100
   ```
3. **Check network:**
   - Are you on the same network?
   - Not on guest Wi-Fi?
   - Firewall not blocking?
4. **Toggle SSL/TLS:**
   - Enable or disable
   - Depending on controller configuration

### Authentication Failed

**Error: "Authentication failed"**

**Solutions:**
1. Check username and password
2. Note case sensitivity
3. Remove trailing spaces
4. Check on the controller:
   - Does the user exist?
   - Is the password correct?
5. Toggle SSL/TLS

### Entities Missing After Setup

**Problem: Not all entities are visible**

**Solutions:**
1. **Restart Home Assistant:**
   - Settings → System → Restart
2. **Clear browser cache:**
   - CTRL + SHIFT + DELETE
3. **Check entity registry:**
   - Settings → Devices & Services → Entities
   - Search for "violet_pool_controller"
4. **Disable features:**
   - Remove the integration
   - Add it again
   - Select only existing features

---

**Next:** [Sensors](Sensors) | [Device States](Device-States) | [Services](Services)
