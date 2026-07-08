# Design: Security Hardening + CI-Gap Closing

**Datum:** 2026-07-08
**Scope:** Safety-Critical Security Fixes (S1–S5) + Tests/CI Holes (T1–T4)
**Status:** Draft — wartet auf Review

## Kontext & Problem

Die violet-hass Integration steuert **reale Pool-Ausrüstung** (Chlor-/pH-Dosierung, Pumpen, Rückspülung, Wassernachfüllung). Version 2.0.0-beta.10 führte eine Sicherheitsarchitektur ein ("auto-disable unsafe switches", "Pflicht-Zeitangaben"). Eine vierschichtige Analyse hat ergeben, dass diese Sicherheitsarchitektur **nur ein UI-Gate ist, keine echte Kontrollebene**, und dass die Integrationstest-Suite **nie in CI läuft**.

Die good-news-Bilanz: keine blockierenden Calls in async, korrektes Connection-Reuse, saubere Entity-Erstellung, gebounded Buffers. Die Codebasis ist solide — die Löcher sind im Sicherheits-Wiring und in der CI-Governance.

## Ziele

1. **Sicherheit als echte Kontrollebene** — jede Code-Pfade, die Dosierung/Backwash/Refill steuert, geht durch denselben Safety-Gate.
2. **Mandatory bounded inputs** — kein Service ohne Schema; keine unvalidierten Eingaben an sicherheitskritische Aktoren.
3. **Restart-sichere Auto-Stop-Timer** — ein laufender Refill/Backwash wird auch nach HA-Neustart rechtzeitig gestoppt.
4. **CI-gated Tests** — die 475 Integrationstests laufen bei jedem PR; Coverage wird gemessen.

## Nicht-Ziele

- Code-Quality-Refactors (Q1–Q5: Boilerplate-Extraktion, Doku-Drift) — separater Durchlauf.
- Performance-Optimierungen (P1–P4: asyncio.gather, Dict-Kopien) — separater Durchlauf.
- API-Paket-Änderungen — alle Fixes in `custom_components/`, außer Imports.

---

## Design

### Teil A: Safety-Gate zentralisieren (S1, S3, S4 des Audits)

#### A.1 Ein zentraler `SafetyGuard` statt verteiltem `_safety_locks`-Dict

**Problem heute:** `VioletServiceManager._safety_locks` (service_manager.py:24) ist ein einfaches in-memory Dict. `check_safety_lock`/`set_safety_lock` werden nur von `handle_smart_dosing` aufgerufen. Jeder andere Pfad (switch toggle, manual_dosing_http, control_backwash_http, control_refill_http) bypassed den Check komplett.

**Design:** Neue Klasse `SafetyGuard` in `safety_guard.py`, die das Safety-Lock-Konzept + Restart-Persistenz + Logging vereinheitlicht.

```
safety_guard.py
├── class SafetyGuard
│   ├── __init__(self, hass, store)  # hass.storage-Backed
│   ├── async async_setup()          # lädt persistierte Deadlines, rearmt Timer
│   ├── async enforce(self, device_key, *, safety_override=False) -> None
│   │     # wirft HomeAssistantError wenn Lock aktiv (außer safety_override=True)
│   ├── async arm(self, device_key, duration_seconds, *, stop_target) -> None
│   │     # stop_target: serialisierbares dict {api_method, args, kwargs}
│   │     # z.B. {"api_method": "set_switch_state", "args": ["REFILL"],
│   │     #       "kwargs": {"action": "OFF"}}
│   │     # setzt Lock + startet in-memory Auto-Stop-Task + persistiert Deadline
│   ├── async disarm(self, device_key) -> None   # clears Lock + persisted Deadline
│   ├── _log_safety_event(self, level, device_key, message) -> None
│   └── UNSAFE_SWITCH_KEYS (canonical set, importiert von switch.py)
```

**Restart-Persistenz:** Beim `arm()` wird ein serialisierbares `stop_target`-Dict in `hass.storage` abgelegt: `{device_key: {deadline_epoch, stop_target}}`. `stop_target` ist ein rein datenbasiertes Dict (`{api_method, args, kwargs}`), das beim Rearmen in einen echten API-Aufruf rekonstruiert wird — **kein** Closure (Closures sind nicht serialisierbar). Beim `async_setup()` werden noch aktive Deadlines gelesen und Timer rearmed; bereits abgelaufene Deadlines führen das Stop-Kommando sofort aus. Das schließt S4.

**Rekonstruktion:** `SafetyGuard` hält eine Referenz auf das `VioletPoolAPI`-Objekt des jeweiligen Coordinators und ruft `getattr(api, stop_target["api_method"])(*args, **kwargs)` auf. Die Zuordnung `device_key → coordinator/api` erfolgt über `hass.data[DOMAIN]`.

