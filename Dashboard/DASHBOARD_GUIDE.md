# 🎨 Violet Pool Controller - ULTIMATE Dashboard Guide

## ⭐ NEU: Komplett-Control Dashboards

Ich habe zwei neue Dashboard-Vorlagen erstellt, die **ALLE Einstellungen für jedes Gerät in kompakten Blöcken** anzeigen!

---

## 🚀 Quick Start - EINFACH & GENIAL

### **Option 1: Simple Blocks** ← EMPFOHLEN!

**Datei:** `pool_control_simple_blocks.yaml`

**Funktioniert SOFORT ohne zusätzliche Custom Cards!**

#### Was du siehst:

```
┌──────────────────────────────────┐
│ 🏊 FILTERPUMPE                   │
├──────────────────────────────────┤
│ Status: ❄️ Frostschutz           │
│ Modus: [Auto ▼] [Ein] [Aus]     │
│ Geschwindigkeit: ⚡⚡⚫ 2          │
│ Laufzeit: 17h 27m                │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ 🔥 HEIZUNG                       │
├──────────────────────────────────┤
│ Status: Auto (Bereit)            │
│ Modus: [Auto ▼]                  │
│ Zieltemperatur: [28°C]           │
│ Aktuelle Temp: 3.3°C             │
│ Laufzeit: 0h                     │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ 💧 pH STEUERUNG                  │
├──────────────────────────────────┤
│ pH aktuell: 7.2 ✅               │
│ pH Sollwert: [7.2]               │
│                                  │
│ ── pH Minus ──                   │
│ Modus: [Auto ▼]                  │
│ Kanister: [9499 ml]              │
│ Reichweite: >99d                 │
│ Laufzeit: 0h                     │
│                                  │
│ ── pH Plus ──                    │
│ Modus: [Auto ▼]                  │
│ Kanister: [20000 ml]             │
│ Reichweite: >99d                 │
│ Laufzeit: 0h                     │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ 🟢 CHLOR STEUERUNG               │
├──────────────────────────────────┤
│ Chlor aktuell: 0.8 mg/l ✅       │
│ Chlor Sollwert: [0.6 mg/l]       │
│ Redox aktuell: 720 mV            │
│ Redox Sollwert: [700 mV]         │
│                                  │
│ ── Dosierung ──                  │
│ Modus: [Auto ▼]                  │
│ Kanister: [16367 ml]             │
│ Reichweite: 41d                  │
│ Laufzeit: 0h                     │
└──────────────────────────────────┘
```

#### Installation:

1. **Home Assistant öffnen**
2. **Übersicht** → Rechts oben **⋮** → **Dashboard bearbeiten**
3. **+ Karte hinzufügen** → Ganz unten **"Manuell"**
4. **Kopiere den Inhalt** von `Dashboard/pool_control_simple_blocks.yaml`
5. **Einfügen** und **Speichern**
6. **FERTIG!** 🎉

---

### **Option 2: Ultimate Dashboard** ← FÜR POWER-USER

**Datei:** `pool_control_ultimate.yaml`

**Schöne, moderne Oberfläche mit Mushroom Cards!**

#### Was du zusätzlich bekommst:

- 🎨 Farbige, animierte Icons
- 📊 Slider zum einfachen Verstellen
- 💡 Farbcodierte Warnungen (rot = Problem, grün = OK)
- 🔄 Responsive Design

#### Benötigte Custom Cards:

1. **HACS** installieren (falls noch nicht): https://hacs.xyz/docs/use/download/download/
2. **HACS** → **Frontend** → Suche nach:
   - **Mushroom**
   - **Slider Entity Row**
   - **Card Mod**
3. Jeweils installieren und **Home Assistant neu starten**
4. Dashboard-Code aus `pool_control_ultimate.yaml` einfügen

---

## 📱 Wie sieht das auf dem Handy aus?

### Mobile Ansicht:

- Scrollbar mit allen Geräte-Blöcken
- Jeder Block klappbar
- Touch-optimierte Slider
- Große, klickbare Buttons

**Tipp:** Aktiviere in der Home Assistant App:
- **Einstellungen** → **Companion App** → **Kompakte Ansicht**

---

## 🎯 Was kann ich alles einstellen?

### Pro Gerät siehst du:

#### 🏊 Filterpumpe
- ✅ **Status** (Frostschutz, Auto Aktiv, Ein, Aus)
- ✅ **Modus** (Auto/Ein/Aus)
- ✅ **Geschwindigkeit** (1=ECO, 2=Normal, 3=Boost)
- ✅ **Laufzeit** (heute)

