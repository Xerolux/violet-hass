> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Automations)**

---

# Automatisierungs-Beispiele

> Copy-paste YAML-Beispiele für häufige Pool-Automatisierungen.

---

## Schnellstart

Alle Beispiele können direkt in Home Assistant eingefügt werden:
**Einstellungen → Automatisierungen → Erstellen → YAML-Modus**

---

## Pumpen-Steuerung

### Tagesprogramm (Zeitgesteuert)

```yaml
# Pumpe morgens einschalten
automation:
  - alias: "Pool: Pumpe Morgens ein"
    description: "Filterpumpe täglich um 8 Uhr einschalten"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 2

  - alias: "Pool: Pumpe Nachts aus"
    description: "Filterpumpe um 22 Uhr ausschalten"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 1
```

### Pumpe bei Solarüberschuss hochdrehen

```yaml
automation:
  - alias: "Pool: Pumpe bei PV-Überschuss"
    description: "Bei viel Solar mehr filtern"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_production
        above: 3000
    condition:
      - condition: time
        after: "09:00:00"
        before: "18:00:00"
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 3
          duration: 7200

  - alias: "Pool: Pumpe nach PV-Überschuss normalisieren"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_production
        below: 1000
    action:
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 2
```

### Pumpe bei Frost schützen

```yaml
automation:
  - alias: "Pool: Frostschutz Pumpe"
    description: "Pumpe bei drohenden Frost einschalten"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outside_temperature
        below: 3
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "off"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_pump
      - service: notify.mobile_app_phone
        data:
          title: "Frost-Alarm"
          message: "Frostschutz aktiv – Filterpumpe eingeschaltet!"
```

---

## Wasserchemie & Dosierung

### Automatische pH-Korrektur

```yaml
automation:
  - alias: "Pool: pH zu niedrig – pH+ dosieren"
    description: "pH+ dosieren wenn pH unter 7.1 fällt"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        below: 7.1
        for:
          minutes: 15
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "on"
    action:
      - service: violet_pool_controller.smart_dosing
        data:
          dosing_type: "pH+"
          action: manual_dose
          duration: 30
      - delay:
          minutes: 60
      - service: notify.mobile_app_phone
        data:
          title: "Pool pH-Alarm"
          message: "pH war zu niedrig ({{ states('sensor.violet_ph_value') }}). pH+ wurde dosiert."

  - alias: "Pool: pH zu hoch – pH- dosieren"
    description: "pH- dosieren wenn pH über 7.6 steigt"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        above: 7.6
        for:
          minutes: 15
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "on"
    action:
      - service: violet_pool_controller.smart_dosing
        data:
          dosing_type: "pH-"
          action: manual_dose
          duration: 30
```

### Chlor-Dosierung nach ORP-Wert

```yaml
automation:
  - alias: "Pool: Chlor nachfüllen bei niedrigem ORP"
    description: "Chlor dosieren wenn ORP unter 650 mV fällt"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_orp_value
        below: 650
        for:
          minutes: 30
    condition:
      - condition: state
        entity_id: switch.violet_pump
        state: "on"
      - condition: time
        after: "10:00:00"
        before: "20:00:00"
    action:
      - service: violet_pool_controller.smart_dosing
        data:
          dosing_type: Chlor
          action: manual_dose
          duration: 45
```

### Wöchentliche Stoßchlorierung

```yaml
automation:
  - alias: "Pool: Wöchentliche Stoßchlorierung"
    description: "Jeden Montag Chlor nachfüllen"
    trigger:
      - platform: time
        at: "10:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: violet_pool_controller.smart_dosing
        data:
          dosing_type: Chlor
          action: manual_dose
          duration: 60
          safety_override: false
      - service: notify.mobile_app_phone
        data:
          message: "Wöchentliche Stoßchlorierung abgeschlossen"
```

---

## Temperatur & Heizung

### Heizung nach Zeitplan

```yaml
automation:
  - alias: "Pool: Wochenend-Heizung"
    description: "Wochenende: Wasser auf 30°C aufheizen"
    trigger:
      - platform: time
        at: "06:00:00"
    condition:
      - condition: time
        weekday:
          - fri
          - sat
          - sun
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 30
          hvac_mode: heat

  - alias: "Pool: Wochentag Eco-Heizung"
    trigger:
      - platform: time
        at: "06:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 26
          hvac_mode: auto
```

### Benachrichtigung wenn Pool warm genug

