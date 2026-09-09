"""Parity between strings.json, the translation files and the keys code uses.

Home Assistant loads a custom integration's UI strings from
``translations/<lang>.json``; ``strings.json`` is the source the English file is
generated from, so for a custom integration the two must be identical.  Every
other language file is expected to carry the same key set - a key the file does
not define falls back to English silently, which is exactly how "teilweise noch
englisch bei deutscher HA" was reported on the forum.

The code-side checks are deliberately asymmetric: a ``translation_key`` used in
Python but missing from ``strings.json`` is a user-visible bug (Home Assistant
renders the raw key), while a key defined in ``strings.json`` that no code path
uses yet is only dead weight and is tolerated.
"""

from __future__ import annotations

import ast
import json
import string
from pathlib import Path

import pytest

COMPONENT_DIR = Path(__file__).parent.parent / "custom_components" / "violet_pool_controller"
TRANSLATIONS_DIR = COMPONENT_DIR / "translations"

# Modules whose ``translation_key=`` arguments name an entity of that platform.
PLATFORM_MODULES = {
    "binary_sensor.py": "binary_sensor",
    "button.py": "button",
    "climate.py": "climate",
    "cover.py": "cover",
    "light.py": "light",
    "number.py": "number",
    "select.py": "select",
    "sensor.py": "sensor",
    "switch.py": "switch",
    "update.py": "update",
}

# Calls whose ``translation_key=`` names an entry outside ``entity.*``.
EXCEPTION_CALLS = frozenset(
    {
        "HomeAssistantError",
        "ServiceValidationError",
        "ConfigEntryAuthFailed",
        "ConfigEntryError",
        "ConfigEntryNotReady",
        "PlatformNotReady",
    }
)
ISSUE_CALLS = frozenset({"async_create_issue", "async_create_repair_issue"})


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _flatten(obj: object, prefix: str = "") -> set[str]:
    """Return every dotted key path in a nested mapping."""
    found: set[str] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            found.add(path)
            found |= _flatten(value, path)
    return found


STRINGS = _load(COMPONENT_DIR / "strings.json")
ENGLISH = _load(TRANSLATIONS_DIR / "en.json")
LANGUAGE_FILES = sorted(p for p in TRANSLATIONS_DIR.glob("*.json") if p.stem != "en")



def _placeholders(value: str) -> set[str]:
    """Return the ``{placeholder}`` names a translation string uses."""
    return {field for _, field, _, _ in string.Formatter().parse(value) if field is not None}


def _strings_by_key(obj: object, prefix: str = "") -> dict[str, str]:
    """Return every dotted key path that maps to a string."""
    found: dict[str, str] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, str):
                found[path] = value
            else:
                found.update(_strings_by_key(value, path))
    return found


def test_strings_json_matches_english_translation() -> None:
    """strings.json and translations/en.json describe the same keys."""
    missing = _flatten(STRINGS) - _flatten(ENGLISH)
    extra = _flatten(ENGLISH) - _flatten(STRINGS)
    hint = (
        " - en.json is generated from strings.json; copy strings.json over "
        "translations/en.json and add the new keys to the other languages."
    )
    assert not missing, f"in strings.json but not en.json: {sorted(missing)[:20]}{hint}"
    assert not extra, f"in en.json but not strings.json: {sorted(extra)[:20]}{hint}"


@pytest.mark.parametrize("path", LANGUAGE_FILES, ids=lambda p: p.name)
def test_language_file_has_the_english_key_set(path: Path) -> None:
    """Every language defines the same keys as English."""
    keys = _flatten(_load(path))
    english = _flatten(ENGLISH)
    missing = english - keys
    extra = keys - english
    assert not missing, (
        f"{path.name} is missing: {sorted(missing)[:20]} - a key a language file "
        "does not define falls back to English without any warning"
    )
    assert not extra, (
        f"{path.name} carries stale keys: {sorted(extra)[:20]} - they translate "
        "nothing any more and should be deleted"
    )


