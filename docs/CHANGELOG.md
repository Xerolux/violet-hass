# Changelog

All notable changes to this project will be documented in this file.
## [1.0.0] - 2026-02-06

## v1.0.0 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features | Neue Funktionen

- Fix critical API bug, improve startup, add German state descriptions (fa94d08)
- feat: Diagnostic sensors, HA 2026 compatibility, security improvements (v1.0.7-alpha.4) (4538860)
- Add security utilities for authentication and SSL validation (8d64181)
- ✨ Add composite state sensors (PUMPSTATE, HEATERSTATE, SOLARSTATE) (7fd6989)
- ✨ Add dosing state array sensors (DOS_*_STATE) (88aae9c)
- add-controller-selection (75a2eb8)
- Add HA test directories to .gitignore (d3e168b)
- Add Home Assistant test infrastructure and test results documentation (4f0c7f8)
- Remove add-controller-selection (e57ab64)
- Add ProCon.IP controller support to config flow (85f9ae3)
- new release workflow (b715be0)
- feat: Add reauthentication, reconfiguration, and diagnostic sensors (ed282c1)
- feat: Add intuitive ON/OFF/AUTO control with Select entities and Dashboard templates (7ac8301)
- Improve UX: Add feature selection to options flow and enhance UI organization (ed6b4c6)
- feat: Add GitHub Codespaces prebuild configuration (cdc97f6)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- feat: Make DMX scene updates fault-tolerant (f914a00)
- Add support for mixed-case system sensor keys (f6f4c10)
- Fix firmware version extraction and add setup guide (6f7aed8)
- Add device info lookup to API (7d53ce0)
- Add error handling utilities for config flow (1ee9bf2)
- 🐛 Fix: Schema-Validierung für Feature-Selection (dict comprehension) (dda5028)
- 🐛 Fix: Config Flow Feature-Selection und Platzhalter (e29ae93)
- ✨ Feature: Multi-Controller Support mit Auto-Bereichen (ff3f7fc)
- ✨ Feature: Auto-Recovery + Enhanced Input Sanitization (bb07c09)
- ✨ Add explicit pre-release support to workflow (96a4bc9)

### 🚀 Improvements | Verbesserungen

- Fix critical API bug, improve startup, add German state descriptions (fa94d08)
- 📝 Release v1.0.7-alpha.3 - Update changelog and version files (33f1eef)
- Improve API error handling and stability (2dc238a)
- Merge pull request #182 from Xerolux/fix-and-optimize-violet-pool-controller-4890044213630928459 (83329c5)
- Fix critical bugs, optimize entity logic, and improve type safety (d82545a)
- 🐛 Fix 18 bugs and optimize code performance (69af24d)
- 📝 Release v1.0.7-alpha.2 - Update changelog and version files (3517131)
- Fix sed regex in release workflow for CLAUDE.md version update (f7ccc6d)
- 📝 Release v1.0.7-alpha.1 - Update changelog and version files (1d9d07c)
- improve-setup-reauthentication (cb143dc)
- optimize-ha-2026 (f63c755)
- Optimize Violet Pool Controller integration for HA 2026 (73ad32a)
- update-dependencies-for-compatibility (e37ce73)
- Update dependencies and compatibility baseline (7404162)
- refactor-config-flow-tests (9b170e8)
- Refactor config flow and improve test coverage (279a658)
- addon-bugfix-ui-refactor (65c0a5b)
- optimize-and-ensure-functionality (0870b0f)
- Fix bugs, optimize code and ensure functionality (ce025d4)
- Improve UX: Add feature selection to options flow and enhance UI organization (ed6b4c6)
- Merge pull request #168 from Xerolux/refactor-config-flow-sensor-selection-12389334522538732123 (e9e8999)
- Refactor config flow sensor selection (84b467f)
- Merge pull request #166 from Xerolux/improve-validation-config-flow (bd5e0b9)
- Merge pull request #167 from Xerolux/improve-validation-config-flow-5901907404985322212 (4249f2e)
- Merge branch 'main' into improve-validation-config-flow to resolve conflicts (7caff24)
- Improve validation and UI in config flow by using NumberSelector (d33dd3c)
- Merge pull request #163 from Xerolux/claude/update-readme-01GdiF4dE7x48kixTQs1mbRk (243046c)
- docs: Update README with v0.2.0-beta.4 changelog and improvements (7e8a039)
- docs: Update CLAUDE.md with comprehensive codebase documentation (90b30d0)
- 📝 Update version to v0.2.0-beta.4 and release notes (6c12109)
- chore: Update .gitignore to exclude test virtual environments (1653084)
- Merge pull request #156 from Xerolux/refactor/code-quality-improvements (712b9f2)
- refactor: Improve code quality and documentation (0a538f5)
- Fix calibration history parsing bug and improve documentation (26332dd)
- Refactor tests and fix logic bugs (2fb1046)
- Fix controller connection setup errors and improve retry logic (3d75ed2)
- Update config_flow.py (d57e4d1)
- Update config_flow.py (c1a8406)
- 🔧 Refactor: Harmonisierung und Code-Optimierung (a9302b2)
- 📝 Update version to v0.2.0-beta.3 and release notes (31e18d7)
- 📝 Update version to v0.2.0-beta.2 and release notes (0713c62)
- 🔧 Refactor: Modular code structure + Security improvements (3946e22)
- 📝 Update version to v0.2.0-beta.1 and release notes (814cd1c)
- Update README.md (8f43330)
- Update README.md (3630abb)
- 📝 Update version to v0.2.0 and release notes (4887b5b)

### 🔧 Bug Fixes | Fehlerbehebungen

- 🔧 Fix hassfest validation: remove homeassistant key, fix URLs (b3757ae)
- 📦 Release v1.0.0 - Fix hassfest validation, version bump (6ae9fea)
- Fix critical API bug, improve startup, add German state descriptions (fa94d08)
- Merge pull request #184 from Xerolux/fix-api-error-handling-3216800569233088969 (553a2ad)
- Fix CI validation failures (manifest and translations) (5c7ca9e)
- Fix CI validation failures (manifest and translations) (eea40c2)
- Fix CI validation failures (api formatting and strings.json schema) (8a12446)
- fix-api-stability-performance (7dd4038)
- Fix type checking and linting errors (aff549e)
- Fix API stability and performance issues (761dfcc)
- Merge pull request #182 from Xerolux/fix-and-optimize-violet-pool-controller-4890044213630928459 (83329c5)
- Fix critical bugs, optimize entity logic, and improve type safety (d82545a)
- 🐛 Fix 18 bugs and optimize code performance (69af24d)
- Fix sed regex in release workflow for CLAUDE.md version update (f7ccc6d)
- display fix (459c3a1)
- Firmware & State Fix (981abfd)
- bugfix release notes (f17acd9)
- addon-bugfix-ui-refactor (65c0a5b)
- fix: Critical bugfixes, UI/UX improvements and code quality enhancements (cf3a920)
- Fix bugs, optimize code and ensure functionality (ce025d4)
- fix: Resolve critical bugs and compatibility issues (292bcf7)
- Merge pull request #169 from Xerolux/claude/fix-smart-home-system-01Lu6UN2XXxKLJaQVHEnT1si (8ccf2ff)
- Merge pull request #164 from Xerolux/bugfix/manual-dosing-elektrolyse (c60dbf6)
- Fix manual dosing for Elektrolyse by using shared DOSING_FUNCTIONS (98f29f5)
- fix: Correct Codespaces prebuild configuration instructions (01f8287)
- Merge pull request #160 from Xerolux/claude/fix-liquid-syntax-error-01G7gM75JFPfS5mprghbgDyC (6e209b7)
- fix: Wrap Jinja2 templates with Liquid raw tags to prevent Jekyll parsing errors (8cb0cc7)
- Merge pull request #157 from Xerolux/claude/check-fix-errors-01WwCxsoB299aFxjZPHHpvyU (df15d72)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- fix: Resolve all mypy type errors (1927793)
- fix (516ec2c)
- Merge pull request #155 from Xerolux/fix/dmx-scene-error-handling (d304b7b)
- Merge pull request #154 from Xerolux/bugfix-calibration-history-and-docs (b41122d)
- Fix calibration history parsing bug and improve documentation (26332dd)
- Merge pull request #153 from Xerolux/fix-tests-and-bugs (f2775fc)
- Refactor tests and fix logic bugs (2fb1046)
- Merge pull request #150 from Xerolux/fix-sensors-config-flow (60af05f)
- Fix config flow, units, and pump status display (00bd86d)
- Merge pull request #149 from Xerolux/claude/fix-config-entry-option-flow-01EYbGFeqcKCZNMPuQunasZ3 (b422c07)
- Fix deprecated config_entry assignment and TypeError in options flow (6590491)
- Merge pull request #148 from Xerolux/codex/fix-invalid-unit-for-temperature-sensors (d3f86ae)
- Merge pull request #146 from Xerolux/codex/fix-pump-status-display-issue (da3ffe7)
- Merge pull request #145 from Xerolux/claude/fix-pool-sensor-unit-01Urx5WUsVtBiNHVZPJTnQXT (bd86ee9)
- Fix unit changes breaking Home Assistant statistics (fd6b633)
- Merge pull request #143 from Xerolux/claude/fix-firmware-pump-status-01LocFcDhW9MQwm1Bf4Wpzg8 (55717f4)
- Fix firmware display and temperature sensor units (3cacf54)
- Merge pull request #142 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (f55cc06)
- Fix firmware version extraction and add setup guide (6f7aed8)
- Merge pull request #141 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (65645c2)
- Fix missing sensors: Handle empty sensor selection correctly (2225fce)
- Merge pull request #140 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (8a61c2d)
- Merge pull request #139 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (42e8e38)
- Fix controller connection setup errors and improve retry logic (3d75ed2)
- Merge pull request #138 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (6eab77b)
- Fix config flow schema serialization and validation errors (fdc6cd4)
- Merge pull request #137 from Xerolux/claude/fix-config-setup-flow-01TZ2YNLshd1qLU6kjhiXh9a (624495c)
- Fix config flow: Change step_id from 'welcome' to 'user' (e70d307)
- fix (34cac7b)
- Merge pull request #136 from Xerolux/codex/fix-violet-pool-controller-integration-error (fc8d347)
- Fix options flow init to use base config entry handling (42b14c0)
- Merge pull request #135 from Xerolux/codex/fix-coroutine-warning-in-aiohttp-server (29054a9)
- Fix awaiting finish step in config flow (918dbf0)
- Merge pull request #134 from Xerolux/codex/fix-schema-validation-errors-on-request (8e6eb46)
- Fix sensor selection schema conversion errors (1e28464)
- Merge pull request #133 from Xerolux/codex/fix-connection-test-error-in-violet-pool-controller (f44f4cf)
- Merge pull request #132 from Xerolux/codex/fix-attributeerror-in-violet-pool-controller (e41328e)
- Fix aiohttp session usage in config flow (63d9246)
- Merge pull request #131 from Xerolux/codex/fix-import-error-in-violet_pool_controller (45643cc)
- Merge pull request #130 from Xerolux/codex/fix-setup-issues-for-violet_pool_controller (3bc1909)
- Fix config flow constants (c7e79e6)
- Merge pull request #129 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (4154a0e)
- fix (8c9c534)
- Merge pull request #128 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (425aea7)
- Merge pull request #127 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (b51847b)
- 🐛 Fix: Schema-Validierung für Feature-Selection (dict comprehension) (dda5028)
- Merge pull request #126 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (0bbb990)
- 🐛 Fix: Config Flow Feature-Selection und Platzhalter (e29ae93)
- Merge pull request #125 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (c7977ef)
- 🐛 Fix: Config Flow Step-ID Fehler welcome (3652e8d)
- Merge pull request #124 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (d5193b9)
- 🐛 Fix: ConfigEntryNotReady Exception-Handling beim Setup (8421498)
- 🐛 Fix: Options Flow + Dynamic Device-Info für Multi-Controller (fd91013)

