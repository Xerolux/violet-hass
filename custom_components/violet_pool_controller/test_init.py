"""Test the Violet Pool Controller integration."""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.violet_pool_controller import (
    async_setup, 
    async_setup_entry, 
    async_unload_entry, 
    async_migrate_entry, 
    register_services
)
from custom_components.violet_pool_controller.const import (
    DOMAIN, 
    CONF_API_URL, 
    CONF_USE_SSL, 
    CONF_DEVICE_ID, 
    CONF_DEVICE_NAME,
    CONF_POLLING_INTERVAL, 
    CONF_TIMEOUT_DURATION, 
    CONF_RETRY_ATTEMPTS, 
    CONF_ACTIVE_FEATURES,
    AVAILABLE_FEATURES, 
    PLATFORMS
)


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = Mock(spec=ConfigEntry)
    entry.data = {
        CONF_API_URL: "192.168.1.100",
        CONF_USE_SSL: False,
        CONF_DEVICE_ID: 1,
        CONF_USERNAME: "test",
        CONF_PASSWORD: "test",
        CONF_DEVICE_NAME: "Test Pool Controller",
        CONF_POLLING_INTERVAL: 10,
        CONF_TIMEOUT_DURATION: 10,
        CONF_RETRY_ATTEMPTS: 3,
        CONF_ACTIVE_FEATURES: ["heating", "ph_control"]
    }
    entry.options = {}
    entry.entry_id = "test_entry"
    entry.version = 1
    entry.title = "Test Pool Controller"
    return entry


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = Mock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.services = Mock()
    hass.services.has_service = Mock(return_value=False)
    hass.services.async_register = Mock()
    return hass


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = Mock()
    coordinator.data = {
        "pH_value": 7.2,
        "PUMP": "ON",
        "TEMP": 25.5,
        "FW": "1.2.3"
    }
    coordinator.last_update_success = True
    coordinator.device = Mock()
    coordinator.device.available = True
    coordinator.device.firmware_version = "1.2.3"
    coordinator.device.device_info = {
        "identifiers": {(DOMAIN, "test_device")},
        "name": "Test Pool Controller",
        "manufacturer": "PoolDigital GmbH & Co. KG",
        "model": "Violet Pool Controller",
        "sw_version": "1.2.3"
    }
    return coordinator


@pytest.mark.asyncio
class TestVioletPoolControllerInit:
    """Test integration initialization."""

    async def test_async_setup_yaml(self, mock_hass):
        """Test YAML configuration warning."""
        result = await async_setup(mock_hass, {DOMAIN: {}})
        assert result is True
        assert DOMAIN in mock_hass.data

    async def test_async_setup_no_yaml(self, mock_hass):
        """Test setup without YAML."""
        result = await async_setup(mock_hass, {})
        assert result is True
        assert DOMAIN in mock_hass.data

    async def test_async_setup_entry_success(self, mock_hass, mock_config_entry, mock_coordinator):
        """Test successful config entry setup."""
        with patch(
            "custom_components.violet_pool_controller.async_setup_device",
            return_value=mock_coordinator
        ):
            result = await async_setup_entry(mock_hass, mock_config_entry)
            assert result is True
            mock_hass.config_entries.async_forward_entry_setups.assert_called_once()
            
            # Verify coordinator is stored in hass.data
            assert DOMAIN in mock_hass.data
            assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]

    async def test_async_setup_entry_failure(self, mock_hass, mock_config_entry):
        """Test failed config entry setup."""
        with patch(
            "custom_components.violet_pool_controller.async_setup_device",
            side_effect=ConfigEntryNotReady("Setup failed")
        ):
            with pytest.raises(ConfigEntryNotReady):
                await async_setup_entry(mock_hass, mock_config_entry)

    async def test_async_setup_entry_api_error(self, mock_hass, mock_config_entry):
        """Test setup failure due to API error."""
        with patch(
            "custom_components.violet_pool_controller.async_setup_device",
            side_effect=Exception("API connection failed")
        ):
            with pytest.raises(Exception):
                await async_setup_entry(mock_hass, mock_config_entry)

    async def test_async_unload_entry_success(self, mock_hass, mock_config_entry):
        """Test successful config entry unload."""
        mock_hass.data[DOMAIN] = {mock_config_entry.entry_id: Mock()}
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
        
        assert result is True
        assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]
        mock_hass.config_entries.async_unload_platforms.assert_called_once_with(
            mock_config_entry,
            PLATFORMS
        )

    async def test_async_unload_entry_failure(self, mock_hass, mock_config_entry):
        """Test failed config entry unload."""
        mock_hass.config_entries.async_unload_platforms = AsyncMock(
            side_effect=Exception("Unload failed")
        )
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
        
        assert result is False

    async def test_async_unload_entry_no_data(self, mock_hass, mock_config_entry):
        """Test unload when entry not in hass.data."""
        mock_hass.data[DOMAIN] = {}
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
        
        # Should still try to unload platforms
        assert result is True

    async def test_async_migrate_entry_v1(self, mock_hass, mock_config_entry):
        """Test migration of version 1 (no changes needed)."""
        mock_config_entry.version = 1
        
        result = await async_migrate_entry(mock_hass, mock_config_entry)
        
        assert result is True

    async def test_async_migrate_entry_future_version(self, mock_hass, mock_config_entry):
        """Test migration rejects future versions."""
        mock_config_entry.version = 2
        
        result = await async_migrate_entry(mock_hass, mock_config_entry)
        
        # Should reject unknown future versions
        assert result is False

    def test_register_services(self, mock_hass):
        """Test service registration."""
        register_services(mock_hass)
        
        # Should register all expected services
        assert mock_hass.services.async_register.call_count == 9
        
        expected_services = [
            "set_temperature_target",
            "set_ph_target",
            "set_chlorine_target",
            "trigger_backwash",
            "start_water_analysis",
            "set_maintenance_mode",
            "set_all_dmx_scenes_mode",
            "set_digital_input_rule_lock_state",
            "trigger_digital_input_rule"
        ]
        
        called_services = [
            call[0][1] for call in mock_hass.services.async_register.call_args_list
        ]
        
        for service in expected_services:
            assert service in called_services

    def test_register_services_already_registered(self, mock_hass):
        """Test no re-registration if services exist."""
        mock_hass.services.has_service.return_value = True
        
        register_services(mock_hass)
        
        # Should not register any services
        mock_hass.services.async_register.assert_not_called()


