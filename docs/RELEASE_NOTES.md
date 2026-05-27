## v1.0.7-alpha.3 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

### ❤️ Support | Unterstützung

If you find this integration useful, consider supporting the developer. Every contribution, no matter how small, is a huge motivation to improve the project and keep it alive! Thank you! 🙏

Jeder kleine Beitrag hilft, die Motivation hochzuhalten, um das Projekt weiter zu verbessern und am Leben zu erhalten! Vielen Dank! 🙏

- 💳 **[PayPal](https://paypal.me/xerolux)**
- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **[Star this repository](https://github.com/Xerolux/violet-hass)**

---

---

### ✨ New Features | Neue Funktionen

- fix: Add missing translations for ADC and EXT sensors (f7bfaac)
- feat: v1.0.7-alpha.1 - EN migration, translation_key for 174 entities, 10-language support, dependency updates (f7e2bfa)
- feat: extend sticky-cache key restoration to ALL optional hardware modules (1b33abf)
- fix: add sticky cache for dosing module to prevent DOS_* switches showing OFF (ad66241)
- Translate all docs and wiki to English; add .de.md German alternatives (ecd37c1)
- feat: upgrade to home assistant 2026.5.0 (4f35d97)
- feat: add ON/OFF/AUTO select entities for all controllable switches (8505b85)

### 🚀 Improvements | Verbesserungen

- 📝 Release v1.0.7-alpha.3 - Update changelog and version files (3f586c3)
- refactor: Improve code quality and diagnostics (ad2238e)
- 📝 Release v1.0.7-alpha.3 - Update changelog and version files (04ae67a)
- 📝 Release v1.0.7-alpha.2 - Update changelog and version files (9cb1c7a)
- 📝 Release v1.0.7-alpha.1 - Update changelog and version files (57a80f1)
- chore(deps): update violet-poolController-api to 0.0.17 (ef42551)
- 📝 Release v1.0.6-alpha.3 - Update changelog and version files (e6cfc12)
- 📝 Release v1.0.6-alpha.2 - Update changelog and version files (e8828ca)
- chore(deps-dev): update pytest-cov requirement from >=6.0.0 to >=7.1.0 (9e33ab2)
- chore(deps): update aiohttp requirement from >=3.11.0 to >=3.13.5 (ff6db43)
- chore(deps): update voluptuous requirement from >=0.15.0 to >=0.16.0 (36f58b1)
- chore(deps-dev): update pytest-asyncio requirement (efbea30)
- chore(deps-dev): update ruff requirement from >=0.15.0 to >=0.15.12 (1f0ec40)
- chore(deps-dev): update mypy requirement from >=1.15.0 to >=1.20.2 (d5f6527)
- chore(deps-dev): update pytest requirement from >=9.0.0 to >=9.0.3 (382b18b)
- chore(deps-dev): update pytest-homeassistant-custom-component requirement (9e3b39d)
- 📝 Release v1.0.6-alpha.1 - Update changelog and version files (c809a6c)
- update-api-version-0-0-14 (cb6208d)
- Update violet-poolController-api to version 0.0.14 (35ab076)
- update-release-changelog-support-section (56ced0f)
- 📝 Release v1.0.5 - Update changelog and version files (acfcaa8)

### 🔧 Bug Fixes | Fehlerbehebungen

- fix: strings.json imp1_value von "Flow Switch" auf "Dosing Inflow" korrigiert (cbb5fca)
- fix: deutsche Lokalisierung – fehlende Translation-Keys, Select-Optionen und Zustandstexte (fb72cdd)
- fix: Correct IMP1 sensor name from 'Flow Switch' to 'Dosing Inflow' (d7519ad)
- fix: Add missing translations for ADC and EXT sensors (f7bfaac)
- fix: Enable translation keys for device entity names (33da009)
- chore: bump API to 0.0.18 (dosing endpoint fix), clean up 23 internal dev reports (38c11d5)
- fix: align translation_key casing with strings.json entries (579a266)
- /fix-release-workflow (3e67e06)
- fix: correct release workflow tag handling and bump to v1.0.7-alpha.2 (ef6e332)
- fix: prevent sensor unit flipping when controller returns boolean-like values (0/1) (524fba5)
- fix-interpret-state-unknown (693d7e7)
- fix: resolve CI failures for voluptuous dependency and test mocks (a6b597e)
- fix: prevent hard off state for unknown sensor data (09a3962)
- device-state-bug (18c967e)
- device-state-bug (a23cafe)
- fix: add sticky cache for dosing module to prevent DOS_* switches showing OFF (ad66241)
- fix: correct feature_id for DOS_6_FLOC (Flockmittel) from chlorine_control to flocculation (1b4bf39)
- fix-test-entity-state-mocks (8a31793)
- Fix ModuleNotFoundError in test suite for HA 2026 (9d12bf1)
- Fix CI tests for Home Assistant 2026.5.0 compatibility (41b8b4e)
- Fix CI tests for Home Assistant 2026.5.0 compatibility (4cec71d)
- Fix CI tests for Home Assistant 2026.5.0 compatibility (5c12e60)
- fix-ext1-api-switching (f761565)
- fix: EXT1/EXT2 sticky hardware detection + longer refresh delay (36cb133)

### 📚 Documentation | Dokumentation

- Translate all docs and wiki to English; add .de.md German alternatives (ecd37c1)
- Translate README from German to English (19d3843)

### 🧪 Tests

- fix: resolve CI failures for voluptuous dependency and test mocks (a6b597e)
- fix-test-entity-state-mocks (8a31793)
- Fix ModuleNotFoundError in test suite for HA 2026 (9d12bf1)
- Fix CI tests for Home Assistant 2026.5.0 compatibility (41b8b4e)
- Fix CI tests for Home Assistant 2026.5.0 compatibility (4cec71d)
- Fix CI tests for Home Assistant 2026.5.0 compatibility (5c12e60)

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

📋 [Full changelog: v1.0.5...v1.0.7-alpha.3](https://github.com/Xerolux/violet-hass/compare/v1.0.5...v1.0.7-alpha.3)

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

_Generated automatically by GitHub Actions on 2026-05-27 23:25:35 UTC_
