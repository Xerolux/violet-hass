## Migration: API zurück ins Standalone-Repo `violet-poolController-api`

### Phase 1 — Standalone-Repo aktualisieren (v0.0.33 → v0.0.35)

Im Repo `C:/Users/basti/Documents/GitHub/violet-poolController-api` auf `main`:

**1a. API-Quellcode + Tests + Docs überschreiben** mit der aktuellen eingebetteten Version aus `violet-hass/violet_poolcontroller_api/`:
- `violet_poolcontroller_api/*.py` (api, circuit_breaker, const_api, const_devices, parsers, readings, utils_rate_limiter, utils_sanitizer, `__init__.py`, py.typed)
- `tests/*.py` (test_api, test_api_smoke, test_circuit_breaker, test_mock_server, test_parsers, test_readings, mock_server, conftest, `__init__`)
- `docs/HA_ADDON_REFERENCE.md` (einzige geänderte Doc)
- `CHANGELOG.md`, `README.md`, `AGENTS.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, alle `RELEASE_NOTES_*.md`

**1b. `pyproject.toml` angleichen, aber URLs auf das Standalone-Repo zurücksetzen.** Die eingebettete Version zeigt die Projekt-URLs auf `violet-hass` — diese zurück auf `violet-poolController-api` setzen:
- `Homepage` / `Bug Tracker` / `Changelog` → `github.com/Xerolux/violet-poolController-api`
- Version `0.0.35` übernehmen
- Die `[tool.setuptools.packages.find]` / `[tool.setuptools.package-data]` Sektionen und `addopts = "-p no:homeassistant"` aus der eingebetteten Version übernehmen (die braucht das Standalone-Repo nicht, schadet aber nicht — genauer: `addopts` bezieht sich auf das HA-Plugin und ist im Standalone ohne HA unschädlich; ich entferne es zugunsten der sauberen Standalone-Konfiguration)
- aiohttp-Constraint `>=3.11.0,<3.15` (v0.0.34-Fix) übernehmen

**1c. `setup.py`** version auf `0.0.35` und aiohttp-Constraint `<3.15` aktualisieren.

**1d. `tox.ini`** — unverändert lassen (deckt py312/313/314 + lint ab, passt zur eingebetteten Version).

**1e. `.github/workflows/`** des Standalone-Repos **unverändert lassen** (ci.yml, release.yml, pages.yml, wiki-sync.yml, dev-release.yml).

**1f. `.gitignore`** unverändert lassen.

### Phase 2 — API aus `violet-hass` entfernen

Im Repo `violet-hass` auf `main`:

**2a. Verzeichnis `violet_poolcontroller_api/` komplett löschen** (gesamter embedded-Tree inkl. Tests, docs, egg-info, Caches).

**2b. `requirements-dev.txt`** — Zeile `-e ./violet_poolcontroller_api[test]` + ihren Kommentar entfernen. Die API wird stattdessen über `requirements.txt` (`violet-poolController-api>=0.0.35` von PyPI) installiert.

**2c. `pyproject.toml` (root)** bereinigen:
- `mypy_path = "violet_poolcontroller_api"` entfernen
- `explicit_package_bases = true` entfernen
- Den `[[tool.mypy.overrides]]`-Block für `module = "violet_poolcontroller_api.*"` entfernen

**2d. `tests/conftest.py`** — den API-Pfad-Hack entfernen (Zeilen ~18–27: Kommentarblock + `_api_src_dir`-Logik). Die restliche Mock-Logik bleibt (sie greift auf die via requirements installierte API oder deren Mock zurück).

**2e. `tests/live_*_check.py`** (4 Skripte: live_dosstart_check.py, live_dosstop_check.py, live_phm_check.py, live_readonly_check.py) — die `sys.path.insert(0, ".../violet_poolcontroller_api")`-Zeile entfernen. Die Skripte importieren `violet_poolcontroller_api` dann über die reguläre Installation.

**2f. API-bezogene Workflows löschen** (laut deiner Entscheidung):
- `.github/workflows/publish-api.yml` (löschen)
- `.github/workflows/test-api.yml` (löschen)
- `.github/workflows/update-api-dependency.yml` (löschen)
- `.github/workflows/security.yml` — die `violet_poolcontroller_api/violet_poolcontroller_api/**`-Pfad-Trigger entfernen (nur die `custom_components/**`-Trigger behalten)

### Phase 3 — Validierung (vor Commit)

- `python -m pytest tests/test_api.py -q` im Standalone-Repo → Tests grün gegen v0.0.35
- `ruff check violet_poolcontroller_api tests` im Standalone-Repo → kein Lint-Fehler
- In `violet-hass`: `grep -rn "violet_poolcontroller_api/" .` → keine verbliebenen Pfad-Referenzen (nur noch `from violet_poolcontroller_api import ...`-Paket-Imports, die legitim sind)
- Sanity: `requirements.txt` verlangt weiterhin `violet-poolController-api>=0.0.35`

### Offen / Hinweis
- **Keine Commits/Push ohne dein Go.** Ich führe die Änderungen aus, zeige dir das Ergebnis, und du commitest selbst (oder sagst mir, dass ich committen soll).
- Der `tests/test_api.py` im `violet-hass`-Root bleibt **unverändert** — er ist ein Integration-Test, der die HA-Konstanten (`API_PRIORITY_*`) mit der API-Klasse zusammen testet und läuft gegen die über `requirements.txt` installierte API.
- `conftest_api_mock.py` bleibt unverändert (Fallback-Mock für Umgebungen ohne installierte API).