# Docker Live Test Guide (Template)

## ⚠️ WICHTIG - Sicherheitshinweis

**Dies ist eine TEMPLATE-Datei. Für die echten Tests mit Passwörtern siehe `DOCKER_TEST_GUIDE.md` (nicht in Git).**

Diese Datei enthält keine echten Passwörter oder sensiblen Daten.

---

## Übersicht

Dieses Dokument beschreibt, wie man das violet-hass Addon in einem Docker Container mit dem live Pool Controller testet.

**Home Assistant Version:** 2026.3.0.dev
**Addon Version:** 1.0.1

---

## Voraussetzungen

### Hardware/Netzwerk
- Pool Controller muss im Netzwerk erreichbar sein
- Docker und Docker Compose müssen installiert sein

### Software
- Docker Desktop für Windows/Mac oder Docker Engine für Linux
- Git Bash oder ähnliche Shell (für Windows)

---

## Schnellstart (Quick Start)

```bash
# 1. In das Projektverzeichnis wechseln
cd /path/to/violet-hass

# 2. Credentials konfigurieren
cp tests/docker/test_credentials.example.txt tests/docker/test_credentials.txt
# Editiere test_credentials.txt mit echten Daten

# 3. Docker Compose starten
docker compose up -d

# 4. Auf Home Assistant warten (~20-30 Sekunden)
sleep 20

# 5. Logs prüfen
docker compose logs -f --tail=100

# 6. Home Assistant WebUI öffnen
# Browser: http://localhost:8123
```

---

## Controller-Daten Setup

Die Anmeldedaten müssen in `tests/docker/test_credentials.txt` konfiguriert werden (NICHT in Git committen!).

### Erforderliche Umgebungsvariablen

```bash
# Controller Verbindung
CONTROLLER_IP=192.168.1.xxx         # IP Adresse des Controllers
CONTROLLER_PORT=80                   # Port (default: 80)
CONTROLLER_USER=your_username        # Benutzername
CONTROLLER_PASS=your_password        # Passwort
CONTROLLER_SSL=false                 # HTTPS verwenden (true/false)
CONTROLLER_DEVICE_ID=1               # Geräte-ID (default: 1)

# Home Assistant Docker
HA_PORT=8123                         # HA Port
HA_URL=http://localhost:8123        # HA URL
```

### API-Endpoints (Beispiele)

```bash
# Alle Readings abrufen
curl -u "USER:PASS" "http://CONTROLLER_IP/getReadings?ALL"

# Pumpe steuern (Speed 2 = Normal)
curl -u "USER:PASS" "http://CONTROLLER_IP/setFunctionManually?PUMP,ON,0,2"

# Pumpe ausschalten
curl -u "USER:PASS" "http://CONTROLLER_IP/setFunctionManually?PUMP,OFF"

# Pumpen-Status prüfen
curl -u "USER:PASS" "http://CONTROLLER_IP/getReadings?PUMP,PUMP_RPM_1,PUMP_RPM_2,PUMP_RPM_3"
```

---

## Docker Konfiguration

### docker-compose.yml

```yaml
services:
  homeassistant:
    container_name: homeassistant-dev
    image: ghcr.io/home-assistant/home-assistant:dev
    restart: unless-stopped
    privileged: true
    volumes:
      - ./config:/config
      - ./custom_components:/config/custom_components
      - /etc/localtime:/etc/localtime:ro
    environment:
      - TZ=Europe/Berlin
    ports:
      - "8123:8123"
    command: >
      python -m homeassistant --config /config --debug
```

### Wichtige Mount-Points

- `./config:/config` - Home Assistant Konfiguration
- `./custom_components:/config/custom_components` - Addon Source Code

---

## Integration Konfiguration

### Manuelles Setup (Entry in .storage/core.config_entries)

Um die Integration manuell zu konfigurieren, muss ein Entry in `config/.storage/core.config_entries` erstellt werden:

```json
{
  "created_at": "2026-02-23T16:45:00.000000+00:00",
  "data": {
    "host": "192.168.1.xxx",       // WICHTIG: "host" nicht "api_url"!
    "device_id": 1,
    "password": "your_password",    // Echtes Passwort
    "use_ssl": false,
    "username": "your_username"     // Echter Benutzername
  },
  "disabled_by": null,
  "discovery_keys": {},
  "domain": "violet_pool_controller",
  "entry_id": "violet_test_001",
  "minor_version": 1,
  "modified_at": "2026-02-23T16:45:00.000000+00:00",
  "options": {
    "active_features": ["filter_control", "backwash"],
    "pool_type": "outdoor",
    "disinfection_method": "chlorine"
  },
  "pref_disable_new_entities": false,
  "pref_disable_polling": false,
  "source": "user",
  "subentries": [],
  "title": "Violet Pool Controller",
  "unique_id": "192.168.1.xxx_1",
  "version": 1
}
```

