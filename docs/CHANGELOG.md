# Changelog

All notable changes to this project will be documented in this file.
## [1.0.7-alpha.3] - 2026-05-27

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

---

## [1.0.7-alpha.3] - 2026-05-27

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

- feat: v1.0.7-alpha.1 - EN migration, translation_key for 174 entities, 10-language support, dependency updates (f7e2bfa)
- feat: extend sticky-cache key restoration to ALL optional hardware modules (1b33abf)
- fix: add sticky cache for dosing module to prevent DOS_* switches showing OFF (ad66241)
- Translate all docs and wiki to English; add .de.md German alternatives (ecd37c1)
- feat: upgrade to home assistant 2026.5.0 (4f35d97)
- feat: add ON/OFF/AUTO select entities for all controllable switches (8505b85)

### 🚀 Improvements | Verbesserungen

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

_Generated automatically by GitHub Actions on 2026-05-27 22:57:23 UTC_

---

## [1.0.7-alpha.3] - 2026-05-27

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

- feat: v1.0.7-alpha.1 - EN migration, translation_key for 174 entities, 10-language support, dependency updates (f7e2bfa)
- feat: extend sticky-cache key restoration to ALL optional hardware modules (1b33abf)
- fix: add sticky cache for dosing module to prevent DOS_* switches showing OFF (ad66241)
- Translate all docs and wiki to English; add .de.md German alternatives (ecd37c1)
- feat: upgrade to home assistant 2026.5.0 (4f35d97)
- feat: add ON/OFF/AUTO select entities for all controllable switches (8505b85)

### 🚀 Improvements | Verbesserungen

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

_Generated automatically by GitHub Actions on 2026-05-27 22:16:45 UTC_

---

## [1.0.7-alpha.2] - 2026-05-27

## v1.0.7-alpha.2 – Violet Pool Controller

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

- feat: v1.0.7-alpha.1 - EN migration, translation_key for 174 entities, 10-language support, dependency updates (f7e2bfa)
- feat: extend sticky-cache key restoration to ALL optional hardware modules (1b33abf)
- fix: add sticky cache for dosing module to prevent DOS_* switches showing OFF (ad66241)
- Translate all docs and wiki to English; add .de.md German alternatives (ecd37c1)
- feat: upgrade to home assistant 2026.5.0 (4f35d97)
- feat: add ON/OFF/AUTO select entities for all controllable switches (8505b85)

### 🚀 Improvements | Verbesserungen

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

