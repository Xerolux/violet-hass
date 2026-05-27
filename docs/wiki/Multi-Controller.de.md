> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Multi-Controller)**

---

# Multi-Controller – Mehrere Pools verwalten

> Verwalte mehrere Violet Pool Controller gleichzeitig in einer einzigen Home Assistant Installation.

---

## Überblick

Die Violet Pool Controller Integration unterstützt **unbegrenzt viele Controller** in einer Home Assistant Instanz. Jeder Controller bekommt seinen eigenen Koordinator, eigene Entities und einen eigenen Bereich (Area).

```
Home Assistant
├── Außenpool (192.168.1.55)
│   ├── sensor.aussenpool_water_temperature
│   ├── switch.aussenpool_pump
│   └── climate.aussenpool_heater
│
├── Whirlpool (192.168.1.56)
│   ├── sensor.whirlpool_water_temperature
│   ├── switch.whirlpool_pump
│   └── climate.whirlpool_heater
│
└── Kinderpool (192.168.1.57)
    ├── sensor.kinderpool_water_temperature
    └── switch.kinderpool_pump
```

---

## Setup: Mehrere Controller hinzufügen

### Schritt 1: Erste Integration einrichten

Falls noch nicht geschehen: [Installation & Setup](Installation-and-Setup) folgen.

### Schritt 2: Weitere Controller hinzufügen

1. **Einstellungen** → **Geräte & Dienste**
2. Klicke **„Integration hinzufügen"** (unten rechts)
3. Suche nach **„Violet Pool Controller"**
4. Gib die Verbindungsdaten des zweiten Controllers ein
5. **Wichtig:** Vergib einen **eindeutigen Controller-Namen**

### Schritt 3: Eindeutige Namen vergeben

| Beispiel | Gut | Schlecht |
|----------|-----|---------|
| Außenbereich | `Außenpool` | `Pool` |
| Whirlpool | `Whirlpool` | `Violet Pool Controller` |
| Kinderpool | `Kinderpool` | `Pool 1` |

> **Tipp:** Der Controller-Name wird zur Area in Home Assistant und zu einem Präfix in den Entity-Namen. Kurze, sprechende Namen sind ideal.

---

## Technische Umsetzung

### Entity-IDs

Jede Entity hat eine eindeutige ID basierend auf der `entry_id`:

```
{entry_id}_{entity_key}
```

Beispiele:
- `sensor.aussenpool_water_temperature`
- `sensor.whirlpool_water_temperature`
- `switch.aussenpool_pump`
- `switch.whirlpool_pump`

### Device-Identifikatoren

```python
# Eindeutig per IP + Device-ID
(DOMAIN, f"{api_url}_{device_id}")
```

### Automatische Bereichszuweisung

Home Assistant erstellt automatisch Bereiche basierend auf `suggested_area`:

```
📍 Außenpool
  ├─ Beckenwasser Temperatur
  ├─ pH-Wert
  ├─ Filterpumpe
  └─ ...

📍 Whirlpool
  ├─ Beckenwasser Temperatur
  ├─ pH-Wert
  ├─ Filterpumpe
  └─ ...
```

---

## Dashboard-Konfiguration

### Tabs für jeden Pool

```yaml
# Lovelace-Konfiguration mit Tabs
views:
  - title: Außenpool
    path: aussenpool
    cards:
      - type: entities
        title: Außenpool – Sensoren
        entities:
          - sensor.aussenpool_water_temperature
          - sensor.aussenpool_ph_value
          - sensor.aussenpool_orp_value
      - type: thermostat
        entity: climate.aussenpool_heater

  - title: Whirlpool
    path: whirlpool
    cards:
      - type: entities
        title: Whirlpool – Sensoren
        entities:
          - sensor.whirlpool_water_temperature
          - sensor.whirlpool_ph_value
```

### Übersichts-Karte für alle Pools

```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.aussenpool_water_temperature
        name: Außenpool Temp.
      - type: entity
        entity: sensor.whirlpool_water_temperature
        name: Whirlpool Temp.

  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.aussenpool_ph_value
        name: Außenpool pH
      - type: entity
        entity: sensor.whirlpool_ph_value
        name: Whirlpool pH
```

---

## Automatisierungen mit mehreren Controllern

### pH-Wert vergleichen und warnen

