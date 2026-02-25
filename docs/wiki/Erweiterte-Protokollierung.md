# Erweiterte Protokollierung & Diagnose-Tools

Diese Wiki-Seite beschreibt die leistungsstarken Diagnose-Features der Violet Pool Controller Home Assistant Integration für Fehlersuche und Performance-Analyse.

## Funktionsübersicht

### 1. 🔍 Diagnose-Protokollierung (Extended Logging)

Wenn aktiviert, protokolliert das System detaillierte Informationen zu jedem Update-Zyklus:

| Information | Beschreibung |
|---|---|
| **Update-Zähler** | Nummer des aktuellen Update-Zyklus |
| **Anzahl Keys** | Wie viele Werte vom Controller geholt wurden |
| **Abrufdauer** | Wie lange die API-Abfrage gedauert hat (in Millisekunden) |
| **Geänderte Keys** | Welche Werte sich seit dem letzten Update geändert haben |
| **Verbindungsmetriken** | Signalstärke, Latenz und Verbindungsinformationen |
| **Beispieldaten** | Aktuelle Messwerte (Temperatur, pH-Wert, etc.) |

Diese detaillierten Logs helfen beim Debugging von Problemen und bei der Performance-Analyse.

**Beispiel-Ausgabe:**
```
[2025-02-24 12:30:45] Update #127 - 42 keys fetched in 245ms
Changed keys: temperature_pool, ph_value, heater_status
Connection: Latency 52ms, Signal Quality: 92%
Sample data: Pool Temp: 24.5°C, pH: 7.2, ORP: 650mV
```

### 2. ⏱️ Force Update (Erzwungene Updates)

Diese Funktion steuert, wann die Entitäten ihren `last_updated` Zeitstempel aktualisieren:

| Einstellung | Verhalten | Verwendungsfall |
|---|---|---|
| **Deaktiviert** ✓ Standard | Zeitstempel nur bei Wertänderungen | Normale Nutzung |
| **Aktiviert** | Zeitstempel bei jedem Zyklus | Verifikation der Verbindung |

**Wann ist es sinnvoll?**
- Überprüfung, dass der Controller aktiv ist und Daten sendet
- Verifizierung, dass die Integration regelmäßig Daten abruft
- Bestätigung, dass Automatisierungen die aktuellen Werte verwenden

### 3 📊 Log-Export-Service

Mit diesem Service können Sie zwischen 10 und 1.000 aktuelle Log-Zeilen exportieren und als Textdatei speichern.

**Export-Format:**
- **Dateiname:** `violet_diagnostic_YYYYMMDD_HHMMSS.txt`
- **Speicherort:** `/config/` Verzeichnis
- **Typische Größe:** 12–157 KB
- **Optionen:** Timestamps und Systeminfos

## 🚀 Schnellstart

### Aktivierung über die Home Assistant UI

1. Öffnen Sie **Einstellungen** → **Geräte & Services**
2. Suchen Sie nach **Violet Pool Controller**
3. Klicken Sie auf **Konfigurieren**
4. Aktivieren Sie:
   - ☑️ **Extended Logging** (Erweiterte Protokollierung)
   - ☑️ **Force Update** (optional)

### Log exportieren

1. Öffnen Sie **Entwickler-Tools** → **Services**
2. Wählen Sie Service: `violet_pool_controller.log_export`
3. Geben Sie ein:
   - `line_count: 200` (Anzahl der zu exportierenden Zeilen)
   - `include_timestamp: true` (mit Zeitstempel)
   - `include_system_info: true` (mit System-Infos)
4. Klicken Sie auf **Aufrufen**
5. Finden Sie die Datei im Verzeichnis `/config/`

### YAML-Beispiel

```yaml
# In einer Automatisierung oder einem Skript:
service: violet_pool_controller.log_export
data:
  line_count: 500
  include_timestamp: true
  include_system_info: true
```

## 🛠️ Verwendungsszenarien

### Szenario 1: Unzureichend reagierende Sensoren

**Problem:** Ein Sensor aktualisiert sich nicht regelmäßig.

**Lösung:**
1. Aktivieren Sie **Extended Logging**
2. Warten Sie 2–3 Minuten
3. Exportieren Sie 200 Log-Zeilen
4. Prüfen Sie, ob der Sensor in den Logs auftaucht und sich ändert

### Szenario 2: Langsame API-Abfragen

**Problem:** Die Integration antwortet langsam.

**Lösung:**
1. Aktivieren Sie **Extended Logging**
2. Notieren Sie die `Abrufdauer` in mehreren Log-Einträgen
3. Wenn Werte > 1000ms:
   - Überprüfen Sie die Netzwerk-Verbindung
   - Reduzieren Sie Scan-Intervalle in anderen Integrationen
   - Kontaktieren Sie Support mit Log-Export

### Szenario 3: Verbindungsprobleme

**Problem:** "Verbindung zum Controller verloren"-Fehlermeldungen.

**Lösung:**
1. Aktivieren Sie beide: **Extended Logging** + **Force Update**
2. Sammeln Sie 3–5 Minuten Logs
3. Exportieren Sie und prüfen Sie auf Verbindungsabbrüche
4. Teilen Sie die Diagnostik mit Support

### Szenario 4: Automatisierungen arbeiten nicht

**Problem:** Eine Automatisierung triggert nicht, obwohl sich der Wert ändert.

**Lösung:**
1. Aktivieren Sie **Extended Logging**
2. Rufen Sie die Aktion manuell am Controller aus
3. Prüfen Sie die Logs auf `Changed keys`
4. Vergleichen Sie mit Ihrer Automatisierungs-Bedingung

## ⚙️ Best Practices

### ✓ Do's (Was Sie tun sollten)

- ✅ **Deaktivieren Sie Extended Logging nach dem Debugging** – Dies reduziert Log-Dateigröße und CPU-Nutzung
- ✅ **Sammeln Sie gezielt 2–3 Minuten Logs** beim Auftreten eines Problems
- ✅ **Exportieren Sie Logs statt sie ständig zu protokollieren**
- ✅ **Nutzen Sie `line_count: 100–500`** für aussagekräftige Exports ohne Überfluss
- ✅ **Löschen Sie alte Export-Dateien** aus `/config/` regelmäßig

### ✗ Don'ts (Was Sie vermeiden sollten)

- ❌ **Lassen Sie Extended Logging dauerhaft aktiviert** – Verschleißt die Log-Dateien unnötig
- ❌ **Exportieren Sie 10.000+ Zeilen auf einmal** – Zu große Dateien, schwer zu analysieren
- ❌ **Ignorieren Sie hohe Abrufdauern** – Dies deutet auf Netzwerk- oder Hardware-Probleme hin
- ❌ **Aktivieren Sie Force Update ohne Grund** – Verschleißt den Speicher unnötig

## 📋 Schritt-für-Schritt Fehlerbehebung

### Debug-Workflow

```
1. Problem beobachten (z.B. Sensor antwortet nicht)
        ↓
2. Extended Logging AKTIVIEREN
        ↓
3. Problem reproduzieren (2–3 Minuten warten)
        ↓
4. Log-Export durchführen
        ↓
5. Extended Logging DEAKTIVIEREN ← Wichtig!
        ↓
6. Export-Datei analysieren
        ↓
7. Lösung implementieren oder Support kontaktieren
```

## 🔧 Erweiterte Konfiguration

### Automatische Log-Erfassung bei Fehlern

```yaml
automation:
  - alias: "Violet Fehler - Logs exportieren"
    trigger:
      platform: state
      entity_id: binary_sensor.violet_pool_controller_connection
      to: "off"
    action:
      service: violet_pool_controller.log_export
      data:
        line_count: 500
        include_system_info: true
```

### Regelmäßige Diagnose-Snapshots

```yaml
automation:
  - alias: "Täglich Diagnose-Snapshot"
    trigger:
      platform: time
      at: "01:00:00"
    action:
      service: violet_pool_controller.log_export
      data:
        line_count: 200
```

## ❓ Häufig gestellte Fragen

**F: Wirkt sich Extended Logging auf die Performance aus?**
> A: Ja, geringfügig. Die CPU-Nutzung steigt um ~5–10%. Deshalb sollte es nur beim Debugging aktiv sein.

**F: Wie lange sollte ich Extended Logging aktiviert lassen?**
> A: Maximal 10–15 Minuten. Danach sollten genug Daten für eine Analyse vorhanden sein.

**F: Wo genau werden Log-Dateien gespeichert?**
> A: Im `/config/` Verzeichnis Ihrer Home Assistant Installation. Via SSH: `ls -la /config/ | grep violet_diagnostic`

**F: Kann ich die Logs automatisch löschen?**
> A: Ja, mit einem Automation-Skript oder manuell. Alte Dateien: `rm /config/violet_diagnostic_*.txt`

**F: Was ist der Unterschied zwischen Extended Logging und Home Assistant Logs?**
> A: Extended Logging zeigt Controller-spezifische Metriken. HA-Logs zeigen Integrations-Fehler. Beide sind hilfreich!

## 📞 Support & Weitere Ressourcen

- **GitHub Issues:** [Violet Pool Controller Issues](https://github.com/Xerolux/violet-hass/issues)
- **Home Assistant Docs:** [Logging Documentation](https://www.home-assistant.io/docs/logging/)
- **Hauptdokumentation:** [[Home]] oder [README.md](https://github.com/Xerolux/violet-hass/blob/main/README.md)

---

**Tipp:** Speichern Sie aussagekräftige Log-Exports bevor Sie Support kontaktieren – sie helfen bei der schnelleren Problemlösung! 🚀
