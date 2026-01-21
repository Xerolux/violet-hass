"""Circuit breaker implementation for resilient API calls."""

import logging
import time
from typing import Any, Callable

_LOGGER = logging.getLogger(__name__)

class CircuitBreakerState:
    """Circuit breaker states."""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Circuit is open, calls fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker pattern for API calls with automatic recovery.
    
    Protects against cascading failures when the controller or network is down.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        recovery_timeout: float = 300.0,
        expected_exception: type = Exception,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: How long to keep circuit open (seconds)
            recovery_timeout: How long to stay in half-open state
            expected_exception: Exception type to consider for failures
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = CircuitBreakerState.CLOSED
        self.half_open_start_time = 0.0
        
        _LOGGER.debug(
            "Circuit breaker initialized: threshold=%d, timeout=%.1fs, recovery=%.1fs",
            failure_threshold,
            timeout,
            recovery_timeout,
        )

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: The async function to call
            *args: Arguments to pass to function
            **kwargs: Keyword arguments to pass to function

        Returns:
            Result of function call

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        current_time = time.time()
        
        # Check if circuit should be closed from timeout
        if (self.state == CircuitBreakerState.OPEN and 
            current_time - self.last_failure_time > self.timeout):
            self.state = CircuitBreakerState.HALF_OPEN
            self.half_open_start_time = current_time
            _LOGGER.info("Circuit breaker entering HALF_OPEN state for recovery test")
        
        # Check if half-open timeout exceeded
        if (self.state == CircuitBreakerState.HALF_OPEN and
            current_time - self.half_open_start_time > self.recovery_timeout):
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            _LOGGER.info("Circuit breaker recovered to CLOSED state")
        
        # Fail fast if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Success: reset failure count and close circuit if half-open
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                _LOGGER.info("Circuit breaker recovered from HALF_OPEN to CLOSED")
            else:
                self.failure_count = 0
            
            return result
            
        except self.expected_exception as err:
            self.failure_count += 1
            self.last_failure_time = current_time
            
            _LOGGER.debug(
                "Circuit breaker failure %d/%d: %s",
                self.failure_count,
                self.failure_threshold,
                str(err),
            )
            
            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                _LOGGER.warning(
                    "Circuit breaker OPENED due to %d failures",
                    self.failure_threshold,
                )
            
            # Re-raise the original exception
            raise
            
        except Exception as err:
            # Unexpected exception - don't count for circuit breaker
            _LOGGER.exception("Unexpected error in circuit breaker: %s", str(err))
            raise

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "recovery_timeout": self.recovery_timeout,
            "last_failure_time": self.last_failure_time,
            "half_open_start_time": self.half_open_start_time,
        }

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.half_open_start_time = 0.0
        _LOGGER.info("Circuit breaker manually reset to CLOSED state")


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass