# Backlog Progress Tracker

**Status**: In Bearbeitung | **Letzte Aktualisierung**: 2026-06-16

Dieses Dokument verfolgt alle Arbeiten aus dem Plan: *Offene Punkte, Bugfixes & Verbesserungen*.

---

## PR-Phasen Übersicht

### PR 1 – Quick Wins & Konsistenz ✅ DONE
- [x] **B1**: API-Versionsanforderung (`requirements.txt` → `>=0.0.31`)
- [x] **B2**: Dev-Dependency Mismatch (pyproject.toml ↔ requirements-dev.txt)
- [x] **D3**: CONTRIBUTING.md: Python/HA-Versionen aktualisieren (3.13→3.14.2, 2025.12→2026.5.0)
- [x] **E3**: .github/CODEOWNERS erstellen, `hacs.json` Formatierung
- [x] **A5**: Lint-Issues (PEP 8, Leerzeilen, bare except)
- [x] **D1**: `docs/RELEASE_NOTES.md` Platzhalter

**PR-Link**: https://github.com/xerolux/violet-hass/pull/373  
**Verantwortlicher**: Claude  
**Status**: Draft, awaiting CI + review  
**Commits**: 5 commits
  1. fix(deps): Update violet-poolController-api requirement to >=0.0.31
  2. fix(deps): Align dev dependencies in pyproject.toml
  3. docs: Update CONTRIBUTING.md with current version requirements
  4. build: Add CODEOWNERS file and fix hacs.json formatting
  5. docs: Add RELEASE_NOTES.md placeholder and BACKLOG_PROGRESS.md

---

### PR 2 – Funktionale Bugfixes ✅ IN PROGRESS
- [x] **A1**: Setpoint-Cache invalidierung (device.py:908,916-924 + climate.py + Test) ✅
- [x] **A2**: Verbindungstest-Logging (config_flow.py:750-751) ✅
- [x] **A3**: Privat→Öffentlich API (update.py) ✅
- [ ] **A4**: Weitere silent-except + None-Handling (deferred to PR 5)

**PR-Link**: *preparing draft*  
**Status**: 3/4 Fixes done, CodeQL warning resolved  
**Commits**: 
  1. fix(A1): Invalidate setpoint cache after successful poll
  2. fix(B2): Correct hallucinated package versions [PART OF PR1]
  3. fix(A2): Add logging to connection test exception handling
  4. fix(A3): Use public API property instead of private _api
  5. fix: Remove unused VioletReadings import

---

### PR 3 – Test-Coverage (ausstehend)
- [ ] **C1**: `parsers.py` Unit-Tests (violet_poolcontroller_api/tests/)
- [ ] **C2**: `readings.py` typed-Properties
- [ ] **C3**: Circuit-Breaker HALF_OPEN-Pfade

**PR-Link**: *ausstehend*  
**Ziel**: nach PR 2

---

### PR 4 – Dokumentation (ausstehend)
- [ ] **D1**: ARCHITECTURE.md erstellen (oder Referenzen entfernen)
- [ ] **D2**: CLAUDE.md aktualisieren (10 statt 7 Plattformen)
- [ ] Fehlende `docs/HA_QUALITY_SCALE_PROGRESS.md`

**PR-Link**: *ausstehend*  
**Ziel**: nach PR 3

---

### PR 5 – CI/CD Härtung (ausstehend)
- [ ] **E1**: Action-Referenzen auf getaggte Releases pinnen
- [ ] **E2**: Test-Matrix Python 3.13 hinzufügen
- [ ] **E3**: CODEOWNERS File

**PR-Link**: *ausstehend*  
**Ziel**: nach PR 4

---

### Backlog/Optional
- [ ] **F**: API-Paket-Verbesserungen (Retry-Jitter, Sanitizer, Rate-Limiter)

---

## Verifizierungs-Checkliste

- [ ] `ruff check custom_components/violet_pool_controller/ --fix` → 0 Fehler
- [ ] `ruff check violet_poolcontroller_api/ --fix` → 0 Fehler
- [ ] `mypy custom_components/violet_pool_controller/` → 0 Fehler
- [ ] `mypy violet_poolcontroller_api/` → 0 Fehler
- [ ] `pytest -v` (alle Tests grün)
- [ ] `pip install -r requirements-dev.txt` (keine Konflikte, B2 resolved)
- [ ] Keine toten Links in Doku (ARCHITECTURE.md, RELEASE_NOTES.md)
- [ ] CI Workflows grün (validate.yml, test-api.yml)

---

## Notizen & Erkenntnisse

- **Branch**: `claude/sharp-dijkstra-b6plaj`
- **Ausgangszustand**: Sauberes Arbeitsverzeichnis, keine offenen GitHub-Issues/PRs
- **Codebasis-Umfang**: 10 HA-Plattformen (vs. 7 dokumentiert) + neue Service/Helper-Module
- **Kritisches Problem**: Setpoint-Cache (A1) kann zu falschen Sollwerten führen
- **Größte Doku-Lücke**: ARCHITECTURE.md, CLAUDE.md-Drift

---

## Commits pro Phase

### PR 1 Commits
```
[ ] Commit 1: Update requirements.txt API version to >=0.0.31
[ ] Commit 2: Align dev dependencies (pyproject.toml ↔ requirements-dev.txt)
[ ] Commit 3: docs: Update CONTRIBUTING.md Python & HA versions
[ ] Commit 4: build: Add CODEOWNERS file, fix hacs.json formatting
[ ] Commit 5: lint: Fix PEP 8 violations (bare except, whitespace)
[ ] Commit 6: docs: Add RELEASE_NOTES.md placeholder
```

---

