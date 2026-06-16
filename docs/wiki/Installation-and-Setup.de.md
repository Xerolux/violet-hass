> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Installation-and-Setup)**

---

# 📦 Installation & Setup

> Schritt-für-Schritt Anleitung zur Installation des Violet Pool Controller Addons in Home Assistant.

---

## ⚠️ WICHTIG - VOR DER INSTALLATION

### 🔒 Sicherheit & Haftungsausschluss

**Das Violet Pool Controller Addon steuert echte Poolausrüstung:**

- ⚠️ **Pumpen, Heizungen, Dosieranlagen können ferngesteuert werden**
- ⚠️ **Falsche Konfiguration kann zu Sachschäden führen**
- ⚠️ **Chemikalien können gefährlich sein bei falscher Handhabung**
- ⚠️ **Elektrische Anlagen müssen vorschriftsmäßig installiert sein**

**Bevor du installierst:**

✅ **Lies den vollständigen Haftungsausschluss**: [Konfigurationshilfe (DE)](https://github.com/Xerolux/violet-hass/blob/main/docs/help/configuration-guide.de.md#-sicherheit--haftung)
✅ **Verstehe alle Sicherheitsmechanismen**
✅ **Halte manuelle Not-Abschalter bereit**
✅ **Beachte alle Sicherheitsdatenblätter**
✅ **Konsultiere einen Fachbetrieb bei Unsicherheiten**

> **⚠️ Die Nutzung erfolgt auf eigene Verantwortung und Gefahr!**

---

## Systemvoraussetzungen

| Anforderung | Mindest | Empfohlen |
|-------------|---------|-----------|
| Home Assistant | 2026.5.0 | 2026.x (aktuell) |
| Python | Wird von Home Assistant 2026.5.0+ bereitgestellt | Von Home Assistant verwaltet |
| Netzwerk | Controller per HTTP erreichbar | Feste IP-Adresse (DHCP-Reservierung) |
| HACS | Optional | Empfohlen für einfache Updates |
| Speicher | <10 MB | – |

> **Hinweis**: HA 2026.x wird vollständig unterstützt und ist die empfohlene Version.

---

## Methode 1: HACS (Empfohlen)

HACS (Home Assistant Community Store) ermöglicht einfache Installation und automatische Updates.

### Schritt 1: HACS installieren (falls noch nicht vorhanden)

Falls HACS noch nicht installiert ist, folge der [offiziellen HACS-Installationsanleitung](https://hacs.xyz/docs/use/download/download/).

### Schritt 2: Repository hinzufügen

1. Öffne **HACS** in Home Assistant
2. Klicke auf die **drei Punkte (⋮)** oben rechts
3. Wähle **"Benutzerdefinierte Repositories"**
4. Füge folgendes ein:
   - **Repository-URL**: `https://github.com/Xerolux/violet-hass`
   - **Kategorie**: `Integration`
5. Klicke **"Hinzufügen"**

### Schritt 3: Integration installieren

1. Gehe in HACS zu **"Integrationen"**
2. Suche nach **"Violet Pool Controller"**
3. Klicke auf die Karte und dann auf **"Herunterladen"**
4. Bestätige die Installation

### Schritt 4: Home Assistant neu starten

```
Einstellungen → System → Neustart → Home Assistant neu starten
```

Oder per Docker:
```bash
docker restart homeassistant
```

### Schritt 5: Integration hinzufügen

1. Gehe zu **Einstellungen → Geräte & Dienste**
2. Klicke auf **"+ Integration hinzufügen"**
3. Suche nach **"Violet Pool Controller"**
4. Folge dem [Setup-Assistenten](#setup-assistent)

---

## Methode 2: Manuelle Installation

Für Benutzer ohne HACS oder Entwickler.

### Option A: Via Git

```bash
# Wechsle in das custom_components Verzeichnis
cd /config/custom_components/

# Repository klonen
git clone https://github.com/Xerolux/violet-hass.git temp_violet

# Nur den Integration-Ordner kopieren
cp -r temp_violet/custom_components/violet_pool_controller ./

# Temp-Ordner löschen
rm -rf temp_violet
```

### Option B: Via ZIP-Download

1. Gehe zu: https://github.com/Xerolux/violet-hass/releases/latest
2. Lade `violet_pool_controller.zip` herunter (oder `Source code.zip`)
3. Entpacke das Archiv
4. Kopiere den Ordner `custom_components/violet_pool_controller` nach `/config/custom_components/`

```bash
# Beispiel (angepasst auf deinen Download-Pfad)
unzip violet-hass-main.zip
cp -r violet-hass-main/custom_components/violet_pool_controller /config/custom_components/
```

### Schritt 3: Home Assistant neu starten

Nach der manuellen Installation **muss** Home Assistant neugestartet werden.

### Schritt 4: Integration hinzufügen

Identisch mit der HACS-Methode: **Einstellungen → Geräte & Dienste → + Integration → "Violet Pool Controller"**

---

## Setup-Assistent

Der integrierte Setup-Assistent führt dich durch alle Konfigurationsschritte.

### Schritt 1: 🚨 DISCLAIMER (HAFTUNGSAUSSCHLUSS)

⚠️ **SEHR WICHTIG - BITTE SORGFÄLTIG LESEN!**

Du wirst einen **umfangreichen Haftungsausschluss** sehen mit:

- **⚠️ Sicherheitswarnung**: Alle Risiken bei der Nutzung
- **🔒 Deine Verantwortung**: Was du tun musst
- **⚖️ Haftungsausschluss**: Keine Gewährleistung
- **📖 Dokumentation**: Links zur ausführlichen Hilfe

**Du musst:**
1. ✅ Den gesamten Text lesen
2. ✅ Das Häkchen bei **"Ich akzeptiere"** setzen
3. ✅ **"Bestätigen"** klicken

**Ohne Bestätigung kannst du die Integration nicht einrichten!**

### Schritt 2: Controller-Verbindung

```
┌──────────────────────────────────────────┐
│  Violet Pool Controller – Verbindung     │
├──────────────────────────────────────────┤
│  Host (IP oder Hostname):                │
│  ┌────────────────────────────────────┐  │
│  │ 192.168.1.100                      │  │
│  └────────────────────────────────────┘  │
│                                          │
│  Port:           [80      ]              │
│  SSL verwenden:  [ ] Nein  [x] Ja        │
│  SSL verifiz.:   [x] Ja   [ ] Nein      │
│  Benutzername:   [admin   ]              │
│  Passwort:       [••••••••]              │
│  Controller-Name:[Violet Pool Controller]│
└──────────────────────────────────────────┘
```

| Feld | Beschreibung | Beispiel |
|------|--------------|---------|
| **Host** | IP-Adresse oder Hostname des Controllers | `192.168.1.100` oder `violet.local` |
| **Port** | HTTP/HTTPS Port (Standard: 80) | `80`, `443`, `8080` |
| **SSL** | HTTPS-Verbindung verwenden | Aktivieren wenn HTTPS |
| **SSL verifizieren** | Zertifikat validieren | Deaktivieren nur bei selbsignierten Zertifikaten |
| **Benutzername** | API-Benutzername (falls gesetzt) | `admin` |
| **Passwort** | API-Passwort (falls gesetzt) | – |
| **Controller-Name** | Anzeigename (wichtig bei mehreren Controllern!) | `Außenpool`, `Whirlpool` |

> **IP-Adresse finden**: Öffne deinen Router-Admin (z.B. `192.168.1.1`) → "Verbundene Geräte" → "Violet" suchen. Alternativ: `ping violet.local`

### Schritt 3: Pooldaten

1. **Poolvolumen**: In m³ (z.B. 40)
2. **Pool-Typ**: Aufenthaltsbecken, Sportbecken, etc.
3. **Desinfektionsmethode**: Chlor, Aktivsauerstoff, etc.

### Schritt 4: Features auswählen

Wähle die Features aus, die dein Controller unterstützt:

| Feature | Aktivieren wenn... |
|---------|-------------------|
| **Heizung** | Ein Wärmetauscher oder Heizer angeschlossen ist |
| **Solar** | Solarkollektor vorhanden |
| **PV-Überschuss** | Solaranlage für Überschuss-Nutzung |
| **pH-Dosierung** | pH- oder pH+ Dosierpumpe angeschlossen |
| **Chlor-Dosierung** | Chlor-Dosierpumpe angeschlossen |
| **Flockmittel** | Flockungs-Dosierpumpe vorhanden |
| **DMX-Beleuchtung** | Pool-Beleuchtung per DMX gesteuert |
| **Digitale Eingänge** | DI1–DI8 für externe Sensoren/Schalter |
| **Abdeckung** | Poolabdeckung (Cover) mit Steuerung |
| **Erweiterungs-Relais** | Zusätzliche Relais-Module (REL1–REL8) |
| **Rückspülung** | Automatische Rückspülung konfiguriert |

> **Tipp**: Features können später über **Einstellungen → Geräte & Dienste → Violet → Optionen → Neu konfigurieren** angepasst werden.

### Schritt 5: Abfrageintervall einstellen

Das Polling-Intervall bestimmt, wie oft Daten vom Controller abgerufen werden:

| Intervall | Vorteile | Nachteile |
|-----------|----------|-----------|
| 10–15 Sekunden | Sehr reaktiv | Höhere Last auf Controller |
| **20–30 Sekunden** | **Gute Balance (empfohlen)** | – |
| 45–60 Sekunden | Minimale Last | Weniger reaktiv |

---

## Erweiterte Einstellungen

Diese Einstellungen sind über **Einstellungen → Geräte & Dienste → Violet → Optionen** zugänglich.

| Option | Standard | Beschreibung |
|--------|---------|--------------|
| `Abfrageintervall` | 30s | Polling-Intervall in Sekunden |
| `Timeout` | 10s | Request-Timeout (80% für Verbindung) |
| `Retry-Versuche` | 3 | Anzahl Wiederholungen bei Fehler |
| `SSL verifizieren` | An | SSL-Zertifikat validieren |

---

## Nach der Installation

### Empfohlene erste Schritte

1. **Dashboard einrichten** – Erstelle eine neue Dashboard-Ansicht für deinen Pool
2. **Automationen testen** – Überprüfe ob Sensoren korrekte Werte zeigen
3. **Logs prüfen** – Stelle sicher, dass keine Fehler auftreten:
   ```
   Einstellungen → System → Protokolle → "violet" suchen
   ```

### Verfügbare Entities prüfen

Nach der Installation findest du alle Entities unter:
```
Einstellungen → Geräte & Dienste → Violet Pool Controller → [Gerät] → Entities
```

Oder direkt: **Entwicklerwerkzeuge → Status** → nach `violet_pool_controller` suchen

---

## Deinstallation

### Mit HACS

1. **HACS → Integrationen → Violet Pool Controller**
2. Klicke auf **"Entfernen"**
3. Gehe zu **Einstellungen → Geräte & Dienste**
4. Entferne die Violet Pool Controller Integration
5. Home Assistant neu starten

### Manuell

```bash
# Integration entfernen
rm -rf /config/custom_components/violet_pool_controller

# Home Assistant neu starten
docker restart homeassistant  # oder über HA-UI
```

> **Hinweis**: Deine Automatisierungen und Dashboard-Konfigurationen bleiben erhalten, funktionieren aber ohne das Addon nicht mehr.

---

## Upgrade von einer älteren Version

### Mit HACS (Automatisch)

1. **HACS → Integrationen** → "Violet Pool Controller" → **"Update"**
2. Home Assistant neu starten
3. Bei Breaking Changes: Integrations-Config prüfen

### Manuell

```bash
cd /config/custom_components/violet_pool_controller
git pull origin main
# oder ZIP erneut herunterladen und ersetzen
```

### Breaking Changes beachten

Vor jedem Update den **[Changelog](Changelog)** prüfen! Bei größeren Updates kann eine Neukonfiguration erforderlich sein.

---

## Häufige Installationsprobleme

| Problem | Ursache | Lösung |
|---------|---------|--------|
| Integration erscheint nicht | HA nicht neugestartet | HA neu starten |
| "Verbindung fehlgeschlagen" | Falsche IP oder Port | IP prüfen, `ping` testen |
| SSL-Fehler | Selbsigniertes Zertifikat | "SSL verifizieren" deaktivieren |
| "Duplicate Integration" | Gleiche IP bereits konfiguriert | Bestehende Integration entfernen |
| Keine Entities | Features nicht aktiviert | Setup-Assistent neu durchlaufen |

---

**Weiter:** [Konfiguration](Configuration) | [Sensoren](Sensors) | [Troubleshooting](Troubleshooting)
