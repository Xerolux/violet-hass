"""Config Flow für Violet Pool Controller Integration - OPTIMIZED VERSION."""
import logging
import ipaddress
import asyncio
from typing import Any, Dict, List

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.data_entry_flow import FlowResult

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
    CONF_POOL_SIZE,
    CONF_POOL_TYPE,
    CONF_DISINFECTION_METHOD,
    CONF_SELECTED_SENSORS,  # Neuer Eintrag
    DEFAULT_USE_SSL,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_POOL_SIZE,
    DEFAULT_POOL_TYPE,
    DEFAULT_DISINFECTION_METHOD,
    AVAILABLE_FEATURES,
)

_LOGGER = logging.getLogger(__name__)

# Konstanten für Validierung
MIN_POLLING_INTERVAL = 10
MAX_POLLING_INTERVAL = 3600
MIN_TIMEOUT = 1
MAX_TIMEOUT = 60
MIN_RETRIES = 1
MAX_RETRIES = 10
MIN_POOL_SIZE = 0.1
MAX_POOL_SIZE = 1000.0
MIN_DEVICE_ID = 1

# Retry-Konstanten
BASE_RETRY_DELAY = 2
DEFAULT_API_TIMEOUT = 10

# Error Messages
ERROR_ALREADY_CONFIGURED = "already_configured"
ERROR_INVALID_IP = "invalid_ip_address"
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_AGREEMENT_DECLINED = "agreement_declined"

# Pool & Disinfection Options
POOL_TYPE_OPTIONS = {
    "outdoor": "🏖️ Freibad", "indoor": "🏠 Hallenbad", "whirlpool": "🛁 Whirlpool/Spa",
    "natural": "🌿 Naturpool/Schwimmteich", "combination": "🔄 Kombination",
}
DISINFECTION_OPTIONS = {
    "chlorine": "🧪 Chlor (Flüssig/Tabletten)", "salt": "🧂 Salzelektrolyse",
    "bromine": "⚗️ Brom", "active_oxygen": "💧 Aktivsauerstoff/H₂O₂",
    "uv": "💡 UV-Desinfektion", "ozone": "🌀 Ozon-Desinfektion",
}

# Features Info
ENHANCED_FEATURES = {
    "heating": {"icon": "🔥", "name": "Heizungssteuerung"},
    "solar": {"icon": "☀️", "name": "Solarabsorber"},
    "ph_control": {"icon": "🧪", "name": "pH-Automatik"},
    "chlorine_control": {"icon": "💧", "name": "Chlor-Management"},
    "cover_control": {"icon": "🪟", "name": "Abdeckungssteuerung"},
    "backwash": {"icon": "🔄", "name": "Rückspül-Automatik"},
    "pv_surplus": {"icon": "🔋", "name": "PV-Überschuss"},
    "filter_control": {"icon": "🌊", "name": "Filterpumpe"},
    "water_level": {"icon": "📏", "name": "Füllstand-Monitor"},
    "water_refill": {"icon": "🚰", "name": "Auto-Nachfüllung"},
    "led_lighting": {"icon": "💡", "name": "LED-Beleuchtung"},
    "digital_inputs": {"icon": "🔌", "name": "Digitale Eingänge"},
    "extension_outputs": {"icon": "🔗", "name": "Erweiterungsmodule"},
}


