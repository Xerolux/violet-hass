import logging
import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_POLLING_INTERVAL,
    CONF_USE_SSL,
    CONF_DEVICE_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_ID,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_USE_SSL,
    API_READINGS,  # API endpoint
)

_LOGGER = logging.getLogger(__name__)

class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Violet Pool Controller."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            base_ip = user_input[CONF_API_URL]  # Only the IP address is entered
            use_ssl = user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL)
            protocol = "https" if use_ssl else "http"

            # Dynamically create the full API URL with the endpoint
            api_url = f"{protocol}://{base_ip}{API_READINGS}"
            _LOGGER.debug("Constructed API URL: %s", api_url)

            device_name = user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller")
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            device_id = user_input.get(CONF_DEVICE_ID, 1)

            await self.async_set_unique_id(base_ip)  # Only the IP address is used
            self._abort_if_unique_id_configured()

            session = aiohttp_client.async_get_clientsession(self.hass)
            try:
                async with async_timeout.timeout(10):
                    auth = aiohttp.BasicAuth(username, password)
                    _LOGGER.debug(
                        "Versuche, eine Verbindung zur API bei %s herzustellen (SSL=%s)",
                        api_url,
                        use_ssl,
                    )

                    async with session.get(api_url, auth=auth, ssl=use_ssl) as response:
                        response.raise_for_status()
                        data = await response.json()

                        _LOGGER.debug("API-Antwort empfangen: %s", data)

                        firmware_version = data.get('fw')
                        if not firmware_version:
                            _LOGGER.error(
                                "Firmware-Version in der API-Antwort nicht gefunden: %s", data
                            )
                            errors["base"] = "firmware_not_found"
                            raise ValueError("Firmware-Version nicht gefunden.")

            except aiohttp.ClientError as err:
                _LOGGER.error("Fehler beim Verbinden mit der API bei %s: %s", api_url, err)
                errors["base"] = "cannot_connect"
            except ValueError as err:
                _LOGGER.error("Ungültige Antwort erhalten: %s", err)
                errors["base"] = "invalid_response"
            except Exception as err:
                _LOGGER.error("Unerwartete Ausnahme: %s", err)
                errors["base"] = "unknown"
            else:
                # Save only the IP address in `CONF_API_URL`
                user_input[CONF_API_URL] = base_ip
                user_input[CONF_DEVICE_NAME] = device_name
                user_input[CONF_USERNAME] = username
                user_input[CONF_PASSWORD] = password
                user_input[CONF_DEVICE_ID] = device_id
                return self.async_create_entry(
                    title=f"{device_name} (ID {device_id})", data=user_input
                )

        data_schema = vol.Schema({
            vol.Required(CONF_API_URL): str,  # Only IP address
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): int,
            vol.Optional(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
            vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str,
            vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for the Violet device."""
        return VioletOptionsFlow(config_entry)

class VioletOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Violet Device."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options for the custom component."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle options for the Violet device."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Optional(
                CONF_USERNAME,
                default=self.config_entry.data.get(CONF_USERNAME, "")
            ): str,
            vol.Optional(
                CONF_PASSWORD,
                default=self.config_entry.data.get(CONF_PASSWORD, "")
            ): str,
            vol.Optional(
                CONF_POLLING_INTERVAL,
                default=self.config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
            ): int,
            vol.Optional(
                CONF_USE_SSL,
                default=self.config_entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL)
            ): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=options_schema
        )
