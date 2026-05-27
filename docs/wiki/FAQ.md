> 🇬🇧 **English** | 🇩🇪 **[Deutsch](FAQ.de)**

---

# ❓ FAQ - Frequently Asked Questions

Over 40 common questions and answers!

## General

**Q: Do I need a cloud connection?**
A: No! The add-on is 100% local. No cloud, no internet required.

**Q: Can I control multiple controllers?**
A: Yes! Multi-controller is fully supported. Simply add multiple integrations.

**Q: Is the add-on secure?**
A: Yes! Local communication with SSL/TLS options and input sanitization against injection attacks.

**Q: Which Home Assistant version?**
A: Minimum 2026.5.0. Tested on 2026.x.

---

## Installation

**Q: How do I find my controller's IP address?**
A:
1. Open router admin (192.168.1.1)
2. Show connected devices
3. Search for "Violet" and note the IP
4. Or: `ping violet.local`

**Q: Can I connect to the controller via HTTPS?**
A: Yes! Enable "Use SSL" in the settings.

**Q: Does a self-signed certificate work?**
A: Yes, but disable "Verify SSL certificate" (only for trusted networks!).

**Q: Why isn't my integration showing up?**
A: Restart Home Assistant after installation!

---

## Features & Operation

**Q: What does "Automatic" vs. "Manual" mean?**
A:
- **Automatic**: Controller regulates independently (by temperature, time, etc.)
- **Manual**: You set directly, auto rules are ignored

**Q: What are Device States 0-6?**
A: Seven different operating states:
- 0 = Automatic, off
- 1 = Manual on
- 2 = Automatic, on
- 3 = Automatic with timer, on
- 4 = Manual forced, on
- 5 = Automatic, waiting
- 6 = Manual, off

Read [Device-States](Device-States) for details.

**Q: Can I adjust pump speed?**
A: Yes! 3 stages available with the `control_pump` service (stages 1-3).

**Q: What is the `export_diagnostic_logs` service?**
A: New service (v1.0.2) for exporting integration logs for troubleshooting. Use it to export up to 10,000 log lines and send them to support. Optionally save to file.

**Q: How do I dose safely?**
A:
- Small amounts (15-30 seconds)
- Observe intervals between dosing
- Always check sensor value
- Safety override only when necessary

**Q: Can sensors show incorrect values?**
A: Possible! Calibration:
- pH/ORP: Monthly
- Chlorine: Weekly with test kit
- Check sensors for contamination

---

## Problems & Troubleshooting

**Q: Sensors show "unavailable"**
A:
1. Increase polling interval (30-45s)
2. Reload integration
3. Activate fewer sensors
4. Check network stability

**Q: Controller responds very slowly**
A:
1. Check network utilization
2. Increase polling interval
3. Check controller CPU load
4. Too many sensors?

**Q: Why aren't sensors showing up?**
A:
1. Not activated in setup flow?
2. Controller doesn't have this sensor
3. Feature not configured
4. Solution: Reload integration

**Q: "Connection failed"**
A:
1. IP address correct? Test ping: `ping 192.168.1.100`
2. Controller online? Open web page
3. Firewall blocking?
4. Username/password correct?

**Q: SSL error when connecting**
A:
1. Certificate valid? Check with browser
2. Disable "Verify SSL certificate" (only temporarily!)
3. Date/time correct on HA?

---

## Performance & Optimization

**Q: What polling interval should I use?**
A:
- 10-15s: Fast, but high load
- **20-30s: Standard, good balance** ✅
- 45-60s: Conservative, less responsive

**Q: Writing automations all the time is boring!**
A: Use Blueprints! Pre-built automation templates are included in the repo.

**Q: Can I reduce logging?**
A: Yes, in `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.violet_pool_controller: warning
```

**Q: Add-on slowing down Home Assistant?**
A: It shouldn't. If problems occur:
1. Increase polling interval
2. Activate fewer sensors
3. Start fewer automations
4. Check logs for error loops

---

## Services & Automations

**Q: How do I call a service?**
A: Three ways:
1. Developer Tools → Services
2. YAML in automation
3. Automation UI Builder

**Q: Can I trigger an automation on a schedule?**
A: Yes!
```yaml
trigger:
  - platform: time
    at: "08:00:00"
```

**Q: Can I react to weather forecasts?**
A: Yes, with the Weather integration!

**Q: What's the difference between services?**
A: Services are specialized:
- `control_pump` - Pump with speed
- `smart_dosing` - Chemical dosing
- `switch.turn_on` - Only on/off

---

## Updates & Maintenance

**Q: How do I update the add-on?**
A: With HACS:
1. HACS → Integrations
2. Find "Violet Pool Controller"
3. If available: "Update"
4. Restart Home Assistant

**Q: What should I do before an update?**
A:
1. Create a backup
2. Read the changelog
3. Check for breaking changes

**Q: What if the update causes problems?**
A:
1. Restart Home Assistant (not just reload!)
2. Reload the integration
3. If problems persist: revert to the old version

**Q: How do I revert to an older version?**
A:
```bash
cd /config/custom_components/violet_pool_controller
git checkout v0.2.0  # example
```

---

## Uninstallation

**Q: How do I uninstall the add-on?**
A:
1. Settings → Devices & Services
2. Select Violet → ⋮ → Remove
3. Delete files: `/config/custom_components/violet_pool_controller`
4. Restart Home Assistant

**Q: Will my automations survive uninstallation?**
A: Yes! They are stored separately. But they won't work without the add-on.

---

## Special Applications

**Q: Can I automate a pool party?**
A: Yes! With services:
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: party_mode
```

**Q: How do I use solar surplus?**
A:
```yaml
service: violet_pool_controller.manage_pv_surplus
data:
  mode: activate
  pump_speed: 3
```

**Q: Can I set temperature limits?**
A: Yes, with climate entities:
```yaml
service: climate.set_temperature
target:
  entity_id: climate.violet_heater
data:
  temperature: 28
  hvac_mode: heat
```

---

## Support & Further Help

Questions still not answered?

- 📖 **Search the wiki** - Probably here
- 🐛 **[GitHub Issues](https://github.com/xerolux/violet-hass/issues)** - Bug reports
- 💬 **[Community Forum](https://community.home-assistant.io/)** - User questions
- 🎮 **[Discord](https://discord.gg/Qa5fW2R)** - Live chat
- 📧 **Email**: git@xerolux.de

---

## More Pages

- 📖 [Installation & Setup](Installation-and-Setup) - Step-by-step installation
- 🎯 [Device-States](Device-States) - States 0-6 explained
- 🤖 [Services](Services) - All services
- 🚨 [Troubleshooting](Troubleshooting) - Troubleshooting guide
