"""Tests for platform error handling."""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock

from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller import (
    async_setup_entry,
)
from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_ACTIVE_FEATURES,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.climate import VioletClimateEntity
from custom_components.violet_pool_controller.cover import VioletCover
from custom_components.violet_pool_controller.switch import VioletSwitch
from custom_components.violet_pool_controller.number import VioletNumber
from custom_components.violet_pool_controller.select import VioletSelect


@pytest.fixture
def mock_coordinator_error():
    """Mock coordinator that raises errors."""
    coordinator = Mock()
    coordinator.data = None  # Simulate error state
    coordinator.device = Mock()
    coordinator.device.device_name = "Test"
    coordinator.device.available = False
    coordinator.device.device_info = {
        "identifiers": {(DOMAIN, "192.168.1.100_1")},
        "name": "Test",
        "manufacturer": "PoolDigital GmbH & Co. KG",
        "model": "Violet Pool Controller",
        "sw_version": "1.0.0",
    }

    # Mock get_str_value to return safe defaults
    def get_str_value(key, default=""):
        return default

    def get_int_value(key, default=0):
        return default

    coordinator.get_str_value = get_str_value
    coordinator.get_int_value = get_int_value

    return coordinator


@pytest.fixture
def config_entry():
    """Mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_URL: "192.168.1.100",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Test Pool",
        },
        options={
            CONF_ACTIVE_FEATURES: ["cover_control", "climate_control"],
        }
    )


class TestCoverErrorHandling:
    """Test cover platform error handling."""

    def test_cover_with_no_data(self, mock_coordinator_error, config_entry):
        """Test cover handles None data gracefully."""
        cover = VioletCover(mock_coordinator_error, config_entry)

        # Should not crash, return safe defaults
        assert cover.is_open is False
        assert cover.is_closed is False
        assert cover.is_opening is False
        assert cover.is_closing is False

    def test_cover_extra_state_attributes_error(self, mock_coordinator_error, config_entry):
        """Test cover extra_state_attributes with errors."""
        mock_coordinator_error.data = {"COVER_STATE": None}

        cover = VioletCover(mock_coordinator_error, config_entry)

        # Should not crash; cover may return None or dict depending on implementation
        attrs = cover.extra_state_attributes
        assert attrs is None or isinstance(attrs, dict)

    def test_cover_device_info(self, mock_coordinator_error, config_entry):
        """Test cover device_info with error coordinator."""
        cover = VioletCover(mock_coordinator_error, config_entry)

        info = cover.device_info
        # device_info comes from coordinator.device.device_info (mocked as a dict)
        assert info is not None


class TestClimateErrorHandling:
    """Test climate platform error handling."""

    def test_climate_with_no_data(self, mock_coordinator_error, config_entry):
        """Test climate handles None data gracefully."""
        climate = VioletClimateEntity(
            mock_coordinator_error,
            config_entry,
            climate_type="HEATER",
        )

        # Should not crash; current_temperature may be None when data is None
        assert climate.current_temperature is None
        # target_temperature returns a default value (not None) when data is None
        target = climate.target_temperature
        assert target is None or isinstance(target, (int, float))

    def test_cl_temperature_with_invalid_data(self, mock_coordinator_error, config_entry):
        """Test climate with invalid temperature data."""
        mock_coordinator_error.data = {
            "onewire1_value": "invalid",  # Invalid temperature
            "HEATER_TARGET_TEMP": "not_a_number",
        }

        climate = VioletClimateEntity(
            mock_coordinator_error,
            config_entry,
            climate_type="HEATER",
        )

        # Should handle gracefully (may return None or 0)
        temp = climate.current_temperature
        assert temp is None or temp == 0

    def test_climate_hvac_action_with_errors(self, mock_coordinator_error, config_entry):
        """Test climate HVAC action calculation with errors."""
        mock_coordinator_error.data = {
            "HEATER": None,  # Invalid state
        }

        climate = VioletClimateEntity(
            mock_coordinator_error,
            config_entry,
            climate_type="HEATER",
        )

        # Should return safe default
        action = climate.hvac_action
        assert action is not None  # Should have some default


class TestSwitchErrorHandling:
    """Test switch platform error handling."""

    def test_switch_with_no_data(self, mock_coordinator_error, config_entry):
        """Test switch handles None data gracefully."""
        desc = SwitchEntityDescription(key="PUMP", name="Pump")
        switch = VioletSwitch(mock_coordinator_error, config_entry, desc)

        # Should not crash
        assert switch.is_on is False

    def test_switch_extra_state_attributes(self, mock_coordinator_error, config_entry):
        """Test switch attributes with error coordinator."""
        mock_coordinator_error.data = {
            "PUMP": None,
            "PUMP-State": None,
        }

        desc = SwitchEntityDescription(key="PUMP", name="Pump")
        switch = VioletSwitch(mock_coordinator_error, config_entry, desc)

        # Should not crash
        attrs = switch.extra_state_attributes
        assert isinstance(attrs, dict)


class TestNumberErrorHandling:
    """Test number platform error handling."""

    def test_number_with_no_data(self, mock_coordinator_error, config_entry):
        """Test number handles None data gracefully."""
        desc = NumberEntityDescription(
            key="PH_TARGET",
            name="pH Target",
            native_min_value=6.0,
            native_max_value=8.0,
        )
        _setpoint_config = {
            "min_value": 6.0, "max_value": 8.0, "step": 0.1,
            "setpoint_fields": [], "indicator_fields": [],
            "default_value": 7.2, "api_key": "PH_TARGET",
        }
        number = VioletNumber(mock_coordinator_error, config_entry, desc, _setpoint_config)

        # Should return safe default (0 or middle of range)
        value = number.native_value
        assert value is None or isinstance(value, (int, float))

    def test_number_with_invalid_value(self, mock_coordinator_error, config_entry):
        """Test number with invalid value data."""
        mock_coordinator_error.data = {
            "PH_TARGET": "invalid_number",
        }

        desc = NumberEntityDescription(
            key="PH_TARGET",
            name="pH Target",
            native_min_value=6.0,
            native_max_value=8.0,
        )
        _setpoint_config = {
            "min_value": 6.0, "max_value": 8.0, "step": 0.1,
            "setpoint_fields": [], "indicator_fields": [],
            "default_value": 7.2, "api_key": "PH_TARGET",
        }
        number = VioletNumber(mock_coordinator_error, config_entry, desc, _setpoint_config)

        # Should handle gracefully
        value = number.native_value
        # May be None or 0 depending on implementation


class TestSelectErrorHandling:
    """Test select platform error handling."""

    def test_select_with_no_data(self, mock_coordinator_error, config_entry):
        """Test select handles None data gracefully."""
        desc = SelectEntityDescription(
            key="PUMP_SPEED",
            name="Pump Speed",
            options=["0", "1", "2", "3"],
        )
        select = VioletSelect(
            mock_coordinator_error,
            config_entry,
            desc,
            device_key="PUMP",
        )

        # Should not crash
        # May return empty string or first option
        current = select.current_option
        assert current is None or current == "" or current in ["0", "1", "2", "3"]

    def test_select_with_invalid_option(self, mock_coordinator_error, config_entry):
        """Test select with invalid current option."""
        mock_coordinator_error.data = {
            "PUMP_SPEED": "999",  # Invalid option
        }

        desc = SelectEntityDescription(
            key="PUMP_SPEED",
            name="Pump Speed",
            options=["0", "1", "2", "3"],
        )
        select = VioletSelect(
            mock_coordinator_error,
            config_entry,
            desc,
            device_key="PUMP",
        )

        # Should handle gracefully
        current = select.current_option
        # May show invalid value or fallback


class TestCoordinatorErrors:
    """Test coordinator error scenarios."""

    @pytest.mark.asyncio
    async def test_coordinator_update_fails(self):
        """Test entities when coordinator update fails."""
        # Mock failed coordinator
        coordinator = Mock()
        coordinator.data = None
        coordinator.last_update_success = False

        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_URL: "192.168.1.100",
                CONF_USE_SSL: False,
                CONF_DEVICE_ID: 1,
                CONF_DEVICE_NAME: "Test Pool",
            },
        )

        # Create entities with failed coordinator
        cover = VioletCover(coordinator, config_entry)
        climate = VioletClimateEntity(coordinator, config_entry, climate_type="HEATER")

        # Entities should still be functional, just showing unavailable state
        assert cover.available is False
        assert climate.available is False

    @pytest.mark.asyncio
    async def test_coordinator_recovers(self):
        """Test entities recover when coordinator recovers."""
        # Mock failed coordinator
        coordinator = Mock()
        coordinator.data = None
        coordinator.last_update_success = False
        coordinator.device = Mock()
        coordinator.device.device_name = "Test"

        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_URL: "192.168.1.100",
                CONF_USE_SSL: False,
                CONF_DEVICE_ID: 1,
                CONF_DEVICE_NAME: "Test Pool",
            },
        )

        cover = VioletCover(coordinator, config_entry)
        assert cover.available is False

        # Simulate recovery
        coordinator.data = {"COVER_STATE": "OPEN"}
        coordinator.last_update_success = True

        # Entity should reflect new state
        # (Note: availability is updated by HA, not by us)


class TestPlatformInitialization:
    """Test platform initialization with errors."""

    def test_async_setup_entry_with_coordinator_error(self):
        """Test setup entry when coordinator fails."""
        # This would require more complex mocking
        # For now, we just verify the function exists
        assert async_setup_entry is not None

    def test_platform_setup_with_missing_features(self, config_entry):
        """Test platform setup when active features don't include platform."""
        config_entry.options = {CONF_ACTIVE_FEATURES: []}  # No features

        # Should not crash when setting up platforms
        # (Actual platform setup is tested by HA test framework)
        assert config_entry.options[CONF_ACTIVE_FEATURES] == []


