"""Tests for diagnostic services."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.violet_pool_controller.services import (
    VioletServiceManager,
    VioletServiceHandlers,
)


@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    hass.services = Mock()
    hass.states = Mock()
    return hass


@pytest.fixture
def mock_coordinator():
    """Mock coordinator with device."""
    coordinator = Mock()
    coordinator.device = Mock()
    coordinator.device.device_name = "Test Pool"
    coordinator.device._available = True
    coordinator.device._last_update_time = 1234567890.0
    coordinator.device._connection_latency = 125.5
    coordinator.device._system_health = 95.0
    coordinator.device._consecutive_failures = 0
    coordinator.device.api_url = "192.168.1.100"
    coordinator.device.use_ssl = False
    coordinator.config_entry = Mock()
    coordinator.config_entry.entry_id = "test_entry_id"

    return coordinator


@pytest.fixture
def service_manager(hass):
    """Mock service manager."""
    manager = VioletServiceManager(hass)

    # Mock get_coordinator_for_device
    async def mock_get_coordinator(device_id):
        coordinator = Mock()
        coordinator.device = Mock()
        coordinator.device.device_name = "Test Pool"
        coordinator.device._available = True
        coordinator.device._last_update_time = 1234567890.0
        coordinator.device._connection_latency = 125.5
        coordinator.device._system_health = 95.0
        coordinator.device._consecutive_failures = 0
        coordinator.device.api_url = "192.168.1.100"
        coordinator.device.use_ssl = False
        return coordinator

    manager.get_coordinator_for_device = AsyncMock(side_effect=mock_get_coordinator)

    return manager


@pytest.fixture
def service_handlers(service_manager):
    """Mock service handlers."""
    return VioletServiceHandlers(service_manager)


class TestGetConnectionStatus:
    """Test get_connection_status service."""

    @pytest.mark.asyncio
    async def test_get_connection_status_success(self, service_handlers):
        """Test successful connection status retrieval."""
        call = Mock()
        call.data = {"device_id": ["test_device_id"]}

        result = await service_handlers.handle_get_connection_status(call)

        assert result["success"] is True
        assert "devices" in result
        assert len(result["devices"]) == 1
        assert result["devices"][0]["device_name"] == "Test Pool"
        assert result["devices"][0]["available"] is True
        assert result["devices"][0]["connection_latency_ms"] == 125.5
        assert result["devices"][0]["system_health"] == 95.0

    @pytest.mark.asyncio
    async def test_get_connection_status_device_not_found(self, service_handlers):
        """Test connection status with device not found."""
        # Mock coordinator as None
        service_handlers.manager.get_coordinator_for_device = AsyncMock(return_value=None)

        call = Mock()
        call.data = {"device_id": ["invalid_device"]}

        with pytest.raises(HomeAssistantError, match="Device .* not found"):
            await service_handlers.handle_get_connection_status(call)


class TestGetErrorSummary:
    """Test get_error_summary service."""

    @pytest.mark.asyncio
    async def test_get_error_summary_success(self, service_handlers):
        """Test successful error summary retrieval."""
        call = Mock()
        call.data = {"device_id": ["test_device_id"], "include_history": False}

        result = await service_handlers.handle_get_error_summary(call)

        assert result["success"] is True
        assert "devices" in result
        assert len(result["devices"]) == 1
        assert result["devices"][0]["device_name"] == "Test Pool"
        assert "error_summary" in result["devices"][0]
        assert "recovery_suggestion" in result["devices"][0]

    @pytest.mark.asyncio
    async def test_get_error_summary_with_history(self, service_handlers):
        """Test error summary with history included."""
        call = Mock()
        call.data = {"device_id": ["test_device_id"], "include_history": True}

        result = await service_handlers.handle_get_error_summary(call)

        assert result["success"] is True
        assert "devices" in result
        # Should include error_history when requested
        # (though it may be empty in our mock)


class TestConnection:
    """Test test_connection service."""

    @pytest.mark.asyncio
    async def test_test_connection_success(self, service_handlers):
        """Test successful connection test."""
        # Mock API
        mock_api = Mock()
        mock_api.get_readings = AsyncMock(return_value={"test": "data"})

        # Get coordinator and set API
        coordinator = await service_handlers.manager.get_coordinator_for_device("test_device_id")
        coordinator.device.api = mock_api

        call = Mock()
        call.data = {"device_id": ["test_device_id"]}

        result = await service_handlers.handle_test_connection(call)

        assert result["success"] is True
        assert "tests" in result
        assert len(result["tests"]) == 1
        assert result["tests"][0]["success"] is True
        assert result["tests"][0]["latency_ms"] > 0
        assert result["tests"][0]["keys_received"] == 1

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, service_handlers):
        """Test connection test with failure."""
        # Mock API that raises error
        mock_api = Mock()
        mock_api.get_readings = AsyncMock(side_effect=Exception("Connection failed"))

        # Get coordinator and set API
        coordinator = await service_handlers.manager.get_coordinator_for_device("test_device_id")
        coordinator.device.api = mock_api

        call = Mock()
        call.data = {"device_id": ["test_device_id"]}

        result = await service_handlers.handle_test_connection(call)

        assert result["success"] is True
        assert "tests" in result
        assert len(result["tests"]) == 1
        assert result["tests"][0]["success"] is False
        assert "error" in result["tests"][0]

    @pytest.mark.asyncio
    async def test_test_connection_no_api(self, service_handlers):
        """Test connection test when API is not available."""
        # Get coordinator without API
        coordinator = await service_handlers.manager.get_coordinator_for_device("test_device_id")
        coordinator.device.api = None

        call = Mock()
        call.data = {"device_id": ["test_device_id"]}

        with pytest.raises(HomeAssistantError, match="API not available"):
            await service_handlers.handle_test_connection(call)


class TestClearErrorHistory:
    """Test clear_error_history service."""

    @pytest.mark.asyncio
    async def test_clear_error_history_success(self, service_handlers):
        """Test successful error history clearing."""
        call = Mock()
        call.data = {"device_id": ["test_device_id"]}

        result = await service_handlers.handle_clear_error_history(call)

        assert result["success"] is True
        assert result["cleared_count"] == 1
        assert "Cleared error history" in result["message"]

    @pytest.mark.asyncio
    async def test_clear_error_history_multiple_devices(self, service_handlers):
        """Test clearing error history for multiple devices."""
        call = Mock()
        call.data = {"device_id": ["device1", "device2", "device3"]}

        result = await service_handlers.handle_clear_error_history(call)

        assert result["success"] is True
        assert result["cleared_count"] == 3


class TestServiceErrorHandling:
    """Test error handling in services."""

    @pytest.mark.asyncio
    async def test_get_connection_status_exception(self, service_handlers):
        """Test exception handling in get_connection_status."""
        # Mock to raise exception
        service_handlers.manager.get_coordinator_for_device = AsyncMock(
            side_effect=Exception("Test error")
        )

        call = Mock()
        call.data = {"device_id": ["test_device"]}

        with pytest.raises(HomeAssistantError, match="Failed to get connection status"):
            await service_handlers.handle_get_connection_status(call)

    @pytest.mark.asyncio
    async def test_get_error_summary_exception(self, service_handlers):
        """Test exception handling in get_error_summary."""
        service_handlers.manager.get_coordinator_for_device = AsyncMock(
            side_effect=Exception("Test error")
        )

        call = Mock()
        call.data = {"device_id": ["test_device"]}

        with pytest.raises(HomeAssistantError, match="Failed to get error summary"):
            await service_handlers.handle_get_error_summary(call)

    @pytest.mark.asyncio
    async def test_test_connection_exception(self, service_handlers):
        """Test exception handling in test_connection."""
        service_handlers.manager.get_coordinator_for_device = AsyncMock(
            side_effect=Exception("Test error")
        )

        call = Mock()
        call.data = {"device_id": ["test_device"]}

        with pytest.raises(HomeAssistantError, match="Failed to test connection"):
            await service_handlers.handle_test_connection(call)

    @pytest.mark.asyncio
    async def test_clear_error_history_exception(self, service_handlers):
        """Test exception handling in clear_error_history."""
        service_handlers.manager.get_coordinator_for_device = AsyncMock(
            side_effect=Exception("Test error")
        )

        call = Mock()
        call.data = {"device_id": ["test_device"]}

        with pytest.raises(HomeAssistantError, match="Failed to clear error history"):
            await service_handlers.handle_clear_error_history(call)


class TestServiceRegistration:
    """Test service registration."""

    @pytest.mark.asyncio
    async def test_diagnostic_services_registered(self, hass):
        """Test that diagnostic services are properly registered."""
        # Import schemas
        from custom_components.violet_pool_controller.services import get_service_schemas

        schemas = get_service_schemas()

        # Check that all diagnostic services have schemas
        assert "get_connection_status" in schemas
        assert "get_error_summary" in schemas
        assert "test_connection" in schemas
        assert "clear_error_history" in schemas
