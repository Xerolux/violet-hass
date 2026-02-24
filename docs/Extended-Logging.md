# Extended Logging & Diagnostic Tools

## 📊 Overview

The Violet Pool Controller integration includes comprehensive logging and diagnostic features to help troubleshoot issues, verify update behavior, and provide detailed information for support requests.

**Features:**
- ✅ Configurable Diagnostic Logging (default: disabled)
- ✅ Force Update option (verify updates are working)
- ✅ Log Export Service (easy download for support)
- ✅ System Health Metrics (latency, connection status)

---

## 🎯 When to Use These Tools

### 1. **Troubleshooting "Data Not Updating" Issues**
- Users report: "My sensors show the same value for hours"
- Question: "Are values actually unchanged or is polling broken?"
- Solution: Enable these tools to verify update cycles

### 2. **Performance Analysis**
- Check connection latency
- Verify system health percentage
- Monitor request rates

### 3. **Support Requests**
- Export detailed logs easily
- Provide system information
- Show update patterns

---

## ⚙️ Feature 1: Diagnostic Logging

### What It Does

When enabled, the integration logs detailed information on **every update cycle**:

```
DEBUG Update #76 for 'Violet Pool Controller': 403 keys fetched in 0.423s
INFO  📊 Update #76: 15 new/changed keys: PUMP, HEATER, SOLAR...
INFO  📈 Connection: 423.0ms latency, 100% health, 7.14 req/min
INFO  🔑 Sample keys (403 total): pH_value, pot_value, onewire1_value...
```

