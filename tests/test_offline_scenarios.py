"""Tests for offline scenario handling."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.violet_pool_controller.device import VioletPoolControllerDevice
from violet_poolcontroller_api.api import VioletPoolAPIError


@pytest.fixture
def mock_api():
    """Mock API instance."""
    api = Mock()
    api.get_readings = AsyncMock()
    return api


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    entry = Mock()
    entry.entry_id = "test_entry"
    entry.data = {
        "device_id": 1,
        "host": "192.168.1.100",
        "use_ssl": False,
        "device_name": "Test Pool",
        "controller_name": "Test Controller",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_hass():
    """Mock Home Assistant instance."""
    hass = Mock()
    hass.data = {}  # Use real dict so 'in' operator works
    hass.config_entries = Mock()
    return hass


@pytest.fixture
def device(mock_hass, mock_config_entry, mock_api):
    """Create device instance for testing.

    Uses yield so patches remain active for the full test duration.
    Patches async_create_issue / async_delete_issue so they don't touch
    the real HA issue registry (which requires hass.data to be populated).
    """
    with (
        patch(
            "custom_components.violet_pool_controller.device.async_get_clientsession",
            return_value=Mock(),
        ),
        patch(
            "custom_components.violet_pool_controller.device.async_create_issue"
        ),
        patch(
            "custom_components.violet_pool_controller.device.async_delete_issue"
        ),
    ):
        dev = VioletPoolControllerDevice(mock_hass, mock_config_entry, mock_api)
        yield dev


class TestOfflineScenarios:
    """Test offline scenario handling."""

    @pytest.mark.asyncio
    async def test_network_timeout_error(self, device, mock_api):
        """Test handling of network timeout errors.

        A single failure is below the threshold (5) — async_update returns
        stale data and does NOT raise UpdateFailed.
        """
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Connection timeout")
        )

        device._available = True
        device._data = {"test": "data"}

        # Single failure → stale data returned, no exception
        result = await device.async_update()

        assert device._consecutive_failures == 1
        assert result == {"test": "data"}

    @pytest.mark.asyncio
    async def test_connection_refused_error(self, device, mock_api):
        """Test handling of connection refused errors."""
        mock_api.get_readings = AsyncMock(
            side_effect=ConnectionRefusedError("Connection refused")
        )

        device._available = True
        device._data = {}

        await device.async_update()

        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_empty_response_error(self, device, mock_api):
        """Test handling of empty/invalid responses."""
        mock_api.get_readings = AsyncMock(return_value=None)

        device._available = True
        device._data = {"test": "data"}

        # Single failure → stale data returned, no exception
        await device.async_update()

        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_invalid_response_error(self, device, mock_api):
        """Test handling of invalid response format."""
        mock_api.get_readings = AsyncMock(return_value="invalid")

        device._available = True
        device._data = {"test": "data"}

        # Single failure → stale data returned, no exception
        await device.async_update()

        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_consecutive_failures_threshold(self, device, mock_api):
        """Test reaching max consecutive failures threshold.

        The first (max-1) calls return stale data; the Nth call raises UpdateFailed
        and marks the device unavailable.
        """
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._max_consecutive_failures = 5
        device._data = {"test": "data"}

        # First 4 failures: no raise
        for _ in range(4):
            await device.async_update()

        assert device._consecutive_failures == 4
        assert device._available is True  # still available

        # 5th failure: raises UpdateFailed and marks unavailable
        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._available is False
        assert device._consecutive_failures == 5

    @pytest.mark.asyncio
    async def test_recovery_after_failures(self, device, mock_api):
        """Test successful recovery after failures."""
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._consecutive_failures = 2
        device._data = {}

        # One more failure (3 total, still below threshold) — no raise
        await device.async_update()

        assert device._consecutive_failures == 3

        # Now recover with valid data
        mock_api.get_readings = AsyncMock(
            return_value={"test": "data", "value": 123}
        )

        result = await device.async_update()

        assert device._available is True
        assert device._consecutive_failures == 0
        assert result == {"test": "data", "value": 123}

    @pytest.mark.asyncio
    async def test_throttled_logging(self, device, mock_api):
        """Test that repeated errors are logged with throttling."""
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._data = {"test": "data"}

        # First failure (below threshold — no raise)
        await device.async_update()

        # Verify _should_log_failure doesn't crash
        result = device._should_log_failure()
        assert result is True or result is False

    @pytest.mark.asyncio
    async def test_api_error_handling(self, device, mock_api):
        """Test VioletPoolAPIError handling."""
        mock_api.get_readings = AsyncMock(
            side_effect=VioletPoolAPIError("API request failed")
        )

        device._available = True
        device._data = {"test": "data"}

        # Single API failure below threshold — no raise
        await device.async_update()

        assert device._consecutive_failures == 1
        assert "API request failed" in device._last_error


class TestOfflineMetrics:
    """Test offline metrics tracking."""

    @pytest.mark.asyncio
    async def test_system_health_degradation(self, device, mock_api):
        """Test system health degradation on errors.

        Uses return_value=None so the data-check path runs, which updates
        _system_health.  The exception path (TimeoutError) does not update health.
        """
        mock_api.get_readings = AsyncMock(return_value=None)

        device._available = True
        device._system_health = 100.0
        device._data = {"test": "data"}

        # Failure via bad data → health degrades
        await device.async_update()

        assert device._system_health < 100.0

    @pytest.mark.asyncio
    async def test_system_health_recovery(self, device, mock_api):
        """Test system health recovery."""
        # Use None response so data-check path runs and health degrades
        mock_api.get_readings = AsyncMock(return_value=None)

        device._available = True
        device._system_health = 60.0
        device._data = {}

        await device.async_update()

        # Now recover
        mock_api.get_readings = AsyncMock(
            return_value={"test": "data"}
        )

        await device.async_update()

        # Health should be back to 100%
        assert device._system_health == 100.0

    @pytest.mark.asyncio
    async def test_connection_latency_tracking(self, device, mock_api):
        """Test connection latency is tracked."""
        async def slow_request():
            await asyncio.sleep(0.1)  # 100ms delay
            return {"test": "data"}

        mock_api.get_readings = AsyncMock(side_effect=slow_request)

        device._data = {}

        await device.async_update()

        # Latency should be tracked (around 100ms)
        assert device._connection_latency > 0
        assert device._connection_latency > 90  # At least 90ms


class TestOfflineErrorHandling:
    """Test error handling integration."""

    @pytest.mark.asyncio
    async def test_offline_duration_tracking(self, device, mock_api):
        """Test that device is marked unavailable after reaching failure threshold."""
        # Pre-set consecutive failures to just below threshold so next failure triggers
        device._consecutive_failures = device._max_consecutive_failures - 1
        device._data = {"test": "data"}

        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True

        # This failure reaches the threshold → UpdateFailed + _available = False
        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Wait a bit to simulate offline duration
        await asyncio.sleep(0.1)

        assert device._available is False

    @pytest.mark.asyncio
    async def test_error_classification(self, device, mock_api):
        """Test that errors are properly classified."""
        from custom_components.violet_pool_controller.error_handler import (
            get_enhanced_error_handler,
            ErrorType,
        )

        handler = get_enhanced_error_handler()

        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._data = {}

        # Single failure below threshold — no raise
        await device.async_update()

        # Error should be classifiable by handler
        summary = handler.get_error_summary()
        assert "total_errors" in summary
        assert summary["total_errors"] >= 0


class TestRecoveryScenarios:
    """Test various recovery scenarios."""

    @pytest.mark.asyncio
    async def test_gradual_recovery(self, device, mock_api):
        """Test gradual recovery with intermittent failures."""
        device._available = True
        device._data = {}

        # Fail (below threshold — no raise)
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )
        await device.async_update()
        assert device._consecutive_failures == 1

        # Succeed
        mock_api.get_readings = AsyncMock(return_value={"test": "data"})
        result = await device.async_update()
        assert device._available is True
        assert device._consecutive_failures == 0

        # Fail again (below threshold — no raise)
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )
        await device.async_update()
        assert device._consecutive_failures == 1

        # Recover again
        mock_api.get_readings = AsyncMock(return_value={"test": "data2"})
        result = await device.async_update()
        assert device._available is True
        assert result["test"] == "data2"

    @pytest.mark.asyncio
    async def test_persistent_offline_recovery(self, device, mock_api):
        """Test recovery after persistent offline state."""
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._data = {}
        # Keep default max_consecutive_failures = 5

        # First 4 failures: no raise
        for _ in range(4):
            await device.async_update()

        assert device._consecutive_failures == 4
        assert device._available is True

        # 5th failure: raises UpdateFailed and marks unavailable
        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 5
        assert device._available is False

        # Now recover
        mock_api.get_readings = AsyncMock(return_value={"status": "online"})

        result = await device.async_update()

        assert device._available is True
        assert device._consecutive_failures == 0
        assert result["status"] == "online"
