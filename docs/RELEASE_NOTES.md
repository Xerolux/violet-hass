## v1.0.2-beta.2 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features | Neue Funktionen

- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements | Verbesserungen

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

📋 [Full changelog: v1.0.1...v1.0.2-beta.2](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.2)

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

_Generated automatically by GitHub Actions on 2026-02-24 13:02:41 UTC_
