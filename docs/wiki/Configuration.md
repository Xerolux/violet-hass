# ⚙️ Konfiguration

> Alle Konfigurationsoptionen erklärt – von Basis-Setup bis zu erweiterten Einstellungen.

---

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

## Konfigurationsübersicht

Die Violet Pool Controller Integration wird vollständig über die Home Assistant UI konfiguriert – keine manuelle YAML-Konfiguration notwendig.

```
Einstellungen → Geräte & Dienste → Violet Pool Controller → Optionen
```

---

## Verbindungseinstellungen

### Host-Konfiguration

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|---------|--------------|
| `host` | String | – | IP-Adresse oder Hostname des Controllers |
| `port` | Integer | 80 | TCP-Port (80 für HTTP, 443 für HTTPS) |
| `use_ssl` | Boolean | False | HTTPS statt HTTP verwenden |
| `verify_ssl` | Boolean | True | SSL-Zertifikat validieren |

**Beispiele für Host-Konfiguration:**

```
HTTP (Standard):     192.168.1.100:80
HTTPS validiert:     192.168.1.100:443  (verify_ssl=True)
HTTPS selbsigniert:  192.168.1.100:443  (verify_ssl=False)
Hostname:            violet.local:80
```

> **Sicherheitshinweis**: `verify_ssl=False` nur in vertrauenswürdigen lokalen Netzwerken verwenden!

### Authentifizierung

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `username` | String | API-Benutzername (leer lassen falls keine Auth) |
| `password` | String | API-Passwort |

Zugangsdaten werden verschlüsselt in der Home Assistant Konfiguration gespeichert.

---

## Poll-Einstellungen

### Abfrageintervall

```
Einstellungen → Geräte & Dienste → Violet → Optionen → Abfrageintervall
```

| Wert | Verhalten | Empfohlen für |
|------|-----------|---------------|
| 10s | Sehr reaktiv, hohe Controller-Last | Debugging |
| **20s** | **Standard-Empfehlung** | Die meisten Nutzer |
| 30s | Gute Balance | Mehrere Controller |
| 45–60s | Niedrige Last, weniger reaktiv | Schwache Hardware/Netzwerk |

Der Coordinator fragt alle Sensoren in einem einzelnen Request ab (`GET /getReadings?ALL`), um Controller-Last zu minimieren.

### Timeout

| Parameter | Standard | Beschreibung |
|-----------|---------|--------------|
| `timeout` | 10s | Gesamter Request-Timeout |
| Verbindungs-Timeout | 8s (80%) | Timeout für TCP-Verbindungsaufbau |

Bei langsamen Netzwerken auf 15–20s erhöhen.

### Retry-Logik

| Parameter | Standard | Beschreibung |
|-----------|---------|--------------|
| `retry_attempts` | 3 | Wiederholungen bei Fehler |
| Backoff | Exponentiell | 2s → 4s → 8s zwischen Versuchen |

---

## Feature-Konfiguration

### Features aktivieren/deaktivieren

Features werden im Setup-Flow konfiguriert und bestimmen, welche Entities erstellt werden:

```
Einstellungen → Geräte & Dienste → Violet → Optionen → Features neu konfigurieren
```

**Verfügbare Features:**

```
┌─────────────────────────────────────────────────────────┐
│                    FEATURE FLAGS                        │
├─────────────────┬───────────────────────────────────────┤
│ PUMP            │ Filterpumpe (immer aktiv)             │
│ HEATER          │ Pool-Heizung / Wärmetauscher           │
│ SOLAR           │ Solarkollektor                        │
│ PV_SURPLUS      │ PV-Überschuss-Modus                   │
│ DOSING_PH_MINUS │ pH- Dosierpumpe                       │
│ DOSING_PH_PLUS  │ pH+ Dosierpumpe                       │
│ DOSING_CHLORINE │ Chlor-Dosierpumpe                     │
│ DOSING_FLOCCULANT│ Flockungs-Dosierpumpe                │
│ DMX             │ DMX-Beleuchtungssteuerung (1–8)       │
│ DIGITAL_INPUTS  │ Digitale Eingänge DI1–DI8             │
│ COVER           │ Pool-Abdeckung                        │
│ EXTENSION_RELAYS│ Erweiterungs-Relais REL1–REL8         │
│ BACKWASH        │ Rückspülung                           │
└─────────────────┴───────────────────────────────────────┘
```

