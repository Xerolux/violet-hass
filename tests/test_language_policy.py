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

_VERSION_HEADING = re.compile(r"^## Version (\d+)\.(\d+)\.(\d+)")


def _sections() -> list[tuple[tuple[int, int, int], str]]:
    """Return every changelog entry as (version, body)."""
    lines = CHANGELOG.read_text(encoding="utf-8").splitlines()
    starts = [i for i, line in enumerate(lines) if _VERSION_HEADING.match(line)]
    entries = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        match = _VERSION_HEADING.match(lines[start])
        assert match is not None
        version = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        entries.append((version, "\n".join(lines[start + 1 : end])))
    return entries


def _current_version() -> tuple[int, int, int]:
    """Return the version the integration currently reports."""
    text = (REPO / "custom_components" / "violet_pool_controller" / ".version").read_text()
    return tuple(int(part) for part in text.strip().split("."))  # type: ignore[return-value]


def test_the_changelog_lists_the_current_version() -> None:
    """A release without its section publishes an empty page."""
    versions = [version for version, _ in _sections()]

    assert _current_version() in versions


@pytest.mark.parametrize("heading", GERMAN_HEADINGS)
def test_new_entries_use_english_headings(heading: str) -> None:
    """A German entry turns straight into a German release page."""
    offenders = sorted(
        ".".join(str(part) for part in version)
        for version, body in _sections()
        if version > GRANDFATHERED_THROUGH and f"### {heading}" in body
    )

    assert not offenders, (
        f"Changelog entries {offenders} use the German heading '{heading}'. "
        "Everything from 2.5.8 onwards is English - see CLAUDE.md."
    )


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