### 📚 Documentation | Dokumentation

- Add Home Assistant test infrastructure and test results documentation (4f0c7f8)
- Merge pull request #163 from Xerolux/claude/update-readme-01GdiF4dE7x48kixTQs1mbRk (243046c)
- docs: Update README with v0.2.0-beta.4 changelog and improvements (7e8a039)
- docs: Update CLAUDE.md with comprehensive codebase documentation (90b30d0)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- refactor: Improve code quality and documentation (0a538f5)
- Merge pull request #154 from Xerolux/bugfix-calibration-history-and-docs (b41122d)
- Fix calibration history parsing bug and improve documentation (26332dd)
- 📝 Docs: Python Cache Cleanup Instructions (cd6fc7d)
- Update README.md (8f43330)
- Update README.md (3630abb)

### 🧪 Tests

- Phase 3: Code quality improvements and comprehensive testing (0e00e5e)
- Add HA test directories to .gitignore (d3e168b)
- Add Home Assistant test infrastructure and test results documentation (4f0c7f8)
- Live Test (bcf7e89)
- refactor-config-flow-tests (9b170e8)
- Refactor config flow and improve test coverage (279a658)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- chore: Update .gitignore to exclude test virtual environments (1653084)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- Merge pull request #153 from Xerolux/fix-tests-and-bugs (f2775fc)
- Refactor tests and fix logic bugs (2fb1046)
- Merge pull request #133 from Xerolux/codex/fix-connection-test-error-in-violet-pool-controller (f44f4cf)
- 🐛🧪 Critical Fixes + Comprehensive Test Suite (733cae0)

---

### 📦 Installation

**HACS (Recommended):**
1. Add custom repository: `Xerolux/violet-hass`
2. Search for "Violet Pool Controller"
3. Click Install

**Manual:**
1. Download `violet_pool_controller.zip`
2. Extract to `custom_components/violet_pool_controller`
3. Restart Home Assistant

---

