
import pytest
from unittest.mock import MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import DOMAIN
from custom_components.violet_pool_controller.services import async_register_services, VioletServiceHandlers, VioletServiceManager

@pytest.mark.asyncio
async def test_export_diagnostic_logs_failure(hass: HomeAssistant, device_registry: dr.DeviceRegistry):
    """Test to reproduce the issue where device_id from registry is not found."""

    # 1. Setup Config Entry
    config_entry = MockConfigEntry(domain=DOMAIN, entry_id="config_entry_123")
    config_entry.add_to_hass(hass)

    # 2. Setup Device in Registry linked to Config Entry
    device = device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, "unique_device_id")},
        name="Test Device"
    )

    # 3. Mock Coordinator and attach to hass.data
    mock_coordinator = MagicMock()
    mock_coordinator.config_entry = config_entry
    # Setup mock device inside coordinator
    mock_coordinator.device = MagicMock()
    mock_coordinator.device.device_name = "Test Device"
    mock_coordinator.device.available = True
    mock_coordinator.device.controller_name = "Violet Pool Controller"
    mock_coordinator.device.api_url = "http://192.168.1.100"
    mock_coordinator.device.device_id = "1"
    mock_coordinator.device.firmware_version = "1.0.0"
    mock_coordinator.device.last_event_age = 10.0
    mock_coordinator.device.connection_latency = 50.0
    mock_coordinator.device.system_health = 100.0
    mock_coordinator.device._update_counter = 100
    mock_coordinator.device.consecutive_failures = 0

    hass.data[DOMAIN] = {
        config_entry.entry_id: mock_coordinator
    }

    # 4. Register Services
    await async_register_services(hass)

    # 5. Call Service with Device Registry ID
    # This is what the UI sends when you select a device.
    # With the fix, this should now succeed.

    response = await hass.services.async_call(
        DOMAIN,
        "export_diagnostic_logs",
        {"device_id": device.id}, # device.id is the registry ID
        blocking=True,
        return_response=True
    )

    # Assert success
    assert response["success"] is True
    assert "lines_exported" in response


# Mock Config class to simulate real behavior (no .version attribute)
class RealConfig:
    def __init__(self):
        self.components = {"http", "websocket_api"}
        self.time_zone = "UTC"
        # Explicitly do NOT set version

    def path(self, *args):
        return "/config/home-assistant.log"

@pytest.mark.asyncio
async def test_reproduce_config_version_error(hass):
    # Setup hass with a restricted Config object
    real_config = RealConfig()
    hass.config = real_config

    # Mock manager
    manager = VioletServiceManager(hass)
    handlers = VioletServiceHandlers(manager)

    # Mock call data
    call = MagicMock()
    call.data = {"device_id": ["test_device"]}

    # Mock manager.get_coordinator_for_device to return a coordinator
    mock_coordinator = MagicMock()
    mock_coordinator.device.device_name = "Test Device"
    # ... set other attributes to avoid other errors
    mock_coordinator.device.controller_name = "Violet"
    mock_coordinator.device.api_url = "http://localhost"
    mock_coordinator.device.device_id = "1"
    mock_coordinator.device.available = True
    mock_coordinator.device.firmware_version = "1.0"
    mock_coordinator.device.last_event_age = 1
    mock_coordinator.device.connection_latency = 10
    mock_coordinator.device.system_health = 100
    mock_coordinator.device._update_counter = 1
    mock_coordinator.device.consecutive_failures = 0
    mock_coordinator.config_entry = MagicMock()
    mock_coordinator.config_entry.data = {}

    # Make get_coordinator_for_device awaitable
    async def get_coordinator(*args, **kwargs):
        return mock_coordinator

    manager.get_coordinator_for_device = MagicMock(side_effect=get_coordinator)

    # Execute
    result = await handlers.handle_export_diagnostic_logs(call)

    # Check if error message is in logs
    logs = result["logs"]
    # Error should be gone
    assert "Error retrieving system info" not in logs
    # HA Version should be present
    from homeassistant.const import __version__ as HA_VERSION
    assert f"Home Assistant: {HA_VERSION}" in logs

@pytest.mark.asyncio
async def test_hacs_version_display(hass):
    # Setup hass with a restricted Config object
    real_config = RealConfig()
    hass.config = real_config

    # Mock HACS
    mock_hacs = MagicMock()
    mock_hacs.version = "1.2.3"
    hass.data["hacs"] = mock_hacs

    # Mock manager
    manager = VioletServiceManager(hass)
    handlers = VioletServiceHandlers(manager)

    # Mock call data
    call = MagicMock()
    call.data = {"device_id": ["test_device"]}

    # Mock manager.get_coordinator_for_device to return a coordinator
    mock_coordinator = MagicMock()
    mock_coordinator.device.device_name = "Test Device"
    mock_coordinator.device.controller_name = "Violet"
    mock_coordinator.device.api_url = "http://localhost"
    mock_coordinator.device.device_id = "1"
    mock_coordinator.device.available = True
    mock_coordinator.device.firmware_version = "1.0"
    mock_coordinator.device.last_event_age = 1
    mock_coordinator.device.connection_latency = 10
    mock_coordinator.device.system_health = 100
    mock_coordinator.device._update_counter = 1
    mock_coordinator.device.consecutive_failures = 0
    mock_coordinator.config_entry = MagicMock()
    mock_coordinator.config_entry.data = {}

    # Make get_coordinator_for_device awaitable
    async def get_coordinator(*args, **kwargs):
        return mock_coordinator

    manager.get_coordinator_for_device = MagicMock(side_effect=get_coordinator)

    # Execute
    result = await handlers.handle_export_diagnostic_logs(call)

    # Check for HACS version
    logs = result["logs"]
    assert "HACS: 1.2.3" in logs
