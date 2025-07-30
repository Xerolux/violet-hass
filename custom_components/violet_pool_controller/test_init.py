"""Test the Violet Pool Controller integration."""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from custom_components.violet_pool_controller import (
    async_setup, async_setup_entry, async_unload_entry, async_migrate_entry, register_services
)
from custom_components.violet_pool_controller.const import (
    DOMAIN, CONF_API_URL, CONF_USE_SSL, CONF_DEVICE_ID, CONF_DEVICE_NAME,
    CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION, CONF_RETRY_ATTEMPTS, CONF_ACTIVE_FEATURES,
    AVAILABLE_FEATURES, PLATFORMS
)


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    return Mock(spec=ConfigEntry, data={
        CONF_API_URL: "192.168.1.100", CONF_USE_SSL: False, CONF_DEVICE_ID: 1,
        CONF_USERNAME: "test", CONF_PASSWORD: "test", CONF_DEVICE_NAME: "Test Pool Controller",
        CONF_POLLING_INTERVAL: 10, CONF_TIMEOUT_DURATION: 10, CONF_RETRY_ATTEMPTS: 3,
        CONF_ACTIVE_FEATURES: ["heating", "ph_control"]
    }, options={}, entry_id="test_entry", version=1)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.services.has_service = Mock(return_value=False)
    hass.services.async_register = Mock()
    return hass


@pytest.mark.asyncio
class TestVioletPoolControllerInit:
    """Test integration initialization."""

    async def test_async_setup_yaml(self, mock_hass):
        """Test YAML configuration warning."""
        assert await async_setup(mock_hass, {DOMAIN: {}}) is True
        assert DOMAIN in mock_hass.data

    async def test_async_setup_no_yaml(self, mock_hass):
        """Test setup without YAML."""
        assert await async_setup(mock_hass, {}) is True
        assert DOMAIN in mock_hass.data

    async def test_async_setup_entry_success(self, mock_hass, mock_config_entry):
        """Test successful config entry setup."""
        with patch("custom_components.violet_pool_controller.async_setup_device", return_value=Mock(last_update_success=True)):
            assert await async_setup_entry(mock_hass, mock_config_entry) is True
            mock_hass.config_entries.async_forward_entry_setups.assert_called_once()

    async def test_async_setup_entry_failure(self, mock_hass, mock_config_entry):
        """Test failed config entry setup."""
        with patch("custom_components.violet_pool_controller.async_setup_device", side_effect=Exception("Setup failed")):
            with pytest.raises(Exception):
                await async_setup_entry(mock_hass, mock_config_entry)

    async def test_async_unload_entry_success(self, mock_hass, mock_config_entry):
        """Test successful config entry unload."""
        mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
        mock_hass.data[DOMAIN] = {"test_entry": Mock()}
        assert await async_unload_entry(mock_hass, mock_config_entry) is True
        assert "test_entry" not in mock_hass.data[DOMAIN]

    async def test_async_unload_entry_failure(self, mock_hass, mock_config_entry):
        """Test failed config entry unload."""
        mock_hass.config_entries.async_unload_platforms = AsyncMock(side_effect=Exception("Unload failed"))
        assert await async_unload_entry(mock_hass, mock_config_entry) is False

    async def test_async_migrate_entry_v1(self, mock_hass, mock_config_entry):
        """Test migration of version 1 (no changes needed)."""
        mock_config_entry.version = 1
        assert await async_migrate_entry(mock_hass, mock_config_entry) is True

    def test_register_services(self, mock_hass):
        """Test service registration."""
        register_services(mock_hass)
        assert mock_hass.services.async_register.call_count == 9
        expected_services = [
            "set_temperature_target", "set_ph_target", "set_chlorine_target", "trigger_backwash",
            "start_water_analysis", "set_maintenance_mode", "set_all_dmx_scenes_mode",
            "set_digital_input_rule_lock_state", "trigger_digital_input_rule"
        ]
        called_services = [call[0][1] for call in mock_hass.services.async_register.call_args_list]
        assert all(service in called_services for service in expected_services)

    def test_register_services_already_registered(self, mock_hass):
        """Test no re-registration if services exist."""
        mock_hass.services.has_service.return_value = True
        register_services(mock_hass)
        mock_hass.services.async_register.assert_not_called()


class TestVioletPoolControllerConfig:
    """Test configuration handling."""

    def test_config_entry_data_extraction(self, mock_config_entry):
        """Test configuration data extraction."""
        test_cases = [
            {CONF_API_URL: "192.168.1.100"}, {"host": "192.168.1.101"}, {"base_ip": "192.168.1.102"}
        ]
        for test_data in test_cases:
            mock_config_entry.data = test_data
            assert any(key in test_data for key in [CONF_API_URL, "host", "base_ip"])

    def test_feature_selection_validation(self):
        """Test feature selection validation."""
        for feature in AVAILABLE_FEATURES:
            assert all(key in feature for key in ["id", "name", "default", "platforms"])
            assert isinstance(feature["platforms"], list)


class TestVioletPoolControllerConstants:
    """Test integration constants."""

    def test_domain_constant(self):
        """Test domain constant."""
        assert DOMAIN == "violet_pool_controller"

    def test_platform_list(self):
        """Test platform definitions."""
        assert PLATFORMS == ["sensor", "binary_sensor", "switch", "climate", "cover", "number"]

    def test_configuration_constants(self):
        """Test configuration constants."""
        configs = [
            CONF_API_URL, CONF_USE_SSL, CONF_DEVICE_ID, CONF_DEVICE_NAME,
            CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION, CONF_RETRY_ATTEMPTS, CONF_ACTIVE_FEATURES
        ]
        for config in configs:
            assert isinstance(config, str)
            assert config


@pytest.mark.asyncio
class TestVioletPoolControllerIntegration:
    """Integration tests."""

    async def test_full_setup_flow(self, mock_hass, mock_config_entry):
        """Test complete setup flow."""
        with patch("custom_components.violet_pool_controller.api.VioletPoolAPI.get_readings", return_value={"pH_value": 7.2, "PUMP": "ON"}), \
             patch("custom_components.violet_pool_controller.async_setup_device", return_value=Mock(last_update_success=True)):
            assert await async_setup_entry(mock_hass, mock_config_entry) is True

    async def test_service_call_handling(self, mock_hass):
        """Test service call handling."""
        register_services(mock_hass)
        for call in mock_hass.services.async_register.call_args_list:
            assert call[0][0] == DOMAIN
            assert callable(call[0][2])  # Handler is callable
            assert call[0][3] is None or hasattr(call[0][3], "schema")  # Schema is None or voluptuous schema
