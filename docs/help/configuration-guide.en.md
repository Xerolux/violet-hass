# Violet Pool Controller – Configuration Guide (EN)

This guide walks you through the Home Assistant setup for the Violet Pool Controller and highlights all relevant safety considerations.

## ⚠️ Safety & Liability

### IMPORTANT DISCLAIMER

**Use of this software integration is at your own risk and responsibility.**

This integration enables remote control of pool equipment including pumps, heaters, lighting and chemical dosing systems. Incorrect configuration or automation errors may result in:

- **Property damage** (destruction of pumps, heaters, and other equipment)
- **Personal injury** from electric shock
- **Chemical overdosing** with health hazards
- **Endangerment of people and animals** in the pool area

### Your Responsibilities When Using

By using this integration, you confirm that you:

1. **Understand safety** – All safety mechanisms and emergency shut-offs are known
2. **Maintain manual control** – Emergency shut-offs are accessible at all times
3. **Handle chemicals properly** – Follow safety data sheets (gloves, goggles, ventilation)
4. **Follow manufacturer documentation** – Observe your pool manufacturer's instructions
5. **Comply with laws and standards** – Local regulations (DIN/EN standards, electrical and chemical laws)
6. **Monitor regularly** – Personally inspect your installation even with active automation
7. **Create backups** – Perform regular configuration backups

### No Warranty

The developer of this integration provides:

- **NO warranty** regarding functionality, safety or completeness
- **NO liability** for any damages whatsoever, including:
  - Property damage (equipment, buildings, surroundings)
  - Personal injury (injuries, health damage)
  - Financial loss (repair costs, consequential damages)
- **NO commercial guarantees** – This is open-source software

### When in Doubt

Consult a **professional** for:
- Electrical installations
- Chemical handling
- Pool installation and maintenance

By using this integration, you acknowledge that you have read, understood and accepted this disclaimer.

---

## ⚠️ Safety First – Checklist

- **Personal responsibility:** You are fully responsible for every action triggered through the integration.
- **Emergency plan:** Keep a manual override for pumps, dosing equipment and the pool cover ready at all times.
- **Protective gear:** Follow the safety data sheets of the chemicals you use (gloves, goggles, etc.).
- **Firmware level:** Always keep your controller firmware up to date and create regular backups of your configuration.

## ✅ Requirements

- Home Assistant **2025.11.1** or newer
- Network access to the Violet Pool Controller (LAN or Wi-Fi)
- Optional: Username and password if controller authentication is enabled
- Access to the Home Assistant file system for backups

## 🚀 Guided Setup Steps

1. **Welcome menu:** Decide whether to start the wizard or read the documentation first.
2. **Disclaimer:** Read the **full liability disclaimer** carefully. You must explicitly confirm that you understand and accept all risks. This is a legally binding disclaimer.
3. **Connection details:**
   - Controller host/IP address
   - Optional username & password
   - Polling interval (recommended 10–60 seconds)
   - Timeout and retry counts
4. **Pool profile:** Provide volume, pool type and disinfection method for automation logic.
5. **Feature selection:** Enable only the modules you really use to keep the system lean and efficient.
6. **Sensor selection (optional):** Pick the dynamic sensors you want to expose, if available.

## 🧠 Feature Overview

| Feature | Description |
| --- | --- |
| **Heating control** | Optimises heating cycles based on targets and PV surplus. |
| **Solar absorber** | Uses solar energy with smart priority logic and safeguards. |
| **pH/Chlorine management** | Automated dosing with safety windows and overrides. |
| **Cover automation** | Time and weather based control of the pool cover. |
| **Backwash automation** | Initiates backwash and rinse cycles depending on pressure or schedule. |
| **Digital inputs** | Integrates external sensors or switches for custom logic. |
| **LED/DMX lighting** | Scene control, sequences and party mode. |

> 💡 **Tip:** Every feature can be fine-tuned later in the options flow. Document your changes so you can trace them later.

## 🛠️ Services & Automations

- **`violet_pool_controller.control_pump`** – Manages pump speed (eco, boost, auto, forced off).
- **`violet_pool_controller.smart_dosing`** – Performs dosing with built-in safety intervals and overrides.
- **`violet_pool_controller.manage_pv_surplus`** – Aligns pool runtime with available PV surplus.
- **`violet_pool_controller.test_output`** – Temporarily toggles controller outputs for diagnostics (use with caution!).

You can find the full service reference in [`services.yaml`](../../custom_components/violet_pool_controller/services.yaml).

## 🧭 Troubleshooting

1. **No connection:** Verify firewall rules, IP address, SSL configuration and credentials.
2. **Timeouts:** Increase the timeout or avoid lowering the polling interval below 10 seconds.
3. **API errors:** Ensure the controller firmware is current and the REST API is enabled.
4. **Dosing blocked:** Check whether a safety interval is still active; override only in exceptional cases.

## 📦 Backup & Recovery

- Export your Home Assistant configuration regularly.
- Keep track of custom service and automation IDs.
- Store controller backups separately (USB drive, NAS or cloud storage).

## 📞 Support & Community

- GitHub Issues: <https://github.com/xerolux/violet-hass/issues>
- German documentation: <https://github.com/xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md>
- Please attach logs, error codes and a short description of the last steps when requesting support.

Test new automation logic gradually and monitor the water chemistry closely. Enjoy automating your pool! 