```yaml
automation:
  - alias: "Pool: Temperatur-Benachrichtigung"
    description: "Info wenn Pool Badetemeratur erreicht"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_water_temperature
        above: 27
    condition:
      - condition: time
        after: "08:00:00"
        before: "21:00:00"
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool ist warm!"
          message: >
            Wassertemperatur: {{ states('sensor.violet_water_temperature') }}°C
            pH: {{ states('sensor.violet_ph_value') }}
            ORP: {{ states('sensor.violet_orp_value') }} mV
```

---

## Beleuchtung & Atmosphäre

### Abendbeleuchtung automatisch

```yaml
automation:
  - alias: "Pool: Abendbeleuchtung"
    description: "Beleuchtung bei Sonnenuntergang einschalten"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:15:00"
    condition:
      - condition: time
        before: "23:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_dmx_scene_1
      - delay:
          hours: 3
      - service: switch.turn_off
        target:
          entity_id: switch.violet_dmx_scene_1

  - alias: "Pool: Beleuchtung aus bei Sonnenaufgang"
    trigger:
      - platform: sun
        event: sunrise
    action:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.violet_dmx_scene_1
            - switch.violet_dmx_scene_2
```

### Party-Modus

```yaml
automation:
  - alias: "Pool: Party-Modus aktivieren"
    trigger:
      - platform: state
        entity_id: input_boolean.party_mode
        to: "on"
    action:
      - service: violet_pool_controller.control_dmx_scenes
        data:
          action: party_mode
      - service: violet_pool_controller.control_pump
        data:
          action: speed_control
          speed: 2
      - service: climate.set_temperature
        target:
          entity_id: climate.violet_heater
        data:
          temperature: 30
          hvac_mode: heat

  - alias: "Pool: Party-Modus deaktivieren"
    trigger:
      - platform: state
        entity_id: input_boolean.party_mode
        to: "off"
    action:
      - service: violet_pool_controller.control_dmx_scenes
        data:
          action: all_off
```

---

## Cover / Abdeckung

### Abdeckung automatisch fahren

```yaml
automation:
  - alias: "Pool: Abdeckung schließen bei Regen"
    trigger:
      - platform: state
        entity_id: weather.home
        to: "rainy"
    condition:
      - condition: state
        entity_id: cover.violet_cover
        state: "open"
    action:
      - service: cover.close_cover
        target:
          entity_id: cover.violet_cover
      - service: notify.mobile_app_phone
        data:
          message: "Pool-Abdeckung automatisch geschlossen (Regen)"

  - alias: "Pool: Abdeckung morgens öffnen"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: state
        entity_id: weather.home
        state: "sunny"
    action:
      - service: cover.open_cover
        target:
          entity_id: cover.violet_cover
```

---

## Wartungs-Erinnerungen

### Kalibrierungs-Erinnerung

```yaml
automation:
  - alias: "Pool: Kalibrierungs-Erinnerung"
    description: "Monatliche Erinnerung zur Elektroden-Kalibrierung"
    trigger:
      - platform: time
        at: "10:00:00"
    condition:
      - condition: template
        value_template: >
          {{ now().day == 1 }}
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool Wartung"
          message: >
            Monatliche Erinnerung:
            - pH-Elektrode kalibrieren
            - ORP-Elektrode prüfen
            - Filter reinigen
            - Kanister-Füllstände prüfen
```

### Wochencheck mit Statusbericht

```yaml
automation:
  - alias: "Pool: Wöchentlicher Statusbericht"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool Wochencheck"
          message: >
            Wasser: {{ states('sensor.violet_water_temperature') }}°C
            pH: {{ states('sensor.violet_ph_value') }}
            ORP: {{ states('sensor.violet_orp_value') }} mV
            Chlor: {{ states('sensor.violet_chlorine') }} mg/l
            Pumpe: {{ states('switch.violet_pump') }}
            Heizung: {{ states('climate.violet_heater') }}
```

---

## Alarme & Benachrichtigungen

### Alarmanlage für kritische Werte

```yaml
automation:
  - alias: "Pool: Kritischer pH-Alarm"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_ph_value
        below: 6.8
    action:
      - service: notify.mobile_app_phone
        data:
          title: "ALARM: Pool pH kritisch!"
          message: >
            pH-Wert: {{ states('sensor.violet_ph_value') }}
            Sofort pH+ dosieren!

  - alias: "Pool: Temperaturfühler-Alarm"
    trigger:
      - platform: state
        entity_id: sensor.violet_water_temperature
        to: "unavailable"
        for:
          minutes: 5
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool Sensor-Ausfall"
          message: "Temperaturfühler meldet keinen Wert!"
```

---

## Blueprint: Fertige Vorlagen

Das Repository enthält fertige Blueprints im Verzeichnis `blueprints/automation/`.

**Installation:**
1. Blueprint-Datei in `config/blueprints/automation/violet_pool/` kopieren
2. Einstellungen → Automatisierungen → Blueprints → Importieren

### Kühlen mit einer Wärmepumpe

`pool_heatpump_cooling.yaml` regelt die Pooltemperatur gemeinsam mit einer
kühlfähigen Wärmepumpe in **beide** Richtungen.

Der Violet Pool Controller kann nicht kühlen: seine API kennt nur die Ausgänge
`HEATER` und `SOLAR`, beide heizen. Seine Climate-Entitäten bieten deshalb
keinen `cool`-Modus an — und werden das auch nicht tun, denn ein Modus, den die
Hardware nicht ausführen kann, wäre ein Versprechen, das die Integration nicht
halten kann. Gekühlt wird von der Wärmepumpe über deren eigene Integration; der
Blueprint verbindet beides:

- Ein `input_number`-Helper hält die Solltemperatur und wird auf die Wärmepumpe
  durchgeschrieben. Der Wert, den du in Home Assistant einstellst, ist damit
  der Wert, auf den die Wärmepumpe tatsächlich regelt.
- Pool über Soll + Hysterese → Wärmepumpe auf `cool`, unter Soll − Hysterese →
  `heat`, innerhalb des Totbands → ein konfigurierbarer Ruhemodus.
- Optional wird der Violet-Heizsollwert auf einer hohen Freigabetemperatur
  gehalten, damit der Controller das Ventil offen lässt und die Wärmepumpe
  Durchfluss sieht. Das ersetzt den verbreiteten Workaround, in der
  Violet-Oberfläche einen irreführend hohen Sollwert stehen zu lassen, während
  in Wirklichkeit die Wärmepumpe regelt.

Modi werden nur gesendet, wenn die Wärmepumpe sie in `hvac_modes` meldet, und
solange ein Messwert `unavailable` ist, wird nichts geschrieben.

**Vorbereitung: den Helper anlegen**

Ein Blueprint kann keine Helfer anlegen — das ist der eine Schritt, der von
Hand passieren muss. Ohne ihn hat die Automatisierung nichts, wogegen sie
regeln könnte.

Einstellungen → Geräte & Dienste → **Helfer** → *+ Helfer erstellen* → **Zahl**

| Feld | Wert |
|------|------|
| Name | z. B. `Pool Solltemperatur` (frei wählbar) |
| Minimum | `20` |
| Maximum | `32` |
| Schrittweite | `0.5` |
| Maßeinheit | `°C` |
| Anzeigemodus | Eingabefeld oder Schieberegler, wie du magst |

Danach den Blueprint importieren (Einstellungen → Automatisierungen & Szenen →
**Blueprints** → *Blueprint importieren*, URL der Datei einfügen), eine
Automatisierung daraus anlegen und die Entitäten zuweisen: Pool-Sensor,
Wärmepumpe, und der eben angelegte Helper.

**Nach dem Import: was aufs Dashboard gehört**

Der Blueprint erzeugt eine *Automatisierung*. Die Entität, die danach im
Dashboard auftaucht (`automation.violet_pool_heat_pump_heating_cooling`), ist
deren Ein/Aus-Schalter — mehr zeigt sie nicht an. Die Solltemperatur stellst du
am `input_number`-Helper ein; ein eigenes Climate-Objekt legt der Blueprint
nicht an, denn genau weil der Controller keinen `cool`-Modus hat, gibt es den
Blueprint überhaupt. Geregelt wird über die Climate-Entität der Wärmepumpe.

Eine passende Karte — Entity-IDs an die eigene Anlage anpassen:

```yaml
type: entities
title: Pool-Temperatur
entities:
  - entity: input_number.pool_solltemperatur   # hier wird die Temperatur eingestellt
    name: Solltemperatur
  - entity: sensor.violet_pool_controller_pool_water   # ältere Installationen: ..._poolwasser
    name: Ist-Temperatur
  - entity: climate.waermepumpe
    name: Wärmepumpe
  - entity: automation.violet_pool_heat_pump_heating_cooling
    name: Regelung aktiv
```

Der Blueprint schreibt jede Änderung am Helper auf die Wärmepumpe durch: der
Wert im Helper ist damit der Wert, auf den die Wärmepumpe tatsächlich regelt.
Stell die Temperatur deshalb **nur dort** ein — was du direkt an der Karte der
Wärmepumpe eintippst, wird beim nächsten Lauf wieder überschrieben.

Die optionale Freigabetemperatur für den Violet-Heizer nimmt Werte von 20 bis
35 °C; darüber lehnt der Controller den Sollwert ab, und das Ventil bliebe zu.

---

*Zurück: [Services](Services) | Weiter: [Troubleshooting](Troubleshooting)*