**Information Logged:**
- ✅ Update counter (track every update)
- ✅ Number of keys fetched (should always be ~403)
- ✅ Fetch duration (performance metric)
- ✅ Changed keys (what's new)
- ✅ Connection metrics (latency, health, request rate)
- ✅ Sample data (first 15 keys)

### How to Enable

1. **Open Home Assistant**
2. Navigate to **Settings → Devices & Services**
3. Find **Violet Pool Controller** integration
4. Click the **⚙️ (3 dots)** menu → **Configure** (or "Options")
5. Select **⚙️ Settings**
6. Find **📊 Extended Logging** (or "Erweiterte Protokollierung")
7. **Toggle ON** to enable

### How to Disable

- Same steps as above, but **toggle OFF**
- Recommended to keep disabled unless troubleshooting (reduces log size)

---

## ⚙️ Feature 2: Force Update

### What It Does

Controls when entities update their `last_updated` timestamp:

**Disabled (Default):**
```
10:00:00 - pH: 7.2 (last_updated: 09:55:00)
10:00:10 - pH: 7.2 (last_updated: 09:55:00) ← No change, no update
10:00:20 - pH: 7.3 (last_updated: 10:00:20) ← Value changed, update!
```

**Enabled:**
```
10:00:00 - pH: 7.2 (last_updated: 10:00:00)
10:00:10 - pH: 7.2 (last_updated: 10:00:10) ← Forced update!
10:00:20 - pH: 7.2 (last_updated: 10:00:20) ← Forced update!
```

### When to Use

- **Troubleshooting:** Verify polling is working (timestamps change every 10s)
- **Dashboard:** Show "activity" even with stable values
- **Verification:** Prove all entities are being updated

### How to Enable

1. Navigate to **Settings → Devices & Services**
2. Find **Violet Pool Controller**
3. Click **⚙️ → Configure**
4. Select **⚙️ Settings**
5. Find **🔄 Force Update** (or "Immer aktualisieren")
6. **Toggle ON**

---

## 📥 Feature 3: Log Export Service

### Overview

The Log Export Service allows you to easily export integration logs for analysis or support requests.

**Features:**
- Export 10-10000 recent log lines
- Save as file in `/config/` directory
- Include/exclude timestamps
- Automatic system information

### Method 1: Developer Tools (GUI)

1. **Open Home Assistant**
2. Navigate to **Developer Tools → Services** (left sidebar)
3. Search for: `violet_pool_controller.export_diagnostic_logs`
4. Fill in the fields:

   | Field | Description | Default |
   |-------|-------------|---------|
   | **Device** | Your Violet Pool Controller | *(required)* |
   | **Lines** | Number of log lines (10-10000) | 100 |
   | **Include timestamps** | Keep timestamps in export | ✅ Yes |
   | **Save to file** | Save as file in /config/ | ❌ No |

5. **Important:** Set **Save to file = YES**
6. Click **Call Service**

### Method 2: YAML Automation

```yaml
alias: "Export Violet Diagnostic Logs"
description: "Export integration logs for troubleshooting"
trigger:
  - platform: web_api  # Manual trigger
action:
  - service: violet_pool_controller.export_diagnostic_logs
    data:
      device_id: "violet_all_features"
      lines: 200
      include_timestamps: true
      save_to_file: true
```

### Method 3: Service Call via CLI

```bash
# SSH into Home Assistant or use Terminal addon
ha-cli call service violet_pool_controller.export_diagnostic_logs \
  device_id="violet_all_features" \
  lines=100 \
  save_to_file=true
```

---

## 📁 Where to Find Downloaded Files

### Step 1: Open File Manager

1. **Settings → Devices & Services**
2. Scroll down to **File Editor** or **File Manager**
3. (Or use left sidebar → **File editor**)

### Step 2: Navigate to /config

The file is saved in the **root** of your Home Assistant configuration.

### Step 3: Find the File

Look for files named:
```
violet_diagnostic_YYYYMMDD_HHMMSS.txt
```

**Examples:**
- `violet_diagnostic_20260224_182500.txt`
- `violet_diagnostic_20260224_190230.txt`

### Step 4: Download

1. Click the file to open it
2. Click the **Download** icon (usually top right)
3. File downloads to your computer

---

## 📊 Understanding the Exported Logs

### File Structure

```
================================================================================
Violet Pool Controller - Diagnostic Log Export
================================================================================
Device: Violet Pool Controller (ALL Features)
Exported: 2026-02-24 18:25:00
Lines: 100
================================================================================

2026-02-24 18:22:50.104 DEBUG Update #72: 403 keys fetched in 0.538s
2026-02-24 18:22:50.105 DEBUG Finished fetching (success: True)
2026-02-24 18:22:50.146 DEBUG HEATER State 2 → HVAC Mode auto
...
```

### Key Information

#### **Update Lines**
```
Update #76: 403 keys fetched in 0.423s
```
- **Update #76**: Update counter (increases each cycle)
- **403 keys**: All data points fetched ✅
- **0.423s**: Response time (good performance)

#### **Success Status**
```
Finished fetching ... (success: True)
```
- ✅ `success: True` = Connection OK
- ❌ `success: False` = Connection problem

#### **Diagnostic Output** (when enabled)
```
📊 Update #76: 15 new/changed keys
📈 Connection: 423.0ms latency, 100% health, 7.14 req/min
🔑 Sample keys (403 total): pH_value, pot_value...
```

---

## 🔍 Troubleshooting Examples

### Problem: "My sensor hasn't updated in hours"

**Step 1: Enable Force Update**
- Settings → Violet Pool Controller → Configure → Settings
- Enable **🔄 Force Update**
- Check if `last_updated` timestamp changes

**Step 2: Enable Diagnostic Logging**
- Enable **📊 Extended Logging**
- Wait 2-3 update cycles (20-30 seconds)

**Step 3: Export Logs**
- Use Log Export Service
- Save 100-200 lines
- Download the file

**Step 4: Analyze**
```
✅ GOOD: Update #70-#77 present, all showing "403 keys fetched"
❌ BAD: Only "Update #50", then nothing for 1 hour
```

### Problem: "Connection issues"

**What to look for in logs:**
```
✅ GOOD:
  Update #70: 403 keys fetched in 0.423s
  Finished fetching ... (success: True)

❌ BAD:
  Update #70: 0 keys fetched
  Finished fetching ... (success: False)
  [Connection timeout errors]
```

---

## 📏 File Size Reference

| Lines | File Size | Duration | Use Case |
|-------|-----------|----------|----------|
| 50 | ~12 KB | ~30 sec | Quick check |
| 100 | ~24 KB | ~1 min | Standard support request |
| 200 | ~48 KB | ~2 min | Detailed troubleshooting |
| 500 | ~120 KB | ~5 min | Extended analysis |
| 1000 | ~240 KB | ~10 min | Full session |
| 5000 | ~1.2 MB | ~30 min | Long-term analysis |
| 10000 | ~2.4 MB | ~60 min | Complete history |

**Note:** A 100-line export is perfect for email or chat support!

---

## 💡 Best Practices

### For Users

1. **Keep Diagnostic Logging disabled** unless troubleshooting
   - Reduces log file size
   - Better HA performance

2. **Enable only when needed**
   - Having issues? Enable it
   - Collect 2-3 minutes of logs
   - Export and disable again

3. **Use Force Update for verification only**
   - Proves polling is working
   - But keeps HA cleaner when disabled

### For Support

1. **Ask users to enable both options**
   - Force Update (shows activity)
   - Diagnostic Logging (shows details)

2. **Request 100-200 log lines**
   - Enough to see patterns
   - Not too large to share

3. **Look for these key indicators:**
   - ✅ Regular update cycles (every 10s)
   - ✅ Always 403 keys fetched
   - ✅ `success: True`
   - ✅ Reasonable latency (< 1000ms)

---

## 🆘 Quick Reference

### Enable Tools
```
Settings → Devices → Violet Pool Controller → ⚙️ → Configure → Settings
```

### Export Logs
```
Developer Tools → Services → export_diagnostic_logs
→ save_to_file: YES
→ Call Service
```

### Download File
```
Settings → File Editor → violet_diagnostic_*.txt → Download
```

### Disable Tools
```
Settings → Devices → Violet Pool Controller → ⚙️ → Configure → Settings
→ Toggle OFF
```

---

## 📚 Related Documentation

- [Configuration Options](Configuration.md)
- [Troubleshooting Guide](Troubleshooting.md)
- [Service Reference](Services.md)

---

## 🤝 Contributing

Found an issue with logging or have suggestions? Please:
1. [Open an Issue](https://github.com/Xerolux/violet-hass/issues)
2. Export diagnostic logs
3. Attach the log file to the issue

---

**Last Updated:** 2024-02-24
**Integration Version:** 1.0.2-beta.3+
