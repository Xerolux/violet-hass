# Testing Checkliste für Violet Pool Controller Integration

## ✅ Automatische Checks (Bereits durchgeführt)

- [x] **Ruff Linting**: Keine Code-Qualitätsprobleme
- [x] **MyPy Type Checking**: Alle Type-Errors behoben
- [x] **Python Syntax**: Alle `.py` Dateien syntaktisch korrekt
- [x] **manifest.json**: Valides JSON, alle Pflichtfelder vorhanden
- [x] **services.yaml**: Valides YAML, 7 Services definiert
- [x] **Übersetzungen**: 10 Sprachen (de, en, es, fr, it, nl, pl, pt, ru, zh)
- [x] **Plattformen**: Alle 6 Plattformen vorhanden

## 🧪 Manuelle Tests in Home Assistant

### 1. Installation & Setup

```bash
# In deiner Home Assistant Installation:
cd /config/custom_components/
git clone https://github.com/Xerolux/violet-hass.git violet_pool_controller
# oder kopiere den violet_pool_controller Ordner manuell

# Starte Home Assistant neu
```

#### Zu testen:
- [ ] Integration erscheint in "Integrationen hinzufügen"
- [ ] Configuration Flow startet ohne Fehler
- [ ] IP-Adresse/Hostname kann eingegeben werden
- [ ] Verbindung zum Controller erfolgreich
- [ ] Features können ausgewählt werden

### 2. Entities Prüfung

Nach erfolgreicher Konfiguration sollten folgende Entities verfügbar sein:

#### Sensors (sensor.*)
- [ ] Temperatur-Sensoren (Wasser, Pool, Solar, etc.)
- [ ] Wasser-Chemie (pH, ORP, Chlor)
- [ ] System-Diagnostics
- [ ] Analoge Eingänge

#### Binary Sensors (binary_sensor.*)
- [ ] Digitale Eingänge
- [ ] System-Alarme

#### Switches (switch.*)
- [ ] Pumpe (ON/OFF/AUTO)
- [ ] Heizung (ON/OFF/AUTO)
- [ ] Solar (ON/OFF/AUTO)
- [ ] Dosierung (Chlor, pH-, pH+, Flockung)
- [ ] DMX Szenen
- [ ] Extension Relays

#### Climate (climate.*)
- [ ] Heizungs-Thermostat
- [ ] Solar-Thermostat
- [ ] Temperatur-Setpoints änderbar
- [ ] HVAC Modi funktionieren

#### Cover (cover.*)
- [ ] Pool-Abdeckung
- [ ] Öffnen/Schließen/Stopp Befehle

#### Number (number.*)
- [ ] Temperatur-Sollwerte
- [ ] pH/ORP Sollwerte

### 3. Services Testen

Gehe zu **Entwicklerwerkzeuge > Services** und teste:

#### control_pump
```yaml
service: violet_pool_controller.control_pump
data:
  action: "on"
  speed: 75
```
- [ ] Pumpe schaltet ein
- [ ] Geschwindigkeit wird gesetzt
- [ ] Status-Update in Entity sichtbar

#### smart_dosing
```yaml
service: violet_pool_controller.smart_dosing
data:
  dosing_type: "chlorine"
  action: "manual"
  duration: 30
```
- [ ] Dosierung startet
- [ ] Timer läuft
- [ ] Safety Lock wird gesetzt

#### manage_pv_surplus
```yaml
service: violet_pool_controller.manage_pv_surplus
data:
  mode: "on"
```
- [ ] PV-Modus aktiviert
- [ ] Status-Update sichtbar

#### control_dmx_scenes
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  scene: "scene1"
  action: "on"
