"""Tests for violet_poolcontroller_api.circuit_breaker module."""

import pytest

from violet_poolcontroller_api.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
)


class TestCircuitBreakerStates:
    """Test circuit breaker state transitions."""

    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker instance."""
        return CircuitBreaker(failure_threshold=3, recovery_timeout=1)

    async def test_initial_state_closed(self, circuit_breaker):
        """Circuit breaker starts in CLOSED state."""
        assert circuit_breaker.state.name == "CLOSED"

    async def test_state_transitions_closed_to_open(self, circuit_breaker):
        """CLOSED → OPEN after threshold failures."""
        async def failing():
            raise ValueError("simulated failure")

        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing)

        assert circuit_breaker.state.name == "OPEN"
        assert circuit_breaker.failure_count == 3

    async def test_circuit_open_rejects_calls(self, circuit_breaker):
        """OPEN circuit raises CircuitBreakerOpenError."""
        async def failing():
            raise ValueError("fail")

        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing)

        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(failing)

    async def test_ignored_exceptions_dont_count(self):
        """Ignored exceptions pass through without incrementing failure count."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1,
            ignored_exceptions=(ValueError,),
        )

        async def value_err():
            raise ValueError("should be ignored")

        for _ in range(5):
            with pytest.raises(ValueError):
                await cb.call(value_err)

        assert cb.failure_count == 0
        assert cb.state.name == "CLOSED"

    async def test_success_resets_failure_count(self, circuit_breaker):
        """Success resets failure count."""
        async def failing():
            raise ValueError("fail")

        async def succeeding():
            return "ok"

        # Trigger one failure
        with pytest.raises(ValueError):
            await circuit_breaker.call(failing)
        assert circuit_breaker.failure_count == 1

        # Success
        result = await circuit_breaker.call(succeeding)
        assert result == "ok"
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.state.name == "CLOSED"


class TestCircuitBreakerConfiguration:
    """Test circuit breaker configuration."""

    def test_custom_failure_threshold(self):
        """Set custom failure threshold."""
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=2)
        assert cb.failure_threshold == 5

    async def test_zero_failure_threshold(self):
        """Zero failure threshold opens on first failure."""
        cb = CircuitBreaker(failure_threshold=0, recovery_timeout=1)

        async def failing():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            await cb.call(failing)
        assert cb.state.name == "OPEN"

    def test_negative_recovery_timeout(self):
        """Negative timeout handled gracefully."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=-1)
        assert cb is not None

    def test_custom_recovery_timeout(self):
        """Set custom recovery timeout."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=5)
        assert cb.recovery_timeout == 5


class TestCircuitBreakerMetrics:
    """Test circuit breaker metrics."""

    async def test_get_stats_returns_state_info(self):
        """get_stats returns current state info."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        stats = cb.get_stats()
        assert stats["state"].name == "CLOSED"
        assert stats["failure_count"] == 0

    async def test_reset_clears_state(self):
        """reset restores CLOSED state and clears counters."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        async def failing():
            raise ValueError("fail")

        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing)

        assert cb.state.name == "OPEN"
        await cb.reset()
        assert cb.state.name == "CLOSED"
        assert cb.failure_count == 0
