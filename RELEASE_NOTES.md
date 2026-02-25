## v1.0.2 – Violet Pool Controller

**Patch Release** — no breaking changes, no new features.

---

### Highlights

Code quality improvements and repository housekeeping. The integration behaviour is unchanged from v1.0.0.

---

### Improvements | Verbesserungen

- **Code Simplification**: Refactored integration code for improved clarity, consistency and long-term maintainability
- **Repository Cleanup**: Removed development/debug artifacts (test scripts, ad-hoc reports) from the repository root
- **`.gitignore` Updated**: Added patterns to prevent future debug artifacts from being accidentally committed

---

### Documentation | Dokumentation

- **SECURITY.md**: Comprehensive security policy — GitHub Private Security Advisories, response timeline, security design summary
- **LICENSE**: Copyright year updated to 2024–2026
- **README**: Minimum HA version corrected to 2025.12.0+

---

### Technische Details

- **Minimum HA Version**: 2025.12.0
- **Python**: 3.12+
- **Dependencies**: aiohttp >= 3.10.0

---

### 📦 Installation

**HACS (Recommended):**
1. Add custom repository: `Xerolux/violet-hass`
2. Search for "Violet Pool Controller"
3. Click Install / Update

**Manual:**
1. Download `violet_pool_controller.zip` from the release assets
2. Extract to `custom_components/violet_pool_controller`
3. Restart Home Assistant

---

📋 [Full changelog: v1.0.0...v1.0.2](https://github.com/Xerolux/violet-hass/compare/v1.0.0...v1.0.2)

---

### ❤️ Support | Unterstützung

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏

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
