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
