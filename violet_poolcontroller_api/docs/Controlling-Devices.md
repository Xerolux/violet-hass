> [🇬🇧 English](Controlling-Devices) | [🇩🇪 Deutsch](de/Controlling-Devices) &nbsp;|&nbsp; [🏠](Home)

# Controlling Devices

Many devices can be turned `ON`, `OFF`, or set to `AUTO`. Some devices support durations (`duration` in seconds, `0` means permanently) or speeds/values.

## Pump Control
```python
# Set filter pump to normal speed (2) permanently (0)
await api.set_pump_speed(speed=2, duration=0)

# Alternative general control: Turn pump OFF for 1 hour (3600 seconds)
await api.control_pump(action="OFF", duration=3600)
```
*Speeds:* `1` = ECO, `2` = Normal, `3` = Boost.

## Climate / Heating Control
```python
# Set Target Temperature for HEATER
await api.set_device_temperature("HEATER", 28.5)

# Set Target Temperature for SOLAR
await api.set_device_temperature("SOLAR", 30.0)

# Turn HEATER ON
await api.set_switch_state("HEATER", "ON")
```

## Light Control
```python
# Turn LIGHT ON
await api.set_switch_state("LIGHT", "ON")

# Trigger the Light Color Pulse
await api.set_light_color_pulse()
```

## Relays & Switches
You can control various relays like `BACKWASH`, `REFILL`, `ECO`, extension relays (`EXT1_1` to `EXT2_8`), and Omni DC outputs (`OMNI_DC0` to `OMNI_DC5`) using `set_switch_state`.
```python
# Turn on Extension Relay 1.1 for 5 minutes
await api.set_switch_state("EXT1_1", "ON", duration=300)
```

## DMX Scenes
The controller supports 12 DMX scenes (`DMX_SCENE1` to `DMX_SCENE12`).
```python
# Trigger DMX Scene 1
await api.set_switch_state("DMX_SCENE1", "ON")

# Turn ALL DMX Scenes OFF
await api.set_all_dmx_scenes("ALLOFF") # options: ALLON, ALLOFF, ALLAUTO
```

## Digital Input Rules
Digital input rules (`DIRULE_1` to `DIRULE_7`) can be triggered or locked.
```python
# Trigger Rule 1
await api.trigger_digital_input_rule("DIRULE_1")

# Lock Rule 1
await api.set_digital_input_rule_lock("DIRULE_1", locked=True)
```