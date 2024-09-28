import paho.mqtt.client as mqtt
import logging
from .const import CONF_MQTT_BROKER, CONF_MQTT_PORT, CONF_MQTT_USERNAME, CONF_MQTT_PASSWORD, CONF_MQTT_BASE_TOPIC

_LOGGER = logging.getLogger(__name__)

async def async_setup_mqtt(hass, config):
    """Asynchronously set up the MQTT client based on configuration."""
    broker = config.get(CONF_MQTT_BROKER)
    port = config.get(CONF_MQTT_PORT, 1883)
    username = config.get(CONF_MQTT_USERNAME)
    password = config.get(CONF_MQTT_PASSWORD)
    base_topic = config.get(CONF_MQTT_BASE_TOPIC)

    client = mqtt.Client()

    if username and password:
        client.username_pw_set(username, password)

    try:
        # Asynchronous connection attempt to the MQTT broker
        await hass.async_add_executor_job(client.connect, broker, port)
        _LOGGER.info(f"Connected to MQTT broker at {broker}:{port}")
    except Exception as e:
        _LOGGER.error(f"Failed to connect to MQTT broker: {e}")
        return None

    return client
