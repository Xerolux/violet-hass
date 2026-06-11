> [🇬🇧 English](Configuration-&-Calibration) | [🇩🇪 Deutsch](de/Configuration-&-Calibration) &nbsp;|&nbsp; [🏠](Home)

# Configuration & Calibration

## Reading Configuration
Fetch specific system configuration keys.
```python
config_values = await api.get_config(["PUMP_SPEED_1", "PUMP_SPEED_2"])
print(config_values)
```

## Setting Configuration
Safely update system settings (input is sanitized automatically).
```python
await api.set_config({"PUMP_SPEED_1": 1500})
```

## Calibration Data
```python
# Get raw calibration values for all sensors
raw_calib = await api.get_calibration_raw_values()

# Get calibration history for a specific sensor (e.g., "pH")
ph_history = await api.get_calibration_history("pH")
print(ph_history)

# Restore a previous calibration (requires timestamp from history)
await api.restore_calibration("pH", "2023-10-01T12:00:00")
```