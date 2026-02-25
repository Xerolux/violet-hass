# Contributing – Mitmachen & Beitragen

> Wie du zum Violet Pool Controller Projekt beitragen kannst.

---

## Willkommen!

Beiträge sind herzlich willkommen – egal ob Bug-Reports, Feature-Requests, Dokumentation oder Code. Jeder Beitrag zählt!

---

## Arten von Beiträgen

| Art | Beschreibung | Wie? |
|-----|-------------|------|
| **Bug-Report** | Fehler gefunden | GitHub Issue |
| **Feature-Request** | Neue Funktion gewünscht | GitHub Issue |
| **Pull Request** | Code oder Doku verbessert | Fork → PR |
| **Übersetzung** | Neue Sprache hinzufügen | Fork → PR |
| **Wiki** | Dokumentation verbessern | Fork → PR |
| **Testing** | Integration testen | Feedback via Issue |

---

## Bug-Report erstellen

### GitHub Issue öffnen

[Neues Issue erstellen](https://github.com/Xerolux/violet-hass/issues/new)

### Ein guter Bug-Report enthält

```
1. ZUSAMMENFASSUNG
   Was ist das Problem? (1-2 Sätze)

2. ENVIRONMENT
   - Home Assistant Version: 2026.x.x (Minimum: 2025.12.0)
   - Integration Version: 1.0.2-beta.5
   - Controller Firmware: x.x.x
   - Python Version: 3.12+

3. SCHRITTE ZUM REPRODUZIEREN
   1. Integration hinzufügen mit ...
   2. Klicke auf ...
   3. Fehler tritt auf

4. ERWARTETES VERHALTEN
   Was sollte passieren?

5. TATSÄCHLICHES VERHALTEN
   Was passiert stattdessen?

6. LOGS
   Einstellungen → System → Protokoll → Filtern nach "violet"
```

---

## Pull Request erstellen

### Schritt-für-Schritt

```bash
# 1. Repository forken (GitHub UI)

# 2. Fork klonen
git clone https://github.com/DEIN_USERNAME/violet-hass.git
cd violet-hass

# 3. Branch erstellen
git checkout -b feat/neue-funktion
# oder: fix/bug-beschreibung

# 4. Änderungen machen
# Code editieren...

# 5. Code-Qualität prüfen
pip install ruff mypy
python -m ruff check custom_components/violet_pool_controller/ --fix
python -m mypy custom_components/violet_pool_controller/

# 6. Tests ausführen
./scripts/setup-test-env.sh  # Einmalig
./scripts/run-tests.sh

# 7. Committen (Conventional Commits)
git add custom_components/violet_pool_controller/datei.py
git commit -m "feat: Neue Funktion XYZ hinzugefügt"

# 8. Pushen
git push origin feat/neue-funktion

# 9. Pull Request auf GitHub erstellen
```

### Branch-Naming

| Typ | Beispiel |
|-----|---------|
| Feature | `feat/dmx-color-control` |
| Bugfix | `fix/pump-state-parsing` |
| Dokumentation | `docs/wiki-update` |
| Refactoring | `refactor/api-cleanup` |
| Tests | `test/sensor-coverage` |

---

## Commit-Nachrichten

Wir folgen [Conventional Commits](https://www.conventionalcommits.org/):

```
<typ>: <kurze Beschreibung>

[optionaler Body]

[optionaler Footer]
```

### Typen

| Typ | Verwendung |
|-----|-----------|
| `feat` | Neue Funktion |
| `fix` | Bug-Behebung |
| `docs` | Dokumentation |
| `refactor` | Code-Umstrukturierung |
| `test` | Tests hinzufügen/ändern |
| `chore` | Build, Dependencies, CI |
| `perf` | Performance-Verbesserung |

### Beispiele

```bash
git commit -m "feat: Unterstützung für AI1-AI8 Analogeingänge hinzugefügt"
git commit -m "fix: pH-Sensor zeigt falschen Wert bei negativen Zahlen"
git commit -m "docs: Fehler-Codes Tabelle erweitert"
git commit -m "test: Tests für Rate-Limiter Randwerte hinzugefügt"
```

---

## Code-Style

### Linting mit Ruff

```bash
# Prüfen
python -m ruff check custom_components/violet_pool_controller/

# Automatisch reparieren
python -m ruff check custom_components/violet_pool_controller/ --fix
```

### Type Checking mit MyPy

```bash
python -m mypy custom_components/violet_pool_controller/
```

### Style-Regeln

```python
# Ja: Moderne Type-Annotations
def get_value(key: str) -> float | None:
    ...

# Nein: Alte Optional-Syntax
from typing import Optional
def get_value(key: str) -> Optional[float]:
    ...

# Ja: collections.abc
from collections.abc import Callable

# Nein: typing.Callable (deprecated)
from typing import Callable
```

### Wichtige Prinzipien

1. **Keine stillen Fehler:** Alle Exceptions loggen
2. **Type Hints:** Alle öffentlichen Methoden typisieren
3. **Docstrings:** Öffentliche Klassen und Methoden dokumentieren
4. **Konstanten:** In `const_*.py` Dateien definieren
5. **Tests:** Neue Funktionen mit Tests abdecken

---

## Tests schreiben

### Neue Tests hinzufügen

```python
# tests/test_meine_funktion.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.violet_pool_controller.api import VioletPoolAPI


class TestMeineFunktion:
    """Tests für meine neue Funktion."""

    @pytest.fixture
    def api(self):
        """API-Fixture."""
        session = AsyncMock()
        return VioletPoolAPI(
            host="192.168.1.55",
            session=session,
        )

    async def test_basic_functionality(self, api):
        """Test der Grundfunktionalität."""
        # Arrange
        expected = 7.2

        # Act
        result = api.parse_ph_value("7.2")

        # Assert
        assert result == expected

    async def test_error_handling(self, api):
        """Test der Fehlerbehandlung."""
        with pytest.raises(ValueError):
            api.parse_ph_value("invalid")
```

### Tests ausführen

```bash
# Alle Tests
pytest tests/ -v

# Einzelner Test
pytest tests/test_meine_funktion.py -v

# Mit Coverage
pytest tests/ --cov=custom_components/violet_pool_controller --cov-report=term

# Details
pytest tests/ -vv --tb=long
```

### Test-Kriterien für PR-Merge

- [ ] Alle 53+ bestehenden Tests bestehen
- [ ] Neue Funktionen haben Tests
- [ ] Coverage > 80%
- [ ] Ruff: 0 Fehler
- [ ] MyPy: 0 Fehler

---

## Neue Sprache hinzufügen

### Übersetzungsdatei erstellen

1. `custom_components/violet_pool_controller/translations/en.json` als Vorlage kopieren
2. Als `xx.json` (Sprachcode) speichern
3. Alle Strings übersetzen
4. PR erstellen

### Unterstützte Sprachen

Aktuell: `de`, `en`, `es`, `fr`, `it`, `nl`, `pl`, `pt`, `ru`, `zh`

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Violet Pool Controller einrichten",
        "description": "Verbindungsdaten eingeben"
      }
    }
  }
}
```

---

## Entwicklungsumgebung einrichten

### Lokale HA-Entwicklungsinstanz

```bash
# Virtuelle Umgebung für Tests
./scripts/setup-test-env.sh

