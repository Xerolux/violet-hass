"""Tests for enhanced error handler."""
import pytest
import asyncio
from unittest.mock import Mock, patch

from custom_components.violet_pool_controller.error_handler import (
    ErrorType,
    ErrorSeverity,
    IntegrationError,
    EnhancedErrorHandler,
    get_enhanced_error_handler,
    VioletErrorCodes,
    NetworkError,
    AuthenticationError,
    APIError,
)


class TestIntegrationError:
    """Test IntegrationError class."""

    def test_integration_error_creation(self):
        """Test creating an IntegrationError."""
        error = IntegrationError(
            error_type=ErrorType.NETWORK_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Test error",
            recoverable=True,
            retry_after=5.0,
        )

        assert error.error_type == ErrorType.NETWORK_ERROR
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.message == "Test error"
        assert error.recoverable is True
        assert error.retry_after == 5.0
        assert error.timestamp > 0

    def test_to_dict(self):
        """Test IntegrationError to_dict conversion."""
        error = IntegrationError(
            error_type=ErrorType.AUTH_ERROR,
            severity=ErrorSeverity.HIGH,
            message="Auth failed",
            recoverable=False,
        )

        result = error.to_dict()

        assert result["type"] == "auth_error"
        assert result["severity"] == "high"
        assert result["message"] == "Auth failed"
        assert result["recoverable"] is False
        assert result["retry_after"] is None
        assert "timestamp" in result


