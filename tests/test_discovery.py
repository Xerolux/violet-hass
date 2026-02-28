"""Tests for Violet Pool Controller ZeroConf discovery (Gold Level)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.core import HomeAssistant


class TestVioletPoolControllerDiscovery:
    """Test VioletPoolControllerDiscovery class."""

    @pytest.fixture
    def discovery_handler(self):
        """Create a fresh discovery handler instance."""
        from custom_components.violet_pool_controller.discovery import (
            VioletPoolControllerDiscovery,
        )

        # Clear any existing singleton state
        import custom_components.violet_pool_controller.discovery as discovery_module

        discovery_module._discovery_handler = None

        return VioletPoolControllerDiscovery()

    @pytest.fixture
    def mock_zeroconf_info(self):
        """Create a mock ZeroConf service info."""
        info = MagicMock(spec=ZeroconfServiceInfo)
        info.name = "Violet Pool Controller._http._tcp.local."
        info.host = "192.168.178.55"
        info.port = 80
        info.hostname = "violet-pool-controller"
        info.type = "_http._tcp.local."
        return info

    def test_init_discovery_handler(self, discovery_handler):
        """Test discovery handler initialization."""
        assert discovery_handler is not None
        assert hasattr(discovery_handler, "_discovered_devices")
        assert isinstance(discovery_handler._discovered_devices, dict)
        assert len(discovery_handler._discovered_devices) == 0

    @pytest.mark.asyncio
    async def test_async_discover_service(
        self, discovery_handler, mock_zeroconf_info
    ):
        """Test discovering a service."""
        from custom_components.violet_pool_controller.discovery import (
            VioletPoolControllerDiscovery,
        )

        handler = VioletPoolControllerDiscovery()

        # Create a mock Hass instance
        mock_hass = MagicMock(spec=HomeAssistant)

        # Call discover_service
        result = handler.async_discover_service(mock_hass, mock_zeroconf_info)

        # Verify the method returns None (no ConfigFlowHandler)
        assert result is None

        # Verify the device was stored as dict
        assert mock_zeroconf_info.name in handler._discovered_devices
        device_info = handler._discovered_devices[mock_zeroconf_info.name]

        # Verify all expected fields are present
        assert device_info["host"] == "192.168.178.55"
        assert device_info["port"] == 80
        assert device_info["hostname"] == "violet-pool-controller"
        assert device_info["name"] == mock_zeroconf_info.name
        assert device_info["type"] == mock_zeroconf_info.type

    @pytest.mark.asyncio
    async def test_async_get_discovered_devices(
        self, discovery_handler, mock_zeroconf_info
    ):
        """Test getting list of discovered devices."""
        from custom_components.violet_pool_controller.discovery import (
            VioletPoolControllerDiscovery,
        )

        handler = VioletPoolControllerDiscovery()

        # Add a device manually as dict
        handler._discovered_devices[mock_zeroconf_info.name] = {
            "host": "192.168.178.55",
            "port": 80,
            "hostname": "violet-pool-controller",
            "name": mock_zeroconf_info.name,
            "type": mock_zeroconf_info.type,
        }

        # Get discovered devices
        result = handler.async_get_discovered_devices()

        assert isinstance(result, dict)
        assert mock_zeroconf_info.name in result
        assert result[mock_zeroconf_info.name]["host"] == "192.168.178.55"
        assert result[mock_zeroconf_info.name]["port"] == 80
        assert result[mock_zeroconf_info.name]["hostname"] == "violet-pool-controller"
        assert result[mock_zeroconf_info.name]["name"] == mock_zeroconf_info.name
        assert result[mock_zeroconf_info.name]["type"] == mock_zeroconf_info.type

    def test_clear_discovered_devices(self, discovery_handler, mock_zeroconf_info):
        """Test clearing all discovered devices."""
        from custom_components.violet_pool_controller.discovery import (
            VioletPoolControllerDiscovery,
        )

        handler = VioletPoolControllerDiscovery()

        # Add some devices as dicts
        handler._discovered_devices["device1"] = {
            "host": "192.168.178.55",
            "port": 80,
            "hostname": "violet-1",
            "name": "device1",
            "type": "_http._tcp.local.",
        }
        handler._discovered_devices["device2"] = {
            "host": "192.168.178.56",
            "port": 80,
            "hostname": "violet-2",
            "name": "device2",
            "type": "_http._tcp.local.",
        }

        assert len(handler._discovered_devices) == 2

        # Clear devices
        handler.clear_discovered_devices()

        assert len(handler._discovered_devices) == 0


class TestDiscoverySingleton:
    """Test the discovery handler singleton pattern."""

    def test_get_discovery_handler_singleton(self):
        """Test that get_discovery_handler returns the same instance."""
        from custom_components.violet_pool_controller.discovery import (
            get_discovery_handler,
        )

        # Clear any existing singleton
        import custom_components.violet_pool_controller.discovery as discovery_module

        discovery_module._discovery_handler = None

        # Get handler twice
        handler1 = get_discovery_handler()
        handler2 = get_discovery_handler()

        # Should be the same instance
        assert handler1 is handler2

    def test_get_discovery_handler_creates_new_instance(self):
        """Test that get_discovery_handler creates a new instance if needed."""
        from custom_components.violet_pool_controller.discovery import (
            get_discovery_handler,
            VioletPoolControllerDiscovery,
        )

        # Clear any existing singleton
        import custom_components.violet_pool_controller.discovery as discovery_module

        discovery_module._discovery_handler = None

        # Get handler
        handler = get_discovery_handler()

        # Should be a VioletPoolControllerDiscovery instance
        assert isinstance(handler, VioletPoolControllerDiscovery)


class TestZeroConfIntegration:
    """Test ZeroConf integration with __init__.py."""

    @pytest.fixture
    def mock_zeroconf_info(self):
        """Create a mock ZeroConf service info."""
        info = MagicMock(spec=ZeroconfServiceInfo)
        info.name = "Violet Pool Controller._http._tcp.local."
        info.host = "192.168.178.55"
        info.port = 80
        info.hostname = "violet-pool-controller"
        info.type = "_http._tcp.local."
        return info

    @pytest.mark.asyncio
    async def test_async_zeroconf_get_service_info(self, mock_zeroconf_info):
        """Test async_zeroconf_get_service_info in __init__.py."""
        from custom_components.violet_pool_controller import (
            async_zeroconf_get_service_info,
        )
        from custom_components.violet_pool_controller.discovery import (
            get_discovery_handler,
        )

        # Create mock Hass instance
        mock_hass = MagicMock(spec=HomeAssistant)

        # Call the function
        result = async_zeroconf_get_service_info(
            mock_hass, mock_zeroconf_info, "_http._tcp.local."
        )

        # Verify function returns None (stores info for later use)
        assert result is None

        # Verify discovery handler has the device stored
        handler = get_discovery_handler()
        assert mock_zeroconf_info.name in handler._discovered_devices


class TestDiscoveryServiceTypes:
    """Test discovery service type definitions."""

    def test_service_types_defined(self):
        """Test that service types are properly defined."""
        from custom_components.violet_pool_controller.discovery import SERVICE_TYPES

        assert isinstance(SERVICE_TYPES, list)
        assert "_http._tcp.local." in SERVICE_TYPES
        assert "_violet-controller._tcp.local." in SERVICE_TYPES

    def test_service_types_valid(self):
        """Test that service types follow mDNS format."""
        from custom_components.violet_pool_controller.discovery import SERVICE_TYPES

        for service_type in SERVICE_TYPES:
            # mDNS service types should end with ._tcp.local. or ._udp.local.
            assert (
                service_type.endswith("._tcp.local.")
                or service_type.endswith("._udp.local.")
            ), f"Invalid service type format: {service_type}"


class TestDiscoveryErrorHandling:
    """Test error handling in discovery."""

    @pytest.fixture
    def discovery_handler(self):
        """Create a fresh discovery handler instance."""
        from custom_components.violet_pool_controller.discovery import (
            VioletPoolControllerDiscovery,
        )

        # Clear any existing singleton state
        import custom_components.violet_pool_controller.discovery as discovery_module

        discovery_module._discovery_handler = None

        return VioletPoolControllerDiscovery()

    @pytest.mark.asyncio
    async def test_discover_service_with_invalid_info(self, discovery_handler):
        """Test discovering service with invalid info."""
        from custom_components.violet_pool_controller.discovery import (
            VioletPoolControllerDiscovery,
        )

        handler = VioletPoolControllerDiscovery()

        # Create invalid service info with None values
        invalid_info = MagicMock(spec=ZeroconfServiceInfo)
        invalid_info.name = "Invalid Device"
        invalid_info.host = None
        invalid_info.port = None
        invalid_info.hostname = None
        invalid_info.type = "_http._tcp.local."

        # Create mock Hass
        mock_hass = MagicMock(spec=HomeAssistant)

        # Should handle gracefully - still stores the device even with None values
        # (Real HA will filter invalid devices before calling this)
        result = handler.async_discover_service(mock_hass, invalid_info)

        # Verify it returns None
        assert result is None

        # Verify device was stored (even with partial/invalid data)
        assert "Invalid Device" in handler._discovered_devices

    def test_get_discovered_devices_empty(self, discovery_handler):
        """Test getting discovered devices when none exist."""
        result = discovery_handler.async_get_discovered_devices()

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_clear_empty_devices(self, discovery_handler):
        """Test clearing devices when none exist."""
        # Should not raise an exception
        discovery_handler.clear_discovered_devices()

        assert len(discovery_handler._discovered_devices) == 0


class TestDiscoveryMultipleDevices:
    """Test discovering multiple controllers."""

    @pytest.fixture
    def discovery_handler(self):
        """Create a fresh discovery handler instance."""
        from custom_components.violet_pool_controller.discovery import (
            VioletPoolControllerDiscovery,
        )

        # Clear any existing singleton state
        import custom_components.violet_pool_controller.discovery as discovery_module

        discovery_module._discovery_handler = None

        return VioletPoolControllerDiscovery()

    @pytest.mark.asyncio
    async def test_discover_multiple_controllers(self, discovery_handler):
        """Test discovering multiple pool controllers."""
        from custom_components.violet_pool_controller.discovery import (
            VioletPoolControllerDiscovery,
        )

        handler = VioletPoolControllerDiscovery()
        mock_hass = MagicMock(spec=HomeAssistant)

        # Create multiple device infos
        device1 = MagicMock(spec=ZeroconfServiceInfo)
        device1.name = "Violet Pool Controller 1._http._tcp.local."
        device1.host = "192.168.178.55"
        device1.port = 80
        device1.hostname = "violet-1"
        device1.type = "_http._tcp.local."

        device2 = MagicMock(spec=ZeroconfServiceInfo)
        device2.name = "Violet Pool Controller 2._http._tcp.local."
        device2.host = "192.168.178.56"
        device2.port = 80
        device2.hostname = "violet-2"
        device2.type = "_http._tcp.local."

        # Discover both devices - should return None
        result1 = handler.async_discover_service(mock_hass, device1)
        result2 = handler.async_discover_service(mock_hass, device2)

        # Verify both return None
        assert result1 is None
        assert result2 is None

        # Verify both are stored as dicts
        assert len(handler._discovered_devices) == 2
        assert device1.name in handler._discovered_devices
        assert device2.name in handler._discovered_devices

        # Get discovered devices
        result = handler.async_get_discovered_devices()

        assert len(result) == 2
        assert result[device1.name]["host"] == "192.168.178.55"
        assert result[device2.name]["host"] == "192.168.178.56"

    @pytest.mark.asyncio
    async def test_discover_duplicate_device(self, discovery_handler):
        """Test discovering the same device twice (update)."""
        from custom_components.violet_pool_controller.discovery import (
            VioletPoolControllerDiscovery,
        )

        handler = VioletPoolControllerDiscovery()
        mock_hass = MagicMock(spec=HomeAssistant)

        # Create device info
        device = MagicMock(spec=ZeroconfServiceInfo)
        device.name = "Violet Pool Controller._http._tcp.local."
        device.host = "192.168.178.55"
        device.port = 80
        device.hostname = "violet-pool-controller"
        device.type = "_http._tcp.local."

        # Discover device twice - both should return None
        result1 = handler.async_discover_service(mock_hass, device)
        result2 = handler.async_discover_service(mock_hass, device)

        # Verify both return None
        assert result1 is None
        assert result2 is None

        # Should only have one entry (updated/overwritten)
        assert len(handler._discovered_devices) == 1
        assert device.name in handler._discovered_devices
