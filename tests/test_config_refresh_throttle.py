"""Tests for throttling the getConfig request.

The setpoints (heater/solar targets, dosing setpoints, firmware version) sit
behind a second HTTP request per poll, but they only change when somebody
writes them. They are therefore re-read at most every CONFIG_REFRESH_INTERVAL
seconds, and immediately after a write from Home Assistant.
"""

from __future__ import annotations

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
    CONFIG_REFRESH_INTERVAL,
    DOMAIN,
)
from custom_components.violet_pool_controller.device import (
    VioletPoolControllerDevice,
    VioletPoolDataUpdateCoordinator,
)

READINGS = {"PUMP": 1, "pH_value": "7.2"}
CONFIG = {"HEATER_set_temp": "28", "SYSTEM_swversion": "1.2.3"}


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Create a config entry."""
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
def mock_api() -> MagicMock:
    """Create a mocked API."""
    api = MagicMock()
    api.get_readings = AsyncMock(return_value=READINGS)
    api.get_output_runtimes = AsyncMock(return_value={})
    api.get_config = AsyncMock(return_value=CONFIG)
    api.dosing_standalone = False
    return api


@pytest.fixture
def device(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_api: MagicMock
) -> VioletPoolControllerDevice:
    """Create a device instance."""
    with patch(
        "custom_components.violet_pool_controller.device.async_get_clientsession",
        return_value=MagicMock(),
    ):
        return VioletPoolControllerDevice(hass=hass, config_entry=config_entry, api=mock_api)


class TestConfigFetchThrottling:
    """getConfig is not called on every poll."""

    async def test_first_poll_fetches_config(self, device, mock_api) -> None:
        """Without cached values the config must be read."""
        data = await device.async_update()

        assert mock_api.get_config.await_count == 1
        assert data["HEATER_set_temp"] == "28"

    async def test_second_poll_reuses_cached_values(self, device, mock_api) -> None:
        """A poll inside the refresh window skips the request but keeps the keys."""
        await device.async_update()
        data = await device.async_update()

        assert mock_api.get_config.await_count == 1
        assert data["HEATER_set_temp"] == "28"
        assert data["SYSTEM_swversion"] == "1.2.3"

    async def test_config_is_refetched_after_the_interval(self, device, mock_api) -> None:
        """Once the interval has passed the values are read again."""
        await device.async_update()
        device._last_config_fetch -= CONFIG_REFRESH_INTERVAL

        await device.async_update()

        assert mock_api.get_config.await_count == 2

    async def test_write_forces_a_refetch(self, device, mock_api) -> None:
        """A setpoint write is confirmed on the very next poll."""
        await device.async_update()
        device.request_config_refresh()

        await device.async_update()

        assert mock_api.get_config.await_count == 2

    async def test_setpoint_cache_update_requests_a_refetch(
        self, hass: HomeAssistant, device, mock_api
    ) -> None:
        """Writing through the coordinator triggers the same refresh."""
        coordinator = VioletPoolDataUpdateCoordinator(
            hass=hass, device=device, name="test", polling_interval=30
        )
        await coordinator._async_update_data()

        coordinator.update_setpoint_cache("HEATER_set_temp", 29.0)
        await coordinator._async_update_data()

        assert mock_api.get_config.await_count == 2

    async def test_failed_fetch_keeps_previous_values(self, device, mock_api) -> None:
        """A failing getConfig must not drop the setpoints from the data."""
        await device.async_update()
        mock_api.get_config = AsyncMock(side_effect=TimeoutError("boom"))
        device.request_config_refresh()

        data = await device.async_update()

        assert data["HEATER_set_temp"] == "28"

    async def test_partial_response_does_not_drop_known_keys(self, device, mock_api) -> None:
        """SYSTEM_availableversion is only part of some fetches and must persist."""
        mock_api.get_config = AsyncMock(
            return_value={**CONFIG, "SYSTEM_availableversion": "1.3.0"}
        )
        await device.async_update()

        mock_api.get_config = AsyncMock(return_value=CONFIG)
        device.request_config_refresh()
        data = await device.async_update()

        assert data["SYSTEM_availableversion"] == "1.3.0"
