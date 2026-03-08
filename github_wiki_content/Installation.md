# 📦 Installation - Violet Pool Controller

## ⚠️ WICHTIG - VOR DER INSTALLATION

### 🔒 Sicherheit & Haftungsausschluss

**Das Violet Pool Controller Addon steuert echte Poolausrüstung:**

- ⚠️ **Pumpen, Heizungen, Dosieranlagen können ferngesteuert werden**
- ⚠️ **Falsche Konfiguration kann zu Sachschäden führen**
- ⚠️ **Chemikalien können gefährlich sein bei falscher Handhabung**
- ⚠️ **Elektrische Anlagen müssen vorschriftsmäßig installiert sein**

**Bevor du installierst:**

✅ **Lies den vollständigen Haftungsausschluss**: [Konfigurationshilfe (DE)](../docs/help/configuration-guide.de.md#-sicherheit--haftung)
✅ **Verstehe alle Sicherheitsmechanismen**
✅ **Halte manuelle Not-Abschalter bereit**
✅ **Beachte alle Sicherheitsdatenblätter**
✅ **Konsultiere einen Fachbetrieb bei Unsicherheiten**

> **⚠️ Die Nutzung erfolgt auf eigene Verantwortung und Gefahr!**

---

## 📋 Systemvoraussetzungen

### Erforderlich:
- **Home Assistant**: 2025.12.0 oder neuer (getestet bis 2026.x)
- **Python**: 3.12+
- **Netzwerk**: Violet Pool Controller muss erreichbar sein
- **Browser**: Aktueller Browser mit JavaScript-Unterstützung

### Empfohlen:
- **SSL/TLS**: Zertifikat für sichere Kommunikation
- **Stromversorgung**: USV für Ausfallsicherheit
- **Backup**: Regelmäßige Konfigurationssicherungen

---

## 🚀 Installation via HACS (Empfohlen)

### Schritt 1: HACS öffnen

1. Öffne Home Assistant
2. Gehe zu **Einstellungen** → **Geräte & Dienste**
3. Klicke auf **HACS**
4. Klicke auf das **⋮ Menü** (drei Punkte oben rechts)
5. Wähle **Benutzerdefinierte Repositories**

### Schritt 2: Repository hinzufügen

```
URL: https://github.com/xerolux/violet-hass
Kategorie: Integration
```

1. Füge die URL ein
2. Wähle **Integration** als Kategorie
3. Klicke **Hinzufügen**

### Schritt 3: Integration installieren

1. Suche im HACS Store nach **"Violet Pool Controller"**
2. Klicke auf den **Integrationen** Tab
3. Scrolle bis zu **"Violet Pool Controller"**
4. Klicke auf **Installieren**
5. Warte bis die Installation abgeschlossen ist

### Schritt 4: Home Assistant neu starten

**WICHTIG**: Nach der Installation muss Home Assistant neu gestartet werden!

**Option A**: Über die Web-UI
- Klicke oben rechts auf **⋮ Menü**
- Wähle **Systemsteuerelemente**
- Klicke auf **Home Assistant neu starten**

**Option B**: Über die Kommandozeile
```bash
docker restart homeassistant
```

**Option C**: Über Supervisor (bei HAOS)
- Einstellungen → System → Supervisor
- Klicke auf **Restart**

---

## 🔧 Manuelle Installation (ohne HACS)

### Voraussetzungen

- SSH-Zugriff auf Home Assistant
- Dateimanager-Add-on (empfohlen) oder Shell-Access

### Installation

#### Methode 1: Git klonen

```bash
# In das custom_components Verzeichnis wechseln
cd /config/custom_components/

# Repository klonen
git clone https://github.com/xerolux/violet-hass.git violet_pool_controller
```

#### Methode 2: ZIP herunterladen

1. Lade die ZIP-Datei herunter: [violet-hass-main.zip](https://github.com/xerolux/violet-hass/archive/refs/heads/main.zip)
2. Entpacke die ZIP-Datei
3. Kopiere den Ordner `violet-hass-main/custom_components/violet_pool_controller` nach `/config/custom_components/`

### Nach der Installation

Home Assistant neu starten (siehe oben).

---

## ⚙️ Erstes Setup - Schritt für Schritt

### Schritt 1: Integration hinzufügen

1. Öffne Home Assistant
2. Gehe zu **Einstellungen** → **Geräte & Dienste**
3. Klicke auf **+ Integration hinzufügen**
4. Suche nach **"Violet Pool Controller"**
5. Klicke darauf

### Schritt 2: 🚨 DISCLAIMER (HAFTUNGSAUSSCHLUSS)

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

### Schritt 3: Verbindung konfigurieren

1. **Host IP-Adresse**: Die IP deines Violet Pool Controllers (z.B. `192.168.1.100`)
2. **Benutzername** (optional): Falls du einen hast (z.B. `admin`)
3. **Passwort** (optional): Falls du eines festgelegt hast
4. **SSL/TLS**: Aktivieren, wenn dein Controller HTTPS verwendet
5. **Geräte-ID**: (Optional) Bei mehreren Controllern (Standard: 1)

### Schritt 4: Pooldaten

1. **Poolvolumen**: In m³ (z.B. 40)
2. **Pool-Typ**: Aufenthaltsbecken, Sportbecken, etc.
3. **Desinfektionsmethode**: Chlor, Aktivsauerstoff, etc.

### Schritt 5: Features auswählen

Der Assistent zeigt alle verfügbaren Features:

- **Heizung**: Nutzt du einen Heizer?
- **Solar**: Solarthermie-Kollektor vorhanden?
- **pH-Kontrolle**: pH-Messung und -Dosierung?
- **Chlor-Kontrolle**: Chlor-Messung und -Dosierung?
- **Rückspülung**: Automatische Rückspülung?
- **Abdeckung**: Poolabdeckung steuerbar?
- **LED-Beleuchtung**: RGB-Lichter vorhanden?
- **PV-Überschuss**: Solaranlage mit Überschuss?

⚠️ **WICHTIG**: Wähle nur Features, die du wirklich hast! Falsche Konfiguration kann zu Fehlern führen.

### Schritt 6: Fertig!

Klicke auf **"Abschließen"** und die Integration wird eingerichtet.

---

## ✅ Erfolgreiche Installation

### Prüfen ob alles funktioniert

1. Öffne **Entwicklerwerkzeuge** → **Zustände**
2. Suche nach `violet_pool_controller`
3. Du solltest jetzt Entities sehen:
   - 🏊 Sensoren (Temperatur, pH, Chlor, etc.)
   - ⚙️ Schalter (Pumpe, Heizung, Licht, etc.)
   - 🌡️ Klima (Heizung, Solar)
   - 🔢 Zahlen (Sollwerte)

### Testen der Verbindung

1. Prüfe ob alle Sensoren Werte anzeigen
2. Teste einen Schalter (z.B. Licht ein/aus)
3. Öffne das **Violet Pool Controller** Dashboard (falls installiert)

---

## 🐛 Troubleshooting

### Installation schlägt fehl

**Problem**: Addon wird nicht in HACS gefunden
- **Lösung**: Prüfe ob die URL korrekt ist: `https://github.com/xerolux/violet-hass`
- **Lösung**: Prüfe ob du die richtige Kategorie ("Integration") gewählt hast

**Problem**: Nach Installation keine Entities
- **Lösung**: Home Assistant neu starten
- **Lösung**: Browser-Cache leeren (STRG + UMSCHALT + ENTF)

### Verbindung zum Controller schlägt fehl

**Problem**: "Keine Verbindung zum Controller"
- **Lösung**: Prüfe ob die IP-Adresse korrekt ist
- **Lösung**: Prüfe ob der Controller eingeschaltet ist
- **Lösung**: Prüfe ob du dich im selben Netzwerk befindest (kein Gast-WLAN!)
- **Lösung**: Firewall prüfen (Port 80/443)

**Problem**: "Authentifizierung fehlgeschlagen"
- **Lösung**: Benutzername und Passwort prüfen
- **Lösung**: SSL/TLS deaktivieren oder aktivieren (je nach Controller)

### Icons fehlen

**Problem**: Manche Entities haben keine Icons
- **Lösung**: Das ist normal bei Custom Integrations
- **Lösung**: Icons wurden in Version 1.x optimiert
- **Lösung**: Prüfe die [Icon-Referenz](Icon-Reference) für Details

---

## 📖 Nächste Schritte

Nach erfolgreicher Installation:

1. 📖 **Konfigurationshilfe lesen**: [DE](../docs/help/configuration-guide.de.md) | [EN](../docs/help/configuration-guide.en.md)
2. 🎛️ **Entities konfigurieren**: [Entities Guide](Entities)
3. 🤖 **Automationen erstellen**: [Services Guide](Services)
4. 🔧 **Troubleshooting**: [Troubleshooting](Troubleshooting)

---

## 💡 Tipps & Tricks

### Tipp 1: Backup vor dem ersten Start
Sichere deine Home Assistant Konfiguration vor der Installation!

### Tipp 2: Features schrittweise aktivieren
Fange mit den wichtigsten Features an (Pumpe, Heizung) und füge nach und nach mehr hinzu.

### Tipp 3: Test-Modus nutzen
Teste die Integration erst mit einfachen Automatisierungen, bevor du komplexe Szenarien einrichtest.

### Tipp 4: Dokumentation lesen
Die ausführliche Dokumentation spart Zeit und Fehler bei der Einrichtung!

---

## 🔐 Sicherheitshinweise

### ⚠️ WICHTIGE SICHERHEITSHINWEISE

**Elektrische Sicherheit:**
- ⚡ Alle Arbeiten an electrischen Anlagen nur von qualifiziertem Personal
- ⚡ Beachte die VDE- und DIN-Normen
- ⚡ Habe einen Not-Aus-Schalter für die Pumpe

**Chemische Sicherheit:**
- 🧪 Trage immer Handschuhe und Schutzbrille
- 🧪 Beachte die Sicherheitsdatenblätter
- 🧪 Sichere Chemikalien vor Kindern aufbewahren

**Betriebliche Sicherheit:**
- 🔒 Überwache deine Anlage regelmäßig persönlich
- 🔒 Verlasse dich nicht auf Automationen
- 🔒 Halte Notfallpläne bereit (manuelle Abschaltung)

---

## 📞 Hilfe & Support

### Probleme bei der Installation?

1. 📖 **Dokumentation durchsuchen**: [Wiki Home](Home)
2. 🔍 **Forum durchsuchen**: [Community Home Assistant](https://community.home-assistant.io/)
3. 🐛 **Issue melden**: [GitHub Issues](https://github.com/xerolux/violet-hass/issues)

### Community & Discord

- 💬 [Home Assistant Discord](https://discord.gg/cAwGJU3)
- 🌍 [Offizieller Discord Server](https://www.home-assistant.io/join-discord/)

---

**Viel Erfolg bei der Installation! 🎉**

Solltest du Probleme haben, schaue dich im [Troubleshooting](Troubleshooting) um oder öffne ein [GitHub Issue](https://github.com/xerolux/violet-hass/issues).
