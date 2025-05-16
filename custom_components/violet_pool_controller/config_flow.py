"""Config Flow for Violet Pool Controller integration."""
import logging
import re
import asyncio
import ipaddress
from typing import Dict, Optional, Union, Any, List

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.typing import ConfigType
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    API_READINGS,
    CONF_API_URL,
    CONF_USE_SSL,
    CONF_DEVICE_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_ID,
    CONF_POLLING_INTERVAL,
    CONF_TIMEOUT_DURATION,
    CONF_RETRY_ATTEMPTS,
    CONF_ACTIVE_FEATURES,
    DEFAULT_USE_SSL,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS,
)

_LOGGER = logging.getLogger(__name__)

# Neue Konfigurationsschlüssel
CONF_POOL_SIZE = "pool_size"  # in m³
CONF_POOL_TYPE = "pool_type"
CONF_DISINFECTION_METHOD = "disinfection_method"

# Standardwerte
DEFAULT_POOL_SIZE = 50  # m³
DEFAULT_POOL_TYPE = "outdoor"
DEFAULT_DISINFECTION_METHOD = "chlorine"

# Optionen für Pool-Typen und Desinfektionsmethoden
POOL_TYPES = ["outdoor", "indoor", "whirlpool", "natural", "combination"]
DISINFECTION_METHODS = ["chlorine", "salt", "bromine", "active_oxygen", "uv", "ozone"]

# Verfügbare Features
AVAILABLE_FEATURES = [
    {"id": "heating", "name": "Heizung", "default": True, "platforms": ["climate"]},
    {"id": "solar", "name": "Solarabsorber", "default": True, "platforms": ["climate"]},
    {"id": "ph_control", "name": "pH-Kontrolle", "default": True, "platforms": ["number", "sensor"]},
    {"id": "chlorine_control", "name": "Chlor-Kontrolle", "default": True, "platforms": ["number", "sensor"]},
    {"id": "cover_control", "name": "Abdeckungssteuerung", "default": True, "platforms": ["cover"]},
    {"id": "backwash", "name": "Rückspülung", "default": True, "platforms": ["switch"]},
    {"id": "pv_surplus", "name": "PV-Überschuss", "default": True, "platforms": ["switch"]},
    {"id": "water_level", "name": "Wasserstand", "default": False, "platforms": ["sensor", "switch"]},
    {"id": "water_refill", "name": "Wassernachfüllung", "default": False, "platforms": ["switch"]},
    {"id": "led_lighting", "name": "LED-Beleuchtung", "default": True, "platforms": ["switch"]},
]

# Regex für Firmware-Versionen
FIRMWARE_REGEX = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:[0-9A-Za-z-_]+)(?:\.[0-9A-Za-z-_]+)*))?(?:\+((?:[0-9A-Za-z-_]+)(?:\.[0-9A-Za-z-_]+)*))?"

