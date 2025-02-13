# Domain der Integration
DOMAIN = "violet_pool_controller"

# Konfigurationsschlüssel
CONF_API_URL = "host"  # Umbenannt zu 'host' – standardgemäß in Home Assistant
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_USE_SSL = "use_ssl"
CONF_MQTT_ENABLED = "mqtt_enabled"  # MQTT-Optionen beibehalten, auch wenn aktuell ungenutzt
CONF_MQTT_BROKER = "mqtt_broker"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_MQTT_BASE_TOPIC = "mqtt_base_topic"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"  # Device-Name hinzufügen

# Standardwerte
DEFAULT_POLLING_INTERVAL = 10  # Standard-Pollingintervall in Sekunden
DEFAULT_USE_SSL = False  # Standard-SSL-Einstellung
DEFAULT_MQTT_ENABLED = False  # MQTT standardmäßig deaktiviert
DEFAULT_DEVICE_NAME = "Violet Pool Controller"  # Standard-Gerätename

# Integrationsdetails
INTEGRATION_VERSION = "0.0.9.0"  # Erhöhte Version
MIN_REQUIRED_HA_VERSION = "2023.9.0"  # Mindestversion von Home Assistant

# Logger-Name
LOGGER_NAME = f"{DOMAIN}_logger"  # Einheitlich mit den anderen Dateien

# API-Endpunkte (Pfad-Erweiterungen)
API_READINGS = "/getReadings?ALL"
API_SET_FUNCTION_MANUALLY = "/setFunctionManually"

# Herstellerinformationen
MANUFACTURER = "PoolDigital GmbH & Co. KG"

# MQTT Standardwerte (anpassen, falls nötig)
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_BASE_TOPIC = "violet_pool_controller"
