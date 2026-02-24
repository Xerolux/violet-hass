# Erweiterte Protokollierung & Diagnose-Tools

Diese Dokumentation beschreibt drei leistungsstarke Diagnose-Features für die Violet Pool Controller Home Assistant Integration.

## Funktionsübersicht

### 1. Diagnose-Protokollierung (Extended Logging)

Wenn aktiviert, protokolliert das System detaillierte Informationen zu jedem Update-Zyklus:

- **Update-Zähler**: Nummer des aktuellen Update-Zyklus
- **Anzahl abgerufener Keys**: Wie viele Werte vom Controller geholt wurden
- **Abrufdauer**: Wie lange die API-Abfrage gedauert hat (in Millisekunden)
- **Geänderte Keys**: Welche Werte sich seit dem letzten Update geändert haben
- **Verbindungsmetriken**: Signalstärke, Latenz und andere Verbindungsinformationen
- **Beispieldaten**: Aktuelle Messwerte (Temperatur, pH-Wert, etc.)

Diese detaillierten Logs helfen beim Debugging von Problemen und bei der Performance-Analyse.

### 2. Force Update (Erzwungene Updates)

Diese Funktion steuert, wann die Entitäten ihren `last_updated` Zeitstempel aktualisieren:

| Einstellung | Verhalten |
|---|---|
| **Deaktiviert** (Standard) | Zeitstempel werden nur aktualisiert, wenn sich der Wert ändert |
| **Aktiviert** | Zeitstempel werden in jedem Zyklus aktualisiert, unabhängig von Wertveränderungen |

**Verwendungsfall**: Hilfreich, um zu verifizieren, dass der Controller aktiv ist und Daten sendet, auch wenn die Messwerte stabil bleiben.

### 3. Log-Export-Service

Mit diesem Service können Sie zwischen 10 und 1.000 aktuelle Log-Zeilen exportieren und als Textdatei im `/config/` Verzeichnis speichern.

**Export-Format**:
- Automatische Benennung: `violet_diagnostic_YYYYMMDD_HHMMSS.txt`
- Optionale Timestamps und Systeminfos in den Logs
- Typische Dateigröße: 12–157 KB (abhängig von Zeilenzahl)

## Verwendungsszenarien

Die erweiterte Protokollierung ist ideal für:

- **Unzureichend reagierende Sensoren**: Überprüfen Sie, ob Werte regelmäßig aktualisiert werden
- **Performance-Analyse**: Messen Sie die Abrufdauer und identifizieren Sie Engpässe
- **Verbindungsüberwachung**: Überprüfen Sie Latenz und Verbindungsstabilität
- **Datensammlung für Support**: Sammeln Sie aussagekräftige Diagnostik-Informationen
- **Fehlersuche bei Automatisierungen**: Verifizieren Sie, dass Automatisierungen die erwarteten Werte auslösen

## Zugriffsmethoden

Die Diagnose-Tools sind auf mehrere Wege erreichbar:

### 1. **Home Assistant UI**
   - Gehen Sie zu **Einstellungen** → **Geräte & Services**
   - Wählen Sie **Violet Pool Controller** aus
   - Öffnen Sie das Konfigurationsmenü
   - Aktivieren/Deaktivieren Sie die gewünschten Optionen

### 2. **Entwickler-Tools**
   - Öffnen Sie **Entwickler-Tools** → **Services**
   - Suchen Sie nach `violet_pool_controller` Services
   - Wählen Sie `log_export` zum Exportieren von Logs

### 3. **YAML-Automatisierung**
   ```yaml
   service: violet_pool_controller.log_export
   data:
     line_count: 100
     include_timestamp: true
     include_system_info: true
   ```

### 4. **Kommandozeile**
   Direkte Calls über die Home Assistant API oder über Skripte möglich.

## Best Practices

### Aktivierung & Deaktivierung

> **Wichtig**: Halten Sie die Diagnose-Protokollierung während des normalen Betriebs **deaktiviert**, um die Log-Dateigröße zu minimieren.

### Schritte zur Fehlersuche

1. **Aktivieren Sie Extended Logging** in der Konfiguration
2. **Sammeln Sie 2–3 Minuten Logs**, während Sie das Problem beobachten
3. **Exportieren Sie die Logs** über den Log-Export-Service
4. **Deaktivieren Sie Extended Logging** wieder
5. **Analysieren Sie die Export-Datei** auf Auffälligkeiten

### Speicherplatz sparen

- Exportieren Sie Logs statt sie ständig protokollieren zu lassen
- Löschen Sie alte Export-Dateien aus `/config/` manuell
- Verwenden Sie `line_count: 100–500` für kleinere Export-Dateien

## Ausgabe-Beispiel

Eine typische Extended-Logging-Ausgabe sieht so aus:

```
[2025-02-24 12:30:45] Update #127 - 42 keys fetched in 245ms
Changed keys: temperature_pool, ph_value
Connection: Latency 52ms, Signal Quality: 92%
Sample data: Pool Temp: 24.5°C, pH: 7.2, ORP: 650mV
```

## Fehlerbehebung

### Problem: Logs werden nicht exportiert
- Überprüfen Sie, dass `/config/` beschreibbar ist
- Stellen Sie sicher, dass genug Speicherplatz vorhanden ist
- Prüfen Sie die Home Assistant Logs auf Fehler

### Problem: Zu viele Logs in der Datei
- Erhöhen Sie nicht die `line_count` ohne Grund
- Deaktivieren Sie Extended Logging zwischen Debug-Sessions
- Nutzen Sie gezielt kleine `line_count` Werte (10–100)

### Problem: Performance-Einbußen
- Reduzieren Sie die Aktualisierungshäufigkeit während des Debuggings
- Deaktivieren Sie Extended Logging nach der Diagnose
- Prüfen Sie, ob andere Integrationen ebenfalls viel protokollieren

## Weitere Ressourcen

- [Home Assistant Logging Dokumentation](https://www.home-assistant.io/docs/logging/)
- [Violet Pool Controller Hauptdokumentation](./README.md)
- [GitHub Issues & Support](https://github.com/Xerolux/violet-hass/issues)
