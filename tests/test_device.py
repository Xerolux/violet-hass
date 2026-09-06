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


class TestHardwareModuleDetection:
    """Module presence must follow the alive-count keys, not raw EXT* keys.

    Regression: the firmware reports every EXT1_/EXT2_ key - with stale
    values for relays of a module that is not connected - and the output
    runtime merge re-imports those zombie keys after the API package
    filtered them out of getReadings. Prefix matching therefore listed a
    second relay extension for a pool that has only one.
    """

    @pytest.fixture
    def device(self):
        """Create a device instance with a mocked API."""
        hass = MagicMock()
        hass.data = {}
        entry = MockConfigEntry(
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
        api = MagicMock()
        api.get_readings = AsyncMock(return_value={})
        api.get_output_runtimes = AsyncMock(return_value={})
        api.dosing_standalone = False
        with patch(
            "custom_components.violet_pool_controller.device.async_get_clientsession",
            return_value=MagicMock(),
        ):
            return VioletPoolControllerDevice(hass=hass, config_entry=entry, api=api)

    def test_ext2_zombie_keys_are_not_a_module(self, device):
        """Keys without an alive-count must not report a second extension."""
        device._data = {
            "SYSTEM_ext1module_alive_count": 455368363,
            "EXT1_1": 0,
            "EXT2_1": 0,
            "EXT2_2": 6,
            "EXT2_8_LAST_OFF": 1786136934,
        }

        modules = device._detect_current_hardware_modules()

        assert "Relais-Erweiterung" in modules
        assert not any("2" in m for m in modules), (
            "EXT2-Keys ohne alive-count dürfen kein zweites Erweiterungsmodul melden"
        )

    def test_both_extensions_are_numbered(self, device):
        """Two attached relay extensions are listed with their number."""
        device._data = {
            "SYSTEM_ext1module_alive_count": 10,
            "SYSTEM_ext2module_alive_count": 20,
        }

        modules = device._detect_current_hardware_modules()

        assert "Relais-Erweiterung 1" in modules
        assert "Relais-Erweiterung 2" in modules

    def test_official_module_names(self, device):
        """Modules are named after the products PoolDigital sells."""
        device._data = {
            "SYSTEM_dosagemodule_alive_count": 5,
            "SYSTEM_ext1module_alive_count": 5,
            "DMX_SCENE1": 3,
            "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_1": 1,
        }

        modules = device._detect_current_hardware_modules()

        assert "Dosier-Modul" in modules
        assert "Relais-Erweiterung" in modules
        assert "DMX-Modul" in modules
        assert "DiRule" in modules

    def test_standalone_dosing_name(self, device):
        """Dosing on the base module is labelled as a function, not a module."""
        device._data = {"HW_STANDALONE_MODE": True}

        assert "Dosier-Funktion" in device._detect_current_hardware_modules()

    def test_model_string_hides_absent_ext2(self, device):
        """The device model must not claim a module the pool does not have."""
        device._data = {
            "SYSTEM_ext1module_alive_count": 1,
            "SYSTEM_dosagemodule_alive_count": 1,
            "EXT2_2": 6,
        }
        device._firmware_version = "1.2.3"

        model = device.device_info["model"]

        assert "Ext2" not in model
        assert "Relais-Erweiterung" in model

    async def test_fetch_marks_ext2_absent_despite_runtime_keys(self, device):
        """The full fetch path mirrors the live payload: alive key only for EXT1."""
        device.api.get_readings = AsyncMock(
            return_value={
                "PUMP": 1,
                "SYSTEM_ext1module_alive_count": 455368363,
                "SYSTEM_dosagemodule_alive_count": 177063463,
                "SYSTEM_carrier_alive_count": 177063575,
            }
        )
        # Der Runtime-Endpoint liefert Zombie-Keys fuer das fehlende EXT2.
        device.api.get_output_runtimes = AsyncMock(
            return_value={
                "EXT1_1_RUNTIME": "00h 00m 00s",
                "EXT2_2_RUNTIME": "00h 00m 00s",
            }
        )
        device._fetch_config_values = AsyncMock(return_value={})

        data = await device._fetch_controller_data()

        assert data["HW_EXTENSION_MODULE_1"] is True
        assert data["HW_EXTENSION_MODULE_2"] is False, (
            "EXT2-Runtime-Keys ohne alive-count duerfen das Modul nicht anmelden"
        )
