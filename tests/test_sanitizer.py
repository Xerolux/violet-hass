"""Tests for Input Sanitization."""
import pytest

from custom_components.violet_pool_controller.utils_sanitizer import InputSanitizer


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
        """Test dass pH-Werte korrekt validiert werden."""
        # Valid range: 6.0-9.0
        assert InputSanitizer.validate_ph_value(7.2) == 7.2
        assert InputSanitizer.validate_ph_value(5.0) == 6.0  # Too low
        assert InputSanitizer.validate_ph_value(10.0) == 9.0  # Too high
        assert InputSanitizer.validate_ph_value("invalid") == 7.2  # Default

    def test_validate_orp_value(self):
        """Test dass ORP-Werte korrekt validiert werden."""
        # Valid range: 400-900 mV
        assert InputSanitizer.validate_orp_value(700) == 700
        assert InputSanitizer.validate_orp_value(300) == 400  # Too low
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

    def test_validate_speed(self):
        """Test dass Speed-Werte korrekt validiert werden."""
        # Valid range: 1-4 (default)
        assert InputSanitizer.validate_speed(2) == 2
        assert InputSanitizer.validate_speed(0) == 1  # Too low
        assert InputSanitizer.validate_speed(5) == 4  # Too high
        assert InputSanitizer.validate_speed("invalid", default=2) == 2

    def test_validate_duration(self):
        """Test dass Duration-Werte korrekt validiert werden."""
        # Valid range: 0-86400s (24h default)
        assert InputSanitizer.validate_duration(300) == 300
        assert InputSanitizer.validate_duration(-10) == 0  # Negative wird zu 0
        assert InputSanitizer.validate_duration(100000) == 86400  # Too high

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

    def test_validate_device_key(self):
        """Test dass Device-Keys korrekt validiert werden."""
        # Valid keys
        assert InputSanitizer.validate_device_key("PUMP") == "PUMP"
        assert InputSanitizer.validate_device_key("DOS_1_CL") == "DOS_1_CL"

        # Lowercase wird uppercase
        assert InputSanitizer.validate_device_key("pump") == "PUMP"

        # Ungültige Zeichen werden entfernt
        assert InputSanitizer.validate_device_key("PUMP-1") == "PUMP_1"

    def test_validate_device_key_too_long(self):
        """Test dass zu lange Device-Keys abgelehnt werden."""
        long_key = "A" * 60
        with pytest.raises(ValueError, match="zu lang"):
            InputSanitizer.validate_device_key(long_key)

    def test_validate_api_parameter(self):
        """Test dass API-Parameter korrekt validiert werden."""
        # Valid parameters
        assert InputSanitizer.validate_api_parameter("temperature") == "temperature"
        assert InputSanitizer.validate_api_parameter("pump_speed") == "pump_speed"
        assert InputSanitizer.validate_api_parameter("pH-value") == "pH-value"

        # Ungültige Zeichen werden entfernt
        assert InputSanitizer.validate_api_parameter("test<>") == "test"

    def test_validate_api_parameter_path_traversal(self):
        """Test dass Path Traversal verhindert wird."""
        with pytest.raises(ValueError, match="Path Traversal"):
            InputSanitizer.validate_api_parameter("../../../etc/passwd")

        with pytest.raises(ValueError, match="Path Traversal"):
            InputSanitizer.validate_api_parameter("..\\..\\windows\\system32")

    def test_validate_api_parameter_too_long(self):
        """Test dass zu lange Parameter abgelehnt werden."""
        long_param = "a" * 150
        with pytest.raises(ValueError, match="zu lang"):
            InputSanitizer.validate_api_parameter(long_param)