class TestVioletPoolControllerConfig:
    """Test configuration handling."""

    def test_config_entry_data_extraction(self, mock_config_entry):
        """Test configuration data extraction."""
        # Test different possible IP address keys
        test_cases = [
            {CONF_API_URL: "192.168.1.100"},
            {"host": "192.168.1.101"},
            {"base_ip": "192.168.1.102"}
        ]
        
        for test_data in test_cases:
            mock_config_entry.data = test_data
            assert any(key in test_data for key in [CONF_API_URL, "host", "base_ip"])

    def test_config_entry_with_auth(self, mock_config_entry):
        """Test configuration with authentication."""
        assert CONF_USERNAME in mock_config_entry.data
        assert CONF_PASSWORD in mock_config_entry.data
        assert mock_config_entry.data[CONF_USERNAME] == "test"
        assert mock_config_entry.data[CONF_PASSWORD] == "test"

    def test_config_entry_without_auth(self):
        """Test configuration without authentication."""
        entry = Mock(spec=ConfigEntry)
        entry.data = {
            CONF_API_URL: "192.168.1.100",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1
        }
        
        # Should handle missing auth gracefully
        assert entry.data.get(CONF_USERNAME, "") == ""
        assert entry.data.get(CONF_PASSWORD, "") == ""

    def test_feature_selection_validation(self):
        """Test feature selection validation."""
        for feature in AVAILABLE_FEATURES:
            # Each feature must have these keys
            assert "id" in feature
            assert "name" in feature
            assert "default" in feature
            assert "platforms" in feature
            
            # Platforms must be a list
            assert isinstance(feature["platforms"], list)
            
            # Each platform must be valid
            for platform in feature["platforms"]:
                assert platform in PLATFORMS

    def test_polling_interval_validation(self, mock_config_entry):
        """Test polling interval validation."""
        interval = mock_config_entry.data[CONF_POLLING_INTERVAL]
        
        # Should be within valid range
        assert 10 <= interval <= 3600

    def test_retry_attempts_validation(self, mock_config_entry):
        """Test retry attempts validation."""
        retries = mock_config_entry.data[CONF_RETRY_ATTEMPTS]
        
        # Should be within valid range
        assert 1 <= retries <= 10


