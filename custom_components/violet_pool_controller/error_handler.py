
"""Error handling utilities for Violet Pool Controller integration."""
from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class VioletErrorCodes:
    """Consistent error codes for all integration errors."""

    # Network errors
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    NETWORK_CONNECTION_ERROR = "NETWORK_CONNECTION_ERROR"
    NETWORK_DNS_ERROR = "NETWORK_DNS_ERROR"
    NETWORK_SSL_ERROR = "NETWORK_SSL_ERROR"

    # API errors
    API_TIMEOUT = "API_TIMEOUT"
    API_CONNECTION_FAILED = "API_CONNECTION_FAILED"
    API_RATE_LIMITED = "API_RATE_LIMITED"
    API_INVALID_RESPONSE = "API_INVALID_RESPONSE"
    API_JSON_DECODE_ERROR = "API_JSON_DECODE_ERROR"

    # Authentication errors
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_WEAK_PASSWORD = "AUTH_WEAK_PASSWORD"
    AUTH_USERNAME_TOO_SHORT = "AUTH_USERNAME_TOO_SHORT"
    AUTH_SESSION_EXPIRED = "AUTH_SESSION_EXPIRED"

    # Configuration errors
    CONFIG_INVALID_PARAMETER = "CONFIG_INVALID_PARAMETER"
    CONFIG_MISSING_REQUIRED = "CONFIG_MISSING_REQUIRED"
    CONFIG_INVALID_FORMAT = "CONFIG_INVALID_FORMAT"

    # Controller errors
    CONTROLLER_OFFLINE = "CONTROLLER_OFFLINE"
    CONTROLLER_UNRESPONSIVE = "CONTROLLER_UNRESPONSIVE"
    CONTROLLER_ERROR = "CONTROLLER_ERROR"

    # Circuit breaker errors
    CIRCUIT_BREAKER_OPEN = "CIRCUIT_BREAKER_OPEN"
    CIRCUIT_BREAKER_TIMEOUT = "CIRCUIT_BREAKER_TIMEOUT"


class VioletPoolControllerError(Exception):
    """Base exception class for all Violet Pool Controller errors."""

    def __init__(
        self,
        message: str,
        code: str,
        details: dict[str, Any] | None = None,
        original_exception: Exception | None = None,
    ):
        """
        Initialize error with consistent structure.

        Args:
            message: Human-readable error message.
            code: Machine-readable error code.
            details: Additional error details.
            original_exception: Original exception if wrapping.
        """
        self.message = message
        self.code = code
        self.details = details or {}
        self.original_exception = original_exception

        super().__init__(message)

    def __str__(self) -> str:
        """String representation."""
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class NetworkError(VioletPoolControllerError):
    """Network-related errors."""

    def __init__(
        self,
        message: str,
        code: str = VioletErrorCodes.NETWORK_CONNECTION_ERROR,
        original_exception: Exception | None = None,
    ):
        details = {
            "error_type": "network",
        }
        if original_exception:
            details["exception_type"] = type(original_exception).__name__

        super().__init__(message, code, details, original_exception)


class APIError(VioletPoolControllerError):
    """API-related errors."""

    def __init__(
        self,
        message: str,
        endpoint: str,
        status_code: int | None = None,
        original_exception: Exception | None = None,
    ):
        code = VioletErrorCodes.API_CONNECTION_FAILED
        if status_code:
            code = f"API_HTTP_{status_code}"

        details: dict[str, Any] = {
            "error_type": "api",
            "endpoint": endpoint,
        }
        if status_code:
            details["status_code"] = status_code

        super().__init__(message, code, details, original_exception)


class AuthenticationError(VioletPoolControllerError):
    """Authentication-related errors."""

    def __init__(
        self,
        message: str,
        code: str = VioletErrorCodes.AUTH_INVALID_CREDENTIALS,
        original_exception: Exception | None = None,
    ):
        details = {
            "error_type": "authentication",
        }
        super().__init__(message, code, details, original_exception)


class ValidationError(VioletPoolControllerError):
    """Input validation errors."""

    def __init__(
        self,
        message: str,
        parameter_name: str,
        value: Any,
        original_exception: Exception | None = None,
    ):
        code = VioletErrorCodes.CONFIG_INVALID_PARAMETER
        details = {
            "error_type": "validation",
            "parameter_name": parameter_name,
            "value": str(value)[:100],  # Truncate long values
        }
        super().__init__(message, code, details, original_exception)


class CircuitBreakerError(VioletPoolControllerError):
    """Circuit breaker errors."""

    def __init__(
        self,
        message: str,
        state: str,
        failure_count: int,
        original_exception: Exception | None = None,
    ):
        code = VioletErrorCodes.CIRCUIT_BREAKER_OPEN
        details = {
            "error_type": "circuit_breaker",
            "state": state,
            "failure_count": failure_count,
        }
        super().__init__(message, code, details, original_exception)


