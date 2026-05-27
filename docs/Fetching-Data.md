> [🇬🇧 English](Fetching-Data) | [🇩🇪 Deutsch](de/Fetching-Data) &nbsp;|&nbsp; [🏠](Home)

# Fetching Data

## All Readings
To retrieve all current sensor and device states:
```python
readings = await api.get_readings()
print(readings)
```

## Specific Readings
To optimize data transfer, you can fetch only specific categories (e.g., `ADC`, `DOSAGE`, `SYSTEM`):
```python
readings = await api.get_specific_readings(["ADC", "SYSTEM"])
```

## History & Statistics
```python
# Fetch history for the last 24 hours
history = await api.get_history(hours=24, sensor="ALL")

# Fetch overall dosing statistics
dosing_stats = await api.get_overall_dosing()

# Fetch output states
output_states = await api.get_output_states()
```

## Weather Data
If configured on the controller, fetch current weather data:
```python
weather = await api.get_weather_data()
```
## Violet Dosing Standalone Mode

The API client seamlessly supports the Violet Dosing Standalone controller. While the original Base Module controller generally returns a flat JSON dictionary of key-value pairs (e.g., `{"PUMPSTATE": "2", "PH": 7.2}`), the newer Standalone version sometimes provides payloads as a list of dictionaries outlining parameter schemas and values.

As of version `0.0.7`, `violet-poolController-api` automatically detects these list-based payloads from the standalone firmware and flattens them into the standard dictionary format. This means your downstream applications (such as Home Assistant) require **no modifications** and will work uniformly whether you are communicating with a Base Module or a Dosing Standalone Module!