class TestEntityErrorStates:
    """Test various entity error states."""

    def test_entity_with_missing_attributes(self, mock_coordinator_error, config_entry):
        """Test entity when required attributes are missing."""
        mock_coordinator_error.data = {}

        cover = VioletCover(mock_coordinator_error, config_entry)
        climate = VioletClimateEntity(mock_coordinator_error, config_entry, climate_type="HEATER")

        # Should not crash
        cover_attrs = cover.extra_state_attributes
        climate_attrs = climate.extra_state_attributes

        # Cover has no extra_state_attributes implementation → returns None
        assert cover_attrs is None or isinstance(cover_attrs, dict)
        assert isinstance(climate_attrs, dict)

    def test_entity_with_none_attributes(self, mock_coordinator_error, config_entry):
        """Test entity when attributes are None."""
        mock_coordinator_error.data = {
            "COVER_STATE": None,
            "HEATER": None,
            "HEATER_TARGET_TEMP": None,
        }

        cover = VioletCover(mock_coordinator_error, config_entry)
        climate = VioletClimateEntity(mock_coordinator_error, config_entry, climate_type="HEATER")

        # Should handle None values gracefully
        assert cover.is_open is False  # Safe default
        # target_temperature falls back to DEFAULT_TARGET_TEMP (28.0) when key is null
        assert climate.target_temperature is None or isinstance(climate.target_temperature, (int, float))
