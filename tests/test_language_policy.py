"""Everything written into this repository is English.

The policy lives in CLAUDE.md; this file is what makes it hold. The changelog
matters most: ``release.yml`` lifts a version's section verbatim onto the
GitHub release page, so the language of CHANGELOG.md is not an internal
detail - it is what every HACS user reads on the release.

Entries up to and including 2.5.7 were written in German before the policy
existed and are kept as published; everything newer must be English.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
CHANGELOG = REPO / "CHANGELOG.md"

# The last version released before the language policy. Entries up to here are
# historical record, not something to rewrite.
GRANDFATHERED_THROUGH = (2, 5, 7)

# Section headings that only a German entry can carry. "Tests" and "Security"
# read the same in both languages, so they say nothing either way.
GERMAN_HEADINGS = (
    "Behoben",
    "Hinzugefügt",
    "Geändert",
    "Entfernt",
    "Verbessert",
    "Sicherheit",
    "Dokumentation",
    "Bekannte Probleme",
)

# A version is three numbers plus an optional pre-release suffix, so that a beta
# such as 2.5.14-beta.1 is recognised as its own release with its own changelog
# section - the release workflow lifts that section onto the release page.
_VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)(\S*)$")
_VERSION_HEADING = re.compile(r"^## Version (\d+\.\d+\.\d+\S*)")

# (major, minor, patch, pre-release suffix); the suffix is "" for a stable release.
Release = tuple[int, int, int, str]


def _parse(version: str) -> Release:
    """Return a version string as (major, minor, patch, suffix)."""
    match = _VERSION.match(version.strip())
    assert match is not None, f"Unparsable version: {version!r}"
    return (int(match[1]), int(match[2]), int(match[3]), match[4])


def _label(release: Release) -> str:
    """Return a release tuple in the form it is written in the changelog."""
    major, minor, patch, suffix = release
    return f"{major}.{minor}.{patch}{suffix}"


def _sections() -> list[tuple[Release, str]]:
    """Return every changelog entry as (version, body)."""
    lines = CHANGELOG.read_text(encoding="utf-8").splitlines()
    starts = [i for i, line in enumerate(lines) if _VERSION_HEADING.match(line)]
    entries = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        match = _VERSION_HEADING.match(lines[start])
        assert match is not None
        entries.append((_parse(match[1]), "\n".join(lines[start + 1 : end])))
    return entries


def _current_version() -> Release:
    """Return the version the integration currently reports."""
    text = (REPO / "custom_components" / "violet_pool_controller" / ".version").read_text()
    return _parse(text)


def test_the_changelog_lists_the_current_version() -> None:
    """A release without its section publishes an empty page."""
    versions = [version for version, _ in _sections()]

    assert _current_version() in versions


@pytest.mark.parametrize("heading", GERMAN_HEADINGS)
def test_new_entries_use_english_headings(heading: str) -> None:
    """A German entry turns straight into a German release page."""
    offenders = sorted(
        _label(version)
        for version, body in _sections()
        if version[:3] > GRANDFATHERED_THROUGH and f"### {heading}" in body
    )

    assert not offenders, (
        f"Changelog entries {offenders} use the German heading '{heading}'. "
        "Everything from 2.5.8 onwards is English - see CLAUDE.md."
    )


def test_a_prerelease_gets_its_own_changelog_section() -> None:
    """A beta publishes a release page too, so it needs a section of its own.

    The heading and .version parsing used to accept three numbers only, which
    made every pre-release look like a version without a changelog entry.
    """
    assert _parse("2.5.14-beta.1") == (2, 5, 14, "-beta.1")
    assert _parse("2.5.14") == (2, 5, 14, "")
    assert _label(_parse("2.5.14-beta.1")) == "2.5.14-beta.1"

    # A pre-release is newer than the grandfathered German entries, so its
    # section is held to the English policy like any other.
    assert _parse("2.5.8-beta.1")[:3] > GRANDFATHERED_THROUGH


def test_the_changelog_does_not_declare_itself_german() -> None:
    """The header used to say the opposite of the policy."""
    header = CHANGELOG.read_text(encoding="utf-8").split("## Version", 1)[0]

    assert "auf Deutsch" not in header
    assert "written in English" in header


def test_the_release_page_boilerplate_is_english() -> None:
    """release.yml appends this text to every release it publishes."""
    workflow = (REPO / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    for german in ("Über HACS aktualisieren", "Diese Integration entsteht", "Unterstützung"):
        assert german not in workflow


def test_the_policy_is_written_down() -> None:
    """Without the rule in CLAUDE.md these tests are just opinions."""
    claude_md = (REPO / "CLAUDE.md").read_text(encoding="utf-8")

    assert "## Language Policy" in claude_md

def test_no_second_changelog() -> None:
    """One changelog, and it is the one the release lifts its notes from.

    ``docs/CHANGELOG.md`` was a stale German copy that stopped at 2.3.0-beta.1
    while the real file was at 2.5.9 - and the pull request template told
    contributors to write into it, while the wiki linked to it as the complete
    changelog. A reader following either was six weeks behind.
    """
    strays = [path.name for path in (REPO / "docs").glob("*.md")
              if path.name in {"CHANGELOG.md", "RELEASE_NOTES.md"}]

    assert not strays, f"docs/ holds a second changelog: {strays}"


def test_the_changelog_links_point_at_the_real_file() -> None:
    """A link to the old copy sends readers to a changelog that stopped."""
    skip = {".git", ".tox", ".venv", "node_modules", "__pycache__"}
    offenders = [
        str(path.relative_to(REPO))
        for path in list(REPO.rglob("*.md")) + list(REPO.rglob("*.yml"))
        if not skip & set(path.parts)
        and "docs/CHANGELOG.md" in path.read_text(encoding="utf-8")
    ]

    assert not offenders, f"still pointing at docs/CHANGELOG.md: {offenders}"


# ---------------------------------------------------------------------------
# German in Python sources
# ---------------------------------------------------------------------------
#
# Ported from the sibling repository (violet-poolController-api,
# tests/test_language_policy.py::test_python_sources_are_english). A German
# comment, docstring or log line is read by people who do not speak German, and
# it is invisible to every reviewer outside the maintainer.

# Directories that hold generated, vendored or virtual-env copies of sources.
# Scanning them says nothing about what is written in this repository.
GENERATED_DIRS = frozenset(
    {".git", ".tox", ".venv", "venv", "build", "dist", "__pycache__", ".mypy_cache", ".ruff_cache"}
)

# This file has to name the German words it looks for, so it exempts itself.
SELF = Path(__file__).name

# TEMPORARY EXEMPTIONS - remove each entry as its file is translated.
#
# These files still carry German prose. They are listed here so the scan can be
# switched on today instead of waiting for the translation to finish; every
# entry is a debt, not a decision. Three groups:
#
#   * const_sensors.py, error_codes.py, error_handler.py - German entity names,
#     controller error descriptions and user-facing recovery hints inside the
#     integration. These belong in translations/*.json, not in Python.
#   * test_api.py, test_config_flow.py, test_device.py, test_sanitizer.py,
#     test_entity_state.py - German test docstrings and assertion messages.
#   * test_dosing_channel_setpoints.py, test_romcode_sensors.py,
#     test_translation_coverage.py, test_translation_parity.py - these quote
#     German user reports verbatim inside otherwise English docstrings. If the
#     maintainer decides quotations are legitimate, replace these four entries
#     with a narrower rule rather than leaving them on this list.
#
# Anything NOT on this list must be English. Do not add to it.
PENDING_TRANSLATION = frozenset(
    {
        "custom_components/violet_pool_controller/const_sensors.py",
        "custom_components/violet_pool_controller/error_codes.py",
        "custom_components/violet_pool_controller/error_handler.py",
        "tests/test_api.py",
        "tests/test_config_flow.py",
        "tests/test_device.py",
        "tests/test_dosing_channel_setpoints.py",
        "tests/test_entity_state.py",
        "tests/test_romcode_sensors.py",
        "tests/test_sanitizer.py",
        "tests/test_translation_coverage.py",
        "tests/test_translation_parity.py",
    }
)

# Words that only appear in German prose. Deliberately not "in", "die" or
# "der": those collide with English words or with identifiers.
GERMAN_WORDS = (
    "für",
    "über",
    "nicht",
    "wird",
    "werden",
    "wenn",
    "diese",
    "dieser",
    "keine",
    "sollte",
    "und",
    "bei",
    "einen",
    "eine",
    "erlaubt",
    "erlaubter",
    "wert",
    "verwende",
    "ungültig",
    "ungültige",
    "ungültigen",
    "ungültiger",
    "verfügbar",
    "zurück",
    "zurückgesetzt",
    "gefährlich",
    "gefährliche",
    "initialisiert",
    "unbekannter",
    "warte",
)
_GERMAN = re.compile(r"\b(" + "|".join(GERMAN_WORDS) + r")\b", re.IGNORECASE)


def _python_sources() -> list[Path]:
    """Return every Python file the policy applies to right now."""
    return sorted(
        path
        for path in REPO.rglob("*.py")
        if not (GENERATED_DIRS & set(path.parts))
        and not any(part.endswith(".egg-info") for part in path.parts)
        and path.name != SELF
        and path.relative_to(REPO).as_posix() not in PENDING_TRANSLATION
    )


@pytest.mark.parametrize("path", _python_sources(), ids=lambda p: p.name)
def test_python_sources_are_english(path: Path) -> None:
    """A German comment is read by people who do not speak German."""
    offenders = [
        f"{path.relative_to(REPO).as_posix()}:{number}: {line.strip()}"
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if _GERMAN.search(line)
    ]

    assert not offenders, (
        "German text in a Python source - see the Language Policy in CLAUDE.md:\n"
        + "\n".join(offenders)
    )


def test_the_localisation_files_are_exempt() -> None:
    """The exemptions are the point, not an oversight - guard them too.

    ``translations/*.json`` IS the localisation, ``README.de.md`` and
    ``docs/wiki/*.de.md`` are the German half of the bilingual documentation.
    None of them is Python, so the scan above never sees them; this test says
    so out loud, so that nobody "fixes" the policy by translating them.
    """
    german_translation = REPO / "custom_components" / "violet_pool_controller"
    german_translation = german_translation / "translations" / "de.json"

    assert german_translation.exists()
    assert not [path for path in _python_sources() if "translations" in path.parts]
    assert (REPO / "README.de.md").exists()
    assert list((REPO / "docs" / "wiki").glob("*.de.md"))


# ---------------------------------------------------------------------------
# Version strings in the published documentation
# ---------------------------------------------------------------------------

# Files that print the integration version to a reader. They were frozen at
# 2.3.0-beta.1 for four minor releases because nothing checked them.
VERSIONED_DOCS = (
    "docs/wiki/_Sidebar.md",
    "docs/wiki/_Sidebar.de.md",
    "docs/wiki/_Footer.md",
    "docs/wiki/_Footer.de.md",
    "docs/wiki/Home.md",
    "docs/wiki/Home.de.md",
    "docs/wiki/README.md",
    "docs/wiki/Installation-and-Setup.md",
    "docs/wiki/Diagnostics.md",
    "docs/index.html",
    "index.html",
)


def _documented_version() -> str:
    """Return the version the release is being cut at.

    Read from pyproject.toml rather than ``.version`` on purpose: validate.yml's
    "Version consistency" job already asserts that pyproject.toml,
    ``manifest.json``, ``const.py``, ``.version`` and CLAUDE.md carry the same
    string, so keying the docs to pyproject.toml checks the same number without
    duplicating that comparison here.
    """
    with (REPO / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)["project"]["version"]


@pytest.mark.parametrize("relative", VERSIONED_DOCS)
def test_the_documentation_names_the_current_version(relative: str) -> None:
    """A wiki page that names an old version is worse than one naming none."""
    path = REPO / relative
    version = _documented_version()

    assert path.exists(), f"{relative} is listed as a versioned doc but does not exist"
    assert version in path.read_text(encoding="utf-8"), (
        f"{relative} does not mention version {version}. Either update it or "
        "drop it from VERSIONED_DOCS - a stale version string is a bug report "
        "waiting to happen."
    )
