"""Test the Violet Pool Controller integration."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from custom_components.violet_pool_controller import (
    async_setup,
    async_setup_entry,
    async_unload_entry,
    async_migrate_entry,
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
)


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    return Mock(spec=ConfigEntry, data={
        CONF_API_URL: "192.168.1.100",
        CONF_USE_SSL: False,
        CONF_DEVICE_ID: 1,
        CONF_USERNAME: "test",
        CONF_PASSWORD: "test",
        CONF_DEVICE_NAME: "Test Pool Controller",
        CONF_POLLING_INTERVAL: 10,
        CONF_TIMEOUT_DURATION: 10,
        CONF_RETRY_ATTEMPTS: 3,
        CONF_ACTIVE_FEATURES: ["heating", "ph_control"],
    }, options={}, entry_id="test_entry", version=1)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = Mock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.services = Mock()
    hass.services.has_service = Mock(return_value=False)
    hass.services.async_register = Mock()
    return hass


class TestVioletPoolControllerInit:
    """Test the Violet Pool Controller integration initialization."""

    async def test_async_setup_yaml_warning(self, mock_hass):
        """Test that YAML configuration shows warning."""
        config = {DOMAIN: {}}
        
        result = await async_setup(mock_hass, config)
        
        assert result is True
        assert DOMAIN in mock_hass.data

    async def test_async_setup_no_yaml(self, mock_hass):
        """Test setup without YAML configuration."""
        config = {}
        
        result = await async_setup(mock_hass, config)
        
        assert result is True
        assert DOMAIN in mock_hass.data

    @patch('custom_components.violet_pool_controller.async_setup_device')
    @patch('custom_components.violet_pool_controller.VioletPoolAPI')
    @patch('custom_components.violet_pool_controller.aiohttp_client.async_get_clientsession')
    async def test_async_setup_entry_success(
        self, mock_session, mock_api, mock_setup_device, mock_hass, mock_config_entry
    ):
        """Test successful setup of config entry."""
        mock_coordinator = Mock()
        mock_setup_device.return_value = mock_coordinator
        
        result = await async_setup_entry(mock_hass, mock_config_entry)
        
        assert result is True
        mock_setup_device.assert_called_once()
        mock_hass.config_entries.async_forward_entry_setups.assert_called_once()

    @patch('custom_components.violet_pool_controller.async_setup_device')
    async def test_async_setup_entry_failure(self, mock_setup_device, mock_hass, mock_config_entry):
        """Test failed setup of config entry."""
        mock_setup_device.side_effect = Exception("Setup failed")
        
        with pytest.raises(Exception):
            await async_setup_entry(mock_hass, mock_config_entry)

    async def test_async_unload_entry_success(self, mock_hass, mock_config_entry):
        """Test successful unload of config entry."""
        mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
        mock_hass.data[DOMAIN] = {"test_entry": Mock()}
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
        
        assert result is True
        assert "test_entry" not in mock_hass.data[DOMAIN]

    async def test_async_unload_entry_failure(self, mock_hass, mock_config_entry):
        """Test failed unload of config entry."""
        mock_hass.config_entries.async_unload_platforms = AsyncMock(side_effect=Exception("Unload failed"))
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
        
        assert result is False

    async def test_async_migrate_entry_v1(self, mock_hass, mock_config_entry):
        """Test migration of version 1 config entry (no migration needed)."""
        mock_config_entry.version = 1
        
        result = await async_migrate_entry(mock_hass, mock_config_entry)
        
        assert result is True

    def test_register_services(self, mock_hass):
        """Test service registration."""
        from custom_components.violet_pool_controller import register_services
        
        register_services(mock_hass)
        
        # Verify that services were registered
        assert mock_hass.services.async_register.call_count > 0
        
        # Check specific services
        service_calls = [call[0] for call in mock_hass.services.async_register.call_args_list]
        expected_services = [
            (DOMAIN, "set_temperature_target"),
            (DOMAIN, "set_ph_target"),
            (DOMAIN, "set_chlorine_target"),
            (DOMAIN, "trigger_backwash"),
            (DOMAIN, "start_water_analysis"),
            (DOMAIN, "set_maintenance_mode"),
            (DOMAIN, "set_all_dmx_scenes_mode"),
            (DOMAIN, "set_digital_input_rule_lock_state"),
            (DOMAIN, "trigger_digital_input_rule"),
        ]
        
        for expected_service in expected_services:
            assert expected_service in service_calls

    def test_register_services_already_registered(self, mock_hass):
        """Test that services are not re-registered if already present."""
        from custom_components.violet_pool_controller import register_services
        
        mock_hass.services.has_service.return_value = True
        
        register_services(mock_hass)
        
        # Should not register services if already present
        mock_hass.services.async_register.assert_not_called()


class TestVioletPoolControllerConfig:
    """Test configuration handling."""

    def test_config_entry_data_extraction(self, mock_config_entry):
        """Test extraction of configuration data from config entry."""
        # Test IP address extraction with different keys
        test_cases = [
            {CONF_API_URL: "192.168.1.100"},
            {"host": "192.168.1.101"},
            {"base_ip": "192.168.1.102"},
        ]
        
        for test_data in test_cases:
            mock_config_entry.data = test_data
            # This would be tested in the actual setup function
            # Here we just verify the data structure
            assert any(key in test_data for key in [CONF_API_URL, "host", "base_ip"])

    def test_feature_selection_validation(self):
        """Test that feature selection validates correctly."""
        from custom_components.violet_pool_controller.const import AVAILABLE_FEATURES
        
        # Verify all features have required fields
        for feature in AVAILABLE_FEATURES:
            assert "id" in feature
            assert "name" in feature
            assert "default" in feature
            assert "platforms" in feature
            assert isinstance(feature["platforms"], list)


class TestVioletPoolControllerConstants:
    """Test integration constants."""

    def test_domain_constant(self):
        """Test that domain constant is correct."""
        assert DOMAIN == "violet_pool_controller"

    def test_platform_list(self):
        """Test that all required platforms are defined."""
        from custom_components.violet_pool_controller import PLATFORMS
        
        expected_platforms = [
            "sensor",
            "binary_sensor",
            "switch",
            "climate",
            "cover",
            "number",
        ]
        
        assert PLATFORMS == expected_platforms

    def test_configuration_constants(self):
        """Test that all configuration constants are defined."""
        required_configs = [
            CONF_API_URL,
            CONF_USE_SSL,
            CONF_DEVICE_ID,
            CONF_DEVICE_NAME,
            CONF_POLLING_INTERVAL,
            CONF_TIMEOUT_DURATION,
            CONF_RETRY_ATTEMPTS,
            CONF_ACTIVE_FEATURES,
        ]
        
        for config in required_configs:
            assert isinstance(config, str)
            assert len(config) > 0


# Integration Tests
@pytest.mark.integration
class TestVioletPoolControllerIntegration:
    """Integration tests for the Violet Pool Controller."""

    @patch('custom_components.violet_pool_controller.api.VioletPoolAPI')
    async def test_full_setup_flow(self, mock_api, mock_hass, mock_config_entry):
        """Test the complete setup flow."""
        # Mock successful API connection
        mock_api_instance = Mock()
        mock_api_instance.get_readings.return_value = {"pH_value": 7.2, "PUMP": "ON"}
        mock_api.return_value = mock_api_instance
        
        with patch('custom_components.violet_pool_controller.async_setup_device') as mock_setup:
            mock_coordinator = Mock()
            mock_coordinator.last_update_success = True
            mock_setup.return_value = mock_coordinator
            
            result = await async_setup_entry(mock_hass, mock_config_entry)
            assert result is True

    async def test_service_call_handling(self, mock_hass):
        """Test service call handling."""
        from custom_components.violet_pool_controller import register_services
        
        # Register services
        register_services(mock_hass)
        
        # Verify service schemas are valid
        service_calls = mock_hass.services.async_register.call_args_list
        
        for call in service_calls:
            domain, service_name, handler, schema = call[0][:4]
            assert domain == DOMAIN
            assert callable(handler)
            # Schema should be a voluptuous schema or None
            assert schema is None or hasattr(schema, 'schema')


if __name__ == "__main__":
    pytest.main([__file__])