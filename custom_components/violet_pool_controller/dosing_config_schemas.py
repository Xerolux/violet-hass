# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Dosing configuration service schemas."""

from __future__ import annotations

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID

from .service_helpers import DEVICE_ID_SELECTOR

DOSING_SYSTEMS = [
    "chlorine",
    "electrolysis",
    "ph_minus",
    "ph_plus",
    "flocculant",
    "h2o2",
]


def get_dosing_schemas() -> dict[str, vol.Schema]:
    """Get all dosing configuration schemas."""
    return {
        "configure_dosing": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("dosing_system"): vol.In(DOSING_SYSTEMS),
                    vol.Required("config_key"): cv.string,
                    vol.Required("value"): vol.Any(
                        cv.boolean,
                        vol.Coerce(int),
                        vol.Coerce(float),
                        cv.string,
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "set_dosing_target": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("dosing_system"): vol.In(DOSING_SYSTEMS),
                    vol.Required("target_value"): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=0, max=100),
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "set_dosing_daytime": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("dosing_system"): vol.In(DOSING_SYSTEMS),
                    vol.Optional("day_start"): vol.Match(r"^\d{2}:\d{2}$"),
                    vol.Optional("day_end"): vol.Match(r"^\d{2}:\d{2}$"),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "set_dosing_max_daily": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("dosing_system"): vol.In(DOSING_SYSTEMS),
                    vol.Required("max_daily_ml"): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=10, max=10000),
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "enable_dosing": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("dosing_system"): vol.In(DOSING_SYSTEMS),
                    vol.Required("enabled"): cv.boolean,
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
    }