**Verhalten:**
- `enforce()` konsultiert Lock + loggt WARNING bei `safety_override=True` (schließt M2 des Audits).
- `arm()` startet gleichzeitig den in-memory Auto-Stop-Task **und** persistiert die serialisierbare Deadline. Bei HA-Neustart rearmt `async_setup()`.
- `disarm()` (aufgerufen bei `smart_dosing` `stop`-Aktion und manuellem Refill/Backwash-stop) cleart beides.

#### A.2 Wiring: jeder unsichere Pfad geht durch `SafetyGuard`

Folgende Pfade werden geändert, sodass sie `SafetyGuard` konsultieren:

| Code-Pfad | Datei:Zeile | Änderung |
|-----------|-------------|----------|
| `handle_smart_dosing` (manual_dose) | service_control.py:164-187 | `manager.safety_guard.enforce(...)` statt `manager.check_safety_lock`; `arm()` statt `set_safety_lock` |
| `handle_smart_dosing` (auto/stop) | service_control.py:189-205 | `stop` cleart den Lock; `auto` bleibt ungesperrt (controller-seitige Limits) |
| `handle_manual_dosing_http` | service_control.py:680-709 | **neu:** `enforce()` vor `trigger_manual_dosing`, `arm()` danach |
| `handle_control_backwash_http` | service_control.py:620-678 | **neu:** `enforce()` + persistenter `arm()` statt `asyncio.sleep` Background-Task |
| `handle_control_refill_http` | service_control.py:711-769 | **neu:** `enforce()` + persistenter `arm()` |
| `VioletSwitch._set_switch_state` (DOS_/BACKWASH/REFILL keys) | switch.py:479-492 | **neu:** bevor Kommando dispatched wird, `enforce()`; nach Erfolg `arm()` mit duration |

**Key-Mapping:** `SafetyGuard` braucht eine Map `entity_key → safety_device_key`. Beispiel: `DOS_1_CL → chlorine`, `BACKWASH → backwash`. Diese wird im SafetyGuard als Konstante geführt, referenziert `UNSAFE_SWITCH_KEYS` aus switch.py (single source of truth — schließt M4 des Audits).

### Teil B: Fehlende Schemas + Range-Korrektur (S2, S5)

#### B.1 `control_pump`-Schema hinzufügen (S2)

**Problem:** `services.py:78` registriert `control_pump` mit `schema=schemas.get("control_pump")` → `None`. Handler macht `call.data["action"]` → `KeyError` wenn fehlt. Dauer bis 86400s.

**Fix:** Schema in `get_service_schemas()`:
```python
"control_pump": vol.Schema(vol.All(
    vol.Schema({
        vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
        vol.Required("action"): vol.In(
            ["speed_control", "force_off", "eco_mode", "boost_mode", "auto"]
        ),
        vol.Optional("speed", default=2): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_PUMP_SPEED, max=MAX_PUMP_SPEED)
        ),
        vol.Optional("duration", default=0): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=3600)
        ),
    }),
    cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
)),
```
Handler wird robuster (kein `KeyError` mehr), Dauer auf 3600s begrenzt.

#### B.2 `set_dosing_target`-Range nach Dosiersystem differenzieren (S5)

**Problem:** `target_value: Range(0, 100)` für alle Systeme. pH sollte 6.8–7.8, Chlor 0–10, etc.

**Fix:** Eine `vol.All`-Validator-Funktion, die das gesamte Dict sieht und `target_value` abhängig vom `dosing_system` prüft:
```python
DOSING_TARGET_RANGES = {
    "ph_minus": (6.8, 7.8),
    "ph_plus": (6.8, 7.8),
    "chlorine": (0.0, 10.0),
    "electrolysis": (0.0, 10.0),
    "flocculant": (0.0, 100.0),
    "h2o2": (0.0, 100.0),
}

def _validate_dosing_target(data: dict) -> dict:
    """Validate target_value range based on dosing_system."""
    ds = data["dosing_system"]
    val = float(data["target_value"])
    lo, hi = DOSING_TARGET_RANGES.get(ds, (0.0, 100.0))
    if not (lo <= val <= hi):
        raise vol.Invalid(
            f"target_value {val} out of range for {ds}: allowed {lo}-{hi}"
        )
    return data
```
Das Schema wrappt das inner Schema mit `vol.All(inner_schema, _validate_dosing_target)`. So bleibt ein einziges `set_dosing_target`-Schema (keine Aufspaltung), und die Range ist kontextabhängig.