📋 [Full changelog: v1.0.5...v1.0.7-alpha.2](https://github.com/Xerolux/violet-hass/compare/v1.0.5...v1.0.7-alpha.2)

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

_Generated automatically by GitHub Actions on 2026-05-27 19:30:03 UTC_

---

## [1.0.7-alpha.1] - 2026-05-27

## v1.0.7-alpha.1 – Violet Pool Controller

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

- feat: v1.0.7-alpha.1 - EN migration, translation_key for 174 entities, 10-language support, dependency updates (f7e2bfa)
- feat: extend sticky-cache key restoration to ALL optional hardware modules (1b33abf)
- fix: add sticky cache for dosing module to prevent DOS_* switches showing OFF (ad66241)
- Translate all docs and wiki to English; add .de.md German alternatives (ecd37c1)
- feat: upgrade to home assistant 2026.5.0 (4f35d97)
- feat: add ON/OFF/AUTO select entities for all controllable switches (8505b85)

### 🚀 Improvements | Verbesserungen

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

📋 [Full changelog: v1.0.5...v1.0.7-alpha.1](https://github.com/Xerolux/violet-hass/compare/v1.0.5...v1.0.7-alpha.1)

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

_Generated automatically by GitHub Actions on 2026-05-27 16:00:39 UTC_

---

## [1.0.6-alpha.3] - 2026-05-22

## v1.0.6-alpha.3 – Violet Pool Controller

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

- feat: extend sticky-cache key restoration to ALL optional hardware modules (1b33abf)
- fix: add sticky cache for dosing module to prevent DOS_* switches showing OFF (ad66241)
- Translate all docs and wiki to English; add .de.md German alternatives (ecd37c1)
- feat: upgrade to home assistant 2026.5.0 (4f35d97)
- feat: add ON/OFF/AUTO select entities for all controllable switches (8505b85)

### 🚀 Improvements | Verbesserungen

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

📋 [Full changelog: v1.0.5...v1.0.6-alpha.3](https://github.com/Xerolux/violet-hass/compare/v1.0.5...v1.0.6-alpha.3)

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

_Generated automatically by GitHub Actions on 2026-05-22 21:01:22 UTC_

---

## [1.0.6-alpha.2] - 2026-05-22

## v1.0.6-alpha.2 – Violet Pool Controller

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

- feat: extend sticky-cache key restoration to ALL optional hardware modules (1b33abf)
- fix: add sticky cache for dosing module to prevent DOS_* switches showing OFF (ad66241)
- Translate all docs and wiki to English; add .de.md German alternatives (ecd37c1)
- feat: upgrade to home assistant 2026.5.0 (4f35d97)
- feat: add ON/OFF/AUTO select entities for all controllable switches (8505b85)

### 🚀 Improvements | Verbesserungen

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

📋 [Full changelog: v1.0.5...v1.0.6-alpha.2](https://github.com/Xerolux/violet-hass/compare/v1.0.5...v1.0.6-alpha.2)

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

_Generated automatically by GitHub Actions on 2026-05-22 20:47:19 UTC_

---

## [1.0.6-alpha.1] - 2026-05-02

## v1.0.6-alpha.1 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

### ❤️ Support

If you find this integration useful, consider supporting the developer. Every contribution, no matter how small, is a huge motivation to improve the project and keep it alive! Thank you! 🙏


- 💳 **[PayPal](https://paypal.me/xerolux)**
- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **[Star this repository](https://github.com/Xerolux/violet-hass)**

---

---

### ⚠️ BREAKING CHANGE

**Home Assistant 2026.5.0+ is now required!**
Due to core platform changes (specifically the removal of `ZeroconfServiceInfo` from `homeassistant.components.zeroconf`), this integration now requires Home Assistant version 2026.5.0 or newer. If you are running an older version, please upgrade Home Assistant before installing this update.


### ✨ New Features

- feat: add ON/OFF/AUTO select entities for all controllable switches (8505b85)

### 🚀 Improvements

- update-api-version-0-0-14 (cb6208d)
- Update violet-poolController-api to version 0.0.14 (35ab076)
- update-release-changelog-support-section (56ced0f)
- 📝 Release v1.0.5 - Update changelog and version files (acfcaa8)

### 🔧 Bug Fixes

- fix-ext1-api-switching (f761565)
- fix: EXT1/EXT2 sticky hardware detection + longer refresh delay (36cb133)

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

📋 [Full changelog: v1.0.5...v1.0.6-alpha.1](https://github.com/Xerolux/violet-hass/compare/v1.0.5...v1.0.6-alpha.1)

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

_Generated automatically by GitHub Actions on 2026-05-02 17:34:12 UTC_

---

## [1.0.5] - 2026-04-23

## v1.0.5 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

- feat: add translation_key to HW_* hardware binary sensors (10 languages) (13f82dd)
- fix: add missing reconfigure step to strings.json (aa0b7d2)
- feat: implement automatic hardware detection with api 0.0.10 including standalone dosing (7930810)
- feat: implement automatic hardware detection with api 0.0.10 (708a146)
- feat: Update API to 0.0.6 and add standalone dosing config (c4199ed)
- feat: Update API to 0.0.8 and add standalone dosing config (4cb47ce)
- Add files via upload (ee3a816)
- feat: Add latest release option and auto-increment version (f191f68)
- chore(ci): add tox matrix and refactor diagnostics/config helpers (83d15c7)

### 🚀 Improvements

- 📝 Release v1.0.5-beta.3 - Update changelog and version files (056eab4)
- 📝 Release v1.0.5-beta.2 - Update changelog and version files (836e435)
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
- Update HACS minimum HA version to 2026.5.0 (6e3a519)
- Update violet-poolController-api to 0.0.5 (334d9ca)
- chore(ci): add tox matrix and refactor diagnostics/config helpers (83d15c7)
- fix: align 1.0.5 version metadata and update test env requirements (00d87a6)
- refactor services into control and diagnostics modules (7ee8f79)
- Update version and dependency for violet_pool_controller (5017122)
- Update version to 1.0.5 (d5790ad)
- Update violet-poolController-api to version 0.0.4 (0d077e7)
- refactor config flow and service modules (5ace21f)
- 📝 Release v1.0.4 - Update changelog and version files (784bc44)

### 🔧 Bug Fixes

- Release v1.0.5-beta.3 - upgrade API to 0.0.12, fix dosing key mismatch (677eb93)
- Fix dosing daily amount key mismatch in switch attributes (5b32af7)
- fix-hardware-detection-ext2 (b7c9e43)
- fix: robust hardware module detection checking valid values (6d1409e)
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

### 📚 Documentation

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

📋 [Full changelog: v1.0.4...v1.0.5](https://github.com/Xerolux/violet-hass/compare/v1.0.4...v1.0.5)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-04-23 04:54:12 UTC_

---

## [1.0.5] - 2026-04-22

## v1.0.5 – Violet Pool Controller

🟢 **STABLE RELEASE**

---

🟢 **STABLE RELEASE**

---

🟢 **STABLE RELEASE**

### ✨ New Features

- feat: add translation_key to HW_* hardware binary sensors (10 languages) (13f82dd)
- fix: add missing reconfigure step to strings.json (aa0b7d2)
- feat: implement automatic hardware detection with api 0.0.10 including standalone dosing (7930810)
- feat: implement automatic hardware detection with api 0.0.10 (708a146)
- feat: Update API to 0.0.6 and add standalone dosing config (c4199ed)
- feat: Update API to 0.0.8 and add standalone dosing config (4cb47ce)
- Add files via upload (ee3a816)
- feat: Add latest release option and auto-increment version (f191f68)
- chore(ci): add tox matrix and refactor diagnostics/config helpers (83d15c7)

### 🚀 Improvements

- 📝 Release v1.0.5 - Update changelog and version files (836e435)
- fix-modules-api-update (18ae039)
- 📝 Release v1.0.5 – Update version and changelog (81b4abf)
- fix: update to API 0.0.11, robust module detection, fix entity cleanup (e1666e1)
- 📝 Release v1.0.5 - Update changelog and version files (a8ebbc3)
- Refactor: Simplify configuration flow to align with HA Core guidelines (45a4d0b)
- Refactor: Remove dosing_standalone from UI and dynamically show hardware modules in Device Info (af65117)
- 📝 Release v1.0.5 - Update changelog and version files (ca8e73c)
- 📝 Release v1.0.5 - Update changelog and version files (df3717b)
- 📝 Release v1.0.5 - Update changelog and version files (e8d3df3)
- Update manifest.json (020ff97)
- Update violet-poolController-api to version 0.0.8 (0ef62ee)
- update-api-dosing-standalone (df88f52)
- feat: Update API to 0.0.6 and add standalone dosing config (c4199ed)
- feat: Update API to 0.0.8 and add standalone dosing config (4cb47ce)
- 📝 Release v1.0.5 - Update changelog and version files (82aa7c3)
- refactor: reduce poll history memory footprint (cc339e8)
- Update HACS minimum HA version to 2026.5.0 (6e3a519)
- Update violet-poolController-api to 0.0.5 (334d9ca)
- chore(ci): add tox matrix and refactor diagnostics/config helpers (83d15c7)
- fix: align 1.0.5 version metadata and update test env requirements (00d87a6)
- refactor services into control and diagnostics modules (7ee8f79)
- Update version and dependency for violet_pool_controller (5017122)
- Update version to 1.0.5 (d5790ad)
- Update violet-poolController-api to version 0.0.4 (0d077e7)
- refactor config flow and service modules (5ace21f)
- 📝 Release v1.0.4 - Update changelog and version files (784bc44)

### 🔧 Bug Fixes

- Release v1.0.5 - upgrade API to 0.0.12, fix dosing key mismatch (677eb93)
- Fix dosing daily amount key mismatch in switch attributes (5b32af7)
- fix-hardware-detection-ext2 (b7c9e43)
- fix: robust hardware module detection checking valid values (6d1409e)
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

### 📚 Documentation

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
1. Add custom repository: `https://github.com/Xerolux/violet-hass`
2. Install "Violet Pool Controller"
3. Restart Home Assistant

**Manual:**
1. Download latest release
2. Extract to `custom_components/violet_pool_controller`
3. Restart Home Assistant

---

📋 [Full changelog: v1.0.4...v1.0.5](https://github.com/Xerolux/violet-hass/compare/v1.0.4...v1.0.5)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:
<a href="https://www.buymeacoffee.com/xerolux" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" ></a>

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

## [1.0.4] - 2026-03-26

## v1.0.4 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

- Merge pull request #280 from Xerolux/claude/add-code-headers-9tKo5 (52c47ab)
- Add Xerolux 2026 copyright headers to all Python source files (411845a)
- add-claude-documentation (47ddfa0)
- add-port-configuration (c7faedd)
- Feat: Add port configuration to setup flow and API client (2b4e285)
- Merge branch 'main' into feat/github-pages-landing-3280418167961250373 (42fb8f6)
- feat: add landing page for github pages with sponsor and shop links\n\n- Created a responsive `index.html` as the landing page based on README.md.\n- Added GitHub Sponsors, Ko-fi, Buy Me a Coffee, Tesla referral, and PayPal badges.\n- Added a link to the PoolDigital Shop.\n- Removed all `target="_blank"` attributes for security scanner compliance. (bd97a08)
- feat: create github pages landing page with sponsors and shop link (cf49372)
- fix: add missing rel attributes to external links (ceaaacf)
- feat: add GitHub Pages landing page (index.html) (d5172a8)
- update-api-and-add-workflow (5531acc)
- feat: update API to 0.0.2 and add auto-update workflow (c92c0f1)
- docs: Update PyPI migration guide to reflect new target repo and module name (edb8257)
- docs: Add PyPI migration boilerplate and instructions (1190d66)

### 🚀 Improvements

- docs: update CLAUDE.md to reflect v1.0.4-beta.1 codebase state (6b46549)
- update-dependencies-2026 (467af10)
- Update dependencies for HA 2026.5.0 compatibility (de0f114)
- Update sponsorship badges in README.md (e59249e)
- refactor(translations): sync translation keys and remove emojis (8788efb)
- Update violet-poolController-api version to 0.0.3 (a0b093c)
- update-api-and-add-workflow (5531acc)
- feat: update API to 0.0.2 and add auto-update workflow (c92c0f1)
- refactor-migrate-to-pypi-api (c6130de)
- Refactor: Migrate to standalone PyPI violet-poolController-api package (dacf019)
- docs: Update PyPI migration guide to reflect new target repo and module name (edb8257)
- Refactor: Extract API into isolated internal package (99e4f90)
- Refactor configuration keys to use standard homeassistant.const (f2d1941)
- Refactor configuration keys to use standard homeassistant.const (d6d89af)
- 📝 Release v1.0.3 - Update changelog and version files (472606d)

### 🔧 Bug Fixes

- fix: resolve 12 bugs and compatibility issues (2182c37)
- fix: remove target blank to resolve security scanner issues (d37e44d)
- fix: standardise noopener noreferrer format (935116c)
- fix: add missing rel attributes to external links (ceaaacf)
- fix: prevent detached HEAD state in release workflow (bcfd477)

### 📚 Documentation

- add-claude-documentation (47ddfa0)
- docs: update CLAUDE.md to reflect v1.0.4-beta.1 codebase state (6b46549)
- Update sponsorship badges in README.md (e59249e)
- feat: add landing page for github pages with sponsor and shop links\n\n- Created a responsive `index.html` as the landing page based on README.md.\n- Added GitHub Sponsors, Ko-fi, Buy Me a Coffee, Tesla referral, and PayPal badges.\n- Added a link to the PoolDigital Shop.\n- Removed all `target="_blank"` attributes for security scanner compliance. (bd97a08)
- docs: Update PyPI migration guide to reflect new target repo and module name (edb8257)
- docs: Add PyPI migration boilerplate and instructions (1190d66)

### 🧪 Tests

- I have updated the quality scale to platinum and fixed the associated tests. Here is a summary of the changes I made: (b0bfc6a)

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

📋 [Full changelog: v1.0.3...v1.0.4](https://github.com/Xerolux/violet-hass/compare/v1.0.3...v1.0.4)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-26 06:22:11 UTC_

---

## [1.0.4] - 2026-03-13

## v1.0.4 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

- **PyPI-Migration**: Complete migration to standalone `violet-poolController-api` package (v0.0.2)
  - API now distributed as separate PyPI package for better modularity
  - Automatic dependency management through PyPI
  - Reduced integration size and complexity
- **Auto-Update Workflow**: Added GitHub Actions workflow to automatically check for PyPI API updates
  - Weekly checks for new API versions
  - Automatic PR creation for dependency updates
- **Refactored Configuration Keys**: Migrated to standard `homeassistant.const` keys
  - Better compatibility with Home Assistant Core requirements
  - Cleaner configuration handling

### 🚀 Improvements

- **Platinum Quality Scale**: Integration now certified at Platinum level
- **HACS Integration**: Improved HACS default instructions and workflows
- **CI/CD Enhancements**: Split HACS and hassfest workflows for better performance

### 🔧 Bug Fixes

- Fixed import paths for PyPI API package
- Updated all API references to use new module structure
- Ensured backward compatibility during migration

### ⚠️ Breaking Changesen

- Requires `violet-poolController-api==0.0.2` as external dependency
- Old internal API module removed - ensure PyPI package is installed

### 📋 Technical Details

- **API Package**: `violet-poolController-api v0.0.2`
- **Dependencies**: `aiohttp>=3.10.0`, `violet-poolController-api==0.0.2`
- **Home Assistant**: 2025.12.0+ (tested up to 2026.5.0.x)
- **Python**: 3.12+

## [1.0.3] - 2026-03-09

## v1.0.3 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

- add-quality-scale-manifest (07e1381)
- chore: add quality scale platinum to manifest.json (2b837c1)
- chore: add quality scale platinum to manifest.json (722e5c1)
- add-hacs-badge (c0d6566)
- docs: add My Home Assistant badge for HACS integration (1261b16)
- feat: Add comprehensive disclaimer, icon optimization, and dark mode support (March 2025) (f32b3a1)
- Add GitHub Action testing for HA 2026.5.0 and Python 3.14 (878e93a)
- add-custom-icon (92e25fe)
- feat: add stale, status-check and auto-label PR workflows (4fe0174)
- Add-custom-icon (65b96a7)
- Add VIOLET_144.png as icon.png to root and component dirs (d3141ae)
- feat: add diagnostics support for HA diagnostics download (8e14741)
- feat: add diagnostics support for HA diagnostics download (88527b9)
- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- 📝 Release v0.1.3 - Update changelog and version files (6d61fb1)
- ci: improve trigger reliability for validation workflows (16a7fcf)
- 📝 Release v0.1.3 - Update changelog and version files (e27c53c)
- 📝 Release v1.0.3 - Update changelog and version files (afd3fc0)
- docs: fix broken internal and external links in GitHub Wiki and update dates (3958807)
- 📝 Release v1.0.3-beta.4 - Update changelog and version files (19aafb9)
- Document pytest-homeassistant-custom-component update policy (6d65c0b)
- 📝 Release v1.0.3-beta.3 - Update changelog and version files (94eebbd)
- Update logo to match brand (d3a089a)
- Update custom integration brand images structure (e190831)
- 📝 Release v1.0.3-beta.3 - Update changelog and version files (a57b380)
- Update integration logo to official Violet icon (8c23aff)
- 📝 Release v1.0.3-beta.2 - Update changelog and version files (fc7ba31)
- Update FUNDING.yml (499a6d5)
- 📝 Release v1.0.3-beta.1 - Update changelog and version files (1fc2bce)
- 📝 Release v1.0.3-alpha.4 - Update changelog and version files (55a78f6)
- 📝 Release v1.0.3-alpha.3 - Update changelog and version files (de05bf5)
- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- fix-test-env-setup (48649a0)
- fix-quality-scale (8bc33d4)
- fix-wiki-links (95274da)
- docs: fix broken internal and external links in GitHub Wiki and update dates (3958807)
- docs: fix broken internal and external links in GitHub Wiki (53bdbec)
- Fix critical zeroconf discovery API compatibility for HA 2026.x (1efc579)
- fix: production bugs, HA 2026.5.0/Python 3.14 compatibility, test suite fixes (4f153f6)
- fix: correct permissions for actions/labeler (afbb57a)
- fix: cleanup auto-label-pr.yml logic (a85edd6)
- fix: prevent command injection and ensure syntax correctness (8e48cd2)
- Fix code formatting in climate.py (fe7ebde)
- fix-zeroconf-discovery-filter (eaa3ed3)
- fix: restrict zeroconf discovery to violet devices (05a94c9)
- fix: make forum login detection robust and fix BBCode URL typo (20216eb)
- Merge branch 'main' into claude/fix-zeroconf-import-error-tplZf (e2f4cd8)
- fix-zeroconf-import-error (4baba0c)
- fix-zeroconf-import-error (739df44)
- fix: move repairs imports to homeassistant.helpers.issue_registry for HA 2026 (3a9d087)
- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- docs: verify hassfest action is present (ef0ef51)
- docs: Provide v1.0.2 PR template links (fee9f75)
- docs: explain how HACS names and searches work (29079f7)
- docs: provide instructions for adding to hacs default (2697277)
- docs: review and analyze HA/HACS guidelines compliance (06bf5d1)
- docs: add My Home Assistant badge for HACS integration (1261b16)
- docs: fix broken internal and external links in GitHub Wiki and update dates (3958807)
- docs: fix broken internal and external links in GitHub Wiki (53bdbec)
- docs: Merge github_wiki_content into docs/wiki (605af30)
- docs: slim README, expand wiki with diagnostics page and HA 2026 notes (55ce11b)
- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix-test-env-setup (48649a0)
- build(tests): Make test environment setup script more robust (8c7bc55)
- I have updated the Home Assistant quality scale to Silver, as the Gold and Platinum requirements are not yet fully met and verified (specifically the 95% test coverage). (c125d8e)
- Simplify CI: Only test Python 3.14 + HA 2026.5.0 (6604006)
- Add GitHub Action testing for HA 2026.5.0 and Python 3.14 (878e93a)
- fix: production bugs, HA 2026.5.0/Python 3.14 compatibility, test suite fixes (4f153f6)
- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-09 10:03:36 UTC_

---

## [0.1.3] - 2026-03-09

## v0.1.3 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

- add-quality-scale-manifest (07e1381)
- chore: add quality scale platinum to manifest.json (2b837c1)
- chore: add quality scale platinum to manifest.json (722e5c1)
- add-hacs-badge (c0d6566)
- docs: add My Home Assistant badge for HACS integration (1261b16)
- feat: Add comprehensive disclaimer, icon optimization, and dark mode support (March 2025) (f32b3a1)
- Add GitHub Action testing for HA 2026.5.0 and Python 3.14 (878e93a)
- add-custom-icon (92e25fe)
- feat: add stale, status-check and auto-label PR workflows (4fe0174)
- Add-custom-icon (65b96a7)
- Add VIOLET_144.png as icon.png to root and component dirs (d3141ae)
- feat: add diagnostics support for HA diagnostics download (8e14741)
- feat: add diagnostics support for HA diagnostics download (88527b9)
- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- ci: improve trigger reliability for validation workflows (16a7fcf)
- 📝 Release v0.1.3 - Update changelog and version files (e27c53c)
- 📝 Release v1.0.3 - Update changelog and version files (afd3fc0)
- docs: fix broken internal and external links in GitHub Wiki and update dates (3958807)
- 📝 Release v1.0.3-beta.4 - Update changelog and version files (19aafb9)
- Document pytest-homeassistant-custom-component update policy (6d65c0b)
- 📝 Release v1.0.3-beta.3 - Update changelog and version files (94eebbd)
- Update logo to match brand (d3a089a)
- Update custom integration brand images structure (e190831)
- 📝 Release v1.0.3-beta.3 - Update changelog and version files (a57b380)
- Update integration logo to official Violet icon (8c23aff)
- 📝 Release v1.0.3-beta.2 - Update changelog and version files (fc7ba31)
- Update FUNDING.yml (499a6d5)
- 📝 Release v1.0.3-beta.1 - Update changelog and version files (1fc2bce)
- 📝 Release v1.0.3-alpha.4 - Update changelog and version files (55a78f6)
- 📝 Release v1.0.3-alpha.3 - Update changelog and version files (de05bf5)
- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- fix-test-env-setup (48649a0)
- fix-quality-scale (8bc33d4)
- fix-wiki-links (95274da)
- docs: fix broken internal and external links in GitHub Wiki and update dates (3958807)
- docs: fix broken internal and external links in GitHub Wiki (53bdbec)
- Fix critical zeroconf discovery API compatibility for HA 2026.x (1efc579)
- fix: production bugs, HA 2026.5.0/Python 3.14 compatibility, test suite fixes (4f153f6)
- fix: correct permissions for actions/labeler (afbb57a)
- fix: cleanup auto-label-pr.yml logic (a85edd6)
- fix: prevent command injection and ensure syntax correctness (8e48cd2)
- Fix code formatting in climate.py (fe7ebde)
- fix-zeroconf-discovery-filter (eaa3ed3)
- fix: restrict zeroconf discovery to violet devices (05a94c9)
- fix: make forum login detection robust and fix BBCode URL typo (20216eb)
- Merge branch 'main' into claude/fix-zeroconf-import-error-tplZf (e2f4cd8)
- fix-zeroconf-import-error (4baba0c)
- fix-zeroconf-import-error (739df44)
- fix: move repairs imports to homeassistant.helpers.issue_registry for HA 2026 (3a9d087)
- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- docs: verify hassfest action is present (ef0ef51)
- docs: Provide v1.0.2 PR template links (fee9f75)
- docs: explain how HACS names and searches work (29079f7)
- docs: provide instructions for adding to hacs default (2697277)
- docs: review and analyze HA/HACS guidelines compliance (06bf5d1)
- docs: add My Home Assistant badge for HACS integration (1261b16)
- docs: fix broken internal and external links in GitHub Wiki and update dates (3958807)
- docs: fix broken internal and external links in GitHub Wiki (53bdbec)
- docs: Merge github_wiki_content into docs/wiki (605af30)
- docs: slim README, expand wiki with diagnostics page and HA 2026 notes (55ce11b)
- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix-test-env-setup (48649a0)
- build(tests): Make test environment setup script more robust (8c7bc55)
- I have updated the Home Assistant quality scale to Silver, as the Gold and Platinum requirements are not yet fully met and verified (specifically the 95% test coverage). (c125d8e)
- Simplify CI: Only test Python 3.14 + HA 2026.5.0 (6604006)
- Add GitHub Action testing for HA 2026.5.0 and Python 3.14 (878e93a)
- fix: production bugs, HA 2026.5.0/Python 3.14 compatibility, test suite fixes (4f153f6)
- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v0.1.3](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v0.1.3)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-09 09:57:06 UTC_

---

## [0.1.3] - 2026-03-09

## v0.1.3 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

- Enhanced Violet Pool Controller functionality

### 🚀 Improvements

- 📝 Release v1.0.3 - Update changelog and version files (afd3fc0)

### 🔧 Bug Fixes

- Minor bug fixes and stability improvements

### 📚 Documentation

- docs: verify hassfest action is present (ef0ef51)
- docs: Provide v1.0.2 PR template links (fee9f75)
- docs: explain how HACS names and searches work (29079f7)
- docs: provide instructions for adding to hacs default (2697277)

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

📋 [Full changelog: v1.0.3...v0.1.3](https://github.com/Xerolux/violet-hass/compare/v1.0.3...v0.1.3)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-09 09:49:19 UTC_

---

## [1.0.3] - 2026-03-09

## v1.0.3 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

- add-quality-scale-manifest (07e1381)
- chore: add quality scale platinum to manifest.json (2b837c1)
- chore: add quality scale platinum to manifest.json (722e5c1)
- add-hacs-badge (c0d6566)
- docs: add My Home Assistant badge for HACS integration (1261b16)
- feat: Add comprehensive disclaimer, icon optimization, and dark mode support (March 2025) (f32b3a1)
- Add GitHub Action testing for HA 2026.5.0 and Python 3.14 (878e93a)
- add-custom-icon (92e25fe)
- feat: add stale, status-check and auto-label PR workflows (4fe0174)
- Add-custom-icon (65b96a7)
- Add VIOLET_144.png as icon.png to root and component dirs (d3141ae)
- feat: add diagnostics support for HA diagnostics download (8e14741)
- feat: add diagnostics support for HA diagnostics download (88527b9)
- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- docs: fix broken internal and external links in GitHub Wiki and update dates (3958807)
- 📝 Release v1.0.3-beta.4 - Update changelog and version files (19aafb9)
- Document pytest-homeassistant-custom-component update policy (6d65c0b)
- 📝 Release v1.0.3-beta.3 - Update changelog and version files (94eebbd)
- Update logo to match brand (d3a089a)
- Update custom integration brand images structure (e190831)
- 📝 Release v1.0.3-beta.3 - Update changelog and version files (a57b380)
- Update integration logo to official Violet icon (8c23aff)
- 📝 Release v1.0.3-beta.2 - Update changelog and version files (fc7ba31)
- Update FUNDING.yml (499a6d5)
- 📝 Release v1.0.3-beta.1 - Update changelog and version files (1fc2bce)
- 📝 Release v1.0.3-alpha.4 - Update changelog and version files (55a78f6)
- 📝 Release v1.0.3-alpha.3 - Update changelog and version files (de05bf5)
- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- fix-test-env-setup (48649a0)
- fix-quality-scale (8bc33d4)
- fix-wiki-links (95274da)
- docs: fix broken internal and external links in GitHub Wiki and update dates (3958807)
- docs: fix broken internal and external links in GitHub Wiki (53bdbec)
- Fix critical zeroconf discovery API compatibility for HA 2026.x (1efc579)
- fix: production bugs, HA 2026.5.0/Python 3.14 compatibility, test suite fixes (4f153f6)
- fix: correct permissions for actions/labeler (afbb57a)
- fix: cleanup auto-label-pr.yml logic (a85edd6)
- fix: prevent command injection and ensure syntax correctness (8e48cd2)
- Fix code formatting in climate.py (fe7ebde)
- fix-zeroconf-discovery-filter (eaa3ed3)
- fix: restrict zeroconf discovery to violet devices (05a94c9)
- fix: make forum login detection robust and fix BBCode URL typo (20216eb)
- Merge branch 'main' into claude/fix-zeroconf-import-error-tplZf (e2f4cd8)
- fix-zeroconf-import-error (4baba0c)
- fix-zeroconf-import-error (739df44)
- fix: move repairs imports to homeassistant.helpers.issue_registry for HA 2026 (3a9d087)
- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- docs: review and analyze HA/HACS guidelines compliance (06bf5d1)
- docs: add My Home Assistant badge for HACS integration (1261b16)
- docs: fix broken internal and external links in GitHub Wiki and update dates (3958807)
- docs: fix broken internal and external links in GitHub Wiki (53bdbec)
- docs: Merge github_wiki_content into docs/wiki (605af30)
- docs: slim README, expand wiki with diagnostics page and HA 2026 notes (55ce11b)
- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix-test-env-setup (48649a0)
- build(tests): Make test environment setup script more robust (8c7bc55)
- I have updated the Home Assistant quality scale to Silver, as the Gold and Platinum requirements are not yet fully met and verified (specifically the 95% test coverage). (c125d8e)
- Simplify CI: Only test Python 3.14 + HA 2026.5.0 (6604006)
- Add GitHub Action testing for HA 2026.5.0 and Python 3.14 (878e93a)
- fix: production bugs, HA 2026.5.0/Python 3.14 compatibility, test suite fixes (4f153f6)
- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-09 09:16:24 UTC_

---

## [1.0.3-beta.4] - 2026-03-08

## v1.0.3-beta.4 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- feat: Add comprehensive disclaimer, icon optimization, and dark mode support (March 2025) (f32b3a1)
- Add GitHub Action testing for HA 2026.5.0 and Python 3.14 (878e93a)
- add-custom-icon (92e25fe)
- feat: add stale, status-check and auto-label PR workflows (4fe0174)
- Add-custom-icon (65b96a7)
- Add VIOLET_144.png as icon.png to root and component dirs (d3141ae)
- feat: add diagnostics support for HA diagnostics download (8e14741)
- feat: add diagnostics support for HA diagnostics download (88527b9)
- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- Document pytest-homeassistant-custom-component update policy (6d65c0b)
- 📝 Release v1.0.3-beta.3 - Update changelog and version files (94eebbd)
- Update logo to match brand (d3a089a)
- Update custom integration brand images structure (e190831)
- 📝 Release v1.0.3-beta.3 - Update changelog and version files (a57b380)
- Update integration logo to official Violet icon (8c23aff)
- 📝 Release v1.0.3-beta.2 - Update changelog and version files (fc7ba31)
- Update FUNDING.yml (499a6d5)
- 📝 Release v1.0.3-beta.1 - Update changelog and version files (1fc2bce)
- 📝 Release v1.0.3-alpha.4 - Update changelog and version files (55a78f6)
- 📝 Release v1.0.3-alpha.3 - Update changelog and version files (de05bf5)
- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- Fix critical zeroconf discovery API compatibility for HA 2026.x (1efc579)
- fix: production bugs, HA 2026.5.0/Python 3.14 compatibility, test suite fixes (4f153f6)
- fix: correct permissions for actions/labeler (afbb57a)
- fix: cleanup auto-label-pr.yml logic (a85edd6)
- fix: prevent command injection and ensure syntax correctness (8e48cd2)
- Fix code formatting in climate.py (fe7ebde)
- fix-zeroconf-discovery-filter (eaa3ed3)
- fix: restrict zeroconf discovery to violet devices (05a94c9)
- fix: make forum login detection robust and fix BBCode URL typo (20216eb)
- Merge branch 'main' into claude/fix-zeroconf-import-error-tplZf (e2f4cd8)
- fix-zeroconf-import-error (4baba0c)
- fix-zeroconf-import-error (739df44)
- fix: move repairs imports to homeassistant.helpers.issue_registry for HA 2026 (3a9d087)
- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- docs: slim README, expand wiki with diagnostics page and HA 2026 notes (55ce11b)
- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- Simplify CI: Only test Python 3.14 + HA 2026.5.0 (6604006)
- Add GitHub Action testing for HA 2026.5.0 and Python 3.14 (878e93a)
- fix: production bugs, HA 2026.5.0/Python 3.14 compatibility, test suite fixes (4f153f6)
- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-beta.4](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-beta.4)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-08 10:42:24 UTC_

---

## [1.0.3-beta.3] - 2026-03-03

## v1.0.3-beta.3 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- Add-custom-icon (65b96a7)
- Add VIOLET_144.png as icon.png to root and component dirs (d3141ae)
- feat: add diagnostics support for HA diagnostics download (8e14741)
- feat: add diagnostics support for HA diagnostics download (88527b9)
- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- Update custom integration brand images structure (e190831)
- 📝 Release v1.0.3-beta.3 - Update changelog and version files (a57b380)
- Update integration logo to official Violet icon (8c23aff)
- 📝 Release v1.0.3-beta.2 - Update changelog and version files (fc7ba31)
- Update FUNDING.yml (499a6d5)
- 📝 Release v1.0.3-beta.1 - Update changelog and version files (1fc2bce)
- 📝 Release v1.0.3-alpha.4 - Update changelog and version files (55a78f6)
- 📝 Release v1.0.3-alpha.3 - Update changelog and version files (de05bf5)
- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- Fix code formatting in climate.py (fe7ebde)
- fix-zeroconf-discovery-filter (eaa3ed3)
- fix: restrict zeroconf discovery to violet devices (05a94c9)
- fix: make forum login detection robust and fix BBCode URL typo (20216eb)
- Merge branch 'main' into claude/fix-zeroconf-import-error-tplZf (e2f4cd8)
- fix-zeroconf-import-error (4baba0c)
- fix-zeroconf-import-error (739df44)
- fix: move repairs imports to homeassistant.helpers.issue_registry for HA 2026 (3a9d087)
- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- docs: slim README, expand wiki with diagnostics page and HA 2026 notes (55ce11b)
- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-beta.3](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-beta.3)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-03 04:51:15 UTC_

---

## [1.0.3-beta.3] - 2026-03-02

## v1.0.3-beta.3 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- feat: add diagnostics support for HA diagnostics download (8e14741)
- feat: add diagnostics support for HA diagnostics download (88527b9)
- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- Update integration logo to official Violet icon (8c23aff)
- 📝 Release v1.0.3-beta.2 - Update changelog and version files (fc7ba31)
- Update FUNDING.yml (499a6d5)
- 📝 Release v1.0.3-beta.1 - Update changelog and version files (1fc2bce)
- 📝 Release v1.0.3-alpha.4 - Update changelog and version files (55a78f6)
- 📝 Release v1.0.3-alpha.3 - Update changelog and version files (de05bf5)
- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- Fix code formatting in climate.py (fe7ebde)
- fix-zeroconf-discovery-filter (eaa3ed3)
- fix: restrict zeroconf discovery to violet devices (05a94c9)
- fix: make forum login detection robust and fix BBCode URL typo (20216eb)
- Merge branch 'main' into claude/fix-zeroconf-import-error-tplZf (e2f4cd8)
- fix-zeroconf-import-error (4baba0c)
- fix-zeroconf-import-error (739df44)
- fix: move repairs imports to homeassistant.helpers.issue_registry for HA 2026 (3a9d087)
- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- docs: slim README, expand wiki with diagnostics page and HA 2026 notes (55ce11b)
- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-beta.3](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-beta.3)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-02 18:40:23 UTC_

---

## [1.0.3-beta.2] - 2026-03-02

## v1.0.3-beta.2 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- feat: add diagnostics support for HA diagnostics download (8e14741)
- feat: add diagnostics support for HA diagnostics download (88527b9)
- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- Update FUNDING.yml (499a6d5)
- 📝 Release v1.0.3-beta.1 - Update changelog and version files (1fc2bce)
- 📝 Release v1.0.3-alpha.4 - Update changelog and version files (55a78f6)
- 📝 Release v1.0.3-alpha.3 - Update changelog and version files (de05bf5)
- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- fix-zeroconf-discovery-filter (eaa3ed3)
- fix: restrict zeroconf discovery to violet devices (05a94c9)
- fix: make forum login detection robust and fix BBCode URL typo (20216eb)
- Merge branch 'main' into claude/fix-zeroconf-import-error-tplZf (e2f4cd8)
- fix-zeroconf-import-error (4baba0c)
- fix-zeroconf-import-error (739df44)
- fix: move repairs imports to homeassistant.helpers.issue_registry for HA 2026 (3a9d087)
- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- docs: slim README, expand wiki with diagnostics page and HA 2026 notes (55ce11b)
- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-beta.2](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-beta.2)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-02 15:48:04 UTC_

---

## [1.0.3-beta.1] - 2026-03-02

## v1.0.3-beta.1 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- feat: add diagnostics support for HA diagnostics download (8e14741)
- feat: add diagnostics support for HA diagnostics download (88527b9)
- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- 📝 Release v1.0.3-alpha.4 - Update changelog and version files (55a78f6)
- 📝 Release v1.0.3-alpha.3 - Update changelog and version files (de05bf5)
- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- fix-zeroconf-import-error (4baba0c)
- fix-zeroconf-import-error (739df44)
- fix: move repairs imports to homeassistant.helpers.issue_registry for HA 2026 (3a9d087)
- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- docs: slim README, expand wiki with diagnostics page and HA 2026 notes (55ce11b)
- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-beta.1](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-beta.1)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-02 06:46:08 UTC_

---

## [1.0.3-alpha.4] - 2026-03-02

## v1.0.3-alpha.4 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features

- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- 📝 Release v1.0.3-alpha.3 - Update changelog and version files (de05bf5)
- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- fix-zeroconf-import-error (739df44)
- fix: move repairs imports to homeassistant.helpers.issue_registry for HA 2026 (3a9d087)
- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-alpha.4](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-alpha.4)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-02 05:14:52 UTC_

---

## [1.0.3-alpha.3] - 2026-03-02

## v1.0.3-alpha.3 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features

- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- 📝 Release v1.0.3-alpha.2 - Update changelog and version files (44d0302)
- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- fix-zeroconf-import-error (512353a)
- fix: replace ZeroconfServiceInfo with AsyncServiceInfo for HA 2026 compatibility (62ac86f)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-alpha.3](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-alpha.3)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-02 05:02:47 UTC_

---

## [1.0.3-alpha.2] - 2026-03-02

## v1.0.3-alpha.2 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features

- add repairs to manifest dependencies (bdfc0cd)
- fix: add repairs to manifest dependencies (e8a4f8a)
- Add missing future annotations to config_flow_utils modules (968c3c5)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- docs: Update README.md to reflect new custom services (f1be61f)
- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- small update for blueprints, dashboards and workflows (38ed640)
- update-readme-services (dac9edf)
- update-wiki-version (77fcc81)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- fix: update test references for VioletClimateEntity (e363dcb)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (2cebf5a)
- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- fix: add repairs to manifest dependencies (e8a4f8a)
- Fix HA coding standards: collections.abc imports and PARALLEL_UPDATES (7d51b91)
- Fix HA coding standards: modernize type hints, add quality_scale.yaml (00ef821)
- fix: update test references for VioletClimateEntity (e363dcb)
- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- update-readme-services (dac9edf)
- docs: Update README.md to reflect new custom services (f1be61f)
- docs: update github wiki to 1.0.3-alpha.1 (43b4c64)
- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- fix: update test references for VioletClimateEntity (e363dcb)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-alpha.2](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-alpha.2)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-03-02 04:29:56 UTC_

---

## [1.0.3-alpha.1] - 2026-02-28

## v1.0.3-alpha.1 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features

- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- 📝 Release v1.0.3-alpha.1 - Update changelog and version files (1c31c4f)
- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- /fix-config-flow-handler (b401866)
- Fix config flow handler not found by adding domain=DOMAIN (9181762)
- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-alpha.1](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-alpha.1)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-28 19:54:21 UTC_

---

## [1.0.3-alpha.1] - 2026-02-28

## v1.0.3-alpha.1 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features

- Add final honest report - Gold Level ~85% complete (3f5f68e)
- Add Quality Scale progress documentation (4710b02)

### 🚀 Improvements

- Update Quality Scale Progress - Bronze Level 100% Complete (c041aad)
- Update Quality Scale progress - Type Hints completed (cc1a922)
- 📝 Release v1.0.2 - Update changelog and version files (c2bb382)

### 🔧 Bug Fixes

- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)