class TestEnhancedErrorHandler:
    """Test EnhancedErrorHandler class."""

    def test_initialization(self):
        """Test error handler initialization."""
        handler = EnhancedErrorHandler()

        assert handler._max_history == 100
        assert handler._consecutive_errors == 0
        assert handler._auth_errors == 0
        assert handler._offline_since is None
        assert len(handler._error_history) == 0

    @pytest.mark.asyncio
    async def test_classify_network_error(self):
        """Test classification of network errors."""
        handler = EnhancedErrorHandler()

        # Simulate aiohttp ClientError
        with patch("custom_components.violet_pool_controller.error_handler.aiohttp") as mock_aiohttp:
            error = mock_aiohttp.ClientError("Connection refused")
            result = handler.classify_error(error)

            assert result.error_type == ErrorType.NETWORK_ERROR
            assert result.severity == ErrorSeverity.MEDIUM
            assert result.recoverable is True
            assert result.retry_after == 5.0

    @pytest.mark.asyncio
    async def test_classify_timeout_error(self):
        """Test classification of timeout errors."""
        handler = EnhancedErrorHandler()

        error = asyncio.TimeoutError("Connection timed out")
        result = handler.classify_error(error)

        assert result.error_type == ErrorType.TIMEOUT_ERROR
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.recoverable is True
        assert result.retry_after == 10.0

    @pytest.mark.asyncio
    async def test_classify_auth_error(self):
        """Test classification of authentication errors."""
        handler = EnhancedErrorHandler()

        auth_error = AuthenticationError("Invalid credentials")
        result = handler.classify_error(auth_error)

        assert result.error_type == ErrorType.AUTH_ERROR
        assert result.severity == ErrorSeverity.HIGH
        assert result.recoverable is False
        assert result.retry_after is None

        # Check auth error counter
        assert handler._auth_errors == 1

    @pytest.mark.asyncio
    async def test_classify_ssl_error(self):
        """Test classification of SSL errors."""
        handler = EnhancedErrorHandler()

        with patch("custom_components.violet_pool_controller.error_handler.aiohttp") as mock_aiohttp:
            # Create a mock ClientError with SSL in message
            error = mock_aiohttp.ClientError("SSL certificate verification failed")
            result = handler.classify_error(error)

            assert result.error_type == ErrorType.SSL_ERROR
            assert result.severity == ErrorSeverity.HIGH
            assert result.recoverable is False

    @pytest.mark.asyncio
    async def test_classify_unknown_error(self):
        """Test classification of unknown errors."""
        handler = EnhancedErrorHandler()

        error = ValueError("Unexpected error")
        result = handler.classify_error(error)

        assert result.error_type == ErrorType.UNKNOWN_ERROR
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.recoverable is True
        assert result.retry_after == 5.0

    def test_record_error(self):
        """Test recording errors in history."""
        handler = EnhancedErrorHandler()

        error = IntegrationError(
            error_type=ErrorType.NETWORK_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Test error",
        )

        handler.record_error(error)

        assert len(handler._error_history) == 1
        assert handler._error_history[0] == error
        assert handler._consecutive_errors == 1
        assert handler._last_error_time > 0

    def test_record_error_offline_tracking(self):
        """Test offline status tracking."""
        handler = EnhancedErrorHandler()

        # Record network error (should trigger offline)
        error1 = IntegrationError(
            error_type=ErrorType.NETWORK_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Network down",
        )
        handler.record_error(error1)

        assert handler._offline_since is not None

        # Record auth error (should not affect offline status)
        error2 = IntegrationError(
            error_type=ErrorType.AUTH_ERROR,
            severity=ErrorSeverity.HIGH,
            message="Auth failed",
        )
        handler.record_error(error2)

        # Offline should still be tracked
        assert handler._offline_since is not None

    def test_get_recent_errors(self):
        """Test getting recent errors."""
        handler = EnhancedErrorHandler()

        # Add 3 errors
        for i in range(3):
            error = IntegrationError(
                error_type=ErrorType.NETWORK_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message=f"Error {i}",
            )
            handler.record_error(error)

        # Get last 2 errors
        recent = handler.get_recent_errors(count=2)

        assert len(recent) == 2
        assert recent[0].message == "Error 1"
        assert recent[1].message == "Error 2"

    def test_get_error_summary(self):
        """Test error summary generation."""
        handler = EnhancedErrorHandler()

        # Add some errors
        error1 = IntegrationError(
            error_type=ErrorType.NETWORK_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Network error",
        )
        error2 = IntegrationError(
            error_type=ErrorType.AUTH_ERROR,
            severity=ErrorSeverity.HIGH,
            message="Auth error",
        )

        handler.record_error(error1)
        handler.record_error(error2)

        summary = handler.get_error_summary()

        assert summary["total_errors"] == 2
        assert summary["consecutive_errors"] == 2
        assert summary["auth_errors"] == 1
        assert summary["is_offline"] is True
        assert "error_counts" in summary
        assert summary["error_counts"]["network_error"] == 1
        assert summary["error_counts"]["auth_error"] == 1

    def test_clear_history(self):
        """Test clearing error history."""
        handler = EnhancedErrorHandler()

        # Add errors
        error = IntegrationError(
            error_type=ErrorType.NETWORK_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Test",
        )
        handler.record_error(error)

        assert len(handler._error_history) > 0
        assert handler._consecutive_errors > 0

        handler.clear_history()

        assert len(handler._error_history) == 0
        assert handler._consecutive_errors == 0
        assert handler._offline_since is None

    def test_should_trigger_reauth(self):
        """Test re-authentication trigger detection."""
        handler = EnhancedErrorHandler()

        # Add 2 auth errors
        for _ in range(2):
            error = IntegrationError(
                error_type=ErrorType.AUTH_ERROR,
                severity=ErrorSeverity.HIGH,
                message="Auth failed",
            )
            handler.record_error(error)

        assert handler.should_trigger_reauth() is True

        # Clear and test with only 1 auth error
        handler.clear_history()

        error = IntegrationError(
            error_type=ErrorType.AUTH_ERROR,
            severity=ErrorSeverity.HIGH,
            message="Auth failed",
        )
        handler.record_error(error)

        assert handler.should_trigger_reauth() is False

    def test_get_recovery_suggestion_auth(self):
        """Test recovery suggestion for auth errors."""
        handler = EnhancedErrorHandler()

        error = IntegrationError(
            error_type=ErrorType.AUTH_ERROR,
            severity=ErrorSeverity.HIGH,
            message="Auth failed",
        )
        handler.record_error(error)

        suggestion = handler.get_recovery_suggestion()

        assert "re-authenticate" in suggestion.lower()
        assert "settings" in suggestion.lower()

    def test_get_recovery_suggestion_network(self):
        """Test recovery suggestion for network errors."""
        handler = EnhancedErrorHandler()

        error = IntegrationError(
            error_type=ErrorType.NETWORK_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Network error",
        )
        handler.record_error(error)

        suggestion = handler.get_recovery_suggestion()

        assert "controller" in suggestion.lower()
        assert "powered" in suggestion.lower()

    def test_get_recovery_suggestion_timeout(self):
        """Test recovery suggestion for timeout errors."""
        handler = EnhancedErrorHandler()

        error = IntegrationError(
            error_type=ErrorType.TIMEOUT_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message="Timeout",
        )
        handler.record_error(error)

        suggestion = handler.get_recovery_suggestion()

        assert "not responding" in suggestion.lower()

    def test_get_recovery_suggestion_none(self):
        """Test recovery suggestion when no errors."""
        handler = EnhancedErrorHandler()

        suggestion = handler.get_recovery_suggestion()

        assert suggestion is None


class TestGlobalErrorHandler:
    """Test global error handler instance."""

    def test_get_enhanced_error_handler_singleton(self):
        """Test that get_enhanced_error_handler returns singleton."""
        handler1 = get_enhanced_error_handler()
        handler2 = get_enhanced_error_handler()

        assert handler1 is handler2


class TestLegacyErrorClasses:
    """Test legacy error classes for backward compatibility."""

    def test_network_error_creation(self):
        """Test NetworkError creation."""
        error = NetworkError("Connection failed")

        assert error.code == VioletErrorCodes.NETWORK_CONNECTION_ERROR
        assert "Connection failed" in error.message
        assert error.details["error_type"] == "network"

    def test_authentication_error_creation(self):
        """Test AuthenticationError creation."""
        error = AuthenticationError("Invalid credentials")

        assert error.code == VioletErrorCodes.AUTH_INVALID_CREDENTIALS
        assert error.details["error_type"] == "authentication"

    def test_api_error_creation(self):
        """Test APIError creation."""
        error = APIError("API failed", endpoint="/test", status_code=500)

        assert "API_HTTP_500" in error.code
        assert error.details["endpoint"] == "/test"
        assert error.details["status_code"] == 500

    def test_error_to_dict(self):
        """Test error to_dict conversion."""
        error = NetworkError("Test error")

        result = error.to_dict()

        assert "code" in result
        assert "message" in result
        assert "details" in result
