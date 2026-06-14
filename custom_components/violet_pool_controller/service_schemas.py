"""Service schemas for the Violet Pool Controller integration."""

from __future__ import annotations

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID

from .service_helpers import (
    DEVICE_ID_SELECTOR,
    DOSING_TYPE_MAPPING,
    MAX_DOSING_DURATION,
    MAX_PUMP_SPEED,
    MIN_DOSING_DURATION,
    MIN_PUMP_SPEED,
)


def get_service_schemas() -> dict[str, vol.Schema]:
    """Get all service schemas."""
    return {
        "control_pump": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("action"): vol.In(
                        ["speed_control", "force_off", "eco_mode", "boost_mode", "auto"]
                    ),
                    vol.Optional("speed", default=2): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_PUMP_SPEED, max=MAX_PUMP_SPEED),
                    ),
                    vol.Optional("duration", default=0): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=86400)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "smart_dosing": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("dosing_type"): vol.In(
                        list(DOSING_TYPE_MAPPING.keys())
                    ),
                    vol.Required("action"): vol.In(["manual_dose", "auto", "stop"]),
                    vol.Optional("duration", default=30): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_DOSING_DURATION, max=MAX_DOSING_DURATION),
                    ),
                    vol.Optional("safety_override", default=False): cv.boolean,
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "manage_pv_surplus": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("mode"): vol.In(["activate", "deactivate", "auto"]),
                    vol.Optional("pump_speed", default=2): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_PUMP_SPEED, max=MAX_PUMP_SPEED),
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "control_dmx_scenes": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Required("action"): vol.In(
                    ["all_on", "all_off", "all_auto", "sequence", "party_mode"]
                ),
                vol.Optional("sequence_delay", default=2): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=60)
                ),
            }
        ),
        "set_light_color_pulse": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Optional("pulse_count", default=1): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=10)
                    ),
                    vol.Optional("pulse_interval", default=500): vol.All(
                        vol.Coerce(int), vol.Range(min=100, max=2000)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "manage_digital_rules": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                # Controller exposes DIRULE_1..7 only
                vol.Required("rule_key"): vol.In([f"DIRULE_{i}" for i in range(1, 8)]),
                vol.Required("action"): vol.In(["trigger", "lock", "unlock"]),
            }
        ),
        "test_output": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                # Output keys are plain identifiers (e.g. PUMP, EXT1_1); the
                # API builds the query string without URL-encoding this value
                vol.Required("output"): vol.All(
                    cv.string, vol.Match(r"^[A-Za-z0-9_]+$")
                ),
                vol.Optional("mode", default="SWITCH"): vol.In(["SWITCH", "ON", "OFF"]),
                vol.Optional("duration", default=120): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=900)
                ),
            }
        ),
        "export_diagnostic_logs": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Optional("lines", default=100): vol.All(
                    vol.Coerce(int), vol.Range(min=10, max=10000)
                ),
                vol.Optional("include_timestamps", default=True): cv.boolean,
                vol.Optional("include_config", default=True): cv.boolean,
                vol.Optional("include_history", default=True): cv.boolean,
                vol.Optional("include_states", default=True): cv.boolean,
                vol.Optional("include_raw_data", default=True): cv.boolean,
                vol.Optional("save_to_file", default=False): cv.boolean,
            }
        ),
        "get_connection_status": vol.Schema(
            {vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}
        ),
        "get_error_summary": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Optional("include_history", default=False): cv.boolean,
            }
        ),
        "test_connection": vol.Schema(
            {vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}
        ),
        "clear_error_history": vol.Schema(
            {vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}
        ),
    }
