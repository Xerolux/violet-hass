## v1.2.4-beta.1 – Violet Pool Controller

🟡 **BETA RELEASE** - Testing phase, may contain bugs

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

- chore: add local API editable install to dev requirements (997bb6c)
- feat: monorepo migration - integrate violet-poolController-api (9a5771e)
- Add 'violet_poolcontroller_api/' from commit '97f11a9ebad53aea478ffa85f297bbff51b90092' (04ec462)
- Add disclaimer regarding project affiliation and risks (783d760)
- fix: add conftest.py to patch aioresponses compatibility with aiohttp 3.13+ (7ad03d0)
- Add version consistency CI, HA dev early warning workflow, and robust composite state parser (ec148bf)
- new-sessio (df9cb4c)
- feat: add mock server, smoke tests, and AGENTS.md (c4944d9)
- feat: add get_log/get_notifications, dosage enable/switch, fix setpoint keys, add HA addon reference (0f525fa)
- ci: add auto dev pre-release workflow (0a3ac30)
- feat: v0.0.18 - error codes, response parsing, dosing tests, live-verified, API reference (eb9b7e6)
- feat: implement get_hardware_profile() and EXT module filtering (401f379)
- docs: add i18n language selector with DE translations, fix ruff config (7ec861e)
- chore: bump version to 0.0.13 and add release notes (87301b9)
- fix-feature-toggle (32464cb)
- feature/hardware-auto-detect (57f66d0)
- feat: filter readings based on hardware profile (20659aa)
- feat: add hardware profile detection (ec6b63c)
- fix(github): Add environment claim to trusted PyPI publishing workflow (73746c2)
- feat: create v0.0.9 release and publish to PyPI (9876c99)
- feat: auto-detect standalone dosing setup from getReadings response (ac90bfb)
- fix: add missing os import in release workflow (8c7c358)
- docs: update readme, wiki and changelog for v0.0.7\n\n- Add RELEASE_NOTES_v0.0.7.md with changelog and explanations.\n- Update README.md to explain transparent Standalone payload parsing.\n- Add Standalone description to docs/Fetching-Data.md. (5fabda6)
- feat: add standalone getReadings parser and bump version to 0.0.7\n\n- Add support for flattening standalone `getReadings` list payload.\n- Bump package version to 0.0.7 in pyproject.toml and setup.py.\n- Fix Node 20 deprecation warnings in GH Actions. (6193cea)
- feat: add standalone getReadings parser and bump version to 0.0.7\n\n- Add support for flattening standalone `getReadings` list payload.\n- Bump package version to 0.0.7 in pyproject.toml and setup.py.\n- Fix Node 20 deprecation warnings in GH Actions. (e8577ff)
- Add files via upload (38e245c)
- add dosing standalone mode without base module (061b9a7)
- Add files via upload (7e491d5)
- ci: add interactive release workflow with auto-version bump (c9dc69e)
- fix: add missing DOS_2_ELO entry to DEVICE_PARAMETERS (c764d72)
- chore(ci): add tox matrix and improve API maintainability/tests (f464ef8)
- add-release-notes-v0.0.2 (dc9df41)
- docs: add release notes for v0.0.2 (05dad29)
- feat: Add workflow_dispatch to update-wiki workflow (971ec33)
- add-wiki (6de5975)
- Merge branch 'main' into docs/add-wiki-5551993568176912030 (e5cb3bc)
- docs: add custom bash workflow for wiki sync (0f76c7a)
- docs/add-wiki (c8eb047)
- add-agpl-license-header (59157b9)
- docs: move WIKI to docs/ and add auto-update workflow (51a109d)
- Add AGPL license header to all Python files (95437c6)
- Modify setup.py with new author email and license (6c7fe6e)
- Add unit tests for VioletPoolAPI (393083f)
- Add funding information to FUNDING.yml (5cf9959)
- Docs: Add 'Use at your own risk' warning (c35039d)
- Docs: Add Violet Pool Controller info and disclaimer (b42cb85)
- Docs: Add LICENSE, SECURITY.md, and CODE_OF_CONDUCT.md (6e4e993)
- Add funding information for Xerolux (4dd3d6f)
- Docs: Add PyPI badges and sponsor buttons to README (b3d034b)
- Add GitHub Actions workflow for Python package publishing (97cba55)