---

## Logging-Konfiguration

### Debug-Logging aktivieren

In `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.violet_pool_controller: debug
    aiohttp: info
```

### Logging reduzieren (Performance)

```yaml
logger:
  logs:
    custom_components.violet_pool_controller: warning
```

### Nur Fehler loggen

```yaml
logger:
  logs:
    custom_components.violet_pool_controller: error
```

---

## Controller-Name & Multi-Controller

Für Installationen mit mehreren Controllern ist der **Controller-Name** wichtig:

```
Einstellungen → Integration hinzufügen → Controller-Name: "Außenpool"
```

| Empfehlung | Beispiel |
|-----------|---------|
| Eindeutig & beschreibend | `Außenpool`, `Whirlpool`, `Hallenbad` |
| Kurz (max. 2–3 Wörter) | `Pool 1`, `Badeteich` |
| Nicht generisch | ~~"Pool"~~, ~~"Controller"~~ |

Der Controller-Name bestimmt:
- Den **Gerätenamen** in HA
- Den **empfohlenen Bereich** (automatische Gruppierung)
- Den **Entity-Prefix** (bei eindeutiger Benennung)

→ Mehr dazu: **[Multi-Controller Guide](Multi-Controller)**

---

## Dashboard-Konfiguration

### Automatische Bereiche

Home Assistant erstellt automatisch einen Bereich basierend auf dem Controller-Namen. Alle Entities werden diesem Bereich zugeordnet.

### Empfohlene Dashboard-Karten

**Sensor-Übersicht:**
```yaml
type: entities
title: Pool Wasserchemie
entities:
  - entity: sensor.violet_water_temperature
    name: Wassertemperatur
  - entity: sensor.violet_ph_value
    name: pH-Wert
  - entity: sensor.violet_orp_value
    name: ORP/Redox
  - entity: sensor.violet_chlorine
    name: Chlorgehalt
```

**Steuerung-Karte:**
```yaml
type: glance
title: Pool Steuerung
entities:
  - entity: switch.violet_pump
    name: Pumpe
  - entity: switch.violet_heater
    name: Heizung
  - entity: switch.violet_solar
    name: Solar
  - entity: cover.violet_cover
    name: Abdeckung
```

**Thermostat-Karte:**
```yaml
type: thermostat
entity: climate.violet_heater
name: Pool Heizung
```

---

## Konfigurationsvalidierung

Die Integration validiert alle Eingaben beim Setup und zeigt klare Fehlermeldungen:

| Fehler | Ursache | Lösung |
|--------|---------|--------|
| `cannot_connect` | Controller nicht erreichbar | IP/Port prüfen |
| `invalid_auth` | Falsches Passwort | Zugangsdaten prüfen |
| `already_configured` | Gleiche IP bereits konfiguriert | Bestehende Integration entfernen |
| `ssl_error` | Zertifikatsproblem | `verify_ssl` deaktivieren |

---

## Konfiguration sichern

### Backup erstellen (vor Änderungen)

```
Einstellungen → System → Sicherungen → Sicherung erstellen
```

### Konfiguration exportieren

Die Integration speichert ihre Konfiguration in:
```
/config/.storage/core.config_entries
```

Dieses File wird automatisch durch HA-Backups gesichert.

---

## Reset & Neukonfiguration

### Integration neu konfigurieren

1. **Einstellungen → Geräte & Dienste**
2. Violet Pool Controller auswählen
3. **"⋮" → "Neu konfigurieren"** (oder "Optionen")
4. Änderungen vornehmen
5. Speichern

### Integration vollständig entfernen und neu hinzufügen

1. **Einstellungen → Geräte & Dienste → Violet**
2. **"⋮" → "Löschen"**
3. Neu hinzufügen wie bei der [Erstinstallation](Installation-and-Setup)

> **Warnung**: Beim Löschen und Neuerstellen werden Entity-IDs neu generiert – ggf. Automatisierungen/Dashboard-Karten anpassen!

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

---

**Weiter:** [Sensoren](Sensors) | [Device States](Device-States) | [Services](Services)
