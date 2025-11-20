# Multi-Controller Support Guide

## ✨ Feature Overview

Die Violet Pool Controller Integration unterstützt jetzt **mehrere Controller gleichzeitig** in einer Home Assistant Installation!

## 🎯 Was ist neu?

### 1. **Controller-Name-Feld**
- Beim Hinzufügen eines Controllers kannst du jetzt einen eindeutigen Namen vergeben
- Beispiele: "Pool 1", "Pool 2", "Hauptpool", "Whirlpool", etc.
- Standard: "Violet Pool Controller" (für Abwärtskompatibilität)

### 2. **Automatische Bereichszuweisung**
- Jeder Controller bekommt automatisch einen eigenen Bereich (Area)
- Alle Entities eines Controllers werden gruppiert
- Visuelle Trennung im Dashboard

### 3. **Eindeutige Entity-IDs**
- Jeder Controller hat einen separaten `entry_id`
- Entities: `{entry_id}_{entity_key}` - automatisch eindeutig
- Keine Konflikte zwischen Controllern

## 📋 Setup-Anleitung

### Controller hinzufügen

1. **Gehe zu:** Einstellungen → Geräte & Dienste
2. **Klicke auf:** "Integration hinzufügen"
3. **Suche nach:** "Violet Pool Controller"
4. **Wichtig:** Vergebe einen **eindeutigen Controller-Namen**
   - ✅ "Pool 1", "Außenpool", "Whirlpool"
   - ❌ Nicht mehrfach: "Violet Pool Controller"

### Mehrere Controller

Wiederhole den Prozess für jeden zusätzlichen Controller:

```
Controller 1:
  - Name: "Außenpool"
  - IP: 192.168.178.55
  - Bereich: "Außenpool" (automatisch)

Controller 2:
  - Name: "Whirlpool"
  - IP: 192.168.178.56
  - Bereich: "Whirlpool" (automatisch)
```

## 🏗️ Technische Details

### Geänderte Dateien

1. **const.py**
   - Neue Konstante: `CONF_CONTROLLER_NAME`
   - Default: `DEFAULT_CONTROLLER_NAME = "Violet Pool Controller"`

2. **config_flow.py**
   - Neues Feld im Connection-Setup: `CONF_CONTROLLER_NAME`
   - Entry-Title verwendet jetzt Controller-Name

3. **__init__.py**
   - Extrahiert `controller_name` aus Config Entry
   - Übergibt an Device

4. **device.py**
   - Speichert `controller_name`
   - `device_info` verwendet:
     - `name`: Controller-Name (statt Device-Name)
     - `suggested_area`: Controller-Name für Auto-Gruppierung

### Entity-Struktur

```python
# Config Entry Unique ID (bereits eindeutig pro IP+Device-ID)
f"{ip_address}-{device_id}"

# Device Identifier
(DOMAIN, f"{api_url}_{device_id}")

# Entity Unique ID (automatisch eindeutig durch entry_id)
f"{config_entry.entry_id}_{entity_key}"
```

## 🎨 Dashboard-Organisation

### Automatische Bereiche

Home Assistant erstellt automatisch Bereiche basierend auf `suggested_area`:

```
📍 Außenpool
  ├─ 🌡️ Beckenwasser Temperatur
  ├─ 💧 pH-Wert
  ├─ 💦 Filterpumpe
  └─ ...

📍 Whirlpool
  ├─ 🌡️ Beckenwasser Temperatur
  ├─ 💧 pH-Wert
  ├─ 💦 Filterpumpe
  └─ ...
```

### Dashboard-Ansicht

Jeder Controller erscheint als separates Gerät:

```yaml
# Beispiel Dashboard-Karte
type: entities
title: Alle Pool Controller
entities:
  - entity: sensor.aussenpool_water_temp
  - entity: sensor.whirlpool_water_temp
```

## ✅ Best Practices

### Namensgebung

