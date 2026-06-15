"""Service schemas for the Violet Pool Controller integration."""

from __future__ import annotations

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID

from .refill_overflow_schemas import get_refill_overflow_schemas
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
    schemas = {
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
# Controller exposes DIRULE_1..8 (internal name: SWITCHINGRULE_1..8)
vol.Required("rule_key"): vol.In([f"DIRULE_{i}" for i in range(1, 9)]),
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
        # reset_blocking clears fault-induced blockings on the controller
        # (e.g. BLOCKED_BY_ESC after an empty-canister alarm was acknowledged).
        # Useful after fixing the underlying issue so dosing/control resumes.
        "reset_blocking": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
            }
        ),
        # set_can_amount updates a dosing canister fill level after refill.
        # action=adjust just sets the new level; action=reset also clears the
        # daily counter and "last reset" timestamp.
        "set_can_amount": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Required("dosing_key"): vol.In([
                    "DOS_1_CL",   # Chlorine
                    "DOS_2_ELO",  # Electrolysis
                    "DOS_4_PHM",  # pH-
                    "DOS_5_PHP",  # pH+
                    "DOS_6_FLOC", # Flocculant
                ]),
                vol.Required("amount_ml"): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=100000)
                ),
                vol.Optional("action", default="adjust"): vol.In(
                    ["adjust", "reset"]
                ),
            }
        ),
        # set_system_service enables/disables a controller-side system
        # service (FTP, Samba, SSH, AirPlay, HomeKit, Alexa, tunnels).
        "set_system_service": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Required("service"): vol.In([
                    "ftp", "samba", "ssh", "shairport",
                    "homebridge", "alexa", "tunnel", "support_tunnel",
                ]),
                vol.Required("enabled"): cv.boolean,
            }
        ),
        # get_system_services_status returns the live state of all
        # controller-side services as a dict.
        "get_system_services_status": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
            }
        ),
        # set_omni_position drives the OmniTronic multi-port valve to a
        # fixed position.  Position 0 (Filtration) also returns the
        # controller to automatic mode.
        "set_omni_position": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                vol.Required("position"): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=5)
                ),
            }
        ),
        # get_live_trace_snapshot returns a single-row snapshot of every
        # controller reading (CSV→dict) for ad-hoc troubleshooting.
        "get_live_trace_snapshot": vol.Schema(
            {
                vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
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
        # NEW HTTP-based control services (Direct setFunctionManually API)
        "control_pump_http": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Optional("speed"): vol.In([0, 1, 2, 3]),
                    vol.Optional("action"): vol.In(["on", "off", "eco", "boost"]),
                    vol.Optional("force_off", default=False): cv.boolean,
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "control_heater_http": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Optional("action"): vol.In(["on", "off"]),
                    vol.Optional("target_temperature"): vol.All(
                        vol.Coerce(float), vol.Range(min=10, max=60)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "control_solar_http": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Optional("action"): vol.In(["on", "off"]),
                    vol.Optional("target_temperature"): vol.All(
                        vol.Coerce(float), vol.Range(min=10, max=60)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "control_cover_http": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Optional("action"): vol.In(["open", "close", "stop"]),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "control_backwash_http": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Optional("action"): vol.In(["run", "abort"]),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "manual_dosing_http": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("dosing_system"): vol.In(
                        [
                            "chlorine",
                            "electrolysis",
                            "ph_minus",
                            "ph_plus",
                            "flocculant",
                            "h2o2",
                        ]
                    ),
                    vol.Required("runtime_seconds"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=3600)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        # Dosing Configuration Services
        "configure_dosing": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("dosing_system"): vol.In(
                        [
                            "chlorine",
                            "electrolysis",
                            "ph_minus",
                            "ph_plus",
                            "flocculant",
                            "h2o2",
                        ]
                    ),
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
                    vol.Required("dosing_system"): vol.In(
                        [
                            "chlorine",
                            "electrolysis",
                            "ph_minus",
                            "ph_plus",
                            "flocculant",
                            "h2o2",
                        ]
                    ),
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
                    vol.Required("dosing_system"): vol.In(
                        [
                            "chlorine",
                            "electrolysis",
                            "ph_minus",
                            "ph_plus",
                            "flocculant",
                            "h2o2",
                        ]
                    ),
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
                    vol.Required("dosing_system"): vol.In(
                        [
                            "chlorine",
                            "electrolysis",
                            "ph_minus",
                            "ph_plus",
                            "flocculant",
                            "h2o2",
                        ]
                    ),
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
                    vol.Required("dosing_system"): vol.In(
                        [
                            "chlorine",
                            "electrolysis",
                            "ph_minus",
                            "ph_plus",
                            "flocculant",
                            "h2o2",
                        ]
                    ),
                    vol.Required("enabled"): cv.boolean,
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
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
        "control_extension_relay": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("relay_id"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=8)
                    ),
                    vol.Optional("action"): vol.In(["on", "off", "toggle"]),
                    vol.Optional("state"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=6)
                    ),
                    vol.Optional("duration", default=0): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=86400)
                    ),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "configure_sensor_calibration": vol.Schema(vol.All(
            vol.Schema(
                {
                    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
                    vol.Optional(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR,
                    vol.Required("sensor_id"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=12)
                    ),
                    vol.Optional("offset"): vol.All(
                        vol.Coerce(float), vol.Range(min=-10, max=10)
                    ),
                    vol.Optional("multiplier"): vol.All(
                        vol.Coerce(float), vol.Range(min=0.5, max=2.0)
                    ),
                    vol.Optional("min_value"): vol.Coerce(float),
                    vol.Optional("max_value"): vol.Coerce(float),
                }
            ),
            cv.has_at_least_one_key(ATTR_ENTITY_ID, ATTR_DEVICE_ID),
        )),
        "get_calibration_status": vol.Schema(
            {vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}
        ),
        "get_backwash_status": vol.Schema(
            {vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}
        ),
        "get_system_update_status": vol.Schema(
            {vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}
        ),
    }
    schemas.update(get_refill_overflow_schemas())
    return schemas
