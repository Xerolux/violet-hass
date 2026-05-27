> [🇬🇧 English](../Advanced-Topics) | [🇩🇪 Deutsch](Advanced-Topics) &nbsp;|&nbsp; [🏠](Home)

# Erweiterte Themen

## PV-Überschussmodus
Wenn du eine Photovoltaik-Anlage integriert hast, kannst du den PV-Überschussmodus aktivieren, um überschüssigen Solarstrom zu nutzen.
```python
# PV-Ueberschussmodus aktivieren und Pumpengeschwindigkeit auf 3 erzwingen
await api.set_pv_surplus(active=True, pump_speed=3)
```

## Testmodus
Den Hardware-Testmodus des Controllers für einen bestimmten Ausgang aktivieren.
```python
await api.set_output_test_mode(output="RELAY_1", mode="SWITCH", duration=120)
```

## Fehlerbehandlung
Alle API-Interaktionen können `VioletPoolAPIError` auslösen. Es wird empfohlen, Aufrufe in einen try-except-Block einzubetten.
```python
try:
    await api.get_readings()
except VioletPoolAPIError as e:
    print(f"API-Fehler: {e}")
```

## Rate Limiting & Circuit Breaker
Der API-Client enthält eingebaute Schutzmechanismen:
- **Rate Limiter:** Verhindert eine Überlastung des Controllers durch Warteschlangensteuerung von Anfragen (z. B. max. 10 Anfragen pro Sekunde).
- **Circuit Breaker:** Hält Anfragen vorübergehend an, wenn mehrere aufeinanderfolgende Fehler auftreten, damit sich der Controller erholen kann.
