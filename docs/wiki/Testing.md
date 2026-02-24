# Testing – Tests ausführen und schreiben

> Komplette Anleitung für das Test-System der Violet Pool Controller Integration.

---

## Quick Start

```bash
# Einmalig: Testumgebung einrichten
./scripts/setup-test-env.sh

# Tests ausführen
./scripts/run-tests.sh

# Erwartetes Ergebnis: 53+ Tests, alle grün ✓
```

---

## Testumgebung einrichten

### Automatisch (empfohlen)

```bash
./scripts/setup-test-env.sh
```

Das Script erledigt:
- Python 3.12 prüfen
- Virtuelle Umgebung `.venv-ha-test/` erstellen
- Home Assistant 2025.1.4+ installieren
- pytest und Abhängigkeiten installieren
- `activate-test-env.sh` Helper erstellen

### Manuell

```bash
python3.12 -m venv .venv-ha-test
source .venv-ha-test/bin/activate
pip install -r requirements-dev.txt
pip install pytest-homeassistant-custom-component
```

---

## Tests ausführen

### Alle Tests

```bash
./scripts/run-tests.sh
# oder
source .venv-ha-test/bin/activate
pytest tests/ -v
```

### Einzelne Test-Dateien

```bash
pytest tests/test_api.py -v
pytest tests/test_config_flow.py -v
pytest tests/test_device.py -v
pytest tests/test_entity_state.py -v
pytest tests/test_integration.py -v
pytest tests/test_sanitizer.py -v
```

### Einzelne Test-Funktion

```bash
pytest tests/test_api.py::TestVioletPoolAPI::test_rate_limiting -v
```

---

## Test-Kategorien

### API Tests (`test_api.py`) – 7 Tests

Testet die HTTP-Kommunikation mit dem Controller:

| Test | Beschreibung |
|------|-------------|
| `test_rate_limiting` | Token-Bucket schränkt Anfragen ein |
| `test_priority_queue` | Hochprioritäre Anfragen zuerst |
| `test_timeout_handling` | Timeouts werden korrekt behandelt |
| `test_retry_logic` | Wiederholungsversuche bei Fehlern |
| `test_error_responses` | HTTP-Fehler werden korrekt weitergeleitet |
| `test_json_parsing` | JSON-Antworten korrekt geparst |
| `test_ssl_config` | SSL-Einstellungen werden angewendet |

```bash
pytest tests/test_api.py -v
```

---

### Config Flow Tests (`test_config_flow.py`) – 5 Tests

Testet den Setup-Assistenten:

| Test | Beschreibung |
|------|-------------|
| `test_duplicate_detection` | Zwei gleiche Controller werden erkannt |
| `test_controller_name_handling` | Controller-Namen korrekt gespeichert |
| `test_ip_validation` | Ungültige IPs werden abgelehnt |
| `test_feature_selection` | Feature-Auswahl wird gespeichert |
| `test_successful_setup` | Vollständiger Setup-Flow |

```bash
pytest tests/test_config_flow.py -v
```

---

### Device Tests (`test_device.py`) – 7 Tests

Testet Device-Management und Recovery:

| Test | Beschreibung |
|------|-------------|
| `test_recovery_lock` | Keine Race Conditions |
| `test_exponential_backoff` | Wartezeiten verdoppeln sich |
| `test_max_recovery_attempts` | Nach 10 Versuchen: Stop |
| `test_device_info_update` | Device-Info korrekt aktualisiert |
| `test_connection_loss` | Verbindungsverlust erkannt |
| `test_successful_recovery` | Verbindung wiederhergestellt |
| `test_coordinator_update` | Daten-Update korrekt verarbeitet |

```bash
pytest tests/test_device.py -v
```

---

### Integration Tests (`test_integration.py`) – 10 Tests

End-to-End Tests:

| Test | Beschreibung |
|------|-------------|
| `test_domain_initialization` | Domain korrekt registriert |
| `test_entry_setup` | Config Entry wird geladen |
| `test_entry_unload` | Integration sauber entladen |
| `test_service_registration` | Alle Services registriert |
| `test_config_migration` | Alte Konfigurationen migriert |
| `test_sensor_creation` | Sensoren werden erstellt |
| `test_switch_creation` | Schalter werden erstellt |
| `test_climate_creation` | Climate-Entities erstellt |
| `test_cover_creation` | Cover-Entity erstellt |
| `test_number_creation` | Number-Entities erstellt |

```bash
pytest tests/test_integration.py -v
```

---

### Entity State Tests (`test_entity_state.py`) – 4 Tests

Testet State-Interpretation:

| Test | Beschreibung |
|------|-------------|
| `test_3state_switches` | ON/OFF/AUTO korrekt interpretiert |
| `test_numeric_prefix` | `"2\|SOLAR_ACTIVE"` korrekt geparst |
| `test_string_state_parsing` | String-States korrekt konvertiert |
| `test_boolean_conversion` | Wahrheitswerte korrekt |

```bash
pytest tests/test_entity_state.py -v
```

---

### Sanitizer Tests (`test_sanitizer.py`) – 13 Tests

Security und Input-Validation:

| Test | Beschreibung |
|------|-------------|
| `test_xss_prevention` | `<script>` wird geblockt |
| `test_sql_injection` | SQL-Syntax wird geblockt |
| `test_command_injection` | Shell-Befehle werden geblockt |
| `test_path_traversal` | `../` wird geblockt |
| `test_ph_range` | pH außerhalb 6.0–8.0 geblockt |
| `test_orp_range` | ORP außerhalb 200–900 mV geblockt |
| `test_temperature_range` | Temp außerhalb 10–40°C geblockt |
| `test_alphanumeric_validation` | Nur erlaubte Zeichen |
| `test_numeric_validation` | Nur Zahlen |
| `test_html_escaping` | HTML-Sonderzeichen escaped |
| `test_empty_input` | Leere Eingaben behandelt |
| `test_null_input` | None-Werte behandelt |
| `test_oversized_input` | Zu lange Eingaben gestutzt |

```bash
pytest tests/test_sanitizer.py -v
```

---

## Erweiterte Optionen

### Coverage-Report

```bash
# Terminal-Report
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=term

# HTML-Report (detailliert)
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=html
# Öffnen: htmlcov/index.html

# Ziel: > 80% Coverage
```

### Parallel ausführen (schneller)

```bash
pip install pytest-xdist
pytest tests/ -n auto -v
```

### Fehlgeschlagene Tests wiederholen

```bash
pytest tests/ --lf -v
```

### Verbose mit Details

```bash
pytest tests/ -vv --tb=long
```

---

## Debugging

### Python Debugger

```bash
pytest tests/ --pdb
# Bei Fehler: Debugger startet automatisch
```

### Print-Ausgaben anzeigen

```bash
pytest tests/ -v -s
```

### Debug-Logging

```bash
pytest tests/ -v --log-cli-level=DEBUG
```

---

## pytest.ini Konfiguration

```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

Diese Einstellungen sind notwendig für:
- **asyncio_mode = auto**: Automatisches async/await-Handling
- **asyncio_default_fixture_loop_scope = function**: Isolierte Event-Loops pro Test

---

## conftest.py – Thread-Workaround

`tests/conftest.py` enthält einen wichtigen Patch:

```python
# Filtert Home Assistant's _run_safe_shutdown_loop Threads
# Verhindert false-positive Thread-Leak-Warnungen
# Notwendig für HA 2025.1+
```

---

## Pre-Release Checkliste

```bash
# 1. Linting (0 Fehler!)
python -m ruff check custom_components/violet_pool_controller/
python -m mypy custom_components/violet_pool_controller/

# 2. Alle Tests grün
./scripts/run-tests.sh

# 3. Coverage prüfen (> 80%)
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=term

# 4. Manueller Test in echter HA-Instanz
```

### Erwartetes Ergebnis

```
======================== test session starts ========================
...
======================== 53 passed in 12.34s ========================
```

---

## CI/CD Integration

GitHub Actions läuft automatisch bei Push/PR:

```yaml
# .github/workflows/validate.yml
- Ruff Linting
- MyPy Type Checking
- pytest (HA 2024.12.0 + 2025.1.0)
- Python 3.12
```

---

## Troubleshooting

### ImportError / ModuleNotFoundError

```bash
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

### "No module named custom_components"

Tests vom Projekt-Root ausführen (nicht aus `tests/`):

```bash
# Richtig
pytest tests/ -v

# Falsch
cd tests && pytest
```

### Thread-Assertion Error

```bash
# Virtuelle Umgebung neu erstellen
rm -rf .venv-ha-test/
./scripts/setup-test-env.sh
```

### Alte HA-Version

```bash
rm -rf .venv-ha-test/
./scripts/setup-test-env.sh
```

---

## Test-Erfolgs-Kriterien

Vor jedem Merge/Release müssen erfüllt sein:

- [ ] **100% aller Unit-Tests bestehen**
- [ ] **Ruff Linting: 0 Fehler**
- [ ] **MyPy: 0 Fehler** (außer `import-not-found`)
- [ ] **Coverage: > 80%**
- [ ] **Kein Regression bei bestehenden Features**

---

*Zurück: [Contributing](Contributing) | Weiter: [API Referenz](API-Reference)*