class TestVioletPoolControllerConstants:
    """Test integration constants."""

    def test_domain_constant(self):
        """Test domain constant."""
        assert DOMAIN == "violet_pool_controller"
        assert isinstance(DOMAIN, str)

    def test_platform_list(self):
        """Test platform definitions."""
        expected_platforms = [
            "sensor",
            "binary_sensor",
            "switch",
            "climate",
            "cover",
            "number"
        ]
        
        assert PLATFORMS == expected_platforms
        assert isinstance(PLATFORMS, list)

    def test_configuration_constants(self):
        """Test configuration constants exist and are strings."""
        configs = [
            CONF_API_URL,
            CONF_USE_SSL,
            CONF_DEVICE_ID,
            CONF_DEVICE_NAME,
            CONF_POLLING_INTERVAL,
            CONF_TIMEOUT_DURATION,
            CONF_RETRY_ATTEMPTS,
            CONF_ACTIVE_FEATURES
        ]
        
        for config in configs:
            assert isinstance(config, str)
            assert config  # Not empty
            assert len(config) > 0


@pytest.mark.asyncio
class TestVioletPoolControllerIntegration:
    """Integration tests."""

    async def test_full_setup_flow(self, mock_hass, mock_config_entry, mock_coordinator):
        """Test complete setup flow."""
        with patch(
            "custom_components.violet_pool_controller.api.VioletPoolAPI.get_readings",
            return_value={"pH_value": 7.2, "PUMP": "ON"}
        ), patch(
            "custom_components.violet_pool_controller.async_setup_device",
            return_value=mock_coordinator
        ):
            result = await async_setup_entry(mock_hass, mock_config_entry)
            
            assert result is True
            assert DOMAIN in mock_hass.data
            assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]

    async def test_full_setup_and_unload_flow(self, mock_hass, mock_config_entry, mock_coordinator):
        """Test complete setup and unload flow."""
        # Setup
        with patch(
            "custom_components.violet_pool_controller.async_setup_device",
            return_value=mock_coordinator
        ):
            setup_result = await async_setup_entry(mock_hass, mock_config_entry)
            assert setup_result is True
        
        # Unload
        unload_result = await async_unload_entry(mock_hass, mock_config_entry)
        assert unload_result is True
        assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]

    def test_service_call_handling(self, mock_hass):
        """Test service call handling."""
        register_services(mock_hass)
        
        # Verify each service registration
        for call in mock_hass.services.async_register.call_args_list:
            domain, service, handler, schema = call[0]
            
            # Domain should be correct
            assert domain == DOMAIN
            
            # Handler should be callable
            assert callable(handler)
            
            # Schema should be None or a valid schema object
            assert schema is None or hasattr(schema, "schema")

    async def test_reload_on_options_change(self, mock_hass, mock_config_entry, mock_coordinator):
        """Test that changing options triggers reload."""
        with patch(
            "custom_components.violet_pool_controller.async_setup_device",
            return_value=mock_coordinator
        ):
            # Initial setup
            await async_setup_entry(mock_hass, mock_config_entry)
            
            # Change options
            mock_config_entry.options = {
                CONF_POLLING_INTERVAL: 30,
                CONF_ACTIVE_FEATURES: ["heating", "ph_control", "solar"]
            }
            
            # This would typically trigger async_reload in real HA
            # Here we just verify the entry can be unloaded and reloaded
            unload_ok = await async_unload_entry(mock_hass, mock_config_entry)
            assert unload_ok is True
            
            setup_ok = await async_setup_entry(mock_hass, mock_config_entry)
            assert setup_ok is True


class TestVioletPoolControllerErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_setup_with_invalid_ip(self, mock_hass):
        """Test setup with invalid IP address."""
        invalid_entry = Mock(spec=ConfigEntry)
        invalid_entry.data = {
            CONF_API_URL: "invalid.ip.address",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1
        }
        invalid_entry.entry_id = "test_invalid"
        
        with patch(
            "custom_components.violet_pool_controller.async_setup_device",
            side_effect=ValueError("Invalid IP address")
        ):
            with pytest.raises(ValueError):
                await async_setup_entry(mock_hass, invalid_entry)

    @pytest.mark.asyncio
    async def test_setup_device_not_reachable(self, mock_hass, mock_config_entry):
        """Test setup when device is not reachable."""
        with patch(
            "custom_components.violet_pool_controller.async_setup_device",
            side_effect=ConfigEntryNotReady("Device not reachable")
        ):
            with pytest.raises(ConfigEntryNotReady):
                await async_setup_entry(mock_hass, mock_config_entry)

    @pytest.mark.asyncio
    async def test_unload_with_platform_error(self, mock_hass, mock_config_entry):
        """Test unload when platform unload fails."""
        mock_hass.data[DOMAIN] = {mock_config_entry.entry_id: Mock()}
        mock_hass.config_entries.async_unload_platforms = AsyncMock(
            return_value=False
        )
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
        
        # Should return False but not crash
        assert result is False