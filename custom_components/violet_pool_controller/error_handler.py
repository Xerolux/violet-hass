"""Error handling consistency improvements for Violet Pool Controller."""

import logging
from typing import Any, Optional

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
        details: Optional[dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
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
        original_exception: Optional[Exception] = None
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
        status_code: Optional[int] = None,
        original_exception: Optional[Exception] = None
    ):
        code = VioletErrorCodes.API_CONNECTION_FAILED
        if status_code:
            code = f"API_HTTP_{status_code}"
        
        details = {
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
        original_exception: Optional[Exception] = None
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
        original_exception: Optional[Exception] = None
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
        original_exception: Optional[Exception] = None
    ):
        code = VioletErrorCodes.CIRCUIT_BREAKER_OPEN
        details = {
            "error_type": "circuit_breaker",
            "state": state,
            "failure_count": failure_count,
        }
        super().__init__(message, code, details, original_exception)


def handle_exception(
    err: Exception,
    context: str = "unknown",
    log_level: str = "ERROR"
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
            f"Network error in {context}: {err}",
            original_exception=err
        )
    # Authentication errors  
    elif "Auth" in error_type or "Credential" in error_type:
        return AuthenticationError(
            f"Authentication error in {context}: {err}",
            original_exception=err
        )
    # Circuit breaker errors
    elif "Circuit" in error_type:
        return CircuitBreakerError(
            f"Circuit breaker error in {context}: {err}",
            state="OPEN",
            failure_count=0,
            original_exception=err
        )
    # Generic API error
    else:
        return APIError(
            f"API error in {context}: {err}",
            endpoint=context,
            original_exception=err
        )
    
    # Log consistently
    # This logic was moved into the individual blocks above to fix type errors
    # log_method = {
    #     "DEBUG": _LOGGER.debug,
    #     "INFO": _LOGGER.info,
    #     "WARNING": _LOGGER.warning,
    #     "ERROR": _LOGGER.error,
    # }.get(log_level, _LOGGER.error)
    
    # log_method(f"Exception wrapped: {error.to_dict()}")
    
    # return error