#### B.3 `configure_dosing` config_key-Whitelist (S5)

**Problem:** `config_key: cv.string` erlaubt beliebige Suffixe → kann `max_daily_ml` o.ä. aushebeln.

**Fix:** Whitelist erlaubter Suffixe:
```python
ALLOWED_DOSING_CONFIG_KEYS = {
    "use", "set_ppm", "set_ph", "start", "can_amount",
    "max_runtime", "speed", "day_start", "day_end",
    # explizit NICHT: max_daily_ml (separater Service set_dosing_max_daily)
}
vol.Required("config_key"): vol.In(sorted(ALLOWED_DOSING_CONFIG_KEYS)),
```

### Teil C: Switch-Pfad härten (S3)

#### C.1 `_validate_duration` mit oberer Schranke für unsichere Keys

**Problem:** `switch.py:_validate_duration` akzeptiert beliebig große Werte; DOS_-Pfad hat Default 30s aber keine echte Obergrenze. BACKWASH/REFILL ON-Pfad sendet gar keine Duration.

**Fix:** In `_set_switch_state`, wenn `key in UNSAFE_SWITCH_KEYS`:
- Für DOS_-Keys: Duration aus kwargs oder Default; begrenzt auf `MAX_DOSING_DURATION` (300s, aus service_helpers).
- Für BACKWASH/BACKWASHRINSE/REFILL: **erfordert** explizite Duration; wirft `HomeAssistantError` wenn fehlt, statt stillschweigend ON ohne Auto-Stop zu senden.

```python
if key in UNSAFE_SWITCH_KEYS:
    await self.coordinator.device.safety_guard.enforce(key, ...)
    duration = self._validate_duration(kwargs.get("duration"), max_sec=MAX_FOR_KEY[key])
    # ... send command ...
    await self.coordinator.device.safety_guard.arm(key, duration, stop_callback=...)
```

### Teil D: CI-Gap schließen (T1–T4)

#### D.1 tox.ini um Tests + Lint erweitern (T1, T9)

**Problem:** `tox.ini:14` führt nur `ruff check custom_components/violet_pool_controller` aus.

**Fix:**
```ini
[testenv]
deps =
    py312,py313,py314: ruff>=0.15.0
    py312,py313: pytest>=8.3.0
    py312,py313: pytest-asyncio>=0.24.0
    py312,py313: pytest-cov>=6.0.0
    py312,py313: pytest-homeassistant-custom-component>=0.13.337
    py312,py313: -r requirements.txt
commands =
    py314: ruff check custom_components/violet_pool_controller tests
    py314: ruff format --check custom_components/violet_pool_controller tests
    py312,py313: ruff check custom_components/violet_pool_controller tests
    py312,py313: ruff format --check custom_components/violet_pool_controller tests
    py312,py313: pytest tests/ -q --cov=custom_components/violet_pool_controller --cov-report=term-missing
```
(Rationale: py314 hat noch keine `pytest-homeassistant-custom-component` wheels; dort nur lint. py312/313 macht lint + tests + coverage.)

#### D.2 validate.yml um Test-Reporting erweitern

Die `validate`-Job ruft bereits `tox -e ${{ matrix.tox-env }}` auf. Da tox jetzt Tests ausführt, wird validate.yml automatisch grün/rot je nach Testergebnis. Zusätzlich `permissions: contents: read` auf Workflow-Ebene setzen.

#### D.3 Coverage-Konfiguration in pyproject.toml (T2)

```toml
[tool.coverage.run]
source = ["custom_components/violet_pool_controller"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 60  # konservativer Start; wird angehoben
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

#### D.4 `test_improvements.py` bereinigen (T4)

- `test_precompiled_regex_performance` (flaky timing) löschen.
- Tests, die lokale Helper testen statt echten Code (`test_credential_strength_checks`, `test_circuit_breaker_states` lokale Konstanten, `test_entity_caching_logic`, `test_async_timing_functions`), löschen — echte Coverage existiert bereits in `test_sanitizer.py`, `test_circuit_breaker.py`.

#### D.5 Neue Tests für Safety-Critical Paths (T3)

Neue Test-Datei `tests/test_safety_guard.py`:
- `test_enforce_blocks_when_lock_active`
- `test_enforce_allows_with_safety_override_logs_warning`
- `test_arm_sets_lock_and_persists_deadline`
- `test_setup_rearms_active_deadline_after_restart`
- `test_setup_executes_expired_deadline_immediately`
- `test_manual_dosing_http_calls_enforce_and_arm`
- `test_control_refill_http_calls_enforce_and_arm`
- `test_control_backwash_http_calls_enforce_and_arm`
- `test_switch_dos_key_requires_duration`
- `test_switch_refill_key_rejects_on_without_duration`

Neue Tests in `tests/test_service_control.py` erweitern:
- `test_control_pump_missing_action_raises_clean_error` (Schema existiert → KeyError weg)
- `test_control_pump_duration_clamped_to_3600`

Neue Tests in `tests/test_service_schemas.py` (neu oder in bestehendem):
- `test_set_dosing_target_ph_range_6_8_to_7_8`
- `test_set_dosing_target_chlorine_range_0_to_10`
- `test_set_dosing_target_rejects_ph_100`
- `test_configure_dosing_rejects_unknown_config_key`

---

## Datei-Änderungsübersicht

### Neu
- `custom_components/violet_pool_controller/safety_guard.py` — SafetyGuard-Klasse
- `tests/test_safety_guard.py` — Safety-Guard-Tests
- `tests/test_service_schemas.py` — Schema-Validierungs-Tests (falls nicht existierend)

### Geändert
- `custom_components/violet_pool_controller/service_manager.py` — delegiert an SafetyGuard statt eigenem `_safety_locks`-Dict
- `custom_components/violet_pool_controller/service_control.py` — 5 Handler gehen durch SafetyGuard; `handle_control_pump` robuster
- `custom_components/violet_pool_controller/switch.py` — `_set_switch_state` für unsichere Keys durch SafetyGuard; `UNSAFE_SWITCH_KEYS` wird kanonisch
- `custom_components/violet_pool_controller/service_schemas.py` — `control_pump`-Schema, `set_dosing_target`-Ranges, `configure_dosing`-Whitelist
- `custom_components/violet_pool_controller/__init__.py` — SafetyGuard-setup beim Integration-Setup; `UNSAFE_SWITCH_KEYS` aus switch.py importiert (DRY)
- `tox.ini` — pytest + coverage + ruff format/check
- `.github/workflows/validate.yml` — `permissions: contents: read`
- `pyproject.toml` — `[tool.coverage.*]`
- `tests/test_improvements.py` — flaky/wertlose Tests entfernt

---

## Build-Sequenz (Review-Checkpoints nach jedem Schritt)

1. **Schritt 1 — SafetyGuard + Persistenz** (A.1): neue `safety_guard.py`, unit-getestet isoliert. Checkpoint: `pytest tests/test_safety_guard.py` grün.
2. **Schritt 2 — Handler-Wiring** (A.2): 5 Handler + Switch-Pfad durch SafetyGuard. Checkpoint: bestehende Tests grün + neue Wiring-Tests.
3. **Schritt 3 — Schemas** (B.1–B.3): control_pump/dosing_target/configure_dosing. Checkpoint: Schema-Tests grün.
4. **Schritt 4 — Switch-Härtung** (C.1): Duration-Begrenzungen + Refill/Backwash-ON benötigt Duration. Checkpoint: Switch-Tests grün.
5. **Schritt 5 — CI** (D.1–D.5): tox/coverage/workflows/test_cleanup. Checkpoint: `tox -e py313` lokal grün incl. pytest.
6. **Schritt 6 — Verifikation**: volle Suite `pytest tests/ -q` + `ruff check` + `ruff format --check`.

## Risiken & Mitigationen

- **Breaking Change für Automations:** Schemas werden strenger. Bisherige Aufrufe mit unvalidierten Feldern schlagen fehl. **Mitigation:** Das ist beabsichtigt (Sicherheit); Changelog-Eintrag + minor-version-bump.
- **Persistenz-Overhead:** `hass.storage`-Schreiben pro `arm()`. Bei typischen Pool-Nutzung (wenige Dosierungen/Stunde) vernachlässigbar.
- **py314 kann keine Integrationstests ausführen** (keine `pytest-homeassistant-custom-component` wheels). **Mitigation:** py314 macht nur lint; py312/313 macht tests. Acceptable da HA 2026.5 py314 noch nicht shipped.

## Erfolgskriterien

- [x] Jede Code-Pfad zu DOS_*/BACKWASH/REFILL geht durch `SafetyGuard.enforce()` + `.arm()`.
- [x] `control_pump` hat ein Schema; kein Service ohne Schema mehr.
- [x] `set_dosing_target` validiert pH/Chlor-spezifische Ranges.
- [x] Auto-Stop-Deadlines überleben HA-Neustart (Test beweist es).
- [x] `tox -e py313` führt pytest aus und MISST Coverage.
- [x] Keine flaky Timing-Tests mehr in `test_improvements.py`.
- [x] `pytest tests/ -q` ≥ 475 Tests, 0 Errors (mit installierter `pytest-homeassistant-custom-component`).
