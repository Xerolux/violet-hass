"""Tests for the auth guard that reports rejected control commands.

Entries set up through discovery before credentials were collected carry an
empty username and password. Readings often work without a login, so the
coordinator stays healthy - but every switch and service call is rejected.
The guard wraps the API and raises a fixable repair issue so the user learns
why nothing can be switched.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from violet_poolcontroller_api import VioletAuthError, VioletPoolAPIError

from custom_components.violet_pool_controller.auth_guard import AuthReportingAPI
from custom_components.violet_pool_controller.const import DOMAIN

ENTRY_ID = "auth_guard_entry"


def _make_proxy(hass: HomeAssistant, api: MagicMock) -> AuthReportingAPI:
    """Wrap ``api`` the way ``VioletPoolControllerDevice`` does."""
    entry = MagicMock()
    entry.entry_id = ENTRY_ID
    entry.data = {"controller_name": "Pool"}
    entry.title = "Pool • 50m³"
    return AuthReportingAPI(api, hass, entry)


class TestPassThrough:
    """The proxy is transparent for everything that is not a control command."""

    async def test_read_methods_pass_through(self, hass: HomeAssistant) -> None:
        """Read results reach the caller unchanged."""
        api = MagicMock()
        api.get_readings = AsyncMock(return_value={"PUMP": 1})
        proxy = _make_proxy(hass, api)

        assert await proxy.get_readings() == {"PUMP": 1}

    async def test_attributes_pass_through(self, hass: HomeAssistant) -> None:
        """Properties of the wrapped API stay reachable."""
        api = MagicMock()
        api.timeout = 12.0
        proxy = _make_proxy(hass, api)

        assert proxy.timeout == 12.0

    async def test_control_success_returns_result(self, hass: HomeAssistant) -> None:
        """A successful command returns the API result unchanged."""
        api = MagicMock()
        api.set_switch_state = AsyncMock(return_value={"success": True})
        proxy = _make_proxy(hass, api)

        assert await proxy.set_switch_state(key="PUMP", action="ON") == {"success": True}


class TestAuthIssueLifecycle:
    """A rejected control command raises a fixable issue; success clears it."""

    def _issue_id(self) -> str:
        return f"controller_requires_auth_{ENTRY_ID}"

    async def test_control_auth_failure_creates_fixable_issue(
        self, hass: HomeAssistant
    ) -> None:
        """HTTP 401 on a command must surface as a repair issue."""
        api = MagicMock()
        api.set_switch_state = AsyncMock(side_effect=VioletAuthError("401"))
        proxy = _make_proxy(hass, api)

        with pytest.raises(VioletAuthError):
            await proxy.set_switch_state(key="PUMP", action="ON")

        issue = ir.async_get(hass).async_get_issue(DOMAIN, self._issue_id())
        assert issue is not None
        assert issue.is_fixable is True
        assert issue.is_persistent is True

    async def test_read_auth_failure_creates_no_issue(self, hass: HomeAssistant) -> None:
        """Read failures belong to the coordinator/reauth path, not to a repair."""
        api = MagicMock()
        api.get_readings = AsyncMock(side_effect=VioletAuthError("401"))
        proxy = _make_proxy(hass, api)

        with pytest.raises(VioletAuthError):
            await proxy.get_readings()

        assert ir.async_get(hass).async_get_issue(DOMAIN, self._issue_id()) is None

    async def test_non_auth_control_error_creates_no_issue(
        self, hass: HomeAssistant
    ) -> None:
        """Plain API errors keep their existing meaning."""
        api = MagicMock()
        api.set_switch_state = AsyncMock(side_effect=VioletPoolAPIError("timeout"))
        proxy = _make_proxy(hass, api)

        with pytest.raises(VioletPoolAPIError):
            await proxy.set_switch_state(key="PUMP", action="ON")

        assert ir.async_get(hass).async_get_issue(DOMAIN, self._issue_id()) is None

    async def test_successful_control_clears_existing_issue(
        self, hass: HomeAssistant
    ) -> None:
        """Once a command goes through, the warning disappears on its own."""
        from homeassistant.helpers import issue_registry as registry

        registry.async_create_issue(
            hass,
            DOMAIN,
            self._issue_id(),
            is_fixable=True,
            is_persistent=True,
            severity=registry.IssueSeverity.ERROR,
            translation_key="controller_requires_auth",
        )
        api = MagicMock()
        api.set_switch_state = AsyncMock(return_value={"success": True})
        proxy = _make_proxy(hass, api)

        await proxy.set_switch_state(key="PUMP", action="ON")

        assert ir.async_get(hass).async_get_issue(DOMAIN, self._issue_id()) is None

    async def test_other_command_verbs_are_guarded(self, hass: HomeAssistant) -> None:
        """Dosing and config writes are control commands, too."""
        api = MagicMock()
        api.manual_dosing = AsyncMock(side_effect=VioletAuthError("401"))
        api.set_config = AsyncMock(side_effect=VioletAuthError("401"))
        proxy = _make_proxy(hass, api)

        with pytest.raises(VioletAuthError):
            await proxy.manual_dosing("CL", 10)
        with pytest.raises(VioletAuthError):
            await proxy.set_config({"pH_min": 7.0})

        issue = ir.async_get(hass).async_get_issue(DOMAIN, self._issue_id())
        assert issue is not None
