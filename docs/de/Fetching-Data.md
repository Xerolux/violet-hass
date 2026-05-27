> [🇬🇧 English](../Fetching-Data) | [🇩🇪 Deutsch](Fetching-Data) &nbsp;|&nbsp; [🏠](Home)

# Daten abrufen

## Alle Messwerte
Um alle aktuellen Sensor- und Gerätestatus abzurufen:
```python
readings = await api.get_readings()
print(readings)
```

## Spezifische Messwerte
Um die Datenübertragung zu optimieren, kannst du nur bestimmte Kategorien abrufen (z. B. `ADC`, `DOSAGE`, `SYSTEM`):
```python
readings = await api.get_specific_readings(["ADC", "SYSTEM"])
```

## Verlauf & Statistiken
```python
# Verlauf der letzten 24 Stunden abrufen
history = await api.get_history(hours=24, sensor="ALL")

# Gesamt-Dosierstatistik abrufen
dosing_stats = await api.get_overall_dosing()

# Ausgangszustaende abrufen
output_states = await api.get_output_states()
```

## Wetterdaten
Falls auf dem Controller konfiguriert, können aktuelle Wetterdaten abgerufen werden:
```python
weather = await api.get_weather_data()
```
## Violet Dosier-Standalone-Modus

Der API-Client unterstützt den Violet Dosier-Standalone-Controller. Während der ursprüngliche Basis-Modul-Controller in der Regel ein einfaches JSON-Dictionary mit Schlüssel-Wert-Paaren zurückgibt (z. B. `{"PUMPSTATE": "2", "PH": 7.2}`), liefert die neuere Standalone-Version teilweise Payloads als Liste von Dictionaries mit Parameterschemata und Werten.

Ab Version `0.0.7` erkennt `violet-poolController-api` diese listenbasierten Payloads der Standalone-Firmware automatisch und wandelt sie in das Standard-Dictionary-Format um. Das bedeutet, dass deine nachgeschalteten Anwendungen (wie z. B. Home Assistant) **keine Änderungen** benötigen und einheitlich funktionieren, unabhängig davon, ob du mit einem Basis-Modul oder einem Dosier-Standalone-Modul kommunizierst!