### 🚀 Improvements | Verbesserungen

- Update README.md (0c4969e)
- Improve icons for extension, OMNI DC, and digital input rule entities (b4557d3)
- fix: replace _api_request with _request, improve extension key filter, clean up SSL handling, optimize rate limiter stats (406bd5b)
- docs: update broken HACS download URLs (09aa3cd)
- docs: update broken HACS download URLs (8b2fe25)
- chore(deps-dev): update pytest-homeassistant-custom-component requirement (164db79)
- chore(deps-dev): update ruff requirement from >=0.15.15 to >=0.15.16 (d8ab0f3)
- chore(deps): update aiohttp requirement from >=3.13.5 to >=3.14.1 (7fd6ae8)
- chore(deps-dev): update pytest-asyncio requirement (dc9439a)
- fix: update test for form-encoded set_config, fix dev-release workflow if-condition (2937f5f)
- chore: bump to v0.0.15 – update deps, fix read/write reliability (e64e8fc)
- Update pyproject.toml (189a9cb)
- Update setup.py (3f5f98c)
- docs: update documentation and fix wiki-sync (2486695)
- Update release.yml (4049429)
- optimize-api (7f8e42f)
- refactor: optimize api components (5ae51ea)
- fix: Update GitHub Pages action versions to correct stable versions (b457b5b)
- docs: update readme, wiki and changelog for v0.0.7\n\n- Add RELEASE_NOTES_v0.0.7.md with changelog and explanations.\n- Update README.md to explain transparent Standalone payload parsing.\n- Add Standalone description to docs/Fetching-Data.md. (5fabda6)
- refactor: apply minor API and type optimizations (77ffc1b)
- chore(ci): add tox matrix and improve API maintainability/tests (f464ef8)
- Update setup.py (81fce62)
- ci: Update wiki sync workflow to use GITHUB_TOKEN instead of PAT (a099423)
- update-wiki-workflow-dispatch (5a59534)
- docs: Update README to reflect AGPLv3 license (670b518)
- feat: Add workflow_dispatch to update-wiki workflow (971ec33)
- docs: move WIKI to docs/ and add auto-update workflow (51a109d)
- Update LICENSE (bcbce4f)
- Update license information in pyproject.toml (3a0d9a8)
- Update setup.py (1d4d5e8)
- Update pyproject.toml (8e7a07c)
- Update license badge style in README.md (53c1ff6)
- Update license badge in README.md (e70b278)
- Update setup.py (cdfece0)
- update-package-structure (b9bc261)
- Merge branch 'main' into jules-update-package-structure-7244243960802970025 (0a91ca5)
- Update project version to 0.0.1 (fedd0d8)
- Update README.md (819b228)
- update-package-structure (8abd094)
- Refactor: Restructure package and rename to violet-poolController-api (9d94b66)

### 🔧 Bug Fixes | Fehlerbehebungen

