"""Tests for the input sanitization the API package performs on our behalf.

Home Assistant installs the API package from PyPI, and ``manifest.json`` asks
only for ``>=0.0.38``, so this suite runs against whichever release is
installed.  Behaviour that changed in 0.0.39 - key validation rejecting an
invalid name instead of silently rewriting it into a different, real
controller setting - is therefore guarded by ``requires_api``.  Once the pin
moves to ``>=0.0.39`` the guard and the legacy branches can go.
"""

import pytest
from violet_poolcontroller_api import SETPOINT_RANGES
from violet_poolcontroller_api.utils_sanitizer import InputSanitizer


def _keys_are_validated_not_rewritten() -> bool:
    """Return whether the installed package validates keys instead of rewriting.

    Probed rather than read from the version string: an editable checkout
    reports the version of its last release, so a version comparison would
    skip tests that the code in front of us actually satisfies.
    """
    try:
        return InputSanitizer.validate_device_key("pH_value") == "pH_value"
    except ValueError:
        return False


requires_strict_key_validation = pytest.mark.skipif(
    not _keys_are_validated_not_rewritten(),
    reason="installed violet-poolController-api still rewrites invalid keys (< 0.0.39)",
)


class TestInputSanitizer:
    """Test Input Sanitization functions."""

    def test_sanitize_float_range_validation(self):
        """Test dass Float-Werte korrekt validiert werden."""
        # Within range
        assert InputSanitizer.sanitize_float(7.2, min_value=6.0, max_value=8.0) == 7.2

        # Below minimum
        assert InputSanitizer.sanitize_float(5.0, min_value=6.0, max_value=8.0) == 6.0

        # Above maximum
        assert InputSanitizer.sanitize_float(9.0, min_value=6.0, max_value=8.0) == 8.0

    def test_sanitize_float_precision(self):
        """Test dass Float-Präzision korrekt angewendet wird."""
        assert InputSanitizer.sanitize_float(7.123456, precision=1) == 7.1
        assert InputSanitizer.sanitize_float(7.123456, precision=2) == 7.12
        assert InputSanitizer.sanitize_float(7.123456, precision=3) == 7.123

    def test_sanitize_float_invalid_input(self):
        """Test dass ungültige Float-Eingaben auf Default fallen."""
        assert InputSanitizer.sanitize_float("invalid", default=0.0) == 0.0
        assert InputSanitizer.sanitize_float(None, default=5.0) == 5.0

    def test_sanitize_integer_range_validation(self):
        """Test dass Integer-Werte korrekt validiert werden."""
        # Within range
        assert InputSanitizer.sanitize_integer(5, min_value=1, max_value=10) == 5

        # Below minimum
        assert InputSanitizer.sanitize_integer(0, min_value=1, max_value=10) == 1

        # Above maximum
        assert InputSanitizer.sanitize_integer(15, min_value=1, max_value=10) == 10

    def test_sanitize_integer_float_conversion(self):
        """Test dass Float zu Integer konvertiert wird."""
        assert InputSanitizer.sanitize_integer(7.8) == 7
        assert InputSanitizer.sanitize_integer(7.2) == 7
        assert InputSanitizer.sanitize_integer(7.9) == 7

    def test_sanitize_integer_invalid_input(self):
        """Test dass ungültige Integer-Eingaben auf Default fallen."""
        assert InputSanitizer.sanitize_integer("invalid", default=0) == 0
        assert InputSanitizer.sanitize_integer(None, default=10) == 10

    def test_validate_ph_value(self):
        """Test dass pH-Werte korrekt validiert werden.

        The bounds are taken from the API package's own ``SETPOINT_RANGES``
        instead of being hard-coded: the accepted range mirrors what the
        controller allows as a setpoint and has been narrowed before (the
        upper bound went from 9.0 to 8.0 in violet-poolController-api 0.0.37).
        """
        ph_min, ph_max = SETPOINT_RANGES["DOSAGE_phminus_setpoint"]

        assert InputSanitizer.validate_ph_value(7.2) == 7.2
        assert InputSanitizer.validate_ph_value(ph_min - 1.0) == ph_min  # Too low
        assert InputSanitizer.validate_ph_value(ph_max + 1.0) == ph_max  # Too high
        assert InputSanitizer.validate_ph_value("invalid") == 7.2  # Default

    def test_validate_orp_value(self):
        """Test dass ORP-Werte korrekt validiert werden."""
        # Valid range: 500-900 mV
        assert InputSanitizer.validate_orp_value(700) == 700
        assert InputSanitizer.validate_orp_value(300) == 500  # Too low
        assert InputSanitizer.validate_orp_value(1000) == 900  # Too high
        assert InputSanitizer.validate_orp_value("invalid") == 700  # Default

    def test_validate_chlorine_level(self):
        """Test dass Chlor-Werte korrekt validiert werden."""
        # Valid range: 0.0-5.0 mg/l
        assert InputSanitizer.validate_chlorine_level(1.5) == 1.5
        assert InputSanitizer.validate_chlorine_level(-1.0) == 0.0  # Too low
        assert InputSanitizer.validate_chlorine_level(10.0) == 5.0  # Too high
        assert InputSanitizer.validate_chlorine_level("invalid") == 0.6  # Default

    def test_validate_temperature(self):
        """Test dass Temperatur-Werte korrekt validiert werden."""
        # Valid range: -50.0 to 100.0°C (default)
        assert InputSanitizer.validate_temperature(25.5) == 25.5
        assert InputSanitizer.validate_temperature(-60.0) == -50.0  # Too low
        assert InputSanitizer.validate_temperature(150.0) == 100.0  # Too high

    def test_sanitize_string_max_length(self):
        """Test dass String-Länge begrenzt wird."""
        long_string = "a" * 300
        result = InputSanitizer.sanitize_string(long_string, max_length=255)
        assert len(result) == 255

    def test_sanitize_string_html_escape(self):
        """Test dass HTML-Zeichen escaped werden."""
        dangerous = "<script>alert('xss')</script>"
        safe = InputSanitizer.sanitize_string(dangerous, escape_html=True, allow_special_chars=True)
        assert "<script>" not in safe
        assert "&lt;script&gt;" in safe

    def test_sanitize_string_special_chars_removal(self):
        """Test dass Sonderzeichen entfernt werden wenn nicht erlaubt."""
        dangerous = "test<>;&|$()"
        safe = InputSanitizer.sanitize_string(dangerous, allow_special_chars=False)
        assert safe == "test"  # Nur alphanumerische Zeichen

    def test_sanitize_boolean_various_inputs(self):
        """Test dass verschiedene Boolean-Eingaben korrekt konvertiert werden."""
        # True values
        assert InputSanitizer.sanitize_boolean(True) is True
        assert InputSanitizer.sanitize_boolean("true") is True
        assert InputSanitizer.sanitize_boolean("TRUE") is True
        assert InputSanitizer.sanitize_boolean("yes") is True
        assert InputSanitizer.sanitize_boolean("1") is True
        assert InputSanitizer.sanitize_boolean(1) is True

        # False values
        assert InputSanitizer.sanitize_boolean(False) is False
        assert InputSanitizer.sanitize_boolean("false") is False
        assert InputSanitizer.sanitize_boolean("FALSE") is False
        assert InputSanitizer.sanitize_boolean("no") is False
        assert InputSanitizer.sanitize_boolean("0") is False
        assert InputSanitizer.sanitize_boolean(0) is False

        # Invalid defaults to default
        assert InputSanitizer.sanitize_boolean("invalid", default=False) is False
        assert InputSanitizer.sanitize_boolean("invalid", default=True) is True

    @requires_strict_key_validation
    def test_validate_device_key(self):
        """A valid key is returned unchanged, including its case.

        Controller keys are case-sensitive - ``pH_value`` and
        ``onewire1_value`` are real keys - so the old upper-casing turned a
        valid key into one the controller does not have.
        """
        assert InputSanitizer.validate_device_key("PUMP") == "PUMP"
        assert InputSanitizer.validate_device_key("DOS_1_CL") == "DOS_1_CL"
        assert InputSanitizer.validate_device_key("pH_value") == "pH_value"
        assert InputSanitizer.validate_device_key("onewire1_value") == "onewire1_value"

    @requires_strict_key_validation
    def test_validate_device_key_rejects_invalid_characters(self):
        """An invalid key is an error, never a rewrite into a different key."""
        for bad in ("PUMP-1", "PUMP 1", "PUMP<>"):
            with pytest.raises(ValueError, match="invalid characters"):
                InputSanitizer.validate_device_key(bad)

    @requires_strict_key_validation
    def test_validate_device_key_too_long(self):
        """An over-long device key is rejected."""
        long_key = "A" * 60
        with pytest.raises(ValueError, match="too long"):
            InputSanitizer.validate_device_key(long_key)

    def test_validate_api_parameter(self):
        """A valid parameter name is returned unchanged."""
        assert InputSanitizer.validate_api_parameter("temperature") == "temperature"
        assert InputSanitizer.validate_api_parameter("pump_speed") == "pump_speed"
        assert InputSanitizer.validate_api_parameter("pH-value") == "pH-value"

    @requires_strict_key_validation
    def test_validate_api_parameter_rejects_invalid_characters(self):
        """Stripping characters used to write to a different, real setting.

        ``DOSAGE_ph.minus`` became ``DOSAGE_phminus`` - a typo silently
        changed a setting the caller never named.
        """
        for bad in ("test<>", "DOSAGE_ph.minus", "pool mode"):
            with pytest.raises(ValueError, match="invalid characters"):
                InputSanitizer.validate_api_parameter(bad)

    def test_validate_api_parameter_path_traversal(self):
        """Path traversal is rejected before anything else."""
        with pytest.raises(ValueError, match="[Pp]ath traversal"):
            InputSanitizer.validate_api_parameter("../../../etc/passwd")

        with pytest.raises(ValueError, match="[Pp]ath traversal"):
            InputSanitizer.validate_api_parameter("..\\..\\windows\\system32")

    @requires_strict_key_validation
    def test_validate_api_parameter_too_long(self):
        """An over-long parameter is rejected."""
        long_param = "a" * 150
        with pytest.raises(ValueError, match="too long"):
            InputSanitizer.validate_api_parameter(long_param)