#### 🔥 Heizung & ☀️ Solar
- ✅ **Status** (Auto, Ein, Aus)
- ✅ **Modus** (Auto/Ein/Aus)
- ✅ **Zieltemperatur** (einstellbar)
- ✅ **Aktuelle Temperatur**
- ✅ **Laufzeit**

#### 💧 pH Steuerung
- ✅ **pH aktuell** (live Messwert)
- ✅ **pH Sollwert** (einstellbar)
- ✅ **pH- Modus** (Auto/Ein/Aus)
- ✅ **pH- Kanister Volumen** (einstellbar in ml)
- ✅ **pH- Reichweite** (berechnet)
- ✅ **pH- Laufzeit**
- ✅ (Gleiche für pH+)

#### 🟢 Chlor Steuerung
- ✅ **Chlor aktuell** (live Messwert)
- ✅ **Chlor Sollwert** (einstellbar)
- ✅ **Redox aktuell** (live Messwert)
- ✅ **Redox Sollwert** (einstellbar)
- ✅ **Chlor Modus** (Auto/Ein/Aus)
- ✅ **Kanister Volumen** (einstellbar)
- ✅ **Reichweite**
- ✅ **Laufzeit**

---

## 🔧 Anpassungen

### Entity-IDs prüfen

Falls eine Entity nicht angezeigt wird:

1. **Entwicklerwerkzeuge** → **Zustände**
2. Suche nach "violet"
3. Finde die korrekte Entity-ID
4. Ersetze im Dashboard-YAML:
   ```yaml
   entity: sensor.violet_pool_controller_ALTE_ID
   # Ändern zu:
   entity: sensor.violet_pool_controller_NEUE_ID
   ```

### Geräte entfernen

Du hast kein Solar? Einfach den kompletten Block löschen:

```yaml
# Lösche diesen kompletten Abschnitt:
- type: entities
  title: ☀️ Solar
  entities:
    # ... alles bis zum nächsten "- type: entities"
```

### Geräte hinzufügen

Kopiere einen bestehenden Block und passe an:

```yaml
- type: entities
  title: 🌊 Mein Neues Gerät
  show_header_toggle: false
  state_color: true
  entities:
    - entity: sensor.mein_neuer_sensor
      name: Mein Wert
      icon: mdi:water
```

---

## 💡 Profi-Tipps

### 1. Dashboard als Favorit

Nach dem Erstellen:
1. Dashboard öffnen
2. Rechts oben **⋮** → **An Sidebar anheften**
3. Jetzt immer in der Seitenleiste sichtbar!

### 2. Mehrere Tabs

Erstelle verschiedene Ansichten:
- **Tab 1:** Schnellzugriff (Pumpe, Temperatur)
- **Tab 2:** Chemie (pH, Chlor)
- **Tab 3:** Statistiken

### 3. Benachrichtigungen

Füge Automationen hinzu:

```yaml
automation:
  - alias: "Pool - Chlor zu niedrig"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_chlorgehalt
        below: 0.3
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ Chlor zu niedrig! Aktuell: {{ states('sensor.violet_pool_controller_chlorgehalt') }} mg/l"
```

---

## ❓ Häufige Fragen

### "Entity not available" Fehler?

**Ursache:** Das Gerät/Feature ist nicht aktiviert oder die Entity-ID stimmt nicht.

**Lösung:**
1. **Einstellungen** → **Geräte & Dienste** → **Violet Pool Controller**
2. Klicke auf **Konfigurieren**
3. Aktiviere die gewünschten Features
4. Home Assistant **neu laden**

### Werte werden nicht angezeigt?

**Ursache:** Polling-Intervall, Verbindungsproblem

**Lösung:**
1. Warte 10-30 Sekunden (Standard Polling)
2. Prüfe **Geräte** → **Violet Pool Controller** → Verbindung OK?
3. **Logs prüfen:** Einstellungen → System → Logs

### "Unknown custom element" Fehler?

**Ursache:** Du nutzt Ultimate Dashboard ohne Custom Cards.

**Lösung:**
- **Entweder:** Custom Cards installieren (siehe oben)
- **Oder:** Nutze Simple Blocks stattdessen

---

## 🎨 Screenshots

_(Sobald du das Dashboard erstellt hast, kannst du hier Screenshots einfügen!)_

---

## 🚀 Los geht's!

1. **Wähle ein Dashboard:**
   - Anfänger: `pool_control_simple_blocks.yaml`
   - Power-User: `pool_control_ultimate.yaml`

2. **Code kopieren & einfügen**

3. **Entity-IDs anpassen** (falls nötig)

4. **Genießen!** 🏊‍♂️

---

**Viel Spaß mit deinem neuen Pool Control Dashboard!**

Bei Fragen: https://github.com/xerolux/violet-hass/issues