- ✅ **Sprechende Namen:** "Außenpool", "Whirlpool", "Pool Erdgeschoss"
- ✅ **Kurz & prägnant:** Maximal 2-3 Wörter
- ❌ **Nicht generisch:** "Pool 1", "Pool 2" nur wenn wirklich nötig

### Netzwerk

- Jeder Controller braucht eine **eigene IP-Adresse**
- Stelle sicher, dass alle Controller im **selben Netzwerk** sind
- **Feste IPs** (DHCP-Reservierung) empfohlen

### Performance

- Jeder Controller hat einen **eigenen Coordinator**
- Polling-Intervalle sind **unabhängig** voneinander
- Bei vielen Controllern: Polling-Intervall erhöhen (z.B. 15-30s)

## 🔧 Troubleshooting

### Problem: Entities haben gleiche Namen

**Lösung:** Verwende eindeutige Controller-Namen beim Setup

### Problem: Controller erscheint nicht in separatem Bereich

**Lösung:** Prüfe, ob `controller_name` korrekt gesetzt ist in:
- Einstellungen → Geräte & Dienste → [Deine Integration]

### Problem: Entity-IDs überschneiden sich

**Lösung:** Dies sollte **nicht** passieren, da `entry_id` automatisch eindeutig ist.
Falls doch: Entferne und füge den Controller neu hinzu.

## 📊 Upgrade von vorherigen Versionen

### Bestehende Installation

Bestehende Installationen behalten den Default-Namen:
- Controller-Name: "Violet Pool Controller"
- Bereich: "Violet Pool Controller"

### Umbenennen

So änderst du den Controller-Namen nachträglich:

1. Einstellungen → Geräte & Dienste
2. Finde "Violet Pool Controller"
3. Klicke auf das Gerät
4. Klicke auf "Umbenennen" (Zahnrad-Symbol)
5. Vergebe neuen Namen

**Hinweis:** Dies ändert nur den Anzeigenamen, nicht den Bereich.
Für einen neuen Bereich: Integration entfernen und neu hinzufügen.

## 🚀 Neue Möglichkeiten

### Automatisierungen

```yaml
# Beispiel: Synchronisiere pH-Werte aller Pools
automation:
  - alias: "Pool pH Synchronisation"
    trigger:
      - platform: numeric_state
        entity_id: sensor.aussenpool_ph_value
        below: 7.0
    action:
      - service: notify.mobile_app
        data:
          message: "Außenpool pH zu niedrig! Whirlpool: {{ states('sensor.whirlpool_ph_value') }}"
```

### Dashboard mit Tabs

```yaml
# Beispiel: Tabs für jeden Pool
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: button
        name: Außenpool
        tap_action:
          action: navigate
          navigation_path: /lovelace/aussenpool
      - type: button
        name: Whirlpool
        tap_action:
          action: navigate
          navigation_path: /lovelace/whirlpool
```

## 📝 Changelog

### v0.2.1-beta.1 (2025-11-20)

✨ **Neue Features:**
- Multi-Controller Support mit eindeutigen Namen
- Automatische Bereichszuweisung (`suggested_area`)
- Verbesserte visuelle Trennung im Dashboard

🔧 **Technische Änderungen:**
- Neue Config-Option: `CONF_CONTROLLER_NAME`
- Device-Info verwendet jetzt `controller_name`
- Entry-Title zeigt Controller-Name

🛡️ **Abwärtskompatibilität:**
- Bestehende Installationen funktionieren weiterhin
- Default-Name: "Violet Pool Controller"

## 💡 Tipps

1. **Plane voraus:** Überlege dir eine konsistente Namensgebung
2. **Nutze Bereiche:** Organisation im Dashboard wird deutlich einfacher
3. **Dashboard-Vorlagen:** Erstelle eine Vorlage für einen Pool, kopiere sie für weitere
4. **Automationen:** Nutze Template-Sensoren für Pool-übergreifende Vergleiche

## 🆘 Support

Bei Fragen oder Problemen:
- **GitHub Issues:** https://github.com/xerolux/violet-hass/issues
- **Dokumentation:** https://github.com/xerolux/violet-hass/blob/main/README.md
