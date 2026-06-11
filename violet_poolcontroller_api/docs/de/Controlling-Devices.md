> [🇬🇧 English](../Controlling-Devices) | [🇩🇪 Deutsch](Controlling-Devices) &nbsp;|&nbsp; [🏠](Home)

# Geräte steuern

Viele Geräte können auf `ON` (Ein), `OFF` (Aus) oder `AUTO` geschaltet werden. Einige Geräte unterstützen Dauerangaben (`duration` in Sekunden, `0` bedeutet dauerhaft) oder Geschwindigkeiten/Werte.

## Pumpensteuerung
```python
# Filterpumpe auf normale Geschwindigkeit (2) dauerhaft (0) einstellen
await api.set_pump_speed(speed=2, duration=0)

# Alternative allgemeine Steuerung: Pumpe fuer 1 Stunde (3600 Sekunden) ausschalten
await api.control_pump(action="OFF", duration=3600)
```
*Geschwindigkeiten:* `1` = ECO, `2` = Normal, `3` = Boost.

## Klima- / Heizungssteuerung
```python
# Zieltemperatur fuer HEIZER setzen
await api.set_device_temperature("HEATER", 28.5)

# Zieltemperatur fuer SOLAR setzen
await api.set_device_temperature("SOLAR", 30.0)

# HEIZER einschalten
await api.set_switch_state("HEATER", "ON")
```

## Lichtsteuerung
```python
# LICHT einschalten
await api.set_switch_state("LIGHT", "ON")

# Licht-Farbpuls ausloesen
await api.set_light_color_pulse()
```

## Relais & Schalter
Du kannst verschiedene Relais wie `BACKWASH`, `REFILL`, `ECO`, Erweiterungsrelais (`EXT1_1` bis `EXT2_8`) und Omni DC-Ausgänge (`OMNI_DC0` bis `OMNI_DC5`) mit `set_switch_state` steuern.
```python
# Erweiterungsrelais 1.1 fuer 5 Minuten einschalten
await api.set_switch_state("EXT1_1", "ON", duration=300)
```

## DMX-Szenen
Der Controller unterstützt 12 DMX-Szenen (`DMX_SCENE1` bis `DMX_SCENE12`).
```python
# DMX-Szene 1 ausloesen
await api.set_switch_state("DMX_SCENE1", "ON")

# Alle DMX-Szenen ausschalten
await api.set_all_dmx_scenes("ALLOFF") # Optionen: ALLON, ALLOFF, ALLAUTO
```

## Digitaleingangsregeln
Digitaleingangsregeln (`DIRULE_1` bis `DIRULE_7`) können ausgelöst oder gesperrt werden.
```python
# Regel 1 ausloesen
await api.trigger_digital_input_rule("DIRULE_1")

# Regel 1 sperren
await api.set_digital_input_rule_lock("DIRULE_1", locked=True)
```
