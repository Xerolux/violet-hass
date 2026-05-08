# 📦 Installation & Setup

> Step-by-step guide to installing the Violet Pool Controller add-on in Home Assistant.

---

## ⚠️ IMPORTANT - BEFORE INSTALLATION

### 🔒 Safety & Liability Disclaimer

**The Violet Pool Controller add-on controls real pool equipment:**

- ⚠️ **Pumps, heaters, and dosing systems can be remotely controlled**
- ⚠️ **Incorrect configuration can cause property damage**
- ⚠️ **Chemicals can be dangerous if mishandled**
- ⚠️ **Electrical systems must be installed in compliance with regulations**

**Before you install:**

✅ **Read the complete liability disclaimer**: [Configuration Guide (DE)](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md#-sicherheit--haftung)
✅ **Understand all safety mechanisms**
✅ **Keep manual emergency shutoffs available**
✅ **Observe all safety data sheets**
✅ **Consult a professional if unsure**

> **⚠️ Use is at your own responsibility and risk!**

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Home Assistant | 2026.5.0 | 2026.x (current) |
| Python | 3.14.2 | 3.14.2+ |
| Network | Controller reachable via HTTP | Static IP address (DHCP reservation) |
| HACS | Optional | Recommended for easy updates |
| Storage | <10 MB | – |

> **Note**: HA 2026.x is fully supported and is the recommended version.

---

## Method 1: HACS (Recommended)

HACS (Home Assistant Community Store) enables easy installation and automatic updates.

### Step 1: Install HACS (if not already installed)

If HACS is not yet installed, follow the [official HACS installation guide](https://hacs.xyz/docs/setup/download).

### Step 2: Add Repository

1. Open **HACS** in Home Assistant
2. Click the **three dots (⋮)** in the top right
3. Select **"Custom Repositories"**
4. Enter the following:
   - **Repository URL**: `https://github.com/Xerolux/violet-hass`
   - **Category**: `Integration`
5. Click **"Add"**

### Step 3: Install Integration

1. Go to **"Integrations"** in HACS
2. Search for **"Violet Pool Controller"**
3. Click the card and then click **"Download"**
4. Confirm the installation

### Step 4: Restart Home Assistant

```
Settings → System → Restart → Restart Home Assistant
```

Or via Docker:
```bash
docker restart homeassistant
```

### Step 5: Add Integration

1. Go to **Settings → Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Violet Pool Controller"**
4. Follow the [Setup Wizard](#setup-wizard)

---

## Method 2: Manual Installation

For users without HACS or developers.

### Option A: Via Git

```bash
# Navigate to the custom_components directory
cd /config/custom_components/

# Clone the repository
git clone https://github.com/Xerolux/violet-hass.git temp_violet

# Copy only the integration folder
cp -r temp_violet/custom_components/violet_pool_controller ./

# Remove the temp folder
rm -rf temp_violet
```

### Option B: Via ZIP Download

1. Go to: https://github.com/Xerolux/violet-hass/releases/latest
2. Download `violet_pool_controller.zip` (or `Source code.zip`)
3. Extract the archive
4. Copy the folder `custom_components/violet_pool_controller` to `/config/custom_components/`

```bash
# Example (adjust to your download path)
unzip violet-hass-main.zip
cp -r violet-hass-main/custom_components/violet_pool_controller /config/custom_components/
```

### Step 3: Restart Home Assistant

After manual installation, Home Assistant **must** be restarted.

### Step 4: Add Integration

Same as the HACS method: **Settings → Devices & Services → + Integration → "Violet Pool Controller"**

---

## Setup Wizard

The built-in setup wizard guides you through all configuration steps.

### Step 1: 🚨 DISCLAIMER (LIABILITY WAIVER)

⚠️ **VERY IMPORTANT - PLEASE READ CAREFULLY!**

You will see a **comprehensive liability disclaimer** with:

- **⚠️ Safety Warning**: All risks of usage
- **🔒 Your Responsibility**: What you must do
- **⚖️ Liability Disclaimer**: No warranty
- **📖 Documentation**: Links to detailed help

**You must:**
1. ✅ Read the entire text
2. ✅ Check the box at **"I accept"**
3. ✅ Click **"Confirm"**

**Without confirmation, you cannot set up the integration!**

### Step 2: Controller Connection

```
┌──────────────────────────────────────────┐
│  Violet Pool Controller – Connection     │
├──────────────────────────────────────────┤
│  Host (IP or Hostname):                  │
│  ┌────────────────────────────────────┐  │
│  │ 192.168.1.100                      │  │
│  └────────────────────────────────────┘  │
│                                          │
│  Port:            [80      ]             │
│  Use SSL:         [ ] No   [x] Yes       │
│  Verify SSL:      [x] Yes  [ ] No       │
│  Username:        [admin   ]             │
│  Password:        [••••••••]             │
│  Controller Name: [Violet Pool Controller]│
└──────────────────────────────────────────┘
```

| Field | Description | Example |
|-------|-------------|---------|
| **Host** | IP address or hostname of the controller | `192.168.1.100` or `violet.local` |
| **Port** | HTTP/HTTPS port (default: 80) | `80`, `443`, `8080` |
| **SSL** | Use HTTPS connection | Enable when using HTTPS |
| **Verify SSL** | Validate certificate | Disable only for self-signed certificates |
| **Username** | API username (if configured) | `admin` |
| **Password** | API password (if configured) | – |
| **Controller Name** | Display name (important for multiple controllers!) | `Outdoor Pool`, `Hot Tub` |

> **Finding the IP address**: Open your router admin panel (e.g. `192.168.1.1`) → "Connected Devices" → search for "Violet". Alternatively: `ping violet.local`

### Step 3: Pool Data

1. **Pool Volume**: In m³ (e.g. 40)
2. **Pool Type**: Swimming pool, sports pool, etc.
3. **Disinfection Method**: Chlorine, active oxygen, etc.

### Step 4: Select Features

Select the features your controller supports:

| Feature | Enable when... |
|---------|----------------|
| **Heating** | A heat exchanger or heater is connected |
| **Solar** | Solar collector is present |
| **PV Surplus** | Solar system for surplus usage |
| **pH Dosing** | pH- or pH+ dosing pump is connected |
| **Chlorine Dosing** | Chlorine dosing pump is connected |
| **Flocculant** | Flocculant dosing pump is present |
| **DMX Lighting** | Pool lighting is controlled via DMX |
| **Digital Inputs** | DI1–DI8 for external sensors/switches |
| **Cover** | Pool cover with control |
| **Extension Relays** | Additional relay modules (REL1–REL8) |
| **Backwash** | Automatic backwash configured |

> **Tip**: Features can be adjusted later via **Settings → Devices & Services → Violet → Options → Reconfigure**.

### Step 5: Set Polling Interval

The polling interval determines how often data is fetched from the controller:

| Interval | Advantages | Disadvantages |
|----------|------------|---------------|
| 10–15 seconds | Very responsive | Higher load on controller |
| **20–30 seconds** | **Good balance (recommended)** | – |
| 45–60 seconds | Minimal load | Less responsive |

---

## Advanced Settings

These settings are accessible via **Settings → Devices & Services → Violet → Options**.

| Option | Default | Description |
|--------|---------|-------------|
| `Polling Interval` | 30s | Polling interval in seconds |
| `Timeout` | 10s | Request timeout (80% for connection) |
| `Retry Attempts` | 3 | Number of retries on error |
| `Verify SSL` | On | Validate SSL certificate |

---

## After Installation

### Recommended First Steps

1. **Set up dashboard** – Create a new dashboard view for your pool
2. **Test automations** – Check if sensors show correct values
3. **Check logs** – Make sure no errors appear:
   ```
   Settings → System → Logs → search for "violet"
   ```

### Check Available Entities

After installation you can find all entities under:
```
Settings → Devices & Services → Violet Pool Controller → [Device] → Entities
```

Or directly: **Developer Tools → States** → search for `violet_pool_controller`

---

## Uninstallation

### With HACS

1. **HACS → Integrations → Violet Pool Controller**
2. Click **"Remove"**
3. Go to **Settings → Devices & Services**
4. Remove the Violet Pool Controller integration
5. Restart Home Assistant

### Manually

```bash
# Remove integration
rm -rf /config/custom_components/violet_pool_controller

# Restart Home Assistant
docker restart homeassistant  # or via HA UI
```

> **Note**: Your automations and dashboard configurations will be preserved but will no longer function without the add-on.

---

## Upgrading from an Older Version

### With HACS (Automatic)

1. **HACS → Integrations** → "Violet Pool Controller" → **"Update"**
2. Restart Home Assistant
3. For breaking changes: check integration config

### Manually

```bash
cd /config/custom_components/violet_pool_controller
git pull origin main
# or re-download ZIP and replace
```

### Note Breaking Changes

Check the **[Changelog](Changelog)** before every update! Major updates may require reconfiguration.

---

## Common Installation Problems

| Problem | Cause | Solution |
|---------|-------|----------|
| Integration doesn't appear | HA not restarted | Restart HA |
| "Connection failed" | Wrong IP or port | Check IP, test with `ping` |
| SSL error | Self-signed certificate | Disable "Verify SSL" |
| "Duplicate Integration" | Same IP already configured | Remove existing integration |
| No entities | Features not activated | Re-run setup wizard |

---

**Next:** [Configuration](Configuration) | [Sensors](Sensors) | [Troubleshooting](Troubleshooting)
