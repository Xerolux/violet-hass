"""Tests for violet_poolcontroller_api.parsers module."""

from datetime import UTC, datetime, timedelta

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
        """Parse valid controller runtime formats."""
        assert parse_runtime_string("5m 30s") == timedelta(minutes=5, seconds=30)
        assert parse_runtime_string("1h 30m 45s") == timedelta(hours=1, minutes=30, seconds=45)
        assert parse_runtime_string("1d 04h 33m 12s") == timedelta(
            days=1, hours=4, minutes=33, seconds=12
        )

    def test_invalid_runtime_string(self):
        """Invalid runtime strings produce a zero duration."""
        assert parse_runtime_string("invalid") == timedelta(0)
        assert parse_runtime_string("") == timedelta(0)


class TestParseHmsString:
    """Test parse_hms_string parser."""

    def test_valid_hms_string(self):
        """Parse valid HH:MM:SS format."""
        assert parse_hms_string("01:30:45") == timedelta(hours=1, minutes=30, seconds=45)
        assert parse_hms_string("00:00:01") == timedelta(seconds=1)
        assert parse_hms_string("23:59:59") == timedelta(hours=23, minutes=59, seconds=59)

    def test_edge_cases(self):
        """Handle an all-zero duration."""
        assert parse_hms_string("00:00:00") == timedelta(0)

    def test_invalid_hms(self):
        """Invalid HMS strings produce a zero duration."""
        assert parse_hms_string("invalid") == timedelta(0)


class TestParseUptimeString:
    """Test parse_uptime_string parser."""

    def test_valid_uptime_formats(self):
        """Parse the controller uptime format."""
        assert parse_uptime_string("5d 3h 45m") == timedelta(days=5, hours=3, minutes=45)

    def test_uptime_with_days(self):
        """Parse uptime containing only days."""
        assert parse_uptime_string("365d") == timedelta(days=365)

    def test_invalid_uptime(self):
        """Invalid uptime strings produce a zero duration."""
        assert parse_uptime_string("invalid") == timedelta(0)


class TestParseOptionalSeconds:
    """Test parse_optional_seconds parser."""

    def test_valid_seconds(self):
        """Parse valid second values."""
        assert parse_optional_seconds("120") == timedelta(seconds=120)
        assert parse_optional_seconds("0") == timedelta(0)
        assert parse_optional_seconds(3600) == timedelta(hours=1)

    def test_none_sentinel(self):
        """Handle the NONE sentinel value."""
        assert parse_optional_seconds("NONE") is None

    def test_invalid_seconds(self):
        """Reject invalid seconds."""
        assert parse_optional_seconds("invalid") is None


class TestParseEpochSeconds:
    """Test parse_epoch_seconds parser."""

    def test_valid_epoch(self):
        """Parse a valid epoch timestamp in seconds."""
        assert parse_epoch_seconds("1609459200") == datetime(2021, 1, 1, tzinfo=UTC)

    def test_zero_epoch(self):
        """Treat zero as the controller's unset sentinel."""
        assert parse_epoch_seconds("0") is None

    def test_invalid_epoch(self):
        """Reject invalid epoch values."""
        assert parse_epoch_seconds("invalid") is None


class TestParseEpochMilliseconds:
    """Test parse_epoch_milliseconds parser."""

    def test_valid_epoch_ms(self):
        """Parse a valid epoch timestamp in milliseconds."""
        assert parse_epoch_milliseconds("1609459200000") == datetime(2021, 1, 1, tzinfo=UTC)

    def test_zero_epoch_ms(self):
        """Treat zero as the controller's unset sentinel."""
        assert parse_epoch_milliseconds("0") is None

    def test_invalid_epoch_ms(self):
        """Reject invalid epoch values."""
        assert parse_epoch_milliseconds("invalid") is None


class TestParserEdgeCases:
    """Test edge cases across all parsers."""

    def test_empty_string(self):
        """Parsers handle empty strings according to their return contract."""
        assert parse_runtime_string("") == timedelta(0)
        assert parse_hms_string("") == timedelta(0)
        assert parse_uptime_string("") == timedelta(0)
        assert parse_optional_seconds("") is None
        assert parse_epoch_seconds("") is None
        assert parse_epoch_milliseconds("") is None

    def test_none_input_for_numeric_parsers(self):
        """Numeric parsers reject missing values gracefully."""
        assert parse_optional_seconds(None) is None
        assert parse_epoch_seconds(None) is None
        assert parse_epoch_milliseconds(None) is None

    def test_whitespace_handling(self):
        """Runtime parsers ignore surrounding whitespace."""
        assert parse_runtime_string("  5m 30s  ") == timedelta(minutes=5, seconds=30)
