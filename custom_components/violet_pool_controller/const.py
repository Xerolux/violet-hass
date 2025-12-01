"""This module serves as the central hub for all constants in the Violet Pool Controller integration.

It aggregates constants from specialized modules (`const_api`, `const_devices`,
`const_sensors`, `const_features`) to provide a single, consistent import point
for the rest of the integration. This modular approach enhances maintainability
by organizing constants based on their functional area.

The module also defines core integration-level information, such as the domain,
version, and manufacturer details, as well as configuration keys and default values.
"""

# flake8: noqa: F401, F403 - Allows central exporting of constants
# ruff: noqa: F401, F403 - Allows central exporting of constants

from .const_api import *
from .const_devices import *
from .const_features import *
from .const_sensors import *

# =============================================================================
# INTEGRATION INFO
# =============================================================================

DOMAIN = "violet_pool_controller"
INTEGRATION_VERSION = "0.2.0-beta.4"
MANUFACTURER = "PoolDigital GmbH & Co. KG"

# =============================================================================
# CONFIGURATION KEYS
# =============================================================================

CONF_API_URL = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_TIMEOUT_DURATION = "timeout_duration"
CONF_RETRY_ATTEMPTS = "retry_attempts"
CONF_USE_SSL = "use_ssl"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_CONTROLLER_NAME = "controller_name"
CONF_ACTIVE_FEATURES = "active_features"
CONF_SELECTED_SENSORS = "selected_sensors"
CONF_POOL_SIZE = "pool_size"
CONF_POOL_TYPE = "pool_type"
CONF_DISINFECTION_METHOD = "disinfection_method"

# Default Values
DEFAULT_POLLING_INTERVAL = 10
DEFAULT_TIMEOUT_DURATION = 10
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_USE_SSL = False
DEFAULT_DEVICE_NAME = "Violet Pool Controller"
DEFAULT_CONTROLLER_NAME = "Violet Pool Controller"
DEFAULT_POOL_SIZE = 50
DEFAULT_POOL_TYPE = "outdoor"
DEFAULT_DISINFECTION_METHOD = "chlorine"

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
    "release_date": "2025-11-20",
    "major_features": [
        "Complete 3-State Switch Support with State 4 Fix",
        "PVSURPLUS Parameter Support",
        "Cover String-State Handling",
        "Extended Sensor Coverage",
        "Enhanced DMX Scene Control",
        "Complete Extension Relay Support",
        "Modular Constants Structure",
        "API Rate Limiting Support",
    ],
}