def handle_exception(
    err: Exception, context: str = "unknown", log_level: str = "ERROR"
) -> VioletPoolControllerError:
    """
    Consistent exception handling wrapper.

    Args:
        err: Original exception to wrap.
        context: Context where error occurred.
        log_level: Log level (DEBUG, INFO, WARNING, ERROR).

    Returns:
        Consistent error object.
    """
    # Already wrapped?
    if isinstance(err, VioletPoolControllerError):
        return err

    # Categorize and wrap exception
    error_type = type(err).__name__

    # Network errors
    if "Timeout" in error_type or "Connection" in error_type:
        return NetworkError(
            f"Network error in {context}: {err}", original_exception=err
        )
    # Authentication errors
    elif "Auth" in error_type or "Credential" in error_type:
        return AuthenticationError(
            f"Authentication error in {context}: {err}", original_exception=err
        )
    # Circuit breaker errors
    elif "Circuit" in error_type:
        return CircuitBreakerError(
            f"Circuit breaker error in {context}: {err}",
            state="OPEN",
            failure_count=0,
            original_exception=err,
        )
    # Generic API error
    else:
        return APIError(
            f"API error in {context}: {err}", endpoint=context, original_exception=err
        )


# =============================================================================
# ENHANCED ERROR HANDLING (Silver Level)
# =============================================================================


class ErrorType(Enum):
    """Classification of errors that can occur."""

    NETWORK_ERROR = "network_error"
    AUTH_ERROR = "auth_error"
    TIMEOUT_ERROR = "timeout_error"
    SSL_ERROR = "ssl_error"
    SERVER_ERROR = "server_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(Enum):
    """Severity levels for errors."""

    LOW = "low"  # Transient errors, auto-recoverable
    MEDIUM = "medium"  # Requires user attention
    HIGH = "high"  # Critical, immediate action needed


