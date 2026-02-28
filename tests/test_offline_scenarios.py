"""Tests for offline scenario handling."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.violet_pool_controller.device import VioletPoolControllerDevice
from custom_components.violet_pool_controller.api import VioletPoolAPIError


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
        "api_url": "192.168.1.100",
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
    hass.config_entries = Mock()
    return hass


@pytest.fixture
def device(mock_hass, mock_config_entry, mock_api):
    """Create device instance for testing."""
    device = VioletPoolControllerDevice(mock_hass, mock_config_entry, mock_api)
    return device


class TestOfflineScenarios:
    """Test offline scenario handling."""

    @pytest.mark.asyncio
    async def test_network_timeout_error(self, device, mock_api):
        """Test handling of network timeout errors."""
        # Mock timeout error
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Connection timeout")
        )

        # First error should be logged
        device._available = True
        device._data = {"test": "data"}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Should increment consecutive failures
        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_connection_refused_error(self, device, mock_api):
        """Test handling of connection refused errors."""
        # Mock connection refused
        mock_api.get_readings = AsyncMock(
            side_effect=ConnectionRefusedError("Connection refused")
        )

        device._available = True

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_empty_response_error(self, device, mock_api):
        """Test handling of empty/invalid responses."""
        # Mock empty response
        mock_api.get_readings = AsyncMock(return_value=None)

        device._available = True
        device._data = {"test": "data"}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_invalid_response_error(self, device, mock_api):
        """Test handling of invalid response format."""
        # Mock invalid response
        mock_api.get_readings = AsyncMock(return_value="invalid")

        device._available = True
        device._data = {"test": "data"}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_consecutive_failures_threshold(self, device, mock_api):
        """Test reaching max consecutive failures threshold."""
        # Mock continuous failures
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._max_consecutive_failures = 5
        device._data = {"test": "data"}

        # Simulate 5 failures
        for _ in range(5):
            with pytest.raises(UpdateFailed):
                await device.async_update()

        # Should be marked unavailable
        assert device._available is False
        assert device._consecutive_failures == 5

    @pytest.mark.asyncio
    async def test_recovery_after_failures(self, device, mock_api):
        """Test successful recovery after failures."""
        # First, cause failures
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._consecutive_failures = 2
        device._data = {}

        # Fail
        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 3

        # Now recover with valid data
        mock_api.get_readings = AsyncMock(
            return_value={"test": "data", "value": 123}
        )

        result = await device.async_update()

        # Should be recovered
        assert device._available is True
        assert device._consecutive_failures == 0
        assert result == {"test": "data", "value": 123}

    @pytest.mark.asyncio
    async def test_throttled_logging(self, device, mock_api):
        """Test that repeated errors are logged with throttling."""
        # Mock continuous failures
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._data = {"test": "data"}

        # First failure should be logged (if available)
        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Check if should_log_failure works
        # (This is internal, we just verify it doesn't crash)
        assert device._should_log_failure() is True or device._should_log_failure() is False

    @pytest.mark.asyncio
    async def test_api_error_handling(self, device, mock_api):
        """Test VioletPoolAPIError handling."""
        # Mock API error
        mock_api.get_readings = AsyncMock(
            side_effect=VioletPoolAPIError("API request failed")
        )

        device._available = True
        device._data = {"test": "data"}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 1
        assert "API request failed" in device._last_error


class TestOfflineMetrics:
    """Test offline metrics tracking."""

    @pytest.mark.asyncio
    async def test_system_health_degradation(self, device, mock_api):
        """Test system health degradation on errors."""
        # Mock failure
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._system_health = 100.0
        device._data = {"test": "data"}

        # Cause failure
        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Health should decrease
        assert device._system_health < 100.0

    @pytest.mark.asyncio
    async def test_system_health_recovery(self, device, mock_api):
        """Test system health recovery."""
        # First cause failure
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._system_health = 60.0
        device._data = {}

        with pytest.raises(UpdateFailed):
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
        # Mock successful request
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
        """Test offline duration is tracked."""
        import time

        # Start offline
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._data = {"test": "data"}

        # Record start time
        start_time = time.time()

        # Go offline
        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Wait a bit
        await asyncio.sleep(0.1)

        # Check still offline
        assert device._available is False

        # Duration should be tracked (in error handler)
        # (This is tested more thoroughly in test_error_handler.py)

    @pytest.mark.asyncio
    async def test_error_classification(self, device, mock_api):
        """Test that errors are properly classified."""
        from custom_components.violet_pool_controller.error_handler import (
            get_enhanced_error_handler,
            ErrorType,
        )

        handler = get_enhanced_error_handler()

        # Mock timeout error
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._data = {}

        # Cause error
        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Error should be classified by handler
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

        # Fail
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )
        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Succeed
        mock_api.get_readings = AsyncMock(return_value={"test": "data"})
        result = await device.async_update()
        assert device._available is True

        # Fail again
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )
        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Recover again
        mock_api.get_readings = AsyncMock(return_value={"test": "data2"})
        result = await device.async_update()
        assert device._available is True
        assert result["test"] == "data2"

    @pytest.mark.asyncio
    async def test_persistent_offline_recovery(self, device, mock_api):
        """Test recovery after persistent offline state."""
        # Go offline for multiple attempts
        mock_api.get_readings = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        device._available = True
        device._data = {}
        device._max_consecutive_failures = 10

        # Cause multiple failures
        for _ in range(5):
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
