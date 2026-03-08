# Violet Pool Controller – Konfigurationshandbuch (DE)

Dieses Handbuch führt dich Schritt für Schritt durch die Einrichtung der Violet-Pool-Integration in Home Assistant und erklärt alle sicherheitsrelevanten Aspekte. Bitte lies die Hinweise sorgfältig, bevor du Änderungen an deiner Anlage vornimmst.

## ⚠️ Sicherheit & Haftung

### WICHTIGER HAFTUNGSAUSSCHLUSS

**Die Nutzung dieser Software-Integration erfolgt auf eigene Verantwortung und Gefahr.**

Diese Integration ermöglicht die Fernsteuerung von Poolausrüstung einschließlich Pumpen, Heizungen, Beleuchtung und chemischen Dosieranlagen. Falsche Konfiguration oder Automatisierungsfehler können zu:

- **Sachschäden** (Zerstörung von Pumpen, Heizungen, anderer Ausrüstung)
- **Verletzungen** durch elektrischen Schlag
- **Chemischen Überdosierungen** mit Gesundheitsgefahren
- **Gefährdung von Personen und Tieren** im Poolbereich

führen.

### Deine Verantwortung bei der Nutzung

Du bestätigst mit der Nutzung, dass du:

1. **Sicherheit verstehst** – Alle Schutzmechanismen und Not-Abschalter bekannt sind
2. **Manuelle Kontrolle behältst** – Not-Abschalter jederzeit erreichbar sind
3. **Chemikalien richtig handhabst** – Sicherheitsdatenblätter befolgst (Handschuhe, Schutzbrille, Belüftung)
4. **Hersteller-Dokumentation befolgst** – Die Anleitungen deines Pool-Herstellers beachtest
5. **Gesetze und Normen einhältst** – Lokale Vorschriften (DIN/EN Standards, VDE, Elektro- und Chemikalienrecht)
6. **Regelmäßig überwachst** – Deine Anlage auch bei aktiver Automation persönlich kontrollierst
7. **Backups erstellst** – Regelmäßige Konfigurationssicherungen durchführst

### Keine Gewährleistung

Der Entwickler dieser Integration übernimmt:

- **Keinerlei Gewährleistung** für die Funktionsfähigkeit, Sicherheit oder Vollständigkeit
- **Keine Haftung** für Schäden jeder Art, einschließlich:
  - Sachschäden (Ausrüstung, Gebäude, Umgebung)
  - Personenschäden (Verletzungen, Gesundheitsschäden)
  - Finanzielle Verluste (Reparaturkosten, Folgeschäden)
- **Keine kommerzielle Garantien** – Dies ist Open-Source-Software

### Bei Unsicherheiten

 Konsultiere einen **Fachbetrieb** für:
- Elektroinstallationen
- Chemikalienhandhabung
- Pool-Installation und -Wartung

Durch die Nutzung dieser Integration erklärst du, dass du diesen Haftungsausschluss gelesen, verstanden und akzeptiert hast.

---

## ⚠️ Sicherheit zuerst – Checkliste

- **Eigenverantwortung:** Du übernimmst die vollständige Verantwortung für alle Aktionen, die über die Integration ausgelöst werden.
- **Notfallplan:** Stelle sicher, dass du Pumpen, Dosieranlagen und Abdeckung jederzeit manuell abschalten kannst.
- **Schutzausrüstung:** Beachte die Sicherheitsdatenblätter der verwendeten Chemikalien (Handschuhe, Schutzbrille etc.).
- **Firmware-Stand:** Verwende die aktuelle Controller-Firmware und sichere deine Konfiguration regelmäßig.

## ✅ Voraussetzungen

- Home Assistant **2025.11.1** oder neuer
- Netzwerkzugriff auf den Violet Pool Controller (LAN/WLAN)
- Optional: Benutzername und Passwort, falls Authentifizierung aktiviert ist
- Zugriff auf das Home Assistant Dateisystem, um Backups anzulegen

## 🚀 Schritt-für-Schritt-Konfiguration

