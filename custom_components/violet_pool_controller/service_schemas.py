"""Service schemas for the Violet Pool Controller integration."""

from __future__ import annotations

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.helpers.typing import VolDictType, VolSchemaType

from .refill_overflow_schemas import get_refill_overflow_schemas
from .service_helpers import (
    DEVICE_ID_SELECTOR,
    DOSING_SYSTEM_SLUGS,
    DOSING_TYPE_MAPPING,
    MAX_DOSING_DURATION,
    MAX_PUMP_SPEED,
    MIN_DOSING_DURATION,
    MIN_PUMP_SPEED,
)

# The pump accepts a duration of up to 24 hours; services.yaml, this schema and
# the handler all have to agree on that number or a value the UI offers gets
# rejected by the schema (or, worse, silently clamped by the handler).
MAX_PUMP_DURATION = 86400

# Per-dosing-system target-value ranges.  pH channels are physically bounded
# to ~6.8-7.8; chlorine/electrolysis to 0-10 mg/L; flocculant/h2o2 use the
# wider 0-100 default.  Applied by _validate_dosing_target below.
DOSING_TARGET_RANGES: dict[str, tuple[float, float]] = {
    "ph_minus": (6.8, 7.8),
    "ph_plus": (6.8, 7.8),
    "chlorine": (0.0, 10.0),
    "electrolysis": (0.0, 10.0),
    "flocculant": (0.0, 100.0),
    "h2o2": (0.0, 100.0),
}

# Whitelist of config_key suffixes allowed for the configure_dosing service.
# Safety-critical keys like max_daily_ml are intentionally EXCLUDED (use the
# dedicated set_dosing_max_daily service instead) to prevent an automation
# from silently disabling controller-side daily caps.
ALLOWED_DOSING_CONFIG_KEYS: set[str] = {
    "use",
    "set_ppm",
    "set_ph",
    "start",
    "can_amount",
    "max_runtime",
    "speed",
    "day_start",
    "day_end",
}


def _dosing_system() -> vol.In:
    """Return the validator for a ``dosing_system`` field."""
    return vol.In(list(DOSING_SYSTEM_SLUGS))


def _targeted(fields: VolDictType) -> VolSchemaType:
    """Build a schema for a service selected through a ``target:`` block.

    Home Assistant merges the resolved target into ``call.data``, so a plain
    ``vol.Schema`` with the default PREVENT_EXTRA rejects an ``area_id`` (or
    ``floor_id``/``label_id``) with "extra keys not allowed" even though the
    UI offers those pickers.  ``cv.make_entity_service_schema`` adds all five
    target fields and enforces that at least one of them is present.
    """
    return cv.make_entity_service_schema(dict(fields))


def _for_device(fields: VolDictType | None = None) -> VolSchemaType:
    """Build a schema for a service that takes an explicit ``device_id`` field."""
    schema: VolDictType = {vol.Required(ATTR_DEVICE_ID): DEVICE_ID_SELECTOR}
    schema.update(fields or {})
    return vol.Schema(schema)


def _rule_outputs() -> VolDictType:
    """Return the three optional ``output_N``/``output_N_state`` pairs."""
    fields: VolDictType = {}
    for index in range(1, 4):
        fields[vol.Optional(f"output_{index}")] = cv.string
        fields[vol.Optional(f"output_{index}_state")] = vol.All(
            vol.Coerce(int), vol.Range(min=0, max=6)
        )
    return fields


def _validate_dosing_target(data: dict) -> dict:
    """Validate target_value range based on dosing_system.

    Raises vol.Invalid if the target_value is outside the safe physical range
    for the given dosing_system.
    """
    ds = data["dosing_system"]
    val = float(data["target_value"])
    lo, hi = DOSING_TARGET_RANGES.get(ds, (0.0, 100.0))
    if not (lo <= val <= hi):
        raise vol.Invalid(f"target_value {val} out of range for {ds}: allowed {lo}-{hi}")
    return data


