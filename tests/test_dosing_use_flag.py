"""Tests for dosing switch _USE flag: disabled channels must show as OFF.

The core logic lives in switch._dosing_switch_on(), a pure function that can be
tested without any Home Assistant infrastructure (mirrors test_entity_state.py).
"""
import pytest

from custom_components.violet_pool_controller.switch import _dosing_switch_on


class TestDosingUseFlagPureFunction:
    """_dosing_switch_on(raw_state, use_val) – unit-test the pure helper."""

    # --- _USE = "0" → always False, regardless of state ---

    @pytest.mark.parametrize("state", [0, 1, 2, 3, 4, 5, 6])
    def test_use_zero_forces_off_for_all_states(self, state):
        """`_USE = '0'` must override every numeric state."""
        assert _dosing_switch_on(state, "0") is False

    def test_use_zero_string_variant(self):
        """String '0' with surrounding whitespace still disabled."""
        assert _dosing_switch_on(2, " 0 ") is False

    # --- _USE = "1" → normal STATE_MAP logic ---

    def test_use_one_state_2_is_on(self):
        """Chlor channel: state=2, _USE=1 → ON (from STATE_MAP)."""
        assert _dosing_switch_on(2, "1") is True

    def test_use_one_state_0_is_off(self):
        """pH- channel: state=0 (AUTO_OFF), _USE=1 → OFF."""
        assert _dosing_switch_on(0, "1") is False

    def test_use_one_state_4_is_on(self):
        """state=4 (MANUAL_ON_FORCED), _USE=1 → ON."""
        assert _dosing_switch_on(4, "1") is True

    # --- _USE absent (None) → normal STATE_MAP logic ---

    def test_no_use_key_state_2_falls_back_to_state_map(self):
        """No _USE key: state=2 → True per STATE_MAP."""
        assert _dosing_switch_on(2, None) is True

    def test_no_use_key_state_0_is_off(self):
        """No _USE key: state=0 → False per STATE_MAP."""
        assert _dosing_switch_on(0, None) is False

    # --- Real-world values from the user's JSON ---

    def test_elo_not_in_use(self):
        """DOS_2_ELO: state=2, USE='0' (Elektrolyse disabled) → OFF."""
        assert _dosing_switch_on(2, "0") is False

    def test_floc_not_in_use(self):
        """DOS_6_FLOC: state=2, USE='0' (Flockmittel disabled) → OFF."""
        assert _dosing_switch_on(2, "0") is False

    def test_php_not_in_use(self):
        """DOS_5_PHP: state=2, USE='0' (pH+ disabled) → OFF."""
        assert _dosing_switch_on(2, "0") is False

    def test_chlor_in_use(self):
        """DOS_1_CL: state=2, USE='1' (Chlor active) → ON."""
        assert _dosing_switch_on(2, "1") is True

    def test_phm_in_use(self):
        """DOS_4_PHM: state=2, USE='1' (pH- active) → ON."""
        assert _dosing_switch_on(2, "1") is True