### Wichtige Config-Keys

- `host` (nicht `api_url`!) - IP Adresse des Controllers
- `username` - Benutzername (optional)
- `password` - Passwort (optional, aber empfohlen)
- `use_ssl` - HTTPS verwenden (true/false)
- `device_id` - Geräte-ID (default: 1)

---

## Testfälle

### Test 1: Container Start & Home Assistant Boot

**Erwartet:**
- Container startet erfolgreich
- Home Assistant bootet in < 5 Sekunden
- Keine kritischen Fehler im Log

**Prüfen:**
```bash
docker compose ps
docker compose logs --tail=50
```

---

### Test 2: Integration Setup

**Erwartet:**
- Addon wird von HA erkannt
- Config Entry wird geladen
- Coordinator startet erfolgreich
- API-Verbindung wird hergestellt

**Prüfen:**
```bash
docker compose logs | grep -i "violet"
```

**Erwartete Logs:**
```
INFO (MainThread) [homeassistant.setup] Setting up violet_pool_controller
INFO (MainThread) [custom_components.violet_pool_controller] Setting up Violet Pool Controller
DEBUG (MainThread) [custom_components.violet_pool_controller.device] Finished fetching Violet Pool Controller data in X.XXX seconds (success: True)
```

---

### Test 3: Entity Creation

**Erwartet:**
- Sensoren werden erstellt
- Binary Sensors werden erstellt
- Switch Entities werden erstellt
- Number Entities werden erstellt

**Prüfen:**
```bash
docker compose logs | grep -i "registered new.*violet"
```

**Erwartete Entities:**
- `sensor.violet_pool_controller_last_error_id`
- `binary_sensor.violet_pool_controller_pump`
- `number.violet_pool_controller_pump_speed`
- etc.

---

### Test 4: Pumpensteuerung (API Test)

**Vorbereitung:** Credentials aus `test_credentials.txt` laden

**Test-Stufen:**

1. **Pumpe Speed 1 (Eco):**
   ```bash
   curl -u "USER:PASS" "http://IP/setFunctionManually?PUMP,ON,0,1"
   # Erwartet: PUMP_RPM_1=4
   ```

2. **Pumpe Speed 2 (Normal):**
   ```bash
   curl -u "USER:PASS" "http://IP/setFunctionManually?PUMP,ON,0,2"
   # Erwartet: PUMP_RPM_2=4
   ```

3. **Pumpe Speed 3 (Boost):**
   ```bash
   curl -u "USER:PASS" "http://IP/setFunctionManually?PUMP,ON,0,3"
   # Erwartet: PUMP_RPM_3=4
   ```

4. **Pumpe OFF:**
   ```bash
   curl -u "USER:PASS" "http://IP/setFunctionManually?PUMP,OFF"
   # Erwartet: PUMP=0 oder 6
   ```

**Verifizierung:**
```bash
curl -u "USER:PASS" "http://IP/getReadings?PUMP,PUMP_RPM_1,PUMP_RPM_2,PUMP_RPM_3"
```

---

### Test 5: State Synchronisation

**Erwartet:**
- Home Assistant erkennt State-Changes
- Entities werden aktualisiert
- Keine Verzögerungen > 10 Sekunden

**Prüfen:**
```bash
# Pumpe einschalten
curl -u "USER:PASS" "http://IP/setFunctionManually?PUMP,ON,0,2"

# Logs beobachten
docker compose logs -f | grep -i "pump"
```

**Erwartete Logs:**
```
DEBUG (MainThread) [custom_components.violet_pool_controller.number] Pumpengeschwindigkeit aktiv: Stufe 2 (PUMP_RPM_2=4)
```

---

## Wichtige Log-Meldungen

### ✅ Positive Signs (Alles OK)