- fix(ci): API GitHub releases must never be marked as latest (8dae83d)
- fix(api): resolve mypy errors in api.py (9559df3)
- fix(dosing): manual dosing runs need an explicit runtime (6ee44ea)
- fix: repair CI pipeline and prepare API v0.0.27 release (eb46340)
- fix(api): spec conformance - PR #41 from violet-poolController-api (6b6e1fa)
- fix: resolve CodeQL unused-import alerts via assignment re-exports (c505ef7)
- fix: address review findings (UpdateFailed re-raise, explicit re-exports) (799b0f2)
- fix: correct device state mapping, controller mismatches, and broken test/CI setup (5fcb4d4)
- fix: format conftest.py to pass ruff import sorting (c7c91b0)
- fix: add conftest.py to patch aioresponses compatibility with aiohttp 3.13+ (7ad03d0)
- fix: pin aiohttp to versions compatible with aioresponses 0.7.8 (32829c3)
- fix: use available aioresponses version 0.7.8 (f38e230)
- fix: correct pyproject.toml configuration and bump version to 0.0.26 (79a71df)
- fix: replace _api_request with _request, improve extension key filter, clean up SSL handling, optimize rate limiter stats (406bd5b)
- Fix cover state mapping, number race condition, switch rules, setpoint ranges, ECO mode, and number display mode (39bf34f)
- Fix dosing switch: use /triggerManualDosing for both start and stop (c814232)
- Fix duplicate dev suffix in dev release tag (090a243)
- Fix dosing switch OFF: send AUTO instead of Manual OFF (5b0d1c1)
- Fix pyproject.toml configuration and COVER_FUNCTIONS type annotation (af68d1d)
- feat: add get_log/get_notifications, dosage enable/switch, fix setpoint keys, add HA addon reference (0f525fa)
- fix: write methods use form-encoded POST /setConfig, correct SOLAR/HEATER keys, bump v0.0.23 (cbf3685)
- fix: set_all_dmx_scenes — one request instead of 12 (919fba8)
- fix: replace /setTargetValues and /setDosingParameters with POST /setConfig (1c602ff)
- fix: resolve merge conflict, keep correct ruff/mypy target versions (5dcdcb6)
- chore: bump version to 0.0.20, fix ruff/mypy target versions (92e6b7c)
- fix: update test for form-encoded set_config, fix dev-release workflow if-condition (2937f5f)
- fix: send setConfig as form-encoded instead of JSON (620d8c1)
- fix: correct ruff/mypy version fields, bump to 0.0.19 (8460099)
- fix: correct output state code mappings per official getReadings spec (fa5a854)
- fix: use /triggerManualDosing for dosing pumps instead of /setFunctionManually (b09a6a3)
- docs: add i18n language selector with DE translations, fix ruff config (7ec861e)
- chore: bump to v0.0.15 – update deps, fix read/write reliability (e64e8fc)
- fix-feature-toggle (32464cb)
- fix: detect EXT module as alive when alive_count key is present but zero (489fbf6)
- fix: hardware profile detection no longer reports phantom EXT2 modules (v0.0.12) (391988c)
- fix: restore setup.py required by release workflow (bb69a96)
- fix: resolve 5 remaining bugs across rate limiter, circuit breaker, and API (2b099f1)
- fix: clean up import order, deduplicate hardware detection, export public API (0bc2f93)
- fix-wiki-sync-exclude-git (f90ea09)
- docs: update documentation and fix wiki-sync (2486695)
- fix(github): Add environment claim to trusted PyPI publishing workflow (73746c2)
- fix-auto-detect-dosing-standalone (628364e)
- Merge branch 'main' into fix-auto-detect-dosing-standalone-6258129374762791943 (d53a9e0)
- fix: resolve PyPI publishing OIDC permission issue (761ae52)
- fix-auto-detect-dosing-standalone (ff0ea5c)
- fix-auto-detect-dosing-standalone (be299ad)
- fix-pages-and-release- (ad432c1)
- fix: add missing os import in release workflow (8c7c358)
- fix-pages-and-release (46c43ff)
- fix: Update GitHub Pages action versions to correct stable versions (b457b5b)
- /jules-fix-pages-and-release (fae65eb)
- chore: fix github pages node warnings and tag release v0.0.7 (0a3708b)
- feat: add standalone getReadings parser and bump version to 0.0.7\n\n- Add support for flattening standalone `getReadings` list payload.\n- Bump package version to 0.0.7 in pyproject.toml and setup.py.\n- Fix Node 20 deprecation warnings in GH Actions. (6193cea)
- feat: add standalone getReadings parser and bump version to 0.0.7\n\n- Add support for flattening standalone `getReadings` list payload.\n- Bump package version to 0.0.7 in pyproject.toml and setup.py.\n- Fix Node 20 deprecation warnings in GH Actions. (e8577ff)
- fix: circuit breaker stale timestamp, 4xx false-positive, dead code, missing device params (f758581)
- fix-bugs (a01f334)
- fix: add missing DOS_2_ELO entry to DEVICE_PARAMETERS (c764d72)
- fix: correct connect timeout and remove unnecessary async methods (fc01e1b)
- fix api error handling and test setup (cd57bef)
- fix-hostname-validation-port (aa62a92)
- Fix hostname validation to allow optional port numbers (64b1ddb)
- Fix hostname validation to allow port numbers (0d6c68c)
- fix-wiki-sync-workflow (bfdd9c3)
- Merge branch 'main' into fix-wiki-sync-workflow-4505122535070983312 (fae7b07)
- ci: Opt-in to Node.js 24 for GitHub Actions to fix deprecation warning (bac4d8d)
- fix-wiki-sync-workflow (c79dc63)
- fix-wiki-sync-workflow (7c8e3c7)
- Merge branch 'main' into fix/aiohttp-ssl-typing-13781193386234050942 (b92e524)
- Fix aiohttp SSL typing issue (f199b7a)

