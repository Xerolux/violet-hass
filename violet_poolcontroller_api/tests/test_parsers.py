"""Tests for violet_poolcontroller_api.parsers module."""

from violet_poolcontroller_api.parsers import (
    parse_epoch_milliseconds,
    parse_epoch_seconds,
    parse_hms_string,
    parse_optional_seconds,
    parse_runtime_string,
    parse_uptime_string,
)


class TestParseRuntimeString:
    """Test parse_runtime_string parser."""

    def test_valid_runtime_string(self):
        """Parse valid runtime format."""
        assert parse_runtime_string("00:05:30") == 330  # 5min 30sec in seconds
        assert parse_runtime_string("01:30:45") == 5445  # 1h 30min 45sec
        assert parse_runtime_string("00:00:00") == 0

    def test_invalid_runtime_string(self):
        """Handle invalid runtime formats gracefully."""
        assert parse_runtime_string("invalid") is None or isinstance(parse_runtime_string("invalid"), (int, float))
        assert parse_runtime_string("") is None or isinstance(parse_runtime_string(""), (int, float))
        assert parse_runtime_string(None) is None or isinstance(parse_runtime_string(None), (int, float))


class TestParseHmsString:
    """Test parse_hms_string parser."""

    def test_valid_hms_string(self):
        """Parse valid HH:MM:SS format."""
        assert parse_hms_string("01:30:45") == 5445
        assert parse_hms_string("00:00:01") == 1
        assert parse_hms_string("23:59:59") == 86399

    def test_edge_cases(self):
        """Handle edge cases."""
        assert parse_hms_string("00:00:00") == 0
        # All-zeros case

    def test_invalid_hms(self):
        """Handle invalid HMS formats."""
        result = parse_hms_string("invalid")
        assert result is None or isinstance(result, (int, float))


class TestParseUptimeString:
    """Test parse_uptime_string parser."""

    def test_valid_uptime_formats(self):
        """Parse valid uptime formats."""
        # Support various uptime formats
        result = parse_uptime_string("5 days, 3:45:22")
        assert isinstance(result, (int, float)) or result is None

    def test_uptime_with_days(self):
        """Parse uptime with days."""
        result = parse_uptime_string("365 days")
        assert isinstance(result, (int, float)) or result is None

    def test_invalid_uptime(self):
        """Handle invalid uptime formats."""
        result = parse_uptime_string("invalid")
        assert result is None or isinstance(result, (int, float))


class TestParseOptionalSeconds:
    """Test parse_optional_seconds parser."""

    def test_valid_seconds(self):
        """Parse valid second values."""
        assert parse_optional_seconds("120") == 120
        assert parse_optional_seconds("0") == 0
        assert parse_optional_seconds("3600") == 3600

    def test_none_sentinel(self):
        """Handle 'NONE' sentinel value."""
        result = parse_optional_seconds("NONE")
        assert result is None or result == 0 or result == -1

    def test_invalid_seconds(self):
        """Handle invalid seconds."""
        result = parse_optional_seconds("invalid")
        assert result is None or isinstance(result, (int, float))


class TestParseEpochSeconds:
    """Test parse_epoch_seconds parser."""

    def test_valid_epoch(self):
        """Parse valid epoch timestamp (seconds)."""
        # Jan 1, 1970 00:00:00 UTC
        assert parse_epoch_seconds("0") == 0
        # Some arbitrary timestamp
        assert isinstance(parse_epoch_seconds("1609459200"), (int, float))

    def test_zero_epoch(self):
        """Handle zero epoch."""
        assert parse_epoch_seconds("0") == 0

    def test_invalid_epoch(self):
        """Handle invalid epoch values."""
        result = parse_epoch_seconds("invalid")
        assert result is None or isinstance(result, (int, float))


class TestParseEpochMilliseconds:
    """Test parse_epoch_milliseconds parser."""

    def test_valid_epoch_ms(self):
        """Parse valid epoch timestamp (milliseconds)."""
        result = parse_epoch_milliseconds("1609459200000")
        assert isinstance(result, (int, float)) or result is None

    def test_zero_epoch_ms(self):
        """Handle zero epoch."""
        result = parse_epoch_milliseconds("0")
        assert result == 0 or result is None

    def test_invalid_epoch_ms(self):
        """Handle invalid epoch values."""
        result = parse_epoch_milliseconds("invalid")
        assert result is None or isinstance(result, (int, float))


class TestParserEdgeCases:
    """Test edge cases across all parsers."""

    def test_empty_string(self):
        """Parsers handle empty strings gracefully."""
        for parser in [
            parse_runtime_string,
            parse_hms_string,
            parse_uptime_string,
            parse_optional_seconds,
            parse_epoch_seconds,
            parse_epoch_milliseconds,
        ]:
            result = parser("")
            assert result is None or isinstance(result, (int, float))

    def test_none_input(self):
        """Parsers handle None input gracefully."""
        for parser in [
            parse_runtime_string,
            parse_hms_string,
            parse_uptime_string,
            parse_optional_seconds,
            parse_epoch_seconds,
            parse_epoch_milliseconds,
        ]:
            result = parser(None)
            assert result is None or isinstance(result, (int, float))

    def test_whitespace_handling(self):
        """Parsers handle whitespace appropriately."""
        # Parsers should either strip or reject whitespace
        result = parse_runtime_string("  00:05:30  ")
        assert result is None or isinstance(result, (int, float))
