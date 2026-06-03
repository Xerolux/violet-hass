## v1.2.1 – Violet Pool Controller

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

- docs: add copy-paste AI prompt to restore API constants in the api package (572bf76)
- test: add missing aiohttp_client mock attrs for phacc compatibility (029d772)
- docs: add API package contract to prevent recurrence of missing-constant breakage (48c4a8d)
- fix: add COVER_FUNCTIONS/DEVICE_PARAMETERS and fix temperature validation (b18ecf1)
- fix: add type annotations to resolve mypy errors (49414b8)
- fix: add basic pytest fixtures for Home Assistant mocks (41e053b)
- fix: add missing constants and mock classes for Home Assistant (9bcf653)
- fix: add device_id field translations to services (672ac81)

### 🚀 Improvements | Verbesserungen

- refactor: DRY up temperature limit logic and clarify constant usage (9c0a4ad)
- refactor: use instance-level temperature limits for better extensibility (2506bea)
- refactor: load setpoint field names dynamically from SETPOINT_DEFINITIONS (2e2003a)
- fix: enhance MockRateLimiter and MockVioletPoolAPI methods (94b477c)
- fix: enhance Home Assistant mocks with additional modules and classes (b31a808)
- fix: improve test infrastructure mocking for HA and external API compatibility (a72f76d)

### 🔧 Bug Fixes | Fehlerbehebungen

- fix(switch): dosing channels with _USE=0 now correctly show as OFF (9e620b0)
- fix: restore COVER_STATE_MAP, pin API dep, remove junk file (6f7601d)
- temperature-bug (0042686)
- fix: use getattr with fallback for temperature limit attributes (2f0d4ce)
- fix: add COVER_FUNCTIONS/DEVICE_PARAMETERS and fix temperature validation (b18ecf1)
- fix: restore COVER_FUNCTIONS/DEVICE_PARAMETERS and bump to v1.2.1 (6670912)
- violet-temp-display-bug (6e52f65)
- fix: resolve test failures and attribute issues (c03612e)
- fix: climate entity reads target temperature from multiple field names (6dedfd4)
- fix: remove unused variable assignments in mock _request method (fb6de89)
- fix: enhance MockRateLimiter and MockVioletPoolAPI methods (94b477c)
- fix: add type annotations to resolve mypy errors (49414b8)
- fix: add basic pytest fixtures for Home Assistant mocks (41e053b)
- fix: resolve CodeQL warnings about unused imports and variables (d646d79)
- fix: complete Home Assistant mocks for test collection (5a71b16)
- fix: add missing constants and mock classes for Home Assistant (9bcf653)
- fix: enhance Home Assistant mocks with additional modules and classes (b31a808)
- fix: pass globals() to exec() for proper Home Assistant mock initialization (2796687)
- fix: resolve CodeQL security issues (81d3ba0)
- fix: improve test infrastructure mocking for HA and external API compatibility (a72f76d)
- fix: extend mock API to support security tests (17d60b6)
- fix: conftest.py - implement set_all_dmx_scenes with error handling in mock API (424a030)
- fix: test_cover.py - remove async decorator from non-async tests (5062680)
- fix: interpret_state_as_bool - correct STATE_MAP values per device specs (feeefcc)
- fix: add device_id field translations to services (672ac81)
- fix: resolve pytest-asyncio version conflict (61fb250)
- fix: use device selector in fields instead of target (326caa6)
- fix: remove device filter from services (use device selector instead) (bb93913)
- fix: use PEP 440 compliant version format (2941f42)
- fix: resolve aiohttp version conflict with Home Assistant 2026.5.x (9bdd309)

### 📚 Documentation | Dokumentation

- docs: add copy-paste AI prompt to restore API constants in the api package (572bf76)
- docs: add API package contract to prevent recurrence of missing-constant breakage (48c4a8d)

### 🧪 Tests

- test: add missing aiohttp_client mock attrs for phacc compatibility (029d772)
- fix: resolve test failures and attribute issues (c03612e)
- fix: complete Home Assistant mocks for test collection (5a71b16)
- fix: improve test infrastructure mocking for HA and external API compatibility (a72f76d)
- fix: extend mock API to support security tests (17d60b6)
- fix: test_cover.py - remove async decorator from non-async tests (5062680)

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

📋 [Full changelog: v1.2.0...v1.2.1](https://github.com/Xerolux/violet-hass/compare/v1.2.0...v1.2.1)

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

_Generated automatically by GitHub Actions on 2026-06-03 21:40:07 UTC_