📋 [Full changelog: v0.2.0...v1.0.0](https://github.com/Xerolux/violet-hass/compare/v0.2.0...v1.0.0)

---

### ❤️ Support | Unterstützung

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏

Jeder Beitrag, egal wie klein, ist eine große Motivation! Vielen Dank! 🙏

---

### 💬 Feedback & Contributions

- 🐛 **[Report a bug](https://github.com/Xerolux/violet-hass/issues/new?template=bug_report.md)**
- 💡 **[Request a feature](https://github.com/Xerolux/violet-hass/issues/new?template=feature_request.md)**
- 🤝 **[Contribute](https://github.com/Xerolux/violet-hass/blob/main/docs/CONTRIBUTING.md)**

---

### 📄 Credits

**Developed by:** [Xerolux](https://github.com/Xerolux)
**Integration for:** Violet Pool Controller by PoolDigital GmbH & Co. KG
**License:** MIT

---

_Generated automatically by GitHub Actions on 2026-02-06 13:00:03 UTC_

---


---

### ❤️ Support | Unterstützung

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you!

Jeder Beitrag, egal wie klein, ist eine große Motivation! Vielen Dank!

---

## [1.0.0] - 2026-02-06

## v1.0.0 – Violet Pool Controller

**STABLE RELEASE** - Production-ready with extensive testing on live hardware!

---

### Highlights

Die erste stabile Version der komplett überarbeiteten Violet Pool Controller Integration.
Getestet auf echtem Controller-Hardware mit HA 2026.

---

### Critical Bug Fixes | Kritische Fehlerbehebungen

- **API Query Parameter Fix**: `getReadings` Endpunkt nutzte fehlerhafte `params={"ALL": ""}` statt korrekte `query="ALL"` - **dies war die Ursache für fehlende Sensordaten**
- **Firmware-Extraktion**: Firmware-Version wird jetzt korrekt aus der API-Antwort extrahiert
- **Switch State Handling**: Leere Strings (`""`) werden nicht mehr als `True` interpretiert
- **Composite State Parsing**: Pipe-separierte Zustände wie `"2|BLOCKED_BY_OUTSIDE_TEMP"` werden jetzt korrekt aufgelöst
- **Empty State Arrays**: `SOLARSTATE = "[]"` wird als fehlender Wert erkannt und Fallback auf Basiszustand genutzt
- **Status-Sensor Deutsch**: Alle Status-Sensoren zeigen jetzt deutsche Beschreibungen statt englischer Texte

### New Features | Neue Funktionen

- **Deutsche Status-Beschreibungen**: Switches zeigen detaillierte deutsche Zustandsinformationen in `extra_state_attributes` (Modus, Geschwindigkeit, Laufzeit)
- **Pumpen-Details**: Aktive Drehzahlstufe (0-3) wird automatisch erkannt und angezeigt
- **Heizungs-Details**: Zieltemperatur und Nachlaufzeit in Attributen sichtbar
- **Solar-Details**: Zieltemperatur als Attribut verfügbar
- **Dosierungs-Details**: Status, Reichweite, Tagesmenge und Kanistervolumen als Attribute
- **Rückspülungs-Details**: Rückspülschritt und Info als Attribute
- **Dashboard Template**: `Dashboard/pool_control_status.yaml` mit `secondaryinfo-entity-row` für Status-Anzeige direkt unter Schaltern
- **Circuit Breaker Pattern**: Automatische Absicherung gegen API-Ausfälle mit Retry und Recovery

### Improvements | Verbesserungen

- **Startup Performance**: 3-Sekunden-Sleep beim Start entfernt - Integration startet sofort
- **Vereinfachtes Data Fetching**: Immer Full Refresh statt komplexer Partial/Full-Logik
- **Composite State Sensoren**: PUMPSTATE, HEATERSTATE, SOLARSTATE korrekt als Sensoren verfügbar
- **Dosing State Sensoren**: DOS_*_STATE Arrays werden korrekt geparst und angezeigt
- **API Rate Limiting**: Token Bucket Algorithmus schützt den Controller vor Überlastung
- **Auto-Recovery**: Exponentieller Backoff (10s-300s) bei Verbindungsverlust
- **Input Sanitization**: Schutz gegen XSS, SQL Injection und Command Injection
- **SSL/TLS Security**: Zertifikatsverifizierung standardmäßig aktiviert
- **HA 2026 Kompatibilität**: Getestet mit Home Assistant 2025.12.0+

### Dashboard | Dashboard-Vorlagen

- Neue `pool_control_status.yaml` mit zwei Varianten:
  - **Variante 1**: Mit `custom:secondaryinfo-entity-row` (HACS) - Status direkt unter Schaltern
  - **Variante 2**: Ohne Custom Card - Status als separate Zeilen

---

### Previous Alpha Changes (included in this release)

## [1.0.7-alpha.3] - 2026-02-06

## v1.0.7-alpha.3 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features | Neue Funktionen

- feat: Diagnostic sensors, HA 2026 compatibility, security improvements (v1.0.7-alpha.4) (4538860)
- Add security utilities for authentication and SSL validation (8d64181)
- ✨ Add composite state sensors (PUMPSTATE, HEATERSTATE, SOLARSTATE) (7fd6989)
- ✨ Add dosing state array sensors (DOS_*_STATE) (88aae9c)
- add-controller-selection (75a2eb8)
- Add HA test directories to .gitignore (d3e168b)
- Add Home Assistant test infrastructure and test results documentation (4f0c7f8)
- Remove add-controller-selection (e57ab64)
- Add ProCon.IP controller support to config flow (85f9ae3)
- new release workflow (b715be0)
- feat: Add reauthentication, reconfiguration, and diagnostic sensors (ed282c1)
- feat: Add intuitive ON/OFF/AUTO control with Select entities and Dashboard templates (7ac8301)
- Improve UX: Add feature selection to options flow and enhance UI organization (ed6b4c6)
- feat: Add GitHub Codespaces prebuild configuration (cdc97f6)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- feat: Make DMX scene updates fault-tolerant (f914a00)
- Add support for mixed-case system sensor keys (f6f4c10)
- Fix firmware version extraction and add setup guide (6f7aed8)
- Add device info lookup to API (7d53ce0)
- Add error handling utilities for config flow (1ee9bf2)
- 🐛 Fix: Schema-Validierung für Feature-Selection (dict comprehension) (dda5028)
- 🐛 Fix: Config Flow Feature-Selection und Platzhalter (e29ae93)
- ✨ Feature: Multi-Controller Support mit Auto-Bereichen (ff3f7fc)
- ✨ Feature: Auto-Recovery + Enhanced Input Sanitization (bb07c09)
- ✨ Add explicit pre-release support to workflow (96a4bc9)

### 🚀 Improvements | Verbesserungen

- Improve API error handling and stability (2dc238a)
- Merge pull request #182 from Xerolux/fix-and-optimize-violet-pool-controller-4890044213630928459 (83329c5)
- Fix critical bugs, optimize entity logic, and improve type safety (d82545a)
- 🐛 Fix 18 bugs and optimize code performance (69af24d)
- 📝 Release v1.0.7-alpha.2 - Update changelog and version files (3517131)
- Fix sed regex in release workflow for CLAUDE.md version update (f7ccc6d)
- 📝 Release v1.0.7-alpha.1 - Update changelog and version files (1d9d07c)
- improve-setup-reauthentication (cb143dc)
- optimize-ha-2026 (f63c755)
- Optimize Violet Pool Controller integration for HA 2026 (73ad32a)
- update-dependencies-for-compatibility (e37ce73)
- Update dependencies and compatibility baseline (7404162)
- refactor-config-flow-tests (9b170e8)
- Refactor config flow and improve test coverage (279a658)
- addon-bugfix-ui-refactor (65c0a5b)
- optimize-and-ensure-functionality (0870b0f)
- Fix bugs, optimize code and ensure functionality (ce025d4)
- Improve UX: Add feature selection to options flow and enhance UI organization (ed6b4c6)
- Merge pull request #168 from Xerolux/refactor-config-flow-sensor-selection-12389334522538732123 (e9e8999)
- Refactor config flow sensor selection (84b467f)
- Merge pull request #166 from Xerolux/improve-validation-config-flow (bd5e0b9)
- Merge pull request #167 from Xerolux/improve-validation-config-flow-5901907404985322212 (4249f2e)
- Merge branch 'main' into improve-validation-config-flow to resolve conflicts (7caff24)
- Improve validation and UI in config flow by using NumberSelector (d33dd3c)
- Merge pull request #163 from Xerolux/claude/update-readme-01GdiF4dE7x48kixTQs1mbRk (243046c)
- docs: Update README with v0.2.0-beta.4 changelog and improvements (7e8a039)
- docs: Update CLAUDE.md with comprehensive codebase documentation (90b30d0)
- 📝 Update version to v0.2.0-beta.4 and release notes (6c12109)
- chore: Update .gitignore to exclude test virtual environments (1653084)
- Merge pull request #156 from Xerolux/refactor/code-quality-improvements (712b9f2)
- refactor: Improve code quality and documentation (0a538f5)
- Fix calibration history parsing bug and improve documentation (26332dd)
- Refactor tests and fix logic bugs (2fb1046)
- Fix controller connection setup errors and improve retry logic (3d75ed2)
- Update config_flow.py (d57e4d1)
- Update config_flow.py (c1a8406)
- 🔧 Refactor: Harmonisierung und Code-Optimierung (a9302b2)
- 📝 Update version to v0.2.0-beta.3 and release notes (31e18d7)
- 📝 Update version to v0.2.0-beta.2 and release notes (0713c62)
- 🔧 Refactor: Modular code structure + Security improvements (3946e22)
- 📝 Update version to v0.2.0-beta.1 and release notes (814cd1c)
- Update README.md (8f43330)
- Update README.md (3630abb)
- 📝 Update version to v0.2.0 and release notes (4887b5b)

### 🔧 Bug Fixes | Fehlerbehebungen

- Merge pull request #184 from Xerolux/fix-api-error-handling-3216800569233088969 (553a2ad)
- Fix CI validation failures (manifest and translations) (5c7ca9e)
- Fix CI validation failures (manifest and translations) (eea40c2)
- Fix CI validation failures (api formatting and strings.json schema) (8a12446)
- fix-api-stability-performance (7dd4038)
- Fix type checking and linting errors (aff549e)
- Fix API stability and performance issues (761dfcc)
- Merge pull request #182 from Xerolux/fix-and-optimize-violet-pool-controller-4890044213630928459 (83329c5)
- Fix critical bugs, optimize entity logic, and improve type safety (d82545a)
- 🐛 Fix 18 bugs and optimize code performance (69af24d)
- Fix sed regex in release workflow for CLAUDE.md version update (f7ccc6d)
- display fix (459c3a1)
- Firmware & State Fix (981abfd)
- bugfix release notes (f17acd9)
- addon-bugfix-ui-refactor (65c0a5b)
- fix: Critical bugfixes, UI/UX improvements and code quality enhancements (cf3a920)
- Fix bugs, optimize code and ensure functionality (ce025d4)
- fix: Resolve critical bugs and compatibility issues (292bcf7)
- Merge pull request #169 from Xerolux/claude/fix-smart-home-system-01Lu6UN2XXxKLJaQVHEnT1si (8ccf2ff)
- Merge pull request #164 from Xerolux/bugfix/manual-dosing-elektrolyse (c60dbf6)
- Fix manual dosing for Elektrolyse by using shared DOSING_FUNCTIONS (98f29f5)
- fix: Correct Codespaces prebuild configuration instructions (01f8287)
- Merge pull request #160 from Xerolux/claude/fix-liquid-syntax-error-01G7gM75JFPfS5mprghbgDyC (6e209b7)
- fix: Wrap Jinja2 templates with Liquid raw tags to prevent Jekyll parsing errors (8cb0cc7)
- Merge pull request #157 from Xerolux/claude/check-fix-errors-01WwCxsoB299aFxjZPHHpvyU (df15d72)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- fix: Resolve all mypy type errors (1927793)
- fix (516ec2c)
- Merge pull request #155 from Xerolux/fix/dmx-scene-error-handling (d304b7b)
- Merge pull request #154 from Xerolux/bugfix-calibration-history-and-docs (b41122d)
- Fix calibration history parsing bug and improve documentation (26332dd)
- Merge pull request #153 from Xerolux/fix-tests-and-bugs (f2775fc)
- Refactor tests and fix logic bugs (2fb1046)
- Merge pull request #150 from Xerolux/fix-sensors-config-flow (60af05f)
- Fix config flow, units, and pump status display (00bd86d)
- Merge pull request #149 from Xerolux/claude/fix-config-entry-option-flow-01EYbGFeqcKCZNMPuQunasZ3 (b422c07)
- Fix deprecated config_entry assignment and TypeError in options flow (6590491)
- Merge pull request #148 from Xerolux/codex/fix-invalid-unit-for-temperature-sensors (d3f86ae)
- Merge pull request #146 from Xerolux/codex/fix-pump-status-display-issue (da3ffe7)
- Merge pull request #145 from Xerolux/claude/fix-pool-sensor-unit-01Urx5WUsVtBiNHVZPJTnQXT (bd86ee9)
- Fix unit changes breaking Home Assistant statistics (fd6b633)
- Merge pull request #143 from Xerolux/claude/fix-firmware-pump-status-01LocFcDhW9MQwm1Bf4Wpzg8 (55717f4)
- Fix firmware display and temperature sensor units (3cacf54)
- Merge pull request #142 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (f55cc06)
- Fix firmware version extraction and add setup guide (6f7aed8)
- Merge pull request #141 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (65645c2)
- Fix missing sensors: Handle empty sensor selection correctly (2225fce)
- Merge pull request #140 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (8a61c2d)
- Merge pull request #139 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (42e8e38)
- Fix controller connection setup errors and improve retry logic (3d75ed2)
- Merge pull request #138 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (6eab77b)
- Fix config flow schema serialization and validation errors (fdc6cd4)
- Merge pull request #137 from Xerolux/claude/fix-config-setup-flow-01TZ2YNLshd1qLU6kjhiXh9a (624495c)
- Fix config flow: Change step_id from 'welcome' to 'user' (e70d307)
- fix (34cac7b)
- Merge pull request #136 from Xerolux/codex/fix-violet-pool-controller-integration-error (fc8d347)
- Fix options flow init to use base config entry handling (42b14c0)
- Merge pull request #135 from Xerolux/codex/fix-coroutine-warning-in-aiohttp-server (29054a9)
- Fix awaiting finish step in config flow (918dbf0)
- Merge pull request #134 from Xerolux/codex/fix-schema-validation-errors-on-request (8e6eb46)
- Fix sensor selection schema conversion errors (1e28464)
- Merge pull request #133 from Xerolux/codex/fix-connection-test-error-in-violet-pool-controller (f44f4cf)
- Merge pull request #132 from Xerolux/codex/fix-attributeerror-in-violet-pool-controller (e41328e)
- Fix aiohttp session usage in config flow (63d9246)
- Merge pull request #131 from Xerolux/codex/fix-import-error-in-violet_pool_controller (45643cc)
- Merge pull request #130 from Xerolux/codex/fix-setup-issues-for-violet_pool_controller (3bc1909)
- Fix config flow constants (c7e79e6)
- Merge pull request #129 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (4154a0e)
- fix (8c9c534)
- Merge pull request #128 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (425aea7)
- Merge pull request #127 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (b51847b)
- 🐛 Fix: Schema-Validierung für Feature-Selection (dict comprehension) (dda5028)
- Merge pull request #126 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (0bbb990)
- 🐛 Fix: Config Flow Feature-Selection und Platzhalter (e29ae93)
- Merge pull request #125 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (c7977ef)
- 🐛 Fix: Config Flow Step-ID Fehler welcome (3652e8d)
- Merge pull request #124 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (d5193b9)
- 🐛 Fix: ConfigEntryNotReady Exception-Handling beim Setup (8421498)
- 🐛 Fix: Options Flow + Dynamic Device-Info für Multi-Controller (fd91013)

### 📚 Documentation | Dokumentation

- Add Home Assistant test infrastructure and test results documentation (4f0c7f8)
- Merge pull request #163 from Xerolux/claude/update-readme-01GdiF4dE7x48kixTQs1mbRk (243046c)
- docs: Update README with v0.2.0-beta.4 changelog and improvements (7e8a039)
- docs: Update CLAUDE.md with comprehensive codebase documentation (90b30d0)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- refactor: Improve code quality and documentation (0a538f5)
- Merge pull request #154 from Xerolux/bugfix-calibration-history-and-docs (b41122d)
- Fix calibration history parsing bug and improve documentation (26332dd)
- 📝 Docs: Python Cache Cleanup Instructions (cd6fc7d)
- Update README.md (8f43330)
- Update README.md (3630abb)

### 🧪 Tests

- Phase 3: Code quality improvements and comprehensive testing (0e00e5e)
- Add HA test directories to .gitignore (d3e168b)
- Add Home Assistant test infrastructure and test results documentation (4f0c7f8)
- Live Test (bcf7e89)
- refactor-config-flow-tests (9b170e8)
- Refactor config flow and improve test coverage (279a658)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- chore: Update .gitignore to exclude test virtual environments (1653084)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- Merge pull request #153 from Xerolux/fix-tests-and-bugs (f2775fc)
- Refactor tests and fix logic bugs (2fb1046)
- Merge pull request #133 from Xerolux/codex/fix-connection-test-error-in-violet-pool-controller (f44f4cf)
- 🐛🧪 Critical Fixes + Comprehensive Test Suite (733cae0)

---

### 📦 Installation

**HACS (Recommended):**
1. Add custom repository: `Xerolux/violet-hass`
2. Search for "Violet Pool Controller"
3. Click Install

**Manual:**
1. Download `violet_pool_controller.zip`
2. Extract to `custom_components/violet_pool_controller`
3. Restart Home Assistant

---

📋 [Full changelog: v0.2.0...v1.0.7-alpha.3](https://github.com/Xerolux/violet-hass/compare/v0.2.0...v1.0.7-alpha.3)

---

### ❤️ Support | Unterstützung

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏

Jeder Beitrag, egal wie klein, ist eine große Motivation! Vielen Dank! 🙏

---

### 💬 Feedback & Contributions

- 🐛 **[Report a bug](https://github.com/Xerolux/violet-hass/issues/new?template=bug_report.md)**
- 💡 **[Request a feature](https://github.com/Xerolux/violet-hass/issues/new?template=feature_request.md)**
- 🤝 **[Contribute](https://github.com/Xerolux/violet-hass/blob/main/docs/CONTRIBUTING.md)**

---

### 📄 Credits

**Developed by:** [Xerolux](https://github.com/Xerolux)
**Integration for:** Violet Pool Controller by PoolDigital GmbH & Co. KG
**License:** MIT

---

_Generated automatically by GitHub Actions on 2026-02-06 11:03:24 UTC_

---

## [1.0.7-alpha.4] - 2026-02-01

### 📊 New Diagnostic Sensors | Neue Diagnose-Sensoren

- **API Request Rate Sensor**:
  - Zeigt API-Aufrufe pro Minute (`api_request_rate`)
  - Einheit: `req/min`
  - Hilft bei der Identifizierung von übermäßigem Polling

- **Average Latency Sensor**:
  - Zeigt durchschnittliche Verbindungslatenz (`average_latency`)
  - Einheit: `ms`
  - Rollender Durchschnitt der letzten 60 Anfragen
  - Hilft bei der Analyse von Leistungstrends

- **Recovery Success Rate Sensor**:
  - Zeigt Erfolgsrate der Auto-Recovery (`recovery_success_rate`)
  - Einheit: `%`
  - Hilft bei der Bewertung der Verbindungsstabilität

### 🔧 Improvements | Verbesserungen

- **Diagnostic Tracking erweitert**:
  - API-Request-Zähler für Rate-Berechnung
  - Latency-Verlauf (Rolling Window, 60 Samples)
  - Recovery-Statistiken (Success/Failure Count)
  - Alle Metriken thread-safe implementiert

### 🌐 Translations | Übersetzungen

- Neue Sensor-Übersetzungen in Deutsch und Englisch
- `api_request_rate` → "API-Anfragerate" / "API Request Rate"
- `average_latency` → "Durchschnittslatenz" / "Average Latency"
- `recovery_success_rate` → "Wiederherstellungsrate" / "Recovery Success Rate"

### 📚 Documentation | Dokumentation

- `FUTURE_IMPROVEMENTS.md` erstellt mit:
  - Detaillierter Roadmap für zukünftige Verbesserungen
  - Prioritäts-Matrix (10 Items identifiziert)
  - Safe Refactoring-Guide für Config Flow
  - Sicherheits-Checklisten

### 🔍 Code Quality

- ✅ Alle ruff checks bestanden
- ✅ Keine breaking changes
- ✅ Backward-kompatibel
- ✅ Thread-sicherheit gewährleistet

---

## [1.0.7-alpha.3] - 2026-02-01

### 🔒 Security Fixes | Sicherheits-Fixes

- **SSL/TLS Certificate Verification**: Added configurable SSL certificate verification with `verify_ssl` parameter
  - Default: Enabled (secure by default)
  - Warning message when disabled for security awareness
  - Proper SSL context handling with certificate validation
- **Improved Timeout Configuration**: Enhanced timeout handling with granular connection timeouts
  - Total timeout: User configurable (default 10s)
  - Connection timeout: 80% of total timeout
  - Socket connection timeout: 80% of total timeout
- **Enhanced Input Sanitization**: Updated API methods to use comprehensive input sanitization

### 🏗️ Refactoring | Code-Refactoring

- **Type Annotations Modernization**:
  - Updated all `typing.Mapping` imports to `collections.abc.Mapping`
  - Replaced `typing.Dict` with `dict` throughout codebase
  - Updated Optional types to use modern `X | None` syntax
- **Code Quality Improvements**:
  - Fixed all 144 ruff linting issues automatically
  - Removed trailing whitespace and blank lines with whitespace
  - Improved line length compliance (max 88 characters)
  - Simplified nested if statements where applicable
- **Import Cleanup**: Modernized all imports to use current best practices

### 🧵 Thread Safety | Thread-Sicherheit

- **Lock Ordering Documentation**: Added comprehensive thread safety documentation
  - Documented lock acquisition order to prevent deadlocks
  - `_api_lock`: Protects API calls and data updates
  - `_recovery_lock`: Protects recovery state and attempts
  - Clear warnings about nested locking and proper patterns
- **Recovery Logic Safety**: Enhanced recovery task with proper lock handling

### 🔧 Compatibility | Kompatibilität

- **Home Assistant 2026.1 Ready**:
  - Updated `manifest.json`: minimum HA version `2025.12.0`
  - Updated `requirements.txt`: `homeassistant>=2025.12.0`
  - Updated `aiohttp` dependency to `>=3.10.0`
- **Backward Compatibility**: Maintained support for older HA versions through minimum version declaration

### 🚀 Performance | Performance

- **Optimized State Management**: Enhanced device.py state handling with better tracking
- **Improved SSL Context Caching**: SSL contexts created only when needed, reducing overhead
- **Better Timeout Granularity**: Prevents hanging connections with proper timeout hierarchy

### 📝 Documentation | Dokumentation

- **Thread Safety Guide**: Added detailed lock ordering documentation in device.py
- **Security Warnings**: Added user-facing warnings for insecure SSL configurations
- **Code Comments**: Enhanced inline documentation for security-critical sections

---

## [1.0.7-alpha.2] - 2026-01-04

## v1.0.7-alpha.2 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features | Neue Funktionen

- add-controller-selection (75a2eb8)
- Add HA test directories to .gitignore (d3e168b)
- Add Home Assistant test infrastructure and test results documentation (4f0c7f8)
- Remove add-controller-selection (e57ab64)
- Add ProCon.IP controller support to config flow (85f9ae3)
- new release workflow (b715be0)
- feat: Add reauthentication, reconfiguration, and diagnostic sensors (ed282c1)
- feat: Add intuitive ON/OFF/AUTO control with Select entities and Dashboard templates (7ac8301)
- Improve UX: Add feature selection to options flow and enhance UI organization (ed6b4c6)
- feat: Add GitHub Codespaces prebuild configuration (cdc97f6)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- feat: Make DMX scene updates fault-tolerant (f914a00)
- Add support for mixed-case system sensor keys (f6f4c10)
- Fix firmware version extraction and add setup guide (6f7aed8)
- Add device info lookup to API (7d53ce0)
- Add error handling utilities for config flow (1ee9bf2)
- 🐛 Fix: Schema-Validierung für Feature-Selection (dict comprehension) (dda5028)
- 🐛 Fix: Config Flow Feature-Selection und Platzhalter (e29ae93)
- ✨ Feature: Multi-Controller Support mit Auto-Bereichen (ff3f7fc)
- ✨ Feature: Auto-Recovery + Enhanced Input Sanitization (bb07c09)
- ✨ Add explicit pre-release support to workflow (96a4bc9)

### 🚀 Improvements | Verbesserungen

- Fix sed regex in release workflow for CLAUDE.md version update (f7ccc6d)
- 📝 Release v1.0.7-alpha.1 - Update changelog and version files (1d9d07c)
- improve-setup-reauthentication (cb143dc)
- optimize-ha-2026 (f63c755)
- Optimize Violet Pool Controller integration for HA 2026 (73ad32a)
- update-dependencies-for-compatibility (e37ce73)
- Update dependencies and compatibility baseline (7404162)
- refactor-config-flow-tests (9b170e8)
- Refactor config flow and improve test coverage (279a658)
- addon-bugfix-ui-refactor (65c0a5b)
- optimize-and-ensure-functionality (0870b0f)
- Fix bugs, optimize code and ensure functionality (ce025d4)
- Improve UX: Add feature selection to options flow and enhance UI organization (ed6b4c6)
- Merge pull request #168 from Xerolux/refactor-config-flow-sensor-selection-12389334522538732123 (e9e8999)
- Refactor config flow sensor selection (84b467f)
- Merge pull request #166 from Xerolux/improve-validation-config-flow (bd5e0b9)
- Merge pull request #167 from Xerolux/improve-validation-config-flow-5901907404985322212 (4249f2e)
- Merge branch 'main' into improve-validation-config-flow to resolve conflicts (7caff24)
- Improve validation and UI in config flow by using NumberSelector (d33dd3c)
- Merge pull request #163 from Xerolux/claude/update-readme-01GdiF4dE7x48kixTQs1mbRk (243046c)
- docs: Update README with v0.2.0-beta.4 changelog and improvements (7e8a039)
- docs: Update CLAUDE.md with comprehensive codebase documentation (90b30d0)
- 📝 Update version to v0.2.0-beta.4 and release notes (6c12109)
- chore: Update .gitignore to exclude test virtual environments (1653084)
- Merge pull request #156 from Xerolux/refactor/code-quality-improvements (712b9f2)
- refactor: Improve code quality and documentation (0a538f5)
- Fix calibration history parsing bug and improve documentation (26332dd)
- Refactor tests and fix logic bugs (2fb1046)
- Fix controller connection setup errors and improve retry logic (3d75ed2)
- Update config_flow.py (d57e4d1)
- Update config_flow.py (c1a8406)
- 🔧 Refactor: Harmonisierung und Code-Optimierung (a9302b2)
- 📝 Update version to v0.2.0-beta.3 and release notes (31e18d7)
- 📝 Update version to v0.2.0-beta.2 and release notes (0713c62)
- 🔧 Refactor: Modular code structure + Security improvements (3946e22)
- 📝 Update version to v0.2.0-beta.1 and release notes (814cd1c)
- Update README.md (8f43330)
- Update README.md (3630abb)
- 📝 Update version to v0.2.0 and release notes (4887b5b)

### 🔧 Bug Fixes | Fehlerbehebungen

- Fix sed regex in release workflow for CLAUDE.md version update (f7ccc6d)
- display fix (459c3a1)
- Firmware & State Fix (981abfd)
- bugfix release notes (f17acd9)
- addon-bugfix-ui-refactor (65c0a5b)
- fix: Critical bugfixes, UI/UX improvements and code quality enhancements (cf3a920)
- Fix bugs, optimize code and ensure functionality (ce025d4)
- fix: Resolve critical bugs and compatibility issues (292bcf7)
- Merge pull request #169 from Xerolux/claude/fix-smart-home-system-01Lu6UN2XXxKLJaQVHEnT1si (8ccf2ff)
- Merge pull request #164 from Xerolux/bugfix/manual-dosing-elektrolyse (c60dbf6)
- Fix manual dosing for Elektrolyse by using shared DOSING_FUNCTIONS (98f29f5)
- fix: Correct Codespaces prebuild configuration instructions (01f8287)
- Merge pull request #160 from Xerolux/claude/fix-liquid-syntax-error-01G7gM75JFPfS5mprghbgDyC (6e209b7)
- fix: Wrap Jinja2 templates with Liquid raw tags to prevent Jekyll parsing errors (8cb0cc7)
- Merge pull request #157 from Xerolux/claude/check-fix-errors-01WwCxsoB299aFxjZPHHpvyU (df15d72)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- fix: Resolve all mypy type errors (1927793)
- fix (516ec2c)
- Merge pull request #155 from Xerolux/fix/dmx-scene-error-handling (d304b7b)
- Merge pull request #154 from Xerolux/bugfix-calibration-history-and-docs (b41122d)
- Fix calibration history parsing bug and improve documentation (26332dd)
- Merge pull request #153 from Xerolux/fix-tests-and-bugs (f2775fc)
- Refactor tests and fix logic bugs (2fb1046)
- Merge pull request #150 from Xerolux/fix-sensors-config-flow (60af05f)
- Fix config flow, units, and pump status display (00bd86d)
- Merge pull request #149 from Xerolux/claude/fix-config-entry-option-flow-01EYbGFeqcKCZNMPuQunasZ3 (b422c07)
- Fix deprecated config_entry assignment and TypeError in options flow (6590491)
- Merge pull request #148 from Xerolux/codex/fix-invalid-unit-for-temperature-sensors (d3f86ae)
- Merge pull request #146 from Xerolux/codex/fix-pump-status-display-issue (da3ffe7)
- Merge pull request #145 from Xerolux/claude/fix-pool-sensor-unit-01Urx5WUsVtBiNHVZPJTnQXT (bd86ee9)
- Fix unit changes breaking Home Assistant statistics (fd6b633)
- Merge pull request #143 from Xerolux/claude/fix-firmware-pump-status-01LocFcDhW9MQwm1Bf4Wpzg8 (55717f4)
- Fix firmware display and temperature sensor units (3cacf54)
- Merge pull request #142 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (f55cc06)
- Fix firmware version extraction and add setup guide (6f7aed8)
- Merge pull request #141 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (65645c2)
- Fix missing sensors: Handle empty sensor selection correctly (2225fce)
- Merge pull request #140 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (8a61c2d)
- Merge pull request #139 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (42e8e38)
- Fix controller connection setup errors and improve retry logic (3d75ed2)
- Merge pull request #138 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (6eab77b)
- Fix config flow schema serialization and validation errors (fdc6cd4)
- Merge pull request #137 from Xerolux/claude/fix-config-setup-flow-01TZ2YNLshd1qLU6kjhiXh9a (624495c)
- Fix config flow: Change step_id from 'welcome' to 'user' (e70d307)
- fix (34cac7b)
- Merge pull request #136 from Xerolux/codex/fix-violet-pool-controller-integration-error (fc8d347)
- Fix options flow init to use base config entry handling (42b14c0)
- Merge pull request #135 from Xerolux/codex/fix-coroutine-warning-in-aiohttp-server (29054a9)
- Fix awaiting finish step in config flow (918dbf0)
- Merge pull request #134 from Xerolux/codex/fix-schema-validation-errors-on-request (8e6eb46)
- Fix sensor selection schema conversion errors (1e28464)
- Merge pull request #133 from Xerolux/codex/fix-connection-test-error-in-violet-pool-controller (f44f4cf)
- Merge pull request #132 from Xerolux/codex/fix-attributeerror-in-violet-pool-controller (e41328e)
- Fix aiohttp session usage in config flow (63d9246)
- Merge pull request #131 from Xerolux/codex/fix-import-error-in-violet_pool_controller (45643cc)
- Merge pull request #130 from Xerolux/codex/fix-setup-issues-for-violet_pool_controller (3bc1909)
- Fix config flow constants (c7e79e6)
- Merge pull request #129 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (4154a0e)
- fix (8c9c534)
- Merge pull request #128 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (425aea7)
- Merge pull request #127 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (b51847b)
- 🐛 Fix: Schema-Validierung für Feature-Selection (dict comprehension) (dda5028)
- Merge pull request #126 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (0bbb990)
- 🐛 Fix: Config Flow Feature-Selection und Platzhalter (e29ae93)
- Merge pull request #125 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (c7977ef)
- 🐛 Fix: Config Flow Step-ID Fehler welcome (3652e8d)
- Merge pull request #124 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (d5193b9)
- 🐛 Fix: ConfigEntryNotReady Exception-Handling beim Setup (8421498)
- 🐛 Fix: Options Flow + Dynamic Device-Info für Multi-Controller (fd91013)

### 📚 Documentation | Dokumentation

- Add Home Assistant test infrastructure and test results documentation (4f0c7f8)
- Merge pull request #163 from Xerolux/claude/update-readme-01GdiF4dE7x48kixTQs1mbRk (243046c)
- docs: Update README with v0.2.0-beta.4 changelog and improvements (7e8a039)
- docs: Update CLAUDE.md with comprehensive codebase documentation (90b30d0)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- refactor: Improve code quality and documentation (0a538f5)
- Merge pull request #154 from Xerolux/bugfix-calibration-history-and-docs (b41122d)
- Fix calibration history parsing bug and improve documentation (26332dd)
- 📝 Docs: Python Cache Cleanup Instructions (cd6fc7d)
- Update README.md (8f43330)
- Update README.md (3630abb)

### 🧪 Tests

- Add HA test directories to .gitignore (d3e168b)
- Add Home Assistant test infrastructure and test results documentation (4f0c7f8)
- Live Test (bcf7e89)
- refactor-config-flow-tests (9b170e8)
- Refactor config flow and improve test coverage (279a658)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- chore: Update .gitignore to exclude test virtual environments (1653084)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- Merge pull request #153 from Xerolux/fix-tests-and-bugs (f2775fc)
- Refactor tests and fix logic bugs (2fb1046)
- Merge pull request #133 from Xerolux/codex/fix-connection-test-error-in-violet-pool-controller (f44f4cf)
- 🐛🧪 Critical Fixes + Comprehensive Test Suite (733cae0)

---

### 📦 Installation

**HACS (Recommended):**
1. Add custom repository: `Xerolux/violet-hass`
2. Search for "Violet Pool Controller"
3. Click Install

**Manual:**
1. Download `violet_pool_controller.zip`
2. Extract to `custom_components/violet_pool_controller`
3. Restart Home Assistant

---

📋 [Full changelog: v0.2.0...v1.0.7-alpha.2](https://github.com/Xerolux/violet-hass/compare/v0.2.0...v1.0.7-alpha.2)

---

### ❤️ Support | Unterstützung

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏

Jeder Beitrag, egal wie klein, ist eine große Motivation! Vielen Dank! 🙏

---

### 💬 Feedback & Contributions

- 🐛 **[Report a bug](https://github.com/Xerolux/violet-hass/issues/new?template=bug_report.md)**
- 💡 **[Request a feature](https://github.com/Xerolux/violet-hass/issues/new?template=feature_request.md)**
- 🤝 **[Contribute](https://github.com/Xerolux/violet-hass/blob/main/docs/CONTRIBUTING.md)**

---

### 📄 Credits

**Developed by:** [Xerolux](https://github.com/Xerolux)
**Integration for:** Violet Pool Controller by PoolDigital GmbH & Co. KG
**License:** MIT

---

_Generated automatically by GitHub Actions on 2026-01-04 08:34:47 UTC_

---

## [1.0.7-alpha.1] - 2026-01-03

## v1.0.7-alpha.1 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features | Neue Funktionen

- new release workflow (b715be0)
- feat: Add reauthentication, reconfiguration, and diagnostic sensors (ed282c1)
- feat: Add intuitive ON/OFF/AUTO control with Select entities and Dashboard templates (7ac8301)
- Improve UX: Add feature selection to options flow and enhance UI organization (ed6b4c6)
- feat: Add GitHub Codespaces prebuild configuration (cdc97f6)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- feat: Make DMX scene updates fault-tolerant (f914a00)
- Add support for mixed-case system sensor keys (f6f4c10)
- Fix firmware version extraction and add setup guide (6f7aed8)
- Add device info lookup to API (7d53ce0)
- Add error handling utilities for config flow (1ee9bf2)
- 🐛 Fix: Schema-Validierung für Feature-Selection (dict comprehension) (dda5028)
- 🐛 Fix: Config Flow Feature-Selection und Platzhalter (e29ae93)
- ✨ Feature: Multi-Controller Support mit Auto-Bereichen (ff3f7fc)
- ✨ Feature: Auto-Recovery + Enhanced Input Sanitization (bb07c09)
- ✨ Add explicit pre-release support to workflow (96a4bc9)

### 🚀 Improvements | Verbesserungen

- improve-setup-reauthentication (cb143dc)
- optimize-ha-2026 (f63c755)
- Optimize Violet Pool Controller integration for HA 2026 (73ad32a)
- update-dependencies-for-compatibility (e37ce73)
- Update dependencies and compatibility baseline (7404162)
- refactor-config-flow-tests (9b170e8)
- Refactor config flow and improve test coverage (279a658)
- addon-bugfix-ui-refactor (65c0a5b)
- optimize-and-ensure-functionality (0870b0f)
- Fix bugs, optimize code and ensure functionality (ce025d4)
- Improve UX: Add feature selection to options flow and enhance UI organization (ed6b4c6)
- Merge pull request #168 from Xerolux/refactor-config-flow-sensor-selection-12389334522538732123 (e9e8999)
- Refactor config flow sensor selection (84b467f)
- Merge pull request #166 from Xerolux/improve-validation-config-flow (bd5e0b9)
- Merge pull request #167 from Xerolux/improve-validation-config-flow-5901907404985322212 (4249f2e)
- Merge branch 'main' into improve-validation-config-flow to resolve conflicts (7caff24)
- Improve validation and UI in config flow by using NumberSelector (d33dd3c)
- Merge pull request #163 from Xerolux/claude/update-readme-01GdiF4dE7x48kixTQs1mbRk (243046c)
- docs: Update README with v0.2.0-beta.4 changelog and improvements (7e8a039)
- docs: Update CLAUDE.md with comprehensive codebase documentation (90b30d0)
- 📝 Update version to v0.2.0-beta.4 and release notes (6c12109)
- chore: Update .gitignore to exclude test virtual environments (1653084)
- Merge pull request #156 from Xerolux/refactor/code-quality-improvements (712b9f2)
- refactor: Improve code quality and documentation (0a538f5)
- Fix calibration history parsing bug and improve documentation (26332dd)
- Refactor tests and fix logic bugs (2fb1046)
- Fix controller connection setup errors and improve retry logic (3d75ed2)
- Update config_flow.py (d57e4d1)
- Update config_flow.py (c1a8406)
- 🔧 Refactor: Harmonisierung und Code-Optimierung (a9302b2)
- 📝 Update version to v0.2.0-beta.3 and release notes (31e18d7)
- 📝 Update version to v0.2.0-beta.2 and release notes (0713c62)
- 🔧 Refactor: Modular code structure + Security improvements (3946e22)
- 📝 Update version to v0.2.0-beta.1 and release notes (814cd1c)
- Update README.md (8f43330)
- Update README.md (3630abb)
- 📝 Update version to v0.2.0 and release notes (4887b5b)

### 🔧 Bug Fixes | Fehlerbehebungen

- addon-bugfix-ui-refactor (65c0a5b)
- fix: Critical bugfixes, UI/UX improvements and code quality enhancements (cf3a920)
- Fix bugs, optimize code and ensure functionality (ce025d4)
- fix: Resolve critical bugs and compatibility issues (292bcf7)
- Merge pull request #169 from Xerolux/claude/fix-smart-home-system-01Lu6UN2XXxKLJaQVHEnT1si (8ccf2ff)
- Merge pull request #164 from Xerolux/bugfix/manual-dosing-elektrolyse (c60dbf6)
- Fix manual dosing for Elektrolyse by using shared DOSING_FUNCTIONS (98f29f5)
- fix: Correct Codespaces prebuild configuration instructions (01f8287)
- Merge pull request #160 from Xerolux/claude/fix-liquid-syntax-error-01G7gM75JFPfS5mprghbgDyC (6e209b7)
- fix: Wrap Jinja2 templates with Liquid raw tags to prevent Jekyll parsing errors (8cb0cc7)
- Merge pull request #157 from Xerolux/claude/check-fix-errors-01WwCxsoB299aFxjZPHHpvyU (df15d72)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- fix: Resolve all mypy type errors (1927793)
- fix (516ec2c)
- Merge pull request #155 from Xerolux/fix/dmx-scene-error-handling (d304b7b)
- Merge pull request #154 from Xerolux/bugfix-calibration-history-and-docs (b41122d)
- Fix calibration history parsing bug and improve documentation (26332dd)
- Merge pull request #153 from Xerolux/fix-tests-and-bugs (f2775fc)
- Refactor tests and fix logic bugs (2fb1046)
- Merge pull request #150 from Xerolux/fix-sensors-config-flow (60af05f)
- Fix config flow, units, and pump status display (00bd86d)
- Merge pull request #149 from Xerolux/claude/fix-config-entry-option-flow-01EYbGFeqcKCZNMPuQunasZ3 (b422c07)
- Fix deprecated config_entry assignment and TypeError in options flow (6590491)
- Merge pull request #148 from Xerolux/codex/fix-invalid-unit-for-temperature-sensors (d3f86ae)
- Merge pull request #146 from Xerolux/codex/fix-pump-status-display-issue (da3ffe7)
- Merge pull request #145 from Xerolux/claude/fix-pool-sensor-unit-01Urx5WUsVtBiNHVZPJTnQXT (bd86ee9)
- Fix unit changes breaking Home Assistant statistics (fd6b633)
- Merge pull request #143 from Xerolux/claude/fix-firmware-pump-status-01LocFcDhW9MQwm1Bf4Wpzg8 (55717f4)
- Fix firmware display and temperature sensor units (3cacf54)
- Merge pull request #142 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (f55cc06)
- Fix firmware version extraction and add setup guide (6f7aed8)
- Merge pull request #141 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (65645c2)
- Fix missing sensors: Handle empty sensor selection correctly (2225fce)
- Merge pull request #140 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (8a61c2d)
- Merge pull request #139 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (42e8e38)
- Fix controller connection setup errors and improve retry logic (3d75ed2)
- Merge pull request #138 from Xerolux/claude/fix-heating-solar-validation-015azcAfv8B4Mox6SiLhpMZ4 (6eab77b)
- Fix config flow schema serialization and validation errors (fdc6cd4)
- Merge pull request #137 from Xerolux/claude/fix-config-setup-flow-01TZ2YNLshd1qLU6kjhiXh9a (624495c)
- Fix config flow: Change step_id from 'welcome' to 'user' (e70d307)
- fix (34cac7b)
- Merge pull request #136 from Xerolux/codex/fix-violet-pool-controller-integration-error (fc8d347)
- Fix options flow init to use base config entry handling (42b14c0)
- Merge pull request #135 from Xerolux/codex/fix-coroutine-warning-in-aiohttp-server (29054a9)
- Fix awaiting finish step in config flow (918dbf0)
- Merge pull request #134 from Xerolux/codex/fix-schema-validation-errors-on-request (8e6eb46)
- Fix sensor selection schema conversion errors (1e28464)
- Merge pull request #133 from Xerolux/codex/fix-connection-test-error-in-violet-pool-controller (f44f4cf)
- Merge pull request #132 from Xerolux/codex/fix-attributeerror-in-violet-pool-controller (e41328e)
- Fix aiohttp session usage in config flow (63d9246)
- Merge pull request #131 from Xerolux/codex/fix-import-error-in-violet_pool_controller (45643cc)
- Merge pull request #130 from Xerolux/codex/fix-setup-issues-for-violet_pool_controller (3bc1909)
- Fix config flow constants (c7e79e6)
- Merge pull request #129 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (4154a0e)
- fix (8c9c534)
- Merge pull request #128 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (425aea7)
- Merge pull request #127 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (b51847b)
- 🐛 Fix: Schema-Validierung für Feature-Selection (dict comprehension) (dda5028)
- Merge pull request #126 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (0bbb990)
- 🐛 Fix: Config Flow Feature-Selection und Platzhalter (e29ae93)
- Merge pull request #125 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (c7977ef)
- 🐛 Fix: Config Flow Step-ID Fehler welcome (3652e8d)
- Merge pull request #124 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (d5193b9)
- 🐛 Fix: ConfigEntryNotReady Exception-Handling beim Setup (8421498)
- 🐛 Fix: Options Flow + Dynamic Device-Info für Multi-Controller (fd91013)

### 📚 Documentation | Dokumentation

- Merge pull request #163 from Xerolux/claude/update-readme-01GdiF4dE7x48kixTQs1mbRk (243046c)
- docs: Update README with v0.2.0-beta.4 changelog and improvements (7e8a039)
- docs: Update CLAUDE.md with comprehensive codebase documentation (90b30d0)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- refactor: Improve code quality and documentation (0a538f5)
- Merge pull request #154 from Xerolux/bugfix-calibration-history-and-docs (b41122d)
- Fix calibration history parsing bug and improve documentation (26332dd)
- 📝 Docs: Python Cache Cleanup Instructions (cd6fc7d)
- Update README.md (8f43330)
- Update README.md (3630abb)

### 🧪 Tests

- Live Test (bcf7e89)
- refactor-config-flow-tests (9b170e8)
- Refactor config flow and improve test coverage (279a658)
- test: Fix thread assertion error and add comprehensive testing infrastructure (93ac071)
- chore: Update .gitignore to exclude test virtual environments (1653084)
- docs: Add comprehensive testing checklist for manual HA testing (2a8028b)
- Merge pull request #153 from Xerolux/fix-tests-and-bugs (f2775fc)
- Refactor tests and fix logic bugs (2fb1046)
- Merge pull request #133 from Xerolux/codex/fix-connection-test-error-in-violet-pool-controller (f44f4cf)
- 🐛🧪 Critical Fixes + Comprehensive Test Suite (733cae0)

---

### 📦 Installation

**HACS (Recommended):**
1. Add custom repository: `Xerolux/violet-hass`
2. Search for "Violet Pool Controller"
3. Click Install

**Manual:**
1. Download `violet_pool_controller.zip`
2. Extract to `custom_components/violet_pool_controller`
3. Restart Home Assistant

---

📋 [Full changelog: v0.2.0...v1.0.7-alpha.1](https://github.com/Xerolux/violet-hass/compare/v0.2.0...v1.0.7-alpha.1)

---

### ❤️ Support | Unterstützung

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏

Jeder Beitrag, egal wie klein, ist eine große Motivation! Vielen Dank! 🙏

---

### 💬 Feedback & Contributions

- 🐛 **[Report a bug](https://github.com/Xerolux/violet-hass/issues/new?template=bug_report.md)**
- 💡 **[Request a feature](https://github.com/Xerolux/violet-hass/issues/new?template=feature_request.md)**
- 🤝 **[Contribute](https://github.com/Xerolux/violet-hass/blob/main/docs/CONTRIBUTING.md)**

---

### 📄 Credits

**Developed by:** [Xerolux](https://github.com/Xerolux)
**Integration for:** Violet Pool Controller by PoolDigital GmbH & Co. KG
**License:** MIT

---

_Generated automatically by GitHub Actions on 2026-01-03 16:00:36 UTC_

---


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-11-20

### 🎉 Semantic Versioning Adoption

This release marks the transition to clean Semantic Versioning (SemVer 2.0.0) for better version clarity and HACS compatibility.

#### ✨ Added
- **Semantic Versioning:** Migrated from `0.1.0-8` to `0.2.0` (SemVer 2.0.0 compliant)
- **Complete 3-State Switch Support:** Enhanced state handling with State 4 (Manual Forced ON)
- **PVSURPLUS Parameter Support:** Full integration of PV surplus functionality
- **Enhanced DMX Scene Control:** Support for 12 DMX lighting scenes
- **Extended Sensor Coverage:** 147 API parameters fully mapped
- **Complete Extension Relay Support:** EXT1/EXT2 relay banks
- **Multi-language support:** German/English translations
- **Comprehensive automation blueprints:** Ready-to-use automations
- **Advanced service implementations:** 7+ custom services

#### 🔧 Fixed
- **STATE_MAP:** Now includes State 4 (Manual Forced ON)
- **PVSURPLUS:** Added to SWITCH_FUNCTIONS mapping
- **COVER_STATE_MAP:** Supports both string and numeric states
- **Thread Safety:** Optimistic updates use local cache variables
- **Logging Optimization:** Smart failure logging prevents log spam

#### 🚀 Improved
- **Release Workflow:** Updated for clean SemVer tags (v0.2.0, v0.2.1, etc.)
- **Version Management:** Centralized version info with automatic updates
- **Documentation:** Updated examples to use SemVer format

## [0.1.0] - 2024-XX-XX

### 🎉 Initial Release

#### ✨ Added
- **Core Integration**
  - Full API integration with Violet Pool Controller
  - Dynamic entity creation based on available features
  - Real-time data synchronization with configurable polling
  - Robust error handling with retry mechanisms
  - Local-only communication (no cloud required)

- **Entity Support**
  - **Climate Entities:** Pool heater and solar absorber control
  - **Sensors:** Temperature, pH, ORP, chlorine, pressure, water level
  - **Binary Sensors:** Pump status, heater state, cover position
  - **Switches:** Pump, lighting, dosing systems, backwash
  - **Cover:** Automatic pool cover control
  - **Number:** Target value controls for pH, ORP, chlorine

- **Custom Services**
  - `turn_auto` - Switch devices to automatic mode
  - `set_pv_surplus` - Activate solar surplus mode
  - `manual_dosing` - Manual chemical dosing control
  - `set_temperature_target` - Climate control service
  - `set_ph_target` - pH target value setting
  - `set_chlorine_target` - Chlorine target setting
  - `trigger_backwash` - Manual backwash activation
  - `start_water_analysis` - Water testing initiation
  - `set_maintenance_mode` - Maintenance mode control

- **Smart Automation Blueprints**
  - **Temperature Control:** Intelligent heating with solar priority
  - **pH Management:** Automated chemical balancing with safety limits
  - **Cover Control:** Weather-aware automatic cover operation
  - **Backwash Automation:** Pressure and time-based filter cleaning

- **Configuration Features**
  - UI-only configuration (no YAML required)
  - Multi-step setup wizard
  - Feature selection and customization
  - Advanced options for polling and timeouts
  - Pool-specific settings (size, type, disinfection method)

- **Developer Features**
  - Comprehensive logging and debugging
  - Data update coordinator for efficient API usage
  - Modular entity structure for easy expansion
  - Unit tests and validation
  - Python 3.11+ compatibility
  - Home Assistant 2024.6+ support

#### 🌍 Internationalization
- Complete German (DE) translations
- English (EN) as default language
- Service descriptions and UI strings
- Error messages and notifications

#### 🔧 Technical Implementation
- **API Client:** Async HTTP client with session management
- **Entity Management:** Dynamic creation based on controller features
- **State Management:** Intelligent state mapping and conversion
- **Error Handling:** Comprehensive exception handling with user feedback
- **Performance:** Optimized polling with coordinator pattern
- **Security:** Support for SSL/TLS and authentication

#### 🤖 Blueprint Features
- **Temperature Control:**
  - Day/night temperature scheduling
  - Solar heating priority logic
  - Energy-efficient heating strategies
  - Weather-based adjustments
  
- **pH Control:**
  - Automatic pH balancing (6.8-7.8 range)
  - Safety limits for dosing
  - Pump-dependent dosing logic
  - Daily dosing counters and limits

- **Cover Control:**
  - Time-based open/close scheduling
  - Weather protection (rain, wind, cold)
  - Pump interlock safety features
  - Manual override capabilities

- **Backwash Control:**
  - Pressure-based triggering
  - Scheduled maintenance cycles
  - Runtime-based activation
  - Full wash/rinse cycle automation

#### 📱 User Experience
- Easy installation via HACS or manual setup
- Intuitive configuration wizard
- Clear error messages and troubleshooting guides
- Comprehensive documentation with examples
- Dashboard cards and automation examples

#### 🛡️ Safety Features
- Connection timeout and retry handling
- Chemical dosing safety limits
- Equipment interlock protections
- Maintenance mode support
- Error logging and reporting

### 🔧 Technical Details
- **Minimum Requirements:**
  - Home Assistant 2024.6.0+
  - Python 3.11+
  - Violet Pool Controller with API access
  
- **Dependencies:**
  - aiohttp >= 3.8.0
  - voluptuous (included with HA)
  - Standard Home Assistant libraries

- **Supported Features:**
  - All standard Violet controller functions
  - Extension modules and digital inputs
  - DMX lighting control
  - PV surplus integration
  - Multi-zone temperature control

### 📊 Statistics
- **Code:** 3000+ lines of Python code
- **Entities:** 50+ dynamic entity types
- **Services:** 9 custom services
- **Blueprints:** 4 automation templates
- **Languages:** 2 complete translations
- **Tests:** Comprehensive test coverage

### 🙏 Acknowledgments
- Home Assistant development team
- PoolDigital for excellent hardware
- Community beta testers
- Integration blueprint template by @Ludeeus

---

## [Future Releases]

### 🔮 Planned Features (v0.2.0)
- **Enhanced Analytics:**
  - Historical data tracking
  - Energy consumption monitoring
  - Chemical usage statistics
  - Maintenance predictions

- **Advanced Automation:**
  - AI-powered optimization
  - Weather forecast integration
  - Energy price optimization
  - Vacation mode automation

- **Mobile Experience:**
  - Custom Lovelace cards
  - Mobile app shortcuts
  - Push notifications
  - Quick action tiles

- **Integration Expansion:**
  - MQTT discovery
  - Grafana dashboards
  - Node-RED nodes
  - REST API expansion

### 🚀 Long-term Vision (v1.0+)
- **Machine Learning Integration:**
  - Predictive maintenance scheduling
  - Automated chemical optimization
  - Energy usage prediction
  - Seasonal adaptation learning

- **Multi-Controller Support:**
  - Pool + Spa dual control
  - Multiple pool management
  - Centralized monitoring
  - Synchronized operations

- **Professional Features:**
  - Commercial pool support
  - Multi-tenant management
  - Advanced reporting
  - API rate limiting

- **Cloud Integration (Optional):**
  - Remote monitoring
  - Cloud backups
  - Mobile alerts
  - Professional dashboards

---

## 🐛 Bug Fixes

### Known Issues (v0.1.0)
- None reported yet (initial release)

### Fixed in Development
- Python 3.13 syntax compatibility issues
- State mapping for binary sensors
- Service parameter validation
- Blueprint template variables
- Translation string completeness

---

## 🔄 Migration Guide

### From Manual API Usage
If you were previously using manual REST sensors or shell commands to interact with your Violet controller:

1. **Remove old configuration:**
   - Delete manual REST sensors from `configuration.yaml`
   - Remove shell command integrations
   - Clean up old automation triggers

2. **Install integration:**
   - Follow installation guide in README
   - Use same IP address and credentials
   - Select equivalent features

3. **Update automations:**
   - Replace REST calls with service calls
   - Update entity names (old: `sensor.pool_temp` → new: `sensor.violet_pool_temperature`)
   - Use new blueprints for common scenarios

### From Beta Versions
Beta testers should:
1. Remove beta installation completely
2. Install stable release via HACS
3. Reconfigure with same settings
4. Update any custom automations

---

## 🏷️ Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0): Incompatible API changes
- **MINOR** version (0.1.0): Backwards-compatible functionality additions  
- **PATCH** version (0.1.1): Backwards-compatible bug fixes

### Release Cycle
- **Major releases:** Yearly (significant new features)
- **Minor releases:** Quarterly (new features, blueprints)
- **Patch releases:** As needed (bug fixes, security)

---

## 📋 Changelog Categories

### 🎉 Added
New features, entities, services, or capabilities

### ⚡ Changed  
Changes in existing functionality (non-breaking)

### 🔧 Fixed
Bug fixes and error corrections

### 🚨 Deprecated
Soon-to-be removed features (with migration path)

### ❌ Removed
Features removed in this version

### 🛡️ Security
Security improvements and vulnerability fixes

---

## 🔗 Related Links

- **GitHub Releases:** [Latest versions and downloads](https://github.com/xerolux/violet-hass/releases)
- **GitHub Issues:** [Bug reports and feature requests](https://github.com/xerolux/violet-hass/issues)
- **HACS:** [Home Assistant Community Store listing](https://hacs.xyz)
- **Documentation:** [Full integration guide](https://github.com/xerolux/violet-hass/blob/main/README.md)
- **Blueprints:** [Automation templates](https://github.com/xerolux/violet-hass/tree/main/blueprints)

---

## 📞 Support & Feedback

Found an issue or have a suggestion? We'd love to hear from you:

- 🐛 **Bug Reports:** [Open an issue on GitHub](https://github.com/xerolux/violet-hass/issues/new/choose)
- 💡 **Feature Requests:** [Request new features](https://github.com/xerolux/violet-hass/issues/new/choose)
- 💬 **Community Discussion:** [Home Assistant Community Forum](https://community.home-assistant.io/)
- 📧 **Direct Contact:** [Email the developer](mailto:git@xerolux.de)

---

**Made with ❤️ for the Home Assistant and Pool Automation Community**

*Keep your pool smart, your water perfect, and your maintenance minimal!* 🏊‍♀️🤖
