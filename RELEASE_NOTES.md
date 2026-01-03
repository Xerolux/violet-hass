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
- 🤝 **[Contribute](https://github.com/Xerolux/violet-hass/blob/main/CONTRIBUTING.md)**

---

### 📄 Credits

**Developed by:** [Xerolux](https://github.com/Xerolux)
**Integration for:** Violet Pool Controller by PoolDigital GmbH & Co. KG
**License:** MIT

---

_Generated automatically by GitHub Actions on 2026-01-03 16:00:36 UTC_