### 📚 Documentation

- Silver Level: Enhanced Error Handling, Diagnostics & Documentation 🥈 (59e947f)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)
- Add Quality Scale progress documentation (4710b02)
- Phase 1: Bronze Level - Code Style & Documentation Improvements (982266d)

### 🧪 Tests

- Fix HA 2026 compatibility and complete Gold Level testing (58fa568)
- Fix ZeroConf Discovery - 100% Tests Passing! ✅ (032d79e)
- Fix Gold Level imports and test issues (8201f6e)
- Bronze & Silver Level: FINAL TEST REPORT - 100% COMPLETE ✅ (dc092ef)
- Silver Level: Complete - Test Suite & Quality Assurance ✅ (d54d7ab)
- Phase 1 Complete: README, Entity Docs & Tests - 100% Bronze Level Achieved (f74118d)

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

📋 [Full changelog: v1.0.2...v1.0.3-alpha.1](https://github.com/Xerolux/violet-hass/compare/v1.0.2...v1.0.3-alpha.1)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-28 18:49:22 UTC_

---

## [1.0.2] - 2026-02-26

## v1.0.2 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

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

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- Update README.md (d8c08bf)
- Update wiki documentation to version 1.0.2-beta.5 (d521c4d)
- docs(wiki): Add German Extended Logging wiki page (d1e0241)
- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Translate Extended Logging documentation to German (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

---

## [1.0.2-beta.6] - 2026-02-25

## v1.0.2-beta.6 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

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

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- Update wiki documentation to version 1.0.2-beta.5 (d521c4d)
- docs(wiki): Add German Extended Logging wiki page (d1e0241)
- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Translate Extended Logging documentation to German (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.6](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.6)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-25 17:24:15 UTC_

---

## [1.0.2-beta.5] - 2026-02-25

## v1.0.2-beta.5 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

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

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- Update wiki documentation to version 1.0.2-beta.5 (d521c4d)
- docs(wiki): Add German Extended Logging wiki page (d1e0241)
- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Translate Extended Logging documentation to German (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.5](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.5)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-25 13:49:04 UTC_

---

## [1.0.2-beta.5] - 2026-02-25

## v1.0.2-beta.5 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

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

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Translate Extended Logging documentation to German (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.5](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.5)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-25 06:52:13 UTC_

---

## [1.0.2-beta.5] - 2026-02-25

## v1.0.2-beta.5 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- Fix diagnostic log export path and add debug hint (4602573)
- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- fix: Add missing force_update option in settings (6ccc232)
- feat: Add diagnostic logging and log export service for troubleshooting (b50dac7)
- Add Force Update option to settings (7927ba0)
- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Translate Extended Logging documentation to German (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.5](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.5)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-25 06:14:17 UTC_

---

## [1.0.2-beta.5] - 2026-02-25

## v1.0.2-beta.5 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- fix: Add missing force_update option in settings (6ccc232)
- feat: Add diagnostic logging and log export service for troubleshooting (b50dac7)
- Add Force Update option to settings (7927ba0)
- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Translate Extended Logging documentation to German (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.5](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.5)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-25 05:58:48 UTC_

---

## [1.0.2-beta.5] - 2026-02-25

## v1.0.2-beta.5 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- fix: Add missing force_update option in settings (6ccc232)
- feat: Add diagnostic logging and log export service for troubleshooting (b50dac7)
- Add Force Update option to settings (7927ba0)
- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Translate Extended Logging documentation to German (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.5](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.5)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-25 05:40:15 UTC_

---

## [1.0.2-beta.4] - 2026-02-24

## v1.0.2-beta.4 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- fix: Add missing force_update option in settings (6ccc232)
- feat: Add diagnostic logging and log export service for troubleshooting (b50dac7)
- Add Force Update option to settings (7927ba0)
- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Translate Extended Logging documentation to German (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.4](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.4)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-24 21:26:11 UTC_

---

## [1.0.2-beta.3] - 2026-02-24

## v1.0.2-beta.3 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- fix: Add missing force_update option in settings (6ccc232)
- feat: Add diagnostic logging and log export service for troubleshooting (b50dac7)
- Add Force Update option to settings (7927ba0)
- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- feat: Increase log export limit to 10,000 lines and update documentation (3c42752)
- docs: Translate Extended Logging documentation to German (48de0fe)
- docs: Add Extended Logging & Diagnostic Tools guide (1bee46a)
- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.3](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.3)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-24 18:47:58 UTC_

---

## [1.0.2-beta.3] - 2026-02-24

## v1.0.2-beta.3 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- feat: Add diagnostic logging and log export service for troubleshooting (b50dac7)
- Add Force Update option to settings (7927ba0)
- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements

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

### 🔧 Bug Fixes

- fix-stuck-sensors-partial-updates (a4055e5)
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

### 📚 Documentation

- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.3](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.3)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-24 17:30:11 UTC_

