"""Config Flow für Violet Pool Controller - Fixed Version."""
import logging
import ipaddress
import asyncio
import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from .const import (
    DOMAIN, API_READINGS, CONF_API_URL, CONF_USE_SSL, CONF_DEVICE_NAME, CONF_USERNAME,
    CONF_PASSWORD, CONF_DEVICE_ID, CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION,
    CONF_RETRY_ATTEMPTS, CONF_ACTIVE_FEATURES, DEFAULT_USE_SSL, DEFAULT_POLLING_INTERVAL,
    DEFAULT_TIMEOUT_DURATION, DEFAULT_RETRY_ATTEMPTS, CONF_POOL_SIZE, CONF_POOL_TYPE,
    CONF_DISINFECTION_METHOD, DEFAULT_POOL_SIZE, DEFAULT_POOL_TYPE, DEFAULT_DISINFECTION_METHOD,
    POOL_TYPES, DISINFECTION_METHODS, AVAILABLE_FEATURES
)

_LOGGER = logging.getLogger(__name__)

def validate_ip_address(ip: str) -> bool:
    """Validiere IP-Adresse."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

async def fetch_api_data(
    session: aiohttp.ClientSession, api_url: str, auth: aiohttp.BasicAuth | None,
    use_ssl: bool, timeout: int, retries: int
) -> dict:
    """API-Daten mit Retry-Logik abrufen."""
    for attempt in range(retries):
        try:
            async with async_timeout.timeout(timeout):
                async with session.get(api_url, auth=auth, ssl=use_ssl) as response:
                    response.raise_for_status()
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            if attempt + 1 == retries:
                _LOGGER.error("API-Fehler nach %d Versuchen: %s", retries, err)
                raise ValueError(f"API-Anfrage fehlgeschlagen: {err}")
            await asyncio.sleep(2 ** attempt)
    raise ValueError("Fehler nach allen Versuchen")

class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Violet Pool Controller."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Options Flow zurückgeben."""
        return VioletOptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        self._config_data: dict = {}

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Schritt 1: Grundkonfiguration."""
        errors = {}
        if user_input:
            ip_address = user_input[CONF_API_URL]
            
            # Prüfung auf doppelte IP-Adressen
            for entry in self._async_current_entries():
                existing_ip = entry.data.get(CONF_API_URL) or entry.data.get("host") or entry.data.get("base_ip")
                if existing_ip == ip_address:
                    errors["base"] = "already_configured"
                    _LOGGER.warning("IP-Adresse %s bereits konfiguriert", ip_address)
                    break
            
            if not errors and not validate_ip_address(ip_address):
                errors[CONF_API_URL] = "invalid_ip_address"
            
            if not errors:
                self._config_data = {
                    CONF_API_URL: ip_address,
                    CONF_USE_SSL: user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL),
                    CONF_DEVICE_NAME: user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
                    CONF_USERNAME: user_input.get(CONF_USERNAME, ""),
                    CONF_PASSWORD: user_input.get(CONF_PASSWORD, ""),
                    CONF_DEVICE_ID: int(user_input.get(CONF_DEVICE_ID, 1)),
                    CONF_POLLING_INTERVAL: int(user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)),
                    CONF_TIMEOUT_DURATION: int(user_input.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)),
                    CONF_RETRY_ATTEMPTS: int(user_input.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)),
                }
                
                protocol = "https" if self._config_data[CONF_USE_SSL] else "http"
                api_url = f"{protocol}://{self._config_data[CONF_API_URL]}{API_READINGS}?ALL"
                
                # Unique ID setzen für Duplikats-Schutz
                await self.async_set_unique_id(f"{self._config_data[CONF_API_URL]}-{self._config_data[CONF_DEVICE_ID]}")
                self._abort_if_unique_id_configured()

                try:
                    session = aiohttp_client.async_get_clientsession(self.hass)
                    auth = aiohttp.BasicAuth(self._config_data[CONF_USERNAME], self._config_data[CONF_PASSWORD]) if self._config_data[CONF_USERNAME] else None
                    await fetch_api_data(
                        session, api_url, auth, self._config_data[CONF_USE_SSL],
                        self._config_data[CONF_TIMEOUT_DURATION], self._config_data[CONF_RETRY_ATTEMPTS]
                    )
                    return await self.async_step_pool_setup()
                except ValueError:
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_URL, default="192.168.1.100"): str,
                vol.Optional(CONF_USERNAME, default=""): str,
                vol.Optional(CONF_PASSWORD, default=""): str,
                vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
                vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
                vol.Required(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                vol.Required(CONF_TIMEOUT_DURATION, default=DEFAULT_TIMEOUT_DURATION): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                vol.Required(CONF_RETRY_ATTEMPTS, default=DEFAULT_RETRY_ATTEMPTS): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
                vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str,
            }),
            errors=errors
        )

    async def async_step_pool_setup(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Schritt 2: Pool-spezifische Einstellungen."""
        if user_input:
            self._config_data.update({
                CONF_POOL_SIZE: float(user_input[CONF_POOL_SIZE]),
                CONF_POOL_TYPE: user_input[CONF_POOL_TYPE],
                CONF_DISINFECTION_METHOD: user_input[CONF_DISINFECTION_METHOD],
            })
            return await self.async_step_feature_selection()

        return self.async_show_form(
            step_id="pool_setup",
            data_schema=vol.Schema({
                vol.Required(CONF_POOL_SIZE, default=DEFAULT_POOL_SIZE): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000)),
                vol.Required(CONF_POOL_TYPE, default=DEFAULT_POOL_TYPE): vol.In(POOL_TYPES),
                vol.Required(CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD): vol.In(DISINFECTION_METHODS),
            }),
            description_placeholders={"device_name": self._config_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")}
        )

    async def async_step_feature_selection(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Schritt 3: Feature-Auswahl."""
        if user_input:
            active_features = [f["id"] for f in AVAILABLE_FEATURES if user_input.get(f["id"], f["default"])]
            self._config_data[CONF_ACTIVE_FEATURES] = active_features
            title = f"{self._config_data.get(CONF_DEVICE_NAME, 'Violet Pool Controller')} (ID {self._config_data.get(CONF_DEVICE_ID, 1)})"
            return self.async_create_entry(title=title, data=self._config_data)

        return self.async_show_form(
            step_id="feature_selection",
            data_schema=vol.Schema({vol.Required(f["id"], default=f["default"]): bool for f in AVAILABLE_FEATURES}),
            description_placeholders={"device_name": self._config_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")}
        )

class VioletOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Violet Pool Controller options - FIXED VERSION."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialisiere Options Flow."""
        # FIXED: Verwende self._config_entry statt self.config_entry
        self._config_entry = config_entry
        self.current_config = {**config_entry.data, **config_entry.options}

    async def async_step_init(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Verwalte Optionen."""
        if user_input:
            # Feature-Checkboxen verarbeiten
            active_features = []
            for feature in AVAILABLE_FEATURES:
                checkbox_key = f"feature_{feature['id']}"
                if user_input.pop(checkbox_key, False):
                    active_features.append(feature["id"])
            
            user_input[CONF_ACTIVE_FEATURES] = active_features
            return self.async_create_entry(title="", data=user_input)

        # Schema für Optionen-Dialog
        schema_dict = {
            vol.Optional(CONF_POLLING_INTERVAL, default=self.current_config.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)): 
                vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
            vol.Optional(CONF_TIMEOUT_DURATION, default=self.current_config.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)): 
                vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            vol.Optional(CONF_RETRY_ATTEMPTS, default=self.current_config.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)): 
                vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            vol.Optional(CONF_POOL_SIZE, default=self.current_config.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)): 
                vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000)),
            vol.Optional(CONF_POOL_TYPE, default=self.current_config.get(CONF_POOL_TYPE, DEFAULT_POOL_TYPE)): 
                vol.In(POOL_TYPES),
            vol.Optional(CONF_DISINFECTION_METHOD, default=self.current_config.get(CONF_DISINFECTION_METHOD, DEFAULT_DISINFECTION_METHOD)): 
                vol.In(DISINFECTION_METHODS),
        }

        # Feature-Checkboxen hinzufügen
        current_features = self.current_config.get(CONF_ACTIVE_FEATURES, [])
        for feature in AVAILABLE_FEATURES:
            checkbox_key = f"feature_{feature['id']}"
            default_value = feature["id"] in current_features
            schema_dict[vol.Optional(checkbox_key, default=default_value)] = bool

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict)
        )