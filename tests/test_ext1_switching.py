"""Tests for EXT1/EXT2 switch detection and command handling.

Regression tests for the bug introduced with API 0.0.12:
- The API package filters EXT1_* keys when the module is not "detected"
  (LAST_ON == 0 for all relays and SYSTEM_ext1module_alive_count is absent).
- The integration must use sticky detection so the module is never lost once
  it has been found, and must restore previous EXT state values into
  coordinator.data when the API filter removes them.
"""

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
from custom_components.violet_pool_controller.switch import (
    REFRESH_DELAY,
    REFRESH_DELAY_EXT,
)
from violet_poolcontroller_api.const_devices import DEVICE_PARAMETERS


@pytest.fixture
def config_entry():
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
def mock_api():
    api = MagicMock()
    api.dosing_standalone = False
    return api


@pytest.fixture
def device(hass, config_entry, mock_api):
    with patch(
        "custom_components.violet_pool_controller.device.async_get_clientsession",
        return_value=MagicMock(),
    ):
        return VioletPoolControllerDevice(
            hass=hass,
            config_entry=config_entry,
            api=mock_api,
        )


# ===========================================================================
# Hardware detection
# ===========================================================================


class TestExt1HardwareDetection:
    """EXT1/EXT2 hardware detection in _fetch_controller_data."""

    async def test_ext1_detected_via_alive_count(self, device, mock_api):
        """SYSTEM_ext1module_alive_count > 0 signals EXT1 presence."""
        mock_api.get_readings = AsyncMock(
            return_value={
                "PUMP": 1,
                "SYSTEM_ext1module_alive_count": 5,
            }
        )
        data = await device._fetch_controller_data()
        assert data["HW_EXTENSION_MODULE_1"] is True
        assert "EXT1" in device._hw_detected

    async def test_ext1_detected_via_data_keys(self, device, mock_api):
        """EXT1_* keys in the (already-filtered) data signal module presence."""
        mock_api.get_readings = AsyncMock(
            return_value={"PUMP": 1, "EXT1_1": 4, "EXT1_2": 0}
        )
        data = await device._fetch_controller_data()
        assert data["HW_EXTENSION_MODULE_1"] is True
        assert "EXT1" in device._hw_detected

    async def test_ext1_not_detected_when_absent(self, device, mock_api):
        """Module absent: alive count not present, no EXT1 keys."""
        mock_api.get_readings = AsyncMock(return_value={"PUMP": 1})
        data = await device._fetch_controller_data()
        assert data["HW_EXTENSION_MODULE_1"] is False
        assert "EXT1" not in device._hw_detected

    async def test_ext1_sticky_once_detected(self, device, mock_api):
        """Once EXT1 detected, it stays True even if keys later disappear."""
        mock_api.get_readings = AsyncMock(
            return_value={"PUMP": 1, "EXT1_2": 4, "EXT1_2_LAST_ON": 1_700_000_000}
        )
        await device._fetch_controller_data()
        assert "EXT1" in device._hw_detected

        # Second poll: API filtered all EXT1 keys away
        mock_api.get_readings = AsyncMock(return_value={"PUMP": 1})
        data = await device._fetch_controller_data()
        assert data["HW_EXTENSION_MODULE_1"] is True, (
            "Sticky detection must keep HW_EXTENSION_MODULE_1 True"
        )

    async def test_ext1_stale_values_restored_when_filtered(self, device, mock_api):
        """Previous EXT1 state values are restored when the API filter removes them."""
        mock_api.get_readings = AsyncMock(
            return_value={"PUMP": 1, "EXT1_2": 4, "EXT1_2_LAST_ON": 1_700_000_000}
        )
        data1 = await device._fetch_controller_data()
        device._data = data1  # simulate coordinator persisting result

        # Second poll: API removed EXT1 keys (module detection dropped in filter)
        mock_api.get_readings = AsyncMock(return_value={"PUMP": 0})
        data2 = await device._fetch_controller_data()
        assert "EXT1_2" in data2, "EXT1_2 must be restored from previous data"
        assert data2["EXT1_2"] == 4

    async def test_ext2_sticky_once_detected(self, device, mock_api):
        """Same sticky logic applies to EXT2."""
        mock_api.get_readings = AsyncMock(
            return_value={"PUMP": 1, "EXT2_1": 1, "EXT2_1_LAST_ON": 1_700_000_000}
        )
        await device._fetch_controller_data()
        assert "EXT2" in device._hw_detected

        mock_api.get_readings = AsyncMock(return_value={"PUMP": 1})
        data = await device._fetch_controller_data()
        assert data["HW_EXTENSION_MODULE_2"] is True

    def test_hw_detected_initialises_empty(self, device):
        """_hw_detected is an empty set on device creation."""
        assert device._hw_detected == set()


# ===========================================================================
# API command format tests (const_devices only – no network needed)
# ===========================================================================


class TestExt1ApiCommandFormat:
    """API command templates for EXT1/EXT2 relays."""

    def test_ext1_2_command_template(self):
        """EXT1_2 has the expected comma-separated command template."""
        tmpl = DEVICE_PARAMETERS.get("EXT1_2", {}).get("api_template", "")
        assert tmpl == "EXT1_2,{action},{duration},0", (
            f"Unexpected template: {tmpl!r}"
        )

    def test_all_ext1_relays_have_templates(self):
        """All 8 EXT1 relay keys must have an api_template."""
        for i in range(1, 9):
            key = f"EXT1_{i}"
            assert key in DEVICE_PARAMETERS, f"{key} missing from DEVICE_PARAMETERS"
            assert "api_template" in DEVICE_PARAMETERS[key], (
                f"{key} missing api_template"
            )

    def test_ext1_template_action_placeholder(self):
        """Template contains {action} placeholder for ON/OFF/AUTO."""
        for i in range(1, 9):
            tmpl = DEVICE_PARAMETERS[f"EXT1_{i}"]["api_template"]
            filled = tmpl.format(action="ON", duration=0)
            assert "ON" in filled
            filled_off = tmpl.format(action="OFF", duration=0)
            assert "OFF" in filled_off

    def test_ext1_template_duration_placeholder(self):
        """Template contains {duration} so timed actions work."""
        tmpl = DEVICE_PARAMETERS["EXT1_2"]["api_template"]
        result = tmpl.format(action="ON", duration=300)
        assert "300" in result, f"Duration not in filled template: {result!r}"

    def test_ext1_template_ends_with_zero(self):
        """Template always ends with ,0 (no speed/value parameter for relays)."""
        for i in range(1, 9):
            tmpl = DEVICE_PARAMETERS[f"EXT1_{i}"]["api_template"]
            assert tmpl.endswith(",0"), (
                f"EXT1_{i} template should end with ',0': {tmpl!r}"
            )


# ===========================================================================
# Refresh delay constants
# ===========================================================================


class TestExt1RefreshDelay:
    """The switch entity uses a longer delay for EXT keys."""

    def test_ext_delay_longer_than_default(self):
        """REFRESH_DELAY_EXT must be strictly greater than REFRESH_DELAY."""
        assert REFRESH_DELAY_EXT > REFRESH_DELAY, (
            "EXT refresh delay should be longer than default"
        )

    def test_ext_delay_at_least_one_second(self):
        """EXT refresh delay should be at least 1 second for controller timing."""
        assert REFRESH_DELAY_EXT >= 1.0, (
            "EXT refresh delay should be at least 1 second"
        )