# VS Code Dev Container (empfohlen)
# .devcontainer/ öffnen → "Reopen in Container"
# → http://localhost:8123
```

### Abhängigkeiten installieren

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Pre-Commit Hook (optional)

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
python -m ruff check custom_components/violet_pool_controller/ --fix
./scripts/run-tests.sh
EOF
chmod +x .git/hooks/pre-commit
```

---

## Review-Prozess

1. **PR öffnen** mit klarer Beschreibung
2. **CI prüft** automatisch: Ruff, MyPy, pytest
3. **Maintainer reviewt** den Code
4. **Feedback** ggf. umsetzen
5. **Merge** nach Genehmigung

### PR-Checkliste

- [ ] Branch von `main` erstellt
- [ ] Beschreibung erklärt Was und Warum
- [ ] Tests wurden ergänzt/angepasst
- [ ] Ruff und MyPy fehlerfrei
- [ ] Dokumentation aktualisiert
- [ ] CHANGELOG.md Eintrag hinzugefügt

---

## Lizenz

Mit einem Beitrag stimmst du zu, dass dein Code unter der **MIT-Lizenz** veröffentlicht wird.

```
MIT License – Copyright (c) 2024 Xerolux

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## Fragen?

- **GitHub Discussions:** Für allgemeine Fragen
- **GitHub Issues:** Für konkrete Bugs/Features
- **Email:** git@xerolux.de

---

*Zurück: [Home](Home) | Weiter: [Testing](Testing)*
