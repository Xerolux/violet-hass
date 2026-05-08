# VIOLET Standalone – Bedienungsanleitung

> **Dosierbaustein mit Ansteuerung durch Raspberry PI 3B / 3B+**  
> Software-Version: 1.1.7 | Stand: 07.2025  
> Hersteller: PoolDigital GmbH & Co. KG | Kapellenstraße 10a | 86441 Zusmarshausen | Tel.: 08291 / 1699-495

---

## Inhaltsverzeichnis

1. [Installationsvoraussetzungen / Planung der Installation](#1-installationsvoraussetzungen--planung-der-installation)
2. [Einleitung](#2-einleitung)
3. [Erstinbetriebnahme / Grundkonfiguration](#3-erstinbetriebnahme--grundkonfiguration)
4. [Dashboard, Statistik, Dosiermengen](#4-dashboard-statistik-dosiermengen)
5. [Allgemeines zu den Dosieroptionen](#5-allgemeines-zu-den-dosieroptionen)
6. [pH Dosierung (Heben/Senken)](#6-ph-dosierung-hebensenken)
7. [Chlor Dosierung (Flüssig-Chlor)](#7-chlor-dosierung-flüssig-chlor)
8. [Elektrolyse-Steuerung](#8-elektrolyse-steuerung)
9. [Flockmittel-Dosierung](#9-flockmittel-dosierung)
10. [Elektroden Kalibrierung](#10-elektroden-kalibrierung)
11. [Regelmäßige Kontrolle aller dosierrelevanten Bauteile](#11-regelmäßige-kontrolle-aller-dosierrelevanten-bauteile)
12. [Außerbetriebnahme der Dosiersteuerung im Winter](#12-außerbetriebnahme-der-dosiersteuerung-im-winter)
13. [Systemeinstellungen](#13-systemeinstellungen)
14. [System Logfiles](#14-system-logfiles)
15. [Werkseinstellungen wiederherstellen](#15-werkseinstellungen-wiederherstellen)
16. [Anbindung an Hausautomationssysteme](#16-anbindung-an-hausautomationssysteme)
17. [Benachrichtigungen per HTTP Request an Fremdsysteme](#17-benachrichtigungen-per-http-request-an-fremdsysteme)
18. [Konformitätserklärung VIOLET](#18-konformitätserklärung-violet)
19. [GPL License Statement](#19-gpl-license-statement)

---

## 1 Installationsvoraussetzungen / Planung der Installation

Elektronische Bauteile und elektrochemische Sensoren (pH / Redox / Chlor) sind empfindlich gegenüber elektromagnetischen Störungen (EMPs) und Hochfrequenzfeldern. Leistungsintensive Verbraucher wie Filterpumpen, Wärmepumpen oder Gegenstromanlagen erzeugen starke elektromagnetische Felder.

> **Wichtig:** Sensorkabel (pH, Redox, Chlor) und Steuerleitungen niemals parallel neben 230 V / 400 V führenden Kabeln verlegen. VDE-Vorgaben zur räumlichen Trennung beachten.

- Mindestabstand zu Frequenzumrichtern, regelbaren Filterpumpen, Inverter-Wärmepumpen: **mindestens 1 m**
- Sensorkabel nicht mit Steckverbindern oder unisolierten Schrankdurchführungen verlängern (Signalpegel: mV-Bereich, pA–nA)
- Netzwerkanbindung bevorzugt kabelgebunden (LAN); WLAN und DLan sind im Industrieumfeld störanfällig
- Netzwerkanbindung VDE-konform **galvanisch getrennt** ausführen; geschirmte RJ45-Stecker am VIOLET-Ende entfernen oder galvanisch getrennte Adapter verwenden

### 1.1 Spannungsversorgung / Kommunikationsverbindung

- 24 V-Netzteil (mind. 15 W) **ausschließlich** für VIOLET verwenden – keine weiteren Verbraucher anschließen
- 5 V-Netzteil **ausschließlich** für den Raspberry Pi
- Bei Bedarf an 24 V DC an anderer Stelle: **separates** Netzteil verwenden
- Kommunikationsverbindung zwischen Raspberry und Dosierbaustein: **USB-Kabel** (beliebige USB-Buchse am Raspberry)

---

## 2 Einleitung

### 2.1 Grundlegende Konfiguration

VIOLET Standalone ist ein Dosierregler für alle gängigen Dosieroptionen. Nach der Grundkonfiguration werden nicht benötigte Menüpunkte ausgeblendet.

**Konfigurationsassistent:** Beim ersten Aufruf der Benutzeroberfläche wird ein Assistent gestartet. Alle Einstellungen können jederzeit unter **MENÜ → KONFIGURATION** und **MENÜ → SYSTEM** angepasst werden.

**UIA (Violet-Inline-Assist):** Bei jeder Steuerungsfunktion ist oben rechts der UIA-Button verfügbar, der direkt zum entsprechenden Abschnitt der Bedienungsanleitung führt.

Aktuelle Versionen aller Anleitungen: **MENÜ → SYSTEM → DOKUMENTATION**

---

## 3 Erstinbetriebnahme / Grundkonfiguration

### 3.1 Benutzeroberfläche im Browser aufrufen

1. Raspberry mit Netzwerk verbinden und per USB mit dem Dosierbaustein verbinden
2. 5 V-Versorgung (Raspberry) und 24 V-Versorgung (Dosierbaustein) einschalten
3. Startzeit: ca. 30 Sekunden

**URL:** `http://violet.local` (bei Bonjour-Unterstützung) oder direkte IP-Adresse aus der Geräteliste des Routers

**Standard-Zugangsdaten:**

| Feld | Wert |
|---|---|
| Benutzername | `admin` |
| Passwort | `violet` |

**Fallback-IP (ohne DHCP-Server):**

| Parameter | Wert |
|---|---|
| IPv4-Adresse | `192.168.1.111` |
| Netzmaske | `255.255.0.0` |
| Gateway | `192.168.1.1` |

Die Weboberfläche kann auf Mobilgeräten als **Bookmark zum Homescreen** gespeichert werden.

### 3.2 Zugangsdaten ändern

`MENÜ → KONFIGURATION → ZUGANGSDATEN`

- Mindestlänge Kennwort: **8 Zeichen**
- Groß-/Kleinschreibung beachten
- Bei Vergessen des Kennworts: Reset über [Abschnitt 15.1](#15-werkseinstellungen-wiederherstellen)

> **Wichtig bei Portfreigabe:** Sicheres Kennwort ist Pflicht.

### 3.3 Netzwerkeinstellungen anpassen

`MENÜ → SYSTEM → NETZWERK`

- Standard: **DHCP-Client** (Router weist IP automatisch zu)
- Feste IP-Adresse: `DHCP verwenden` auf **NEIN** setzen, dann IP, Subnetz, Gateway und DNS eingeben
- Feste IP muss außerhalb des DHCP-Bereichs des Routers liegen

> **Empfehlung für Hausautomation:** Feste IP-Adresse vergeben und Abfragen direkt an diese IP richten (nicht an `http://violet.local`), um zuverlässige Erreichbarkeit und schnelle Namensauflösung sicherzustellen.

**WiFi Direct-Access (HotSpot):**

| Parameter | Wert |
|---|---|
| SSID | `Violet` |
| Kennwort | `violet2023` |

> **Sicherheitshinweis:** Standard-Zugangsdaten unbedingt ändern, wenn der HotSpot dauerhaft genutzt wird.

### 3.4 Beckendaten einstellen

`MENÜ → KONFIGURATION → BECKENDATEN`

Folgende Parameter einstellen:

- `Beckenstandort` (Indoor / Outdoor)
- `Beckenart` (Skimmer / Überlaufrinne)
- `Beckenabdeckung`
- `Beckenoberfläche` in m²
- `Beckeninhalt` in m³
- Art der Nutzung

> Diese Werte bilden die Grundlage für die automatische Parametrierung aller Dosierregler.

### 3.5 Benachrichtigungseinstellungen

`MENÜ → KONFIGURATION → BENACHRICHTIGUNGEN`

Verfügbare Benachrichtigungskanäle:
- **E-Mail** (bis zu 5 Empfängeradressen; über VIOLET Mailservice oder eigenen SMTP)
- **PUSH-Nachrichten** (Pushover.net oder Telegram)
- **HTTP-Requests** an Fremdsysteme (z. B. Hausautomation)

**E-Mail:**
- `Emailversand über`: VIOLET Mailservice oder eigener SMTP
- Test-E-Mail über Button `TESTMAIL SENDEN`

**PUSH – Pushover.net:**
- Benötigt Account und APP von http://www.pushover.net
- `Push Anbieter User-Key`: User Key aus Pushover-Account
- `Push Anbieter API_Token`: API-Token des registrierten Geräts

**PUSH – Telegram:**
- Telegram-App mit Benutzernamen erforderlich
- Benutzername (mit `@`) eintragen → Button `VERBINDEN` → innerhalb von 3 Minuten eine Nachricht an den VIOLET Telegram-Bot senden

**Tägliche Statusbenachrichtigung:** Sendet täglich zu einer konfigurierbaren Uhrzeit alle aktuellen Messwerte und Schaltzustände.

### 3.6 Dosieroptionen konfigurieren

`MENÜ → KONFIGURATION → DOSIEROPTIONEN`

| Option | Beschreibung |
|---|---|
| `Chlor Dosierung (flüssig)` | Flüssig-Chlor (Natriumhypochlorit); Förderleistung der Dosierpumpe angeben; kombinierbar mit Elektrolyse |
| `Salzelektrolyse` | Salzelektrolyse-Anlage; Produktionsleistung in g/h angeben; benötigt Relaiserweiterung; kombinierbar mit Flüssig-Chlor |
| `Chlormessung` | Direkte Chlormessung über potentiostatische Chlor-Elektrode (optional); nur aktivieren wenn Elektrode verbaut |
| `pH-Dosierung` | pH-Senker-Dosierung; Förderleistung angeben; kombinierbar mit pH+ |
| `pH+ Dosierung` | pH-Heber / Alkalinität-Heber; Förderleistung angeben; kombinierbar mit pH- |
| `Flockmittel-Dosierung` | Flockmittel-Dosierung; Förderleistung angeben |

### 3.7 Impulseingang konfigurieren

`MENÜ → KONFIGURATION → IMPULSEINGANG`

**Impulseingang 1** dient der Messwasserüberwachung / Durchflussüberwachung an den Elektroden.

| Sensortyp | Beschreibung |
|---|---|
| `Hallgeber` | Durchflussgeber aus Violet-Zubehör |
| `Näherungsschalter` | Näherungs-/Durchflussschalter mit Schließer-Kontakt (Klemmen GND + DATA an IMP1) |

---

## 4 Dashboard, Statistik, Dosiermengen

### 4.1 Dashboard

`MENÜ → START → DASHBOARD`

Gesamtübersicht über alle Wasserparameter. Angezeigte Widgets richten sich nach den aktivierten Dosieroptionen.

Login: Button `[LOGIN]` oben rechts (Standard: `admin` / `violet`)

#### 4.1.1 Hinweis-, Warn- und Alarmmeldungen

Die erste Zeile zeigt aktuelle Meldungen – farblich nach Schwere markiert:

| Symbol | Farbe | Bedeutung |
|---|---|---|
| ▲ | Grün | Erinnerung / Hinweis |
| ▲ | Gelb | Warnung (z. B. Kanister-Füllstand, Grenzwertüberschreitung) |
| ▲ | Rot | Alarm (Überwachungsfunktion ausgelöst) |

- Einzelne Meldung bestätigen: Button `BESTÄTIGEN`
- Alle Meldungen bestätigen: Button `ALLE BESTÄTIGEN`
- Ein aktiver **Alarm (rot)** muss bestätigt werden, bevor VIOLET die gesperrte Funktion wieder freigibt
- Meldungen, deren Auslöser noch aktiv ist, werden direkt wieder ausgelöst → erst Ursache beheben, dann bestätigen

#### 4.1.2 Widgets im Dashboard

Jedes Widget zeigt Messwert + Zusatzinfos. Klick in den Textbereich öffnet das Kontextmenü.

**Widget Anströmung:**

| Anzeige | Beschreibung |
|---|---|
| Hauptwert | Anströmung in cm/s (inkl. Tages-Min/Max seit 00:00 Uhr) |
| Laufzeit | Tageslaufzeit mit Anströmung > 0 |
| Flockmitteldosierung | Betriebszustand (sofern aktiv) |
| Status | Betriebszustand Dosierregler |
| Tages-Dosiermenge | ml seit 00:00 Uhr |
| Kanister-Restinhalt | in ml |

> **Nach Stromausfall:** „MANUELL AUS"-Funktionen bleiben nach Neustart deaktiviert. „MANUELL EIN"-Funktionen werden nach Unterbrechung > 5 Minuten auf AUTO zurückgesetzt. Manuell ausgelöste Dosierungen werden nicht fortgesetzt.

#### 4.1.3 Kontextmenü für pH- / pH+ / Redox / Elektrolyse / Flockmittel

| Button | Funktion |
|---|---|
| `[ - ]` / `[ + ]` | Sollwert innerhalb definierter Grenzen ändern (wird sofort übernommen) |
| `[ MAN ]` | Manuelle Dosierung starten; Format MM:SS (HH:MM bei Elektrolyse) |
| `[ AUTO ]` | Zurück in Automatikbetrieb |
| `[ AUS ]` | Dosiersteuerung dauerhaft oder für wählbaren Zeitraum deaktivieren |
| `[ GEBINDEWECHSEL ]` | Kanisterinhalt nach Wechsel zurücksetzen (ml eingeben) |

> `MANUELL AUS` hat Vorrang – die Dosierpumpe wird unter keinen Umständen durch die Automatik angesteuert. Für Wartung oder längerfristige Deaktivierung geeignet.

**Widget Dosieroption (Beispiel):**

| Anzeige | Beschreibung |
|---|---|
| Hauptwert | Wasserparameter inkl. Tages-Min/Max |
| Dosiersteuerung | Betriebszustand |
| Status | Betriebszustand Dosierregler |
| Tages-Dosiermenge | ml seit 00:00 Uhr |
| Kanister-Restinhalt | ml + geschätzte Reichweite in Tagen (Basis: Ø letzte 5 Tage Chlor / 7 Tage pH) |

### 4.2 Statistik

`MENÜ → START → STATISTIK`

- Snapshot alle 5 Minuten
- Zeitraum wählbar; Starttag und Anzahl zurückliegender Tage einstellbar
- Messwerte links/rechts wählbar → linke/rechte Y-Achse
- Auswahl wird gespeichert
- Export als `.csv` (Excel) über Button `DOWNLOAD`

### 4.3 Dosierstatistik

`MENÜ → START → DOSIERMENGEN`

- Tägliche Gesamt-Dosiermengen tabellarisch
- Zeitraum wählbar; Spalten konfigurierbar
- Export als `.csv` über Button `DOWNLOAD`
- Einzeldosierungen: im Konfigurationsbereich der jeweiligen Dosieroption unter „Informationen"

---

## 5 Allgemeines zu den Dosieroptionen

- Grundlegende Regelparameter werden anhand der Beckendaten automatisch ermittelt
- **Mengenanpassung**: Schieberegler (+/- 50%) zum Feinabstimmen der Dosiermenge pro Zyklus
- Dosierung erfolgt nur bei **Anströmung** an den Elektroden und wenn kein Sperrgrund vorliegt
- Bei **Grenzwertüberschreitung**: Dosierung gesperrt bis Messwert wieder im Bereich; manuelle Dosierung jederzeit möglich (bei vorhandener Anströmung)
- Benachrichtigung bei Grenzwertüberschreitung: wenn Grenzwert konstant > 10 Minuten über-/unterschritten
- Bei **Erreichen des Tagesdosierlimits**: Sperre bis 23:59 Uhr; Reset um 00:00 Uhr; manuelle Dosierung trotzdem möglich
- Das Tagesdosierlimit ist **kein normaler Begrenzer**, sondern ein Fehlerdetektor (z. B. defekte Pumpe, verstopftes Impfventil)
- Kanister-Restinhalt: Berechnung aus Förderleistung × Laufzeit; Dosierung stoppt **nicht** automatisch bei Restinhalt = 0
- Optional: Sauglanze mit Leermeldekontakt für definitive Pumpensperre

---

## 6 pH Dosierung (Heben/Senken)

### 6.1 pH- Dosiersteuerung

`MENÜ → DOSIERUNG → PH-`

Regelt den pH-Wert in Richtung **pH senken**.

**Einstellbare Parameter:**

| Parameter | Beschreibung | Empfehlung |
|---|---|---|
| `Dosiersteuerung` | Automatik aktivieren/deaktivieren | – |
| `pH Sollwert` | Sollwert für pH- Regelung | 7.2–7.4 (allgemein), 7.4–7.5 (Fliesen/Naturstein) |
| `Mengenanpassung` | Dosiermenge +/- 50% | 0 % |
| `Freigabeverzögerung` | Sperrzeit nach Filterpumpenstart (MM:SS) | 20:00–30:00 |
| `Max. Tagesdosierleistung` | Maximale Tagesdosiermenge in ml | 300–500 ml pro 10 m³ |
| `Unterer Warngrenzwert` | Unterschreitung → Dosierung gesperrt | 0.4 pH unter Sollwert |
| `Oberer Warngrenzwert` | Überschreitung → Dosierung gesperrt | 0.4 pH über Sollwert |
| `Warngrenzwert Kanisterinhalt` | Benachrichtigung bei niedrigem Restinhalt | – |
| `Leermeldekontakt verwenden` | Sauglanze-Kontakt für Pumpensperre | – |
| `Leermeldekontakt Typ` | Öffner oder Schließer | – |

> Bei gleichzeitiger Verwendung von pH- und pH+: Sollwert pH- muss mindestens 0.05 pH-Einheiten **über** dem pH+-Sollwert liegen.

**Informationsbereich:**

| Anzeige | Beschreibung |
|---|---|
| Status pH Dosierung | Warum die Dosierung ggf. keine Freigabe hat |
| Aktueller Messwert | Aktueller pH-Wert |
| Nächster Dosierzyklus | Restzeit bis nächster Zyklus |
| Dosiermenge letzter Zyklus | Dosiermenge letzter aktiver Zyklus |
| Heutige Dosiermenge | Gesamt-Dosiermenge heute; Klick öffnet Detailhistorie (bis 1000 Einträge) |
| Restinhalt Kanister | Restinhalt in ml; Zahnrad = anpassen; Pfeile = Gebindewechsel |

### 6.2 pH+ Dosiersteuerung

`MENÜ → DOSIERUNG → PH+`

Regelt den pH-Wert in Richtung **pH heben**. Parameter und Funktionen identisch mit pH- Dosierung (siehe Abschnitt 6.1).

---

## 7 Chlor Dosierung (Flüssig-Chlor)

`MENÜ → DOSIERUNG → FLÜSSIGCHLOR`

Dosiert Natriumhypochlorit über eine Dosierpumpe. Regelung basiert auf Redox-Potential oder kombiniert auf Redox + Chlorgehalt.

> **Kombinierte Regelung (Redox + Chlor):** Reduziert Stellmittelbedarf um bis zu 25 % gegenüber reiner Chlorregelung; hält DIN-konforme Grenzwerte ein.

**Einstellbare Parameter:**

| Parameter | Beschreibung | Empfehlung |
|---|---|---|
| `Dosiersteuerung` | Automatik aktivieren/deaktivieren | – |
| `Regelart` | Redoxbasiert oder Redox- und chlorbasiert | – |
| `Redox Sollwert` | Sollwert in mV | 750–800 mV (allein); ~20–30 mV unter Elektrolyse-Sollwert (bei Kombination) |
| `Min. Chlorgehalt (mg/l)` | Mindest-Chlorgehalt (nur bei Chlormessung) | 0.15–0.3 mg/l |
| `Max. Chlorgehalt Tag (mg/l)` | Obergrenze 08:00–21:00 Uhr (nur bei Chlormessung) | 0.45–0.60 mg/l |
| `Max. Chlorgehalt Nacht (mg/l)` | Obergrenze 22:00–06:00 Uhr (nur bei Chlormessung) | 0.6–1.0 mg/l |
| `Freigabeverzögerung` | Sperrzeit nach Filterpumpenstart (MM:SS) | 20:00–30:00 |
| `Max. Tagesdosierleistung` | Maximale Tagesdosiermenge in ml | 300–500 ml/10 m³ (Außen); 80–100 ml/10 m³ (Innen) |
| `Unterer Warngrenzwert Redox` | Unterschreitung → Dosierung gesperrt | 150–200 mV unter Sollwert |
| `Oberer Warngrenzwert Redox` | Überschreitung → Dosierung gesperrt | 30–50 mV über Sollwert |
| `Unterer Warngrenzwert Cl` | Unterschreitung → Dosierung gesperrt | 0.05–0.15 mg/l |
| `Oberer Warngrenzwert Cl` | Überschreitung → Dosierung gesperrt | 1.2–1.5 mg/l |
| `Warngrenzwert Kanisterinhalt` | Benachrichtigung bei niedrigem Restinhalt | – |
| `Leermeldekontakt verwenden` | Sauglanze-Kontakt | – |

---

## 8 Elektrolyse-Steuerung

`MENÜ → DOSIERUNG → SALZELEKTROLYSE`

Steuerung von Salzelektrolyse-Anlagen (bestehend oder selbst zusammengestellt). Separate Ausgänge für Zellensteuerung und Umpolung.

> **Kombinierte Regelung (Redox + Chlor):** Identische Vorteile wie bei Flüssig-Chlor; empfohlen für Inline-Elektrolyse-Anlagen (Redoxmessung nicht immer zuverlässig).

**Einstellbare Parameter:**

| Parameter | Beschreibung | Empfehlung |
|---|---|---|
| `Dosiersteuerung` | Automatik aktivieren/deaktivieren | – |
| `Regelart` | Redoxbasiert oder Redox- und chlorbasiert | – |
| `Redox Sollwert` | Sollwert in mV | 650–750 mV; ~20–30 mV über Flüssigchlor-Sollwert (bei Kombination) |
| `Min. Chlorgehalt (mg/l)` | Mindest-Chlorgehalt (nur bei Chlormessung) | 0.15–0.3 mg/l |
| `Max. Chlorgehalt Tag (mg/l)` | Obergrenze (nur bei Chlormessung) | 0.45–0.60 mg/l |
| `Max. Chlorgehalt Nacht (mg/l)` | Obergrenze (nur bei Chlormessung) | 0.6–1.0 mg/l |
| `Freigabeverzögerung` | Sperrzeit nach Filterpumpenstart (MM:SS) | 05:00–10:00 |
| `Umpolintervall (HH:MM)` | Intervall für Zellenumpolung | 4–6 Stunden |
| `Max. Tagesproduktion (g)` | Maximale tägliche Chlorproduktion | 50–80 g/10 m³ (Außen); 10–15 g/10 m³ (Innen) |
| `Unterer Warngrenzwert Redox` | Unterschreitung → Dosierung gesperrt | 250–300 mV unter Sollwert |
| `Oberer Warngrenzwert Redox` | Überschreitung → Dosierung gesperrt | 100–150 mV über Sollwert |
| `Unterer Warngrenzwert Cl` | (nur bei Chlormessung) | 0.05–0.15 mg/l |
| `Oberer Warngrenzwert Cl` | (nur bei Chlormessung) | 1.2–1.5 mg/l |
| `Warngrenzwert Zellenlaufzeit` | Benachrichtigung bei verbleibender Restlaufzeit | – |

**Informationsbereich (zusätzlich zu pH/Chlor):**

| Anzeige | Beschreibung |
|---|---|
| Polaritätswechsel (HH:MM:SS) | Restzeit bis zum nächsten Polaritätswechsel |
| Heutige Produktionsleistung | Gesamt-Produktion heute in g |
| Restlaufzeit Zelle | Verbleibende Zelllaufzeit; Zahnrad = anpassen; Pfeile = Zellwechsel |

---

## 9 Flockmittel-Dosierung

`MENÜ → DOSIERUNG → FLOCKMITTEL`

Dosiert konstant kleine Flockmittelmengen über den Tag verteilt. Freigabe erfolgt ohne Verzögerung mit Pumpenstart.

**Einstellbare Parameter:**

| Parameter | Beschreibung | Empfehlung |
|---|---|---|
| `Dosiersteuerung` | Automatik aktivieren/deaktivieren | – |
| `Tagesdosiermenge` | Tägliche Gesamtdosiermenge in ml | 20–30 ml pro 10 m³ pro Tag |
| `Aufteilen auf` | Zeitspanne, auf die die Tagesdosiermenge verteilt wird | – |
| `Warngrenzwert Kanisterinhalt` | Benachrichtigung bei niedrigem Restinhalt | – |
| `Leermeldekontakt verwenden` | Sauglanze-Kontakt | – |

---

## 10 Elektroden Kalibrierung

### 10.1 Allgemeines zum Thema Kalibrieren

- Elektrochemische Sensoren sind Verschleißteile und müssen regelmäßig kontrolliert werden
- Wasserparameter mindestens **wöchentlich** mit Fotometer prüfen (Desinfektionsmittel + pH)
- Neue Elektroden müssen einlaufen: **pH/Redox** mind. 4–6 Stunden, **Chlor** mind. 24 Stunden im Poolwasser
- Kalibrierung **nicht** direkt nach Reinigung der Elektrode – Einlaufzeit erneut abwarten
- Pufferlösungen sauber halten; Elektrode vor Eintauchen mit Leitungswasser spülen und trocken tupfen
- Pufferlösungen nach Öffnen gut verschließen; Lichtschutz; Verfallsdatum beachten

### 10.2 Kalibrierung der pH Elektrode

`MENÜ → DOSIERUNG → ELEKTRODENKALIBRIERUNG`

**Methode:** 2-Punkt-Kalibrierung (pH 7 + zweite Pufferlösung mit mind. 2 pH-Einheiten Abstand)

**Ablauf:**
1. Klick auf Überschrift `pH Elektrode kalibrieren (2-Punkt)`
2. Temperatur der Pufferlösung eingeben
3. Elektrode in Pufferlösung 1 (pH 7) tauchen; Wert `Gemessener Rohwert (mV)` stabilisieren lassen
4. Wert der Pufferlösung 1 eingeben → Button `WEITER`
5. Elektrode spülen/trocknen → in Pufferlösung 2 tauchen; Rohwert stabilisieren lassen
6. Wert der Pufferlösung 2 eingeben → Button `KALIBRIEREN`

**Erwartete Rohwerte:**

| Pufferlösung | Erwarteter Rohwert |
|---|---|
| pH 7 | ca. 0 mV (± 15 mV) |
| pH 4 | ca. 177,5 mV (± 25 mV, temperaturabhängig) |

> Erinnerung an nächste Kalibrierung konfigurierbar (7 Tage bis 6 Monate).

### 10.3 Kalibrierung der Redox Elektrode

`MENÜ → DOSIERUNG → ELEKTRODENKALIBRIERUNG`

**Methode:** 1-Punkt-Kalibrierung mit beliebiger Redox-Pufferlösung

**Ablauf:**
1. Klick auf Überschrift `Redox Elektrode kalibrieren`
2. Wert der Pufferlösung eingeben
3. Elektrode eintauchen; `Gemessener Rohwert (mV)` stabilisieren lassen
4. Button `KALIBRIEREN`

> Kann gleichzeitig mit der pH-Kalibrierung durchgeführt werden.

### 10.4 Kalibrierung der Chlor Elektrode

`MENÜ → DOSIERUNG → ELEKTRODENKALIBRIERUNG`

**Methode:** 2-Punkt-Kalibrierung (0-Punkt + DPD1-Referenzmessung)

> **Voraussetzung:** Elektrode mind. 24 Stunden montiert und elektrisch angeschlossen (nicht in Aufbewahrungslösung anschließen).

**0-Punkt ermitteln** (nur bei Filterpumpe AUS / keine Anströmung > 60 Min.):
1. Klick auf Überschrift `Chlor-Elektrode kalibrieren`
2. Angezeigten 0-Punkt durch Klick auf `0-Punkt speichern` speichern
3. Vorgang abgeschlossen (kann bei Bedarf wiederholt werden)

**Kalibrierung per DPD1-Referenzmessung:**
1. Filterpumpe muss mind. 15 Minuten laufen
2. Wasserprobe möglichst nahe an der Elektrode entnehmen → Button `WASSERPROBE ENTNOMMEN`
3. DPD1-Referenzmessung mit Fotometer durchführen
4. Ergebnis in Feld `Referenzmessung DPD1 (mg/l)` eingeben
5. Button `KALIBRIEREN`

**Gültigkeitsbereich:** Chlorgehalt zwischen **0.2 mg/l und 3.0 mg/l**

> Chlor-Elektrode: auch ohne konfigurierte Erinnerung wird nach 3 Wochen automatisch ein Dashboard-Hinweis angezeigt (nicht deaktivierbar).

**Korrekturfaktor für unterschiedliche Anströmungsgeschwindigkeiten:**

Direkt nach der Kalibrierung sichtbar. Anströmungsgeschwindigkeit verändern (z. B. Pumpdrehzahl ändern) → Wert stabilisieren lassen → Button `Anströmung kompensieren`.

- Neue Anströmung muss mind. 2 cm/s von der Kalibrieranströmung abweichen
- Bereich: 5–20 cm/s
- Einmalige Ermittlung ausreichend

Weitere Infos: https://www.poolsteuerung.de/viewtopic.php?f=99&t=2074

### 10.5 Kalibrier-Historie

Für jede Elektrode verfügbar über das „Statistik"-Symbol in der Zeile `Letzte Kalibrierung`.

| Markierung | Bedeutung |
|---|---|
| Grüner Punkt | Kalibrierung fehlerfrei |
| Roter Punkt | Parameter außerhalb der Grenzen (Hinweis wurde angezeigt) |

Frühere fehlerfreie Kalibrierungen können per Klick wiederhergestellt werden.

---

## 11 Regelmäßige Kontrolle aller dosierrelevanten Bauteile

| Aufgabe | Intervall |
|---|---|
| Wasserparameter (pH + Desinfektionsmittel) mit Fotometer prüfen (pH 7.0–7.5; Chlor 0.3–1.5 mg/l) | Mind. 1× wöchentlich |
| Alkalinität (30–100 ppm / 2–6 °kH) und ggf. Salzgehalt (Elektrolyse) prüfen | Alle 2–4 Wochen |
| Chlor-Elektrode kalibrieren | Alle 1–2 Wochen |
| pH- und Redox-Elektroden kalibrieren | Alle 1–3 Monate |
| Sichtkontrolle Peristaltikschläuche der Dosierpumpen (Undichtigkeiten, Beschädigungen) | Alle 3–4 Wochen |
| Impfventile für Chlor und pH-Heber auf Verkrustung prüfen | Alle 4–6 Wochen |
| Impfventile für pH-Senker und Flockmittel prüfen | Alle 5–6 Monate |
| Dosierschläuche auf Beschädigungen und Alterung prüfen | Alle 5–6 Monate |
| Drehkreuz der Dosierpumpen prüfen (Verschleiß; ggf. mit handelsüblichem Fett nachschmieren) | Alle 5–6 Monate |

---

## 12 Außerbetriebnahme der Dosiersteuerung im Winter

**Dosierpumpen einwintern:**
1. Saugschlauch in klares Wasser stellen
2. Manuelle Dosierung 2–3 Minuten auslösen (Schläuche spülen)
3. Bei Frostgefahr: Saugschlauch entnehmen und nochmals kurz manuell dosieren (Restwasser entfernen)
4. Demontage nicht notwendig; Pumpen und Schläuche sind frostfest

**Elektroden einwintern:**
1. Elektroden 15–20 Minuten in Reinigungslösung legen (elektrisch getrennt)
2. Bei sichtbaren Verunreinigungen länger einlegen; mechanische Reinigung (weiche Bürste) vorsichtig möglich
3. Mit klarem Wasser spülen
4. In Aufbewahrungsköcher mit **frischer 3m KCl-Lösung** einlagern (stehend, Elektrode eingetaucht)

> Normales Wasser, destilliertes Wasser, Kalibrierlösung oder andere Flüssigkeiten sind **nicht** geeignet. Elektroden nicht elektrisch angeschlossen lassen.

**Messzelle einwintern:**
- Messzelle und Schläuche wasserfrei machen (besonders bei Frostgefahr)
- Demontage nicht notwendig
- Falls Filterpumpe weiterlaufend: Alle Dosiersteuerungen über Dashboard auf **MANUELL AUS** setzen

---

## 13 Systemeinstellungen

### 13.1 Netzwerkeinstellungen

`MENÜ → SYSTEM → NETZWERK`

#### 13.1.1 Netzwerkeinstellungen (LAN)

| Parameter | Beschreibung |
|---|---|
| `DHCP verwenden` | DHCP ein/aus; bei AUS: manuelle Eingabe von IP, Subnetz, Gateway, DNS |
| `IPv4 Adresse` | Nur sichtbar bei DHCP=NEIN |
| `Subnetz` | Nur sichtbar bei DHCP=NEIN |
| `Gateway` | Nur sichtbar bei DHCP=NEIN |
| `DNS-Server` | Nur sichtbar bei DHCP=NEIN |

#### 13.1.2 WiFi Direct-Access

VIOLET stellt einen 2.4-GHz-WLAN-HotSpot bereit.

- Erreichbarkeit: `http://violet.local` oder `http://172.16.1.200`
- Kein Internetzugang über diese Verbindung; kein Zugriff auf das LAN-Netzwerk
- Standard-SSID: `Violet` | Standard-Kennwort: `violet2023`

| Parameter | Beschreibung |
|---|---|
| `WiFi Direct-Access` | HotSpot aktivieren/deaktivieren |
| `SSID` | Name des HotSpots |
| `Kennwort` | Mind. 8 Zeichen |
| `Kanal` | WLAN-Kanal 1–11 |

#### 13.1.3 Aktuelle Daten (LAN)

Zeigt aktuelle Netzwerkkonfiguration (IPv4, IPv6, Subnetz, Gateway, MAC-Adresse, Steuerungs-ID) – nur lesbar.

### 13.2 Sprache / Farbe / Uhrzeit der Benutzeroberfläche

`MENÜ → SYSTEM → BENUTZEROBERFLÄCHE`

- Sprache und Farbschema wählbar
- Zeitzone einstellen (z. B. `EUROPE/Berlin`); Sommer-/Winterzeit wird automatisch umgestellt
- Nach Änderung der Uhrzeiteinstellungen: automatischer Neustart (~20 Sekunden)

### 13.3 Dienste

`MENÜ → SYSTEM → DIENSTE`

#### 13.3.1 FTP-Server

Zugriff auf Statistikdateien und Konfigurations-Backups auf der SD-Card.

| Parameter | Wert |
|---|---|
| Host | `violet.local` oder IP-Adresse |
| Port | 21 |
| Benutzername | `backupuser` |
| Passwort | `backupuser` |

> Kennwort änderbar über Schloss-Symbol; gilt auch für CIFS/SAMBA. Benutzername nicht änderbar. Nur im lokalen Netzwerk erreichbar (kein Fernzugriff).

#### 13.3.2 CIFS/SAMBA Freigabe

Netzlaufwerk für Statistikdateien und Backups.

| Parameter | Wert |
|---|---|
| Ordner | `\\violet.local` oder `\\<IP-Adresse>` |
| Benutzername | `backupuser` |
| Passwort | `backupuser` |

Unterordner in der Freigabe:
- `/backup` – Konfigurationsbackups
- `/history` – Statistikdateien

**Windows-10-Einrichtung (Kurzanleitung):**
1. Windows Explorer öffnen → „Dieser PC" → Registerkarte „Computer"
2. „Netzlaufwerk verbinden" → Laufwerksbuchstabe wählen
3. Ordner: `\\violet.local` eingeben → „Durchsuchen"
4. Netzwerkordner markieren → OK
5. Zugangsdaten eingeben → „Anmeldedaten speichern" → OK
6. Ordner „Pool" markieren → OK → „Fertig stellen"

### 13.4 Update

`MENÜ → SYSTEM → UPDATE`

| Update-Typ | Benachrichtigungstext | Vorgehen |
|---|---|---|
| Automatisches Update | „Keine Aktion erforderlich" | VIOLET installiert nachts zwischen 02:00–06:00 Uhr automatisch; manuell vorzeitig möglich |
| Manuelles Update | „Installation erforderlich" | Muss manuell über Button `Update installieren` ausgelöst werden; Releasenotes beachten |

> Nach Update: VIOLET startet neu (~kurze Nichterreichbarkeit). Fernzugriff wird vorübergehend getrennt.

### 13.5 Konfigurations-Backup

`MENÜ → SYSTEM → BACKUP`

- Zugangsdaten und Netzwerkeinstellungen werden **nicht** in Backups gespeichert/verändert
- Backups enthalten nur Konfigurationsdaten (keine Statistiken)
- Ältere Backups können immer eingespielt werden (fehlende Parameter werden beibehalten)

#### 13.5.1 Backup auf lokaler SD-Card

- Täglich oder wöchentlich (bestimmter Wochentag)
- Max. 100 Backups; älteste werden überschrieben (außer manuelle Backups)
- Manuelles Backup: Button `Backup jetzt manuell erstellen`

#### 13.5.2 Backup auf USB-Speichermedium

- FAT32 oder HFS+-formatierter USB-Stick
- Speicherort: `/VIOLET/config` (wird automatisch angelegt)
- Funktionsweise identisch mit SD-Card-Backup

### 13.6 Dokumentation

`MENÜ → SYSTEM → DOKUMENTATION`

Alle verfügbaren Anleitungen als PDF; Sprache wählbar; werden bei Software-Updates aktualisiert.

---

## 14 System Logfiles

### 14.1 Logfile „Aktionen"

`MENÜ → LOGFILES → AKTIONEN`

Max. 5000 Einträge; älteste werden gelöscht.

| Kategorie | Inhalt |
|---|---|
| `USERACTION` | Konfigurationsänderungen, manuelles Schalten |
| `CONTROLTASK` | Schaltaktionen durch konfigurierte Regeln |
| `SYSTEMTASK` | Benachrichtigungen, Neustarts, Backups |

- Kategorien über Button `KONFIGURIEREN` ein-/ausblenden
- Export als Textdatei über Button `DOWNLOAD`
- Logfile nicht löschbar / nicht bearbeitbar

### 14.2 Logfile „Benachrichtigungen"

`MENÜ → LOGFILES → BENACHRICHTIGUNGEN`

Letzte 500 Benachrichtigungen; Datum, Uhrzeit, Betreff, Benachrichtigungskanal.

| Kanal | Beschreibung |
|---|---|
| `MAIL` | Mailversand über VIOLET Mailservice |
| `SMTP` | Mailversand über eigenen SMTP |
| `PUSH` | Push-Nachrichten |
| `HTTP` | HTTP-Requests |

| Farbe | Bedeutung |
|---|---|
| Grün | Erfolgreich versendet |
| Orange | Nicht erfolgreich; erneuter Versuch folgt |
| Rot | Nicht versendet oder global deaktiviert; kein Wiederholungsversuch |
| Durchgestrichen | Kanal in Konfiguration nicht aktiviert |

> Klick auf Kanal-Text: Response der Schnittstelle zur Diagnose anzeigen.

### 14.3 Ausgänge testen

`MENÜ → LOGFILES → AUSGÄNGE TESTEN`

- Schaltzustand aller Dosierausgänge / Leermeldekontakte anzeigen
- Relaisausgang für max. 5 Sekunden manuell schalten (kein Dauerbetrieb)
- Namensgebung der Leermeldekontakte anpassbar

> Dosierausgänge (pH, Chlor, Elektrolyse, Flockmittel) max. 4 Sekunden aktiv; nur nutzen wenn Dosierpumpen noch nicht am Kanister angeschlossen.

---

## 15 Werkseinstellungen wiederherstellen

### 15.1 Zurücksetzen in den Auslieferungszustand

**Methode:** USB-Verbindung zwischen Raspberry und Dosiermodul **5× innerhalb von 30 Sekunden** ab- und wieder anstecken.

**Ablauf:**
1. USB-Stecker abziehen → sofort wieder anstecken
2. 3 Sekunden warten
3. Vorgang insgesamt 5× wiederholen (alles innerhalb von 30 Sekunden)
4. 30 Sekunden nach erstem Abstecken: Reset wird ausgeführt → System fährt herunter (LAN-LEDs erlöschen)
5. Raspberry kurz stromlos schalten → wieder einschalten
6. Nach ca. 30 Sekunden: VIOLET wieder erreichbar mit Werkseinstellungen

**Zurückgesetzte Einstellungen:**
- DHCP aktiviert
- Zugangsdaten: `admin` / `violet`
- Alle Konfigurationseinstellungen zurückgesetzt

---

## 16 Anbindung an Hausautomationssysteme

> **Empfehlung:** Feste IP-Adresse für VIOLET konfigurieren (außerhalb des DHCP-Bereichs); alle Abfragen direkt an die IP richten (nicht an `http://violet.local`).

### 16.1 JSON-API – Abfrage von Messwerten

VIOLET stellt alle Messwerte über eine JSON-API zur Verfügung.

**Basis-URL:** `http://<VIOLET-IP>/getReadings?<PARAMETER>`

**API-Beschreibung (vollständige Liste):**  
https://www.pooldigital.de/_red/paperwork/api_description/getReadings.xlsx

**Beispiel-Abfragen:**

```
GET /getReadings?ALL
→ Alle Messwerte und Zustände

GET /getReadings?pH_value
→ pH-Wert + Tages-Min/Max

GET /getReadings?IMP1_value
→ Durchflussgeber-Messwert

GET /getReadings?pH_value,orp_value,pot_value
→ pH, ORP (Redox) und Potentiostat (Chlor)

GET /getReadings?_value
→ Alle Werte die „_value" enthalten

GET /getReadings?DOSING
→ Tägliche Dosiermengen

GET /getReadings?ALL,DOSAGE,RUNTIMES
→ Alle maximal verfügbaren Werte
```

**Beispiel-Response `/getReadings?pH_value`:**
```json
{
  "pH_value_min": 7.22,
  "pH_value_max": 7.30,
  "pH_value": 7.30
}
```

**Beispiel-Response `/getReadings?DOSING`:**
```json
{
  "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "2204",
  "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": "0.0",
  "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "144",
  "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "0",
  "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "84"
}
```

---

## 17 Benachrichtigungen per HTTP Request an Fremdsysteme

### 17.1 Konfiguration des HTTP Requests

`MENÜ → KONFIGURATION → BENACHRICHTIGUNGEN`

VIOLET sendet Benachrichtigungen als GET- oder POST-Request mit folgenden Feldern:

| Feldname | Wert |
|---|---|
| `ERRORCODE` | Vierstelliger Fehlercode |
| `SUBJECT` | Kurzbeschreibung des Fehlers |

**Einstellbare Parameter:**

| Parameter | Beschreibung |
|---|---|
| `http Requests` | Global aktivieren/deaktivieren |
| `URL/IP zur Empfänger-API` | IP-Adresse oder Domainname (ohne `http://`); Port muss 80 sein |
| `Pfad zur Empfänger-API` | Vollständiger Pfad inkl. `/` (z. B. `/myScript/violet.php`) |
| `Basis-Query` | Optionale zusätzliche field=value Paare (mehrere mit `&` trennen) |
| `Methode` | GET oder POST |
| `API-Response-body (success)` | String, den die API bei Erfolg zurücksendet (Pattern-Matching) |
| `API-Response-body (error)` | String, den die API bei Fehler zurücksendet |

> Bei unbekannter oder ausbleibender Antwort: erneuter Versuch alle 60 Minuten, max. 10×. Bestätigung der Fehlermeldung in VIOLET stoppt Wiederholungsversuche.

**Beispiel GET-Request (Fehlercode 0020):**
```
http://192.168.1.100/myScript/violet_messaging.php?ERRORCODE=0020&SUBJECT=Alarm,Filterdrucküberwachung (Druck zu niedrig)&user=Violet
```

### 17.2 Fehlercode-Liste für HTTP Requests

| ERRORCODE | SUBJECT |
|---|---|
| 0000 | Testnachricht |
| 0001 | Statusnachricht |
| 0008 | CPU-Temperatur hoch (> 83 °C) |
| 0009 | CPU-Temperatur zu hoch (> 95 °C) |
| 0010 | Update steht zur Installation bereit. Keine Aktion erforderlich. |
| 0011 | Update steht zur Installation bereit. Installation erforderlich. |
| 0012 | Update steht zur Installation bereit. Installation erforderlich. |
| 0022 | Warnung, Messwasserüberwachung (Anströmung fehlt) |
| 0023 | Warnung, Messwasserüberwachung (Anströmung zu hoch) |
| 0120 | Warnung, Chlor-Dosierung: Redox Grenzwert erreicht |
| 0121 | Warnung, Chlor-Dosierung: Chlor Grenzwert erreicht |
| 0122 | Warnung, Chlor-Dosierung: max. Tagesdosierleistung erreicht |
| 0123 | Warnung, Chlor-Kanister Restinhalt niedrig |
| 0124 | Warnung, Chlor-Kanister leer |
| 0125 | Warnung, Leermeldekontakt: Chlor-Kanister |
| 0130 | Warnung, Elektrolyse: Redox Grenzwert erreicht |
| 0131 | Warnung, Elektrolyse: Chlor Grenzwert erreicht |
| 0132 | Warnung, Elektrolyse: maximale Tagesproduktion erreicht |
| 0133 | Warnung, Elektrolyse: Restlaufzeitwarnung für Zelle |
| 0134 | Warnung, Elektrolyse: maximale Gesamt-Betriebszeit erreicht |
| 0150 | Warnung, pH-minus Dosierung: pH Grenzwert erreicht |
| 0152 | Warnung, pH-minus Dosierung: max. Tagesdosierleistung erreicht |
| 0153 | Warnung, pH-minus Dosierung: Kanister Restinhalt niedrig |
| 0154 | Warnung, pH-minus Dosierung: Kanister leer |
| 0155 | Warnung, Leermeldekontakt: pH-minus Kanister |
| 0160 | Warnung, pH-plus Dosierung: pH Grenzwert erreicht |
| 0162 | Warnung, pH-plus Dosierung: max. Tagesdosierleistung erreicht |
| 0163 | Warnung, pH-plus Dosierung: Kanister Restinhalt niedrig |
| 0164 | Warnung, pH-plus Dosierung: Kanister leer |
| 0165 | Warnung, Leermeldekontakt: pH-plus Kanister |
| 0173 | Warnung, Flockmittel: Kanister Restinhalt niedrig |
| 0174 | Warnung, Flockmittel: Kanister leer |
| 0175 | Warnung, Leermeldekontakt: Flockmittel Kanister |
| 0180 | Erinnerung, pH-Elektrode kalibrieren |
| 0181 | Erinnerung, Redox-Elektrode kalibrieren |
| 0182 | Erinnerung, Chlor-Elektrode kalibrieren |
| 0200 | Warnung, Dosiermodul nicht mehr verbunden (abgesteckt) |
| 0201 | Warnung, Dosiermodul, Kommunikation verloren |
| 0208 | Alarm, Zweites Dosiermodul erkannt. Wird ignoriert. |

---

## 18 Konformitätserklärung VIOLET

**EG-Konformitätserklärung**

Hiermit erklären wir, dass das nachstehend bezeichnete Produkt den grundlegenden Sicherheits- und Gesundheitsanforderungen der EG-Richtlinie Niederspannung entspricht.

| Feld | Inhalt |
|---|---|
| Produktbezeichnung | VIOLET |
| Seriennummer | Siehe Herstelleretikett am Gerät |
| Produkttyp | Schwimmbadsteuerung |
| Hersteller | PoolDigital GmbH & Co KG, Gablinger Weg 102, D-86156 Augsburg |
| Datum | 01. Februar 2024 |

**Angewendete harmonisierte Normen:**
- EG-Niederspannungsrichtlinie 2014/35/EU
- EMV-Richtlinie 2014/30/EU
- EN 61000-4-3, EN 61000-4-4, EN 61000-4-5, EN 61000-4-6, EN 61000-4-8
- EN 61000-3-2, EN 61000-3-3
- EN 55011

---

## 19 GPL License Statement

Besides VIOLET's application code (closed-source), this product includes software code developed by third parties, including software subject to the GNU GPLv3, LGPL2.1, Apache License 2.0 and MIT License.

Full license information:  
https://www.pooldigital.de/_red/paperwork/privacy_policy/LicenseStatement.pdf

**Written Offer for GPL/LGPL Source Code:**  
Source code available on request (USB-Stick; nominal cost for shipping/media; valid 3 years).

Contact:
> PoolDigital GmbH & Co. KG  
> – GPL Anfrage VIOLET –  
> Kapellenstraße 10a  
> 86441 Zusmarshausen