class IntegrationError:
    """Structured error information for better error handling."""

    def __init__(
        self,
        error_type: ErrorType,
        severity: ErrorSeverity,
        message: str,
        recoverable: bool = True,
        retry_after: float | None = None,
    ) -> None:
        """Initialize error information.

        Args:
            error_type: The type of error.
            severity: The severity level.
            message: Human-readable error message.
            recoverable: Whether the error is automatically recoverable.
            retry_after: Suggested retry delay in seconds.
        """
        self.error_type = error_type
        self.severity = severity
        self.message = message
        self.recoverable = recoverable
        self.retry_after = retry_after
        self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for logging/sensors.

        Returns:
            Dictionary representation of the error.
        """
        return {
            "type": self.error_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "recoverable": self.recoverable,
            "retry_after": self.retry_after,
            "timestamp": self.timestamp,
        }


class EnhancedErrorHandler:
    """Enhanced error handling with offline resilience and auto-recovery."""

    def __init__(self) -> None:
        """Initialize enhanced error handler."""
        self._error_history: list[IntegrationError] = []
        self._max_history = 100
        self._consecutive_errors = 0
        self._last_error_time = 0.0
        self._offline_since: float | None = None
        self._auth_errors = 0

    def classify_error(self, error: Exception) -> IntegrationError:
        """Classify an error and determine appropriate handling.

        Args:
            error: The exception that occurred.

        Returns:
            An IntegrationError with classification and handling info.
        """
        # Authentication errors (401, 403)
        if isinstance(error, aiohttp.ClientResponseError):
            if error.status in (401, 403):
                self._auth_errors += 1
                return IntegrationError(
                    error_type=ErrorType.AUTH_ERROR,
                    severity=ErrorSeverity.HIGH,
                    message=f"Authentication failed: {error.message}",
                    recoverable=False,  # Requires user intervention
                    retry_after=None,
                )

            # Server errors (5xx)
            if error.status >= 500:
                return IntegrationError(
                    error_type=ErrorType.SERVER_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    message=f"Server error: HTTP {error.status}",
                    recoverable=True,
                    retry_after=30.0,  # Suggest 30s retry
                )

            # Rate limiting (429)
            if error.status == 429:
                return IntegrationError(
                    error_type=ErrorType.RATE_LIMIT_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    message="Rate limit exceeded, please wait",
                    recoverable=True,
                    retry_after=60.0,  # Suggest 60s retry
                )

        # Network errors (connection refused, timeout, DNS failure)
        if isinstance(error, (aiohttp.ClientError, asyncio.TimeoutError)):
            error_str = str(error).lower()

            # SSL certificate errors
            if "ssl" in error_str or "certificate" in error_str:
                return IntegrationError(
                    error_type=ErrorType.SSL_ERROR,
                    severity=ErrorSeverity.HIGH,
                    message=f"SSL certificate error: {error}",
                    recoverable=False,
                    retry_after=None,
                )

            # Timeout errors
            if isinstance(error, asyncio.TimeoutError) or "timeout" in error_str:
                return IntegrationError(
                    error_type=ErrorType.TIMEOUT_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    message=f"Connection timeout: {error}",
                    recoverable=True,
                    retry_after=10.0,  # Suggest 10s retry
                )

            # General network errors
            return IntegrationError(
                error_type=ErrorType.NETWORK_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message=f"Network error: {error}",
                recoverable=True,
                retry_after=5.0,  # Suggest 5s retry
            )

        # Our own API errors
        if isinstance(error, VioletPoolControllerError):
            error_str = str(error).lower()

            if "authentication" in error_str or "unauthorized" in error_str:
                self._auth_errors += 1
                return IntegrationError(
                    error_type=ErrorType.AUTH_ERROR,
                    severity=ErrorSeverity.HIGH,
                    message=f"API authentication failed: {error}",
                    recoverable=False,
                    retry_after=None,
                )

            if "timeout" in error_str:
                return IntegrationError(
                    error_type=ErrorType.TIMEOUT_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    message=f"API timeout: {error}",
                    recoverable=True,
                    retry_after=10.0,
                )

            return IntegrationError(
                error_type=ErrorType.SERVER_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message=f"API error: {error}",
                recoverable=True,
                retry_after=5.0,
            )

        # Unknown errors
        return IntegrationError(
            error_type=ErrorType.UNKNOWN_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message=f"Unexpected error: {error}",
            recoverable=True,
            retry_after=5.0,
        )

    def record_error(self, error_info: IntegrationError) -> None:
        """Record an error in the history.

        Args:
            error_info: The error to record.
        """
        self._error_history.append(error_info)

        # Keep history at max size
        if len(self._error_history) > self._max_history:
            self._error_history.pop(0)

        # Update consecutive error counter
        now = time.time()
        if now - self._last_error_time < 60:  # Errors within 60 seconds
            self._consecutive_errors += 1
        else:
            self._consecutive_errors = 1

        self._last_error_time = now

        # Track offline status
        if error_info.error_type in (
            ErrorType.NETWORK_ERROR,
            ErrorType.TIMEOUT_ERROR,
            ErrorType.SERVER_ERROR,
        ):
            if self._offline_since is None:
                self._offline_since = now
                _LOGGER.warning(
                    "Controller marked as OFFLINE (error: %s)", error_info.message
                )
        else:
            self._offline_since = None

    def get_recent_errors(self, count: int = 10) -> list[IntegrationError]:
        """Get the most recent errors.

        Args:
            count: Maximum number of errors to return.

        Returns:
            List of recent errors.
        """
        return self._error_history[-count:]

    def get_error_summary(self) -> dict[str, Any]:
        """Get a summary of error statistics.

        Returns:
            Dictionary with error statistics.
        """
        # Count errors by type
        error_counts: dict[ErrorType, int] = {}
        for error in self._error_history:
            error_counts[error.error_type] = error_counts.get(error.error_type, 0) + 1

        # Calculate offline duration
        offline_duration = 0.0
        if self._offline_since:
            offline_duration = time.time() - self._offline_since

        return {
            "total_errors": len(self._error_history),
            "consecutive_errors": self._consecutive_errors,
            "auth_errors": self._auth_errors,
            "offline_duration_seconds": offline_duration,
            "is_offline": self._offline_since is not None,
            "error_counts": {k.value: v for k, v in error_counts.items()},
            "last_error": (
                self._error_history[-1].to_dict() if self._error_history else None
            ),
        }

    def clear_history(self) -> None:
        """Clear error history (e.g., after successful recovery)."""
        self._error_history.clear()
        self._consecutive_errors = 0
        self._offline_since = None
        _LOGGER.debug("Error history cleared")

    def should_trigger_reauth(self) -> bool:
        """Determine if re-authentication flow should be triggered.

        Returns:
            True if re-authentication is needed.
        """
        # Trigger if we've had multiple recent auth errors
        recent_auth_errors = sum(
            1
            for e in self._error_history[-10:]
            if e.error_type == ErrorType.AUTH_ERROR
        )

        return recent_auth_errors >= 2

    def get_recovery_suggestion(self) -> str | None:
        """Get a suggested recovery action based on recent errors.

        Returns:
            Human-readable recovery suggestion or None.
        """
        if not self._error_history:
            return None

        last_error = self._error_history[-1]

        if last_error.error_type == ErrorType.AUTH_ERROR:
            return "Please re-authenticate via Settings > Devices & Services > Configure"

        if last_error.error_type == ErrorType.NETWORK_ERROR:
            return "Check if the controller is powered on and connected to the network"

        if last_error.error_type == ErrorType.TIMEOUT_ERROR:
            return "The controller is not responding. Check network connectivity and controller status"

        if last_error.error_type == ErrorType.SSL_ERROR:
            return "SSL certificate verification failed. Check certificate configuration or disable SSL verification for testing"

        if last_error.error_type == ErrorType.RATE_LIMIT_ERROR:
            return "Too many requests. Please wait before trying again"

        if last_error.error_type == ErrorType.SERVER_ERROR:
            return "The controller is experiencing issues. Check controller logs and status"

        return None


# Global enhanced error handler instance
_enhanced_error_handler: EnhancedErrorHandler | None = None


def get_enhanced_error_handler() -> EnhancedErrorHandler:
    """Get the global enhanced error handler instance.

    Returns:
        The global EnhancedErrorHandler instance.
    """
    global _enhanced_error_handler
    if _enhanced_error_handler is None:
        _enhanced_error_handler = EnhancedErrorHandler()
    return _enhanced_error_handler

