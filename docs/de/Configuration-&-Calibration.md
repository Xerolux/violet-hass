> [🇬🇧 English](../Configuration-&-Calibration) | [🇩🇪 Deutsch](Configuration-&-Calibration) &nbsp;|&nbsp; [🏠](Home)

# Konfiguration & Kalibrierung

## Konfiguration auslesen
Spezifische Systemkonfigurationsschlüssel abrufen.
```python
config_values = await api.get_config(["PUMP_SPEED_1", "PUMP_SPEED_2"])
print(config_values)
```

## Konfiguration ändern
Systemeinstellungen sicher aktualisieren (Eingaben werden automatisch bereinigt).
```python
await api.set_config({"PUMP_SPEED_1": 1500})
```

## Kalibrierungsdaten
```python
# Rohe Kalibrierungswerte fuer alle Sensoren abrufen
raw_calib = await api.get_calibration_raw_values()

# Kalibrierungsverlauf fuer einen bestimmten Sensor abrufen (z. B. "pH")
ph_history = await api.get_calibration_history("pH")
print(ph_history)

# Eine vorherige Kalibrierung wiederherstellen (erfordert Zeitstempel aus dem Verlauf)
await api.restore_calibration("pH", "2023-10-01T12:00:00")
```
