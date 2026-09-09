"""Tests for offline scenario handling.

Every failed poll raises ``UpdateFailed``. The coordinator keeps the last good
data itself and marks the entities unavailable, so the device must never return
the previous readings as if they had just been read - that used to present
five-minute-old values as fresh.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from violet_poolcontroller_api.api import VioletPoolAPIError

from custom_components.violet_pool_controller.device import VioletPoolControllerDevice
from custom_components.violet_pool_controller.error_handler import ErrorType


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
        patch("custom_components.violet_pool_controller.device.async_create_issue"),
        patch("custom_components.violet_pool_controller.device.async_delete_issue"),
    ):
        dev = VioletPoolControllerDevice(mock_hass, mock_config_entry, mock_api)
        yield dev


class TestOfflineScenarios:
    """Test offline scenario handling."""

    @pytest.mark.asyncio
    async def test_network_timeout_error(self, device, mock_api):
        """A network timeout raises instead of republishing the previous data."""
        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Connection timeout"))

        device._available = True
        device._data = {"test": "data"}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 1
        # The previous readings survive for the coordinator, but they were not
        # handed out as a successful update.
        assert device.data == {"test": "data"}

    @pytest.mark.asyncio
    async def test_connection_refused_error(self, device, mock_api):
        """Test handling of connection refused errors."""
        mock_api.get_readings = AsyncMock(side_effect=ConnectionRefusedError("Connection refused"))

        device._available = True
        device._data = {}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_empty_response_error(self, device, mock_api):
        """An empty response is a failure, not an update with stale values."""
        mock_api.get_readings = AsyncMock(return_value=None)

        device._available = True
        device._data = {"test": "data"}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_invalid_response_error(self, device, mock_api):
        """Test handling of invalid response format."""
        mock_api.get_readings = AsyncMock(return_value="invalid")

        device._available = True
        device._data = {"test": "data"}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_consecutive_failures_threshold(self, device, mock_api):
        """The device stays 'available' until the failure threshold is reached."""
        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))

        device._available = True
        device._max_consecutive_failures = 5
        device._data = {"test": "data"}

        for _ in range(4):
            with pytest.raises(UpdateFailed):
                await device.async_update()

        assert device._consecutive_failures == 4
        assert device._available is True  # still available

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._available is False
        assert device._consecutive_failures == 5

    @pytest.mark.asyncio
    async def test_repair_issue_raised_for_api_errors_too(self, device, mock_api):
        """The repair issue must not be limited to the empty-data branch.

        Regression: ``controller_unavailable_*`` was only created when the
        controller answered with empty data, never for the far more common
        ``VioletPoolAPIError``.
        """
        mock_api.get_readings = AsyncMock(side_effect=VioletPoolAPIError("boom"))
        device._available = True
        device._data = {"test": "data"}

        with patch(
            "custom_components.violet_pool_controller.device.async_create_issue"
        ) as create_issue:
            for _ in range(device._max_consecutive_failures):
                with pytest.raises(UpdateFailed):
                    await device.async_update()

        assert create_issue.called
        assert create_issue.call_args[0][2] == "controller_unavailable_test_entry"

    @pytest.mark.asyncio
    async def test_recovery_after_failures(self, device, mock_api):
        """Test successful recovery after failures."""
        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))

        device._available = True
        device._consecutive_failures = 2
        device._data = {}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._consecutive_failures == 3

        # Now recover with valid data
        mock_api.get_readings = AsyncMock(return_value={"test": "data", "value": 123})
        mock_api.dosing_standalone = False

        result = await device.async_update()

        assert device._available is True
        assert device._consecutive_failures == 0
        assert result["test"] == "data"
        assert result["value"] == 123
        assert "HW_BASE_MODULE" in result
        assert "HW_STANDALONE_MODE" in result

    @pytest.mark.asyncio
    async def test_throttled_logging(self, device, mock_api):
        """Test that repeated errors are logged with throttling."""
        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))

        device._available = True
        device._data = {"test": "data"}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Verify _should_log_failure doesn't crash
        result = device._should_log_failure()
        assert result is True or result is False

    @pytest.mark.asyncio
    async def test_api_error_handling(self, device, mock_api):
        """Test VioletPoolAPIError handling."""
        mock_api.get_readings = AsyncMock(side_effect=VioletPoolAPIError("API request failed"))

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
        mock_api.get_readings = AsyncMock(return_value=None)

        device._available = True
        device._system_health = 100.0
        device._data = {"test": "data"}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device._system_health < 100.0

    @pytest.mark.asyncio
    async def test_system_health_recovery(self, device, mock_api):
        """Test system health recovery."""
        mock_api.get_readings = AsyncMock(return_value=None)

        device._available = True
        device._system_health = 60.0
        device._data = {}

        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Now recover
        mock_api.get_readings = AsyncMock(return_value={"test": "data"})

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

        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))

        device._available = True

        with pytest.raises(UpdateFailed):
            await device.async_update()

        # Wait a bit to simulate offline duration
        await asyncio.sleep(0.1)

        assert device._available is False

    @pytest.mark.asyncio
    async def test_failed_polls_are_recorded_per_device(self, device, mock_api):
        """Each failed poll feeds this device's own error statistics."""
        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))

        device._available = True
        device._data = {}

        for _ in range(3):
            with pytest.raises(UpdateFailed):
                await device.async_update()

        summary = device.error_handler.get_error_summary()

        assert summary["total_errors"] == 3
        assert summary["consecutive_errors"] == 3
        assert summary["error_counts"][ErrorType.TIMEOUT_ERROR.value] == 3
        assert summary["is_offline"] is True
        # The offline duration is a monotonic difference, not "seconds since
        # the epoch" - it used to come out at ~1.7 billion.
        assert 0.0 <= summary["offline_duration_seconds"] < 60.0

    @pytest.mark.asyncio
    async def test_successful_poll_clears_the_offline_state(self, device, mock_api):
        """A successful poll records the recovery in the error statistics."""
        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))
        device._available = True
        device._data = {}

        with pytest.raises(UpdateFailed):
            await device.async_update()
        assert device.error_handler.get_error_summary()["is_offline"] is True

        mock_api.get_readings = AsyncMock(return_value={"test": "data"})
        await device.async_update()

        summary = device.error_handler.get_error_summary()
        assert summary["is_offline"] is False
        assert summary["consecutive_errors"] == 0
        # The recorded history is kept for diagnostics.
        assert summary["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_error_handler_is_not_shared_between_devices(
        self, device, mock_hass, mock_config_entry, mock_api
    ):
        """A second controller's outage must not show up in this device's stats."""
        with patch(
            "custom_components.violet_pool_controller.device.async_get_clientsession",
            return_value=Mock(),
        ):
            other = VioletPoolControllerDevice(mock_hass, mock_config_entry, mock_api)

        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))
        device._data = {}
        with pytest.raises(UpdateFailed):
            await device.async_update()

        assert device.error_handler is not other.error_handler
        assert other.error_handler.get_error_summary()["total_errors"] == 0


