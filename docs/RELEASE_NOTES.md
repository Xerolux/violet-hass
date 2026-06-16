# Release Notes

**This document is maintained by the release workflow (`.github/workflows/release.yml`).**

Release notes are automatically generated from commits and tags. This file serves as a reference for significant releases and breaking changes.

## Latest Release

See [GitHub Releases](https://github.com/xerolux/violet-hass/releases) for the complete changelog.

## Release Schedule

- **Major versions** (e.g., 2.0.0) → breaking changes
- **Minor versions** (e.g., 2.1.0) → new features, backward-compatible
- **Patch versions** (e.g., 2.0.1) → bug fixes

## Version Requirements

- **Integration Version**: See `manifest.json:version`
- **API Package Version**: See `violet_poolcontroller_api/pyproject.toml:version` (published to PyPI as `violet-poolController-api`)
- **Minimum Home Assistant**: `2026.5.0` (see `hacs.json`)
- **Minimum Python**: `3.14.2` (see `pyproject.toml`)

---

For contributors: see [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.
