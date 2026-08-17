# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Repair flows for the Violet Pool Controller integration.

``device.py`` raises a fixable repair issue when the controller has been
unreachable for several polling cycles. Home Assistant shows a "Fix" button for
fixable issues and calls :func:`async_create_fix_flow` when the user presses it;
without this platform the button ends in an error dialog.

The flow re-tests the connection: on success the config entry is reloaded and
the issue disappears, otherwise the user is shown the failure and can retry.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ISSUE_PREFIX_CONTROLLER_UNAVAILABLE = "controller_unavailable_"


class _ConfirmRepairFlowBase(RepairsFlow):
    """Shared confirmation form, mirroring Home Assistant's ConfirmRepairFlow."""

    def _show_confirm_form(self) -> FlowResult:
        """Show the confirm step, carrying over the issue's placeholders.

        ``handler`` and ``issue_id`` are assigned by Home Assistant's repairs
        flow manager, so they may be missing when a flow is driven directly.
        """
        placeholders = None
        handler = getattr(self, "handler", None)
        issue_id = getattr(self, "issue_id", None)
        if handler and issue_id:
            issue = ir.async_get(self.hass).async_get_issue(handler, issue_id)
            placeholders = issue.translation_placeholders if issue else None

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders=placeholders,
        )


class ControllerUnavailableRepairFlow(_ConfirmRepairFlowBase):
    """Retry the connection to a controller that stopped responding."""

    def __init__(self, entry_id: str) -> None:
        """Store the config entry the issue belongs to."""
        self._entry_id = entry_id

    async def async_step_init(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Show the confirmation form."""
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Reload the config entry and report whether the controller answered."""
        if user_input is None:
            return self._show_confirm_form()

        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        if entry is None:
            # The entry was removed in the meantime - nothing left to repair.
            return self.async_create_entry(data={})

        _LOGGER.debug("Repair flow: reloading config entry %s", self._entry_id)
        await self.hass.config_entries.async_reload(self._entry_id)

        coordinator = self.hass.data.get(DOMAIN, {}).get(self._entry_id)
        if coordinator is None or not coordinator.device.available:
            return self.async_abort(reason="still_unavailable")

        return self.async_create_entry(data={})


class _DismissRepairFlow(_ConfirmRepairFlowBase):
    """Fallback flow that just deletes the issue after confirmation."""

    def __init__(self, issue_id: str) -> None:
        """Store the issue to delete."""
        self._issue_id = issue_id

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Show the confirmation form."""
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Delete the issue once the user confirms."""
        if user_input is None:
            return self._show_confirm_form()

        ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
        return self.async_create_entry(data={})


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create the flow that repairs ``issue_id``."""
    if issue_id.startswith(ISSUE_PREFIX_CONTROLLER_UNAVAILABLE):
        entry_id = issue_id[len(ISSUE_PREFIX_CONTROLLER_UNAVAILABLE) :]
        return ControllerUnavailableRepairFlow(entry_id)

    # Unknown issue: confirming simply acknowledges and dismisses it.
    return _DismissRepairFlow(issue_id)
