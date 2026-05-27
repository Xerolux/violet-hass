> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Error-Codes.de)**

---

# Error Codes – Controller Error Codes Explained

> Complete reference of all Violet Pool Controller error codes with causes and solutions.

---

## Overview

The Violet Pool Controller sends error codes via the API. These are displayed in Home Assistant as sensor attributes and can be used for automations.

### Severity Classes

| Class | Symbol | Meaning |
|--------|--------|---------|
| `info` | ℹ️ | Information / Reminder – no action required |
| `warning` | ⚠️ | Warning – attention required |
| `critical` | 🚨 | Critical – immediate action required |

### Code Types

| Type | Description |
|-----|-------------|
| `MESSAGE` | Status message from the controller |
| `ALERT` | Alarm – system error or safety function active |
| `WARNING` | Warning – threshold exceeded |
| `REMINDER` | Reminder – maintenance or update |

---

## System & Hardware

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `0` | MESSAGE | ℹ️ | Test message | No action required |
| `1` | MESSAGE | ℹ️ | Status message | No action required |
| `2` | ALERT | 🚨 | **Hardware issue: COM-Link to carrier faulty** | Restart device, check hardware, contact support |
| `3` | REMINDER | ℹ️ | Happy Birthday | System birthday – no action |
| `8` | WARNING | ⚠️ | CPU temperature high | Ventilate device, check ambient temperature |
| `9` | ALERT | 🚨 | **CPU temperature critical** | Shut down device immediately, check case/ventilation |

---

## Updates

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `10` | REMINDER | ℹ️ | Update available – will be installed automatically | Wait until next night |
| `11` | REMINDER | ℹ️ | Update available – confirmation required | Confirm in controller web interface |
| `12` | REMINDER | ℹ️ | Update available – install manually | Trigger update manually |

---

## Filter Pump & Pressure

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `20` | ALERT | 🚨 | **Filter pressure too low** | Check pump and filter, inspect intake |
| `21` | ALERT | 🚨 | **Filter pressure too high** | Backwash filter, check filter housing |
| `22` | WARNING | ⚠️ | Sample water inflow missing | Open sampling valve, check flow |
| `23` | WARNING | ⚠️ | Sample water inflow too high | Throttle sampling valve |
| `24` | ALERT | 🚨 | **Circulation missing** | Check pump and piping system |
| `25` | ALERT | 🚨 | **Circulation too high** | Check shut-off valve, throttle pump |
| `26` | ALERT | 🚨 | **Frost protection filter pump unavailable** | Check temperature sensor |
| `27` | ALERT | 🚨 | **Frost protection absorber unavailable** | Check solar temperature sensor |

---

## Heater & Temperature

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `30` | WARNING | ⚠️ | Heat exchanger temperature high | Increase flow rate, reduce heating power |
| `31` | ALERT | 🚨 | **Over-temperature protection unavailable** | Check temperature sensor |

### Temperature Programs (71–78)

| Code | Type | Severity | Description |
|------|------|----------|-------------|
| `71` | WARNING | ⚠️ | Temperature control program 1 triggered |
| `72` | WARNING | ⚠️ | Temperature control program 2 triggered |
| `73` | WARNING | ⚠️ | Temperature control program 3 triggered |
| `74` | WARNING | ⚠️ | Temperature control program 4 triggered |
| `75` | MESSAGE | ℹ️ | Temperature control program 5 triggered |
| `76` | WARNING | ⚠️ | Temperature control program 6 triggered |
| `77` | WARNING | ⚠️ | Temperature control program 7 triggered |
| `78` | WARNING | ⚠️ | Temperature control program 8 triggered |

---

## Backwash

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `40` | WARNING | ⚠️ | Backwash skipped | Backwash manually, check time window |
| `41` | MESSAGE | ℹ️ | Pre-backwash refill failed | Check water supply |
| `42` | MESSAGE | ℹ️ | Refill not possible | Check refill valve and supply |
| `45` | ALERT | 🚨 | **Omnitronic no feedback (backwash)** | Check actuator, inspect wiring |
| `46` | ALERT | 🚨 | **Omnitronic no feedback (rinse)** | Check actuator |
| `47` | ALERT | 🚨 | **Omni actuator position not reached** | Check mechanics, inspect limit switches |
| `49` | ALERT | 🚨 | **Omnitronic feedback contact open** | Check connection and contact |

---

## Water Refill

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `50` | ALERT | 🚨 | **Safety time exceeded** | Check float switch and water supply |
| `51` | ALERT | 🚨 | **Upper float did not respond** | Clean/replace float switch |
| `52` | ALERT | 🚨 | **Lower float did not reset** | Clean/replace float switch |

---

## Overflow Tank

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `60` | ALERT | 🚨 | **Refill failed** | Check water supply and valve |
| `61` | WARNING | ⚠️ | Dry run | Increase fill level, check intake |
| `62` | WARNING | ⚠️ | Level measurement faulty | Clean/calibrate level probe |

---

## Temperature Sensors (101–112)

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `101` | WARNING | ⚠️ | Temperature sensor 1 missing | Check sensor cable, replace sensor |
| `102` | WARNING | ⚠️ | Temperature sensor 2 missing | Check sensor cable |
| `103–112` | WARNING | ⚠️ | Temperature sensors 3–12 missing | Check corresponding sensor |

**Steps for sensor failure:**
1. Check cable for damage
2. Clean connector on controller
3. Measure sensor with ohmmeter (1-Wire: ~1kΩ at 25°C)
4. If defective: Use same sensor type (DS18B20)

---

