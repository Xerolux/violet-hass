"""Tests für interpret_state_as_bool Utility."""

from pathlib import Path
import sys
import types

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
        (" 2 |AUTO", True),
        ("0|OFF", False),
    ],
)
def test_interpret_state_with_numeric_prefix(raw_state, expected):
    """Composite string states should use their numeric prefix for evaluation."""

    assert interpret_state_as_bool(raw_state, "PUMPSTATE") is expected