---

## [1.0.2-beta.2] - 2026-02-24

## v1.0.2-beta.2 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements

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

### 🔧 Bug Fixes

- fix-stuck-sensors-partial-updates (a4055e5)
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

### 📚 Documentation

- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-24 13:37:16 UTC_

---

## [1.0.2-beta.2] - 2026-02-24

## v1.0.2-beta.2 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

---

## [1.0.2-beta.1] - 2026-02-24

## v1.0.2-beta.1 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

---

### ✨ New Features

- fix: add .nojekyll to prevent GitHub Pages Jekyll build failure (e8ba40d)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- Add comprehensive Code Review documentation (18bdf74)

### 🚀 Improvements

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

### 🔧 Bug Fixes

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

### 📚 Documentation

- Merge pull request #203 from Xerolux/claude/setup-wiki-docs-RsE1I (dc50f7e)
- ci: Add workflow to sync docs/wiki/ to GitHub Wiki (5eba541)
- docs(wiki): Fix double-bracket links and update date (d315c7e)
- docs: Komplettes GitHub Wiki mit allen Seiten (880bb0b)
- Cleanup: Remove obsolete reports, archived docs, and debug tools (64d613b)
- Add comprehensive Code Review documentation (18bdf74)
- docs: Add complete wiki documentation (d6188d6)
- docs: Create complete wiki with all features and documentation (4e980f4)
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

