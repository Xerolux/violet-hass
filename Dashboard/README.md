# 📊 Violet Pool Controller - Dashboard-Vorlagen

Dieses Verzeichnis enthält vorgefertigte Dashboard-Konfigurationen für eine intuitive und übersichtliche Steuerung Ihres Violet Pool Controllers in Home Assistant.

## 📁 Verfügbare Dashboards

### 1. `pool_control_card.yaml` - Vollständige Steuerung
**Empfohlen für:** Desktop, Tablets, Haupt-Dashboard

**Features:**
- ✅ Vollständige ON/OFF/AUTO Steuerung für Pumpe, Heizung, Solar
- ✅ Geschwindigkeitssteuerung für die Pumpe
- ✅ Temperatur-Sollwerte und -Anzeige
- ✅ pH- und Chlor-Kontrolle mit Dosierungssteuerung
- ✅ Temperatur-Gauges für Becken, Solar, Außentemperatur
- ✅ 24h-History-Graph für Wasserchemie
- ✅ Erweiterte Steuerung (Licht, PV-Überschuss, Abdeckung)
- ✅ System-Status und Verbindungsüberwachung

### 2. `pool_control_compact.yaml` - Kompakte Ansicht
**Empfohlen für:** Mobile Geräte, Schnellzugriff, Übersichtsseiten

**Features:**
- ✅ Essenzielle Steuerungselemente
- ✅ Wasserqualität auf einen Blick
- ✅ Verbindungsstatus
- ✅ Optimiert für kleine Bildschirme

## 🚀 Installation

### Methode 1: Manuelles Kopieren (Empfohlen)

1. **Dashboard öffnen**
   - Öffnen Sie Ihr Home Assistant Dashboard
   - Klicken Sie auf die drei Punkte (⋮) oben rechts
   - Wählen Sie "Bearbeiten"

2. **Neue Karte hinzufügen**
   - Klicken Sie auf "+ Karte hinzufügen"
   - Scrollen Sie nach unten und wählen Sie "Manuell" oder klicken Sie auf "Code-Editor anzeigen"

3. **Konfiguration einfügen**
   - Öffnen Sie die gewünschte YAML-Datei (`pool_control_card.yaml` oder `pool_control_compact.yaml`)
   - Kopieren Sie den gesamten Inhalt
   - Fügen Sie ihn in den Code-Editor ein

4. **Entity-IDs anpassen**
   - Ersetzen Sie `violet_pool_controller` durch Ihren tatsächlichen Entity-ID-Prefix
   - Dies ist besonders wichtig, wenn Sie:
     - Mehrere Pool-Controller haben
     - Einen anderen Namen während der Installation vergeben haben
     - Beispiel: `pool1_controller` statt `violet_pool_controller`

5. **Speichern**
   - Klicken Sie auf "Speichern"
   - Beenden Sie den Bearbeitungsmodus

### Methode 2: YAML-Dashboard (Für Fortgeschrittene)

Wenn Sie ein YAML-basiertes Dashboard verwenden:

1. Öffnen Sie Ihre `ui-lovelace.yaml` oder die entsprechende Dashboard-Datei
2. Fügen Sie die Karten-Konfiguration unter `views` → `cards` hinzu
3. Passen Sie die Entity-IDs an
4. Speichern und neu laden

## 🎨 Anpassung

### Entity-IDs herausfinden

Wenn Sie nicht sicher sind, welche Entity-IDs Sie verwenden sollen:

1. Gehen Sie zu **Entwicklerwerkzeuge** → **Zustände**
2. Suchen Sie nach `violet` oder `pool`
3. Notieren Sie die vollständigen Entity-IDs (z.B. `select.violet_pool_controller_pump_mode`)
4. Verwenden Sie diese IDs in der Dashboard-Konfiguration

### Icons anpassen

