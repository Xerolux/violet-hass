# Backlog Progress Tracker

**Status**: Phase 1+2 ✅ ABGESCHLOSSEN (PR #373), Phase 3+ geplant | **Letzte Aktualisierung**: 2026-06-16 11:05 UTC

Dieses Dokument verfolgt alle Arbeiten aus dem Plan: *Offene Punkte, Bugfixes & Verbesserungen*.

---

## Executive Summary

**Phase 1+2 Abgeschlossen** ✅
- **11 Commits** in PR #373 (Draft)
- **2 Phasen kombiniert** für Effizienz:
  - Phase 1: Quick Wins & Konsistenz (6 commits)
  - Phase 2: Funktionale Bugfixes (5 commits)
- **Highlights**:
  - 🔴 **A1**: Kritischer Setpoint-Cache Bug behoben (stale values nach externen Änderungen)
  - ⚠️ **B2**: Halluzinierte Package-Versionen in pyproject.toml korrigiert (Gemini Code Review)
  - 🧪 **Test Suite**: Neue Test für Cache-Invalidierung
  - 📝 **Dokumentation**: RELEASE_NOTES.md, BACKLOG_PROGRESS.md, CODEOWNERS hinzugefügt

**Phase 3-5 Geplant** 🔄
- Test-Coverage für API-Paket (benötigt Python 3.12+)
- Dokumentation (ARCHITECTURE.md, CLAUDE.md updates)
- CI-Härtung (Action-Pinning, Test-Matrix)

**Umgebungsbeschränkung**: Python 3.11 Container (benötigt 3.12+ für Violet API Tests)

---

## PR-Phasen Übersicht

### PR 1+2 (Combined) – Quick Wins + Functional Bugfixes ✅ DONE
- [x] **B1**: API-Versionsanforderung (`requirements.txt` → `>=0.0.31`)
- [x] **B2**: Dev-Dependency Mismatch (pyproject.toml ↔ requirements-dev.txt) ⚠️ CORRECTED
- [x] **D3**: CONTRIBUTING.md: Python/HA-Versionen aktualisieren (3.13→3.14.2, 2025.12→2026.5.0)
- [x] **E3**: .github/CODEOWNERS erstellen, `hacs.json` Formatierung
- [x] **A5**: Lint-Issues (PEP 8, Leerzeilen, bare except)
- [x] **D1**: `docs/RELEASE_NOTES.md` Platzhalter
- [x] **A1**: Setpoint-Cache invalidierung ✅ (CRITICAL BUG FIX)
- [x] **A2**: Verbindungstest-Logging ✅
- [x] **A3**: Privat→Öffentlich API ✅
- [ ] **A4**: Weitere silent-except + None-Handling (deferred to PR 4)

**PR-Link**: https://github.com/xerolux/violet-hass/pull/373  
**Verantwortlicher**: Claude  
**Status**: Draft, ready for review  
**Commits**: 11 commits
  - Phase 1: 6 commits (dependencies, docs, build)
  - Phase 2: 5 commits (bugfixes, tests)
  
**Besonderheiten**:
- B2: Halluzinierte Versionen in pyproject.toml gefunden & korrigiert (Code Review)
- A1: Kritischer Bug → neue Test Suite ergänzt
- CodeQL: Unused import entfernt

---

### PR 3 – Test-Coverage (GEPLANT)
- [ ] **C1**: `parsers.py` Unit-Tests (violet_poolcontroller_api/tests/)
- [ ] **C2**: `readings.py` typed-Properties
- [ ] **C3**: Circuit-Breaker HALF_OPEN-Pfade

**Status**: Ausstehend – benötigt Python 3.12+ Umgebung  
**Ziel**: Nach PR 1+2 genehmigt

---

### PR 4 – Dokumentation + A4 Bugfixes (GEPLANT)
- [ ] **D1**: ARCHITECTURE.md erstellen (oder Referenzen entfernen)
- [ ] **D2**: CLAUDE.md aktualisieren (10 statt 7 Plattformen)
- [ ] **D1b**: Fehlende `docs/HA_QUALITY_SCALE_PROGRESS.md`
- [ ] **A4**: Weitere silent-except + None-Handling (config_flow_utils/sensor_helper.py, service_diagnostics.py)

**Status**: Ausstehend  
**Ziel**: Nach PR 3

---

### PR 5 – CI/CD Härtung (GEPLANT)
- [ ] **E1**: Action-Referenzen auf getaggte Releases pinnen (security.yml, validate.yml)
- [ ] **E2**: Test-Matrix Python 3.13 hinzufügen
- [ ] **E3**: .github/CODEOWNERS erstellen → ✅ BEREITS GEMACHT IN PR 1+2

**Status**: Ausstehend  
**Ziel**: Nach PR 4

---

### Backlog/Optional
- [ ] **F**: API-Paket-Verbesserungen (Retry-Jitter, Sanitizer, Rate-Limiter)
  - Größere Refaktorierungen, nur bei Bedarf

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