📋 [Full changelog: v1.0.1...v1.0.2-beta.1](https://github.com/Xerolux/violet-hass/compare/v1.0.1...v1.0.2-beta.1)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-24 09:46:32 UTC_

---

## [1.0.1] - 2026-02-22

## v1.0.1 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

- Enhanced Violet Pool Controller functionality

### 🚀 Improvements

- Refactor: Clean up repository structure and resolve conflicts (c4821fe)
- 📝 Release v1.0.0 - Update changelog and version files (71bc58a)

### 🔧 Bug Fixes

- Release v1.0.1 - Critical Bug Fixes (fe08725)
- Fix: Multiple critical improvements and bug fixes (642a98e)
- /repo-cleanup-docs-fix-conflicts (251e375)

### 📚 Documentation

- /repo-cleanup-docs-fix-conflicts (251e375)

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

📋 [Full changelog: v1.0.0...v1.0.1](https://github.com/Xerolux/violet-hass/compare/v1.0.0...v1.0.1)

---

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

_Generated automatically by GitHub Actions on 2026-02-22 13:42:20 UTC_

---

## [1.0.1] - 2026-02-22

## v1.0.1 – Violet Pool Controller

✅ **CRITICAL BUG FIXES RELEASE**

This release fixes critical issues with sensor display, configuration updates, and session management. All users are strongly recommended to update!

---

### 🐛 Bug Fixes

#### Critical Fixes

- **Contact Sensor State Class Issue**:
  - Fixed sensors returning string values ('RELEASED'/'TRIGGERED') with numeric state_class
  - Added runtime override in `VioletSensor.state_class` property
  - Added pattern matching for all sensors containing 'contact'
  - Added explicit keys: CLOSE_CONTACT, OPEN_CONTACT, ERROR_CONTACT
  - **Impact**: Fixes ValueError for all contact sensors

- **Session Management - CRITICAL FIX**:
  - Fixed aiohttp session being closed by integration (managed by HA)
  - Removed all `await api._session.close()` calls
  - Sessions now properly managed by Home Assistant lifecycle
  - **Impact**: Prevents warnings and potential connection issues

- **API Configuration Update Issues**:
  - Fixed AttributeError when accessing API internal attributes
  - Changed from attribute manipulation to creating new API instances
  - Fixed accessing private attributes (_timeout, _max_retries, _auth)
  - **Impact**: Dynamic configuration now works correctly

#### Sensor Display Fixes

- **Timestamp Display Issues**:
  - Fixed timestamps displayed as large numbers instead of dates
  - Added millisecond handling (timestamps > 10000000000)
  - Added suffix-based timestamp detection (_LAST_AUTO_RUN, etc.)
  - All timestamp sensors now show proper datetime format
  - **Impact**: "Backwash Last Auto Run" now shows date instead of raw number

- **Freezecount Unit Problem**:
  - Fixed freezecount/faultcount sensors incorrectly treated as temperatures
  - Excluded from temperature device class and state_class
  - No unit assigned for counter sensors
  - **Impact**: Fixes recorder warnings and unit conversion errors

- **Rounding Consistency**:
  - All numeric values now rounded consistently:
    - pH, ORP, Chlorine: 2 decimal places
    - Temperatures: 2 decimal places (changed from 1)
    - Analog sensors (ADC, IMP): 2 decimal places
    - Percentages: 1 decimal place
    - Others: 2 decimal places
  - **Impact**: Better readability and consistent formatting

#### Configuration & Translation Fixes

- **Retries TypeError**:
  - Fixed 'float' object cannot be interpreted as an integer in range()
  - Updated `fetch_api_data()` to accept int | float for retries parameter
  - Added int(retries) conversion before range() calls
  - **Impact**: Config flow now handles retry values correctly

- **German Translation Placeholders**:
  - Fixed validation errors: docs_de → docs_en in de.json
  - All translation placeholders now match English version
  - **Impact**: Fixes translation validation warnings

- **Dynamic Configuration Updates**:
  - Added async_update_listener for instant config application
  - ALL settings now update immediately without reload/restart
  - Polling interval, timeout, retries, connection settings - all instant!
  - **Impact**: No more restart needed for config changes

- **Connection Settings in Reconfigure**:
  - Added username/password fields to reconfigure step
  - All connection settings now editable via UI
  - **Impact**: Users can now update credentials without full reconfiguration

### 🚀 Improvements

- **Dynamic Configuration**:
  - Settings changes now take effect immediately
  - No Home Assistant restart required
  - No integration reload required
  - Better user experience

- **Enhanced Error Handling**:
  - Better logging for configuration updates
  - Clear error messages for invalid states
  - Improved debug information

### 📝 Documentation

- Updated CHANGELOG with comprehensive v1.0.1 fixes
- All fixes documented with impact analysis
- Clear upgrade instructions

### ⚠️ Breaking Changes

**None** - This is a bug fix release, fully backward compatible

### 📦 Installation

**HACS (Recommended):**
1. Check for updates in HACS
2. Click "Update" for Violet Pool Controller
3. Restart Home Assistant

**Manual:**
1. Download latest `violet_pool_controller.zip`
2. Extract to `custom_components/violet_pool_controller`
3. Restart Home Assistant

---

## [1.0.0] - 2026-02-06

## v1.0.0 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features

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
- 🐛 Fix: Schema validation for feature selection (dict comprehension) (dda5028)
- 🐛 Fix: Config flow feature selection and placeholders (e29ae93)
- ✨ Feature: Multi-controller support with auto ranges (ff3f7fc)
- ✨ Feature: Auto-recovery + enhanced input sanitization (bb07c09)
- ✨ Add explicit pre-release support to workflow (96a4bc9)

### 🚀 Improvements

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
- 🔧 Refactor: Harmonization and code optimization (a9302b2)
- 📝 Update version to v0.2.0-beta.3 and release notes (31e18d7)
- 📝 Update version to v0.2.0-beta.2 and release notes (0713c62)
- 🔧 Refactor: Modular code structure + security improvements (3946e22)
- 📝 Update version to v0.2.0-beta.1 and release notes (814cd1c)
- Update README.md (8f43330)
- Update README.md (3630abb)
- 📝 Update version to v0.2.0 and release notes (4887b5b)

### 🔧 Bug Fixes

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
- 🐛 Fix: Schema validation for feature selection (dict comprehension) (dda5028)
- Merge pull request #126 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (0bbb990)
- 🐛 Fix: Config flow feature selection and placeholders (e29ae93)
- Merge pull request #125 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (c7977ef)
- 🐛 Fix: Config flow step ID error welcome (3652e8d)
- Merge pull request #124 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (d5193b9)
- 🐛 Fix: ConfigEntryNotReady exception handling during setup (8421498)
- 🐛 Fix: Options flow + dynamic device info for multi-controller (fd91013)

### 📚 Documentation

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

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you!


---

## [1.0.0] - 2026-02-06

## v1.0.0 – Violet Pool Controller

**STABLE RELEASE** - Production-ready with extensive testing on live hardware!

---

### Highlights

The first stable release of the completely rewritten Violet Pool Controller integration.
Tested on real controller hardware with HA 2026.

---

### Critical Bug Fixes

- **API Query Parameter Fix**: `getReadings` endpoint used incorrect `params={"ALL": ""}` instead of correct `query="ALL"` - **this was the cause of missing sensor data**
- **Firmware Extraction**: Firmware version is now correctly extracted from the API response
- **Switch State Handling**: Empty strings (`""`) are no longer interpreted as `True`
- **Composite State Parsing**: Pipe-separated states like `"2|BLOCKED_BY_OUTSIDE_TEMP"` are now correctly resolved
- **Empty State Arrays**: `SOLARSTATE = "[]"` is recognized as a missing value with fallback to base state
- **Status Sensor Localization**: All status sensors now show localized descriptions instead of English text

### New Features

- **Localized Status Descriptions**: Switches show detailed state information in `extra_state_attributes` (mode, speed, runtime)
- **Pump Details**: Active speed level (0-3) is automatically detected and displayed
- **Heater Details**: Target temperature and overrun time visible in attributes
- **Solar Details**: Target temperature available as attribute
- **Dosing Details**: Status, range, daily amount and canister volume as attributes
- **Backwash Details**: Backwash step and info as attributes
- **Dashboard Template**: `Dashboard/pool_control_status.yaml` with `secondaryinfo-entity-row` for status display directly under switches
- **Circuit Breaker Pattern**: Automatic protection against API failures with retry and recovery

### Improvements

- **Startup Performance**: Removed 3-second sleep at startup - integration starts immediately
- **Simplified Data Fetching**: Always full refresh instead of complex partial/full logic
- **Composite State Sensors**: PUMPSTATE, HEATERSTATE, SOLARSTATE correctly available as sensors
- **Dosing State Sensors**: DOS_*_STATE arrays are correctly parsed and displayed
- **API Rate Limiting**: Token bucket algorithm protects the controller from overload
- **Auto-Recovery**: Exponential backoff (10s-300s) on connection loss
- **Input Sanitization**: Protection against XSS, SQL injection and command injection
- **SSL/TLS Security**: Certificate verification enabled by default
- **HA 2026 Compatibility**: Tested with Home Assistant 2025.12.0+

### Dashboard

- New `pool_control_status.yaml` with two variants:
  - **Variant 1**: With `custom:secondaryinfo-entity-row` (HACS) - status directly under switches
  - **Variant 2**: Without custom card - status as separate rows

---

### Previous Alpha Changes (included in this release)

## [1.0.7-alpha.3] - 2026-02-06

## v1.0.7-alpha.3 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features

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
- 🐛 Fix: Schema validation for feature selection (dict comprehension) (dda5028)
- 🐛 Fix: Config flow feature selection and placeholders (e29ae93)
- ✨ Feature: Multi-controller support with auto ranges (ff3f7fc)
- ✨ Feature: Auto-recovery + enhanced input sanitization (bb07c09)
- ✨ Add explicit pre-release support to workflow (96a4bc9)

### 🚀 Improvements

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
- 🔧 Refactor: Harmonization and code optimization (a9302b2)
- 📝 Update version to v0.2.0-beta.3 and release notes (31e18d7)
- 📝 Update version to v0.2.0-beta.2 and release notes (0713c62)
- 🔧 Refactor: Modular code structure + security improvements (3946e22)
- 📝 Update version to v0.2.0-beta.1 and release notes (814cd1c)
- Update README.md (8f43330)
- Update README.md (3630abb)
- 📝 Update version to v0.2.0 and release notes (4887b5b)

### 🔧 Bug Fixes

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
- 🐛 Fix: Schema validation for feature selection (dict comprehension) (dda5028)
- Merge pull request #126 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (0bbb990)
- 🐛 Fix: Config flow feature selection and placeholders (e29ae93)
- Merge pull request #125 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (c7977ef)
- 🐛 Fix: Config flow step ID error welcome (3652e8d)
- Merge pull request #124 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (d5193b9)
- 🐛 Fix: ConfigEntryNotReady exception handling during setup (8421498)
- 🐛 Fix: Options flow + dynamic device info for multi-controller (fd91013)

### 📚 Documentation

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

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

### 📊 New Diagnostic Sensors

- **API Request Rate Sensor**:
  - Shows API calls per minute (`api_request_rate`)
  - Unit: `req/min`
  - Helps identify excessive polling

- **Average Latency Sensor**:
  - Shows average connection latency (`average_latency`)
  - Unit: `ms`
  - Rolling average of the last 60 requests
  - Helps analyze performance trends

- **Recovery Success Rate Sensor**:
  - Shows auto-recovery success rate (`recovery_success_rate`)
  - Unit: `%`
  - Helps evaluate connection stability

### 🔧 Improvements

- **Extended Diagnostic Tracking**:
  - API request counter for rate calculation
  - Latency history (rolling window, 60 samples)
  - Recovery statistics (success/failure count)
  - All metrics implemented thread-safely

### 🌐 Translations

- New sensor translations in German and English
- `api_request_rate` → "API Request Rate"
- `average_latency` → "Average Latency"
- `recovery_success_rate` → "Recovery Success Rate"

### 📚 Documentation

- `FUTURE_IMPROVEMENTS.md` created with:
  - Detailed roadmap for future improvements
  - Priority matrix (10 items identified)
  - Safe refactoring guide for config flow
  - Security checklists

### 🔍 Code Quality

- ✅ All ruff checks passed
- ✅ No breaking changes
- ✅ Backward compatible
- ✅ Thread safety guaranteed

---

## [1.0.7-alpha.3] - 2026-02-01

### 🔒 Security Fixes

- **SSL/TLS Certificate Verification**: Added configurable SSL certificate verification with `verify_ssl` parameter
  - Default: Enabled (secure by default)
  - Warning message when disabled for security awareness
  - Proper SSL context handling with certificate validation
- **Improved Timeout Configuration**: Enhanced timeout handling with granular connection timeouts
  - Total timeout: User configurable (default 10s)
  - Connection timeout: 80% of total timeout
  - Socket connection timeout: 80% of total timeout
- **Enhanced Input Sanitization**: Updated API methods to use comprehensive input sanitization

### 🏗️ Refactoring

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

### 🧵 Thread Safety

- **Lock Ordering Documentation**: Added comprehensive thread safety documentation
  - Documented lock acquisition order to prevent deadlocks
  - `_api_lock`: Protects API calls and data updates
  - `_recovery_lock`: Protects recovery state and attempts
  - Clear warnings about nested locking and proper patterns
- **Recovery Logic Safety**: Enhanced recovery task with proper lock handling

### 🔧 Compatibility

- **Home Assistant 2026.1 Ready**:
  - Updated `manifest.json`: minimum HA version `2025.12.0`
  - Updated `requirements.txt`: `homeassistant>=2025.12.0`
  - Updated `aiohttp` dependency to `>=3.10.0`
- **Backward Compatibility**: Maintained support for older HA versions through minimum version declaration

### 🚀 Performance | Performance

- **Optimized State Management**: Enhanced device.py state handling with better tracking
- **Improved SSL Context Caching**: SSL contexts created only when needed, reducing overhead
- **Better Timeout Granularity**: Prevents hanging connections with proper timeout hierarchy

### 📝 Documentation

- **Thread Safety Guide**: Added detailed lock ordering documentation in device.py
- **Security Warnings**: Added user-facing warnings for insecure SSL configurations
- **Code Comments**: Enhanced inline documentation for security-critical sections

---

## [1.0.7-alpha.2] - 2026-01-04

## v1.0.7-alpha.2 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

---

### ✨ New Features

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
- 🐛 Fix: Schema validation for feature selection (dict comprehension) (dda5028)
- 🐛 Fix: Config flow feature selection and placeholders (e29ae93)
- ✨ Feature: Multi-controller support with auto ranges (ff3f7fc)
- ✨ Feature: Auto-recovery + enhanced input sanitization (bb07c09)
- ✨ Add explicit pre-release support to workflow (96a4bc9)

### 🚀 Improvements

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
- 🔧 Refactor: Harmonization and code optimization (a9302b2)
- 📝 Update version to v0.2.0-beta.3 and release notes (31e18d7)
- 📝 Update version to v0.2.0-beta.2 and release notes (0713c62)
- 🔧 Refactor: Modular code structure + security improvements (3946e22)
- 📝 Update version to v0.2.0-beta.1 and release notes (814cd1c)
- Update README.md (8f43330)
- Update README.md (3630abb)
- 📝 Update version to v0.2.0 and release notes (4887b5b)

### 🔧 Bug Fixes

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
- 🐛 Fix: Schema validation for feature selection (dict comprehension) (dda5028)
- Merge pull request #126 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (0bbb990)
- 🐛 Fix: Config flow feature selection and placeholders (e29ae93)
- Merge pull request #125 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (c7977ef)
- 🐛 Fix: Config flow step ID error welcome (3652e8d)
- Merge pull request #124 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (d5193b9)
- 🐛 Fix: ConfigEntryNotReady exception handling during setup (8421498)
- 🐛 Fix: Options flow + dynamic device info for multi-controller (fd91013)

### 📚 Documentation

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

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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

### ✨ New Features

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
- 🐛 Fix: Schema validation for feature selection (dict comprehension) (dda5028)
- 🐛 Fix: Config flow feature selection and placeholders (e29ae93)
- ✨ Feature: Multi-controller support with auto ranges (ff3f7fc)
- ✨ Feature: Auto-recovery + enhanced input sanitization (bb07c09)
- ✨ Add explicit pre-release support to workflow (96a4bc9)

### 🚀 Improvements

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
- 🔧 Refactor: Harmonization and code optimization (a9302b2)
- 📝 Update version to v0.2.0-beta.3 and release notes (31e18d7)
- 📝 Update version to v0.2.0-beta.2 and release notes (0713c62)
- 🔧 Refactor: Modular code structure + security improvements (3946e22)
- 📝 Update version to v0.2.0-beta.1 and release notes (814cd1c)
- Update README.md (8f43330)
- Update README.md (3630abb)
- 📝 Update version to v0.2.0 and release notes (4887b5b)

### 🔧 Bug Fixes

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
- 🐛 Fix: Schema validation for feature selection (dict comprehension) (dda5028)
- Merge pull request #126 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (0bbb990)
- 🐛 Fix: Config flow feature selection and placeholders (e29ae93)
- Merge pull request #125 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (c7977ef)
- 🐛 Fix: Config flow step ID error welcome (3652e8d)
- Merge pull request #124 from Xerolux/claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk (d5193b9)
- 🐛 Fix: ConfigEntryNotReady exception handling during setup (8421498)
- 🐛 Fix: Options flow + dynamic device info for multi-controller (fd91013)

### 📚 Documentation

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

### ❤️ Support

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏


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
