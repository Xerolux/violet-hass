# Auto-Discovery Guide 🔍

**Automatic Controller Detection for Violet Pool Controller**

---

## Overview

This guide explains how to use the **ZeroConf/mDNS auto-discovery** feature of the Violet Pool Controller integration. Auto-discovery allows Home Assistant to automatically find your Violet Pool Controller on the network, eliminating the need to manually enter IP addresses.

---

## Table of Contents

1. [What is ZeroConf?](#what-is-zeroconf)
2. [How Auto-Discovery Works](#how-auto-discovery-works)
3. [Setup Requirements](#setup-requirements)
4. [Using Auto-Discovery](#using-auto-discovery)
5. [Troubleshooting](#troubleshooting)
6. [Network Configuration](#network-configuration)
7. [Manual Fallback](#manual-fallback)

---

## What is ZeroConf?

### ZeroConf (mDNS/Bonjour)

**ZeroConf** (Zero Configuration Networking) is a set of technologies that allow devices to automatically discover each other on a local network without manual configuration.

**Also Known As**:
- mDNS (multicast DNS)
- Bonjour (Apple)
- Avahi (Linux)
- SSDP (Microsoft - similar concept)

### How It Works

```
┌─────────────────────────────────────────────────┐
│              Local Network (192.168.x.x)        │
│                                                 │
│  ┌──────────────┐      mDNS broadcast      ┌──────────────┐ │
│  │   Controller │  ──────────────────────►  │ Home Assistant│ │
│  │   .55        │    "I'm here! .55"       │   Scanning    │ │
│  └──────────────┘                           └──────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

1. **Controller Announces**: "I'm a Violet Pool Controller at 192.168.178.55"
2. **Home Assistant Listens**: Scans for mDNS broadcasts
3. **Service Matched**: Recognized as `_violet-controller._tcp.local.`
4. **Auto-Setup**: Controller appears in integration setup

### Service Types

The integration listens for two service types:

| Service Type | Purpose | Example |
|-------------|---------|---------|
| `_http._tcp.local.` | Standard HTTP services | `Violet Controller._http._tcp.local.` |
| `_violet-controller._tcp.local.` | Violet-specific | `Violet._violet-controller._tcp.local.` |

---

## How Auto-Discovery Works

### Step 1: Integration Initialization

When you open "Add Integration" in Home Assistant:

```python
# Home Assistant scans for mDNS services
zeroconf.scan([
    "_http._tcp.local.",
    "_violet-controller._tcp.local."
])
```

### Step 2: Service Detection

Controller responds to mDNS query:

```
Name:    Violet Pool Controller
Type:    _violet-controller._tcp.local.
Domain:  local.
Host:    192.168.178.55
Port:    80
```

### Step 3: Discovery Handler

The integration's discovery handler processes the service:

```python
async def async_zeroconf_get_service_info(
    hass: HomeAssistant,
    info: ZeroconfServiceInfo,
    service_info_type: str,
) -> ConfigFlow:
    """Handle discovered Violet Pool Controller."""

    # Extract device info
    host = info.host          # 192.168.178.55
    port = info.port          # 80
    name = info.name          # Violet Pool Controller

    # Return config flow with discovered info
    return ConfigFlow(
        host=host,
        port=port,
        discovered=True
    )
```

### Step 4: User Confirmation

In the UI, you see:

```
┌─────────────────────────────────────────┐
│  Found Violet Pool Controller           │
├─────────────────────────────────────────┤
│  Device: Violet Pool Controller         │
│  IP Address: 192.168.178.55             │
│  Port: 80                               │
│                                         │
│  [Cancel]          [Add Integration]    │
└─────────────────────────────────────────┘
```

---

## Setup Requirements

### Network Requirements

✅ **Same Network**
- Controller and Home Assistant on same LAN
- No VPN or router isolation between them

✅ **mDNS Enabled**
- Router supports mDNS/Bonjour (most modern routers do)
- mDNS not blocked by firewall

✅ **UDP Port 5353**
- mDNS uses UDP port 5353
- Must be open for multicast traffic

### Hardware Requirements

| Component | Requirement |
|-----------|-------------|
| **Controller** | Violet Pool Controller (any model) |
| **Home Assistant** | Version 2023.12 or newer |
| **Router** | mDNS/Bonjour support (usually enabled by default) |
| **Network** | Local LAN (WiFi or Ethernet) |

### Software Requirements

- ✅ Home Assistant OS or Supervised (recommended)
- ✅ Integration version 1.1.0 or higher
- ✅ ZeroConf component enabled in Home Assistant

---

## Using Auto-Discovery

### Method 1: Automatic (Recommended)

1. **Power On Controller**
   - Ensure controller is connected to network
   - Wait 30 seconds for full startup

2. **Add Integration in HA**
   ```
   Settings → Devices & Services → + Add Integration
   ```

3. **Search for Integration**
   - Type "Violet" in search box
   - Click "Violet Pool Controller"

4. **Discovered Device Appears**
   - If controller found, shows automatically
   - Click "Submit" to add

5. **Complete Setup**
   - Follow setup wizard
   - Configure any additional settings
   - Finish configuration

### Method 2: Manual Trigger

If auto-discovery didn't work initially:

1. **Restart Home Assistant**
   ```
   Settings → System → Power → Restart
   ```

2. **Restart Controller**
   - Power cycle the controller
   - Wait for full boot

3. **Try Discovery Again**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Violet Pool Controller"

### Method 3: Network Scan

Force a network scan from developer tools:

1. **Open Developer Tools**
   ```
   Developer Tools → Services
   ```

2. **Call ZeroConf Scan**
   ```yaml
   service: zeroconf.scan
   data: {}
   ```

3. **Check Logs**
   ```
   Settings → System → Logs
   Filter for "zeroconf" or "violet"
   ```

---

## Troubleshooting

### Problem: Controller Not Found

#### Symptom
```
No controllers found in discovery
Manual entry required
```

#### Solutions

**1. Check Network Connectivity**

```bash
# From Home Assistant terminal
ping 192.168.178.55

# Should respond:
# 64 bytes from 192.168.178.55: icmp_seq=0 ttl=64 time=5 ms
```

**2. Verify mDNS/Bonjour**

```bash
# On Home Assistant OS (Terminal)
avahi-browse -r _http._tcp.local.

# Should list your controller if mDNS working
```

**3. Check Router Settings**

- Enable mDNS/Bonjour/UPnP
- Disable AP Isolation
- Allow multicast traffic

**4. Check Firewall**

```bash
# Ensure UDP port 5353 is open
# Allow multicast on local network
```

### Problem: Discovery Works but Setup Fails

#### Symptom
```
Controller found but cannot connect
Connection timeout error
```

#### Solutions

**1. Verify Controller API**

```bash
# Test API endpoint
curl http://192.168.178.55/api/v1/readings

# Should return JSON data
```

**2. Check Authentication**

- If controller uses auth, enter credentials
- Verify username/password correct

**3. Test SSL/HTTPS**

```bash
# If using HTTPS
curl -k https://192.168.178.55/api/v1/readings
```

### Problem: Multiple Controllers Show Up

#### Symptom
```
Found 2+ controllers with same name
Unable to differentiate
```

#### Solution

Each controller has unique **Device ID**:

1. Check controller's back panel for device ID
2. Use Device ID to differentiate
3. IP address also unique per controller

---

## Network Configuration

### Router Settings

#### Enable mDNS/Bonjour

**Common Router Locations**:

| Router Brand | Location |
|--------------|----------|
| **ASUS** | Advanced Settings → LAN → mDNS |
| **Netgear** | Advanced → Advanced Setup → UPnP |
| **TP-Link** | Advanced → Network → UPnP |
| **FritzBox** | Home Network → Network → Network Settings |
| **Ubiquiti** | Settings → Networking → UPnP |

#### Disable AP Isolation

**Guest Networks** often have AP isolation enabled:
- Disable AP isolation for controller network
- Or move controller to main network

### Firewall Configuration

Allow mDNS traffic:

```yaml
# Firewall Rules
Source: Any
Destination: 224.0.0.251 (mDNS multicast)
Port: UDP 5353
Action: Allow
```

### Static IP Configuration

**Recommended**: Set static IP for controller

**Router Configuration**:
1. Find DHCP lease table
2. Find controller's MAC address
3. Create DHCP reservation
4. Assign static IP (e.g., 192.168.178.55)

**Benefits**:
- Controller always at same IP
- Discovery more reliable
- Manual setup still works if discovery fails

---

## Manual Fallback

### When to Use Manual Setup

Use manual IP entry if:
- ❌ Auto-discovery not working
- ❌ Controller on different network
- ❌ mDNS blocked by router/firewall
- ❌ Static IP preferred

### Manual Setup Process

1. **Add Integration**
   ```
   Settings → Devices & Services → + Add Integration
   ```

2. **Choose Manual Setup**
   - If discovery shows no devices
   - Or click "Configure Manually"

3. **Enter Controller Details**
   ```
   IP Address: 192.168.178.55
   Port: 80 (default)
   SSL: Disabled (or enabled if configured)
   ```

4. **Test Connection**
   - Integration tests connection
   - Shows success or error

5. **Complete Setup**
   - Follow remaining setup steps

### Finding Controller IP

**Method 1: Router DHCP Table**
```
Router Web UI → DHCP Clients
Look for: "Violet" or manufacturer name
```

**Method 2: Network Scanner**
```bash
# Use nmap to scan network
nmap -p 80 192.168.178.0/24

# Look for devices with port 80 open
```

**Method 3: Controller Display**
- Some controllers show IP on LCD display
- Check controller's menu: Network → Status

---

## Advanced Configuration

### Custom Discovery Timeout

Adjust how long HA waits for discovery:

```yaml
# configuration.yaml
zeroconf:
  default_timeout: 5  # seconds (default)
```

### Discovery Logging

Enable detailed discovery logs:

```yaml
# configuration.yaml
logger:
  logs:
    homeassistant.components.zeroconf: debug
    custom_components.violet_pool_controller: debug
```

Check logs:
```
Settings → System → Logs
Filter: "zeroconf" or "discovery"
```

### Multiple Network Interfaces

If HA has multiple networks:

```yaml
# configuration.yaml
# ZeroConf binds to all interfaces by default
zeroconf:
  # No config needed - auto-detects interfaces
```

---

## FAQ

**Q: Is auto-discovery secure?**
A: Yes, only works on local network. No internet exposure.

**Q: Can I disable auto-discovery?**
A: Yes, simply enter IP manually. No need to disable feature.

**Q: Does discovery work with VLANs?**
A: Only if controller and HA on same VLAN. Routing blocks mDNS.

**Q: What if I have 2+ controllers?**
A: Each discovered separately. Use Device ID to differentiate.

**Q: Discovery used to work, now doesn't**
A: Check for:
- Router firmware update (may have changed settings)
- Network topology change
- Controller firmware update

---

## Comparison: Auto vs Manual

| Feature | Auto-Discovery | Manual Setup |
|---------|---------------|--------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Reliability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Network Requirements** | mDNS required | None |
| **IP Changes** | Handles automatically | Requires update |
| **Multiple Controllers** | Easy setup | More work |

**Recommendation**: Use auto-discovery when possible. Fall back to manual if needed.

---

## Technical Details

### mDNS Packet Format

```
Ethernet Frame
├── IP Header (224.0.0.251 - multicast)
├── UDP Header (port 5353)
└── mDNS Packet
    ├── Questions (Service queries)
    ├── Answers (Service responses)
    └── Resources (PTR, A, SRV records)
```

### Service Registration

Controller announces:

```dns
# PTR Record
_violet-controller._tcp.local. → Violet Pool Controller._http._tcp.local.

# SRV Record
Violet Pool Controller._http._tcp.local. → host: 192.168.178.55, port: 80

# A Record
192.168.178.55 → AA records
```

### Discovery Flow Sequence

```
1. HA: mDNS Query for _violet-controller._tcp.local.
2. Controller: mDNS Response with PTR record
3. HA: mDNS Query for service instance
4. Controller: mDNS Response with SRV and A records
5. HA: Parse records, extract IP/port
6. HA: Show device in UI
7. User: Click "Add"
8. HA: Start config flow with discovered IP
```

---

## Getting Help

### Debug Logs

Enable detailed logging:

```yaml
logger:
  logs:
    homeassistant.components.zeroconf: debug
    custom_components.violet_pool_controller.discovery: debug
```

### Community Support

- 🐛 [Report Issues](https://github.com/xerolux/violet-hass/issues)
- 💬 [Discussions](https://github.com/xerolux/violet-hass/discussions)
- 📖 [Documentation](GOLD_LEVEL_GUIDE.md)

---

## Conclusion

Auto-discovery makes setting up your Violet Pool Controller **effortless**:

✅ **No IP hunting** - Found automatically
✅ **No manual entry** - One-click setup
✅ **Handles IP changes** - Rediscovery if IP changes
✅ **Multiple controllers** - All discovered

**Enjoy the simplicity of automatic discovery!** 🎉

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-28
