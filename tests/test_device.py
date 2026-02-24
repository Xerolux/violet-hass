"""Tests for Violet Pool Controller Device."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.device import VioletPoolControllerDevice


class TestVioletPoolControllerDevice:
    """Test VioletPoolControllerDevice."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = MagicMock()
        hass.data = {}
        return hass

    @pytest.fixture
    def mock_api(self):
        """Create mock API instance."""
        api = MagicMock()
        api.get_readings = AsyncMock(return_value={"test": "data"})
        api.get_specific_readings = AsyncMock(return_value={"test": "data"})
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
    def device(self, mock_hass, config_entry, mock_api):
        """Create device instance."""
        with patch("custom_components.violet_pool_controller.device.async_get_clientsession", return_value=MagicMock()):
            device = VioletPoolControllerDevice(
                hass=mock_hass,
                config_entry=config_entry,
                api=mock_api,
            )
            return device

    async def test_controller_name_in_device_info(self, device):
        """Test dass Controller-Name in device_info verwendet wird."""
        device_info = device.device_info

        assert device_info["name"] == "Test Pool", "device_info sollte Controller-Name verwenden"
        assert device_info["suggested_area"] == "Test Pool", "suggested_area sollte Controller-Name sein"

    async def test_device_info_dynamic_updates(self, device):
        """Test dass device_info bei Options-Änderung aktualisiert wird."""
        # Initial
        initial_info = device.device_info
        assert initial_info["name"] == "Test Pool"

        # Simuliere Options-Änderung
        device.controller_name = "Neuer Pool Name"

        # Device-Info sollte sofort neuen Namen zeigen (kein Caching!)
        updated_info = device.device_info
        assert updated_info["name"] == "Neuer Pool Name"
        assert updated_info["suggested_area"] == "Neuer Pool Name"