class TestRecoveryScenarios:
    """Test various recovery scenarios."""

    @pytest.mark.asyncio
    async def test_gradual_recovery(self, device, mock_api):
        """Test gradual recovery with intermittent failures."""
        device._available = True
        device._data = {}

        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))
        with pytest.raises(UpdateFailed):
            await device.async_update()
        assert device._consecutive_failures == 1

        # Succeed
        mock_api.get_readings = AsyncMock(return_value={"test": "data"})
        await device.async_update()
        assert device._available is True
        assert device._consecutive_failures == 0

        # Fail again
        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))
        with pytest.raises(UpdateFailed):
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
        mock_api.get_readings = AsyncMock(side_effect=TimeoutError("Timeout"))

        device._available = True
        device._data = {}
        # Keep default max_consecutive_failures = 5

        for _ in range(4):
            with pytest.raises(UpdateFailed):
                await device.async_update()

        assert device._consecutive_failures == 4
        assert device._available is True

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


class TestErrorHandlerAccessor:
    """The per-device handler must be reachable from the coordinator too."""

    def test_coordinator_passthrough(self, device):
        """``coordinator.error_handler`` is the device's handler."""
        from custom_components.violet_pool_controller.device import (
            VioletPoolDataUpdateCoordinator,
        )

        coordinator = VioletPoolDataUpdateCoordinator.__new__(
            VioletPoolDataUpdateCoordinator
        )
        coordinator.device = device

        assert coordinator.error_handler is device.error_handler
