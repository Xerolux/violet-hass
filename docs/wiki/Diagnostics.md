# Diagnosedaten – Diagnostics

> Mit dem eingebauten Diagnostics-Feature kannst du mit einem Klick alle relevanten Informationen über deinen Violet Pool Controller als JSON-Datei herunterladen – ideal für Bug-Reports und Troubleshooting.

---

## Was sind Diagnosedaten?

Home Assistant bietet für Integrationen eine eingebaute Diagnostics-Funktion. Beim Klick auf **„Diagnosedaten herunterladen"** wird eine JSON-Datei erstellt, die alle wichtigen Informationen zum aktuellen Zustand der Integration enthält – ohne sensible Daten wie Passwörter.

---

## Diagnosedaten herunterladen

1. Gehe zu **Einstellungen → Geräte & Dienste**
2. Klicke auf **Violet Pool Controller**
3. Wähle dein Gerät aus
4. Klicke auf **„Diagnosedaten herunterladen"** (⬇️)
5. Eine JSON-Datei wird gespeichert

> Die Datei kann direkt als Anhang an ein [GitHub Issue](https://github.com/Xerolux/violet-hass/issues) angehängt werden.

---

## Inhalt der Diagnosedaten

Die heruntergeladene JSON-Datei ist in folgende Sektionen aufgeteilt:

### `integration`

Basisinformationen zur Integration:

```json
"integration": {
  "version": "1.0.3-beta.1",
  "domain": "violet_pool_controller"
}
```

---

### `config_entry`

Alle Konfigurationseinstellungen. **Passwörter und Benutzernamen werden automatisch geschwärzt (`**REDACTED**`).**

```json
"config_entry": {
  "title": "Violet Pool Controller • 50.0m³",
  "entry_id": "abc123...",
  "data": {
    "host": "192.168.1.100",
    "polling_interval": 10,
    "timeout_duration": 10,
    "retry_attempts": 3,
    "use_ssl": false,
    "verify_ssl": true,
    "device_id": 1,
    "device_name": "Violet Pool Controller",
    "controller_name": "Hauptpool",
    "active_features": ["pump", "heater", "solar", "dosing_ph"],
    "password": "**REDACTED**"
  },
  "options": {}
}
```

---

### `device`

Aktueller Status des Controllers:

```json
"device": {
  "name": "Violet Pool Controller",
  "controller_name": "Hauptpool",
  "firmware": "1.1.9",
  "device_id": 1,
  "api_url": "192.168.1.100",
  "use_ssl": false,
  "available": true,
  "consecutive_failures": 0,
  "last_error": null
}
```

| Feld | Bedeutung |
|------|-----------|
| `available` | `true` = Controller erreichbar |
| `consecutive_failures` | Anzahl aufeinanderfolgender Verbindungsfehler (ab 5 wird der Controller als nicht verfügbar markiert) |
| `last_error` | Letzter Fehlertext (null = kein Fehler) |
| `firmware` | Firmware-Version des Controllers |

---

### `connection`

Verbindungsmetriken und Gesundheitsstatus:

```json
"connection": {
  "system_health_pct": 98.5,
  "last_latency_ms": 207.3,
  "average_latency_ms": 195.1,
  "total_api_requests": 432,
  "api_request_rate_per_min": 6.0,
  "seconds_since_last_update": 4.2,
  "last_update_success": true
}
```

| Feld | Bedeutung |
|------|-----------|
| `system_health_pct` | Gesundheitsscore 0–100 % |
| `last_latency_ms` | Antwortzeit des letzten API-Calls in ms |
| `average_latency_ms` | Durchschnitt der letzten 60 Messungen |
| `total_api_requests` | Gesamtanzahl API-Requests seit HA-Start |
| `api_request_rate_per_min` | Aktuelle Request-Rate pro Minute |
| `seconds_since_last_update` | Sekunden seit dem letzten erfolgreichen Update |
| `last_update_success` | `true` = letztes Update erfolgreich |

---

### `current_data`

Snapshot aller aktuellen Messwerte vom Controller (z. B. Temperaturen, pH, ORP, Pumpenstatus):

```json
"current_data": {
  "onewire1_value": 27.3,
  "onewire2_value": 24.1,
  "pH_value": 7.25,
  "orp_value": 685,
  "PUMP": 1,
  "HEATER": 0,
  "FW": "1.1.9",
  ...
}
```

> Der Inhalt hängt von deinem Controller und den aktivierten Features ab. Alle verfügbaren Sensoren werden hier aufgelistet.

---

### `poll_statistics`

Statistiken über die bisherigen Datenabfragen:

```json
"poll_statistics": {
  "total_polls": 432,
  "first_poll": "2026-03-02T05:32:50",
  "last_poll": "2026-03-02T06:05:10",
  "avg_data_points": 403.0
}
```

| Feld | Bedeutung |
|------|-----------|
| `total_polls` | Gesamtanzahl abgeschlossener Polls seit Start |
| `first_poll` | Zeitstempel des ersten Polls |
| `last_poll` | Zeitstempel des letzten Polls |
| `avg_data_points` | Durchschnittliche Anzahl empfangener Datenpunkte pro Poll |

---

## Datenschutz & Sicherheit

Die Diagnosedaten werden **nur lokal erzeugt** und nur dann weitergegeben, wenn du die Datei manuell hochlädst. Folgende Felder werden automatisch geschwärzt:

| Feld | Behandlung |
|------|-----------|
| `password` | `**REDACTED**` |
| `username` | `**REDACTED**` |
| Alle anderen Felder | Klartext |

> Die IP-Adresse des Controllers (`host`) ist in den Diagnosedaten sichtbar. Falls du sie nicht teilen möchtest, ersetze sie manuell im JSON-Editor, bevor du die Datei hochlädst.

---

## Diagnosedaten für einen Bug-Report nutzen

1. Diagnosedaten herunterladen (siehe oben)
2. Datei ggf. in einem Texteditor öffnen und IP anonymisieren
3. [Neues Issue erstellen](https://github.com/Xerolux/violet-hass/issues/new/choose)
4. Fehlerbeschreibung, HA-Version und Integrations-Version angeben
5. JSON-Datei als Anhang hinzufügen

---

## Verwandte Seiten

- [Troubleshooting](Troubleshooting) – Häufige Probleme & Lösungen
- [Erweiterte Protokollierung](Erweiterte-Protokollierung) – Debug-Logs aktivieren
- [Fehler-Codes](Error-Codes) – Controller-Fehlercodes erklärt
- [FAQ](FAQ) – Häufige Fragen
