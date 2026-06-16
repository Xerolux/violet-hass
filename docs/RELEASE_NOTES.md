## v2.0.0 – Violet Pool Controller

✅ **STABLE RELEASE**

### ❤️ Support | Unterstützung

If you find this integration useful, consider supporting the developer. Every contribution, no matter how small, is a huge motivation to improve the project and keep it alive! Thank you! 🙏

Jeder kleine Beitrag hilft, die Motivation hochzuhalten, um das Projekt weiter zu verbessern und am Leben zu erhalten! Vielen Dank! 🙏

- 💳 **[PayPal](https://paypal.me/xerolux)**
- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **[Star this repository](https://github.com/Xerolux/violet-hass)**

---

### ✨ New Features | Neue Funktionen

- fix: Add py313 support to tox configuration (334e653)
- feat(F): API package performance & security enhancements (e7e984c)
- fix(A4): Add logging to silent exception handlers (0efd90b)
- docs: Add CI_CD_ACTION_PINNING.md guidelines (8ba65a4)
- ci: Add Python 3.13 to validate.yml test matrix (5447134)
- docs: Add HA_QUALITY_SCALE_PROGRESS.md documentation (74a51fa)
- docs: Add ARCHITECTURE.md and update CLAUDE.md (f3980a5)
- fix(A2): Add logging to connection test exception handling (eba2422)
- docs: Add RELEASE_NOTES.md placeholder and BACKLOG_PROGRESS.md (d56fa16)
- build: Add CODEOWNERS file and fix hacs.json formatting (9d72eb0)
- feat: Complete German translation of all sensor names and services (2a16890)
- feat: Complete translations for remaining 5 languages (en, nl, pl, pt, ru) (780ac51)
- feat: Add agent-generated translations for es, it, pl, ru (e35a7d7)
- feat: Complete translation of all 9 languages (en, es, fr, it, nl, pl, pt, ru, zh) (9534696)
- feat: Complete German translation of all sensor names and services (419d7bc)
- docs: Add comprehensive CHANGELOG with breaking changes (German) (5337166)
- docs: Add comprehensive CHANGELOG with breaking changes (German) (3aae94f)
- Add Safety Settings to reconfigure flow (926984d)
- Add Safety Settings to reconfigure flow (5702814)
- feat: Add safety-critical switch control opt-in to config flow (41a6b47)
- feat: Auto-disable unsafe switches for existing installations (6691b63)
- fix: Add missing @property decorator to device_info method (6d8b684)
- fix: Add missing @property decorator to device_info method (5290e03)
- docs: Add Code of Conduct for community standards (db63a20)
- 🚨 CRITICAL: Add control_refill_http service with REQUIRED duration for flooding prevention (9a9f183)
- Add German translations for dosing sensor names (dbe8225)
- Add SSL certificate verification option to reconfigure flow (b357e3c)
- docs: add markdown link references to CHANGELOG.md for direct GitHub navigation (7b5c38f)
- docs: add comprehensive security architecture documentation (13e0d38)
- fix: prevent duplicate entity ID prefix generation on new installs (fa160f3)
- feat: add Reset Error Blockings button for direct error management (ab3bf4d)
- feat: apply 15 firmware-discovery improvements (beta.8, API 0.0.31) (c291673)
- feat: add invert_cover option for pools with reversed cover wiring (3a26ba1)
- feat: improve mock server with real controller keys from pooldigital-mock (9e31a47)
- fix: Violet Pool Controller 2.0.0-beta.7 — entity prefix migration, firmware update detection, new sensors (e0a10f3)
- fix: restore firmware version detection for both old and new key names (2b443b4)
- i18n: Add translations for new sensors across all 10 languages (c7b714f)
- feat: Implement 5 firmware findings — H2O2, runtimes, RS485 power, stopwatch, dosing stats (63b5238)
- feat(integration): implement 6 HA integration improvements from myviolet-hass (260023e)
- feat(api): add VioletReadings — typed Mapping wrapper over /getReadings snapshot (643eccc)
- feat(api): apply lessons from myviolet — enums, exceptions, parsers, validation (6ee64c3)
- feat: Apply dynamic naming to climate and cover platforms (92b67f1)
- refactor: Add EntityNameResolver import to all platforms (5b80c98)
- feat: Complete hardware configuration system - all configurable names (ab3c46b)
- feat: Dynamic digital input configuration from hardware (eece964)
- feat: Add firmware update entity and status service (9a35c76)
- feat: Add sensor organization following WebUI layout + Backwash status (93d7f0b)
- feat: Add sensor calibration monitoring and status service (b13129a)
- feat: Phase 6 - Complete REFILL & OVERFLOW protection services (fae5665)
- Merge branch 'feature/complete-pool-controller-api' (41b04bc)
- i18n: Complete German translations for all new services (283332b)
- feat: Add active errors sensor to show all simultaneous error codes (3bc8130)
- Merge pull request #352 from Xerolux/feature/complete-pool-controller-api (9ba87b8)
- fix: Simplify feature-release workflow - use gh CLI directly (915d359)
- ci: Add feature-release workflow for automatic pre-release generation (ad293d5)
- docs: Phase 5 Part 2 - Add service translations for HTTP control, dosing, rule, and system config services (bc69036)
- feat: Phase 4 - Complete system configuration services (Extension Relays, Sensor Calibration) (06ba426)
- feat: Phase 3 - Complete rule management services (Temperature, Analog, Switching, Timer rules) (707e9b0)
- feature: phase 2 - dosing system configuration services (all 6 systems) (7abe236)
- feature: integrate new HTTP-based control services with setFunctionManually API (cedccbf)
- feature: phase 1 - state management, error handling, and HTTP control layer (3d587cf)

### 🚀 Improvements | Verbesserungen

- Remove verbose logging and force-update options from reconfigure flow (911510c)
- refactor: Remove redundant ROM-code exclusion checks (fb3cf0e)
- docs: Final update - ALL BACKLOG + OPTIONAL F COMPLETE (ee5afeb)
- docs: Final update - Phase 1-5 now ~95% COMPLETE (6b80261)
- docs: Final update to BACKLOG_PROGRESS - Phase 3-5 Status (8537dd5)
- docs: Add ARCHITECTURE.md and update CLAUDE.md (f3980a5)
- docs: Update BACKLOG_PROGRESS - Phase 1+2 complete (27ee065)
- docs: Update BACKLOG_PROGRESS for PR 2 status (5cc39e4)
- docs: Update CONTRIBUTING.md with current version requirements (42478ac)
- fix(deps): Update violet-poolController-api requirement to >=0.0.31 (9fe22a5)
- fix: Restore zh.json and update all translation files (d8e4c40)
- refactor: Address code review feedback on CHANGELOG (e03a00f)
- chore: Update contact email in Code of Conduct (ae69d1d)
- chore: prepare v2.0.0 release - update versions, workflows, and changelog (556a217)
- docs: update changelog with firmware version fix for beta.9 (f503065)
- fix: fetch firmware update info from getConfig endpoint (SYSTEM_swversion, SYSTEM_availableversion) (9be304b)
- fix: firmware update entity shows correct version (beta.9) (a334544)
- fix: enhance error management UI and entity duplication migration (27c86ff)
- feat: improve mock server with real controller keys from pooldigital-mock (9e31a47)
- fix: make firmware update entity visible and improve version detection (22e084c)
- chore(deps): update aiohttp requirement to >=3.14.1,<3.15 (927b0c3)
- chore(deps): update violet-poolcontroller-api requirement to >=0.0.29 (ec4dc17)
- fix: Violet Pool Controller 2.0.0-beta.7 — entity prefix migration, firmware update detection, new sensors (e0a10f3)
- fix: SSL default off, remove sensor picker, fix firmware update entity (011c26a)
- fix: Repair firmware update API calls and synchronize service translations (7c1abed)
- Merge pull request #357 from Xerolux/codex/fix-automatic-detection-and-update-issues (cc215c9)
- Merge pull request #356 from Xerolux/codex/update-pyproject.toml-version (538a4af)
- Fix Violet API compatibility and update device info (bd856ed)
- 📝 Release v2.0.0-beta.5 - Update changelog and version files (9a8c180)
- 📝 Release v2.0.0-beta.5 - Update changelog and version files (93a6d7a)
- refactor: Add EntityNameResolver import to all platforms (5b80c98)
- 📝 Release v2.0.0-beta.4 - Update changelog and version files (d0845d4)
- 📝 Release v2.0.0-beta.4 - Update changelog and version files (b3dd1d8)
- feat: Add firmware update entity and status service (9a35c76)
- 📝 Release v2.0.0-beta.3 - Update changelog and version files (7baeda1)
- 📝 Release v2.0.0-beta.3 - Update changelog and version files (0e79829)
- 📝 Release v2.0.0-beta.3 - Update changelog and version files (ed63713)
- 📝 Release v2.0.0-beta.2 - Update changelog and version files (9d80e73)
- 📝 Release v2.0.0-beta.1 - Update changelog and version files (0ae3b51)
- 📝 Release v2.0.0-beta.1 - Update changelog and version files (a4ae471)
- 📝 Release v2.0.0-beta.1 - Update changelog and version files (873086c)
- 📝 Release v1.2.4-pool-control - Update changelog and version files (c5a6c5d)
- 📝 Release v1.2.4-pool-control - Update changelog and version files (57406a7)
- refactor: Rename HTTP control services to avoid conflicts with legacy API (387ad20)
- chore: sync versions, fix mypy errors, and update tooling (f14f215)

### 🔧 Bug Fixes | Fehlerbehebungen

- Fix onewire (03b3abc)
- fix(sensors): Treat OneWire ROM-code sensors as text, not temperature (420673d)
- fix(ci): Use @main for trufflehog and trivy-action (pinned versions don't exist) (3a06f71)
- fix(lint): Separate first-party imports with blank line (ruff I001) (1bcf8fa)
- fix(lint): Sort imports alphabetically (ruff I001) (8d22c97)
- fix(ci): Revert hacs/action to @main (no pinnable version found) (ce8ce28)
- fix(ci): Correct action versions and tox configuration (eb368ed)
- fix: Add py313 support to tox configuration (334e653)
- Backlog Phase 1+2: Quick Wins, Dependencies & Functional Bugfixes (8f31cd4)
- fix: Correct violet_poolcontroller_api imports (c17f9eb)
- fix: Correct HACS and Hassfest action versions (e0317c0)
- fix: Resolve CodeQL warnings in test files (4707c65)
- fix(A4): Add logging to silent exception handlers (0efd90b)
- fix: Remove unused VioletReadings import (6ec1cbb)
- fix(A3): Use public API property instead of private _api (1b2ecc2)
- fix(A2): Add logging to connection test exception handling (eba2422)
- fix(B2): Correct hallucinated package versions in pyproject.toml (40638fb)
- fix(A1): Invalidate setpoint cache after successful poll (99023cb)
- build: Add CODEOWNERS file and fix hacs.json formatting (9d72eb0)
- fix(deps): Align dev dependencies in pyproject.toml with requirements-dev.txt (7bef238)
- fix(deps): Update violet-poolController-api requirement to >=0.0.31 (9fe22a5)
- fix: Integrate ONEWIRE_ROMCODE_SENSORS and fix case-sensitivity (a5d3ab2)
- fix: Restore fr.json from previous commit (29f98ca)
- fix: Restore zh.json and update all translation files (d8e4c40)
- fix: Final translation refinements for all languages (419c853)
- fix: Russian translation final updates (255b25c)
- fix: Final translation updates for es.json and ru.json (43b0271)
- fix: Correct 6 translation errors in German and fix technical terminology (66352b5)
- Fix: Use 'disabled' instead of 'enabled' for RegistryEntry (c76efc0)
- Fix: Use 'disabled' instead of 'enabled' for RegistryEntry attribute (d2d8c48)
- Fix safety settings storage and re-enable logic per review (6305d64)
- fix: Set state_class=None for DI-Rule stopwatch sensors (fde5f4f)
- fix: Remove @property decorator from _detect_current_hardware_modules (ca0d57b)
- fix: Remove @property decorator from _detect_current_hardware_modules (ab6df72)
- fix: Add missing @property decorator to device_info method (6d8b684)
- fix: Add missing @property decorator to device_info method (5290e03)
- fix: Remove redundant .keys() in dictionary iteration (d0a03ee)
- fix: Remove redundant .keys() in dictionary iteration (35e268f)
- Fix Onewire romcode sensors incorrectly getting °C unit assignment (0bb763b)
- Fix hardware module detection to use current API data instead of cached values (05c81cd)
- Fix CONF_VERIFY_SSL fallback to preserve existing user configuration (dc593c5)
- fix: address Sourcery AI code review issues (9f004d0)
- fix: address CodeQL warnings in security test suite (c6cfc6a)
- fix: normalize boolean config values to integers (0/1) globally (3f69aa6)
- fix: ensure DOSAGE_*_use config sends integer 0/1, not float (349b56c)
- fix: remove api-dependent tests from security test suite (515920e)
- fix: simplify security principles tests to match actual API (680e3a6)
- fix: correct test_security_principles.py imports and method signatures (42da769)
- fix: resolve aiohttp dependency conflict with violet-poolController-api (65e5ad8)
- docs: update changelog with firmware version fix for beta.9 (f503065)
- fix: fetch firmware update info from getConfig endpoint (SYSTEM_swversion, SYSTEM_availableversion) (9be304b)
- fix: sync all version numbers to 2.0.0-beta.9 and fix workflow validation (fe8cf6d)
- fix: firmware update entity shows correct version (beta.9) (a334544)
- fix: prevent duplicate entity ID prefix generation on new installs (fa160f3)
- fix: enhance error management UI and entity duplication migration (27c86ff)
- fix: use own seed values and fix VioletReadings test assertions (cb8cb6e)
- fix: make firmware update entity visible and improve version detection (22e084c)
- fix: collapse repeated domain slugs in entity_id migration (6d3b57b)
- fix: Violet Pool Controller 2.0.0-beta.7 — entity prefix migration, firmware update detection, new sensors (e0a10f3)
- fix: restore firmware version detection for both old and new key names (2b443b4)
- fix: migrate duplicate device-prefix entity_ids on startup (2d59349)
- fix: Correct system sensor key names and dosing response error handling (16bafd0)
- fix: SSL default off, remove sensor picker, fix firmware update entity (011c26a)
- fix: Correct firmware protocol violations in http_control and dosing indices (e0288d9)
- fix: Repair firmware update API calls and synchronize service translations (7c1abed)
- Merge pull request #357 from Xerolux/codex/fix-automatic-detection-and-update-issues (cc215c9)
- fix: avoid duplicate device prefixes in entity names (7bad05b)
- Fix API publish workflow dispatch version (9a6ba8c)
- Merge pull request #355 from Xerolux/codex/fix-import-error-in-violet_pool_controller (f3e3125)
- Fix cover platform API compatibility (1a13b26)
- Merge pull request #354 from Xerolux/codex/fix-import-error-in-violet_pool_controller (ef9094d)
- Fix Violet API compatibility and update device info (bd856ed)
- api-fix (71e47b3)
- fix: Enable error code sensor by default to show error descriptions (4f14b71)
- fix: Simplify feature-release workflow - use gh CLI directly (915d359)
- fix: Phase 5 Part 3 - Code quality improvements and linting fixes (2db6166)
- fix: remove invalid homeassistant key from manifest.json (a22a4c4)
- chore: sync versions, fix mypy errors, and update tooling (f14f215)

### 📚 Documentation | Dokumentation

- docs: sync wiki and pages context (cd2a7a5)
- docs: Final update - ALL BACKLOG + OPTIONAL F COMPLETE (ee5afeb)
- docs: Phase 3 COMPLETE - Test coverage 100% (2b964d5)
- docs: Final update - Phase 1-5 now ~95% COMPLETE (6b80261)
- docs: Final update to BACKLOG_PROGRESS - Phase 3-5 Status (8537dd5)
- docs: Add CI_CD_ACTION_PINNING.md guidelines (8ba65a4)
- docs: Add HA_QUALITY_SCALE_PROGRESS.md documentation (74a51fa)
- docs: Add ARCHITECTURE.md and update CLAUDE.md (f3980a5)
- docs: Update BACKLOG_PROGRESS - Phase 1+2 complete (27ee065)
- docs: Update BACKLOG_PROGRESS for PR 2 status (5cc39e4)
- docs: Add RELEASE_NOTES.md placeholder and BACKLOG_PROGRESS.md (d56fa16)
- docs: Update CONTRIBUTING.md with current version requirements (42478ac)
- docs: Add comprehensive CHANGELOG with breaking changes (German) (5337166)
- docs: Add comprehensive CHANGELOG with breaking changes (German) (3aae94f)
- docs: Add Code of Conduct for community standards (db63a20)
- docs: add markdown link references to CHANGELOG.md for direct GitHub navigation (7b5c38f)
- docs: add comprehensive security architecture documentation (13e0d38)
- docs: update changelog with firmware version fix for beta.9 (f503065)
- docs: privatize internal markdown docs and refresh wiki content (deeaa53)
- docs: Phase 5 Part 2 - Add service translations for HTTP control, dosing, rule, and system config services (bc69036)
- docs: Phase 5 Part 1 - Complete services.yaml with all HTTP control, dosing, rule, and system config services (374368a)

### 🧪 Tests

- fix: Resolve CodeQL warnings in test files (4707c65)
- docs: Phase 3 COMPLETE - Test coverage 100% (2b964d5)
- test(C1,C2,C3): Comprehensive API package test coverage (790e702)
- ci: Add Python 3.13 to validate.yml test matrix (5447134)
- fix(A2): Add logging to connection test exception handling (eba2422)
- fix: address CodeQL warnings in security test suite (c6cfc6a)
- fix: remove api-dependent tests from security test suite (515920e)
- fix: simplify security principles tests to match actual API (680e3a6)
- fix: use own seed values and fix VioletReadings test assertions (cb8cb6e)

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

📋 [Full changelog: v1.2.4...v2.0.0](https://github.com/Xerolux/violet-hass/compare/v1.2.4...v2.0.0)

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

_Generated automatically by GitHub Actions on 2026-06-16 17:26:59 UTC_
