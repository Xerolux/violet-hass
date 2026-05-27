> [🇬🇧 English](../Dosing-&-Targets) | [🇩🇪 Deutsch](Dosing-&-Targets) &nbsp;|&nbsp; [🏠](Home)

# Dosierung & Zielwerte

Alle Befehle in diesem Abschnitt werden in Standard-Violet-Konfigurationen sowie im Dosier-Standalone-Modus (`dosing_standalone=True`) unterstützt.

## Zielwerte
Die Chemie-Zielwerte deines Pools aktualisieren:
```python
# pH-Zielwert auf 7.2 setzen
await api.set_ph_target(7.2)

# ORP (Redox)-Zielwert auf 750 mV setzen
await api.set_orp_target(750)

# Mindest-Chlorgehalt auf 1,5 mg/l setzen
await api.set_min_chlorine_level(1.5)
```

## Manuelle Dosierung
Manuelle Dosierung für eine bestimmte Dauer (in Sekunden) auslösen.
Unterstützte Typen: `"Chlor"`, `"pH-"`, `"pH+"`, `"Elektrolyse"`, `"Flockmittel"`.
```python
# Manuell Chlor fuer 60 Sekunden dosieren
await api.manual_dosing(dosing_type="Chlor", duration=60)
```

## Dosierparameter
Spezifische Dosiereinstellungen über eine Zuordnung aktualisieren:
```python
parameters = {
    "DOS_1_CL_PER_H": 500,
    "DOS_4_PHM_PER_H": 250
}
await api.set_dosing_parameters(parameters)
```
