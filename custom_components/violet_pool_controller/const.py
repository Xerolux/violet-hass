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
from .const_features import *
from .const_sensors import *

# =============================================================================
# INTEGRATION INFO
# =============================================================================

DOMAIN = "violet_pool_controller"
INTEGRATION_VERSION = "1.2.1"
MANUFACTURER = "PoolDigital GmbH & Co. KG"

# =============================================================================
# CONFIGURATION KEYS
# =============================================================================

CONF_API_URL = CONF_HOST
CONF_POLLING_INTERVAL = "polling_interval"
CONF_TIMEOUT_DURATION = "timeout_duration"
CONF_RETRY_ATTEMPTS = "retry_attempts"
CONF_FORCE_UPDATE = "force_update"
CONF_USE_SSL = "use_ssl"
CONF_DEVICE_NAME = "device_name"
CONF_CONTROLLER_NAME = "controller_name"
CONF_ACTIVE_FEATURES = "active_features"
CONF_SELECTED_SENSORS = "selected_sensors"
CONF_POOL_SIZE = "pool_size"
CONF_POOL_TYPE = "pool_type"
CONF_DISINFECTION_METHOD = "disinfection_method"
CONF_ENABLE_DIAGNOSTIC_LOGGING = "enable_diagnostic_logging"
CONF_DOSING_STANDALONE = "dosing_standalone"

# =============================================================================
# ACTION CONSTANTS
# =============================================================================

ACTION_PUSH = "PUSH"
ACTION_ALLAUTO = "ALLAUTO"
ACTION_ALLOFF = "ALLOFF"
ACTION_ALLON = "ALLON"
ACTION_AUTO = "AUTO"
ACTION_OFF = "OFF"
ACTION_ON = "ON"

# Default Values
DEFAULT_POLLING_INTERVAL = 10
DEFAULT_TIMEOUT_DURATION = 10
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_FORCE_UPDATE = False
DEFAULT_USE_SSL = False
DEFAULT_VERIFY_SSL = True
DEFAULT_DEVICE_NAME = "Violet Pool Controller"
DEFAULT_CONTROLLER_NAME = "Violet Pool Controller"
DEFAULT_PORT = 80
DEFAULT_POOL_SIZE = 50
DEFAULT_POOL_TYPE = "outdoor"
DEFAULT_DISINFECTION_METHOD = "chlorine"
DEFAULT_ENABLE_DIAGNOSTIC_LOGGING = False
DEFAULT_DOSING_STANDALONE = False

# =============================================================================
# POOL CONFIGURATION
# =============================================================================

POOL_TYPES = ["outdoor", "indoor", "whirlpool", "natural", "combination"]
DISINFECTION_METHODS = ["chlorine", "salt", "bromine", "active_oxygen", "uv", "ozone"]

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
