"""Tests for setpoint cache invalidation after successful polls."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.device import (
    VioletPoolControllerDevice,
    VioletPoolDataUpdateCoordinator,
)


class TestSetpointCacheInvalidation:
    """Test setpoint cache invalidation after polls."""

    @pytest.fixture
    def mock_api(self):
        """Create mock API instance."""
        api = MagicMock()
        # Initial response
        api.get_readings = AsyncMock(
            return_value={
                "POOL_TEMP": 24.5,
                "SOLAR_TEMP": 30.0,
            }
        )
        return api

    @pytest.fixture
    def config_entry(self):
        """Create mock config entry."""
        return MockConfigEntry(
            domain=DOMAIN,
            title="Test Pool",
            data={
                CONF_API_URL: "192.168.178.55",
                CONF_USE_SSL: False,
                CONF_DEVICE_ID: 1,
                CONF_DEVICE_NAME: "Test Pool Controller",
                CONF_CONTROLLER_NAME: "Test Pool",
            },
        )

    @pytest.fixture
    def device(self, hass: HomeAssistant, config_entry, mock_api):
        """Create device instance."""
        with patch(
            "custom_components.violet_pool_controller.device.async_get_clientsession",
            return_value=MagicMock(),
        ):
            device = VioletPoolControllerDevice(
                hass=hass,
                config_entry=config_entry,
                api=mock_api,
            )
            return device

    @pytest.fixture
    def coordinator(self, hass: HomeAssistant, device):
        """Create coordinator instance."""
        coordinator = VioletPoolDataUpdateCoordinator(
            hass=hass,
            device=device,
            name="test_coordinator",
            polling_interval=30,
        )
        return coordinator

    async def test_setpoint_cache_invalidated_on_poll(self, coordinator, mock_api):
        """Test that setpoint cache is invalidated after a successful poll.

        Scenario:
        1. User writes a setpoint (24.0°C) → cache populated
        2. Another client changes it to 26.0°C on the controller
        3. Coordinator polls → should get 26.0°C
        4. Cache should be invalidated for polled keys
        5. Next read should return 26.0°C, not cached 24.0°C
        """
        # Setup: Mock two different responses
        initial_response = {"POOL_TEMP": 24.0}
        updated_response = {"POOL_TEMP": 26.0}

        mock_api.get_readings = AsyncMock(side_effect=[initial_response, updated_response])

        # Step 1: Initial poll
        data1 = await coordinator._async_update_data()
        assert data1 is not None

        # Step 2: User writes a setpoint (simulate optimistic update)
        coordinator.update_setpoint_cache("POOL_TEMP", 24.0)
        assert coordinator._setpoint_cache.get("POOL_TEMP") == 24.0

        # Step 3: Another client changes controller to 26.0°C (we don't know yet)
        # Step 4: Coordinator polls again
        data2 = await coordinator._async_update_data()
        assert data2 is not None

        # Step 5: Cache should be cleared for keys that were just polled
        # The bug was: cache would never be cleared, so it would keep showing 24.0
        # After fix: cache should be cleared, allowing fresh data to show 26.0
        assert coordinator._setpoint_cache.get("POOL_TEMP") is None, (
            "Cache should be invalidated after poll for keys that exist in new data"
        )

    async def test_setpoint_cache_immediate_availability(self, coordinator):
        """Test that setpoint cache provides immediate feedback before poll.

        This verifies the positive use case: that the cache works as intended
        for immediate user feedback.
        """
        # Write to cache (simulates successful API write)
        coordinator.update_setpoint_cache("POOL_TEMP", 25.0)

        # Cache should immediately have the value
        assert coordinator._setpoint_cache.get("POOL_TEMP") == 25.0
