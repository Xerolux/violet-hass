# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024-2026  Xerolux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Circuit breaker implementation for resilient API calls."""
from __future__ import annotations

import asyncio
import logging
import time
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

_LOGGER = logging.getLogger(__name__)


class CircuitBreakerState(StrEnum):
    """Circuit breaker states."""

    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Circuit is open, calls fail fast
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
        expected_exception: type[BaseException] = Exception,
    ) -> None:
        """Initialize circuit breaker.

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

        # Protects mutable state from concurrent coroutine access (e.g., asyncio.gather)
        self._lock = asyncio.Lock()

        _LOGGER.debug(
            "Circuit breaker initialized: threshold=%d, timeout=%.1fs, recovery=%.1fs",
            failure_threshold,
            timeout,
            recovery_timeout,
        )

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """Execute function with circuit breaker protection.

        Args:
            func: The async function to call
            *args: Arguments to pass to function
            **kwargs: Keyword arguments to pass to function

        Returns:
            Result of function call

        Raises:
            CircuitBreakerOpenError: If circuit is open

        """
        current_time = time.monotonic()

        # Check and update circuit state under lock to prevent races
        async with self._lock:
            # Check if circuit should be closed from timeout
            if (
                self.state == CircuitBreakerState.OPEN
                and current_time - self.last_failure_time > self.timeout
            ):
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_start_time = current_time
                _LOGGER.info(
                    "Circuit breaker entering HALF_OPEN state for recovery test",
                )

            # Check if half-open timeout exceeded
            if (
                self.state == CircuitBreakerState.HALF_OPEN
                and current_time - self.half_open_start_time > self.recovery_timeout
            ):
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                _LOGGER.info("Circuit breaker recovered to CLOSED state")

            # Fail fast if circuit is open
            if self.state == CircuitBreakerState.OPEN:
                msg = "Circuit breaker is OPEN"
                raise CircuitBreakerOpenError(msg)

        try:
            # Execute the function outside the lock to avoid blocking other coroutines
            result = await func(*args, **kwargs)

        except self.expected_exception as err:
            async with self._lock:
                failure_time = time.monotonic()
                self.failure_count += 1
                self.last_failure_time = failure_time

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

        except Exception:
            # Unexpected exception - don't count for circuit breaker
            _LOGGER.exception("Unexpected error in circuit breaker")
            raise

        else:
            # Success: reset failure count and close circuit if half-open
            async with self._lock:
                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    _LOGGER.info("Circuit breaker recovered from HALF_OPEN to CLOSED")
                else:
                    self.failure_count = 0

            return result

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

    async def reset(self) -> None:
        """Manually reset the circuit breaker."""
        async with self._lock:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.last_failure_time = 0.0
            self.half_open_start_time = 0.0
        _LOGGER.info("Circuit breaker manually reset to CLOSED state")


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
