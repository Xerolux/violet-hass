> 🇩🇪 **Deutsch** | 🇬🇧 **[English](README)**

---

# 🏊 Violet Pool Controller — Wiki-Index

Willkommen zur Dokumentation der Violet Pool Controller Integration für Home
Assistant. Jede Seite gibt es auf Englisch und auf Deutsch; die Links unten
zeigen auf die deutsche Fassung, und jede Seite verlinkt oben ihr englisches
Gegenstück.

---

## 📚 Alle Seiten

### Erste Schritte

| Seite | Inhalt |
|---|---|
| [Startseite](Home.de) | Überblick, Funktionsumfang, unterstützte Hardware |
| [Installation & Einrichtung](Installation-and-Setup.de) | Schritt für Schritt über HACS oder manuell |
| [Konfiguration](Configuration.de) | Config-Flow, Optionen, Funktionsauswahl |
| [Mehrere Controller](Multi-Controller.de) | Betrieb mit mehr als einem Controller |

### Entitäten & Geräte

| Seite | Inhalt |
|---|---|
| [Entitäten](Entities.de) | Alle Entitäten, die die Integration anlegt |
| [Sensoren](Sensors.de) | Temperaturen, Wasserchemie, Analogeingänge, Diagnose |
| [Schalter](Switches.de) | Pumpe, Heizung, Solar, Dosierung, Relais |
| [Klima](Climate.de) | Thermostate für Heizung und Solar |
| [Gerätezustände](Device-States.de) | Was die Zustände 0-6 bedeuten |
| [Dashboards](Dashboards.de) | Dashboard- und Pool-Karten-Beispiele |

### Automatisierung

| Seite | Inhalt |
|---|---|
| [Services](Services.de) | Alle registrierten Services und ihre Felder |
| [Automatisierungen](Automations.de) | Fertige Automatisierungsbeispiele |

### Betrieb & Hilfe

| Seite | Inhalt |
|---|---|
| [Fehlerbehebung](Troubleshooting.de) | Symptome, Ursachen, Lösungen |
| [Diagnosedaten](Diagnostics.de) | Der Diagnose-Download, Feld für Feld |
| [Erweiterte Protokollierung](Erweiterte-Protokollierung.de) | Debug-Logging und `export_diagnostic_logs` |
| [Fehlercodes](Error-Codes.de) | Fehlercodes des Controllers und ihre Bedeutung |
| [Sicherheit](Security.de) | SSL, Rate Limiting, das Sicherheitsmodell |
| [FAQ](FAQ.de) | Häufige Fragen |

### Entwicklung

| Seite | Inhalt |
|---|---|
| [API-Paket](API-Package.de) | Der eigenständige Client `violet-poolController-api` |
| [API-Referenz](API-Reference.de) | Endpunkte und Payloads des Controllers |
| [Tests](Testing.de) | Testsuite ausführen und erweitern |
| [Icon-Referenz](Icon-Reference.de) | Icons der Entitäten |
| [Mitwirken](Contributing.de) | Wie man beiträgt |
| [Changelog](Changelog.de) | Wo der Changelog tatsächlich liegt |

---

## ⭐ Schnellzugriff

| Situation | Seite |
|---|---|
| Neu hier | [Installation & Einrichtung](Installation-and-Setup.de) |
| Zustände unklar | [Gerätezustände](Device-States.de) |
| Automatisieren | [Services](Services.de) |
| Etwas funktioniert nicht | [Fehlerbehebung](Troubleshooting.de) |
| Allgemeine Fragen | [FAQ](FAQ.de) |
| Fehler gefunden | [GitHub Issues](https://github.com/Xerolux/violet-hass/issues) |

---

## 🔄 Umfang & Aktualität

- Diese Wiki dokumentiert Version **2.7.0** der Integration.
- Die Seiten werden vom Workflow `docs.yml` aus `docs/wiki/` im Repository
  synchronisiert — bearbeite sie dort, nicht in der GitHub-Wiki-Oberfläche,
  sonst überschreibt die nächste Synchronisation deine Änderung.
- Die englische Seite wird zuerst geschrieben; die `.de.md`-Fassung ist ihre
  Übersetzung.
- Ein „Zuletzt aktualisiert"-Datum steht hier bewusst nicht mehr: es blieb bei
  2026-06-16 stehen, während sich die Wiki weiterentwickelte.

---

**Mit ❤️ für die Home-Assistant- und Pool-Community**
