import logging
import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, CONF_API_URL, CONF_POLLING_INTERVAL, CONF_USE_SSL, CONF_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)

class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Violet Device."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_url = user_input[CONF_API_URL]
            use_ssl = user_input.get(CONF_USE_SSL, False)
            device_name = user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller")

            # Check for duplicate entries based on the API URL (unique ID)
            await self.async_set_unique_id(api_url)
            self._abort_if_unique_id_configured()

            # Validate the API URL
            session = aiohttp_client.async_get_clientsession(self.hass)
            try:
                async with async_timeout.timeout(10):
                    async with session.get(api_url, ssl=use_ssl) as response:
                        response.raise_for_status()  # Raise error for non-200 status codes
                        data = await response.json()
                        
                        # Log the complete response for debugging
                        _LOGGER.debug("API response received: %s", data)

                        # Ensure firmware version exists in the response
                        firmware_version = data.get('fw')

                        if not firmware_version:
                            _LOGGER.error("Firmware version not found in API response: %s", data)
                            errors["base"] = "firmware_not_found"
                            raise ValueError("Firmware version not found in API response.")

            except aiohttp.ClientError as err:
                _LOGGER.error("Error connecting to API: %s", err)
                errors["base"] = "cannot_connect"
            except ValueError as err:
                _LOGGER.error("Invalid response received: %s", err)
                errors["base"] = "invalid_response"
            except Exception as err:
                _LOGGER.error("Unexpected exception: %s", err)
                errors["base"] = "unknown"
            else:
                # Input is valid, create the config entry with the custom device name
                user_input[CONF_DEVICE_NAME] = device_name
                return self.async_create_entry(title=device_name, data=user_input)

        # Show the configuration form with errors (if any)
        data_schema = vol.Schema({
            vol.Required(CONF_API_URL, default="http://192.168.178.55/getReadings?ALL"): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=10): int,
            vol.Optional(CONF_USE_SSL, default=False): bool,
            vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

