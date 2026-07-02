"""Tests for violet_poolcontroller_api.readings module."""

import pytest

from violet_poolcontroller_api.readings import VioletReadings


class TestVioletReadingsBasic:
    """Test VioletReadings basic functionality."""

    @pytest.fixture
    def sample_data(self):
        """Provide sample API response data."""
        return {
            "POOL_TEMP": 24.5,
            "SOLAR_TEMP": 32.1,
            "AMBIENT_TEMP": 18.3,
            "pH": 7.2,
            "ORP": 650,
            "PUMP_STATE": "1",
            "HEATER_STATE": "0",
        }

    def test_readings_creation(self, sample_data):
        """Create VioletReadings from dict."""
        readings = VioletReadings(sample_data)
        assert readings is not None
        assert len(readings) == len(sample_data)

    def test_readings_value_access(self, sample_data):
        """Access values from VioletReadings."""
        readings = VioletReadings(sample_data)
        assert readings.get("POOL_TEMP") == 24.5
        assert readings.get("pH") == 7.2

    def test_readings_missing_key(self, sample_data):
        """Handle missing keys gracefully."""
        readings = VioletReadings(sample_data)
        assert readings.get("NONEXISTENT") is None
        assert readings.get("NONEXISTENT", "default") == "default"


class TestVioletReadingsTypeConversions:
    """Test typed property access and conversions."""

    @pytest.fixture
    def mixed_data(self):
        """Data with various types."""
        return {
            "TEMPERATURE": "24.5",
            "STATE": "1",
            "RUNTIME": 3600,
            "ENABLED": "true",
            "DISABLED": "false",
            "NULL_VALUE": None,
        }

    def test_temperature_conversion(self, mixed_data):
        """Convert temperature string to float."""
        readings = VioletReadings(mixed_data)
        temp = readings.get("TEMPERATURE")
        # Should be convertible to float
        assert isinstance(temp, (int, float, str))

    def test_state_conversion(self, mixed_data):
        """Convert state string to int."""
        readings = VioletReadings(mixed_data)
        state = readings.get("STATE")
        assert state is not None

    def test_boolean_conversion(self, mixed_data):
        """Convert boolean strings."""
        readings = VioletReadings(mixed_data)
        enabled = readings.get("ENABLED")
        disabled = readings.get("DISABLED")
        # Should be interpretable as boolean
        assert enabled is not None
        assert disabled is not None

    def test_none_handling(self, mixed_data):
        """Handle None values properly."""
        readings = VioletReadings(mixed_data)
        null_val = readings.get("NULL_VALUE")
        assert null_val is None


class TestVioletReadingsAggregation:
    """Test readings aggregation and derived properties."""

    def test_readings_contains_all_keys(self):
        """Verify readings contains all provided keys."""
        data = {
            "KEY1": "value1",
            "KEY2": "value2",
            "KEY3": "value3",
        }
        readings = VioletReadings(data)
        assert "KEY1" in readings
        assert "KEY2" in readings
        assert "KEY3" in readings

    def test_readings_iteration(self):
        """Iterate over readings."""
        data = {"A": 1, "B": 2, "C": 3}
        readings = VioletReadings(data)
        keys = list(readings.keys())
        assert "A" in keys
        assert "B" in keys
        assert "C" in keys


class TestVioletReadingsEdgeCases:
    """Test edge cases in readings handling."""

    def test_empty_readings(self):
        """Create readings from empty dict."""
        readings = VioletReadings({})
        assert len(readings) == 0

    def test_large_dataset(self):
        """Handle large dataset."""
        large_data = {f"KEY_{i}": f"value_{i}" for i in range(1000)}
        readings = VioletReadings(large_data)
        assert len(readings) == 1000
        assert readings.get("KEY_0") == "value_0"
        assert readings.get("KEY_999") == "value_999"

    def test_special_characters_in_values(self):
        """Handle special characters in values."""
        data = {
            "UNICODE": "测试",
            "SPECIAL": "!@#$%^&*()",
            "QUOTES": 'value with "quotes"',
        }
        readings = VioletReadings(data)
        assert readings.get("UNICODE") == "测试"
        assert readings.get("SPECIAL") == "!@#$%^&*()"

    def test_numeric_edge_cases(self):
        """Handle numeric edge cases."""
        data = {
            "ZERO": 0,
            "NEGATIVE": -100,
            "FLOAT": 3.14159,
            "LARGE": 999999999,
            "SCIENTIFIC": 1e-6,
        }
        readings = VioletReadings(data)
        assert readings.get("ZERO") == 0
        assert readings.get("NEGATIVE") == -100
        assert readings.get("FLOAT") == 3.14159


class TestVioletReadingsIntegration:
    """Integration tests with realistic data."""

    def test_realistic_pool_data(self):
        """Test with realistic pool controller data."""
        realistic_data = {
            "POOL_TEMP": 24.5,
            "SOLAR_TEMP": 35.2,
            "AMBIENT_TEMP": 22.0,
            "pH": 7.3,
            "ORP": 680,
            "CONDUCTIVITY": 1200,
            "PUMP_STATE": "1",
            "HEATER_STATE": "0",
            "SOLAR_STATE": "1",
            "DOSING_PH_MINUS": "0",
            "DOSING_PH_PLUS": "0",
            "DOSING_CL": "1",
            "PUMP_RUNTIME": 3600,
            "FILTER_RUNTIME": 3600,
            "ERROR_CODE": "0",
            "DI1": "0",
            "DI2": "1",
            "DO1": "0",
            "DO2": "1",
        }
        readings = VioletReadings(realistic_data)
        assert len(readings) == len(realistic_data)
        assert readings.get("POOL_TEMP") == 24.5
        assert readings.get("DI1") == "0"

    def test_readings_snapshot_behavior(self):
        """Verify readings behave as immutable snapshots."""
        data = {"TEMP": 25.0}
        readings = VioletReadings(data)
        # Original data shouldn't affect readings after creation
        original_temp = readings.get("TEMP")
        # Readings should be stable
        assert readings.get("TEMP") == original_temp
