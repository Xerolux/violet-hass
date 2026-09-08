"""Setup must route a rejected password to the re-auth flow.

Regression: ``async_setup_device`` retried every failure three times inside a
bare ``except Exception`` and then raised ``ConfigEntryNotReady``, and both
``async_setup_device`` and ``async_setup_entry`` wrapped anything that escaped
into ``ConfigEntryNotReady`` as well. A wrong password therefore looped
forever as "not ready" and ``ConfigFlow.async_step_reauth`` was unreachable.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from pytest_homeassistant_custom_component.common import MockConfigEntry
from violet_poolcontroller_api import VioletAuthError, VioletPoolAPIError

from custom_components.violet_pool_controller import async_setup_entry
from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONFIG_ENTRY_VERSION,
    DOMAIN,
)

ENTRY_DATA = {
    CONF_API_URL: "192.168.178.55",
    CONF_PORT: 80,
    CONF_USE_SSL: False,
    CONF_DEVICE_ID: 1,
    CONF_DEVICE_NAME: "Test Pool Controller",
    CONF_CONTROLLER_NAME: "Test Pool",
    CONF_USERNAME: "admin",
    CONF_PASSWORD: "wrong-password",
}


def _entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a config entry registered with hass, ready to be set up."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data=ENTRY_DATA,
        version=CONFIG_ENTRY_VERSION,
        unique_id="192.168.178.55-1",
    )
    entry.add_to_hass(hass)
    entry.mock_state(hass, ConfigEntryState.SETUP_IN_PROGRESS)
    return entry


def _api(side_effect: Exception) -> MagicMock:
    """Return a mock API whose readings call always fails."""
    api = MagicMock()
    api.get_readings = AsyncMock(side_effect=side_effect)
    api.get_output_runtimes = AsyncMock(return_value={})
    api.get_config = AsyncMock(return_value={})
    api.dosing_standalone = False
    return api


class TestAuthFailureDuringSetup:
    """A rejected password must reach the re-auth flow, not the retry loop."""

    async def test_setup_entry_raises_config_entry_auth_failed(self, hass: HomeAssistant):
        """VioletAuthError from the API surfaces as ConfigEntryAuthFailed."""
        entry = _entry(hass)

        with patch(
            "custom_components.violet_pool_controller.VioletPoolAPI",
            return_value=_api(VioletAuthError("HTTP 401: unauthorized")),
        ):
            with pytest.raises(ConfigEntryAuthFailed):
                await async_setup_entry(hass, entry)

    async def test_setup_entry_does_not_downgrade_auth_to_not_ready(
        self, hass: HomeAssistant
    ):
        """ConfigEntryAuthFailed must not be re-wrapped as ConfigEntryNotReady."""
        entry = _entry(hass)

        with patch(
            "custom_components.violet_pool_controller.VioletPoolAPI",
            return_value=_api(VioletAuthError("HTTP 403: forbidden")),
        ):
            with pytest.raises(ConfigEntryAuthFailed) as raised:
                await async_setup_entry(hass, entry)

        assert not isinstance(raised.value, ConfigEntryNotReady)

    async def test_unreachable_controller_still_raises_not_ready(self, hass: HomeAssistant):
        """A plain connection problem stays retryable."""
        entry = _entry(hass)

        with patch(
            "custom_components.violet_pool_controller.VioletPoolAPI",
            return_value=_api(VioletPoolAPIError("connection refused")),
        ):
            with pytest.raises(ConfigEntryNotReady):
                await async_setup_entry(hass, entry)

    async def test_setup_does_not_retry_the_request_itself(self, hass: HomeAssistant):
        """Setup makes a single attempt; Home Assistant owns the backoff.

        The manual three-attempt loop cost four to six extra requests on every
        start, on top of the retries the API client already performs.
        """
        entry = _entry(hass)
        api = _api(VioletPoolAPIError("connection refused"))

        with patch(
            "custom_components.violet_pool_controller.VioletPoolAPI", return_value=api
        ):
            with pytest.raises(ConfigEntryNotReady):
                await async_setup_entry(hass, entry)

        assert api.get_readings.await_count == 1
