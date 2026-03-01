# Changelog – Versionshistorie

> Alle wichtigen Änderungen am Violet Pool Controller Addon.

---

## [1.0.3-alpha.1] – 2026-02-28 🔴 ALPHA

### Neue Features

- **Quality Scale Progress:** Dokumentation des Fortschritts zur Quality Scale hinzugefügt (Gold Level ~85% abgeschlossen).

### Verbesserungen

- **Code Quality:** Type Hints vervollständigt (Bronze Level 100% abgeschlossen).
- **Fehlerbehebung:** Behebung von Config Flow Handler Problemen.
- **HA 2026 Kompatibilität:** Fixes für Home Assistant 2026 Kompatibilität und Abschluss von Gold Level Tests.
- **ZeroConf Discovery:** Fixes für ZeroConf Discovery (100% Tests erfolgreich).

### Dokumentation

- **Enhanced Documentation:** Verbesserte Fehlerbehandlung, Diagnostics und Dokumentation (Silver Level 100% abgeschlossen).

### Kompatibilität
- Getestet auf Home Assistant 2025.12.0+
- Vorbereitet für 2026.x Versionen
- aiohttp>=3.10.0 erforderlich

---

## [1.0.2] – 2026-02-26 ✅ STABLE

### Neue Features

**Diagnostic Service**
- Neuer Service: `export_diagnostic_logs`
- Exportiere bis zu 10.000 Log-Zeilen für Troubleshooting
- Optional in Datei speichern für Support-Tickets
- Mit Timestamps und flexibler Zeilenanzahl
- Export enthält nun auch installierte Komponenten und Home Assistant System-Infos.

### Verbesserungen

**Fehlerbehandlung**
- Bessere Recovery-Mechanismen bei Verbindungsverlust
- Erweiterte Logging-Fähigkeiten

**Wiki & Dokumentation**
- Aktualisierte Services-Dokumentation
- Neue Log-Export-Tipps in Troubleshooting
- Erweiterte SSL/TLS-Dokumentation

### Kompatibilität
- Getestet auf Home Assistant 2025.12.0+
- Vorbereitet für 2026.x Versionen
- aiohttp>=3.10.0 erforderlich

---

## [1.0.1] – 2026-02-22 ✅ STABLE

### Kritische Bugfixes

**Contact Sensor State Class**
- Sensoren gaben String-Werte (`'RELEASED'`/`'TRIGGERED'`) mit numerischer `state_class` zurück
- Fix: Runtime-Override in `VioletSensor.state_class` Property

**Weitere kritische Fixes in diesem Release:**
- Verbesserungen der Sensor-Anzeige
- Korrekturen bei Konfigurations-Updates
- Session-Management verbessert

### Upgraden auf 1.0.1

**HACS:**
1. HACS → Integrationen
2. „Violet Pool Controller" → Aktualisieren
3. Home Assistant neu starten

**Manuell:**
```bash
cd /config/custom_components
rm -rf violet_pool_controller
# ZIP von GitHub Release extrahieren
```

---

## [1.0.0] – 2026-02-22 ✅ STABLE

### Erstes stabiles Release!

#### Neue Features
- Vollständige Home Assistant Integration für Violet Pool Controller
- Multi-Controller Support (mehrere Pools gleichzeitig)
- Automatische Bereichszuweisung (Areas)

#### Plattformen
- **Sensor**: Temperaturen, pH, ORP, Chlor, Leitfähigkeit, AI1–AI8, Fehlercodes
- **Binary Sensor**: Digitaleingänge DI1–DI8, Alarme, Verbindungsstatus
- **Switch**: Pumpe, Heizung, Solar, pH±, Chlor, Flockmittel, DMX 1–8, Relais 1–8
- **Climate**: Poolheizung, Solarheizung (Thermostat)
- **Cover**: Poolabdeckung mit Position
- **Number**: Sollwerte für Temperatur, pH, ORP, Dosierung

