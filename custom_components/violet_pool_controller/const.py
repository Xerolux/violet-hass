# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""This module serves as the central hub for all constants in the Violet Pool
Controller integration.

It aggregates constants from specialized modules (`const_api`, `const_devices`,
`const_sensors`, `const_features`) to provide a single, consistent import point
for the rest of the integration. This modular approach enhances maintainability
by organizing constants based on their functional area.

The module also defines core integration-level information, such as the domain,
version, and manufacturer details, as well as configuration keys and default values.
"""

from __future__ import annotations

from typing import Any

from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
)

# flake8: noqa: F401, F403 - Allows central exporting of constants
# ruff: noqa: F401, F403 - Allows central exporting of constants
from violet_poolcontroller_api.const_api import *
from violet_poolcontroller_api.const_devices import *

# Explicit re-exports via assignment so that both type checkers and static
# analysis see these names as defined and used here - the external package
# ships no py.typed marker, so the wildcard imports above are opaque to mypy
from violet_poolcontroller_api import const_api as _const_api
from violet_poolcontroller_api import const_devices as _const_devices

from .const_features import *
from .const_sensors import *

ACTION_ALLAUTO = _const_api.ACTION_ALLAUTO
ACTION_ALLOFF = _const_api.ACTION_ALLOFF
ACTION_ALLON = _const_api.ACTION_ALLON
ACTION_AUTO = _const_api.ACTION_AUTO
ACTION_COLOR = _const_api.ACTION_COLOR
ACTION_LOCK = _const_api.ACTION_LOCK
ACTION_MAN = _const_api.ACTION_MAN
ACTION_OFF = _const_api.ACTION_OFF
ACTION_ON = _const_api.ACTION_ON
ACTION_PUSH = _const_api.ACTION_PUSH
ACTION_UNLOCK = _const_api.ACTION_UNLOCK
COVER_FUNCTIONS = _const_devices.COVER_FUNCTIONS
DEVICE_PARAMETERS = _const_devices.DEVICE_PARAMETERS

# =============================================================================
# INTEGRATION INFO
# =============================================================================

DOMAIN = "violet_pool_controller"
INTEGRATION_VERSION = "2.0.2"
MANUFACTURER = "PoolDigital GmbH & Co. KG"

# =============================================================================
# CONFIGURATION KEYS
# =============================================================================

CONF_API_URL = CONF_HOST
CONF_POLLING_INTERVAL = "polling_interval"
CONF_TIMEOUT_DURATION = "timeout_duration"
CONF_RETRY_ATTEMPTS = "retry_attempts"
CONF_USE_SSL = "use_ssl"
CONF_DEVICE_NAME = "device_name"
CONF_CONTROLLER_NAME = "controller_name"
CONF_ACTIVE_FEATURES = "active_features"
CONF_SELECTED_SENSORS = "selected_sensors"
CONF_POOL_SIZE = "pool_size"
CONF_POOL_TYPE = "pool_type"
CONF_DISINFECTION_METHOD = "disinfection_method"
CONF_DOSING_STANDALONE = "dosing_standalone"
CONF_INVERT_COVER = "invert_cover"
CONF_ALLOW_UNSAFE_SWITCHES = "allow_unsafe_switches"

# ACTION_* constants come from violet_poolcontroller_api.const_api (wildcard
# import above) - do not redefine them here, local copies drift from the API.

# Default Values
DEFAULT_POLLING_INTERVAL = 10
DEFAULT_TIMEOUT_DURATION = 10
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_USE_SSL = False
DEFAULT_VERIFY_SSL = False
DEFAULT_DEVICE_NAME = "Violet Pool Controller"
DEFAULT_CONTROLLER_NAME = "Violet Pool Controller"
DEFAULT_PORT = 80
DEFAULT_POOL_SIZE = 50
DEFAULT_POOL_TYPE = "outdoor"
DEFAULT_DISINFECTION_METHOD = "chlorine"
DEFAULT_DOSING_STANDALONE = False
DEFAULT_INVERT_COVER = False
DEFAULT_ALLOW_UNSAFE_SWITCHES = False

# =============================================================================
# POOL CONFIGURATION
# =============================================================================

POOL_TYPES = ["outdoor", "indoor", "whirlpool", "natural", "combination"]
DISINFECTION_METHODS = ["chlorine", "salt", "bromine", "active_oxygen", "uv", "ozone"]

# =============================================================================
# COVER & DEVICE CONTROL CONSTANTS
# =============================================================================
# These constants are imported/used by cover.py, switch.py, and service handlers.
# They map high-level control actions to protocol command strings recognized
# by the Violet Pool Controller API.

# COVER_FUNCTIONS and DEVICE_PARAMETERS come from
# violet_poolcontroller_api.const_devices (wildcard import above).

# COVER_STATE_MAP is also provided by violet_poolcontroller_api.const_devices
# (wildcard import above) — no local override needed.

# =============================================================================
# VERSION INFO
# =============================================================================

VERSION_INFO = {
    "version": INTEGRATION_VERSION,
    "release_date": "2026-05-28",
    "major_features": [
        "Fixed state 2 mapping: Auto-Priority OFF is now correctly OFF (was ON)",
        "Fixed select mode mapping: all auto states map to AUTO mode",
        "Updated state descriptions to match DEVICE_STATE_MAPPING",
        "Added OMNI DC output switches (OMNI_DC0-OMNI_DC5)",
        "Added H2O2 dosing support",
        "Added overflow/backwash/bathing AI binary sensors",
        "Added runtime and dosing statistics sensors",
        "Updated setpoint config keys to match API",
        "Updated API dependency to violet-poolController-api 0.0.24",
    ],
}

# =============================================================================
# DOSING / OUTPUT DETAIL STATE DESCRIPTIONS
# =============================================================================
# Human-readable English labels for the BLOCKED_BY_*/WAITING_FOR_*/etc. detail
# codes that the controller returns inside DOS_*_STATE arrays (e.g.
# ``["BLOCKED_BY_PUMP_OFF", "BLOCKED_BY_MISSING_MODULE"]``) and inside
# composite PUMPSTATE/HEATERSTATE/SOLARSTATE values (e.g. ``"3|PUMP_ANTI_FREEZE"``).
# Source: firmware includes/controlfunction_*.js + includes/dosage_controller_*.js
# + sample READINGS.json from controller snapshot 1.0.9.
DOSING_STATE_DESCRIPTIONS: dict[str, str] = {
    # -- Frost / anti-freeze modes (PUMPSTATE composite key) --
    "PUMP_ANTI_FREEZE": "Frost Protection",
    # -- Generic thresholds (firmware uses both spellings "TRESHOLDS" and
    # "THRESHOLDS"; keep both for safety) --
    "BLOCKED_BY_TRESHOLDS": "Blocked (Thresholds)",
    "BLOCKED_BY_THRESHOLDS": "Blocked (Thresholds)",
    "BLOCKED_BY_CL_TRESHOLDS": "Blocked (Chlorine Thresholds)",
    "BLOCKED_BY_CL_THRESHOLDS": "Blocked (Chlorine Thresholds)",
    "TRESHOLDS_REACHED": "Thresholds Reached",
    "THRESHOLDS_REACHED": "Thresholds Reached",
    "TRESHOLDS_REACHED_CL": "Chlorine Thresholds Reached",
    "THRESHOLDS_REACHED_CL": "Chlorine Thresholds Reached",
    # -- Block by pump state --
    "BLOCKED_BY_PUMP": "Blocked (Pump Off)",
    "BLOCKED_BY_PUMP_OFF": "Blocked (Pump Off)",
    "BLOCKED_BY_PUMP_DELAY": "Blocked (Pump Start Delay)",
    "BLOCKED_BY_START_DELAY": "Blocked (Start Delay)",
    "BLOCKED_BY_POSTRUN": "Blocked (Post-Run)",
    "BLOCKED_BY_HEATER_OFF_DELAY": "Blocked (Heater Off Delay)",
    # -- Block by flow / circulation --
    "BLOCKED_BY_FLOW": "Blocked (Flow)",
    "BLOCKED_BY_MISSING_FLOW": "Blocked (Missing Flow)",
    "BLOCKED_BY_MISSING_CIRCULATION": "Blocked (Missing Circulation)",
    "WAITING_FOR_PUMP": "Waiting for Pump",
    "WAITING_FOR_FLOW": "Waiting for Flow",
    # -- Block by other subsystems --
    "BLOCKED_BY_SOLAR": "Blocked (Solar)",
    "BLOCKED_BY_HEATER": "Blocked (Heater)",
    "BLOCKED_BY_BACKWASH": "Blocked (Backwash)",
    "BLOCKED_BY_OUTSIDE_TEMP": "Blocked (Outside Temperature)",
    "BLOCKED_BY_MAXTEMP": "Blocked (Max Temperature)",
    "BLOCKED_BY_BOILER_TEMP": "Blocked (Boiler Temperature)",
    "BLOCKED_BY_MAX_AMOUNT": "Blocked (Max Daily Amount)",
    # -- Hardware / module issues --
    "BLOCKED_BY_MISSING_MODULE": "Blocked (Missing Module)",
    "BLOCKED_BY_SENSOR_FAULT": "Blocked (Sensor Fault)",
    # -- Rules / overrides --
    "BLOCKED_BY_EMERGENCY_CONTROL_RULE": "Blocked (Emergency Rule)",
    "BLOCKED_BY_ESC": "Blocked (Emergency Stop)",
    "BLOCKED_BY_MANUAL_OFF": "Blocked (Manual Off)",
    "BLOCKED_BY_UPDATE": "Blocked (Update)",
    "BLOCKED_BY_RULE": "Blocked (Rule)",
    # -- OmniTronic multi-port valve states --
    "BLOCKED_BY_OMNI": "Blocked (OmniTronic)",
    "BLOCKED_BY_OMIN": "Blocked (OmniTronic)",  # firmware typo, kept for safety
    "BLOCKED_BY_OMNI_POS": "Blocked (OmniTronic Positioning)",
    "BLOCKED_BY_Z1Z2": "Blocked (OmniTronic Z1/Z2 Contact)",
    # -- Electrolysis specific --
    "BLOCKED_BY_POLEREVERSAL": "Blocked (Polarity Reversal)",  # firmware typo
    # -- Waiting states --
    "WAITING_FOR_DOSAGECONTROLLERS": "Waiting for Dosing Controllers",
    "WAITING_FOR_HEATER_POSTRUN": "Waiting for Heater Post-Run",
    "WAITING_FOR_PREFILL": "Waiting for Pre-Fill",
    "WAITING_FOR_STARTTIME": "Waiting for Start Time",
    # -- Active dosing states --
    "DOSING": "Dosing",
    "DOSING_PAUSED": "Dosing Paused",
    "MANUAL_DOSING": "Manual Dosing",
}

# =============================================================================
# DIAGNOSTIC PROBLEM KEYS
# =============================================================================
# Sensor keys whose value indicates an active fault or hardware-issue state.
# Used by VioletHealthSensor to aggregate all problems into one summary.
#
# Conventions:
#   * Binary-sensor keys are True == problem.
#   * Hardware-module keys (HW_*) are True == module PRESENT (so the sensor
#     being False indicates a hardware problem).
#   * State-string keys (e.g. BACKWASH_OMNI_STATE) use a denylist of bad
#     substrings rather than a simple boolean check.
DIAGNOSTIC_PROBLEM_KEYS: dict[str, dict[str, Any]] = {
    # Binary problem sensors (device_class=PROBLEM)
    "CIRCULATION_STATE": {"label": "Circulation Issue", "type": "problem"},
    "ELECTRODE_FLOW_STATE": {"label": "Electrode Flow Issue", "type": "problem"},
    "PRESSURE_STATE": {"label": "Pressure Issue", "type": "problem"},
    "CAN_RANGE_STATE": {"label": "Can Range Issue", "type": "problem"},
    "OVERFLOW_OVERFILL_STATE": {"label": "Overflow Overfill", "type": "problem"},
    "OVERFLOW_DRYRUN_STATE": {"label": "Overflow Dry Run", "type": "problem"},
    # Hardware-module presence sensors (False == missing/disconnected).
    # Inverted in the health check.
    "HW_BASE_MODULE": {"label": "Base Module", "type": "hardware"},
    "HW_DOSING_MODULE": {"label": "Dosing Module", "type": "hardware"},
    "HW_EXTENSION_MODULE_1": {"label": "Extension Module 1", "type": "hardware"},
    "HW_EXTENSION_MODULE_2": {"label": "Extension Module 2", "type": "hardware"},
    "HW_DMX_MODULE": {"label": "DMX Module", "type": "hardware"},
    "HW_DIRULE_MODULE": {"label": "Digital Rules Module", "type": "hardware"},
}

# OmniTronic / backwash state strings that indicate an active fault.
# Matched case-insensitively against BACKWASH_OMNI_STATE.
OMNI_FAULTY_STATES: tuple[str, ...] = (
    "BLOCKED_BY_Z1Z2",
    "BLOCKED_BY_OMNI",
    "BLOCKED_BY_OMIN",  # firmware typo
    "POS_FAILURE",
    "POS_FAILURE_FILTRATION",
    "POS_FAILURE_RINSE",
    "Z1Z2_CONTACT_FAILURE",
    "OMNI_Z1Z2_CONTACT_FAILURE",
)
