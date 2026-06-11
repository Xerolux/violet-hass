## v1.2.4-beta.1 – Violet Pool Controller

🧪 **BETA RELEASE**

### 🐛 Critical Fixes | Kritische Fixes

**Dosing / Dosierung (Flockung, Chlor, pH±):**
- Manual dosing via switch entities now sends an explicit runtime (30s default) —
  `POST /triggerManualDosing` requires one, `runtime=0` silently did nothing.
  This fixes dosing switches appearing "read-only" (flipping back after a few seconds).
  | Manuelle Dosierung über Switch-Entities sendet jetzt eine explizite Laufzeit
  (Standard 30s) — vorher sprang der Schalter nach wenigen Sekunden zurück.
- Requires API package **v0.0.27**: `AUTO` on a dosing channel no longer *starts*
  a dosing run (now maps to stop/auto, verified on real hardware FW 1.1.9).
  | Benötigt API-Paket **v0.0.27**: `AUTO` startet keine Dosierung mehr.
- `manual_dosing(type, 0)` now stops a running dosing instead of sending a
  zero-second start. | stoppt jetzt statt eines 0-Sekunden-Starts.

**Live-verified | Live verifiziert:** DOSSTART/DOSSTOP, AUTO→Stop mapping, output
index mapping and auth tested against a real controller (FW 1.1.9).

### 🚀 Improvements | Verbesserungen

- API package is now developed in this monorepo (`violet_poolcontroller_api/`) and
  released to PyPI via `api-v*` tags | API-Paket wird jetzt im Monorepo entwickelt
- 4xx errors fail fast and bypass the circuit breaker (wrong credentials show the
  real HTTP error) | 4xx-Fehler schlagen sofort fehl statt den Circuit Breaker zu öffnen
- Configurable state display language (`set_state_translation_language`)
- CI: repaired tox packaging, API format/type checks, version sync workflow;
  CodeQL now also scans the API package | CI repariert und erweitert
- Docs: README/Wiki now cover the Python API package | Doku um API-Paket ergänzt

### ❤️ Support | Unterstützung

- 💳 **[PayPal](https://paypal.me/xerolux)**
- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- ⭐ **[Star this repository](https://github.com/Xerolux/violet-hass)**

---

## v1.2.3 – Violet Pool Controller

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

- Add comprehensive RUNTIME sensor definitions for all modules (c8f9593)
- Add missing RUNTIME sensor definitions (9838671)
- Add missing sensor definitions for BACKWASHRINSE (a325492)

### 🚀 Improvements | Verbesserungen

- Performance improvements and code optimizations

### 🔧 Bug Fixes | Fehlerbehebungen

- Fix state-class (21c3007)

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

📋 [Full changelog: v1.2.2...v1.2.3](https://github.com/Xerolux/violet-hass/compare/v1.2.2...v1.2.3)

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

_Generated automatically by GitHub Actions on 2026-06-04 10:12:49 UTC_
