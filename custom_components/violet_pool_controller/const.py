# Domain of the integration
DOMAIN = "violet_pool_controller"

# Configuration keys
CONF_API_URL = "host"  # Changed to 'host' - more standard for Home Assistant
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_USE_SSL = "use_ssl"
CONF_MQTT_ENABLED = "mqtt_enabled"  #  Keep MQTT config options, even if unused
CONF_MQTT_BROKER = "mqtt_broker"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_MQTT_BASE_TOPIC = "mqtt_base_topic"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name" # Add device_name

# Defaults
DEFAULT_POLLING_INTERVAL = 10  # Default polling interval in seconds
DEFAULT_USE_SSL = False  # Default SSL setting
DEFAULT_MQTT_ENABLED = False  # Default MQTT setting (disabled by default)
DEFAULT_DEVICE_NAME = "Violet Pool Controller" # Default device name

# Integration details
INTEGRATION_VERSION = "0.0.9.0"  # Increased version
MIN_REQUIRED_HA_VERSION = "2023.9.0"  # Keep the minimum HA version

# Log messages
LOGGER_NAME = f"{DOMAIN}_logger"  #  Consistent with other files.

# API Endpoints (path extensions)
API_READINGS = "/getReadings?ALL"
API_SET_FUNCTION_MANUALLY = "/setFunctionManually"

# Device name and manufacturer - now using constants for consistency
DEVICE_NAME = "Violet Pool Controller" # Redundant
MANUFACTURER = "PoolDigital GmbH & Co. KG"

# MQTT Default values (adjust these based on typical MQTT configurations)
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_BASE_TOPIC = "violet_pool_controller"
