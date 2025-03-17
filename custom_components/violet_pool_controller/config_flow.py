import logging
import re
import asyncio

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_USE_SSL,
    CONF_DEVICE_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_ID,
    API_READINGS,
)

_LOGGER = logging.getLogger(__name__)

# Neue Konstanten für Polling, Timeout, Retry
CONF_POLLING_INTERVAL = "polling_interval"
CONF_TIMEOUT_DURATION = "timeout_duration"
CONF_RETRY_ATTEMPTS = "retry_attempts"

DEFAULT_POLLING_INTERVAL = 60  # z.B. alle 60 Sekunden aktualisieren
DEFAULT_TIMEOUT_DURATION = 10   # z.B. 10 Sekunden Request-Timeout
DEFAULT_RETRY_ATTEMPTS = 3      # z.B. 3 Versuche beim Abrufen

# Regex für Firmware-Versionen: Erlaubt 3 oder 4 Segmente, z.B. 0.9.1 oder 0.9.1.2, 1.2.3, 1.2.3.4
FIRMWARE_REGEX = r"^\d+(\.\d+){2,3}$"

def is_valid_firmware(firmware_version: str) -> bool:
    """Validiere, ob die Firmware-Version 0.X.Y oder 0.X.Y.Z usw. sein kann."""
    return bool(re.match(FIRMWARE_REGEX, firmware_version))

async def fetch_api_data(
    session: aiohttp.ClientSession,
    api_url: str,
    auth: aiohttp.BasicAuth | None,
    use_ssl: bool,
    timeout_duration: int,
    retry_attempts: int,
) -> dict:
    """
    Hole Daten von der API mit Retry-Logik und exponentiellem Backoff.
    Separates Timeout und Retry – unabhängig vom Polling-Intervall.
    """
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

        except (
            aiohttp.ClientConnectionError,
            aiohttp.ClientResponseError,
            asyncio.TimeoutError,
        ) as err:
            _LOGGER.error("API-Fehler: %s (Versuch %d/%d)", err, attempt + 1, retry_attempts)
            if attempt + 1 == retry_attempts:
                raise ValueError(
                    f"API-Anfrage nach {retry_attempts} Versuchen fehlgeschlagen."
                ) from err

        # Exponentielles Backoff: Warte 2^attempt Sekunden
        await asyncio.sleep(2**attempt)

    raise ValueError("Fehler beim Abrufen der API-Daten nach allen Versuchen.")


class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für den Violet Pool Controller."""
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Erster Schritt (benutzerinitiierte Eingabe) für das Setup."""
        errors = {}

        if user_input is not None:
            # Konfigurationsdaten aus dem Formular übernehmen
            config_data = {
                # IP-Adresse / Host des Geräts
                "base_ip": user_input[CONF_API_URL],
                "use_ssl": user_input.get(CONF_USE_SSL, True),
                "device_name": user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
                "username": user_input.get(CONF_USERNAME),
                "password": user_input.get(CONF_PASSWORD),
                "device_id": user_input.get(CONF_DEVICE_ID, 1),

                # Hier nun separat Polling-Interval, Timeout und Retry
                "polling_interval": int(user_input[CONF_POLLING_INTERVAL]),
                "timeout_duration": int(user_input[CONF_TIMEOUT_DURATION]),
                "retry_attempts": int(user_input[CONF_RETRY_ATTEMPTS]),
            }

            # Protokoll-URL zusammenbauen
            protocol = "https" if config_data["use_ssl"] else "http"
            api_url = f"{protocol}://{config_data['base_ip']}{API_READINGS}"

            # Eindeutige ID: combination aus IP und device_id
            await self.async_set_unique_id(f"{config_data['base_ip']}-{config_data['device_id']}")
            self._abort_if_unique_id_configured()

            # Versuche Daten von der API zu holen
            session = aiohttp_client.async_get_clientsession(self.hass)
            auth = None
            if config_data["username"]:
                auth = aiohttp.BasicAuth(config_data["username"], config_data["password"] or "")

            try:
                data = await fetch_api_data(
                    session=session,
                    api_url=api_url,
                    auth=auth,
                    use_ssl=config_data["use_ssl"],
                    timeout_duration=config_data["timeout_duration"],
                    retry_attempts=config_data["retry_attempts"],
                )

                await self._process_firmware_data(data, errors)

            except ValueError as err:
                _LOGGER.error("Fehler beim Abrufen/Verarbeiten der Daten: %s", err)
                errors["base"] = str(err)

            if not errors:
                # Wenn alles okay ist, Integration anlegen
                return self.async_create_entry(
                    title=f"{config_data['device_name']} (ID {config_data['device_id']})",
                    data=config_data,
                )

        # Hier definieren wir das Formular-Schema
        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_URL, default="192.168.1.100"): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
                vol.Required(CONF_USE_SSL, default=True): bool,
                vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),

                # Polling, Timeout und Retry separat
                vol.Required(CONF_POLLING_INTERVAL, default=str(DEFAULT_POLLING_INTERVAL)): str,
                vol.Required(CONF_TIMEOUT_DURATION, default=str(DEFAULT_TIMEOUT_DURATION)): str,
                vol.Required(CONF_RETRY_ATTEMPTS, default=str(DEFAULT_RETRY_ATTEMPTS)): str,

                vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def _process_firmware_data(self, data: dict, errors: dict) -> None:
        """Prüft die Firmware-Version in den API-Daten und fügt ggf. Fehler hinzu."""
        firmware_version = data.get("fw")

        if not firmware_version:
            errors["base"] = "Firmware-Daten fehlen in der API-Antwort."
            return

        if not is_valid_firmware(firmware_version):
            errors["base"] = f"Ungültige Firmware-Version: {firmware_version}"

    async def async_get_options_flow(self, config_entry: config_entries.ConfigEntry):
        """Erzeugt den OptionsFlow, damit man später Parameter ändern kann."""
        return VioletOptionsFlowHandler(config_entry)


class VioletOptionsFlowHandler(config_entries.OptionsFlow):
    """OptionsFlow, um nachträglich Polling, Timeout, Retry, etc. einzustellen."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Speichere das ConfigEntry."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Erster Options-Schritt."""
        if user_input is not None:
            # Speichere die neuen Options
            return self.async_create_entry(title="", data=user_input)

        # Bestehende Werte aus config_entry (oder defaults)
        current_options = dict(self.config_entry.options)
        polling = str(current_options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))
        timeout = str(current_options.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION))
        retries = str(current_options.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS))

        options_schema = vol.Schema(
            {
                vol.Required(CONF_POLLING_INTERVAL, default=polling): str,
                vol.Required(CONF_TIMEOUT_DURATION, default=timeout): str,
                vol.Required(CONF_RETRY_ATTEMPTS, default=retries): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=options_schema)
