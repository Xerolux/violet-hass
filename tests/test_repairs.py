"""Tests for the repair flow behind the "controller unavailable" issue.

``device.py`` creates that issue with ``is_fixable=True``. Home Assistant then
shows a "Fix" button and calls ``async_create_fix_flow`` - which did not exist,
so pressing the button failed.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from custom_components.violet_pool_controller.const import DOMAIN
from custom_components.violet_pool_controller.repairs import (
    ControllerUnavailableRepairFlow,
    _DismissRepairFlow,
    async_create_fix_flow,
)


@pytest.fixture
def entry_id() -> str:
    """Return a config entry id."""
    return "abc123"


class TestFixFlowSelection:
    """The right flow is created for a given issue id."""

    async def test_controller_unavailable_issue(self, hass: HomeAssistant, entry_id) -> None:
        """The controller issue maps to the reconnect flow, entry id included."""
        flow = await async_create_fix_flow(hass, f"controller_unavailable_{entry_id}", None)

        assert isinstance(flow, ControllerUnavailableRepairFlow)
        assert flow._entry_id == entry_id

    async def test_unknown_issue_gets_dismiss_flow(self, hass: HomeAssistant) -> None:
        """Unknown issues still get a working (dismissing) flow."""
        flow = await async_create_fix_flow(hass, "something_else", None)

        assert isinstance(flow, _DismissRepairFlow)


class TestControllerUnavailableRepairFlow:
    """Confirming the flow reloads the entry and reports the outcome."""

    async def test_form_is_shown_first(self, hass: HomeAssistant, entry_id) -> None:
        """The user gets a confirmation form before anything happens."""
        flow = ControllerUnavailableRepairFlow(entry_id)
        flow.hass = hass

        result = await flow.async_step_init()

        assert result["type"] == "form"
        assert result["step_id"] == "confirm"

    async def test_successful_reconnect_finishes_the_flow(
        self, hass: HomeAssistant, entry_id
    ) -> None:
        """A controller that answers again resolves the issue."""
        coordinator = MagicMock()
        coordinator.device.available = True
        hass.data[DOMAIN] = {entry_id: coordinator}
        hass.config_entries.async_get_entry = MagicMock(return_value=MagicMock())
        hass.config_entries.async_reload = AsyncMock()

        flow = ControllerUnavailableRepairFlow(entry_id)
        flow.hass = hass

        result = await flow.async_step_confirm({})

        hass.config_entries.async_reload.assert_awaited_once_with(entry_id)
        assert result["type"] == "create_entry"

    async def test_still_unreachable_aborts_with_reason(
        self, hass: HomeAssistant, entry_id
    ) -> None:
        """A controller that stays silent tells the user so."""
        coordinator = MagicMock()
        coordinator.device.available = False
        hass.data[DOMAIN] = {entry_id: coordinator}
        hass.config_entries.async_get_entry = MagicMock(return_value=MagicMock())
        hass.config_entries.async_reload = AsyncMock()

        flow = ControllerUnavailableRepairFlow(entry_id)
        flow.hass = hass

        result = await flow.async_step_confirm({})

        assert result["type"] == "abort"
        assert result["reason"] == "still_unavailable"

    async def test_removed_entry_is_handled(self, hass: HomeAssistant, entry_id) -> None:
        """An entry deleted in the meantime must not raise."""
        hass.config_entries.async_get_entry = MagicMock(return_value=None)
        hass.config_entries.async_reload = AsyncMock()

        flow = ControllerUnavailableRepairFlow(entry_id)
        flow.hass = hass

        result = await flow.async_step_confirm({})

        hass.config_entries.async_reload.assert_not_awaited()
        assert result["type"] == "create_entry"


class TestDismissRepairFlow:
    """The fallback flow deletes the issue it was created for."""

    async def test_issue_is_deleted_on_confirm(self, hass: HomeAssistant) -> None:
        """Confirming removes the issue from the registry."""
        ir.async_create_issue(
            hass,
            DOMAIN,
            "some_issue",
            is_fixable=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key="controller_unavailable",
        )

        flow = _DismissRepairFlow("some_issue")
        flow.hass = hass

        result = await flow.async_step_confirm({})

        assert result["type"] == "create_entry"
        assert ir.async_get(hass).async_get_issue(DOMAIN, "some_issue") is None
