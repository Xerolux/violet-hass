"""Tests for Violet Pool Controller Device."""

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
    FIRMWARE_VERSION_REFRESH_POLLS,
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
        with patch(
            "custom_components.violet_pool_controller.device.async_get_clientsession",
            return_value=MagicMock(),
        ):
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
        assert device_info["suggested_area"] == "Test Pool", (
            "suggested_area sollte Controller-Name sein"
        )

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

    def test_build_config_keys_always_includes_swversion_and_setpoints(self):
        """Every poll must include swversion and the setpoint keys."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = 0
        keys = device._build_config_keys()

        assert "SYSTEM_swversion" in keys
        assert "HEATER_set_temp" in keys
        assert "DOSAGE_phminus_setpoint" in keys

    def test_build_config_keys_first_poll_includes_availableversion(self):
        """Counter == 0 (first poll after start) fetches availableversion immediately."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = 0
        keys = device._build_config_keys()

        assert "SYSTEM_availableversion" in keys

    def test_build_config_keys_throttles_availableversion(self):
        """availableversion is fetched only every FIRMWARE_VERSION_REFRESH_POLLS cycles."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = 1  # not a cadence boundary
        keys = device._build_config_keys()

        assert "SYSTEM_availableversion" not in keys

    def test_build_config_keys_availableversion_again_at_cadence(self):
        """availableversion reappears exactly when counter hits a multiple of the cadence."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = FIRMWARE_VERSION_REFRESH_POLLS
        keys = device._build_config_keys()

        assert "SYSTEM_availableversion" in keys

    def test_build_config_keys_never_includes_updateavailable(self):
        """The live-server-trigger flag must NEVER be requested (value never consumed)."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        # Sweep many cycles to be sure it never shows up regardless of counter.
        device._firmware_version_poll_counter = 0
        seen_keys = set()
        for _ in range(FIRMWARE_VERSION_REFRESH_POLLS + 5):
            seen_keys.update(device._build_config_keys())

        assert "SYSTEM_updateavailable" not in seen_keys

    def test_build_config_keys_increments_counter(self):
        """Each call advances the counter by exactly 1."""
        device = VioletPoolControllerDevice.__new__(VioletPoolControllerDevice)
        device._firmware_version_poll_counter = 0
        device._build_config_keys()
        device._build_config_keys()

        assert device._firmware_version_poll_counter == 2
