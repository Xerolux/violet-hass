import logging
import aiohttp
import async_timeout
import voluptuous as vol
import re  # Für Firmware-Version-Validierung
import asyncio
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
    API_READINGS,
)

# Timeout- und Retry-Konstanten
MIN_TIMEOUT_DURATION = 5
MAX_TIMEOUT_DURATION = 60
MIN_RETRY_ATTEMPTS = 1   # Minimalzahl der Retry-Versuche
MAX_RETRY_ATTEMPTS = 10  # Maximalzahl der Retry-Versuche

_LOGGER = logging.getLogger(__name__)


def is_valid_firmware(firmware_version: str) -> bool:
    """Validiere, ob die Firmware-Version im korrekten Format vorliegt (z.B. 1.1.4)."""
    return bool(re.match(r'^[1-9]\d*\.\d+\.\d+$', firmware_version))


async def fetch_api_data(
    session: aiohttp.ClientSession,
    api_url: str,
    auth: aiohttp.BasicAuth,
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
                    response.raise_for_status()  # Exception bei fehlerhaftem Statuscode
                    data = await response.json()
                    _LOGGER.debug("API-Antwort erhalten: %s", data)
                    return data

        except aiohttp.ClientConnectionError as err:
            _LOGGER.error("Verbindungsfehler zu API unter %s: %s", api_url, err)
            if attempt + 1 == retry_attempts:
                raise ValueError(f"Verbindungsfehler nach {retry_attempts} Versuchen.") from err

        except aiohttp.ClientResponseError as err:
            _LOGGER.error("Ungültige API-Antwort (Status: %s): %s", err.status, err)
            raise ValueError("Ungültige API-Antwort.") from err

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout während der API-Anfrage.")
            if attempt + 1 == retry_attempts:
                raise ValueError("Timeout während der API-Anfrage nach mehreren Versuchen.")

        except Exception as err:
            _LOGGER.error("Unerwartete Ausnahme: %s", err)
            raise ValueError("Unerwartete Ausnahme.") from err

        # Exponentielles Backoff vor dem nächsten Versuch
        await asyncio.sleep(2 ** attempt)

    # Sollte niemals hier ankommen, aber als Fallback:
    raise ValueError("Fehler beim Abrufen der API-Daten nach allen Versuchen.")


class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für den Violet Pool Controller."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Ersten Schritt (benutzerinitiierte Eingabe) verarbeiten."""
        errors = {}

        if user_input is not None:
            base_ip = user_input[CONF_API_URL]
            use_ssl = user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL)
            protocol = "https" if use_ssl else "http"
            api_url = f"{protocol}://{base_ip}{API_READINGS}"  # Vollständige API-URL konstruieren
            _LOGGER.debug("Konstruiere API-URL: %s", api_url)

            device_name = user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller")
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            device_id = user_input.get(CONF_DEVICE_ID, 1)

            # Setze eine eindeutige ID, um Duplikate zu verhindern (inklusive device_id)
            await self.async_set_unique_id(f"{base_ip}-{device_id}")
            self._abort_if_unique_id_configured()

            session = aiohttp_client.async_get_clientsession(self.hass)

            # Timeout und Retry-Versuche validieren und einschränken
            timeout_duration = user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
            timeout_duration = max(MIN_TIMEOUT_DURATION, min(timeout_duration, MAX_TIMEOUT_DURATION))
            retry_attempts = user_input.get("retry_attempts", 3)
            retry_attempts = max(MIN_RETRY_ATTEMPTS, min(retry_attempts, MAX_RETRY_ATTEMPTS))

            auth = aiohttp.BasicAuth(username, password) if username and password else None

            try:
                data = await fetch_api_data(session, api_url, auth, use_ssl, timeout_duration, retry_attempts)
                await self._process_firmware_data(data, errors)
            except ValueError as err:
                _LOGGER.error("%s", err)
                errors["base"] = str(err)

            if not errors:
                # Speichere die ursprüngliche IP und weitere Daten in der Config
                user_input[CONF_API_URL] = base_ip
                user_input[CONF_DEVICE_NAME] = device_name
                user_input[CONF_USERNAME] = username
                user_input[CONF_PASSWORD] = password
                user_input[CONF_DEVICE_ID] = device_id

                return self.async_create_entry(
                    title=f"{device_name} (ID {device_id})", data=user_input
                )

        data_schema = vol.Schema({
            vol.Required(CONF_API_URL): str,  # IP-Adresse erforderlich
            vol.Optional(CONF_USERNAME): str,
            vol.Optional(CONF_PASSWORD): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL):
                vol.All(vol.Coerce(int), vol.Range(min=MIN_TIMEOUT_DURATION, max=MAX_TIMEOUT_DURATION)),
            vol.Optional(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
            vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str,
            vol.Required(CONF_DEVICE_ID, default=1):
                vol.All(vol.Coerce(int), vol.Range(min=1)),
            vol.Optional("retry_attempts", default=3):
                vol.All(vol.Coerce(int), vol.Range(min=MIN_RETRY_ATTEMPTS, max=MAX_RETRY_ATTEMPTS)),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _process_firmware_data(self, data: dict, errors: dict) -> None:
        """Verarbeite die Firmware-Daten und validiere sie."""
        firmware_version = data.get('fw') or data.get('SW_VERSION')
        if not firmware_version:
            _LOGGER.error("Firmware-Version nicht in API-Antwort gefunden: %s", data)
            errors["base"] = "Firmware-Version nicht gefunden. Bitte Geräte-Konfiguration prüfen."
            raise ValueError("Firmware-Version nicht gefunden.")
        elif not is_valid_firmware(firmware_version):
            _LOGGER.error("Ungültige Firmware-Version erhalten: %s", firmware_version)
            errors["base"] = "Ungültiges Firmware-Format. Bitte Firmware aktualisieren."
            raise ValueError("Ungültiges Firmware-Format.")
        else:
            _LOGGER.info("Firmware-Version erfolgreich abgerufen: %s", firmware_version)

        _LOGGER.info("Carrier Software-Version: %s", data.get('SW_VERSION_CARRIER', 'Nicht verfügbar'))
        _LOGGER.info("Carrier Hardware-Version: %s", data.get('HW_VERSION_CARRIER', 'Nicht verfügbar'))
        _LOGGER.info("Carrier Hardware-Seriennummer: %s", data.get('HW_SERIAL_CARRIER', 'Nicht verfügbar'))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Gebe den Options Flow für das Violet-Gerät zurück."""
        return VioletOptionsFlow(config_entry)


class VioletOptionsFlow(config_entries.OptionsFlow):
    """Options Flow für Violet-Gerät."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.hass.config_entries.async_update_entry(config_entry, options=config_entry.options)

    async def async_step_init(self, user_input: dict | None = None):
        """Initialer Schritt im Options Flow."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input: dict | None = None):
        """Optionen für das Violet-Gerät verwalten."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={**self.config_entry.data, **user_input}
            )
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Optional(CONF_USERNAME, default=self.config_entry.data.get(CONF_USERNAME, "")): str,
            vol.Optional(CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD, "")): str,
            vol.Optional(CONF_POLLING_INTERVAL, default=self.config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)):
                vol.All(vol.Coerce(int), vol.Range(min=MIN_TIMEOUT_DURATION, max=MAX_TIMEOUT_DURATION)),
            vol.Optional(CONF_USE_SSL, default=self.config_entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL)): bool,
            vol.Optional("retry_attempts", default=self.config_entry.data.get("retry_attempts", 3)):
                vol.All(vol.Coerce(int), vol.Range(min=MIN_RETRY_ATTEMPTS, max=MAX_RETRY_ATTEMPTS)),
        })

        return self.async_show_form(step_id="user", data_schema=options_schema)