def validate_ip_address(ip: str) -> bool:
    """Validierung der IP-Adresse."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

async def fetch_api_data(
    session: aiohttp.ClientSession,
    api_url: str,
    auth: Optional[aiohttp.BasicAuth],
    use_ssl: bool,
    timeout_duration: int,
    retry_attempts: int,
) -> Dict[str, Any]:
    """API-Daten mit Retry-Logik abrufen."""
    for attempt in range(retry_attempts):
        try:
            async with async_timeout.timeout(timeout_duration):
                async with session.get(api_url, auth=auth, ssl=use_ssl) as response:
                    if response.status >= 400:
                        raise ValueError(f"HTTP-Fehler {response.status}: {response.reason}")
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("API-Fehler: %s (Versuch %d/%d)", err, attempt + 1, retry_attempts)
            if attempt + 1 == retry_attempts:
                raise ValueError(f"API-Anfrage fehlgeschlagen: {str(err)}")
        await asyncio.sleep(2 ** attempt)
    raise ValueError("Fehler nach allen Versuchen.")

class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Violet Pool Controller."""
    VERSION = 1

    def __init__(self):
        self._config_data = {}
        self._api_data = None

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Schritt 1: Grundkonfiguration."""
        errors = {}

        if user_input is not None:
            if not validate_ip_address(user_input[CONF_API_URL]):
                errors[CONF_API_URL] = "Ungültige IP-Adresse"
            else:
                self._config_data = {
                    CONF_API_URL: user_input[CONF_API_URL],
                    CONF_USE_SSL: user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL),
                    CONF_DEVICE_NAME: user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
                    CONF_USERNAME: user_input.get(CONF_USERNAME),
                    CONF_PASSWORD: user_input.get(CONF_PASSWORD),
                    CONF_DEVICE_ID: int(user_input.get(CONF_DEVICE_ID, 1)),
                    CONF_POLLING_INTERVAL: int(user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)),
                    CONF_TIMEOUT_DURATION: int(user_input.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)),
                    CONF_RETRY_ATTEMPTS: int(user_input.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)),
                }

                protocol = "https" if self._config_data[CONF_USE_SSL] else "http"
                api_url = f"{protocol}://{self._config_data[CONF_API_URL]}{API_READINGS}?ALL"
                await self.async_set_unique_id(f"{self._config_data[CONF_API_URL]}-{self._config_data[CONF_DEVICE_ID]}")
                self._abort_if_unique_id_configured()

                try:
                    session = aiohttp_client.async_get_clientsession(self.hass)
                    auth = aiohttp.BasicAuth(self._config_data[CONF_USERNAME], self._config_data[CONF_PASSWORD]) if self._config_data[CONF_USERNAME] else None
                    self._api_data = await fetch_api_data(
                        session, api_url, auth, self._config_data[CONF_USE_SSL],
                        self._config_data[CONF_TIMEOUT_DURATION], self._config_data[CONF_RETRY_ATTEMPTS]
                    )
                    return await self.async_step_pool_setup()
                except ValueError as err:
                    errors["base"] = str(err)

        data_schema = vol.Schema({
            vol.Required(CONF_API_URL, default="192.168.1.100"): str,
            vol.Optional(CONF_USERNAME): str,
            vol.Optional(CONF_PASSWORD): str,
            vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
            vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
            vol.Required(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
            vol.Required(CONF_TIMEOUT_DURATION, default=DEFAULT_TIMEOUT_DURATION): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            vol.Required(CONF_RETRY_ATTEMPTS, default=DEFAULT_RETRY_ATTEMPTS): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_pool_setup(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Schritt 2: Pool-spezifische Einstellungen."""
        errors = {}

        if user_input is not None:
            try:
                pool_size = float(user_input[CONF_POOL_SIZE])
                if pool_size <= 0 or pool_size > 1000:
                    errors[CONF_POOL_SIZE] = "Poolgröße muss zwischen 0.1 und 1000 m³ liegen."
                else:
                    self._config_data.update({
                        CONF_POOL_SIZE: pool_size,
                        CONF_POOL_TYPE: user_input[CONF_POOL_TYPE],
                        CONF_DISINFECTION_METHOD: user_input[CONF_DISINFECTION_METHOD],
                    })
                    return await self.async_step_feature_selection()
            except ValueError:
                errors[CONF_POOL_SIZE] = "Ungültige Poolgröße"

        data_schema = vol.Schema({
            vol.Required(CONF_POOL_SIZE, default=DEFAULT_POOL_SIZE): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000)),
            vol.Required(CONF_POOL_TYPE, default=DEFAULT_POOL_TYPE): vol.In(POOL_TYPES),
            vol.Required(CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD): vol.In(DISINFECTION_METHODS),
        })

        return self.async_show_form(step_id="pool_setup", data_schema=data_schema, errors=errors)

    async def async_step_feature_selection(self, user_input: Optional[Dict[str, bool]] = None) -> config_entries.FlowResult:
        """Schritt 3: Feature-Auswahl."""
        errors = {}

        if user_input is not None:
            active_features = [f["id"] for f in AVAILABLE_FEATURES if user_input.get(f["id"], f["default"])]
            self._config_data[CONF_ACTIVE_FEATURES] = active_features
            return self.async_create_entry(
                title=f"{self._config_data[CONF_DEVICE_NAME]} (ID {self._config_data[CONF_DEVICE_ID]})",
                data=self._config_data,
            )

        schema_dict = {vol.Required(f["id"], default=f["default"]): bool for f in AVAILABLE_FEATURES}
        data_schema = vol.Schema(schema_dict)

        return self.async_show_form(step_id="feature_selection", data_schema=data_schema, errors=errors)
