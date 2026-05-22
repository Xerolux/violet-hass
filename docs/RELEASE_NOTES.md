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
