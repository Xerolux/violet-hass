# 🚨 Troubleshooting

Having issues? Here you'll find the solutions!

## Common Errors

### ❌ "Connection to controller failed"

**Symptoms:**
- Integration shows "Unavailable" in red
- All entities are "unavailable"

**Solution steps:**

1. **Test connectivity:**
```bash
# Ping controller
ping 192.168.1.100

# Test HTTP request
curl http://192.168.1.100/getReadings?ALL
```

2. **Verify IP address**
   - Is the IP still correct? (Router may have changed the IP)
   - Use a static IP or DHCP reservation

3. **Check firewall**
   - Is the firewall blocking access?
   - Open port 80 (or 8080)

4. **Restart the controller**
   - Turn off the controller (main switch)
   - Wait 30 seconds
   - Turn it back on

5. **Reload the integration**
   - Settings → Devices & Services → Violet
   - ⋮ (Menu) → "Reload"

### ❌ "SSL Certificate Error"

**Symptom:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Causes:**
- Controller uses a self-signed certificate
- Date/time on HA is incorrect
- Wrong hostname in URL

**Solution 1: Disable SSL validation (quick)**
1. Settings → Devices & Services → Violet
2. ⋮ → "Options"
3. Disable "Verify SSL certificate"

⚠️ **Warning:** Only for trusted networks!

**Solution 2: Validate the certificate**
```bash
# Check with browser
https://192.168.1.100/

# Or with OpenSSL
openssl s_client -connect 192.168.1.100:8443 -showcerts
```

### ❌ "Timeout - Request takes too long"

**Symptoms:**
- Integration works but is very slow
- Frequent "Timeout" errors in logs

**Causes:**
- Network overloaded
- Controller not responsive
- Too many sensors queried
- Timeout value too low

**Solutions:**

1. **Increase polling interval:**
   - Settings → Devices & Services → Violet → Options
   - Increase "Polling interval" (e.g., 45 seconds instead of 30)

2. **Enable fewer sensors:**
   - Reload the integration
   - Select only important sensors

3. **Increase timeout value (advanced):**
   - Settings → Devices & Services → Violet → Options
   - Increase "Timeout" (e.g., 15 seconds instead of 10)

4. **Check network stability:**
```bash
# Test ping and packet loss
ping -c 20 192.168.1.100
```

### ❌ "Entities are constantly 'unavailable'"

**Symptoms:**
- Entities show "unavailable" state
- Coordinator errors in the log

**Causes:**
- Polling interval too short
- Sensor error on the controller
- Rate limit reached

**Solutions:**

1. **Increase polling interval:**
   - Currently at 10-15s? → Increase to 30-45s

2. **Reload the integration:**
```yaml
# In automation or Developer Tools
service: homeassistant.reload_config_entry
target:
  device_id: <device_id>
```

3. **Check logs:**
```bash
tail -f /config/home-assistant.log | grep violet_pool_controller
```

### ❌ "Sensor shows 'unknown' or incorrect values"

**Causes:**
- Sensor not calibrated
- Sensor defective
- Incorrect API response

**Solutions:**

1. **Sensor calibration:**
   - pH: Calibrate monthly
   - ORP: Along with pH calibration
   - Chlorine: Check weekly with test kit

2. **Clean sensor:**
   - Clean the sensor lenses
   - Remove dirt/deposits

3. **Check controller:**
   - Look at error codes
   - Check `sensor.violet_system_error_codes`

## Enabling Debug Mode

For detailed logs:

1. **Edit configuration.yaml:**
```yaml
logger:
  logs:
    custom_components.violet_pool_controller: debug
    aiohttp: debug
```

2. **Restart Home Assistant**

3. **Check logs:**
   - Home Assistant → Settings → System → Logs
   - Or: `tail -f /config/home-assistant.log`

## Analyzing Logs

**Important log entries:**

| Log Level | Meaning | Example |
|-----------|---------|---------|
| **DEBUG** | Detailed info | Request being sent |
| **INFO** | Normal info | Integration loaded |
| **WARNING** | Warning | Sensor not found |
| **ERROR** | Error | Connection failed |

**Save logs:**
```bash
# Save logs to file
cp /config/home-assistant.log ~/violet-logs.txt
```

### Export Logs with Service (NEW in v1.0.2)

Use the `export_diagnostic_logs` service to export logs directly:

```yaml
service: violet_pool_controller.export_diagnostic_logs
target:
  device_id: <device_id>
data:
  lines: 500
  include_timestamps: true
  save_to_file: true
```

This saves the logs to `/config/` for later analysis or support tickets.

## Common Log Errors

### `Connection refused`
- **Cause:** Controller not reachable
- **Solution:** Check IP, port, firewall

### `Request timeout`
- **Cause:** Connection too slow
- **Solution:** Increase polling interval

### `SSL: CERTIFICATE_VERIFY_FAILED`
- **Cause:** Certificate problem
- **Solution:** Disable SSL validation or check certificate

### `Invalid JSON response`
- **Cause:** Controller responding incorrectly
- **Solution:** Restart controller, check firmware

## Controller Error Codes

These codes appear in `sensor.violet_system_error_codes`:

| Code | Error | Solution |
|------|-------|----------|
| **101** | Sensor error (pH, ORP, etc.) | Check/clean sensor |
| **205** | Pressure too high | Open valve, backwash |
| **301** | Water level too low | Refill water |
| **401** | Temperature sensor defective | Replace sensor |

See the controller manual for a complete list.

## Special Issues

### Issue: State stays at "5" (Waiting)

**Meaning:** Automation is waiting for conditions

**Solutions:**
1. Check conditions (e.g., temperature threshold)
2. Check error codes
3. Safety interval (usually 5-10 minutes)
4. Set manually to "1" (on) for testing

### Issue: Pump speed shows incorrect value

**Symptom:** Speed sensor shows 0 even though pump is running

**Solution:**
- Not all controllers have a speed sensor
- Use the `control_pump` service for speed control

### Issue: DMX scenes not working

**Solutions:**
1. Are the lights connected via DMX?
2. Is DMX addressing correct on the controller?
3. Test with the `test_output` service

### Issue: Dosing not working

**Check:**
1. Are dosing pumps connected?
2. Has the safety interval passed? (usually 5 minutes)
3. Override safety (if desired)

## Performance & Optimization

### Home Assistant is slow

**Checks:**
1. Increase polling interval to 45-60s
2. Enable fewer sensors
3. Reduce automations
4. Check logs for error loops

### Too many log entries

```yaml
logger:
  logs:
    custom_components.violet_pool_controller: warning
    aiohttp: warning
```

## Backup & Recovery

### Create backup
```
Settings → System → Backups → Create
```

### Restore from backup
```
Settings → System → Backups → Restore
```

### Reload integration without restart
```
Settings → Devices & Services → Violet → ⋮ → Reload
```

## Getting Support

If nothing helps:

1. **Collect logs:**
   - Copy 50-100 lines from home-assistant.log
   - Enable debug mode

2. **System info:**
   - Home Assistant version
   - Addon version
   - Controller model & firmware

3. **Create an issue:**
   - [GitHub Issues](https://github.com/xerolux/violet-hass/issues)
   - Detailed problem description
   - Attach logs (without passwords!)

4. **Community help:**
   - [Discord](https://discord.gg/Qa5fW2R)
   - [Community Forum](https://community.home-assistant.io/)

---

## More Pages

- 📖 [Installation & Setup](Installation-and-Setup) - Step-by-step installation
- 🎯 [Device States](Device-States) - Understanding states
- ❓ [FAQ](FAQ) - Frequently asked questions
- 🤖 [Services](Services) - All services