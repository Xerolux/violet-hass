[![GitHub Release][releases-shield]][releases]
[![Downloads][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![HACS][hacs-badge]][hacs]
[![Maintainer][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymeacoffee-badge]][buymeacoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

# Violet Pool Controller for Home Assistant

Diese benutzerdefinierte Integration ermöglicht es Ihnen, Ihre Poolausrüstung mit dem Violet Pool Controller in Home Assistant zu überwachen und zu steuern. Sie umfasst Sensoren, Binärsensoren, Schalter, Klimasteuerungen und Abdeckungsentitäten, um verschiedene Poolmetriken zu verfolgen und essentielle Operationen durchzuführen.

![Violet Home Assistant Integration][logo]

## Funktionen

- **Sensoren:** Überwachung von Wassertemperatur, pH-Werten, Redox-Potenzial, Chlorwerten, Filterdruck und mehr.
- **Binärsensoren:** Statusverfolgung von Pumpen, Solarsystemen, Heizungen und Systemverbindung.
- **Schalter:** Steuerung von Poolgeräten wie Pumpen, Beleuchtung, Öko-Modus, Dosiersystemen und Rückspülfunktionen.
- **Klimasteuerungen:** Verwaltung der Poolheizung und Solarabsorbertemperatur.
- **Abdeckungssteuerungen:** Bedienung Ihrer Poolabdeckung direkt über Home Assistant.
- **Zahlentitäten:** Festlegen von Zielwerten für pH, Redox und Chlor.

## Inhaltsverzeichnis

- [Screenshots](#screenshots)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Entitäten](#entitäten)
- [Dienste](#dienste)
- [Häufige Probleme und Lösungen](#häufige-probleme-und-lösungen)
- [Support erhalten](#support-erhalten)
- [Diese Integration unterstützen](#diese-integration-unterstützen)
- [Mitwirken](#mitwirken)
- [Über den Violet Pool Controller](#über-den-violet-pool-controller)
- [Änderungsprotokoll](#änderungsprotokoll)
- [Danksagung](#danksagung)

## Screenshots

![Übersicht](https://github.com/xerolux/violet-hass/raw/main/screenshots/overview.png)  
*Übersicht des Violet Pool Controller Dashboards in Home Assistant.*

![Poolmetriken](https://github.com/xerolux/violet-hass/raw/main/screenshots/pool_metrics.png)  
*Detaillierte Ansicht von Poolmetriken wie pH, Chlor und Temperatur.*

![Bedienfeld](https://github.com/xerolux/violet-hass/raw/main/screenshots/control_panel.png)  
*Bedienfeld für Schalter und Klimasteuerungen.*

## Installation

### HACS-Installation (Empfohlen)

1. Öffnen Sie HACS in Ihrer Home Assistant-Oberfläche.
2. Klicken Sie auf die drei Punkte oben rechts und wählen Sie "Benutzerdefinierte Repositories".
3. Fügen Sie `https://github.com/Xerolux/violet-hass.git` als benutzerdefiniertes Repository hinzu.
4. Wählen Sie "Integration" als Kategorie und klicken Sie auf "Hinzufügen".
5. Suchen Sie nach "Violet Pool Controller" in HACS und klicken Sie auf "Download".
6. Starten Sie Home Assistant neu.

### Manuelle Installation (Fortgeschrittene Nutzer)

1. Kopieren Sie den Ordner `violet_pool_controller` aus diesem Repository in das Verzeichnis `custom_components` Ihrer Home Assistant-Instanz.
2. Starten Sie Home Assistant neu.

## Konfiguration

Die Konfiguration erfolgt vollständig über die Home Assistant-Benutzeroberfläche:

1. Gehen Sie zu **Einstellungen > Geräte & Dienste > Integrationen**.
2. Klicken Sie auf "+ Integration hinzufügen".
3. Suchen Sie nach "Violet Pool Controller" und wählen Sie ihn aus.
4. Geben Sie die folgenden Informationen ein:
   - **Host:** IP-Adresse oder Hostname Ihres Violet Pool Controllers (z. B. `192.168.1.100`). *Fügen Sie nicht* `http://` oder `https://` hinzu.
   - **Benutzername:** Lassen Sie das Feld leer, wenn kein Benutzername erforderlich ist.
   - **Passwort:** Lassen Sie das Feld leer, wenn kein Passwort erforderlich ist.
   - **SSL verwenden:** Aktivieren Sie diese Option, wenn Ihr Controller HTTPS nutzt.
   - **Geräte-ID:** Eine eindeutige numerische Kennung (Standard: 1).
   - **Gerätename:** Ein beschreibender Name für Ihren Controller.
   - **Abfrageintervall (Sekunden):** Wie oft Daten abgerufen werden sollen (Standard: 60).
   - **Timeout-Dauer (Sekunden):** Maximale Wartezeit für API-Antworten (Standard: 10).
   - **Wiederholungsversuche:** Anzahl der Wiederholungen bei Fehlern (Standard: 3).
5. Klicken Sie auf "Absenden". Bei Erfolg fahren Sie mit der Pool-Einrichtung fort.
6. Konfigurieren Sie die Pooleinstellungen:
   - **Poolgröße:** Volumen in Kubikmetern.
   - **Pooltyp:** Wählen Sie aus Optionen wie Außenpool, Innenpool usw.
   - **Desinfektionsmethode:** Wählen Sie Ihre Methode (z. B. Chlor, Salz).
7. Wählen Sie die zu aktivierenden Funktionen aus.
8. Klicken Sie auf "Absenden", um die Einrichtung abzuschließen.

## Entitäten

Die Integration erstellt dynamisch Entitäten basierend auf verfügbaren API-Daten und ausgewählten Funktionen:

- **Sensoren:** Wassertemperatur, pH, Redox, Chlor, Filterdruck usw.
- **Binärsensoren:** Pumpenstatus, Solarstatus, Heizungsstatus usw.
- **Schalter:** Pumpe, Beleuchtung, Heizung, Dosierung, Rückspülung, PV-Überschuss usw.
- **Klimageräte:** Heizung und Solarabsorbersteuerung.
- **Abdeckungsentitäten:** Poolabdeckungssteuerung.
- **Zahlentitäten:** Zielwerte für pH, Redox und Chlor.

## Dienste

Die Integration bietet benutzerdefinierte Dienste für erweiterte Steuerungen:

- **`violet_pool_controller.turn_auto`**: Schaltet einen Schalter in den AUTO-Modus.
- **`violet_pool_controller.set_pv_surplus`**: Aktiviert den PV-Überschuss mit Pumpengeschwindigkeit.
- **`violet_pool_controller.manual_dosing`**: Startet manuelle Dosierung.
- **`violet_pool_controller.set_temperature_target`**: Legt die Zieltemperatur fest.
- **`violet_pool_controller.set_ph_target`**: Legt den pH-Zielwert fest.
- **`violet_pool_controller.set_chlorine_target`**: Legt den Chlor-Zielwert fest.
- **`violet_pool_controller.trigger_backwash`**: Startet die Rückspülung.
- **`violet_pool_controller.start_water_analysis`**: Initiiert eine Wasseranalyse.
- **`violet_pool_controller.set_maintenance_mode`**: Aktiviert/Deaktiviert den Wartungsmodus.

Detaillierte Parameter finden Sie in der Integrationsdokumentation.

## Häufige Probleme und Lösungen

### Verbindungsfehler
- Überprüfen Sie IP-Adresse, Benutzername und Passwort.
- Stellen Sie sicher, dass Home Assistant und der Controller im selben Netzwerk sind.
- Prüfen Sie die `use_ssl`-Einstellung.
- Deaktivieren Sie vorübergehend Firewalls, um Blockierungen auszuschließen.
- Erhöhen Sie Timeout oder Wiederholungsversuche in der Konfiguration.

### "Unerwartete Antwortstruktur" oder "Firmware-Version nicht gefunden"
- Aktualisieren Sie die Firmware des Controllers über die PoolDigital-Website.
- Überprüfen Sie die eingegebene IP-Adresse.

### Entitäten werden nicht aktualisiert
- Überprüfen Sie die Home Assistant-Logs auf Fehler.
- Starten Sie Home Assistant neu.
- Stellen Sie sicher, dass das Abfrageintervall nicht zu niedrig ist.
- Verifizieren Sie die Einrichtung des Data Update Coordinators.

### Entitäten werden nicht angezeigt
- Stellen Sie sicher, dass die relevanten Funktionen in den Einstellungen aktiviert sind.
- Prüfen Sie, ob der Controller die Funktionen unterstützt.
- Überprüfen Sie die Logs auf Initialisierungsfehler.

## Support erhalten

Falls Probleme bestehen bleiben:
1. **Logs prüfen:** Suchen Sie nach Fehlern in den Home Assistant-Logs.
2. **README konsultieren:** Überprüfen Sie die Schritte zur Fehlerbehebung.
3. **Problem melden:** Eröffnen Sie ein Issue auf [GitHub][issues] mit Details.
4. **PoolDigital-Forum:** Besuchen Sie das [Forum](http://forum.pooldigital.de/) für Hardware-/Firmware-Fragen.

## Diese Integration unterstützen

Wenn Ihnen diese Integration gefällt, unterstützen Sie ihre Entwicklung:

<a href="https://www.buymeacoffee.com/xerolux" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;"></a>

## Mitwirken

Beiträge sind willkommen:
1. Forken Sie das Repository.
2. Erstellen Sie einen neuen Branch.
3. Nehmen Sie Änderungen vor.
4. Reichen Sie einen Pull Request ein.

Halten Sie sich an den bestehenden Kodierstil und Konventionen.

## Über den Violet Pool Controller

![Violet Pool Controller][pbuy]

VIOLET ist ein intelligentes Poolsteuerungssystem von PoolDigital, das Filtration, Heizung, Beleuchtung und mehr verwaltet. Es bietet Benachrichtigungen, eine Browser-Oberfläche und eine JSON-API für Smart-Home-Integrationen.

- **Shop:** [pooldigital.de](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart)
- **Forum:** [forum.pooldigital.de](http://forum.pooldigital.de/)

## Änderungsprotokoll

Ein detailliertes Änderungsprotokoll wird bei der offiziellen Veröffentlichung erstellt.

## Danksagung

Erstellt mit dem [Integration Blueprint][integration_blueprint] von [@Ludeeus](https://github.com/ludeeus). Dank an die Home Assistant-Community!

---

[integration_blueprint]: https://github.com/ludeeus/integration_blueprint
[buymeacoffee]: https://www.buymeacoffee.com/xerolux
[buymeacoffee-badge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/xerolux/violet-hass.svg?style=for-the-badge
[commits]: https://github.com/xerolux/violet-hass/commits/main
[hacs]: https://hacs.xyz
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[logo]: https://github.com/xerolux/violet-hass/raw/main/logo.png
[picture]: https://github.com/xerolux/violet-hass/raw/main/picture.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/xerolux/violet-hass.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Xerolux%20(@xerolux)-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/xerolux/violet-hass.svg?style=for-the-badge
[releases]: https://github.com/xerolux/violet-hass/releases
[user_profile]: https://github.com/xerolux
[issues]: https://github.com/xerolux/violet-hass/issues
[screens1]: https://github.com/xerolux/violet-hass/raw/main/screenshots/overview.png
[screens2]: https://github.com/xerolux/violet-hass/raw/main/screenshots/screens2.png
[buy]: https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart
[pbuy]: https://github.com/xerolux/violet-hass/raw/main/screenshots/violetbm.jpg
[downloads-shield]: https://img.shields.io/github/downloads/xerolux/violet-hass/latest/total.svg?style=for-the-badge
