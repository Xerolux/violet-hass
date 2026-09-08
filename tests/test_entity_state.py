"""Tests for the shared state-interpretation utilities."""

import sys
from pathlib import Path

import pytest

# Ensure repository root is on the import path (mirrors other tests)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from custom_components.violet_pool_controller.entity import (  # noqa: E402
    interpret_state_as_bool,
    parse_state_code,
)


@pytest.mark.parametrize(
    "raw_state,expected",
    [
        ("3|PUMP_ANTI_FREEZE", True),
        ("5|AUTO_WAIT", False),
        # State 2 = "Auto - Priority OFF (Rule Blocked)" → device is OFF
        (" 2 |AUTO", False),
        ("0|OFF", False),
        ("N/A", None),
        ("n/a", None),
        ("UNKNOWN", None),
        ("unknown", None),
        ("NONE", None),
        ("NULL", None),
        ("---", None),
        (None, None),
        ("", None),
    ],
)
def test_interpret_state_with_numeric_prefix(raw_state, expected):
    """Composite string states should use their numeric prefix for evaluation."""

    assert interpret_state_as_bool(raw_state, "PUMPSTATE") is expected


@pytest.mark.parametrize(
    "raw_state,expected",
    [
        (0, False),
        (1, True),  # ON via digital input
        (2, True),  # ON via HTTP request (not "rule blocked" like outputs)
    ],
)
def test_interpret_pv_surplus_states(raw_state, expected):
    """PVSURPLUS uses its own 0/1/2 scheme, not the 0-6 output states."""

    assert interpret_state_as_bool(raw_state, "PVSURPLUS") is expected


def test_unrecognized_string_is_unknown():
    """Unknown strings must not be guessed as ON."""

    assert interpret_state_as_bool("MAINTENANCE", "PUMP") is None


@pytest.mark.parametrize(
    "raw_state,expected",
    [
        # Composite states carry the code in their leading part
        ("3|PUMP_ANTI_FREEZE", 3),
        ("6|X", 6),
        ("3|PUMP_ANTI_FREEZE|NEW_FLAG", 3),
        (" 4 | MANUAL ", 4),
        # Plain values
        ("1", 1),
        ("0", 0),
        (2, 2),
        (2.0, 2),
        # Nothing usable
        ("[]", None),
        ("{}", None),
        ([], None),
        ({}, None),
        ("", None),
        ("|X", None),
        ("MAINTENANCE", None),
        (None, None),
    ],
)
def test_parse_state_code(raw_state, expected):
    """The state code is the leading part of a plain or composite value."""

    assert parse_state_code(raw_state) == expected


def test_parse_state_code_never_raises_on_containers():
    """Lists and dicts reach this helper from *STATE keys such as "[]"."""

    assert parse_state_code(["3", "PUMP_ANTI_FREEZE"]) is None
    assert parse_state_code({"state": 3}) is None
