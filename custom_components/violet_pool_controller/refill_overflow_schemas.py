# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Refill and Overflow control service schemas."""

from __future__ import annotations

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import ATTR_DEVICE_ID

from .service_helpers import DEVICE_ID_SELECTOR


def get_refill_overflow_schemas() -> dict[str, Any]:
    """Get refill and overflow control schemas."""
    return {
        "control_refill_http": cv.make_entity_service_schema(
            {
                vol.Required("action"): vol.In(["fill", "stop"]),
                vol.Required("duration_seconds"): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=10, max=3600),
                ),
                vol.Optional("safety_override", default=False): cv.boolean,
            }
        ),
        "configure_refill": cv.make_entity_service_schema(
            {
                vol.Required("refill_type"): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
                vol.Optional("enabled", default=True): cv.boolean,
                vol.Optional("max_fill_time"): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=3600)
                ),
                vol.Optional("target_level"): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=100)
                ),
                # No default: the handler writes REFILL_blocks_dosage only when
                # the caller asked for it, so configuring a fill time cannot
                # silently un-block dosing.
                vol.Optional("blocks_dosing"): cv.boolean,
            }
        ),
        # Every field is optional and none carries a default.  The handler
        # sends only the keys the caller supplied, so a call meant to raise the
        # overflow level cannot switch the dry-run or bathing protections on as
        # a side effect (SECURITY.md: no implicit state changes).
        "configure_overflow": cv.make_entity_service_schema(
            {
                vol.Optional("enabled"): cv.boolean,
                vol.Optional("dryrun_level"): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=100)
                ),
                vol.Optional("dryrun_enabled"): cv.boolean,
                vol.Optional("overflow_level"): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=100)
                ),
                vol.Optional("overflow_rpm"): vol.All(vol.Coerce(int), vol.Range(min=0, max=3)),
                vol.Optional("overflow_runtime"): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=3600)
                ),
                vol.Optional("bathing_ai_enabled"): cv.boolean,
                vol.Optional("bathing_level_change"): vol.All(
                    vol.Coerce(float), vol.Range(min=0.1, max=10)
                ),
                vol.Optional("bathing_level_time"): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=600)
                ),
                vol.Optional("bathing_pump_rpm"): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=3)
                ),
                vol.Optional("bathing_runtime"): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=3600)
                ),
            }
        ),
        "get_refill_status": vol.Schema({vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}),
        "get_overflow_status": vol.Schema({vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}),
    }