```
- [ ] DMX Szene aktiviert
- [ ] Lichter reagieren

### 4. API Kommunikation

#### Rate Limiting
- [ ] Schnelle aufeinanderfolgende Requests werden gedrosselt
- [ ] Keine 429 "Too Many Requests" Fehler
- [ ] Exponential Backoff funktioniert

#### Error Handling
- [ ] Controller offline → Entities werden "unavailable"
- [ ] Netzwerkfehler werden geloggt
- [ ] Auto-Recovery nach Wiederverbindung

#### Optimistic Updates
- [ ] Switches zeigen sofort neuen Status (optimistic)
- [ ] Nach API-Response wird Status aktualisiert
- [ ] Attribute `optimistic_state` und `pending_update` vorhanden

### 5. State Interpretation

#### 3-State Switches (ON/OFF/AUTO)
Teste mit verschiedenen Rohwerten:
- [ ] "1", 1, "ON" → Status ON
- [ ] "0", 0, "OFF" → Status OFF
- [ ] "2", "AUTO", "A" → Status AUTO
- [ ] String-States werden korrekt interpretiert

#### Cover States
- [ ] "OPEN", "open", "1" → Abdeckung offen
- [ ] "CLOSED", "closed", "0" → Abdeckung geschlossen
- [ ] Zwischenpositionen werden erkannt

### 6. Logging & Debugging

Prüfe Home Assistant Logs (`/config/home-assistant.log`):

```bash
grep -i "violet" /config/home-assistant.log | tail -50
```

Achte auf:
- [ ] Keine ERROR oder CRITICAL Meldungen
- [ ] INFO-Level zeigt normale Operationen
- [ ] DEBUG-Level (wenn aktiviert) zeigt Details
- [ ] Keine Python Tracebacks

### 7. Performance

- [ ] Coordinator Update alle 30s (Standard)
- [ ] CPU-Last < 5% normal
- [ ] Speicher-Usage stabil
- [ ] Keine Memory Leaks bei Langzeit-Betrieb (24h+)

### 8. Edge Cases

#### Fehlende Daten
- [ ] Leere API Response → Default-Werte
- [ ] Fehlende Sensor-Keys → Keine Crashes
- [ ] None-Werte werden behandelt

#### Ungültige Eingaben
- [ ] Zu hohe Temperatur → Clamping/Warning
- [ ] Negative Duration → Validation
- [ ] Ungültiger Action → Error Message

#### Gleichzeitige Requests
- [ ] Multiple Switches gleichzeitig → Queuing
- [ ] Rate Limiter verhindert Überlast
- [ ] Keine Race Conditions

### 9. Config Flow

#### Ersteinrichtung
- [ ] IP/Hostname Validation
- [ ] Connection Test funktioniert
- [ ] Feature Discovery zeigt verfügbare Features

#### Optionen Flow
- [ ] Update Intervall änderbar
- [ ] Features de-/aktivierbar
- [ ] Änderungen werden sofort angewendet

#### Migration
- [ ] Alte Configs werden migriert (falls vorhanden)
- [ ] Keine Datenverluste

### 10. Übersetzungen

Ändere die Sprache in Home Assistant und prüfe:
- [ ] Entity Names übersetzt
- [ ] Service Beschreibungen übersetzt
- [ ] Error Messages übersetzt
- [ ] Config Flow Texte übersetzt

## 🐛 Bug Reporting

Falls Fehler auftreten, sammle:

1. **Home Assistant Version**
   ```bash
   cat /config/.HA_VERSION
   ```

2. **Integration Version**
   ```bash
   cat /config/custom_components/violet_pool_controller/manifest.json | grep version
   ```

3. **Relevante Logs**
   ```bash
   grep -i "violet" /config/home-assistant.log > violet_debug.log
   ```

4. **Config Entry Data** (aus .storage/core.config_entries)

5. **API Response Sample** (anonymisiert)

## ✨ Type-Fixes in diesem Update

Die folgenden Type-Errors wurden behoben:

1. ✅ Optional parameters in `utils_sanitizer.py`
2. ✅ Float/Int type mismatch in `utils_rate_limiter.py`
3. ✅ Dict return types in `const_devices.py`
4. ✅ Template string type in `api.py`
5. ✅ Attribute dict typing in `switch.py`
6. ✅ None checks in `sensor.py`
7. ✅ Temperature return type in `climate.py`
8. ✅ Safety interval cast in `services.py`

Alle MyPy Type-Errors (außer erwartete import-not-found) sind behoben!