## Chlorine Dosing (120–125)

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `120` | WARNING | ⚠️ | ORP threshold chlorine dosing | Check ORP value, dose manually if needed |
| `121` | WARNING | ⚠️ | Chlorine threshold dosing | Check chlorine level |
| `122` | WARNING | ⚠️ | Max. daily dosing exceeded | Find cause (water loss, high demand) |
| `123` | WARNING | ⚠️ | Chlorine canister low | Refill! |
| `124` | WARNING | ⚠️ | **Chlorine canister empty** | Refill immediately, dosing interrupted |
| `125` | WARNING | ⚠️ | Empty indicator contact suction lance | Check canister level and suction lance |

---

## Electrolysis (130–135)

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `130` | WARNING | ⚠️ | ORP threshold electrolysis | Monitor ORP value |
| `131` | WARNING | ⚠️ | Chlorine threshold electrolysis | Check chlorine measurement |
| `132` | WARNING | ⚠️ | Max. daily production electrolysis | Check performance |
| `133` | WARNING | ⚠️ | Electrolysis remaining runtime | Check cell lifespan, plan maintenance |
| `134` | WARNING | ⚠️ | Max. operating hours electrolysis cell | Replace cell |
| `135` | WARNING | ⚠️ | Flow switch electrolysis | Check flow, clean switch |

---

## H2O2 Dosing (142–145)

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `142` | WARNING | ⚠️ | H2O2 max. daily dosing | Check water quality |
| `143` | WARNING | ⚠️ | H2O2 canister low | Refill |
| `144` | WARNING | ⚠️ | H2O2 canister empty | Refill immediately |
| `145` | WARNING | ⚠️ | Empty indicator oxygen canister | Check suction lance |

---

## pH Dosing (150–165)

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `150` | WARNING | ⚠️ | pH-minus threshold | Check pH value |
| `152` | WARNING | ⚠️ | pH-minus max. daily dosing | Check water chemistry |
| `153` | WARNING | ⚠️ | pH-minus canister low | Refill |
| `154` | WARNING | ⚠️ | **pH-minus canister empty** | Refill immediately |
| `155` | WARNING | ⚠️ | pH-minus empty indicator | Check suction lance |
| `160` | WARNING | ⚠️ | pH-plus threshold | Check pH value |
| `162` | WARNING | ⚠️ | pH-plus max. daily dosing | Check water chemistry |
| `163` | WARNING | ⚠️ | pH-plus canister low | Refill |
| `164` | WARNING | ⚠️ | **pH-plus canister empty** | Refill immediately |
| `165` | WARNING | ⚠️ | pH-plus empty indicator | Check suction lance |

---

## Flocculant (172–175)

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `172` | WARNING | ⚠️ | Flocculant max. daily dosing | Check water turbidity |
| `173` | WARNING | ⚠️ | Flocculant canister low | Refill |
| `174` | WARNING | ⚠️ | **Flocculant canister empty** | Refill immediately |
| `175` | WARNING | ⚠️ | Flocculant empty indicator | Check suction lance |

---

## Calibration Reminders (180–182)

| Code | Type | Severity | Description | Interval |
|------|------|----------|-------------|----------|
| `180` | REMINDER | ℹ️ | pH electrode calibration due | Monthly |
| `181` | REMINDER | ℹ️ | ORP electrode calibration due | Monthly |
| `182` | REMINDER | ℹ️ | Chlorine electrode calibration due | Monthly |

---

## Communication & Modules (200–210)

| Code | Type | Severity | Description | Solution |
|------|------|----------|-------------|----------|
| `200` | WARNING | ⚠️ | Dosing module disconnected | Check cable and connectors |
| `201` | WARNING | ⚠️ | Dosing module communication lost | Check bus communication |
| `203` | WARNING | ⚠️ | Relay extension 1 disconnected | Check cable |
| `204` | WARNING | ⚠️ | Relay extension 1 communication lost | Check bus communication |
| `206` | WARNING | ⚠️ | Relay extension 2 disconnected | Check cable |
| `207` | WARNING | ⚠️ | Relay extension 2 communication lost | Check bus communication |
| `209` | ALERT | 🚨 | **Second dosing module detected** | Only one dosing module allowed – remove |
| `210` | ALERT | 🚨 | **Incorrectly coded relay extension** | Check extension coding |

---

## Analog and Switch Rules (81–98)

### Analog Rules

| Code | Description |
|------|-------------|
| `81–88` | Analog rule programs 1–8 triggered |

### Switch Rules

| Code | Description |
|------|-------------|
| `91–98` | Switch rule programs 1–8 triggered |

---

## Using Error Codes in Home Assistant

### Query Error Sensor

```yaml
# Template sensor for current error code
template:
  - sensor:
      - name: "Pool Error Text"
        state: >
          {{ state_attr('sensor.violet_error_code', 'description') | default('No error') }}
```

### Automation on Critical Error

```yaml
automation:
  - alias: "Pool: Critical Error Alarm"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('sensor.violet_error_code', 'severity') == 'critical' }}
    action:
      - service: notify.mobile_app_phone
        data:
          title: "CRITICAL POOL ERROR"
          message: >
            Code: {{ states('sensor.violet_error_code') }}
            Problem: {{ state_attr('sensor.violet_error_code', 'subject') }}
            Details: {{ state_attr('sensor.violet_error_code', 'description') }}
```

### Automatic Calibration Reminder

```yaml
automation:
  - alias: "Pool: Calibration Due"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.violet_error_code') in ['180', '181', '182'] }}
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool: Calibration Required"
          message: >
            {{ state_attr('sensor.violet_error_code', 'subject') }}
```

---

## Unknown Error Codes

If a code is not listed here:

1. Check controller firmware version (newer codes in newer firmware)
2. Open controller web interface for direct error message
3. Create a [GitHub Issue](https://github.com/Xerolux/violet-hass/issues) with the code and description

---

*Back: [Troubleshooting](Troubleshooting) | Back: [Home](Home)*