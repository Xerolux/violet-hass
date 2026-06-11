> [🇬🇧 English](Dosing-&-Targets) | [🇩🇪 Deutsch](de/Dosing-&-Targets) &nbsp;|&nbsp; [🏠](Home)

# Dosing & Targets

All commands in this section are supported in standard Violet setups and in dosing-standalone mode (`dosing_standalone=True`).

## Target Values
Update your pool's chemistry targets:
```python
# Set pH target to 7.2
await api.set_ph_target(7.2)

# Set ORP (Redox) target to 750 mV
await api.set_orp_target(750)

# Set Minimum Chlorine target to 1.5 mg/l
await api.set_min_chlorine_level(1.5)
```

## Manual Dosing
Trigger manual dosing for a specific duration (in seconds).
Supported types: `"Chlor"`, `"pH-"`, `"pH+"`, `"Elektrolyse"`, `"Flockmittel"`.
```python
# Manually dose Chlorine for 60 seconds
await api.manual_dosing(dosing_type="Chlor", duration=60)
```

## Dosing Parameters
Update specific dosing settings via a mapping:
```python
parameters = {
    "DOS_1_CL_PER_H": 500,
    "DOS_4_PHM_PER_H": 250
}
await api.set_dosing_parameters(parameters)
```