#### Services
- `control_pump` – Pumpensteuerung mit Geschwindigkeit
- `smart_dosing` – Intelligente Chemikaliendosierung
- `manage_pv_surplus` – PV-Überschuss-Management
- `control_dmx_scenes` – DMX-Beleuchtungsszenen
- `set_light_color_pulse` – Lichtfarb-Pulse
- `manage_digital_rules` – Digitale Eingangsregeln
- `test_output` – Diagnose-Testmodus

#### Sicherheit
- Token-Bucket Rate Limiting
- Input Sanitization (XSS, SQL-Injection, Command-Injection)
- SSL/TLS Zertifikats-Verifikation (Standard: aktiv)
- Thread-Safe Locking mit dokumentierter Reihenfolge

#### Auto-Recovery
- Exponentielles Backoff: 10s → 300s
- Max. 10 Wiederholungsversuche
- Intelligentes Fehler-Logging (Throttling alle 5 Minuten)

#### Übersetzungen
- DE, EN, ES, FR, IT, NL, PL, PT, RU, ZH

---

## [0.2.1-beta.1] – 2025-11-20 🧪 BETA

### Multi-Controller Support

#### Neu
- Controller-Name-Feld beim Setup
- Automatische Bereichszuweisung (`suggested_area`)
- Verbesserte visuelle Trennung im Dashboard

#### Technisch
- Neue Konstante: `CONF_CONTROLLER_NAME`
- Device-Info verwendet `controller_name`
- Entry-Title zeigt Controller-Name

#### Abwärtskompatibilität
- Bestehende Installationen funktionieren weiter
- Default-Name: „Violet Pool Controller"

---

## [0.2.0] – 2025-10-15 🧪 BETA

### Große Umstrukturierung

#### Änderungen
- Modulare Konstanten (`const_api.py`, `const_devices.py`, `const_sensors.py`, `const_features.py`)
- Rate Limiter als separates Modul (`utils_rate_limiter.py`)
- Input Sanitizer (`utils_sanitizer.py`)
- Fehlercode-Mapping (`error_codes.py`)

#### Neue Entities
- Kalibrierungsverlauf-Sensoren
- Analogeingänge AI1–AI8
- Erweiterungs-Relais 1–8

---

## [0.1.0] – 2025-08-01 🧪 ALPHA

### Erster öffentlicher Release

#### Features
- Grundlegende HTTP-API-Kommunikation
- Sensor-Entities für Temperaturen und Chemiewerte
- Einfache Switch-Entities für Pumpe und Heizung
- Config Flow für Setup

---

## Breaking Changes

### 1.0.0 → 1.0.1

Keine Breaking Changes. Direktes Upgrade möglich.

### 0.2.x → 1.0.0

- Mindest-HA-Version: **2025.12.0** (vorher 2024.12.0)
- Python: **3.12+** erforderlich
- Type Annotations: `X | None` statt `Optional[X]`

### 0.1.x → 0.2.x

- Konstanten reorganisiert (Import aus `const.py` weiterhin möglich)
- Entity-IDs können sich geändert haben (Neuinstallation empfohlen)

---

## Upgrade-Anleitung

### Via HACS (empfohlen)

1. HACS → Integrationen
2. Violet Pool Controller finden
3. „Aktualisieren" klicken
4. HA neu starten
5. Einstellungen → Geräte & Dienste → Integration prüfen

### Manuell

```bash
# Backup erstellen!
cp -r /config/custom_components/violet_pool_controller \
       /config/backup_violet_$(date +%Y%m%d)

# Neue Version installieren
cd /config/custom_components
rm -rf violet_pool_controller
# ZIP entpacken oder git pull

# HA neu starten
```

---

## Links

- [GitHub Releases](https://github.com/Xerolux/violet-hass/releases)
- [Vollständiger Changelog auf GitHub](https://github.com/Xerolux/violet-hass/blob/main/docs/CHANGELOG.md)
- [Bug melden](https://github.com/Xerolux/violet-hass/issues/new?template=bug_report.md)
- [Feature anfragen](https://github.com/Xerolux/violet-hass/issues/new?template=feature_request.md)

---

*Zurück: [API-Referenz](API-Reference) | Zurück: [Home](Home)*
