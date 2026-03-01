# Testing Guide für Violet Pool Controller

## 🧪 Übersicht

Dieses Projekt enthält umfassende Tests, die vor jedem Release durchgeführt werden müssen.

## 📋 Quick Start

### 1. Testumgebung einrichten (einmalig)

```bash
# Aus dem Projekt-Stammverzeichnis:
./scripts/setup-test-env.sh
```

Das Script:
- ✅ Prüft Python 3.13
- ✅ Erstellt virtuelle Umgebung (`.venv-ha-test/`)
- ✅ Installiert Home Assistant 2025.12.0
- ✅ Installiert pytest und Test-Dependencies
- ✅ Erstellt `activate-test-env.sh` Helper

### 2. Tests ausführen

```bash
# Option 1: Mit dem Run-Script (empfohlen)
./scripts/run-tests.sh

# Option 2: Manuell
source activate-test-env.sh
pytest tests/ -v
```

## 🎯 Test-Kategorien

### API Tests (`tests/test_api.py`)
Tests für die API-Kommunikation mit dem Pool-Controller:
- ✅ Rate Limiting (Token Bucket)
- ✅ Priority Queue
- ✅ Timeout Handling
- ✅ Error Handling
- ✅ JSON Parsing

```bash
pytest tests/test_api.py -v
```

### Config Flow Tests (`tests/test_config_flow.py`)
Tests für die Konfigurations-UI:
- ✅ Duplikat-Erkennung
- ✅ Controller-Name Handling
- ✅ IP-Validierung

```bash
pytest tests/test_config_flow.py -v
```

### Device Tests (`tests/test_device.py`)
Tests für Device-Management und Recovery:
- ✅ Recovery-Lock gegen Race Conditions
- ✅ Exponential Backoff
- ✅ Device Info Updates

```bash
pytest tests/test_device.py -v
```

### Integration Tests (`tests/test_integration.py`)
End-to-End Tests für Integration Setup:
- ✅ Domain Initialisierung
- ✅ Entry Setup/Unload
- ✅ Service Registration
- ✅ Config Migration

```bash
pytest tests/test_integration.py -v
```

### Entity State Tests (`tests/test_entity_state.py`)
Tests für State-Interpretation:
- ✅ 3-State Switches (ON/OFF/AUTO)
- ✅ Numeric Prefix Handling
- ✅ String State Parsing

```bash
pytest tests/test_entity_state.py -v
```

### Sanitizer Tests (`tests/test_sanitizer.py`)
Security und Input-Validation Tests:
- ✅ XSS Prevention
- ✅ Path Traversal Prevention
- ✅ Range Validation (pH, ORP, Chlor)
- ✅ SQL Injection Prevention

```bash
pytest tests/test_sanitizer.py -v
```

## 📊 Test-Coverage

Coverage-Report erstellen:

```bash
source activate-test-env.sh
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=html
```

HTML-Report öffnen:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🔧 Erweiterte Test-Optionen

### Einzelnen Test ausführen

```bash
pytest tests/test_api.py::TestVioletPoolAPI::test_rate_limiting_active -v
```

### Tests mit bestimmtem Marker

```bash
pytest -m thread_safe -v
```

### Tests parallel ausführen (schneller)

```bash
pip install pytest-xdist
pytest tests/ -n auto -v
```

### Detaillierte Fehlerausgabe

```bash
pytest tests/ -vv --tb=long
```

### Nur fehlgeschlagene Tests wiederholen

```bash
pytest tests/ --lf -v
```

## 🐛 Debugging Tests

### Mit pdb (Python Debugger)

```bash
pytest tests/ --pdb
```

Bei Fehler wird automatisch der Debugger gestartet.

### Test-Output anzeigen (print statements)

```bash
pytest tests/ -v -s
```

### Logging aktivieren

```bash
pytest tests/ -v --log-cli-level=DEBUG
```

## ⚙️ pytest.ini Konfiguration

Die `pytest.ini` enthält:
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

Diese Einstellungen sind wichtig für async Tests mit Home Assistant.

## 🔍 conftest.py - Thread-Check Workaround

Die `tests/conftest.py` enthält einen wichtigen Patch:
- Filtert Home Assistant's `_run_safe_shutdown_loop` Threads
- Verhindert false-positive Thread-Leaks
- Notwendig für Kompatibilität mit HA 2025.1+

## 📝 Vor jedem Release

### Pre-Release Checklist

```bash
# 1. Code-Qualität prüfen
ruff check custom_components/
mypy custom_components/violet_pool_controller/

# 2. Alle Tests laufen lassen
./scripts/run-tests.sh

# 3. Coverage prüfen (sollte > 80% sein)
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=term

# 4. Integration in echter HA-Instanz testen (siehe TESTING_CHECKLIST.md)
```

### Erwartete Test-Ergebnisse

```
======================== Test Summary ========================
✓ 53 Tests BESTANDEN
══════════════════════════════════════════════════════════════
Erfolgsrate: 100%
```

Alle Tests müssen bestehen, bevor ein Release erstellt wird!

## 🏗️ Test-Struktur

```
tests/
├── conftest.py              # Pytest-Konfiguration & Fixtures
├── test_api.py              # API-Tests (7 Tests)
├── test_config_flow.py      # Config Flow Tests (5 Tests)
├── test_device.py           # Device Tests (7 Tests)
├── test_entity_state.py     # State Tests (4 Tests)
├── test_integration.py      # Integration Tests (10 Tests)
└── test_sanitizer.py        # Security Tests (13 Tests)
```

## 🔄 CI/CD Integration

Für GitHub Actions / GitLab CI:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Setup Test Environment
        run: ./scripts/setup-test-env.sh
      - name: Run Tests
        run: ./scripts/run-tests.sh
```

## 🆘 Troubleshooting

### Problem: Import-Fehler

**Lösung:**
```bash
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

### Problem: "No module named custom_components"

**Lösung:** Test von Projekt-Root ausführen, nicht aus `tests/` Verzeichnis.

### Problem: Thread-Name Assertion Error

**Lösung:** `conftest.py` enthält bereits den Fix. Falls Problem weiterhin besteht:
```bash
rm -rf .venv-ha-test/
./scripts/setup-test-env.sh
```

### Problem: Alte Home Assistant Version

**Lösung:**
```bash
rm -rf .venv-ha-test/
./scripts/setup-test-env.sh
```

### Problem: pytest not found

**Lösung:**
```bash
source .venv-ha-test/bin/activate
```

## 📚 Weitere Ressourcen

- [pytest Dokumentation](https://docs.pytest.org/)
- [Home Assistant Testing Best Practices](https://developers.home-assistant.io/docs/development_testing)
- [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)

## ✅ Test-Erfolg Kriterien

Vor einem Merge/Release müssen erfüllt sein:

- [ ] **100% aller Unit-Tests bestehen**
- [ ] **Ruff Linting: 0 Fehler**
- [ ] **MyPy Type Check: 0 Fehler (außer import-not-found)**
- [ ] **Test Coverage: > 80%**
- [ ] **Manuelle Tests in echter HA-Instanz** (siehe TESTING_CHECKLIST.md)
- [ ] **Keine Regression bei existierenden Features**

## 🚀 Continuous Testing

Es wird empfohlen, Tests automatisch bei jedem Commit zu laufen:

```bash
# Git pre-commit hook erstellen
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./scripts/run-tests.sh
EOF
chmod +x .git/hooks/pre-commit
```

Dann werden Tests automatisch vor jedem Commit ausgeführt.
