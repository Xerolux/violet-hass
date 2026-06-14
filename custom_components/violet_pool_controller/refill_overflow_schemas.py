# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Refill and Overflow control service schemas."""

from __future__ import annotations

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID

from .service_helpers import DEVICE_ID_SELECTOR


def get_refill_overflow_schemas() -> dict[str, vol.Schema]:
    """Get refill and overflow control schemas."""
    return {
        "configure_refill": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("refill_type"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=3)
                    ),
                    vol.Optional("enabled", default=True): cv.boolean,
                    vol.Optional("max_fill_time"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=3600)
                    ),
                    vol.Optional("target_level"): vol.All(
                        vol.Coerce(float), vol.Range(min=0, max=100)
                    ),
                    vol.Optional("blocks_dosing", default=False): cv.boolean,
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "configure_overflow": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Optional("enabled", default=True): cv.boolean,
                    vol.Optional("dryrun_level"): vol.All(
                        vol.Coerce(float), vol.Range(min=0, max=100)
                    ),
                    vol.Optional("dryrun_enabled", default=True): cv.boolean,
                    vol.Optional("overflow_level"): vol.All(
                        vol.Coerce(float), vol.Range(min=0, max=100)
                    ),
                    vol.Optional("overflow_rpm"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=3)
                    ),
                    vol.Optional("overflow_runtime"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=3600)
                    ),
                    vol.Optional("bathing_ai_enabled", default=True): cv.boolean,
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
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "get_refill_status": vol.Schema(
            {vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}
        ),
        "get_overflow_status": vol.Schema(
            {vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}
        ),
    }
