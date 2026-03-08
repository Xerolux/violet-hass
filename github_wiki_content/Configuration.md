# ⚙️ Konfiguration - Violet Pool Controller

## 🚨 SICHERHEIT & HAFTUNG (BITTE ZUERST LESEN!)

### ⚠️ WICHTIGE SICHERHEITSHINWEISE

**Das Violet Pool Controller Addon steuert echte Poolausrüstung:**

- ⚠️ **Pumpen, Heizungen, Dosieranlagen können ferngesteuert werden**
- ⚠️ **Falsche Konfiguration kann zu Sachschäden führen**
- ⚠️ **Chemikalien können gefährlich sein bei falscher Handhabung**
- ⚠️ **Elektrische Anlagen müssen vorschriftsmäßig installiert sein**

### 🔒 DEINE VERANTWORTUNG

**Bevor du die Integration konfigurierst:**

✅ **Lies den vollständigen Haftungsausschluss**: [📖 Konfigurationshilfe (DE)](../docs/help/configuration-guide.de.md#-sicherheit--haftung)
✅ **Verstehe alle Sicherheitsmechanismen**
✅ **Halte manuelle Not-Abschalter bereit**
✅ **Beachte alle Sicherheitsdatenblätter**
✅ **Konsultiere einen Fachbetrieb bei Unsicherheiten**

> **⚠️ Die Nutzung erfolgt auf eigene Verantwortung und Gefahr!**

---

## 📋 Inhaltsverzeichnis

1. [Ersteinrichtung](#-ersteinrichtung)
2. [Verbindungseinstellungen](#-verbindungseinstellungen)
3. [Pooldaten](#-pooldaten)
4. [Features auswählen](#-features-auswählen)
5. [Erweiterte Konfiguration](#-erweiterte-konfiguration)
6. [Multi-Controller Setup](#-multi-controller-setup)
7. [Troubleshooting](#-troubleshooting)

---

## 🚀 Ersteinrichtung

### Schritt 1: Integration hinzufügen

1. Öffne Home Assistant
2. Gehe zu **Einstellungen** → **Geräte & Dienste**
3. Klicke auf **+ Integration hinzufügen**
4. Suche nach **"Violet Pool Controller"**
5. Klicke darauf

### Schritt 2: 🚨 DISCLAIMER (HAFTUNGSAUSSCHLUSS)

⚠️ **SEHR WICHTIG - BITTE SORGFÄLTIG LESEN!**

Du wirst einen **umfassenden Haftungsausschluss** sehen mit:

- **⚠️ Sicherheitswarnung**: Alle Risiken bei der Nutzung
- **🔒 Deine Verantwortung**: Was du tun musst
- **⚖️ Haftungsausschluss**: Keine Gewährleistung
- **📖 Dokumentation**: Links zur ausführlichen Hilfe

**Du musst:**
1. ✅ Den gesamten Text lesen
2. ✅ Das Häkchen bei **"Ich akzeptiere"** setzen
3. ✅ **"Bestätigen"** klicken

**Ohne Bestätigung kannst du die Integration nicht einrichten!**

---

## 🔌 Verbindungseinstellungen

### Host IP-Adresse

Die IP-Adresse deines Violet Pool Controllers im lokalen Netzwerk.

**Beispiele:**
- `192.168.1.100` (Standard)
- `192.168.178.50` (FRITZ!Box)
- `10.0.0.100` (Unternehmensnetzwerk)

**So findest du die IP:**
1. Violet Pool Controller Display anschauen
2. Netzwerk-Einstellungen öffnen
3. IP-Adresse notieren

**Oder über Router:**
1. Router-Webinterface öffnen (z.B. `fritz.box`)
2. Geräteliste / DHCP suchen
3. "Violet" oder "Pool" suchen
4. IP-Adresse kopieren

### Benutzername & Passwort

**Optional** - Nur wenn du auf dem Controller einen benutzerdefinierten Login eingerichtet hast.

**Standard:**
- Benutzername: Leer lassen (oder `admin` bei älteren Firmware-Versionen)
- Passwort: Leer lassen (oder Standardpasswort prüfen)

**Empfehlung:**
- Richte auf dem Controller einen dedizierten Benutzer ein
- Verwende ein sicheres Passwort
- Aktiviere SSL/TLS für verschlüsselte Kommunikation

### SSL/TLS

Aktivieren, wenn dein Controller HTTPS verwendet.

**Wann aktivieren?**
- ✅ Du hast ein Zertifikat auf dem Controller eingerichtet
- ✅ Du erreichst den Controller über `https://`
- ❌ Du erreichst den Controller nur über `http://`

**Vorteile:**
- 🔒 Verschlüsselte Kommunikation
- 🔒 Schutz vor Abhören
- 🔒 Sichere Authentifizierung

### Geräte-ID

Optional - Bei mehreren Controllern in einer Home Assistant Instanz.

**Beispiele:**
- `1` (Standard, erster Controller)
- `2` (zweiter Controller, z.B. Hauptpool + Whirlpool)
- `3` (dritter Controller)

**Wann verwenden?**
- Du hast mehrere Violet Pool Controller
- Du möchtest getrennte Entities pro Pool
- Du möchtest eindeutige Namen pro Controller

**Ergebnis:**
- Controller 1: `sensor.violet_pool_controller_1_pool_water_temp`
- Controller 2: `sensor.violet_pool_controller_2_pool_water_temp`

---

## 🏊 Pooldaten

### Poolvolumen

Das Wasservolumen deines Pools in Kubikmetern (m³).

**Beispiele:**
- Kleinpool: 20 m³
- Standardpool: 40 m³
- Großpool: 80 m³
- Olympiabecken: 2500 m³

**So berechnest du das Volumen:**

**Rechteckiger Pool:**
```
Länge (m) × Breite (m) × durchschnittliche Tiefe (m) = Volumen (m³)
```

Beispiel: 8 × 4 × 1.5 = 48 m³

**Runder Pool:**
```
Radius (m) × Radius (m) × 3.14159 × durchschnittliche Tiefe (m) = Volumen (m³)
```

Beispiel: 3 × 3 × 3.14159 × 1.5 = 42.4 m³

**Warum ist das wichtig?**
- 💊 Berechnung der Chemikalien-Dosierung
- ⏱️ Bestimmung der Filterlaufzeit
- 🌡️ Heizzeit-Berechnung
- 💧 Wasseraustausch-Berechnung

### Pool-Typ

Wähle den Typ deines Pools aus der Liste.

**Verfügbare Optionen:**
- Aufenthaltsbecken (Standard)
- Sportbecken
- Therapiebecken
- Whirlpool
- Kinderbecken
- Plunge Pool
- Kombibecken

**Auswirkungen:**
- Empfohlene Temperatur-Bereiche
- Filterzyklus-Empfehlungen
- Chemikalien-Grenzwerte
- Heizungsstrategien

### Desinfektionsmethode

Wähle die primäre Methode zur Wasserdesinfektion.

**Optionen:**

| Methode | Beschreibung | Vorteile | Nachteile |
|---------|-------------|----------|-----------|
| **Chlor** | Klassisches Chlor | Effektiv, günstig | Geruch, Hautreizung |
| **Aktivsauerstoff** | Sauerstoff-basiert | Geruchlos, sanft | Teurer, weniger effektiv |
| **Elektrolyse**** | Salzaufbereitung | Automatisch, sanft | Initialkosten |
| **UV + Chlor** | UV-Licht + Chlor | Weniger Chlor, hochwirksam | Wartungsaufwand |
| **Mineral** | Mineralien-basiert | Sanft, natürlich | Ergänzend benötigt |
| **Andere** | Andere Methode | - | - |

**Auswirkungen:**
- Empfohlene Chlorgrenzwerte
- pH-Optimalbereiche
- Automatische Dosierungs-Strategie

---

## ✨ Features auswählen

Der Assistent zeigt alle verfügbaren Features, die dein Controller unterstützt.

### Übersicht aller Features

| Feature | Beschreibung | Wann aktivieren? |
|---------|-------------|-------------------|
| **🔥 Heizung** | Elektrische Heizer oder Wärmepumpen | Du hast einen Heizer |
| **☀️ Solar** | Solarthermie-Kollektoren | Du hast Solar auf dem Dach |
| **🧪 pH-Kontrolle** | pH-Messung und -Dosierung | Du hast pH-Sensoren und -Dosierer |
| **🧪 Chlor-Kontrolle** | Chlor-Messung und -Dosierung | Du hast Chlor-Sensor und -Dosierer |
| **💧 Flockung** | automatische Flockmittel-Dosierung | Du hast Flockmittel-Dosierer |
| **🔄 Rückspülung** | automatische Rückspülung | Du hast ein 6-Wege-Ventil |
| **☀️ PV-Überschuss** | Solarheizung bei PV-Überschuss | Du hast Photovoltaik |
| **💧 Filterpumpe** | Poolpumpe steuern | Immer aktivieren! |
| **📊 Wasserstand** | Wasserstand-Überwachung | Du habe Wasserstand-Sensor |
| **🚰 Wassernachfüllung** | automatische Nachfüllung | Du haben elektroventil |
| **💡 LED-Beleuchtung** | RGB-Lichter steuern | Du hast Poolbeleuchtung |
| **🔌 Digitale Eingänge** | Zusätzliche Sensoren | Du hast Erweiterungen |
| **🔌 Erweiterungs-Ausgänge** | Zusätzliche Relais | Du hast Erweiterungskarten |

### WICHTIG: Nur vorhandene Features aktivieren!

⚠️ **Aktiviere nur Features, die du wirklich hast!**

**Falsche Konfiguration kann zu:**
- ❌ Fehlern in den Logs
- ❌ Non-responding Entities
- ❌ Verwirrung im Dashboard
- ❌ Falschen Automationen

**Beispiele:**

✅ **Korrigiert:**
- Du hast Solarthermie → Aktiviere "Solarabsorber"
- Du hast pH-Dosierung → Aktiviere "pH-Kontrolle"
- Du hast KEINE LED → Lasse "LED-Beleuchtung" deaktiviert

❌ **Falsch:**
- Du hast KEIN Solar → Aktiviere "Solarabsorber" nicht!
- Du hast KEIN Heizung → Aktiviere "Heizung" nicht!
- Du hast KEIN Chlor-Dosierer → Aktiviere "Chlor-Kontrolle" nicht!

### Empfohlene Start-Konfiguration

**Für Standard-Pools:**
- ✅ Filterpumpe
- ✅ Heizung (wenn vorhanden)
- ✅ pH-Kontrolle (wenn vorhanden)
- ✅ Chlor-Kontrolle (wenn vorhanden)
- ❌ Alles andere deaktiviert (wenn nicht vorhanden)

**Nach und nach erweitern:**
1. Starte mit den wichtigsten Features
2. Teste 1-2 Wochen
3. Füge weitere Features hinzu
4. Bei Problemen: Feature deaktivieren

---

## 🔧 Erweiterte Konfiguration

### Zeitpläne und Automationen

Nach der Einrichtung kannst du Zeitpläne erstellen:

**Beispiel: Pumpe automatisch steuern**
```yaml
alias: Pool - Pumpe morgens starten
description: Startet die Pumpe jeden Tag um 6:00 Uhr
trigger:
  - platform: time
    at: "06:00:00"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.violet_pool_controller_pump
```

**Beispiel: Heizung basierend auf Temperatur**
```yaml
alias: Pool - Heizung bei kaltem Wasser
description: Heizung einschalten wenn Wasser unter 25°C
trigger:
  - platform: numeric_state
    entity_id: sensor.violet_pool_controller_onewire1_value
    below: 25
action:
  - service: switch.turn_on
    target:
      entity_id: switch.violet_pool_controller_heater
```

### Szenarien

**Party-Modus:**
```yaml
alias: Pool - Party Modus
description: Alles an für Poolparty
sequence:
  - service: switch.turn_on
    target:
      entity_id:
        - switch.violet_pool_controller_light
        - switch.violet_pool_controller_pump
  - service: climate.set_temperature
    target:
      entity_id: climate.violet_pool_controller_heater
    data:
      temperature: 28
```

**Eco-Modus:**
```yaml
alias: Pool - Eco Modus
description: Energie sparen wenn Pool nicht genutzt wird
sequence:
  - service: select.select_option
    target:
      entity_id: select.violet_pool_controller_heater_mode
    data:
      option: "Aus"
  - service: switch.turn_off
    target:
      entity_id: switch.violet_pool_controller_light
```

---

## 🏘️ Multi-Controller Setup

### Mehrere Pools in einer HA-Instanz

Du kannst mehrere Violet Pool Controller in Home Assistant betreiben.

**Beispiele:**
- Hauptpool + Whirlpool
- Pool + Zisterne
- Innenpool + Außenpool

### Einrichtung

**Erster Controller (Standard):**
1. Integration hinzufügen
2. Host: `192.168.1.100`
3. Geräte-ID: `1` (oder leer lassen)
4. Features auswählen
5. Einrichten

**Zweiter Controller:**
1. Nochmal Integration hinzufügen
2. Host: `192.168.1.101`
3. Geräte-ID: `2`
4. Features auswählen
5. Einrichten

**Ergebnis:**
```
sensor.violet_pool_controller_1_pool_water_temp
sensor.violet_pool_controller_2_pool_water_temp
switch.violet_pool_controller_1_pump
switch.violet_pool_controller_2_pump
```

### Tipps für Multi-Controller

**Naming:**
- Benenne die Controller im Integration-Menu um
- "Hauptpool" statt "Violet Pool Controller 1"
- "Whirlpool" statt "Violet Pool Controller 2"

**Automationen:**
- Nutze die Gerät-ID in Automationen
- Trenne die Pools logisch
- Erstelle separate Dashboards

---

## 🐛 Troubleshooting

### Verbindung kann nicht hergestellt werden

**Fehler: "Keine Verbindung zum Controller"**

**Lösungen:**
1. **IP prüfen:**
   ```bash
   ping 192.168.1.100
   ```
2. **Port prüfen:**
   ```bash
   # HTTP
   curl http://192.168.1.100
   # HTTPS
   curl https://192.168.1.100
   ```
3. **Netzwerk prüfen:**
   - Bist du im gleichen Netzwerk?
   - Kein Gast-WLAN?
   - Firewall blockiert nicht?
4. **SSL/TLS umschalten:**
   - Aktivieren oder deaktivieren
   - Je nach Controller-Konfiguration

### Authentifizierung fehlgeschlagen

**Fehler: "Authentifizierung fehlgeschlagen"**

**Lösungen:**
1. Benutzername und Passwort prüfen
2. Groß-/Kleinschreibung beachten
3. Leerzeichen entfernen
4. Auf dem Controller prüfen:
   - Existiert der Benutzer?
   - Ist das Passwort korrekt?
5. SSL/TLS umschalten

### Entities fehlen nach Einrichtung

**Problem: Nicht alle Entities sind sichtbar**

**Lösungen:**
1. **Home Assistant neu starten:**
   - Einstellungen → System → Neustart
2. **Browser-Cache leeren:**
   - STRG + UMSCHALT + ENTF
3. **Entity-Registry prüfen:**
   - Einstellungen → Geräte & Dienste → Entities
   - Suche nach "violet_pool_controller"
4. **Features deaktivieren:**
   - Entferne die Integration
   - Füge sie wieder hinzu
   - Wähle nur vorhandene Features

### Fehlerhafte Werte

**Problem: Sensoren zeigen unplausible Werte**

**Beispiele:**
- Temperatur: -999°C
- pH: 0.0
- Druck: 9999 bar

**Lösungen:**
1. **Controller-Logs prüfen:**
   - Violet Controller Webinterface öffnen
   - Logs / Diagnose
   - Nach Fehlern suchen
2. **Sensor-Verbindung prüfen:**
   - Sind alle Sensoren angeschlossen?
   - Kabelverbindung prüfen
   - Stromversorgung prüfen
3. **Integration neu starten:**
   - Einstellungen → Geräte & Dienste → Violet Pool Controller
   - "..." → Neu laden
4. **Home Assistant Logs prüfen:**
   - Einstellungen → System → Logs
   - Nach Fehlern suchen

### Hilfe bekommen

**Probleme die du nicht lösen kannst:**

1. 📖 **Dokumentation lesen:**
   - [Konfigurationshilfe (DE)](../docs/help/configuration-guide.de.md)
   - [Entities Guide](Entities)
   - [Troubleshooting](Troubleshooting)

2. 🔍 **Forum durchsuchen:**
   - [Community Home Assistant](https://community.home-assistant.io/)
   - Suche nach "Violet Pool Controller"

3. 🐛 **Issue melden:**
   - [GitHub Issues](https://github.com/xerolux/violet-hass/issues)
   - Folgende Informationen anhängen:
     - Home Assistant Version
     - Violet Pool Controller Firmware
     - Genauer Fehlerbeschreibung
     - Logs (entsprechende Teile)
     - Konfiguration (ohne Passwörter!)

---

## 📖 Nächste Schritte

Nach erfolgreicher Konfiguration:

1. 🎛️ **Entities erkunden**: [Entities Guide](Entities)
2. 🤖 **Automationen erstellen**: [Services Guide](Services)
3. 🐛 **Probleme lösen**: [Troubleshooting](Troubleshooting)
4. 📊 **Dashboard einrichten**: [Dashboard Guide](Dashboard)

---

## 🔐 Sicherheitshinweise (Wiederholung)

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

### Probleme bei der Konfiguration?

1. 📖 **Dokumentation durchsuchen**: [Wiki Home](Home)
2. 🔍 **Forum durchsuchen**: [Community Home Assistant](https://community.home-assistant.io/)
3. 🐛 **Issue melden**: [GitHub Issues](https://github.com/xerolux/violet-hass/issues)

### Community & Discord

- 💬 [Home Assistant Discord](https://discord.gg/cAwGJU3)
- 🌍 [Offizieller Discord Server](https://www.home-assistant.io/join-discord/)

---

**Viel Erfolg bei der Konfiguration! 🎉**

Solltest du Probleme haben, schaue im [Troubleshooting](Troubleshooting) nach oder öffne ein [GitHub Issue](https://github.com/xerolux/violet-hass/issues).