```log
INFO (MainThread) [homeassistant.setup] Setting up violet_pool_controller
INFO (MainThread) [custom_components.violet_pool_controller] Setting up Violet Pool Controller
DEBUG (MainThread) [custom_components.violet_pool_controller.device] Finished fetching Violet Pool Controller data in 0.255 seconds (success: True)
INFO (MainThread) [homeassistant.helpers.entity_registry] Registered new sensor.violet_pool_controller entity: sensor.violet_pool_controller_last_error_id
DEBUG (MainThread) [custom_components.violet_pool_controller.number] Pumpengeschwindigkeit aktiv: Stufe 2 (PUMP_RPM_2=4)
```

### ⚠️ Erwartete Warnungen (Kein Fehler)

```log
WARNING (SyncWorker_0) [homeassistant.loader] We found a custom integration violet_pool_controller which has not been tested by Home Assistant.
WARNING (MainThread) [asyncio] Executing <Task...> took 0.XXX seconds
```

### ❌ Fehler (Müssen behoben werden)

```log
ERROR (MainThread) [custom_components.violet_pool_controller] Required IP address is missing from the configuration.
ERROR (MainThread) [homeassistant.config_entries] Error setting up entry Violet Pool Controller
```

---

## Troubleshooting

### Container startet nicht

**Problem:** `docker compose up -d` zeigt Fehler

**Lösung:**
```bash
# Alten Container entfernen
docker compose down
docker rm -f homeassistant-dev

# Neu starten
docker compose up -d
```

### Integration wird nicht geladen

**Problem:** Keine violet-Logs zu sehen

**Lösung:**
1. Config Entry prüfen: `config/.storage/core.config_entries`
2. Key muss `host` sein, nicht `api_url`!
3. Container neu starten: `docker compose restart`

### Keine Verbindung zum Controller

**Problem:** `cannot_connect` Fehler

**Lösung:**
1. Controller erreichbar?
   ```bash
   ping CONTROLLER_IP
   ```
2. Credentials korrekt?
   ```bash
   curl -u "USER:PASS" "http://CONTROLLER_IP/getReadings?ALL"
   ```
3. Firewall prüfen

---

## Automatisierte Tests

Verwende das Test-Skript für automatisierte Tests:

```bash
# Alle Tests
./tests/docker/run_docker_test.sh all

# Nur Smoke Tests
./tests/docker/run_docker_test.sh smoke

# Nur API Tests
./tests/docker/run_docker_test.sh api

# Pumpen-Test
./tests/docker/run_docker_test.sh pump

# Logs anzeigen
./tests/docker/run_docker_test.sh logs

# Status anzeigen
./tests/docker/run_docker_test.sh status
```

---

## Nächste Schritte

### Für zukünftige Tests

1. **Neue Features testen:**
   - Climate Entity (Heizung/Solar)
   - Select Entity (ON/OFF/AUTO)
   - Sensor Readings

2. **Performance Tests:**
   - Langlebigkeit (> 1 Stunde laufen lassen)
   - Memory Leaks prüfen
   - API Rate Limiting testen

3. **Fehler-Szenarien:**
   - Controller nicht erreichbar
   - Falsche Credentials
   - Netzwerk-Timeout

4. **Code Review Improvements validieren:**
   - ✅ Private Attribute Access Fix
   - ✅ Task Cleanup
   - ✅ Type Hints
   - ✅ Shared Code Reduction

---

## Referenzen

- **Addon Repository:** https://github.com/xerolux/violet-hass
- **Docker Hub:** https://github.com/home-assistant/home-assistant
- **HA Dokumentation:** https://developers.home-assistant.io/

---

## Test-Checkliste

### Vorbereitung
- [ ] Docker läuft
- [ ] Controller ist eingeschaltet und erreichbar
- [ ] `test_credentials.txt` existiert mit korrekten Daten
- [ ] `.gitignore` ist aktualisiert

### Durchführung
- [ ] Container gestartet
- [ ] Home Assistant bootet erfolgreich
- [ ] Integration wird geladen (keine Fehler)
- [ ] API-Verbindung erfolgreich (fetch success)
- [ ] Entities werden erstellt
- [ ] Pumpensteuerung funktioniert (Speed 1, 2, 3, OFF)
- [ ] State-Sync funktioniert

### Aufräumen
- [ ] Pumpe wieder ausschalten
- [ ] Test-Ergebnisse dokumentieren

---

*Template Version: 2026-02-23*
*Status: Production Ready ✅*
*Für echte Test-Daten mit Passwörtern siehe `DOCKER_TEST_GUIDE.md` (nicht in Git)*
