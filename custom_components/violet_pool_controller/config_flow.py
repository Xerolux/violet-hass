import logging
import aiohttp
import asyncio  # Import asyncio
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
import re  # For firmware version validation
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

# Define timeout limits as constants
MIN_TIMEOUT_DURATION = 5
MAX_TIMEOUT_DURATION = 60

_LOGGER = logging.getLogger(__name__)

# Firmware version validation
def is_valid_firmware(firmware_version):
    """Validate if the firmware version is in the correct format (e.g., 1.1.4)."""
    # Use a regular expression to check if the firmware version matches the expected format
    return bool(re.match(r'^[1-9]\d*\.\d+\.\d+$', firmware_version))

async def fetch_api_data(session, api_url, auth, use_ssl, timeout_duration, retry_attempts):
    """Fetch data from the API with retry logic and exponential backoff."""
    for attempt in range(retry_attempts):
        try:
            # Use aiohttp.ClientTimeout for better integration
            timeout = aiohttp.ClientTimeout(total=timeout_duration)
            _LOGGER.debug("Attempting to connect to API at %s (SSL=%s), attempt %d/%d", api_url, use_ssl, attempt + 1, retry_attempts)

            # Make an HTTP GET request to the API
            async with session.get(api_url, auth=auth, ssl=use_ssl, timeout=timeout) as response:
                # Raise an exception if the response status is not 200 OK
                response.raise_for_status()
                # Parse the JSON response
                data = await response.json()
                _LOGGER.debug("API response received: %s", data)
                return data
        except aiohttp.ClientConnectionError as err:
            _LOGGER.error("Connection error to API at %s: %s", api_url, err)
            if attempt + 1 == retry_attempts:
                raise ValueError("Connection error after multiple attempts.") from err  # Include original exception
        except aiohttp.ClientResponseError as err:
            _LOGGER.error("Invalid API response (Status code: %s): %s", err.status, str(err))
            raise ValueError("Invalid API response.") from err
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout occurred during API request.")
            if attempt + 1 == retry_attempts:
                raise ValueError("Timeout during API request.") from err
        except Exception as err:
            _LOGGER.error("Unexpected exception: %s", err)
            raise ValueError("Unexpected exception.") from err

        # Exponential backoff before retrying
        await asyncio.sleep(2 ** attempt)

class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Violet Pool Controller."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Extract the base IP address provided by the user
            base_ip = user_input[CONF_API_URL]  # Corrected: Get full URL later
            use_ssl = user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL)
            protocol = "https" if use_ssl else "http"

            # Construct the complete API URL
            api_url = f"{protocol}://{base_ip}{API_READINGS}"
            _LOGGER.debug("Constructed API URL: %s", api_url)

            device_name = user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller")
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            device_id = user_input.get(CONF_DEVICE_ID, 1)

            await self.async_set_unique_id(f"{base_ip}-{device_id}")
            self._abort_if_unique_id_configured()

            session = aiohttp_client.async_get_clientsession(self.hass)
            timeout_duration = user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
            timeout_duration = max(MIN_TIMEOUT_DURATION, min(timeout_duration, MAX_TIMEOUT_DURATION))
            retry_attempts = user_input.get("retry_attempts", 3)
            auth = aiohttp.BasicAuth(username, password)

            try:
                data = await fetch_api_data(session, api_url, auth, use_ssl, timeout_duration, retry_attempts)
                await self._process_firmware_data(data, errors)

            except ValueError as err:
                _LOGGER.error("%s", err)
                errors["base"] = str(err)

            if not errors:
                # Store the *full* API URL
                user_input[CONF_API_URL] = api_url
                user_input[CONF_DEVICE_NAME] = device_name  # No change needed here
                user_input[CONF_USERNAME] = username       # No change needed here
                user_input[CONF_PASSWORD] = password       # No change needed here
                user_input[CONF_DEVICE_ID] = device_id       # No change needed here

                return self.async_create_entry(
                    title=f"{device_name} (ID {device_id})", data=user_input
                )

        data_schema = vol.Schema({
            vol.Required(CONF_API_URL): str,  # Expecting only the IP or hostname here
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
            vol.Optional(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
            vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str,
            vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
            vol.Optional("retry_attempts", default=3): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _process_firmware_data(self, data, errors):
        """Process firmware data and validate."""
        firmware_version = data.get('fw') or data.get('SW_VERSION')

        if not firmware_version:
            _LOGGER.error("Firmware version not found in API response: %s", data)
            errors["base"] = "Firmware version not found. Please check your device configuration."
            raise ValueError("Firmware version not found.")
        elif not is_valid_firmware(firmware_version):
            _LOGGER.error("Invalid firmware version received: %s", firmware_version)
            errors["base"] = "Invalid firmware version format. Please update your device firmware."
        else:
            _LOGGER.info("Firmware version successfully retrieved: %s", firmware_version)

        # Additional logging for carrier and hardware versions
        _LOGGER.info("Carrier Software Version: %s", data.get('SW_VERSION_CARRIER', 'Not available'))
        _LOGGER.info("Carrier Hardware Version: %s", data.get('HW_VERSION_CARRIER', 'Not available'))
        _LOGGER.info("Carrier Hardware Serial Number: %s", data.get('HW_SERIAL_CARRIER', 'Not available'))

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
            # Create a new entry for the provided options
            return self.async_create_entry(title="Violet Device Options", data=user_input)

        options_schema = vol.Schema({
            vol.Optional(CONF_USERNAME, default=self.config_entry.options.get(CONF_USERNAME, "")): str,
            vol.Optional(CONF_PASSWORD, default=self.config_entry.options.get(CONF_PASSWORD, "")): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=self.config_entry.options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
            vol.Optional(CONF_USE_SSL, default=self.config_entry.options.get(CONF_USE_SSL, DEFAULT_USE_SSL)): bool,
            vol.Optional("retry_attempts", default=self.config_entry.options.get("retry_attempts", 3)): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
        })

        return self.async_show_form(step_id="user", data_schema=options_schema)