1. **Willkommensmenü:** Wähle, ob du direkt starten oder zuerst die Dokumentation lesen möchtest.
2. **Haftungshinweise:** Lies den **vollständigen Haftungsausschluss** sorgfältig. Du musst ausdrücklich bestätigen, dass du die Risiken verstehst und akzeptierst. Dies ist ein rechtlich bindender Haftungsausschluss.
3. **Verbindungsdaten:**
   - Host/IP-Adresse des Controllers
   - Optional Benutzername & Passwort
   - Polling-Intervall (empfohlen 10–60 Sekunden)
   - Timeout und Anzahl der Wiederholungsversuche
4. **Pooldaten:** Lege Volumen, Pool-Typ und Desinfektionsmethode fest. Diese Angaben werden für Automatisierung und Dosierung benötigt.
5. **Feature-Auswahl:** Aktiviere nur die Funktionen, die du wirklich nutzt – so bleibt das System schlank und performant.
6. **Sensor-Auswahl (optional):** Falls dynamische Sensoren erkannt werden, kannst du sie gezielt auswählen.

## 🧠 Funktionsübersicht

| Funktion | Beschreibung |
| --- | --- |
| **Heizungssteuerung** | Optimiert Heizzeiten anhand Soll-Temperaturen und PV-Überschuss. |
| **Solarabsorber** | Nutzt Sonnenenergie mit Priorisierungen und Schutzlogik. |
| **pH-/Chlor-Management** | Automatische Dosierung, inklusive Sicherheitsintervallen. |
| **Abdeckungssteuerung** | Zeit- und wetterabhängige Steuerung der Poolabdeckung. |
| **Rückspül-Automatik** | Startet Rück- und Nachspülen je nach Druck oder Zeitplan. |
| **Digitale Eingänge** | Bindet externe Sensoren oder Schalter für Sonderlogik ein. |
| **LED-Beleuchtung & DMX** | Szenensteuerung, Sequenzen und Partymodus. |

> 💡 **Tipp:** Jede Funktion lässt sich später im Optionsmenü feinjustieren. Dokumentiere Änderungen, damit du sie nachvollziehen kannst.

## 🛠️ Services & Automationen

- **`violet_pool_controller.control_pump`** – Steuerung der Filterpumpe (ECO, Boost, Auto, Zeitsperre).
- **`violet_pool_controller.smart_dosing`** – Dosierung mit Sicherheitsintervallen, inkl. Override.
- **`violet_pool_controller.manage_pv_surplus`** – Bindet PV-Überschuss intelligent ein.
- **`violet_pool_controller.test_output`** – Aktiviert Ausgänge temporär zum Testen; achte auf Sicherheit!

Eine vollständige Referenz findest du in der Datei [`services.yaml`](../../custom_components/violet_pool_controller/services.yaml).

## 🧭 Fehlerbehebung

1. **Keine Verbindung:** Prüfe Firewall, IP-Adresse, SSL-Einstellungen und Anmeldedaten.
2. **Zeitüberschreitung:** Erhöhe Timeout oder verringere das Polling-Intervall nicht unter 10 Sekunden.
3. **API-Fehler:** Stelle sicher, dass der Controller aktuelle Firmware nutzt und die API aktiviert ist.
4. **Dosierung blockiert:** Sicherheitsintervall aktiv? Warte den Countdown ab oder nutze den Override nur in Ausnahmefällen.

## 📦 Backup & Wiederherstellung

- Exportiere regelmäßig deine Home-Assistant-Konfiguration.
- Notiere individuelle Service- und Automations-IDs.
- Bewahre Controller-Backups separat auf (z.B. USB-Stick oder Cloudspeicher).

## 📞 Support & Community

- GitHub-Issues: <https://github.com/xerolux/violet-hass/issues>
- Dokumentation (EN): <https://github.com/xerolux/violet-hass/blob/main/docs/help/configuration-guide.en.md>
- Bitte stelle bei Support-Anfragen Logs, Fehlercodes und eine Beschreibung der letzten Schritte bereit.

Bleib aufmerksam und teste neue Automationen zunächst in kleinen Schritten. Viel Erfolg bei der Automatisierung deines Pools!