### 📚 Documentation | Dokumentation

- docs: sync CLAUDE.md version with manifest (1.2.4-dev) (a7092fc)
- Update README.md (0c4969e)
- docs: update broken HACS download URLs (09aa3cd)
- docs: update broken HACS download URLs (8b2fe25)
- release: v0.0.17 - hardware profile, i18n docs, full test coverage (ccdb78a)
- docs: add i18n language selector with DE translations, fix ruff config (7ec861e)
- ci(docs): exclude .git from rsync in wiki-sync workflow (672e207)
- docs: update documentation and fix wiki-sync (2486695)
- docs: update readme, wiki and changelog for v0.0.7\n\n- Add RELEASE_NOTES_v0.0.7.md with changelog and explanations.\n- Update README.md to explain transparent Standalone payload parsing.\n- Add Standalone description to docs/Fetching-Data.md. (5fabda6)
- align docs workflows for pages and wiki (9424ad3)
- docs: add release notes for v0.0.2 (05dad29)
- docs: Split Home.md into multiple wiki pages (ddc7b04)
- docs: Update README to reflect AGPLv3 license (670b518)
- Merge branch 'main' into docs/add-wiki-5551993568176912030 (e5cb3bc)
- docs: add custom bash workflow for wiki sync (0f76c7a)
- docs/add-wiki (c8eb047)
- docs: move WIKI to docs/ and add auto-update workflow (51a109d)
- Update license badge style in README.md (53c1ff6)
- Update license badge in README.md (e70b278)
- docs: create comprehensive WIKI.md and link it in README.md (6a9c7a6)
- Docs: Add 'Use at your own risk' warning (c35039d)
- Docs: Add Violet Pool Controller info and disclaimer (b42cb85)
- Docs: Add LICENSE, SECURITY.md, and CODE_OF_CONDUCT.md (6e4e993)
- Docs: Add PyPI badges and sponsor buttons to README (b3d034b)
- Update README.md (819b228)

### 🧪 Tests

- fix: correct device state mapping, controller mismatches, and broken test/CI setup (5fcb4d4)
- feat: add mock server, smoke tests, and AGENTS.md (c4944d9)
- fix: update test for form-encoded set_config, fix dev-release workflow if-condition (2937f5f)
- feat: v0.0.18 - error codes, response parsing, dosing tests, live-verified, API reference (eb9b7e6)
- release: v0.0.17 - hardware profile, i18n docs, full test coverage (ccdb78a)
- chore(ci): add tox matrix and improve API maintainability/tests (f464ef8)
- fix api error handling and test setup (cd57bef)
- Add unit tests for VioletPoolAPI (393083f)

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

📋 [Full changelog: v1.2.3...v1.2.4-beta.1](https://github.com/Xerolux/violet-hass/compare/v1.2.3...v1.2.4-beta.1)

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

_Generated automatically by GitHub Actions on 2026-06-11 11:51:37 UTC_
