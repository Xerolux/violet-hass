import logging

import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.selector import TextSelector

from .const import DOMAIN, CONF_API_URL, CONF_POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)


class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Violet Device."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_url = user_input[CONF_API_URL]

            # Check for duplicate entries
            await self.async_set_unique_id(api_url)
            self._abort_if_unique_id_configured()

            # Validate the API URL
            session = aiohttp_client.async_get_clientsession(self.hass)
            try:
                async with async_timeout.timeout(10):
                    async with session.get(api_url, ssl=False) as response:
                        response.raise_for_status()
                        await response.json()
            except aiohttp.ClientError as err:
                _LOGGER.error("Error connecting to API: %s", err)
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.error("Unexpected exception: %s", err)
                errors["base"] = "unknown"
            else:
                # Input is valid, create the config entry
                return self.async_create_entry(title="Violet Device", data=user_input)

        # Show the configuration form with errors (if any)
        data_schema = vol.Schema({
            vol.Required(CONF_API_URL, default="http://192.168.178.55/getReadings?ALL"): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=10): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

