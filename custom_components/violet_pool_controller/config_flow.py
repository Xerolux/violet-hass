import logging
import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
import re  # Für die Validierung der Firmware-Version
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

# Timeout-Limits als Konstanten definieren
MIN_TIMEOUT_DURATION = 5
MAX_TIMEOUT_DURATION = 60

_LOGGER = logging.getLogger(__name__)

# Validierung der Firmware-Version
def is_valid_firmware(firmware_version):
    """Validiere, ob die Firmware-Version im richtigen Format vorliegt (z.B. 1.1.4)."""
    return bool(re.match(r'^[1-9]\d*\.\d+\.\d+$', firmware_version))

async def fetch_api_data(session, api_url, auth, use_ssl, timeout_duration, retry_attempts):
    """Fetch data from the API with retry logic."""
    for attempt in range(retry_attempts):
        try:
            async with async_timeout.timeout(timeout_duration):
                _LOGGER.debug(
                    "Versuche, eine Verbindung zur API bei %s herzustellen (SSL=%s)",
                    api_url,
                    use_ssl,
                )
                async with session.get(api_url, auth=auth, ssl=use_ssl) as response:
                    response.raise_for_status()
                    data = await response.json()
                    _LOGGER.debug("API-Antwort empfangen: %s", data)
                    return data
        except aiohttp.ClientConnectionError as err:
            _LOGGER.error("Verbindungsfehler zur API bei %s: %s", api_url, err)
            if attempt + 1 == retry_attempts:
                raise ValueError("Verbindungsfehler nach mehreren Versuchen.")
        except aiohttp.ClientResponseError as err:
            _LOGGER.error("Fehlerhafte API-Antwort erhalten (Statuscode: %s): %s", err.status, err.message)
            raise ValueError("Fehlerhafte API-Antwort.")
        except asyncio.TimeoutError:
            _LOGGER.error("Zeitüberschreitung bei der API-Anfrage.")
            raise ValueError("Zeitüberschreitung bei der API-Anfrage.")
        except Exception as err:
            _LOGGER.error("Unerwartete Ausnahme: %s", err)
            raise ValueError("Unerwartete Ausnahme.")

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

            # Dynamisch erstellte vollständige API-URL
            api_url = f"{protocol}://{base_ip}{API_READINGS}"
            _LOGGER.debug("Constructed API URL: %s", api_url)

            device_name = user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller")
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            device_id = user_input.get(CONF_DEVICE_ID, 1)

            await self.async_set_unique_id(base_ip)  # Use the base IP as the unique ID
            self._abort_if_unique_id_configured()

            session = aiohttp_client.async_get_clientsession(self.hass)

            # Timeout-Dauer dynamisch anpassen
            timeout_duration = user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
            timeout_duration = max(MIN_TIMEOUT_DURATION, min(timeout_duration, MAX_TIMEOUT_DURATION))

            retry_attempts = 3  # Wiederholungsversuche bei Verbindungsfehlern
            auth = aiohttp.BasicAuth(username, password)

            try:
                data = await fetch_api_data(session, api_url, auth, use_ssl, timeout_duration, retry_attempts)

                await self._process_firmware_data(data, errors)

            except ValueError as err:
                _LOGGER.error("%s", err)

            if not errors:
                # Nur die IP-Adresse speichern, um unnötige Daten zu vermeiden
                user_input[CONF_API_URL] = base_ip
                user_input[CONF_DEVICE_NAME] = device_name
                user_input[CONF_USERNAME] = username
                user_input[CONF_PASSWORD] = password
                user_input[CONF_DEVICE_ID] = device_id

                # Erfolgreiche Konfiguration
                return self.async_create_entry(
                    title=f"{device_name} (ID {device_id})", data=user_input
                )

        # Formular für den Benutzer anzeigen
        data_schema = vol.Schema({
            vol.Required(CONF_API_URL): str,  # Nur die IP-Adresse wird eingegeben
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
            vol.Optional(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
            vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str,
            vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _process_firmware_data(self, data, errors):
        """Process firmware data and validate."""
        # Firmware-Version aus 'fw' oder 'SW_VERSION' auslesen
        firmware_version = data.get('fw') or data.get('SW_VERSION')

        # Zusätzlich die Daten von 'SW_VERSION_CARRIER', 'HW_VERSION_CARRIER', 'HW_SERIAL_CARRIER' auslesen
        sw_version_carrier = data.get('SW_VERSION_CARRIER')
        hw_version_carrier = data.get('HW_VERSION_CARRIER')
        hw_serial_carrier = data.get('HW_SERIAL_CARRIER')

        if not firmware_version:
            _LOGGER.error("Firmware-Version in der API-Antwort nicht gefunden: %s", data)
            errors["base"] = "firmware_not_found"
            raise ValueError("Firmware-Version nicht gefunden.")
        else:
            # Optional: Validierung des Firmware-Formats
            if is_valid_firmware(firmware_version):
                _LOGGER.info("Firmware-Version erfolgreich ausgelesen: %s", firmware_version)
            else:
                _LOGGER.error("Ungültige Firmware-Version erhalten: %s", firmware_version)
                errors["base"] = "invalid_firmware"

        # Zusätzliche Informationen zu SW_VERSION_CARRIER, HW_VERSION_CARRIER und HW_SERIAL_CARRIER anzeigen
        _LOGGER.info("Carrier Software-Version (SW_VERSION_CARRIER): %s", sw_version_carrier or "Nicht verfügbar")
        _LOGGER.info("Carrier Hardware-Version (HW_VERSION_CARRIER): %s", hw_version_carrier or "Nicht verfügbar")
        _LOGGER.info("Carrier Hardware-Seriennummer (HW_SERIAL_CARRIER): %s", hw_serial_carrier or "Nicht verfügbar")

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
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
            vol.Optional(
                CONF_USE_SSL,
                default=self.config_entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL)
            ): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=options_schema
        )
