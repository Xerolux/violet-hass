> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Erweiterte-Protokollierung.de)**

---

# Advanced Logging & Diagnostic Tools

This wiki page describes the powerful diagnostic features of the Violet Pool Controller Home Assistant integration for troubleshooting and performance analysis.

## Feature Overview

### 1. 🔍 Diagnostic Logging (Extended Logging)

When enabled, the system logs detailed information for each update cycle:

| Information | Description |
|---|---|
| **Update Counter** | Number of the current update cycle |
| **Key Count** | How many values were fetched from the controller |
| **Fetch Duration** | How long the API query took (in milliseconds) |
| **Changed Keys** | Which values have changed since the last update |
| **Connection Metrics** | Signal strength, latency, and connection information |
| **Sample Data** | Current measurements (temperature, pH value, etc.) |

These detailed logs help with debugging issues and performance analysis.

**Example Output:**
```
[2025-02-24 12:30:45] Update #127 - 42 keys fetched in 245ms
Changed keys: temperature_pool, ph_value, heater_status
Connection: Latency 52ms, Signal Quality: 92%
Sample data: Pool Temp: 24.5°C, pH: 7.2, ORP: 650mV
```

### 2. ⏱️ Force Update (Forced Updates)

This feature controls when entities update their `last_updated` timestamp:

| Setting | Behavior | Use Case |
|---|---|---|
| **Disabled** ✓ Default | Timestamp only on value changes | Normal usage |
| **Enabled** | Timestamp on every cycle | Connection verification |

**When is it useful?**
- Verify that the controller is active and sending data
- Verify that the integration is regularly fetching data
- Confirm that automations are using current values

### 3 📊 Log Export Service

This service allows you to export between 10 and 1,000 recent log lines and save them as a text file.

**Export Format:**
- **Filename:** `violet_diagnostic_YYYYMMDD_HHMMSS.txt`
- **Location:** `/config/` directory
- **Typical Size:** 12–157 KB
- **Options:** Timestamps and system info

## 🚀 Quick Start

### Activation via Home Assistant UI

1. Open **Settings** → **Devices & Services**
2. Search for **Violet Pool Controller**
3. Click **Configure**
4. Enable:
   - ☑️ **Extended Logging**
   - ☑️ **Force Update** (optional)

### Export Logs

1. Open **Developer Tools** → **Services**
2. Select service: `violet_pool_controller.log_export`
3. Enter:
   - `line_count: 200` (number of lines to export)
   - `include_timestamp: true` (with timestamp)
   - `include_system_info: true` (with system info)
4. Click **Call Service**
5. Find the file in the `/config/` directory

### YAML Example

```yaml
# In an automation or script:
service: violet_pool_controller.log_export
data:
  line_count: 500
  include_timestamp: true
  include_system_info: true
```

## 🛠️ Usage Scenarios

### Scenario 1: Unresponsive Sensors

**Problem:** A sensor is not updating regularly.

**Solution:**
1. Enable **Extended Logging**
2. Wait 2–3 minutes
3. Export 200 log lines
4. Check whether the sensor appears in the logs and changes

### Scenario 2: Slow API Queries

**Problem:** The integration is responding slowly.

**Solution:**
1. Enable **Extended Logging**
2. Note the `Fetch Duration` across several log entries
3. If values > 1000ms:
   - Check the network connection
   - Reduce scan intervals in other integrations
   - Contact support with log export

### Scenario 3: Connection Issues

**Problem:** "Connection to controller lost" error messages.

**Solution:**
1. Enable both: **Extended Logging** + **Force Update**
2. Collect 3–5 minutes of logs
3. Export and check for connection drops
4. Share the diagnostics with support

### Scenario 4: Automations Not Working

**Problem:** An automation does not trigger even though the value changes.

**Solution:**
1. Enable **Extended Logging**
2. Trigger the action manually on the controller
3. Check the logs for `Changed keys`
4. Compare with your automation condition

## ⚙️ Best Practices

### ✓ Do's

- ✅ **Disable Extended Logging after debugging** – This reduces log file size and CPU usage
- ✅ **Collect 2–3 minutes of logs** when an issue occurs
- ✅ **Export logs instead of continuously logging**
- ✅ **Use `line_count: 100–500`** for meaningful exports without excess
- ✅ **Delete old export files** from `/config/` regularly

### ✗ Don'ts

- ❌ **Leave Extended Logging enabled permanently** – Wears out log files unnecessarily
- ❌ **Export 10,000+ lines at once** – Files too large, hard to analyze
- ❌ **Ignore high fetch durations** – This indicates network or hardware issues
- ❌ **Enable Force Update without reason** – Wears out storage unnecessarily

## 📋 Step-by-Step Troubleshooting

### Debug Workflow

```
1. Observe the problem (e.g. sensor not responding)
        ↓
2. ENABLE Extended Logging
        ↓
3. Reproduce the problem (wait 2–3 minutes)
        ↓
4. Perform log export
        ↓
5. DISABLE Extended Logging ← Important!
        ↓
6. Analyze export file
        ↓
7. Implement solution or contact support
```

## 🔧 Advanced Configuration

### Automatic Log Capture on Errors

```yaml
automation:
  - alias: "Violet Error - Export Logs"
    trigger:
      platform: state
      entity_id: binary_sensor.violet_pool_controller_connection
      to: "off"
    action:
      service: violet_pool_controller.log_export
      data:
        line_count: 500
        include_system_info: true
```

### Regular Diagnostic Snapshots

```yaml
automation:
  - alias: "Daily Diagnostic Snapshot"
    trigger:
      platform: time
      at: "01:00:00"
    action:
      service: violet_pool_controller.log_export
      data:
        line_count: 200
```

## ❓ Frequently Asked Questions

**Q: Does Extended Logging affect performance?**
> A: Yes, slightly. CPU usage increases by ~5–10%. Therefore it should only be active during debugging.

**Q: How long should I keep Extended Logging enabled?**
> A: Maximum 10–15 minutes. After that, there should be enough data for analysis.

**Q: Where exactly are log files stored?**
> A: In the `/config/` directory of your Home Assistant installation. Via SSH: `ls -la /config/ | grep violet_diagnostic`

**Q: Can I delete the logs automatically?**
> A: Yes, with an automation script or manually. Old files: `rm /config/violet_diagnostic_*.txt`

**Q: What is the difference between Extended Logging and Home Assistant Logs?**
> A: Extended Logging shows controller-specific metrics. HA logs show integration errors. Both are helpful!

## 📞 Support & Further Resources

- **GitHub Issues:** [Violet Pool Controller Issues](https://github.com/Xerolux/violet-hass/issues)
- **Home Assistant Docs:** [Logging Documentation](https://www.home-assistant.io/docs/logging/)
- **Main Documentation:** [[Home]] or [README.md](https://github.com/Xerolux/violet-hass/blob/main/README.md)

---

**Tip:** Save meaningful log exports before contacting support – they help speed up problem resolution! 🚀