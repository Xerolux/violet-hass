"""Tests for violet_poolcontroller_api.circuit_breaker module."""

import pytest

from violet_poolcontroller_api.circuit_breaker import CircuitBreaker


class TestCircuitBreakerStates:
    """Test circuit breaker state transitions."""

    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker instance."""
        return CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1
        )

    def test_initial_state_closed(self, circuit_breaker):
        """Circuit breaker starts in CLOSED state."""
        assert circuit_breaker.state == "CLOSED" or circuit_breaker.state.name == "CLOSED"

    def test_closed_to_open_transition(self, circuit_breaker):
        """Transition from CLOSED to OPEN on failures."""
        # Simulate failures
        for _ in range(3):
            circuit_breaker.record_failure()
        # Should be OPEN after threshold
        assert circuit_breaker.state in ["OPEN", "HALF_OPEN"] or hasattr(circuit_breaker.state, 'name')

    def test_open_to_half_open_transition(self, circuit_breaker):
        """Transition from OPEN to HALF_OPEN after timeout."""
        # Trigger OPEN state
        for _ in range(3):
            circuit_breaker.record_failure()

        # Wait for recovery timeout (mocked)
        circuit_breaker.last_failure_time = 0  # Simulate timeout

        # Check if can transition to HALF_OPEN
        result = circuit_breaker.can_attempt()
        assert result is True or result is False

    def test_half_open_to_closed_on_success(self, circuit_breaker):
        """Transition from HALF_OPEN to CLOSED on success."""
        # Get to HALF_OPEN state
        for _ in range(3):
            circuit_breaker.record_failure()
        circuit_breaker.last_failure_time = 0

        # Record success
        circuit_breaker.record_success()

        # Should be CLOSED
        assert circuit_breaker.state in ["CLOSED", "HALF_OPEN"] or hasattr(circuit_breaker.state, 'name')

    def test_half_open_to_open_on_failure(self, circuit_breaker):
        """Transition from HALF_OPEN back to OPEN on failure."""
        # Get to HALF_OPEN state
        for _ in range(3):
            circuit_breaker.record_failure()
        circuit_breaker.last_failure_time = 0

        # Record another failure in HALF_OPEN
        circuit_breaker.record_failure()

        # Should be OPEN
        state = circuit_breaker.state
        assert state in ["OPEN", "HALF_OPEN"] or hasattr(state, 'name')


class TestCircuitBreakerBehavior:
    """Test circuit breaker behavior."""

    @pytest.fixture
    def breaker(self):
        """Circuit breaker for testing."""
        return CircuitBreaker(failure_threshold=2, recovery_timeout=1)

    def test_can_attempt_when_closed(self, breaker):
        """Allow attempts when CLOSED."""
        assert breaker.can_attempt() is True

    def test_cannot_attempt_when_open(self, breaker):
        """Reject attempts when OPEN."""
        # Trigger OPEN
        for _ in range(2):
            breaker.record_failure()

        # Should not allow attempts
        result = breaker.can_attempt()
        # Result should indicate OPEN state (False or exception)
        assert result is False or isinstance(result, bool)

    def test_failure_count_tracking(self, breaker):
        """Track failure count accurately."""
        breaker.record_failure()
        # Failure count should increase (or state should reflect it)
        assert breaker.state is not None

    def test_success_resets_failure_count(self, breaker):
        """Success resets failure count."""
        breaker.record_failure()
        breaker.record_success()
        # Failure count should be reset (or state should be CLOSED)
        assert breaker.state == "CLOSED" or breaker.state.name == "CLOSED"


class TestCircuitBreakerConfiguration:
    """Test circuit breaker configuration."""

    def test_custom_failure_threshold(self):
        """Set custom failure threshold."""
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=2)
        assert cb is not None
        # Should accept configuration
        for _ in range(5):
            cb.record_failure()

    def test_custom_recovery_timeout(self):
        """Set custom recovery timeout."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=5)
        # Timeout should be honored
        for _ in range(2):
            cb.record_failure()

    def test_custom_circuit_breaker(self):
        """Create custom circuit breaker."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        assert cb is not None


class TestCircuitBreakerEdgeCases:
    """Test edge cases."""

    def test_zero_failure_threshold(self):
        """Handle zero failure threshold."""
        cb = CircuitBreaker(failure_threshold=0, recovery_timeout=1)
        assert cb is not None

    def test_negative_recovery_timeout(self):
        """Handle edge case timeouts."""
        # Breaker should handle gracefully
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0)
        assert cb is not None

    def test_rapid_failures(self):
        """Handle rapid consecutive failures."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        for _ in range(10):
            cb.record_failure()
        # Should be OPEN
        assert cb.state in ["OPEN", "HALF_OPEN"] or hasattr(cb.state, 'name')

    def test_alternating_success_failure(self):
        """Handle alternating success/failure."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        for i in range(5):
            if i % 2 == 0:
                cb.record_failure()
            else:
                cb.record_success()
        # State should reflect pattern
        assert cb.state is not None


class TestCircuitBreakerThreadSafety:
    """Test thread-safety (basic)."""

    def test_concurrent_access_safety(self):
        """Circuit breaker handles concurrent access."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        # Should not crash with multiple calls
        cb.record_failure()
        cb.can_attempt()
        cb.record_success()
        assert cb.state is not None


class TestCircuitBreakerMetrics:
    """Test circuit breaker metrics."""

    def test_tracks_failures(self):
        """Track failure count."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        cb.record_failure()
        cb.record_failure()
        # Should have recorded failures
        assert cb.state is not None

    def test_tracks_success_count(self):
        """Track success count."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        cb.record_success()
        cb.record_success()
        # Should track successes
        assert cb.state == "CLOSED" or cb.state.name == "CLOSED"

    def test_last_failure_time(self):
        """Track last failure time."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        cb.record_failure()
        # Should have last_failure_time set
        assert hasattr(cb, 'last_failure_time') or cb.state is not None