```yaml
automation:
  - alias: "Multi-Pool: pH-Vergleich"
    trigger:
      - platform: numeric_state
        entity_id:
          - sensor.aussenpool_ph_value
          - sensor.whirlpool_ph_value
        below: 7.0
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool pH-Alarm"
          message: >
            Außenpool: {{ states('sensor.aussenpool_ph_value') }} pH
            Whirlpool: {{ states('sensor.whirlpool_ph_value') }} pH
```

### Beide Pumpen gleichzeitig steuern

```yaml
automation:
  - alias: "Alle Pumpen nachts aus"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id:
            - switch.aussenpool_pump
            - switch.whirlpool_pump
            - switch.kinderpool_pump
```

### Pool-übergreifende Durchschnittswerte

```yaml
# Template-Sensor für Durchschnittstemperatur
template:
  - sensor:
      - name: "Alle Pools Durchschnittstemperatur"
        unit_of_measurement: "°C"
        state: >
          {{ (
            states('sensor.aussenpool_water_temperature') | float(0) +
            states('sensor.whirlpool_water_temperature') | float(0)
          ) / 2 | round(1) }}
```

---

## Netzwerk-Konfiguration

### Empfehlungen

| Aspekt | Empfehlung |
|--------|-----------|
| **IP-Adressen** | Statische IPs (DHCP-Reservierung) verwenden |
| **Netzwerk** | Alle Controller im selben Subnetz |
| **Polling-Intervall** | Bei 3+ Controllern: 30-60 Sekunden |
| **SSL** | Konsistente Einstellung (alle SSL oder keiner) |

### DHCP-Reservierung (Fritzbox)

```
Heimnetz → Netzwerk → Netzwerkverbindungen → Gerät → IP-Adresse immer zuweisen
```

---

## Best Practices

### Namensgebung

```
Gut:
- "Außenpool"          → sensor.aussenpool_*
- "Whirlpool"          → sensor.whirlpool_*
- "Pool Erdgeschoss"   → sensor.pool_erdgeschoss_*

Vermeiden:
- "Pool 1"             → zu generisch
- "Violet Pool"        → Standard-Name, nicht eindeutig
```

### Performance

- **Staffeln** der Polling-Zeiten durch unterschiedliche Intervalle
- Bei 2-3 Controllern: 20-30s Intervall
- Bei 4+ Controllern: 30-60s Intervall empfohlen

### Backup

Vor dem Hinzufügen weiterer Controller:
```
Einstellungen → System → Backups → Backup erstellen
```

---

## Upgrade & Migration

### Bestehende Installation umbenennen

So änderst du den Controller-Namen nachträglich:

1. **Einstellungen** → **Geräte & Dienste**
2. „Violet Pool Controller" auswählen
3. Klicke auf **Gerätename** → Bearbeiten

> **Hinweis:** Das ändert nur den Anzeigenamen. Für neue Entity-IDs: Integration entfernen und neu hinzufügen.

### Migration von Einzel- zu Multi-Controller

1. Erstelle ein Backup
2. Notiere alle Automatisierungen
3. Füge zweite Integration hinzu
4. Passe Automatisierungen auf neue Entity-IDs an

---

## Troubleshooting

### Problem: Entities haben identische Namen

**Ursache:** Beide Controller haben den gleichen Namen.

**Lösung:**
1. Einstellungen → Geräte & Dienste
2. Controller umbenennen (eindeutige Namen!)

### Problem: Controller erscheint nicht in separatem Bereich

**Lösung:** Prüfe ob `controller_name` im Config Entry korrekt gesetzt ist.

```
Einstellungen → Geräte & Dienste → [Integration] → Konfigurieren
```

### Problem: Zu viele API-Anfragen

**Lösung:** Polling-Intervall erhöhen:
```
Einstellungen → Geräte & Dienste → Violet Pool Controller → Konfigurieren
→ Abfrageintervall: 45 Sekunden
```

### Problem: Ein Controller offline, andere funktionieren

Das ist normales Verhalten! Jeder Controller ist unabhängig. Der ausgefallene Controller zeigt `unavailable`, die anderen arbeiten weiter.

---

## Support

- **GitHub Issues:** https://github.com/Xerolux/violet-hass/issues
- **Wiki:** [Troubleshooting](Troubleshooting)
- **FAQ:** [FAQ](FAQ)

---

*Zuletzt aktualisiert: 2026-02-23*