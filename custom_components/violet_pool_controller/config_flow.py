import logging
import aiohttp
import async_timeout
import voluptuous as vol
import re
import asyncio

from homeassistant import config_entries
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.typing import ConfigType
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

# Timeout- und Retry-Konstanten
MIN_TIMEOUT_DURATION = 5
MAX_TIMEOUT_DURATION = 60
MIN_RETRY_ATTEMPTS = 1
MAX_RETRY_ATTEMPTS = 10

_LOGGER = logging.getLogger(__name__)

def is_valid_firmware(firmware_version: str) -> bool:
    """Validiere, ob die Firmware-Version im korrekten Format vorliegt (z.B. 1.1.4)."""
    return bool(re.match(r'^[1-9]\d*\.\d+\.\d+$', firmware_version))

async def fetch_api_data(
    session: aiohttp.ClientSession,
    api_url: str,
    auth: aiohttp.BasicAuth | None,
    use_ssl: bool,
    timeout_duration: int,
    retry_attempts: int,
) -> dict:
    """Hole Daten von der API mit Retry-Logik und exponentiellem Backoff."""
    for attempt in range(retry_attempts):
        try:
            async with async_timeout.timeout(timeout_duration):
                _LOGGER.debug(
                    "Versuche Verbindung zur API unter %s (SSL=%s), Versuch %d/%d",
                    api_url,
                    use_ssl,
                    attempt + 1,
                    retry_attempts,
                )
                async with session.get(api_url, auth=auth, ssl=use_ssl) as response:
                    response.raise_for_status()
                    data = await response.json()
                    _LOGGER.debug("API-Antwort erhalten: %s", data)
                    return data
        except (aiohttp.ClientConnectionError, aiohttp.ClientResponseError, asyncio.TimeoutError) as err:
            _LOGGER.error("API-Fehler: %s", err)
            if attempt + 1 == retry_attempts:
                raise ValueError(f"API-Anfrage nach {retry_attempts} Versuchen fehlgeschlagen.") from err
        await asyncio.sleep(2**attempt)
    raise ValueError("Fehler beim Abrufen der API-Daten nach allen Versuchen.")

class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für den Violet Pool Controller."""
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Ersten Schritt (benutzerinitiierte Eingabe) verarbeiten."""
        errors = {}

        if user_input is not None:
            base_ip = user_input[CONF_API_URL]
            use_ssl = user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL)
            protocol = "https" if use_ssl else "http"
            api_url = f"{protocol}://{base_ip}{API_READINGS}"

            device_name = user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller")
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            device_id = user_input.get(CONF_DEVICE_ID, 1)

            await self.async_set_unique_id(f"{base_ip}-{device_id}")
            self._abort_if_unique_id_configured()

            session = aiohttp_client.async_get_clientsession(self.hass)

            timeout_duration = int(user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))
            retry_attempts = int(user_input.get("retry_attempts", 3))

            auth = aiohttp.BasicAuth(username, password) if username and password else None

            try:
                data = await fetch_api_data(session, api_url, auth, use_ssl, timeout_duration, retry_attempts)
                await self._process_firmware_data(data, errors)
            except ValueError as err:
                _LOGGER.error("Fehler beim Abrufen oder Verarbeiten der Daten: %s", err)
                errors["base"] = str(err)

            if not errors:
                return self.async_create_entry(
                    title=f"{device_name} (ID {device_id})",
                    data={
                        CONF_API_URL: base_ip,
                        CONF_DEVICE_NAME: device_name,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_DEVICE_ID: device_id,
                        CONF_USE_SSL: use_ssl,
                        CONF_POLLING_INTERVAL: timeout_duration,
                        "retry_attempts": retry_attempts,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_URL): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
                vol.Required(CONF_POLLING_INTERVAL, default=str(DEFAULT_POLLING_INTERVAL)): str,
                vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
                vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
                vol.Required("retry_attempts", default="3"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def _process_firmware_data(self, data: dict, errors: dict) -> None:
        """Überprüft die Firmware-Version und fügt Fehler hinzu, falls ungültig."""
        firmware_version = data.get("fw")
        
        if not firmware_version:
            errors["base"] = "Firmware-Daten fehlen in der API-Antwort."
            return

        if not is_valid_firmware(firmware_version):
            errors["base"] = f"Ungültige Firmware-Version: {firmware_version}"
