# Diagnostics Data

> With the built-in diagnostics feature, you can download all relevant information about your Violet Pool Controller as a JSON file with a single click – ideal for bug reports and troubleshooting.

---

## What Are Diagnostics Data?

Home Assistant provides a built-in diagnostics function for integrations. When you click **"Download Diagnostics"**, a JSON file is created containing all important information about the current state of the integration – without sensitive data like passwords.

---

## Download Diagnostics Data

1. Go to **Settings → Devices & Services**
2. Click on **Violet Pool Controller**
3. Select your device
4. Click **"Download Diagnostics"** (⬇️)
5. A JSON file will be saved

> The file can be attached directly to a [GitHub Issue](https://github.com/Xerolux/violet-hass/issues).

---

## Contents of the Diagnostics Data

The downloaded JSON file is divided into the following sections:

### `integration`

Basic integration information:

```json
"integration": {
  "version": "1.0.5",
  "domain": "violet_pool_controller"
}
```

---

### `config_entry`

All configuration settings. **Passwords and usernames are automatically redacted (`**REDACTED**`).**

```json
"config_entry": {
  "title": "Violet Pool Controller • 50.0m³",
  "entry_id": "abc123...",
  "data": {
    "host": "192.168.1.100",
    "polling_interval": 10,
    "timeout_duration": 10,
    "retry_attempts": 3,
    "use_ssl": false,
    "verify_ssl": true,
    "device_id": 1,
    "device_name": "Violet Pool Controller",
    "controller_name": "Main Pool",
    "active_features": ["pump", "heater", "solar", "dosing_ph"],
    "password": "**REDACTED**"
  },
  "options": {}
}
```

---

### `device`

Current controller status:

```json
"device": {
  "name": "Violet Pool Controller",
  "controller_name": "Main Pool",
  "firmware": "1.1.9",
  "device_id": 1,
  "api_url": "192.168.1.100",
  "use_ssl": false,
  "available": true,
  "consecutive_failures": 0,
  "last_error": null
}
```

| Field | Meaning |
|------|---------|
| `available` | `true` = Controller reachable |
| `consecutive_failures` | Number of consecutive connection failures (from 5 onwards, the controller is marked as unavailable) |
| `last_error` | Last error text (null = no error) |
| `firmware` | Controller firmware version |

---

### `connection`

Connection metrics and health status:

```json
"connection": {
  "system_health_pct": 98.5,
  "last_latency_ms": 207.3,
  "average_latency_ms": 195.1,
  "total_api_requests": 432,
  "api_request_rate_per_min": 6.0,
  "seconds_since_last_update": 4.2,
  "last_update_success": true
}
```

| Field | Meaning |
|------|---------|
| `system_health_pct` | Health score 0–100% |
| `last_latency_ms` | Response time of the last API call in ms |
| `average_latency_ms` | Average of the last 60 measurements |
| `total_api_requests` | Total API requests since HA start |
| `api_request_rate_per_min` | Current request rate per minute |
| `seconds_since_last_update` | Seconds since the last successful update |
| `last_update_success` | `true` = last update successful |

---

### `current_data`

Snapshot of all current measurements from the controller (e.g., temperatures, pH, ORP, pump status):

```json
"current_data": {
  "onewire1_value": 27.3,
  "onewire2_value": 24.1,
  "pH_value": 7.25,
  "orp_value": 685,
  "PUMP": 1,
  "HEATER": 0,
  "FW": "1.1.9",
  ...
}
```

> The content depends on your controller and the enabled features. All available sensors are listed here.

---

### `poll_statistics`

Statistics about previous data queries:

```json
"poll_statistics": {
  "total_polls": 432,
  "first_poll": "2026-03-02T05:32:50",
  "last_poll": "2026-03-02T06:05:10",
  "avg_data_points": 403.0
}
```

| Field | Meaning |
|------|---------|
| `total_polls` | Total number of completed polls since start |
| `first_poll` | Timestamp of the first poll |
| `last_poll` | Timestamp of the last poll |
| `avg_data_points` | Average number of received data points per poll |

---

## Privacy & Security

Diagnostics data is **only generated locally** and only shared if you manually upload the file. The following fields are automatically redacted:

| Field | Treatment |
|------|-----------|
| `password` | `**REDACTED**` |
| `username` | `**REDACTED**` |
| All other fields | Plaintext |

> The controller's IP address (`host`) is visible in the diagnostics data. If you don't want to share it, replace it manually in a JSON editor before uploading the file.

---

## Using Diagnostics Data for a Bug Report

1. Download diagnostics data (see above)
2. Open the file in a text editor if needed and anonymize the IP
3. [Create a new issue](https://github.com/Xerolux/violet-hass/issues/new/choose)
4. Provide error description, HA version, and integration version
5. Attach the JSON file

---

## Related Pages

- [Troubleshooting](Troubleshooting) – Common problems & solutions
- [Advanced Logging](Erweiterte-Protokollierung) – Enable debug logs
- [Error Codes](Error-Codes) – Controller error codes explained
- [FAQ](FAQ) – Frequently asked questions