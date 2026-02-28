# UI Reconfiguration Guide ⚙️

**Change Integration Settings Without Removal**

---

## Overview

The **UI Reconfiguration** feature allows you to modify connection settings for your Violet Pool Controller integration **without** removing and re-adding it. This means:

- ✅ **No Data Loss** - Keep all entity history, automations, and scripts
- ✅ **Instant Updates** - Settings applied immediately
- ✅ **User Friendly** - No YAML editing or server restarts
- ✅ **Dynamic Updates** - Change polling, timeout, retries on-the-fly

---

## Table of Contents

1. [What is Reconfiguration?](#what-is-reconfiguration)
2. [Reconfiguration vs Options Flow](#reconfiguration-vs-options-flow)
3. [Reconfiguration Scenarios](#reconfiguration-scenarios)
4. [Step-by-Step Guide](#step-by-step-guide)
5. [Common Use Cases](#common-use-cases)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## What is Reconfiguration?

### Traditional Method (Before Gold Level)

**Problem**: To change IP address, you had to:

1. ❌ Remove integration (loses all entities)
2. ❌ Re-add integration (recreates entities)
3. ❌ Rebuild all automations
4. ❌ Lose entity history
5. ❌ Manually configure everything again

**Time Required**: 30-60 minutes

### New Method (Gold Level)

**Solution**: UI Reconfiguration

1. ✅ Click "Configure" on integration
2. ✅ Change IP address
3. ✅ Submit - integration reloads
4. ✅ Everything preserved - entities, automations, history

**Time Required**: 2 minutes

### What Can Be Reconfigured?

| Setting | Reconfiguration | Options Flow | Description |
|---------|---------------|--------------|-------------|
| **IP Address** | ✅ | ❌ | Controller's IP/hostname |
| **Username** | ✅ | ❌ | Authentication username |
| **Password** | ✅ | ❌ | Authentication password |
| **SSL/HTTPS** | ✅ | ❌ | Use encrypted connection |
| **Polling Interval** | ✅ | ✅ | How often to fetch data (5-300s) |
| **Timeout** | ✅ | ✅ | Max wait for response (5-60s) |
| **Retry Attempts** | ✅ | ✅ | Number of retries (1-10) |
| **Features** | ❌ | ✅ | Enable/disable features |
| **Sensors** | ❌ | ✅ | Select which sensors to show |
| **Controller Name** | ❌ | ✅ | Display name for controller |

**Rule of Thumb**:
- 🔧 **Connection/Network Settings** → Use **Reconfiguration**
- 🎛️ **Feature/Display Settings** → Use **Options Flow**

---

## Reconfiguration vs Options Flow

### When to Use Reconfiguration

Use **Reconfiguration** when:
- Controller got new IP address from router
- Want to enable/disable SSL
- Need to update username/password
- Experiencing connection timeouts
- Want to adjust polling interval
- Need more/less retry attempts

**Example Scenarios**:
```
1. Router assigned new IP to controller
2. Enabled HTTPS on controller
3. Network is slow - increase timeout
4. Controller moved to different subnet
5. Added authentication to controller
```

### When to Use Options Flow

Use **Options Flow** when:
- Want to enable/disable smart features
- Select which sensors to display
- Change controller display name
- Adjust feature-specific settings
- Enable diagnostic logging

**Example Scenarios**:
```
1. Don't have solar - disable solar feature
2. Only want temperature sensors
3. Rename controller to "Backyard Pool"
4. Enable detailed logging for troubleshooting
```

### Quick Reference Decision Tree

```
What do you want to change?

Network/Connection? ───────────────► Use RECONFIGURATION
├── IP Address
├── SSL/HTTPS
├── Username/Password
└── Timeout/Retries

Features/Display? ──────────────────► Use OPTIONS FLOW
├── Enable/Disable Features
├── Select Sensors
├── Controller Name
└── Diagnostic Settings
```

---

## Reconfiguration Scenarios

### Scenario 1: IP Address Change

**Situation**: Router assigned new IP via DHCP

```
Before: 192.168.178.55
After:  192.168.178.60
```

**Steps**:

1. **Find New IP**
   - Check router's DHCP client list
   - Or use network scanner

2. **Open Reconfiguration**
   ```
   Settings → Devices & Services → Violet Pool Controller → Configure
   ```

3. **Select "Reconfigure Connection"**
   ```
   ┌──────────────────────────────────────┐
   │  What would you like to configure?   │
   ├──────────────────────────────────────┤
   │  ○ Features                          │
   │  ○ Sensors                           │
   │  ⦿ Reconfigure Connection  ← SELECT  │
   └──────────────────────────────────────┘
   ```

4. **Update IP Address**
   ```
   IP Address or Hostname: 192.168.178.60
   ```

5. **Submit & Test**
   - Integration tests connection
   - Shows success or error

6. **Complete**
   - Integration reloads
   - All entities preserved
   - No data loss!

### Scenario 2: Enable Authentication

**Situation**: You've enabled auth on controller

**Steps**:

1. **Open Reconfiguration**
   ```
   Settings → Devices & Services → Violet Pool Controller → Configure
   ```

2. **Enter Credentials**
   ```
   Username (optional): admin
   Password (optional): your_password
   ```

3. **Submit**
   - Integration tests credentials
   - Shows success or "invalid_auth" error

4. **Complete**
   - All future requests use authentication

### Scenario 3: Slow Network - Increase Timeout

**Situation**: Controller shows "unavailable" frequently

**Current Settings**:
- Timeout: 30s
- Retries: 3
- Result: Connection timeouts

**Solution**:

1. **Open Reconfiguration**

2. **Adjust Settings**
   ```
   Polling Interval: 10s (unchanged)
   Timeout (seconds): 60s  ← INCREASED
   Retry Attempts: 5      ← INCREASED
   ```

3. **Submit**

4. **Result**: More stable connection on slow networks

### Scenario 4: Faster Updates Wanted

**Situation**: Want near real-time sensor updates

**Current**: Polling every 10 seconds
**Desired**: Polling every 5 seconds

**Steps**:

1. **Open Reconfiguration**

2. **Change Polling Interval**
   ```
   Polling Interval: 5s  ← MINIMUM
   ```

3. **Submit**

4. **Result**: Updates every 5 seconds

⚠️ **Caution**: Faster polling = more network traffic

### Scenario 5: Switch to HTTPS

**Situation**: Controller now supports SSL

**Current**: HTTP (unencrypted)
**Desired**: HTTPS (encrypted)

**Steps**:

1. **Open Reconfiguration**

2. **Enable SSL**
   ```
   Use SSL/HTTPS: [✓] ← CHECKED
   ```

3. **Submit**

4. **Result**: Encrypted connection

⚠️ **Note**: If controller uses self-signed cert, you may need to disable SSL verification (not recommended for production).

---

## Step-by-Step Guide

### Complete Reconfiguration Process

#### Step 1: Navigate to Integration

**Method 1: From Settings**
```
Home Assistant
  └── Settings
       └── Devices & Services
            └── Violet Pool Controller
```

**Method 2: From Configuration**
```
Home Assistant
  └── Configuration
       └── Integrations
            └── Violet Pool Controller
```

#### Step 2: Click Configure

Look for one of:
- "Configure" button
- ⚙️ Gear icon
- "⋮" (three dots) menu → "Configure"

#### Step 3: Choose Configuration Type

```
┌─────────────────────────────────────────┐
│  Pool-Einstellungen anpassen           │
├─────────────────────────────────────────┤
│  What would you like to configure?     │
│                                         │
│  ⦿ Reconfigure Connection              │
│  ○ Enable/disable features             │
│  ○ Select sensors                       │
└─────────────────────────────────────────┘
```

#### Step 4: Update Settings

**Connection Settings Form**:

```
┌─────────────────────────────────────────┐
│  🌐 Controller Connection               │
├─────────────────────────────────────────┤
│                                         │
│  * IP Address or Hostname:              │
│    [192.168.178.55           ]          │
│                                         │
│  Username (optional):                   │
│    [admin                   ]          │
│                                         │
│  Password (optional):                   │
│    [••••••••                 ]          │
│                                         │
│  * Use SSL/HTTPS:                      │
│    [✓] Yes  [ ] No                     │
│                                         │
│  * Polling Interval (seconds):          │
│    [10               ] (5-300)         │
│                                         │
│  * Timeout (seconds):                   │
│    [30               ] (5-60)          │
│                                         │
│  * Retry Attempts:                      │
│    [3                ] (1-10)          │
│                                         │
│  [Cancel]              [Submit]         │
└─────────────────────────────────────────┘
```

#### Step 5: Submit & Test

**What Happens**:

1. **Validation**
   ```python
   if not valid_ip(ip):
       show_error("Invalid IP address")
   ```

2. **Connection Test**
   ```python
   api = VioletPoolAPI(
       host=new_ip,
       username=new_username,
       password=new_password,
       ...
   )
   readings = await api.get_readings()
   ```

3. **Result**
   - ✅ **Success**: Settings saved, integration reloads
   - ❌ **Failure**: Error message shown, no changes applied

#### Step 6: Verification

**After Successful Reconfiguration**:

1. **Check Integration Status**
   - Should show "Connected" or similar
   - No error messages

2. **Check Entities**
   ```
   Developer Tools → States
   Search: sensor.violet_*

   All entities should have current values
   ```

3. **Check Logs**
   ```
   Settings → System → Logs
   Filter: "violet"

   Should see: "Setup completed successfully"
   ```

---

## Common Use Cases

### Use Case 1: Network Migration

**Scenario**: Moving pool controller to new network

**Old Network**: 192.168.1.x (main LAN)
**New Network**: 192.168.2.x (IoT VLAN)

**Steps**:

1. **Physically Move Controller**
   - Connect to new network
   - Verify connectivity

2. **Find New IP**
   - New IP: 192.168.2.55

3. **Reconfigure**
   ```
   IP Address: 192.168.2.55
   ```

4. **Done!**

### Use Case 2: Router Replacement

**Scenario**: Replaced old router with new model

**Issue**: DHCP assigns different IP range

**Before**:
- Old router: 192.168.0.x range
- Controller: 192.168.0.55

**After**:
- New router: 192.168.1.x range
- Controller: 192.168.1.55

**Steps**:

1. **Find new IP** (check new router's DHCP table)

2. **Reconfigure integration** with new IP

3. **Static IP Recommended**: Reserve IP in new router

### Use Case 3: Performance Optimization

**Scenario**: Want faster updates vs network load

**High Performance** (more traffic, faster updates):
```
Polling Interval: 5s   ← Fastest
Timeout: 30s
Retries: 3
```

**Balanced** (recommended):
```
Polling Interval: 10s  ← Default
Timeout: 30s
Retries: 3
```

**Low Network Load** (less traffic, slower updates):
```
Polling Interval: 60s  ← Slower
Timeout: 30s
Retries: 3
```

### Use Case 4: Unreliable Network

**Scenario**: WiFi drops occasionally

**Solution**: Increase retries and timeout

```
Polling Interval: 10s
Timeout: 60s          ← Give more time
Retry Attempts: 5     ← Try more times
```

**Result**: More resilient to temporary network issues.

---

## Troubleshooting

### Problem: Reconfiguration Fails

#### Error: "Invalid IP Address"

**Cause**: IP format incorrect

**Solution**:
```
Correct:
- 192.168.178.55
- 10.0.0.5
- pool-controller.local

Incorrect:
- 192.168.178.555  (invalid octet)
- 192.168          (incomplete)
- http://192.168.178.55  (no protocol)
```

#### Error: "Cannot Connect"

**Causes**:
1. Wrong IP address
2. Controller offline
3. Firewall blocking
4. SSL mismatch

**Solutions**:

**1. Verify IP**
```bash
ping 192.168.178.55
```

**2. Test API**
```bash
# HTTP
curl http://192.168.178.55/api/v1/readings

# HTTPS
curl -k https://192.168.178.55/api/v1/readings
```

**3. Check Controller**
- Power light on?
- Network link active?
- Can access web UI?

#### Error: "Invalid Authentication"

**Cause**: Wrong username/password

**Solution**:
1. Verify credentials
2. Check controller settings
3. Ensure auth enabled on controller

### Problem: Settings Not Applied

#### Symptom: Reconfiguration succeeded but settings unchanged

**Solution**:

1. **Verify Integration Reloaded**
   ```
   Should see notification: "Integration reloaded"
   ```

2. **Manual Reload**
   ```
   Settings → Devices & Services
   → Violet Pool Controller → ⋮ → Reload
   ```

3. **Check Config Entry**
   ```yaml
   # Home Assistant configuration
   .storage/core.config_entries

   Verify settings saved correctly
   ```

4. **Restart HA (Last Resort)**
   ```
   Settings → System → Power → Restart
   ```

### Problem: Connection Unstable After Reconfiguration

#### Cause: Polling too fast for network/device

**Solution**:

1. **Increase Polling Interval**
   ```
   From: 5s
   To:   10s or 15s
   ```

2. **Increase Timeout**
   ```
   From: 30s
   To:   60s
   ```

3. **Reduce Retries** (if flooding)
   ```
   From: 5
   To:   3
   ```

---

## Best Practices

### 1. Test Before Changing

Before reconfiguring, verify new settings work:

```bash
# Test IP
ping 192.168.178.60

# Test API
curl http://192.168.178.60/api/v1/readings

# Test credentials
curl -u admin:password http://192.168.178.60/api/v1/readings
```

### 2. Document Current Settings

Before changing, note current values:

```
Current Settings:
- IP: 192.168.178.55
- SSL: Off
- Polling: 10s
- Timeout: 30s
- Retries: 3
```

Useful if you need to rollback.

### 3. Change One Setting at a Time

Don't change everything at once.

**Bad**:
```
Change: IP, SSL, timeout, polling, retries (all at once)
Problem: If something breaks, what caused it?
```

**Good**:
```
Step 1: Change IP → Test
Step 2: Enable SSL → Test
Step 3: Adjust timeout → Test
```

### 4. Use Static IPs

Prevent IP changes in the first place:

```
Router Settings → DHCP → Reserve
MAC: AA:BB:CC:DD:EE:FF
IP:  192.168.178.55
```

### 5. Monitor After Changes

After reconfiguration:

1. Check entity states update
2. Verify no error logs
3. Test automations still work
4. Monitor for 24 hours

### 6. Schedule Changes During Off-Hours

Don't reconfigure during pool usage:

- **Bad**: Middle of day, pool in use
- **Good**: Night/morning when pool idle

---

## Advanced Topics

### Reconfiguration via YAML

For advanced users, you can edit config entry directly:

⚠️ **Warning**: Edit YAML at your own risk!

```yaml
# .storage/core.config_entries

entry_id: "abc123"
domain: "violet_pool_controller"
data:
  api_url: "192.168.178.55"      # Can edit
  use_ssl: true                  # Can edit
  polling_interval: 10           # Can edit
  timeout_duration: 30           # Can edit
  retry_attempts: 3              # Can edit
```

After editing, reload HA:
```
Settings → System → Power → Restart
```

### Programmatic Reconfiguration

Using Home Assistant service:

```yaml
service: homeassistant.reload_config_entry
data:
  entry_id: "abc123"
```

Or via Python script:

```python
await hass.config_entries.async_reload(entry_id)
```

### Batch Reconfiguration

Multiple controllers? Update all at once:

```bash
# Script to find all violet controllers
for entry in hass.config_entries.async_entries("violet_pool_controller"):
    print(f"Entry ID: {entry.entry_id}")
    print(f"IP: {entry.data['api_url']}")
    # Update via UI or API
```

---

## FAQ

**Q: Will I lose entity history?**
A: No! History preserved. Only connection settings change.

**Q: Do automations break?**
A: No. Entity IDs unchanged. Automations continue working.

**Q: Can I undo reconfiguration?**
A: Yes. Just reconfigure back to old settings.

**Q: What if I enter wrong IP?**
A: Connection test fails. No changes applied. Try again.

**Q: How long does reconfiguration take?**
A: Usually < 30 seconds. Most time is connection test.

**Q: Do I need to restart Home Assistant?**
A: No. Integration reloads automatically.

**Q: Can I reconfigure if controller offline?**
A: No. Connection test must pass for changes to apply.

**Q: What's the difference between "Reload" and "Reconfigure"?**
A:
- **Reload**: Restart integration, same settings
- **Reconfigure**: Change settings, then reload

---

## Comparison: Before vs After Gold Level

### Before Gold Level

| Task | Effort | Time | Data Loss |
|------|--------|------|-----------|
| Change IP | High | 30-60 min | Yes |
| Update credentials | Medium | 15-30 min | No |
| Adjust polling | High | 30-60 min | Yes |
| Change timeout | High | 30-60 min | Yes |

**Process**:
1. Remove integration (❌ loses entities)
2. Re-add integration
3. Rebuild automations
4. Lose entity history

### After Gold Level (Now)

| Task | Effort | Time | Data Loss |
|------|--------|------|-----------|
| Change IP | Low | 2 min | No |
| Update credentials | Low | 2 min | No |
| Adjust polling | Low | 2 min | No |
| Change timeout | Low | 2 min | No |

**Process**:
1. Click "Configure"
2. Change setting
3. Submit
4. ✅ Done!

---

## Summary

The **UI Reconfiguration** feature makes managing your Violet Pool Controller integration **effortless**:

✅ **No Data Loss** - Keep everything
✅ **Instant Updates** - No restart needed
✅ **User Friendly** - Simple UI forms
✅ **Safe** - Connection test before applying
✅ **Flexible** - Change what you need, when you need

**Enjoy the convenience of Gold Level reconfiguration!** 🎉

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-28
