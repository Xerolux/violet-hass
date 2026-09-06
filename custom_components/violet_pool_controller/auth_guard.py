# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Report authentication failures on control commands.

Config entries created through zeroconf discovery before credentials were
collected carry an empty username and password. Reading the controller often
works without a login, so the coordinator stays healthy and Home Assistant's
native re-auth never fires - while every switch and service call is rejected.
The first a user hears of it is the command failing.

:class:`AuthReportingAPI` wraps the API client and turns that silent failure
into a fixable repair issue: the first rejected control command raises
``controller_requires_auth`` (with a "Fix it" form for the credentials), and
the first command that goes through clears it again.
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import TYPE_CHECKING, Any

from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.issue_registry import IssueSeverity
from violet_poolcontroller_api import VioletAuthError

from .const import CONF_CONTROLLER_NAME, DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from violet_poolcontroller_api import VioletPoolAPI

_LOGGER = logging.getLogger(__name__)

ISSUE_AUTH_REQUIRED = "controller_requires_auth"

# Command-style methods that mutate controller state. Everything the
# integration calls on the API either reads (``get_*``, ``is_*``) or is
# listed here; reads must stay untouched because their auth failures are
# already routed to the coordinator's re-auth path.
_CONTROL_METHOD_NAMES = frozenset(
    {
        "manual_dosing",
        "restore_calibration",
        "reset_blocking",
        "init_update",
        "set_system_service",
    }
)


def _is_control_method(name: str) -> bool:
    """Return whether ``name`` is a state-changing API method."""
    return name.startswith("set_") or name in _CONTROL_METHOD_NAMES


class AuthReportingAPI:
    """Transparent proxy that reports auth failures on control commands."""

    def __init__(
        self,
        api: VioletPoolAPI,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Wrap ``api`` for the owning config entry."""
        self._api = api
        self._hass = hass
        self._config_entry = config_entry

    @property
    def _issue_id(self) -> str:
        """Issue id scoped to the config entry."""
        return f"{ISSUE_AUTH_REQUIRED}_{self._config_entry.entry_id}"

    def _report_auth_failure(self) -> None:
        """Raise the repair issue once; further failures only log."""
        name = self._config_entry.data.get(CONF_CONTROLLER_NAME) or (
            self._config_entry.title
        )
        _LOGGER.error(
            "Controller '%s' rejected a command: authentication required. "
            "The entry likely has no username/password stored - "
            "check the repair notification to add them",
            name,
        )
        ir.async_create_issue(
            self._hass,
            DOMAIN,
            self._issue_id,
            is_fixable=True,
            is_persistent=True,
            severity=IssueSeverity.ERROR,
            translation_key=ISSUE_AUTH_REQUIRED,
            translation_placeholders={"name": str(name)},
        )

    def _clear_auth_issue(self) -> None:
        """Clear the repair issue once a command succeeds again."""
        registry = ir.async_get(self._hass)
        if registry.async_get_issue(DOMAIN, self._issue_id) is not None:
            registry.async_delete(DOMAIN, self._issue_id)

    def __getattr__(self, name: str) -> Any:
        """Forward to the wrapped API, guarding control commands."""
        attr = getattr(self._api, name)
        if not callable(attr) or not _is_control_method(name):
            return attr

        @wraps(attr)
        async def guarded(*args: Any, **kwargs: Any) -> Any:
            try:
                result = await attr(*args, **kwargs)
            except VioletAuthError:
                self._report_auth_failure()
                raise
            self._clear_auth_issue()
            return result

        return guarded
