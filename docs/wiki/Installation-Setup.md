# 📦 Installation & Setup

Schritt-für-Schritt Anleitung zur Installation und erstem Setup des Violet Pool Controller Addons.

## Systemanforderungen

- **Home Assistant Version**: 2025.12.0 oder neuer
- **Python**: 3.12+
- **Netzwerk**: Violet Pool Controller im lokalen Netzwerk erreichbar
- **Speicher**: Minimal (Integration benötigt <10 MB)

## HACS Installation (Empfohlen)

### Schritt 1: HACS öffnen
1. Home Assistant → **Einstellungen**
2. **Geräte & Dienste** → HACS (in der Sidebar)
3. ⋮ (Menü oben rechts) → **Benutzerdefinierte Repositories**

### Schritt 2: Repository hinzufügen
```
URL: https://github.com/xerolux/violet-hass
Kategorie: Integration
```
Dann "Hinzufügen" klicken.

### Schritt 3: Integration installieren
1. Nach **"Violet Pool Controller"** suchen
2. Auf die Integration klicken
3. **"Installieren"** klicken
4. **Home Assistant neu starten** (wichtig!)

Neu starten über:
- Web-UI: ⋮ → Systemsteuerelemente → Home Assistant neu starten
- Docker: `docker restart homeassistant`

### Schritt 4: Integration aktivieren
1. **Einstellungen** → **Geräte & Dienste**
2. **"Integration hinzufügen"** (+ Button rechts unten)
3. **"Violet Pool Controller"** suchen
4. Aus der Liste auswählen und hinzufügen
5. **Host IP-Adresse** eingeben (z.B. `192.168.1.100`)

## Manuelle Installation

Für Entwickler oder ohne HACS:

```bash
# Option 1: Git Clone
cd /config/custom_components/
git clone https://github.com/xerolux/violet-hass.git violet_pool_controller

# Option 2: ZIP Download
cd /config
wget https://github.com/xerolux/violet-hass/archive/main.zip
unzip main.zip
mv violet-hass-main/custom_components/violet_pool_controller .
```

Danach Home Assistant **neu starten**.

## Erstes Setup

### Konfigurationsflow starten

1. **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **"Integration hinzufügen"**
3. Suche nach **"Violet Pool Controller"**
4. Wähle es aus

### Schritt 1: Host IP-Adresse

Gib die **IP-Adresse deines Controllers** ein:

```
Beispiele:
192.168.1.100
192.168.0.50
10.0.0.25
```

**Wie finde ich die IP-Adresse?**

1. Öffne dein **Router-Admin-Interface** (meist 192.168.1.1)
2. Schaue unter "Verbundene Geräte"
3. Suche nach "Violet" oder ähnlich
4. Notiere die IP

Oder im Terminal:
```bash
ping violet.local    # Falls mDNS aktiviert
ping violet          # Mit Hostname
```

### Schritt 2: Authentifizierung (Optional)

Falls dein Controller Benutzername/Passwort erfordert:

- **Benutzername**: `admin` (normalerweise)
- **Passwort**: Dein Controller-Passwort
- **SSL verwenden**: Nur wenn HTTPS erforderlich

### Schritt 3: Features auswählen

Der Assistent zeigt folgende Optionen. Aktiviere nur Features, die wirklich vorhanden sind:

| Feature | Bedeutung | Aktivieren wenn... |
|---------|-----------|-------------------|
| **Heizung** | Poolheizer | Heizer ist angeschlossen |
| **Solar** | Solarthermie | Solarthermie-Kollektor vorhanden |
| **Digitale Eingänge** | DI1-DI8 | Diese sind konfiguriert |
| **PV-Überschuss** | Solar-Nutzung | Solaranlage mit Überschuss vorhanden |
| **Weitere...** | Rückspülung, Dosierung | Komponenten vorhanden |

> **Tipp**: Nur wirklich verwendete Features aktivieren = bessere Performance!

### Schritt 4: Sensor-Auswahl

Die Integration prüft deinen Controller und zeigt verfügbare Sensoren:

- **Wasserchemie**: pH, ORP, Chlorin
- **Temperaturen**: Pool, Umgebung, Solar
- **System-Status**: Druck, Wasserstände, Laufzeiten
- **Laufzeitstatistiken**: Pumpen, Heizer, Energieverbrauch

> **Hinweis**: Wenn nichts ausgewählt wird, erstellt die Integration automatisch alle Sensoren. Das ist kompatibel mit bestehenden Installationen.

### Schritt 5: Abfrage-Intervall

Das ist die Frequenz, wie oft HA den Controller abfragt:

| Wert | Empfehlung | Verwendung |
|------|-----------|-----------|
| 10s | ⚠️ Sehr schnell | Nur für spezielle Anwendungen |
| **20-30s** | ✅ Standard | Die meisten Pools |
| 45-60s | 🟢 Sparsam | Große Pools, weniger wichtig |
| 300s | Sehr langsam | Archiv-Daten |

Typischerweise ist **30 Sekunden** ein guter Kompromiss zwischen Reaktionsfähigkeit und Systembelastung.

## Nach dem Setup

Nach dem ersten Setup solltest du:

1. ✅ Dein **Dashboard** öffnen
2. ✅ Die **Entitäten** überprüfen
3. ✅ Erste **Test-Automatisierungen** erstellen
4. ✅ **Sicherung erstellen** (Einstellungen → Sicherungen)

Die Integration ist jetzt betriebsbereit!

## Erste Schritte

### 1. Dashboard erstellen
Ein vorgefertigtes Dashboard liegt im Repository:
- Datei: `Dashboard/pool-dashboard.yaml`
- Kopiere nach `/config/`
- Importiere in HA → Einstellungen → Dashboards

### 2. Erste Automatisierung
Erstelle eine einfache Test-Automatisierung:
```yaml
automation:
  - alias: "Test: Pumpe einschalten"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.violet_pump
```

### 3. Benachrichtigungen einrichten
Überwache wichtige Werte:
```yaml
automation:
  - alias: "Pool zu warm!"
    trigger:
      - platform: numeric_state
        entity_id: sensor.violet_pool_temperature
        above: 32
    action:
      - service: notify.notify
        data:
          message: "Pool ist {{ states('sensor.violet_pool_temperature') }}°C!"
```

## Nächste Schritte

- 📖 Lies mehr: [Device States](Device-States) - Verstehe die 7 Device States
- 🤖 Automatisierungen: [Services](Services) - Verfügbare Services
- 🚨 Probleme: [Troubleshooting](Troubleshooting) - Häufige Fehler
