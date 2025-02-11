# Domain of the integration
DOMAIN = "violet_pool_controller"

# Configuration keys
CONF_API_URL = "api_url"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_USE_SSL = "use_ssl"
CONF_MQTT_ENABLED = "mqtt_enabled"  # You'll likely remove these MQTT options
CONF_MQTT_BROKER = "mqtt_broker"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_MQTT_BASE_TOPIC = "mqtt_base_topic"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"


# Defaults
DEFAULT_POLLING_INTERVAL = 10  # Default polling interval in seconds
DEFAULT_USE_SSL = False  # Default SSL setting
DEFAULT_MQTT_ENABLED = False  # Default MQTT setting (likely to be removed)
DEFAULT_MQTT_PORT = 1883  # (likely to be removed)
DEFAULT_MQTT_BASE_TOPIC = "violet_pool_controller"  # (likely to be removed)

# Integration details
INTEGRATION_VERSION = "0.0.8.8"
MIN_REQUIRED_HA_VERSION = "2023.9.0"

# API Endpoints (path extensions)
API_READINGS = "/getReadings?ALL"
API_SET_FUNCTION_MANUALLY = "/setFunctionManually"

# Supported platforms
PLATFORMS = ["switch", "sensor", "binary_sensor"]