def validate_ip_address(ip: str) -> bool:
    """Validiere IP-Adresse."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


async def fetch_api_data(
    session: aiohttp.ClientSession, api_url: str, auth: aiohttp.BasicAuth | None,
    use_ssl: bool, timeout: int, retries: int,
) -> dict[str, Any]:
    """API-Daten mit Retry-Logik abrufen."""
    for attempt in range(retries):
        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            async with session.get(
                api_url, auth=auth, ssl=use_ssl, timeout=timeout_obj
            ) as response:
                response.raise_for_status()
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            if attempt + 1 == retries:
                _LOGGER.error("API-Fehler nach %d Versuchen: %s", retries, err)
                raise ValueError(f"API-Anfrage fehlgeschlagen: {err}") from err
            retry_delay = BASE_RETRY_DELAY ** attempt
            _LOGGER.warning("API-Versuch %d/%d fehlgeschlagen, wiederhole in %ds", attempt + 1, retries, retry_delay)
            await asyncio.sleep(retry_delay)
    raise ValueError("Fehler nach allen Versuchen")


class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Violet Pool Controller."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        """Initialisiere Config Flow."""
        self._config_data: dict[str, Any] = {}
        self._sensor_data: dict[str, list[str]] = {}
        _LOGGER.info("Violet Pool Controller Setup gestartet")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Options Flow zurückgeben."""
        return VioletOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Schritt 1: User-initiierter Setup-Start."""
        return await self.async_step_disclaimer()

    async def async_step_disclaimer(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """⚠️ Disclaimer und Nutzungsbedingungen."""
        if user_input and user_input.get("agreement"):
            return await self.async_step_connection()
        if user_input is not None:
            return self.async_abort(reason=ERROR_AGREEMENT_DECLINED)

        return self.async_show_form(
            step_id="disclaimer",
            data_schema=vol.Schema({vol.Required("agreement", default=False): bool}),
            description_placeholders={"disclaimer_text": self._get_disclaimer_text()},
        )

    async def async_step_connection(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """🌐 Schritt 2: Controller-Verbindung."""
        errors = {}
        if user_input:
            if self._is_duplicate_entry(user_input[CONF_API_URL]):
                errors["base"] = ERROR_ALREADY_CONFIGURED
            elif not validate_ip_address(user_input[CONF_API_URL]):
                errors[CONF_API_URL] = ERROR_INVALID_IP
            else:
                self._config_data = self._build_config_data(user_input)
                await self.async_set_unique_id(f"{self._config_data[CONF_API_URL]}-{self._config_data[CONF_DEVICE_ID]}")
                self._abort_if_unique_id_configured()
                if await self._test_connection():
                    return await self.async_step_pool_setup()
                errors["base"] = ERROR_CANNOT_CONNECT

        return self.async_show_form(
            step_id="connection", data_schema=self._get_connection_schema(), errors=errors
        )

    async def async_step_pool_setup(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """🏊 Schritt 3: Pool-Konfiguration."""
        if user_input:
            self._config_data.update({
                CONF_POOL_SIZE: float(user_input[CONF_POOL_SIZE]),
                CONF_POOL_TYPE: user_input[CONF_POOL_TYPE],
                CONF_DISINFECTION_METHOD: user_input[CONF_DISINFECTION_METHOD],
            })
            return await self.async_step_feature_selection()

        return self.async_show_form(
            step_id="pool_setup", data_schema=self._get_pool_setup_schema()
        )

    async def async_step_feature_selection(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """⚙️ Schritt 4: Feature-Auswahl."""
        if user_input:
            self._config_data[CONF_ACTIVE_FEATURES] = self._extract_active_features(user_input)
            
            # Hole Sensor-Daten für nächsten Schritt
            self._sensor_data = await self._get_grouped_sensors()
            if not self._sensor_data:
                 _LOGGER.warning("Keine dynamischen Sensoren gefunden. Überspringe Auswahl.")
                 self._config_data[CONF_SELECTED_SENSORS] = []
                 return self.async_create_entry(title=self._generate_entry_title(), data=self._config_data)
                 
            return await self.async_step_sensor_selection()

        return self.async_show_form(
            step_id="feature_selection", data_schema=self._get_feature_selection_schema()
        )
        
    async def async_step_sensor_selection(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """📊 Schritt 5: Dynamische Sensor-Auswahl."""
        if user_input:
            selected_sensors = []
            for key, value in user_input.items():
                if isinstance(value, list):
                    selected_sensors.extend(value)
            
            self._config_data[CONF_SELECTED_SENSORS] = selected_sensors
            _LOGGER.info("%d dynamische Sensoren ausgewählt", len(selected_sensors))
            
            return self.async_create_entry(title=self._generate_entry_title(), data=self._config_data)

        return self.async_show_form(
            step_id="sensor_selection",
            data_schema=self._get_sensor_selection_schema(),
            description_placeholders={
                "step_icon": "📊",
                "step_title": "Dynamische Sensoren",
                "step_description": "Wähle die Sensoren aus, die du in Home Assistant sehen möchtest."
            }
        )

    # ================= Helper Methods =================

    def _is_duplicate_entry(self, ip: str) -> bool:
        return any(entry.data.get(CONF_API_URL) == ip for entry in self._async_current_entries())

    def _build_config_data(self, ui: dict) -> dict:
        return {
            CONF_API_URL: ui[CONF_API_URL],
            CONF_USE_SSL: ui.get(CONF_USE_SSL, DEFAULT_USE_SSL),
            CONF_DEVICE_NAME: ui.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller"),
            CONF_USERNAME: ui.get(CONF_USERNAME, ""),
            CONF_PASSWORD: ui.get(CONF_PASSWORD, ""),
            CONF_DEVICE_ID: int(ui.get(CONF_DEVICE_ID, 1)),
            CONF_POLLING_INTERVAL: int(ui.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)),
            CONF_TIMEOUT_DURATION: int(ui.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)),
            CONF_RETRY_ATTEMPTS: int(ui.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)),
        }

    async def _test_connection(self) -> bool:
        try:
            protocol = "https" if self._config_data[CONF_USE_SSL] else "http"
            api_url = f"{protocol}://{self._config_data[CONF_API_URL]}{API_READINGS}?ALL"
            session = aiohttp_client.async_get_clientsession(self.hass)
            auth = aiohttp.BasicAuth(self._config_data[CONF_USERNAME], self._config_data[CONF_PASSWORD]) if self._config_data[CONF_USERNAME] else None
            await fetch_api_data(
                session, api_url, auth, self._config_data[CONF_USE_SSL],
                self._config_data[CONF_TIMEOUT_DURATION], self._config_data[CONF_RETRY_ATTEMPTS]
            )
            return True
        except ValueError:
            return False
            
    async def _get_grouped_sensors(self) -> Dict[str, List[str]]:
        """Ruft Sensoren ab und gruppiert sie."""
        try:
            protocol = "https" if self._config_data[CONF_USE_SSL] else "http"
            api_url = f"{protocol}://{self._config_data[CONF_API_URL]}{API_READINGS}?ALL"
            session = aiohttp_client.async_get_clientsession(self.hass)
            auth = aiohttp.BasicAuth(self._config_data[CONF_USERNAME], self._config_data[CONF_PASSWORD]) if self._config_data[CONF_USERNAME] else None
            
            data = await fetch_api_data(
                session, api_url, auth, self._config_data[CONF_USE_SSL],
                self._config_data[CONF_TIMEOUT_DURATION], self._config_data[CONF_RETRY_ATTEMPTS]
            )
            
            grouped: Dict[str, List[str]] = {}
            for key in sorted(data.keys()):
                # Einfache Gruppierung nach Präfix
                group = key.split('_')[0]
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(key)
            return grouped
            
        except ValueError:
            return {}

    def _extract_active_features(self, ui: dict) -> list:
        return [f['id'] for f in AVAILABLE_FEATURES if ui.get(f"enable_{f['id']}", f["default"])]

    def _generate_entry_title(self) -> str:
        name = self._config_data.get(CONF_DEVICE_NAME)
        pool_size = self._config_data.get(CONF_POOL_SIZE)
        return f"{name} • {pool_size}m³"
        
    def _get_disclaimer_text(self) -> str:
        return "⚠️ WICHTIGE SICHERHEITSHINWEISE..." # Gekürzt für Lesbarkeit

    def _get_connection_schema(self) -> vol.Schema:
        return vol.Schema({
            vol.Required(CONF_API_URL, default="192.168.178.55"): str,
            vol.Optional(CONF_USERNAME): str,
            vol.Optional(CONF_PASSWORD): str,
            vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
            vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
            vol.Required(CONF_POLLING_INTERVAL, default=30): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
            vol.Required(CONF_TIMEOUT_DURATION, default=10): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            vol.Required(CONF_RETRY_ATTEMPTS, default=3): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            vol.Optional(CONF_DEVICE_NAME, default="🌊 Violet Pool Controller"): str,
        })

    def _get_pool_setup_schema(self) -> vol.Schema:
        return vol.Schema({
            vol.Required(CONF_POOL_SIZE, default=DEFAULT_POOL_SIZE): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000.0)),
            vol.Required(CONF_POOL_TYPE, default=DEFAULT_POOL_TYPE): vol.In(POOL_TYPE_OPTIONS),
            vol.Required(CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD): vol.In(DISINFECTION_OPTIONS),
        })

    def _get_feature_selection_schema(self) -> vol.Schema:
        return vol.Schema({
            vol.Optional(f"enable_{f['id']}", default=f["default"]): bool for f in AVAILABLE_FEATURES
        })
        
    def _get_sensor_selection_schema(self) -> vol.Schema:
        """Erstellt das Schema für die Sensor-Auswahl."""
        schema = {}
        for group, sensors in self._sensor_data.items():
            # Verwende den Gruppennamen als Key und Label
            schema[vol.Optional(group, default=sensors)] = vol.All(
                list, vol.Length(min=0), [vol.In(sensors)]
            )
        return vol.Schema(schema)


class VioletOptionsFlowHandler(config_entries.OptionsFlow):
    """Options Flow für Violet Pool Controller."""
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry
        self.current_config = {**config_entry.data, **config_entry.options}
        self._sensor_data: dict[str, list[str]] = {}

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Erweiterte Einstellungen und Sensor-Auswahl."""
        if user_input is not None:
            # Trenne Sensor-Auswahl von anderen Optionen
            selected_sensors = []
            other_options = {}
            for key, value in user_input.items():
                if key in self._sensor_data: # Key ist eine Sensor-Gruppe
                    selected_sensors.extend(value)
                else:
                    other_options[key] = value
            
            other_options[CONF_SELECTED_SENSORS] = selected_sensors
            _LOGGER.info("%d Sensoren in Optionen gespeichert", len(selected_sensors))
            
            return self.async_create_entry(title="", data=other_options)

        # Lade Sensoren für die Anzeige im Options-Flow
        self._sensor_data = await self._get_grouped_sensors()

        return self.async_show_form(
            step_id="init",
            data_schema=self._get_options_schema(),
        )

    async def _get_grouped_sensors(self) -> Dict[str, List[str]]:
        """Ruft Sensoren für den Options-Flow ab."""
        # Logik ist identisch zum ConfigFlow, könnte man auslagern
        try:
            protocol = "https" if self.current_config[CONF_USE_SSL] else "http"
            api_url = f"{protocol}://{self.current_config[CONF_API_URL]}{API_READINGS}?ALL"
            session = aiohttp_client.async_get_clientsession(self.hass)
            auth = aiohttp.BasicAuth(self.current_config[CONF_USERNAME], self.current_config[CONF_PASSWORD]) if self.current_config[CONF_USERNAME] else None
            
            data = await fetch_api_data(
                session, api_url, auth, self.current_config[CONF_USE_SSL],
                self.current_config[CONF_TIMEOUT_DURATION], self.current_config[CONF_RETRY_ATTEMPTS]
            )
            
            grouped: Dict[str, List[str]] = {}
            for key in sorted(data.keys()):
                group = key.split('_')[0]
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(key)
            return grouped
        except ValueError:
            return {}

    def _get_options_schema(self) -> vol.Schema:
        """Schema für Options Flow."""
        # Allgemeine Optionen
        schema = {
            vol.Optional(CONF_POLLING_INTERVAL, default=self.current_config.get(CONF_POLLING_INTERVAL, 30)): int,
            # ... weitere allgemeine Optionen ...
        }

        # Dynamische Sensor-Auswahl hinzufügen
        current_sensors = self.current_config.get(CONF_SELECTED_SENSORS, [])
        for group, sensors in self._sensor_data.items():
            # Standardmäßig sind die aktuell ausgewählten Sensoren dieser Gruppe vorausgewählt
            default_selection = [s for s in sensors if s in current_sensors]
            schema[vol.Optional(group, default=default_selection)] = vol.All(
                list, vol.Length(min=0), [vol.In(sensors)]
            )
        
        return vol.Schema(schema)
