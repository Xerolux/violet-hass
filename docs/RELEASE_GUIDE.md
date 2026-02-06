# Release Guide

This guide explains how to create releases for the Violet Pool Controller integration.

## Release Types

The integration supports four types of releases:

### 1. **Stable Release** ✅
- Production-ready releases
- Marked as "latest" on GitHub
- Full changelog and documentation
- **Format:** `v1.0.0`, `v1.2.3`

### 2. **Beta Release** 🟡
- Feature-complete but needs testing
- Pre-release flag set
- May contain minor bugs
- **Format:** `v1.0.0-beta.1`, `v1.2.0-beta.2`

### 3. **Alpha Release** 🔴
- Early testing versions
- Experimental features
- May be unstable
- **Format:** `v1.0.0-alpha.1`, `v1.2.0-alpha.3`

### 4. **Draft Release** 📝
- Work-in-progress
- Not publicly visible until published
- Used for review before release
- **Format:** Any valid version tag

---

## Creating a Release

### Method 1: Automatic (Recommended) - Tag Push

1. **Update version locally** (optional, workflow will do this too):
   ```bash
   # Edit these files:
   # - custom_components/violet_pool_controller/manifest.json
   # - custom_components/violet_pool_controller/const.py
   ```

2. **Create and push a tag:**

   **For stable release:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

   **For beta release:**
   ```bash
   git tag v1.0.0-beta.1
   git push origin v1.0.0-beta.1
   ```

   **For alpha release:**
   ```bash
   git tag v1.0.0-alpha.1
   git push origin v1.0.0-alpha.1
   ```

3. **Workflow runs automatically** when tag is pushed
4. **Release is created** with:
   - Auto-generated release notes
   - ZIP artifact (`violet_pool_controller.zip`)
   - SHA256 checksum
   - Installation instructions
   - Credits and funding links

---

### Method 2: Manual Release via GitHub Actions

1. **Go to Actions tab** on GitHub
2. **Click "Release Management"** workflow
3. **Click "Run workflow"** button
4. **Fill in the form:**
   - **Tag name:** `v1.0.0` (or `v1.0.0-beta.1`, etc.)
   - **Release type:** Choose from dropdown
     - `stable` - Production release
     - `beta` - Beta testing release
     - `alpha` - Alpha testing release
     - `draft` - Draft (not published)
   - **Mark as latest:** Check if this should be the latest release

5. **Click "Run workflow"**

---

## What Happens During Release

The release workflow performs these steps:

### 1. Version Detection & Validation
```bash
✅ Detects release type from tag name
✅ Validates semantic versioning format
✅ Sets pre-release flags automatically
```

### 2. Version Updates
```bash
✅ Updates manifest.json
✅ Updates const.py
✅ Commits changes back to repo
```

### 3. Changelog Generation
```bash
✅ Parses commits since last stable release
✅ Categorizes into:
   - New Features
   - Improvements
   - Bug Fixes
   - Documentation
   - Tests
✅ Creates formatted release notes
```

### 4. Artifact Creation
```bash
✅ Creates ZIP archive
✅ Generates SHA256 checksum
✅ Uploads to GitHub release
```

### 5. Documentation Updates
```bash
✅ Updates CHANGELOG.md (cumulative history)
✅ Updates RELEASE_NOTES.md (latest only)
✅ Commits and pushes changes
```

### 6. Social Media (Stable Only)
```bash
✅ Posts to X (Twitter) if secrets configured
✅ Announces new release
```

---

## Release Notes Format

The workflow automatically generates release notes in this format:

```markdown
## v1.0.0 – Violet Pool Controller

✅ **STABLE RELEASE**

### ✨ New Features | Neue Funktionen
- Add support for DMX lighting control (abc123)
- Add temperature setpoint entities (def456)

### 🚀 Improvements | Verbesserungen
- Improve error handling in API client (ghi789)
- Optimize sensor update performance (jkl012)

### 🔧 Bug Fixes | Fehlerbehebungen
- Fix switch state interpretation for DMX scenes (mno345)
- Fix memory leak in coordinator (pqr678)

### 📚 Documentation | Dokumentation
- Add installation guide (stu901)
- Update README with new features (vwx234)

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

📋 [Full changelog: v0.9.0...v1.0.0](...)

---

### ❤️ Support | Unterstützung

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

---

### 💬 Feedback & Contributions

- 🐛 **[Report a bug](...)**
- 💡 **[Request a feature](...)**
- 🤝 **[Contribute](...)**

---

### 📄 Credits

**Developed by:** [Xerolux](https://github.com/Xerolux)
**Integration for:** Violet Pool Controller by PoolDigital GmbH & Co. KG
**License:** MIT
```

---

## Commit Message Conventions

To get better automatic changelogs, use these prefixes in commit messages:

```bash
# New Features
feat: Add DMX scene support
add: Add temperature setpoint entities

# Improvements
improve: Better error handling
enhance: Faster sensor updates
update: Modernize API client
refactor: Simplify switch logic
optimize: Reduce memory usage

# Bug Fixes
fix: Resolve switch state bug
bug: Fix memory leak
patch: Hotfix for crash
hotfix: Emergency fix for critical bug
bugfix: Fix sensor reading error

# Documentation
doc: Add installation guide
docs: Update README
documentation: Improve API docs

# Tests
test: Add integration tests
tests: Improve test coverage
testing: Add sensor state tests
```

---

## Examples

### Example 1: Stable Release v1.0.0

```bash
# Make sure you're on main branch
git checkout main
git pull

# Create tag
git tag v1.0.0

# Push tag (triggers workflow)
git push origin v1.0.0

# Workflow will:
# ✅ Detect as stable release
# ✅ Mark as latest
# ✅ Generate changelog from v0.9.0 to v1.0.0
# ✅ Post to X (Twitter)
```

---

### Example 2: Beta Release v1.1.0-beta.1

```bash
# Create beta tag
git tag v1.1.0-beta.1

# Push tag
git push origin v1.1.0-beta.1

# Workflow will:
# ✅ Detect as beta (pre-release)
# ✅ Mark as pre-release (not latest)
# ✅ Add beta warning to release notes
# ✅ Skip X post
```

---

### Example 3: Alpha Release v2.0.0-alpha.1

```bash
# Create alpha tag
git tag v2.0.0-alpha.1

# Push tag
git push origin v2.0.0-alpha.1

# Workflow will:
# ✅ Detect as alpha (pre-release)
# ✅ Add "use with caution" warning
# ✅ Mark as pre-release
# ✅ Skip X post
```

---

### Example 4: Draft Release (Manual)

```bash
# Go to GitHub Actions
# Click "Release Management"
# Click "Run workflow"
# Fill in:
#   Tag: v1.0.0-rc.1
#   Type: draft
#   Latest: no
# Click "Run workflow"

# Workflow will:
# ✅ Create draft release (not published)
# ✅ Allow review before publishing
# ✅ Can edit release notes manually
```

---

## Troubleshooting

### Issue: "Invalid tag format"

**Solution:** Use semantic versioning:
```bash
✅ v1.0.0
✅ v1.2.3
✅ v1.0.0-beta.1
✅ v1.0.0-alpha.1
✅ v1.0.0-rc.1

❌ 1.0.0 (missing 'v' prefix)
❌ v1.0 (missing patch version)
❌ v1.0.0.1 (too many parts)
```

---

### Issue: "Version not updated in files"

**Solution:** Check these files have correct format:
```json
// manifest.json
{
  "version": "1.0.0"
}
```

```python
# const.py
INTEGRATION_VERSION = "1.0.0"
```

---

### Issue: "Changelog empty"

**Solution:** Make sure you have commits with proper keywords:
```bash
# Good commit messages:
✅ "fix: Resolve switch bug"
✅ "feat: Add new sensor"
✅ "improve: Better performance"

# Bad commit messages:
❌ "updates"
❌ "wip"
❌ "asdf"
```

---

### Issue: "X post failed"

**Solution:** Configure these GitHub secrets:
```
TWITTER_CONSUMER_API_KEY
TWITTER_CONSUMER_API_SECRET
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET
```

Or set `continue-on-error: true` (already configured) to skip X posting.

---

## Release Checklist

Before creating a release, check:

- [ ] All tests pass
- [ ] Version number is correct
- [ ] CHANGELOG.md is up to date (workflow does this automatically)
- [ ] README.md mentions new features
- [ ] Documentation is updated
- [ ] No open critical bugs
- [ ] Code is merged to main branch
- [ ] Git tag follows semantic versioning

---

## Hotfix Releases

For emergency bug fixes:

```bash
# 1. Create hotfix branch
git checkout -b hotfix/v1.0.1 main

# 2. Fix the bug
git commit -m "fix: Emergency fix for critical bug"

# 3. Merge to main
git checkout main
git merge hotfix/v1.0.1

# 4. Tag and release
git tag v1.0.1
git push origin v1.0.1

# 5. Workflow creates hotfix release automatically
```

---

## Release Schedule

Recommended schedule:

- **Alpha:** Every 1-2 weeks (feature development)
- **Beta:** Every 2-4 weeks (feature freeze, bug fixes)
- **RC:** 1 week before stable (final testing)
- **Stable:** Monthly or when ready

---

## Questions?

- 📧 Open an issue on GitHub
- 💬 Discussion in GitHub Discussions
- 🐦 DM on X (Twitter): @xerolux

---

**Happy Releasing! 🚀**