Sie können die Icons beliebig ändern. Suchen Sie nach verfügbaren Icons auf:
- [Material Design Icons](https://pictogrammers.com/library/mdi/)

Beispiel:
```yaml
- entity: select.violet_pool_controller_pump_mode
  name: Pumpe
  icon: mdi:pump  # ← Hier können Sie das Icon ändern
```

### Farben und Schwellwerte (Gauges)

Die Gauge-Karten verwenden Farbschwellwerte. Passen Sie diese an Ihre Präferenzen an:

```yaml
severity:
  green: 24  # Ab 24°C grün
  yellow: 20  # 20-24°C gelb
  red: 10     # Unter 20°C rot
```

## 🔧 Fehlerbehebung

### "Entity nicht gefunden" Fehler

**Problem:** Eine oder mehrere Entities werden nicht gefunden.

**Lösung:**
1. Überprüfen Sie, ob das entsprechende Feature aktiviert ist:
   - Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
   - Klicken Sie auf "Violet Pool Controller"
   - Wählen Sie "Konfigurieren"
   - Aktivieren Sie die benötigten Features
2. Prüfen Sie die Entity-IDs wie oben beschrieben
3. Entfernen Sie Entities, die Sie nicht benötigen, aus der Konfiguration

### Karten werden nicht korrekt angezeigt

**Problem:** Karten sind zu groß/klein oder unübersichtlich.

**Lösung:**
1. Verwenden Sie `pool_control_compact.yaml` für mobile Geräte
2. Verwenden Sie `pool_control_card.yaml` für Desktop/Tablet
3. Passen Sie die `hours_to_show` im History-Graph an (Standard: 24h)

### Entities fehlen

**Problem:** Nicht alle Sensoren/Steuerungen werden angezeigt.

**Lösung:**
1. Stellen Sie sicher, dass die Features in der Integration aktiviert sind
2. Warten Sie auf den nächsten Update-Zyklus (Standard: alle 10 Sekunden)
3. Prüfen Sie die Logs: **Einstellungen** → **System** → **Protokolle**

## 📱 Mobile Optimierung

Für die beste mobile Erfahrung:

1. Verwenden Sie `pool_control_compact.yaml`
2. Erstellen Sie ein separates Dashboard speziell für mobile Geräte:
   - Gehen Sie zu **Einstellungen** → **Dashboards**
   - Klicken Sie auf "+ Dashboard hinzufügen"
   - Wählen Sie "Mobil" als Namen
   - Fügen Sie nur die kompakte Karte hinzu
3. Aktivieren Sie "Für mobile App optimieren" in den Dashboard-Einstellungen

## 🎯 Erweiterte Funktionen

### Automationen verknüpfen

Sie können die Dashboard-Elemente mit Automationen kombinieren:

```yaml
# Beispiel: Benachrichtigung bei niedrigem pH-Wert
automation:
  - alias: "Pool: pH-Wert zu niedrig"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_controller_ph_value
        below: 7.0
    action:
      - service: notify.mobile_app
        data:
          message: "Pool pH-Wert zu niedrig: {{ states('sensor.violet_pool_controller_ph_value') }}"
```

### Bedingte Karten

Zeigen Sie Karten nur an, wenn bestimmte Bedingungen erfüllt sind:

```yaml
type: conditional
conditions:
  - entity: select.violet_pool_controller_pump_mode
    state: "on"
card:
  type: entities
  entities:
    - entity: sensor.violet_pool_controller_pump_runtime
      name: Laufzeit seit Start
```

## 💡 Tipps

1. **Gruppierung:** Die Entities sind automatisch nach Funktionen gruppiert (Steuerung, Wasserqualität, System)
2. **Entity-Categories:** Konfigurationselemente (Modi, Sollwerte) sind als "CONFIG" kategorisiert
3. **State-Colors:** `state_color: true` färbt Entities basierend auf ihrem Zustand
4. **Updates:** Die Dashboard-Vorlagen werden mit Updates der Integration aktualisiert

## 🆘 Support

Bei Problemen:
1. Überprüfen Sie die [Integration-Dokumentation](../README.md)
2. Erstellen Sie ein [GitHub Issue](https://github.com/Xerolux/violet-hass/issues)
3. Teilen Sie Ihre Dashboard-Konfiguration und Fehlerprotokolle

## 📝 Lizenz

Diese Dashboard-Vorlagen sind Teil der Violet Pool Controller Integration und stehen unter der gleichen Lizenz.
