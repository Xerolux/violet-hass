import logging
import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
import re  # For firmware version validation
import asyncio
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
    API_READINGS,
)

# Define timeout limits as constants
MIN_TIMEOUT_DURATION = 5
MAX_TIMEOUT_DURATION = 60
MIN_RETRY_ATTEMPTS = 1  # Minimum number of retry attempts
MAX_RETRY_ATTEMPTS = 10 # Maximum number of retry attempts

_LOGGER = logging.getLogger(__name__)

# Firmware version validation (using a regular expression)
def is_valid_firmware(firmware_version):
    """Validate if the firmware version is in the correct format (e.g., 1.1.4)."""
    return bool(re.match(r'^[1-9]\d*\.\d+\.\d+$', firmware_version))

async def fetch_api_data(session, api_url, auth, use_ssl, timeout_duration, retry_attempts):
    """Fetch data from the API with retry logic and exponential backoff."""
    for attempt in range(retry_attempts):
        try:
            # Use async_timeout to set a timeout for the entire request.
            async with async_timeout.timeout(timeout_duration):
                _LOGGER.debug("Attempting to connect to API at %s (SSL=%s), attempt %d/%d", api_url, use_ssl, attempt + 1, retry_attempts)

                # Make the HTTP GET request using the provided session.
                async with session.get(api_url, auth=auth, ssl=use_ssl) as response:
                    response.raise_for_status()  # Raise an exception for bad status codes.
                    data = await response.json() # Parse the JSON response.
                    _LOGGER.debug("API response received: %s", data)
                    return data

        except aiohttp.ClientConnectionError as err:
            _LOGGER.error("Connection error to API at %s: %s", api_url, str(err))
            if attempt + 1 == retry_attempts:
              raise ValueError(f"Connection error after {retry_attempts} attempts.") from err

        except aiohttp.ClientResponseError as err:
            _LOGGER.error("Invalid API response (Status code: %s): %s", err.status, str(err))
            raise ValueError("Invalid API response.") from err

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout occurred during API request.")
            if attempt + 1 == retry_attempts:
                raise ValueError("Timeout during API request after multiple attempts.")

        except Exception as err:
            _LOGGER.error("Unexpected exception: %s", str(err))
            raise ValueError("Unexpected exception.") from err  # Re-raise as ValueError for consistency

        # Exponential backoff before the next retry.
        await asyncio.sleep(2 ** attempt)

class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Violet Pool Controller."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step (user-initiated)."""
        errors = {}

        if user_input is not None:
            # Extract and prepare data from user input.
            base_ip = user_input[CONF_API_URL]
            use_ssl = user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL)
            protocol = "https" if use_ssl else "http"
            api_url = f"{protocol}://{base_ip}{API_READINGS}"  # Construct the full API URL.
            _LOGGER.debug("Constructed API URL: %s", api_url)

            device_name = user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller")
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            device_id = user_input.get(CONF_DEVICE_ID, 1)

            # Set a unique ID to prevent duplicate entries.  Crucially, include device_id.
            await self.async_set_unique_id(f"{base_ip}-{device_id}")
            self._abort_if_unique_id_configured()  # Abort if this configuration already exists.

            session = aiohttp_client.async_get_clientsession(self.hass)

            # Validate and sanitize timeout and retry attempts
            timeout_duration = user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
            timeout_duration = max(MIN_TIMEOUT_DURATION, min(timeout_duration, MAX_TIMEOUT_DURATION))
            retry_attempts = user_input.get("retry_attempts", 3)  # Get retry_attempts from user input
            retry_attempts = max(MIN_RETRY_ATTEMPTS, min(retry_attempts, MAX_RETRY_ATTEMPTS)) # Ensure within limits

            auth = aiohttp.BasicAuth(username, password) if username and password else None

            try:
                # Attempt to fetch data from the API to validate the connection.
                data = await fetch_api_data(session, api_url, auth, use_ssl, timeout_duration, retry_attempts)

                # Process and validate the firmware version from the API response.
                await self._process_firmware_data(data, errors)


            except ValueError as err:
                _LOGGER.error("%s", str(err))
                errors["base"] = str(err)  # Set a user-friendly error message.

            if not errors:
                # If no errors, create the config entry.
                user_input[CONF_API_URL] = base_ip  # Store the base IP.
                user_input[CONF_DEVICE_NAME] = device_name
                user_input[CONF_USERNAME] = username
                user_input[CONF_PASSWORD] = password
                user_input[CONF_DEVICE_ID] = device_id

                return self.async_create_entry(
                    title=f"{device_name} (ID {device_id})", data=user_input
                )

        # Define the data schema for the user input form.
        data_schema = vol.Schema({
            vol.Required(CONF_API_URL): str,  # IP Address is required.
            vol.Optional(CONF_USERNAME): str,  # Username is optional
            vol.Optional(CONF_PASSWORD): str,  # Password is optional
            vol.Optional(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),  # Polling interval with limits.
            vol.Optional(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool, # Use SSL is optional
            vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str, # Device name is optional
            vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),  # Device ID (at least 1).
            vol.Optional("retry_attempts", default=3): vol.All(vol.Coerce(int), vol.Range(min=MIN_RETRY_ATTEMPTS, max=MAX_RETRY_ATTEMPTS)),  # Retry attempts
        })

        # Show the form to the user.
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,  # Pass any errors to the form.
        )

    async def _process_firmware_data(self, data, errors):
        """Process firmware data and validate."""
        firmware_version = data.get('fw') or data.get('SW_VERSION') # Get Firmware

        if not firmware_version:
            _LOGGER.error("Firmware version not found in API response: %s", data)
            errors["base"] = "Firmware version not found.  Please check your device configuration."
            raise ValueError("Firmware version not found.")
        elif not is_valid_firmware(firmware_version):
            _LOGGER.error("Invalid firmware version received: %s", firmware_version)
            errors["base"] = "Invalid firmware version format. Please update your device firmware."
            raise ValueError("Invalid firmware version format.")
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
        return await self.async_step_user()  # Options flow is the same as initial setup

    async def async_step_user(self, user_input=None):
        """Handle options for the Violet device."""
        if user_input is not None:
            # Update existing entry with new options
            self.hass.config_entries.async_update_entry(self.config_entry, data={**self.config_entry.data, **user_input})
            return self.async_create_entry(title="", data=user_input)

        # Define the options schema, pre-filling with existing values.
        options_schema = vol.Schema({
            vol.Optional(CONF_USERNAME, default=self.config_entry.data.get(CONF_USERNAME, "")): str,
            vol.Optional(CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD, "")): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=self.config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
            vol.Optional(CONF_USE_SSL, default=self.config_entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL)): bool,
            vol.Optional("retry_attempts", default=self.config_entry.data.get("retry_attempts", 3)): vol.All(vol.Coerce(int), vol.Range(min=MIN_RETRY_ATTEMPTS, max=MAX_RETRY_ATTEMPTS)),  # Retry attempts
        })

        return self.async_show_form(step_id="user", data_schema=options_schema)
