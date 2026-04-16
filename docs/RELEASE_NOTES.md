## v1.0.5-beta.2 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features | Neue Funktionen

- feat: add translation_key to HW_* hardware binary sensors (10 languages) (13f82dd)
- fix: add missing reconfigure step to strings.json (aa0b7d2)
- feat: implement automatic hardware detection with api 0.0.10 including standalone dosing (7930810)
- feat: implement automatic hardware detection with api 0.0.10 (708a146)
- feat: Update API to 0.0.6 and add standalone dosing config (c4199ed)
- feat: Update API to 0.0.8 and add standalone dosing config (4cb47ce)
- Add files via upload (ee3a816)
- feat: Add latest release option and auto-increment version (f191f68)
- chore(ci): add tox matrix and refactor diagnostics/config helpers (83d15c7)

### 🚀 Improvements | Verbesserungen

- fix-modules-api-update (18ae039)
- 📝 Release v1.0.5-beta.2 – Update version and changelog (81b4abf)
- fix: update to API 0.0.11, robust module detection, fix entity cleanup (e1666e1)
- 📝 Release v1.0.5-beta.1 - Update changelog and version files (a8ebbc3)
- Refactor: Simplify configuration flow to align with HA Core guidelines (45a4d0b)
- Refactor: Remove dosing_standalone from UI and dynamically show hardware modules in Device Info (af65117)
- 📝 Release v1.0.5-alpha.4 - Update changelog and version files (ca8e73c)
- 📝 Release v1.0.5-alpha.3 - Update changelog and version files (df3717b)
- 📝 Release v1.0.5-alpha.2 - Update changelog and version files (e8d3df3)
- Update manifest.json (020ff97)
- Update violet-poolController-api to version 0.0.8 (0ef62ee)
- update-api-dosing-standalone (df88f52)
- feat: Update API to 0.0.6 and add standalone dosing config (c4199ed)
- feat: Update API to 0.0.8 and add standalone dosing config (4cb47ce)
- 📝 Release v1.0.5-alpha.1 - Update changelog and version files (82aa7c3)
- refactor: reduce poll history memory footprint (cc339e8)
- Update HACS minimum HA version to 2026.3.0 (6e3a519)
- Update violet-poolController-api to 0.0.5 (334d9ca)
- chore(ci): add tox matrix and refactor diagnostics/config helpers (83d15c7)
- fix: align 1.0.5 version metadata and update test env requirements (00d87a6)
- refactor services into control and diagnostics modules (7ee8f79)
- Update version and dependency for violet_pool_controller (5017122)
- Update version to 1.0.5 (d5790ad)
- Update violet-poolController-api to version 0.0.4 (0d077e7)
- refactor config flow and service modules (5ace21f)
- 📝 Release v1.0.4 - Update changelog and version files (784bc44)

### 🔧 Bug Fixes | Fehlerbehebungen

- fix-modules-api-update (18ae039)
- fix: dosing_standalone config read + complete translation coverage (103565d)
- fix: add missing reconfigure step to strings.json (aa0b7d2)
- fix: update to API 0.0.11, robust module detection, fix entity cleanup (e1666e1)
- chore: fix ruff linting errors and warnings in test suite (6cc7439)
- chore: fix ruff linting errors and warnings in test suite (af6a96e)
- fix(ci): stabilize config flow tests for zeroconf and invalid host (bd3f547)
- fix-bugs (1469f03)
- fix: two more bugs - PUMP_RPM_0 missing and wrong float fallback (cabf378)
- fix: resolve type safety, None-safety and async task bugs (84c6efb)
- fix: align 1.0.5 version metadata and update test env requirements (00d87a6)

### 📚 Documentation | Dokumentation

- docs: align README and testing docs with current requirements (2d280e7)

### 🧪 Tests

- test-linter-errors (301aedc)
- chore: fix ruff linting errors and warnings in test suite (6cc7439)
- chore: fix ruff linting errors and warnings in test suite (af6a96e)
- test: cover config flow IP literal helper (4063b29)
- fix(ci): stabilize config flow tests for zeroconf and invalid host (bd3f547)
- docs: align README and testing docs with current requirements (2d280e7)
- fix: align 1.0.5 version metadata and update test env requirements (00d87a6)

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

📋 [Full changelog: v1.0.4...v1.0.5-beta.2](https://github.com/Xerolux/violet-hass/compare/v1.0.4...v1.0.5-beta.2)

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

_Generated automatically by GitHub Actions on 2026-04-16 04:37:29 UTC_