def get_service_schemas() -> dict[str, Any]:
    """Get all service schemas."""
    schemas: dict[str, Any] = {
        "control_pump": _targeted(
            {
                vol.Required("action"): vol.In(
                    ["speed_control", "force_off", "eco_mode", "boost_mode", "auto"]
                ),
                vol.Optional("speed", default=2): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_PUMP_SPEED, max=MAX_PUMP_SPEED),
                ),
                vol.Optional("duration", default=0): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=MAX_PUMP_DURATION)
                ),
            }
        ),
        "smart_dosing": _targeted(
            {
                vol.Required("dosing_type"): vol.In(list(DOSING_TYPE_MAPPING)),
                vol.Required("action"): vol.In(["manual_dose", "auto", "stop"]),
                vol.Required("duration"): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_DOSING_DURATION, max=MAX_DOSING_DURATION),
                ),
                vol.Optional("safety_override", default=False): cv.boolean,
            }
        ),
        "manage_pv_surplus": _targeted(
            {
                # The controller knows no AUTO mode for PVSURPLUS (manual
                # section 26.3 documents ON and OFF only), so the service does
                # not offer one either - the API would have rewritten it to OFF.
                vol.Required("mode"): vol.In(["activate", "deactivate"]),
                vol.Optional("pump_speed", default=2): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_PUMP_SPEED, max=MAX_PUMP_SPEED),
                ),
            }
        ),
        "control_dmx_scenes": _for_device(
            {
                vol.Required("action"): vol.In(
                    ["all_on", "all_off", "all_auto", "sequence", "party_mode"]
                ),
                vol.Optional("sequence_delay", default=2): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=60)
                ),
            }
        ),
        "set_light_color_pulse": _targeted(
            {
                vol.Optional("pulse_count", default=1): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=10)
                ),
                vol.Optional("pulse_interval", default=500): vol.All(
                    vol.Coerce(int), vol.Range(min=100, max=2000)
                ),
            }
        ),
        "manage_digital_rules": _for_device(
            {
                # Controller exposes DIRULE_1..8 (internal name: SWITCHINGRULE_1..8)
                vol.Required("rule_key"): vol.In([f"DIRULE_{i}" for i in range(1, 9)]),
                vol.Required("action"): vol.In(["trigger", "lock", "unlock"]),
            }
        ),
        "test_output": _for_device(
            {
                # Output keys are plain identifiers (e.g. PUMP, EXT1_1); the
                # API builds the query string without URL-encoding this value
                vol.Required("output"): vol.All(cv.string, vol.Match(r"^[A-Za-z0-9_]+$")),
                vol.Optional("mode", default="SWITCH"): vol.In(["SWITCH", "ON", "OFF"]),
                vol.Optional("duration", default=120): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=900)
                ),
            }
        ),
        # reset_blocking clears fault-induced blockings on the controller
        # (e.g. BLOCKED_BY_ESC after an empty-canister alarm was acknowledged).
        # Useful after fixing the underlying issue so dosing/control resumes.
        "reset_blocking": _for_device(),
        # set_can_amount updates a dosing canister fill level after refill.
        # action=adjust just sets the new level; action=reset also clears the
        # daily counter and "last reset" timestamp.
        "set_can_amount": _for_device(
            {
                vol.Required("dosing_key"): vol.In(
                    [
                        "DOS_1_CL",  # Chlorine
                        "DOS_2_ELO",  # Electrolysis
                        "DOS_4_PHM",  # pH-
                        "DOS_5_PHP",  # pH+
                        "DOS_6_FLOC",  # Flocculant
                    ]
                ),
                vol.Required("amount_ml"): vol.All(vol.Coerce(int), vol.Range(min=1, max=100000)),
                vol.Optional("action", default="adjust"): vol.In(["adjust", "reset"]),
            }
        ),
        # set_system_service enables/disables a controller-side system
        # service (FTP, Samba, SSH, AirPlay, HomeKit, Alexa, tunnels).
        "set_system_service": _for_device(
            {
                vol.Required("service"): vol.In(
                    [
                        "ftp",
                        "samba",
                        "ssh",
                        "shairport",
                        "homebridge",
                        "alexa",
                        "tunnel",
                        "support_tunnel",
                    ]
                ),
                vol.Required("enabled"): cv.boolean,
            }
        ),
        # get_system_services_status returns the live state of all
        # controller-side services as a dict.
        "get_system_services_status": _for_device(),
        # set_omni_position drives the OmniTronic multi-port valve to a
        # fixed position.  Position 0 (Filtration) also returns the
        # controller to automatic mode.
        "set_omni_position": _for_device(
            {
                vol.Required("position"): vol.All(vol.Coerce(int), vol.Range(min=0, max=5)),
            }
        ),
        # get_live_trace_snapshot returns a single-row snapshot of every
        # controller reading (CSV→dict) for ad-hoc troubleshooting.
        "get_live_trace_snapshot": _for_device(),
        "export_diagnostic_logs": _for_device(
            {
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
        "get_connection_status": _for_device(),
        "get_error_summary": _for_device(
            {vol.Optional("include_history", default=False): cv.boolean}
        ),
        "test_connection": _for_device(),
        "clear_error_history": _for_device(),
        # NEW HTTP-based control services (Direct setFunctionManually API)
        "control_pump_http": _targeted(
            {
                # Speed 0 would be sent as "manual ON at speed 0", which is not
                # an off command; use action: off / force_off for that instead.
                vol.Optional("speed"): vol.In([1, 2, 3]),
                vol.Optional("action"): vol.In(["on", "off", "eco", "boost"]),
                vol.Optional("force_off", default=False): cv.boolean,
            }
        ),
        "control_heater_http": _targeted(
            {
                vol.Optional("action"): vol.In(["on", "off"]),
                vol.Optional("target_temperature"): vol.All(
                    vol.Coerce(float), vol.Range(min=10, max=60)
                ),
            }
        ),
        "control_solar_http": _targeted(
            {
                vol.Optional("action"): vol.In(["on", "off"]),
                vol.Optional("target_temperature"): vol.All(
                    vol.Coerce(float), vol.Range(min=10, max=60)
                ),
            }
        ),
        "control_cover_http": _targeted(
            {vol.Optional("action"): vol.In(["open", "close", "stop"])}
        ),
        "control_backwash_http": _targeted(
            {
                vol.Required("action"): vol.In(["run", "abort"]),
                vol.Required("duration_seconds"): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=10, max=3600),
                ),
                vol.Optional("safety_override", default=False): cv.boolean,
            }
        ),
        "manual_dosing_http": _targeted(
            {
                vol.Required("dosing_system"): _dosing_system(),
                vol.Required("runtime_seconds"): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=3600)
                ),
                vol.Optional("safety_override", default=False): cv.boolean,
            }
        ),
        # Dosing Configuration Services
        "configure_dosing": _targeted(
            {
                vol.Required("dosing_system"): _dosing_system(),
                vol.Required("config_key"): vol.In(sorted(ALLOWED_DOSING_CONFIG_KEYS)),
                vol.Required("value"): vol.Any(
                    cv.boolean,
                    vol.Coerce(int),
                    vol.Coerce(float),
                    cv.string,
                ),
            }
        ),
        "set_dosing_target": vol.All(
            _targeted(
                {
                    vol.Required("dosing_system"): _dosing_system(),
                    vol.Required("target_value"): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=0, max=100),
                    ),
                }
            ),
            _validate_dosing_target,
        ),
        "set_dosing_daytime": _targeted(
            {
                vol.Required("dosing_system"): _dosing_system(),
                vol.Optional("day_start"): vol.Match(r"^\d{2}:\d{2}$"),
                vol.Optional("day_end"): vol.Match(r"^\d{2}:\d{2}$"),
            }
        ),
        "set_dosing_max_daily": _targeted(
            {
                vol.Required("dosing_system"): _dosing_system(),
                vol.Required("max_daily_ml"): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=10, max=10000),
                ),
            }
        ),
        "enable_dosing": _targeted(
            {
                vol.Required("dosing_system"): _dosing_system(),
                vol.Required("enabled"): cv.boolean,
            }
        ),
        "configure_temp_rule": _targeted(
            {
                vol.Required("rule_id"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Optional("enabled", default=True): cv.boolean,
                vol.Optional("sensor_1"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Optional("sensor_2"): vol.All(vol.Coerce(int), vol.Range(min=0, max=8)),
                vol.Optional("logic"): vol.In([">=", "<="]),
                vol.Optional("diff_value"): vol.Coerce(float),
                vol.Optional("hyst_value"): vol.Coerce(float),
                vol.Optional("runtime_on"): vol.Match(r"^\d{2}:\d{2}$"),
                vol.Optional("runtime_off"): vol.Match(r"^\d{2}:\d{2}$"),
                **_rule_outputs(),
            }
        ),
        "configure_analog_rule": _targeted(
            {
                vol.Required("rule_id"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Optional("enabled", default=True): cv.boolean,
                vol.Optional("adc_input"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Optional("logic"): vol.In([">=", "<="]),
                vol.Optional("threshold"): vol.Coerce(float),
                vol.Optional("hysteresis"): vol.Coerce(float),
                vol.Optional("runtime_on"): vol.Match(r"^\d{2}:\d{2}$"),
                vol.Optional("runtime_off"): vol.Match(r"^\d{2}:\d{2}$"),
                **_rule_outputs(),
            }
        ),
        "configure_switching_rule": _targeted(
            {
                vol.Required("rule_id"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Optional("enabled", default=True): cv.boolean,
                vol.Optional("di_input"): vol.All(vol.Coerce(int), vol.Range(min=1, max=12)),
                vol.Optional("contact_type"): vol.In([0, 1]),
                vol.Optional("output"): cv.string,
                vol.Optional("action_on"): vol.All(vol.Coerce(int), vol.Range(min=0, max=6)),
                vol.Optional("action_off"): vol.All(vol.Coerce(int), vol.Range(min=0, max=6)),
                vol.Optional("timeout"): vol.All(vol.Coerce(int), vol.Range(min=0, max=3600)),
            }
        ),
        "configure_timer_rule": _targeted(
            {
                vol.Required("rule_id"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Optional("enabled", default=True): cv.boolean,
                vol.Optional("on_time"): vol.Match(r"^\d{2}:\d{2}$"),
                vol.Optional("off_time"): vol.Match(r"^\d{2}:\d{2}$"),
                vol.Optional("weekdays"): vol.All(vol.Coerce(int), vol.Range(min=0, max=127)),
                **_rule_outputs(),
            }
        ),
        "enable_rule": _targeted(
            {
                vol.Required("rule_type"): vol.In(
                    ["temprule", "analogrule", "switchingrule", "timerrule"]
                ),
                vol.Required("rule_id"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Required("enabled"): cv.boolean,
            }
        ),
        "control_extension_relay": _targeted(
            {
                # The controller has two extension banks of eight relays each
                # (EXT1_1..EXT1_8 and EXT2_1..EXT2_8), so a single 1-8 "relay
                # id" cannot address a relay - bank and relay are both needed.
                vol.Required("bank"): vol.All(vol.Coerce(int), vol.Range(min=1, max=2)),
                vol.Required("relay"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
                vol.Optional("action", default="on"): vol.In(["on", "off", "auto"]),
                vol.Optional("duration", default=0): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=86400)
                ),
            }
        ),
        "configure_sensor_calibration": _targeted(
            {
                vol.Required("sensor_id"): vol.All(vol.Coerce(int), vol.Range(min=1, max=12)),
                vol.Optional("offset"): vol.All(vol.Coerce(float), vol.Range(min=-10, max=10)),
                vol.Optional("multiplier"): vol.All(
                    vol.Coerce(float), vol.Range(min=0.5, max=2.0)
                ),
                vol.Optional("min_value"): vol.Coerce(float),
                vol.Optional("max_value"): vol.Coerce(float),
            }
        ),
        "get_calibration_status": _for_device(),
        "get_backwash_status": _for_device(),
        "get_system_update_status": _for_device(),
    }
    schemas.update(get_refill_overflow_schemas())
    return schemas