def _collect_translation_keys() -> tuple[set[str], set[tuple[str, str]]]:
    """Return the exception keys and (platform, key) pairs the code uses."""
    exception_keys: set[str] = set()
    entity_keys: set[tuple[str, str]] = set()

    for source in sorted(COMPONENT_DIR.rglob("*.py")):
        platform = PLATFORM_MODULES.get(source.name)
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            keyword = next(
                (
                    kw
                    for kw in node.keywords
                    if kw.arg == "translation_key"
                    and isinstance(kw.value, ast.Constant)
                    and isinstance(kw.value.value, str)
                ),
                None,
            )
            if keyword is None:
                continue
            value = keyword.value.value  # type: ignore[union-attr]
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name in EXCEPTION_CALLS:
                exception_keys.add(value)
            elif name in ISSUE_CALLS:
                continue
            elif platform is not None:
                entity_keys.add((platform, value))
    return exception_keys, entity_keys


CODE_EXCEPTION_KEYS, CODE_ENTITY_KEYS = _collect_translation_keys()


def test_every_raised_exception_key_is_translated() -> None:
    """``raise ...Error(translation_key=...)`` needs an ``exceptions`` entry."""
    defined = set(STRINGS.get("exceptions", {}))
    missing = CODE_EXCEPTION_KEYS - defined
    assert not missing, f"exceptions.* missing from strings.json: {sorted(missing)}"


def test_every_entity_translation_key_is_translated() -> None:
    """A literal entity ``translation_key`` must exist under its platform."""
    missing = {
        f"entity.{platform}.{key}"
        for platform, key in CODE_ENTITY_KEYS
        if key not in STRINGS.get("entity", {}).get(platform, {})
    }
    assert not missing, f"missing from strings.json: {sorted(missing)}"


def test_placeholders_match_the_english_string() -> None:
    """A translated string must use exactly the placeholders English uses.

    Home Assistant compares the two sets in
    ``helpers/translation.py::_validate_placeholders`` and, on any difference,
    **deletes the translated string** -- the user silently gets English back.
    That is how the German setup wizard came to show its safety step with no
    warning in it and its disclaimer step with no disclaimer: both descriptions
    had lost the placeholder carrying the text.
    """
    english = _strings_by_key(ENGLISH)

    offenders: list[str] = []
    for path in LANGUAGE_FILES:
        for key, value in _strings_by_key(_load(path)).items():
            if key not in english:
                continue
            translated = _placeholders(value)
            native = _placeholders(english[key])
            if translated != native:
                offenders.append(
                    f"{path.name}: {key} has {sorted(translated)}, needs {sorted(native)}"
                )

    assert not offenders, "Home Assistant discards these strings:\n" + "\n".join(offenders)


def _markdown_shape(value: str) -> tuple[int, int, int, int]:
    """Return the markdown structure of a string.

    Bold markers, both bullet spellings and the number of non-empty lines. A
    translation of the *current* English carries the same ones, so a difference
    means the translation was written against an older wording.
    """
    return (
        value.count("**"),
        sum(1 for line in value.splitlines() if line.lstrip().startswith("- ")),
        value.count("•"),
        len([line for line in value.splitlines() if line.strip()]),
    )


def test_markdown_shape_matches_the_english_string() -> None:
    """A translated string must be shaped like the English one.

    Nothing else notices when English is rewritten and a translation is not:
    the key is still there, the placeholders still match, the string still
    renders. It just says what the integration used to do. Structure is the
    one part that gives it away, because a heading or a bullet list that was
    added to the English text has no counterpart in the stale translation.

    Two that got through this way: ``options.step.sensors.description``, which
    still promised to choose "which sensors are displayed" long after the step
    had become a datapoint selection covering switches, lights and controls;
    and ``services.smart_dosing.description``, which never got the paragraph
    saying H2O2 dosing is not offered - added when 2.7.0 removed H2O2 from the
    dosing paths for dosing the wrong chemical.
    """
    english = _strings_by_key(ENGLISH)

    offenders: list[str] = []
    for path in LANGUAGE_FILES:
        for key, value in _strings_by_key(_load(path)).items():
            if key not in english or value == english[key]:
                continue
            if _markdown_shape(value) != _markdown_shape(english[key]):
                offenders.append(
                    f"{path.name}: {key} is "
                    f"{_markdown_shape(value)}, English is {_markdown_shape(english[key])} "
                    "(bold markers, '- ' bullets, bullet characters, non-empty lines)"
                )

    assert not offenders, (
        "these translations were written against an older English text:\n"
        + "\n".join(offenders)
    )
