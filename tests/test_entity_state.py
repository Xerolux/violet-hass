"""Tests für interpret_state_as_bool Utility."""

import sys
from pathlib import Path

import pytest

# Ensure repository root is on the import path (mirrors other tests)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from custom_components.violet_pool_controller.entity import interpret_state_as_bool  # noqa: E402


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
