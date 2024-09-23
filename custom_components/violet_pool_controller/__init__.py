import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, CONF_API_URL, CONF_DEVICE_NAME  # Import CONF_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Device from a config entry."""
    
    # Fetch API URL from the config entry
    api_url = entry.data[CONF_API_URL]
    
    # Get the shared aiohttp session
    session = aiohttp_client.async_get_clientsession(hass)
    
    # Get the custom device name or default to 'Violet Pool Controller'
    device_name = entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
    
    try:
        # Fetch data from the API, including firmware version
        async with session.get(api_url, ssl=False) as response:
            data = await response.json()
            firmware_version = data.get('fw', 'Unknown')  # Get the firmware from JSON data
            ip_address = entry.data.get('host', 'Unknown IP')  # Get IP from config entry

            _LOGGER.info("Registering device with firmware version: %s and IP: %s", firmware_version, ip_address)

            # Register device with Home Assistant
            device_registry = dr.async_get(hass)
            device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "violet_pool_controller")},
                manufacturer="PoolDigital GmbH & Co. KG",
                name=device_name,  # Use custom device name
                model="Violet Model X",
                sw_version=firmware_version,
                configuration_url=f"http://{ip_address}",  # Store the IP address in the configuration URL
            )

            _LOGGER.info("Device '%s' registered successfully.", device_name)

    except Exception as err:
        _LOGGER.error("Failed to register device: %s", err)
        return False

    # Forward entry setup to sensor platform using the new method
    _LOGGER.info("Forwarding entry setup to sensor platform.")
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return unload_ok
