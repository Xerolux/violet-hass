# Violet Pool Controller für Home Assistant – Beta 7 zum Testen gesucht!

**Version:** 2.0.0-beta.7 (Early Release)
**Datum:** Juni 2026
**GitHub:** https://github.com/xerolux/violet-hass
**Installation via HACS:** Einfach Repository als benutzerdefinierte Integration hinzufügen

---

## Was ist das?

Die **Violet Pool Controller** Integration für Home Assistant verbindet euren Violet-Schwimmbadcontroller direkt mit HA. Ihr bekommt alle Sensoren, Schalter, Temperaturen, Dosierungen und Automatisierungen – alles lokal, kein Cloud-Zwang.

---

## Was ist neu in Beta 7?

### Bugfixes

**Doppelter Gerätename in Entitäts-IDs behoben**
Entities hatten bisher Namen wie `switch.violet_pool_controller_violet_pool_controller_beleuchtung` – also den Gerätenamen doppelt. Das ist jetzt gefixt. Die Integration bereinigt beim Start automatisch alle alten Einträge in der Entity Registry, sodass bestehende Installationen ohne manuellen Eingriff migriert werden.

**Firmware-Update-Erkennung repariert**
Die Funktion "Systemupdate" in HA hat keine verfügbaren Updates mehr angezeigt. Ursache war, dass neue Firmware-Versionen die Schlüssel `SYSTEM_swversion` / `SYSTEM_availableversion` nutzen, ältere dagegen `SW_VERSION` / `SW_UPDATE_AVAILABLE`. Die Integration unterstützt jetzt beide Varianten automatisch mit Fallback.

**SSL-Zertifikatsverifizierung standardmäßig deaktiviert**
Da viele Violet-Controller selbst-signierte Zertifikate oder nur HTTP nutzen, ist SSL-Verify jetzt standardmäßig aus. Kann in den Optionen jederzeit aktiviert werden.

**Cover-Platform API-Kompatibilität**
Poolabdeckungs-Entitäten haben mit neueren API-Versionen nicht mehr korrekt funktioniert. Behoben.

**Dosierungs-Indizes und HTTP-Control-Protokoll**
Falsche Endpunkt-Parameter bei der manuellen Dosierung und beim HTTP-Control wurden korrigiert.

### Neue Sensoren / Features

**Neue Messwerte aus der Firmware**
- Wasserstoffperoxid (H₂O₂) Sensor
- Betriebszeitzähler (Pumpenlaufzeit, Heizbetrieb etc.)
- RS485-Stromversorgung Sensor
- Stoppuhr-Funktion
- Dosierstatistiken (verbrauchte Menge je Chemikalie)

**Firmware-Update direkt aus HA starten**
Der Update-Eintrag unter `Einstellungen → Updates` zeigt jetzt korrekt an, ob eine neue Firmware verfügbar ist. Über den "Installieren"-Button kann das Update direkt gestartet werden – der Controller lädt und installiert eigenständig (~30 Sekunden offline). Die Release Notes (Changelog) werden direkt vom PoolDigital-Server geladen und in HA angezeigt.

**Übersetzungen für neue Sensoren**
Alle neuen Sensoren wurden in 10 Sprachen übersetzt (Deutsch, Englisch, Französisch, Spanisch, Italienisch, Niederländisch, Polnisch, Portugiesisch, Russisch, Chinesisch).

---

## Voraussetzungen

| | |
|---|---|
| Home Assistant | ≥ 2026.5.0 |
| Python | ≥ 3.14.2 |
| Violet Firmware | getestet ab 1.1.x |
| Installation | HACS (empfohlen) oder manuell |

---

## Installation / Update via HACS

1. HACS öffnen → **Integrationen** → drei Punkte oben rechts → **Benutzerdefinierte Repositories**
2. URL eingeben: `https://github.com/xerolux/violet-hass`
3. Kategorie: **Integration**
4. Hinzufügen → dann in HACS nach "Violet Pool Controller" suchen und installieren
5. HA neu starten

Bei einem Update einfach in HACS auf die neue Version klicken und danach neu starten – die Entity-Migration läuft automatisch.

---

## Was wird getestet?

Ich suche Tester die folgendes prüfen können:

- [ ] Update-Anzeige: Wird eine neue Firmware korrekt als verfügbar angezeigt?
- [ ] Update starten: Funktioniert der "Installieren"-Button in HA → Updates?
- [ ] Release Notes: Werden Changelogs im Update-Dialog angezeigt?
- [ ] Entity-Namen: Sind nach dem Update die doppelten Präfixe weg?
- [ ] Neue Sensoren: Tauchen H₂O₂, Laufzeiten, Dosierstatistiken in der Entity-Liste auf (sofern vom Controller geliefert)?
- [ ] Dosierung: Funktioniert die manuelle Dosierung über den Service `violet_pool_controller.smart_dosing`?
- [ ] Cover: Poolabdeckung öffnen/schließen funktioniert?

---

## Bekannte Einschränkungen (Beta)

- Die automatische mDNS-Erkennung (ZeroConf) ist noch nicht von allen Netzwerkkonfigurationen getestet
- Bei sehr alten Firmware-Versionen (< 1.0) können einzelne Sensoren fehlen – das ist kein Fehler der Integration

---

## Feedback / Bugs

Bitte Bugs direkt als GitHub Issue melden:
👉 https://github.com/xerolux/violet-hass/issues

Alternativ hier im Thread oder per PN.

Danke fürs Testen! 🏊
