## v1.0.2 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features | Neue Funktionen

- Add list of installed components to diagnostic export (6f16d16)
- Add Home Assistant system info to diagnostic export (372f8be)
- Add detailed feature logging to diagnostic export (46a2eae)
- Add version 1.0.2-beta.5 to changelog (fed7182)
- Add export_diagnostic_logs service to troubleshooting guide (2850fb3)
- Add optional arguments to log export service (61b8bba)
- Add configuration settings and poll history to diagnostic log export (5b5fe8c)
- Add configuration settings to diagnostic log export (f522af0)
- Fix diagnostic log export path and add debug hint (4602573)
- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- fix: Add missing force_update option in settings (6ccc232)
- feat: Add diagnostic logging and log export service for troubleshooting (b50dac7)
- Add Force Update option to settings (7927ba0)
- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements | Verbesserungen

- Update README.md (d8c08bf)
- 📝 Release v1.0.2-beta.6 - Update changelog and version files (3139add)
- 📝 Release v1.0.2-beta.5 - Update changelog and version files (e41f6e1)
- workflow-update-remove (b5ec596)
- update-wiki-content (0c3cfb0)
- Update remaining wiki files with version 1.0.2-beta.5 (48d830a)
- Update wiki documentation to version 1.0.2-beta.5 (d521c4d)
- 📝 Release v1.0.2-beta.5 - Update changelog and version files (418c5fd)
- Enhance diagnostic log export with entity states and raw data (e6d8c69)
- 📝 Release v1.0.2-beta.5 - Update changelog and version files (316e76d)
- 📝 Release v1.0.2-beta.5 - Update changelog and version files (3f0d719)
- 📝 Release v1.0.2-beta.5 - Update changelog and version files (1682109)
- fix-cover-binary-sensor-force-update (5e4ee48)
- Refactor `CoverIsClosedBinarySensor` to inherit from `VioletPoolControllerEntity`. (7d47fac)
- 📝 Release v1.0.2-beta.4 - Update changelog and version files (11afbf8)
- refactor-recovery-api-retries (5453672)
- Refactor recovery logic, enable API retries, and remove deprecated code (b4cce7a)
- 📝 Release v1.0.2-beta.3 - Update changelog and version files (81a6b55)
- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- 📝 Release v1.0.2-beta.3 - Update changelog and version files (13d57e4)
- force-update-option (3778ec2)
- Add Force Update option to settings (7927ba0)
- 📝 Release v1.0.2-beta.2 - Update changelog and version files (6874e31)
- 📝 Release v1.0.2-beta.2 - Update changelog and version files (bb134ff)
- fix: resolve sensor update stalling caused by mutable dict reference (16ed441)
- 📝 Release v1.0.2-beta.1 - Update changelog and version files (c6c0cf0)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- config-device-refactor (3fa6b19)
- fix: correct 3 bugs in config_flow_utils and device after refactor (6e3e6d2)
- Fix static analysis errors and optimize entity performance (d074202)
- refactor/sensor-modules (b41984b)
- Refactor: Split sensor.py into modular structure (2ef7455)
- refactor/split-large-files (a2d0b83)
- Merge branch 'main' into refactor/split-large-files (b5992ed)
- security: Remove all passwords from repository and update .gitignore (6563515)
- refactor: Split config_flow.py into modular structure (2fe1f5c)
- /refactor-optimization-bugfix (c3ee1bf)
- Refactor config flow, optimize API calls, and fix linting issues (95144d0)
- 📝 Release v1.0.1 - Update changelog and version files (012a9a2)

### 🔧 Bug Fixes | Fehlerbehebungen

- Potential fix for code scanning alert no. 7040: Unused local variable (f3a9936)
- fix-ha-version-access-services (626fa5a)
- Fix: Replace deprecated `hass.config.version` with `homeassistant.const.__version__` in diagnostic logs. (8fd9380)
- enhanced-logging-and-sensor-fix (343ad18)
- fix-log-export-path (976d4d8)
- fix-log-export-path (cddb3a3)
- Fix diagnostic log export path and add debug hint (4602573)
- fix-hass-data-keyerror (e93e589)
- Fix KeyError in async_setup_entry by initializing hass.data[DOMAIN] (1c8ffef)
- fix-release-workflow-injection (07a4cb4)
- fix: use env vars in release workflow to prevent shell injection (edf65ca)
- fix-log-export-device-id (c930a35)
- Fix export_diagnostic_logs failing with Device not found (ebe9ccc)
- fix-cover-binary-sensor-force-update (5e4ee48)
- fix-sensor-log-spam (cadec9a)
- Fix log spam in contact sensor state class override (c98a906)
- fix: YAML parse error in services.yaml and ruff F541 cleanup in services.py (7b176ae)
- fix: services.yaml YAML error and optimistic cache leak on task cancellation (655855c)
- fix: dead code cleanup and recovery data propagation (8d94ca0)
- fix: Add missing force_update option in settings (6ccc232)
- fix-stuck-sensors-partial-updates (a4055e5)
- fix: prevent permanent optimistic cache staleness in number/switch/select (5a12b66)
- Fix: Prevent stuck sensor values by replacing device data instead of merging (395e5cc)
- fix: resolve sensor update stalling caused by mutable dict reference (16ed441)
- fix-github-actions (e9bfba6)
- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- fix: comprehensive code analysis - 8 bugs and race conditions resolved (d3564f7)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- fix: correct 3 bugs in config_flow_utils and device after refactor (6e3e6d2)
- Fix static analysis errors and optimize entity performance (d074202)
- /refactor-optimization-bugfix (c3ee1bf)
- Fix CI failure by allowing Claude Code action to fail (122f9ad)
- Refactor config flow, optimize API calls, and fix linting issues (95144d0)
- fix-readme-logo-url- (f0d309d)
- Fix broken logo URL in README.md (a9cdebc)
- fix: Pumpengeschwindigkeit zeigt korrekte aktive Stufe an (6cec3c6)
- fix: remove wrong RPM unit from PUMP_RPM state code sensors (10e27b3)

### 📚 Documentation | Dokumentation

- Update README.md (d8c08bf)
- Update wiki documentation to version 1.0.2-beta.5 (d521c4d)
- docs(wiki): Füge deutsche Erweiterte-Protokollierung Wiki-Seite hinzu (d1e0241)
- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Übersetze Extended Logging Dokumentation ins Deutsche (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Füge komplette Wiki-Dokumentation hinzu (d6188d6)
- docs: Erstelle komplette Wiki mit allen Features und Dokumentation (4e980f4)
- fix-readme-logo-url- (f0d309d)
- Fix broken logo URL in README.md (a9cdebc)

### 🧪 Tests

- Test: Complete integration test with all 14 features (1d98bef)

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

📋 [Full changelog: v1.0.1...v1.0.2](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2)

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

_Generated automatically by GitHub Actions on 2026-02-26 19:53:49 UTC_
