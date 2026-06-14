# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Rule management service schemas."""

from __future__ import annotations

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID

from .service_helpers import DEVICE_ID_SELECTOR


def get_rule_schemas() -> dict[str, vol.Schema]:
    """Get all rule management schemas."""
    return {
        "configure_temp_rule": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("rule_id"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=8)
                    ),
                    vol.Optional("enabled", default=True): cv.boolean,
                    vol.Optional("sensor_1"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=8)
                    ),
                    vol.Optional("sensor_2"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=8)
                    ),
                    vol.Optional("logic"): vol.In([">=", "<="]),
                    vol.Optional("diff_value"): vol.Coerce(float),
                    vol.Optional("hyst_value"): vol.Coerce(float),
                    vol.Optional("runtime_on"): vol.Match(r"^\d{2}:\d{2}$"),
                    vol.Optional("runtime_off"): vol.Match(r"^\d{2}:\d{2}$"),
                    vol.Optional("output_1"): cv.string,
                    vol.Optional("output_1_state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                    vol.Optional("output_2"): cv.string,
                    vol.Optional("output_2_state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                    vol.Optional("output_3"): cv.string,
                    vol.Optional("output_3_state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "configure_analog_rule": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("rule_id"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=8)
                    ),
                    vol.Optional("enabled", default=True): cv.boolean,
                    vol.Optional("adc_input"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=8)
                    ),
                    vol.Optional("logic"): vol.In([">=", "<="]),
                    vol.Optional("threshold"): vol.Coerce(float),
                    vol.Optional("hysteresis"): vol.Coerce(float),
                    vol.Optional("runtime_on"): vol.Match(r"^\d{2}:\d{2}$"),
                    vol.Optional("runtime_off"): vol.Match(r"^\d{2}:\d{2}$"),
                    vol.Optional("output_1"): cv.string,
                    vol.Optional("output_1_state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                    vol.Optional("output_2"): cv.string,
                    vol.Optional("output_2_state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                    vol.Optional("output_3"): cv.string,
                    vol.Optional("output_3_state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "configure_switching_rule": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("rule_id"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=8)
                    ),
                    vol.Optional("enabled", default=True): cv.boolean,
                    vol.Optional("di_input"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=12)
                    ),
                    vol.Optional("contact_type"): vol.In([0, 1]),
                    vol.Optional("output"): cv.string,
                    vol.Optional("action_on"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                    vol.Optional("action_off"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                    vol.Optional("timeout"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=3600)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "configure_timer_rule": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("rule_id"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=8)
                    ),
                    vol.Optional("enabled", default=True): cv.boolean,
                    vol.Optional("on_time"): vol.Match(r"^\d{2}:\d{2}$"),
                    vol.Optional("off_time"): vol.Match(r"^\d{2}:\d{2}$"),
                    vol.Optional("weekdays"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=127)
                    ),
                    vol.Optional("output_1"): cv.string,
                    vol.Optional("output_1_state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                    vol.Optional("output_2"): cv.string,
                    vol.Optional("output_2_state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                    vol.Optional("output_3"): cv.string,
                    vol.Optional("output_3_state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "enable_rule": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("rule_type"): vol.In(
                        ["temprule", "analogrule", "switchingrule", "timerrule"]
                    ),
                    vol.Required("rule_id"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=8)
                    ),
                    vol.Required("enabled"): cv.boolean,
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
    }
