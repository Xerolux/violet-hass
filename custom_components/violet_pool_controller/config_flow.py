"""Config Flow für Violet Pool Controller Integration - OPTIMIZED VERSION."""

from __future__ import annotations

import asyncio
import ipaddress
import logging
import re
from typing import Any, Mapping

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client, selector

from .const import (
    API_READINGS,
    AVAILABLE_FEATURES,
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_CONTROLLER_TYPE,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_DISINFECTION_METHOD,
    CONF_ERROR_TOLERANCE,
    CONF_PASSWORD,
    CONF_POLLING_INTERVAL,
    CONF_POOL_SIZE,
    CONF_POOL_TYPE,
    CONF_RETRY_ATTEMPTS,
    CONF_SELECTED_SENSORS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONTROLLER_TYPE_PROCONIP,
    CONTROLLER_TYPE_VIOLET,
    DEFAULT_CONTROLLER_NAME,
    DEFAULT_CONTROLLER_TYPE,
    DEFAULT_DISINFECTION_METHOD,
    DEFAULT_ERROR_TOLERANCE,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_POOL_SIZE,
    DEFAULT_POOL_TYPE,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_USE_SSL,
    DOMAIN,
    PROCONIP_API_GETSTATE,
)
from .const_sensors import (
    ANALOG_SENSORS,
    STATUS_SENSORS,
    SYSTEM_SENSORS,
    TEMP_SENSORS,
    WATER_CHEM_SENSORS,
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
MAX_DEVICE_ID = 99

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
    "outdoor": "🏖️ Freibad",
    "indoor": "🏠 Hallenbad",
    "whirlpool": "🛁 Whirlpool/Spa",
    "natural": "🌿 Naturpool/Schwimmteich",
    "combination": "🔄 Kombination",
}
DISINFECTION_OPTIONS = {
    "chlorine": "🧪 Chlor (Flüssig/Tabletten)",
    "salt": "🧂 Salzelektrolyse",
    "bromine": "⚗️ Brom",
    "active_oxygen": "💧 Aktivsauerstoff/H₂O₂",
    "uv": "💡 UV-Desinfektion",
    "ozone": "🌀 Ozon-Desinfektion",
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

GITHUB_BASE_URL = "https://github.com/xerolux/violet-hass"
HELP_DOC_DE_URL = f"{GITHUB_BASE_URL}/blob/main/docs/help/configuration-guide.de.md"
HELP_DOC_EN_URL = f"{GITHUB_BASE_URL}/blob/main/docs/help/configuration-guide.en.md"
SUPPORT_URL = f"{GITHUB_BASE_URL}/issues"

MENU_ACTION_START = "start_setup"
MENU_ACTION_HELP = "open_help"


def validate_ip_address(ip: str) -> bool:
    """
    Validate IP address or hostname.

    Args:
        ip: The IP address or hostname to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not ip:
        return False
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        # Allow hostnames (letters, numbers, dots, dashes)
        return bool(re.match(r"^[a-zA-Z0-9\-\.]+$", ip))


def get_sensor_label(key: str) -> str:
    """
    Get the friendly name for a sensor key.

    Args:
        key: The sensor key.

    Returns:
        The friendly name with key.
    """
    all_sensors = {
        **TEMP_SENSORS,
        **WATER_CHEM_SENSORS,
        **ANALOG_SENSORS,
        **SYSTEM_SENSORS,
        **STATUS_SENSORS,
    }
    if key in all_sensors:
        return f"{all_sensors[key]['name']} ({key})"
    return key


async def fetch_api_data(
    session: aiohttp.ClientSession,
    api_url: str,
    auth: aiohttp.BasicAuth | None,
    use_ssl: bool,
    timeout: int,
    retries: int,
) -> dict[str, Any]:
    """
    Fetch API data with retry logic.

    Args:
        session: The aiohttp client session.
        api_url: The API URL.
        auth: The authentication object.
        use_ssl: Whether to use SSL.
        timeout: The timeout in seconds.
        retries: The number of retries.

    Returns:
        A dictionary containing the API data.

    Raises:
        ValueError: If the API request fails.
    """
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
            retry_delay = BASE_RETRY_DELAY**attempt
            _LOGGER.warning(
                "API-Versuch %d/%d fehlgeschlagen, wiederhole in %ds",
                attempt + 1,
                retries,
                retry_delay,
            )
            await asyncio.sleep(retry_delay)
    raise ValueError("Fehler nach allen Versuchen")


async def get_grouped_sensors(
    hass: HomeAssistant,
    config_data: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Fetch sensors and group them.

    Args:
        hass: The Home Assistant instance.
        config_data: The configuration data.

    Returns:
        A dictionary mapping groups to lists of sensor keys.
    """
    try:
        protocol = "https" if config_data[CONF_USE_SSL] else "http"
        api_url = f"{protocol}://{config_data[CONF_API_URL]}{API_READINGS}?ALL"
        session = aiohttp_client.async_get_clientsession(hass)
        auth = (
            aiohttp.BasicAuth(
                config_data[CONF_USERNAME],
                config_data[CONF_PASSWORD],
            )
            if config_data.get(CONF_USERNAME)
            else None
        )

        data = await fetch_api_data(
            session,
            api_url,
            auth,
            config_data[CONF_USE_SSL],
            config_data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION),
            config_data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS),
        )

        grouped: dict[str, list[str]] = {}
        for key in sorted(data.keys()):
            # Einfache Gruppierung nach Präfix
            group = key.split("_")[0]
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(key)
        return grouped

    except ValueError:
        return {}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Violet Pool Controller."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialisiere Config Flow."""
        self._config_data: dict[str, Any] = {}
        self._sensor_data: dict[str, list[str]] = {}
        self._reauth_entry: config_entries.ConfigEntry | None = None
        _LOGGER.info("Violet Pool Controller Setup gestartet")

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Options Flow zurückgeben."""
        return OptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle the user-initiated setup start step.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input:
            action = user_input.get("action", MENU_ACTION_START)
            if action == MENU_ACTION_HELP:
                return await self.async_step_help()
            return await self.async_step_controller_type()

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_main_menu_schema(),
            description_placeholders=self._get_help_links(),
        )

    async def async_step_disclaimer(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle the disclaimer and terms of use step.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input and user_input.get("agreement"):
            return await self.async_step_connection()
        if user_input is not None:
            return self.async_abort(reason=ERROR_AGREEMENT_DECLINED)

        return self.async_show_form(
            step_id="disclaimer",
            data_schema=vol.Schema({vol.Required("agreement", default=False): bool}),
            description_placeholders={
                "disclaimer_text": self._get_disclaimer_text(),
                **self._get_help_links(),
            },
        )

    async def async_step_help(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Display additional help.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input is not None:
            return await self.async_step_user()

        return self.async_show_form(
            step_id="help",
            data_schema=vol.Schema({}),
            description_placeholders=self._get_help_links(),
        )

    async def async_step_controller_type(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle controller type selection.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input:
            controller_type = user_input.get(
                CONF_CONTROLLER_TYPE, DEFAULT_CONTROLLER_TYPE
            )
            self._config_data[CONF_CONTROLLER_TYPE] = controller_type

            if controller_type == CONTROLLER_TYPE_PROCONIP:
                return await self.async_step_proconip_connection()
            else:
                return await self.async_step_disclaimer()

        return self.async_show_form(
            step_id="controller_type",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CONTROLLER_TYPE, default=DEFAULT_CONTROLLER_TYPE
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=CONTROLLER_TYPE_VIOLET,
                                    label="🌊 Violet Pool Controller (Modern)",
                                ),
                                selector.SelectOptionDict(
                                    value=CONTROLLER_TYPE_PROCONIP,
                                    label="🏊 ProCon.IP Pool Controller (Legacy)",
                                ),
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
            description_placeholders={
                **self._get_help_links(),
                "violet_info": (
                    "Moderne Violet-Steuerung von PoolDigital mit JSON API, "
                    "erweiterten Features und Home Assistant Integration."
                ),
                "proconip_info": (
                    "Ältere ProCon.IP Steuerung mit CSV API. "
                    "Grundlegende Pool-Automatisierung mit Relays und Sensoren."
                ),
            },
        )

    async def async_step_connection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle the controller connection step.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        errors = {}
        error_hints = {}

        if user_input:
            if self._is_duplicate_entry(
                user_input[CONF_API_URL], int(user_input.get(CONF_DEVICE_ID, 1))
            ):
                errors["base"] = ERROR_ALREADY_CONFIGURED
                error_hints["base"] = (
                    "This controller is already configured. "
                    "Please check your integrations list."
                )
            elif not validate_ip_address(user_input[CONF_API_URL]):
                errors[CONF_API_URL] = ERROR_INVALID_IP
                error_hints[CONF_API_URL] = (
                    "Please enter a valid IP address "
                    "(e.g., 192.168.1.100) or hostname."
                )
            else:
                self._config_data = self._build_config_data(user_input)
                await self.async_set_unique_id(
                    f"{self._config_data[CONF_API_URL]}-{self._config_data[CONF_DEVICE_ID]}"
                )
                self._abort_if_unique_id_configured()
                if await self._test_connection():
                    return await self.async_step_pool_setup()
                errors["base"] = ERROR_CANNOT_CONNECT
                error_hints["base"] = (
                    "Cannot connect to the controller. Please check:\n"
                    "• Is the controller powered on and connected?\n"
                    "• Is the IP address correct?\n"
                    "• Are username/password correct (if auth enabled)?\n"
                    "• Can you ping the controller from this device?"
                )

        placeholders = {
            **self._get_help_links(),
            "step_progress": "Step 1 of 4",
            "step_title": "Connection Settings",
        }

        # Add error hints to placeholders if present
        if error_hints:
            placeholders["error_hint"] = "\n".join(error_hints.values())

        return self.async_show_form(
            step_id="connection",
            data_schema=self._get_connection_schema(),
            errors=errors,
            description_placeholders=placeholders,
        )

    async def async_step_pool_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle the pool configuration step.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input:
            self._config_data.update(
                {
                    CONF_POOL_SIZE: float(user_input[CONF_POOL_SIZE]),
                    CONF_POOL_TYPE: user_input[CONF_POOL_TYPE],
                    CONF_DISINFECTION_METHOD: user_input[CONF_DISINFECTION_METHOD],
                }
            )
            return await self.async_step_feature_selection()

        return self.async_show_form(
            step_id="pool_setup",
            data_schema=self._get_pool_setup_schema(),
            description_placeholders={
                "step_progress": "Step 2 of 4",
                "step_title": "Pool Configuration",
            },
        )

    async def async_step_feature_selection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle the feature selection step.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input:
            self._config_data[CONF_ACTIVE_FEATURES] = self._extract_active_features(
                user_input
            )

            # Hole Sensor-Daten für nächsten Schritt
            self._sensor_data = await self._get_grouped_sensors()
            if not self._sensor_data:
                _LOGGER.warning(
                    "Keine dynamischen Sensoren gefunden. Überspringe Auswahl."
                )
                self._config_data[CONF_SELECTED_SENSORS] = []
                return self.async_create_entry(
                    title=self._generate_entry_title(),
                    data=self._config_data,
                )

            return await self.async_step_sensor_selection()

        return self.async_show_form(
            step_id="feature_selection",
            data_schema=self._get_feature_selection_schema(),
            description_placeholders={
                "step_progress": "Step 3 of 4",
                "step_title": "Feature Selection",
            },
        )

    async def async_step_sensor_selection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle the dynamic sensor selection step.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input:
            selected_sensors = []
            for key, value in user_input.items():
                if isinstance(value, list) and value:  # Prüfe ob Liste und nicht leer
                    selected_sensors.extend(value)

            # ✅ FIX: Speichere Auswahl direkt. Leere Liste = keine Sensoren.
            # Wir verwenden None nur für Legacy-Konfigs, wo es "Alle" bedeutet.
            # Hier hat der User explizit gewählt (oder abgewählt).
            self._config_data[CONF_SELECTED_SENSORS] = selected_sensors

            if selected_sensors:
                _LOGGER.info("%d dynamische Sensoren ausgewählt", len(selected_sensors))
            else:
                _LOGGER.info("Keine dynamischen Sensoren ausgewählt.")

            return self.async_create_entry(
                title=self._generate_entry_title(), data=self._config_data
            )

        return self.async_show_form(
            step_id="sensor_selection",
            data_schema=self._get_sensor_selection_schema(),
            description_placeholders={
                "step_progress": "Step 4 of 4",
                "step_icon": "📊",
                "step_title": "Dynamic Sensors",
                "step_description": (
                    "Select the sensors you want to see in Home Assistant."
                ),
            },
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """
        Handle reauthentication when credentials have changed or expired.

        Args:
            entry_data: The existing config entry data.

        Returns:
            The flow result.
        """
        # Store the existing entry for updating
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle reauthentication confirmation and credential update.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        errors = {}

        if user_input:
            # Get existing config data
            assert self._reauth_entry is not None
            existing_data = dict(self._reauth_entry.data)

            # Update credentials
            existing_data[CONF_USERNAME] = user_input.get(CONF_USERNAME, "")
            existing_data[CONF_PASSWORD] = user_input.get(CONF_PASSWORD, "")

            # Test new credentials
            self._config_data = existing_data
            if await self._test_connection():
                # Update the config entry with new credentials
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry,
                    data=existing_data,
                )
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

            errors["base"] = ERROR_CANNOT_CONNECT

        # Show form with current values
        assert self._reauth_entry is not None
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_USERNAME,
                        default=self._reauth_entry.data.get(CONF_USERNAME, ""),
                    ): str,
                    vol.Optional(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "controller_name": self._reauth_entry.data.get(
                    CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME
                ),
                "api_url": self._reauth_entry.data.get(CONF_API_URL),
            },
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle reconfiguration of connection settings.

        Allows updating host, SSL, and other connection parameters without
        repeating the entire setup process.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        errors = {}

        # Get the entry being reconfigured
        reconfigure_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        assert reconfigure_entry is not None

        if user_input:
            # Validate IP address
            if not validate_ip_address(user_input[CONF_API_URL]):
                errors[CONF_API_URL] = ERROR_INVALID_IP
            else:
                # Build updated config
                updated_data = dict(reconfigure_entry.data)
                updated_data[CONF_API_URL] = user_input[CONF_API_URL]
                updated_data[CONF_USE_SSL] = user_input.get(
                    CONF_USE_SSL, DEFAULT_USE_SSL
                )
                updated_data[CONF_POLLING_INTERVAL] = int(
                    user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
                )
                updated_data[CONF_TIMEOUT_DURATION] = int(
                    user_input.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)
                )
                updated_data[CONF_RETRY_ATTEMPTS] = int(
                    user_input.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)
                )

                # Test connection with new settings
                self._config_data = updated_data
                if await self._test_connection():
                    # Update the config entry
                    self.hass.config_entries.async_update_entry(
                        reconfigure_entry,
                        data=updated_data,
                    )
                    await self.hass.config_entries.async_reload(
                        reconfigure_entry.entry_id
                    )
                    return self.async_abort(reason="reconfigure_successful")

                errors["base"] = ERROR_CANNOT_CONNECT

        # Show form with current values
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_URL,
                        default=reconfigure_entry.data.get(
                            CONF_API_URL, "192.168.178.55"
                        ),
                    ): str,
                    vol.Required(
                        CONF_USE_SSL,
                        default=reconfigure_entry.data.get(
                            CONF_USE_SSL, DEFAULT_USE_SSL
                        ),
                    ): bool,
                    vol.Required(
                        CONF_POLLING_INTERVAL,
                        default=reconfigure_entry.data.get(
                            CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_POLLING_INTERVAL,
                            max=MAX_POLLING_INTERVAL,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Required(
                        CONF_TIMEOUT_DURATION,
                        default=reconfigure_entry.data.get(
                            CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_TIMEOUT,
                            max=MAX_TIMEOUT,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Required(
                        CONF_RETRY_ATTEMPTS,
                        default=reconfigure_entry.data.get(
                            CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_RETRIES,
                            max=MAX_RETRIES,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
                "controller_name": reconfigure_entry.data.get(
                    CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME
                ),
            },
        )

    async def async_step_proconip_connection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle ProconIP controller connection setup.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        errors = {}
        error_hints = {}

        if user_input:
            # Extract controller URL (e.g., http://192.168.1.100)
            controller_url = user_input[CONF_API_URL].strip()

            # Normalize URL format
            if not controller_url.startswith(("http://", "https://")):
                controller_url = f"http://{controller_url}"

            # Check for duplicate
            if self._is_duplicate_proconip_entry(controller_url):
                errors["base"] = ERROR_ALREADY_CONFIGURED
                error_hints["base"] = (
                    "This ProCon.IP controller is already configured."
                )
            else:
                # Build config data for ProconIP
                self._config_data.update(
                    {
                        CONF_API_URL: controller_url,
                        CONF_USERNAME: user_input.get(CONF_USERNAME, "admin"),
                        CONF_PASSWORD: user_input.get(CONF_PASSWORD, "admin"),
                        CONF_POLLING_INTERVAL: int(
                            user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
                        ),
                        CONF_TIMEOUT_DURATION: int(
                            user_input.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)
                        ),
                        CONF_ERROR_TOLERANCE: int(
                            user_input.get(CONF_ERROR_TOLERANCE, DEFAULT_ERROR_TOLERANCE)
                        ),
                        CONF_CONTROLLER_NAME: user_input.get(
                            CONF_CONTROLLER_NAME, "ProCon.IP Pool Controller"
                        ),
                        CONF_DEVICE_ID: 1,  # ProconIP doesn't need multiple device IDs
                        CONF_USE_SSL: False,  # ProconIP typically doesn't use SSL
                    }
                )

                await self.async_set_unique_id(f"proconip-{controller_url}")
                self._abort_if_unique_id_configured()

                # Test connection to ProconIP
                if await self._test_proconip_connection():
                    return await self.async_step_proconip_features()

                errors["base"] = ERROR_CANNOT_CONNECT
                error_hints["base"] = (
                    "Cannot connect to ProCon.IP controller. Please check:\n"
                    "• Is the controller powered on and connected?\n"
                    "• Is the URL correct (e.g., http://192.168.1.100)?\n"
                    "• Are username/password correct?\n"
                    "• Can you access the web interface from this device?"
                )

        placeholders = {
            **self._get_help_links(),
            "step_progress": "Step 1 of 2",
            "step_title": "ProCon.IP Connection",
        }

        if error_hints:
            placeholders["error_hint"] = "\n".join(error_hints.values())

        return self.async_show_form(
            step_id="proconip_connection",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL, default="http://192.168.1.100"): str,
                    vol.Optional(CONF_USERNAME, default="admin"): str,
                    vol.Optional(CONF_PASSWORD, default="admin"): str,
                    vol.Required(
                        CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_POLLING_INTERVAL,
                            max=MAX_POLLING_INTERVAL,
                            step=5,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    ),
                    vol.Required(
                        CONF_TIMEOUT_DURATION, default=DEFAULT_TIMEOUT_DURATION
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_TIMEOUT,
                            max=MAX_TIMEOUT,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    ),
                    vol.Required(
                        CONF_ERROR_TOLERANCE, default=DEFAULT_ERROR_TOLERANCE
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=10,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_CONTROLLER_NAME, default="ProCon.IP Pool Controller"
                    ): str,
                }
            ),
            errors=errors,
            description_placeholders=placeholders,
        )

    async def async_step_proconip_features(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle ProconIP feature configuration (simplified).

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input:
            # ProconIP has basic features - store pool info
            self._config_data.update(
                {
                    CONF_POOL_SIZE: float(
                        user_input.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)
                    ),
                    CONF_POOL_TYPE: user_input.get(CONF_POOL_TYPE, DEFAULT_POOL_TYPE),
                    CONF_DISINFECTION_METHOD: user_input.get(
                        CONF_DISINFECTION_METHOD, DEFAULT_DISINFECTION_METHOD
                    ),
                    # ProconIP doesn't have advanced features like Violet
                    CONF_ACTIVE_FEATURES: [],
                    CONF_SELECTED_SENSORS: None,  # All sensors enabled by default
                }
            )

            # Create entry
            return self.async_create_entry(
                title=self._generate_proconip_entry_title(),
                data=self._config_data,
            )

        return self.async_show_form(
            step_id="proconip_features",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_POOL_SIZE, default=DEFAULT_POOL_SIZE
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_POOL_SIZE,
                            max=MAX_POOL_SIZE,
                            step=0.5,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="m³",
                        )
                    ),
                    vol.Required(
                        CONF_POOL_TYPE, default=DEFAULT_POOL_TYPE
                    ): vol.In(POOL_TYPE_OPTIONS),
                    vol.Required(
                        CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD
                    ): vol.In(DISINFECTION_OPTIONS),
                }
            ),
            description_placeholders={
                "step_progress": "Step 2 of 2",
                "step_title": "Pool Configuration",
                "step_description": (
                    "Provide basic information about your pool for optimal monitoring."
                ),
            },
        )

    # ================= Helper Methods =================

    def _is_duplicate_entry(self, ip: str, device_id: int = 1) -> bool:
        """
        Check if the IP + Device ID combination already exists.

        ✅ MULTI-CONTROLLER FIX: Allows multiple controllers with the same IP
        but different Device IDs (e.g., on different ports).

        Args:
            ip: Controller IP address.
            device_id: Device ID (default: 1).

        Returns:
            True if this combination is already configured, False otherwise.
        """
        return any(
            entry.data.get(CONF_API_URL) == ip
            and entry.data.get(CONF_DEVICE_ID, 1) == device_id
            for entry in self._async_current_entries()
        )

    def _build_config_data(self, ui: dict) -> dict:
        """
        Build the configuration data dictionary.

        Args:
            ui: The user input dictionary.

        Returns:
            The configuration data dictionary.
        """
        return {
            CONF_API_URL: ui[CONF_API_URL],
            CONF_USE_SSL: ui.get(CONF_USE_SSL, DEFAULT_USE_SSL),
            CONF_DEVICE_NAME: ui.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller"),
            CONF_CONTROLLER_NAME: ui.get(CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME),
            CONF_USERNAME: ui.get(CONF_USERNAME, ""),
            CONF_PASSWORD: ui.get(CONF_PASSWORD, ""),
            CONF_DEVICE_ID: int(ui.get(CONF_DEVICE_ID, 1)),
            CONF_POLLING_INTERVAL: int(
                ui.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
            ),
            CONF_TIMEOUT_DURATION: int(
                ui.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)
            ),
            CONF_RETRY_ATTEMPTS: int(
                ui.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)
            ),
        }

    async def _test_connection(self) -> bool:
        """
        Test the connection to the controller.

        Returns:
            True if successful, False otherwise.
        """
        try:
            protocol = "https" if self._config_data[CONF_USE_SSL] else "http"
            api_url = (
                f"{protocol}://{self._config_data[CONF_API_URL]}{API_READINGS}?ALL"
            )
            session = aiohttp_client.async_get_clientsession(self.hass)
            auth = (
                aiohttp.BasicAuth(
                    self._config_data[CONF_USERNAME],
                    self._config_data[CONF_PASSWORD],
                )
                if self._config_data[CONF_USERNAME]
                else None
            )
            await fetch_api_data(
                session,
                api_url,
                auth,
                self._config_data[CONF_USE_SSL],
                self._config_data[CONF_TIMEOUT_DURATION],
                self._config_data[CONF_RETRY_ATTEMPTS],
            )
            return True
        except ValueError:
            return False

    def _is_duplicate_proconip_entry(self, controller_url: str) -> bool:
        """
        Check if ProconIP controller URL already exists.

        Args:
            controller_url: The controller URL to check.

        Returns:
            True if already configured, False otherwise.
        """
        return any(
            entry.data.get(CONF_API_URL) == controller_url
            and entry.data.get(CONF_CONTROLLER_TYPE) == CONTROLLER_TYPE_PROCONIP
            for entry in self._async_current_entries()
        )

    async def _test_proconip_connection(self) -> bool:
        """
        Test connection to ProconIP controller via GetState.csv.

        Returns:
            True if successful, False otherwise.
        """
        try:
            api_url = f"{self._config_data[CONF_API_URL]}{PROCONIP_API_GETSTATE}"
            session = aiohttp_client.async_get_clientsession(self.hass)

            # ProconIP uses basic auth
            auth = None
            if self._config_data.get(CONF_USERNAME):
                auth = aiohttp.BasicAuth(
                    self._config_data[CONF_USERNAME],
                    self._config_data[CONF_PASSWORD],
                )

            timeout_obj = aiohttp.ClientTimeout(
                total=self._config_data[CONF_TIMEOUT_DURATION]
            )

            async with session.get(
                api_url, auth=auth, ssl=False, timeout=timeout_obj
            ) as response:
                response.raise_for_status()
                # ProconIP returns CSV data - just check if we get a response
                content = await response.text()
                if len(content) > 0:
                    _LOGGER.info("ProCon.IP connection test successful")
                    return True
                return False

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("ProCon.IP connection test failed: %s", err)
            return False

    def _generate_proconip_entry_title(self) -> str:
        """
        Generate title for ProconIP config entry.

        Returns:
            The config entry title.
        """
        controller_name = self._config_data.get(
            CONF_CONTROLLER_NAME, "ProCon.IP Pool Controller"
        )
        pool_size = self._config_data.get(CONF_POOL_SIZE)
        return f"{controller_name} • {pool_size}m³"

    async def _get_grouped_sensors(self) -> dict[str, list[str]]:
        """
        Fetch and group sensors.

        Returns:
            A dictionary mapping groups to lists of sensor keys.
        """
        return await get_grouped_sensors(self.hass, self._config_data)

    def _extract_active_features(self, ui: dict) -> list:
        """
        Extract active features from user input.

        Args:
            ui: The user input dictionary.

        Returns:
            A list of active feature IDs.
        """
        return [
            f["id"]
            for f in AVAILABLE_FEATURES
            if ui.get(f"enable_{f['id']}", f["default"])
        ]

    def _generate_entry_title(self) -> str:
        """
        Generate the title for the config entry.

        Returns:
            The config entry title.
        """
        controller_name = self._config_data.get(
            CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME
        )
        pool_size = self._config_data.get(CONF_POOL_SIZE)
        return f"{controller_name} • {pool_size}m³"

    def _get_disclaimer_text(self) -> str:
        """
        Get the disclaimer text.

        Returns:
            The disclaimer text.
        """
        template = (
            "⚠️ **Sicherheitswarnung / Safety Warning**\n\n"
            "**DE:** Diese Integration kann Pumpen, Heizungen, Beleuchtung und "
            "Dosieranlagen deines Pools fernsteuern. Falsche Einstellungen können "
            "zu Sachschäden, Verletzungen oder Überdosierungen führen. Stelle sicher, "
            "dass du alle Schutzmechanismen verstehst und jederzeit manuell eingreifen "
            "kannst. Lies vor der Nutzung unbedingt die Hinweise in der "
            "Konfigurationshilfe ({docs_de}).\n\n"
            "**EN:** This integration provides remote control for pumps, heaters, "
            "lights and dosing systems. Incorrect configuration may cause equipment "
            "damage, personal injury or chemical overdosing. Make sure you understand "
            "all safety features and keep manual overrides accessible. Please review "
            "the configuration guide ({docs_en}) before you continue."
        )
        return template.format(**self._get_help_links())

    def _get_help_links(self) -> dict[str, str]:
        """
        Get helper links.

        Returns:
            A dictionary of help links.
        """
        return {
            "docs_de": HELP_DOC_DE_URL,
            "docs_en": HELP_DOC_EN_URL,
            "github_url": GITHUB_BASE_URL,
            "issues_url": SUPPORT_URL,
        }

    def _get_main_menu_schema(self) -> vol.Schema:
        """
        Get the main menu schema.

        Returns:
            The voluptuous schema.
        """
        return vol.Schema(
            {
                vol.Required(
                    "action", default=MENU_ACTION_START
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value=MENU_ACTION_START,
                                label="⚙️ Setup starten / Start setup",
                            ),
                            selector.SelectOptionDict(
                                value=MENU_ACTION_HELP,
                                label="📘 Hilfe & Dokumentation / Help & docs",
                            ),
                        ]
                    )
                )
            }
        )

    def _get_connection_schema(self) -> vol.Schema:
        """
        Get the connection schema.

        Returns:
            The voluptuous schema.
        """
        return vol.Schema(
            {
                vol.Required(CONF_API_URL, default="192.168.178.55"): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
                vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
                vol.Required(CONF_DEVICE_ID, default=1): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_DEVICE_ID,
                        max=MAX_DEVICE_ID,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_POLLING_INTERVAL,
                        max=MAX_POLLING_INTERVAL,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_TIMEOUT_DURATION, default=DEFAULT_TIMEOUT_DURATION
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_TIMEOUT,
                        max=MAX_TIMEOUT,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_RETRY_ATTEMPTS, default=DEFAULT_RETRY_ATTEMPTS
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_RETRIES,
                        max=MAX_RETRIES,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_DEVICE_NAME, default="🌊 Violet Pool Controller"
                ): str,
                vol.Optional(
                    CONF_CONTROLLER_NAME, default=DEFAULT_CONTROLLER_NAME
                ): str,
            }
        )

    def _get_pool_setup_schema(self) -> vol.Schema:
        """
        Get the pool setup schema.

        Returns:
            The voluptuous schema.
        """
        return vol.Schema(
            {
                vol.Required(
                    CONF_POOL_SIZE, default=DEFAULT_POOL_SIZE
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_POOL_SIZE,
                        max=MAX_POOL_SIZE,
                        step=0.1,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="m³",
                    )
                ),
                vol.Required(CONF_POOL_TYPE, default=DEFAULT_POOL_TYPE): vol.In(
                    POOL_TYPE_OPTIONS
                ),
                vol.Required(
                    CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD
                ): vol.In(DISINFECTION_OPTIONS),
            }
        )

    def _get_feature_selection_schema(self) -> vol.Schema:
        """
        Get the feature selection schema.

        Returns:
            The voluptuous schema.
        """
        return vol.Schema(
            {
                vol.Optional(f"enable_{f['id']}", default=f["default"]): bool
                for f in AVAILABLE_FEATURES
            }
        )

    def _get_sensor_selection_schema(self) -> vol.Schema:
        """
        Create the sensor selection schema.

        Returns:
            The voluptuous schema.
        """
        schema = {}
        for group, sensors in self._sensor_data.items():
            # Erstelle Optionen mit freundlichen Namen
            options = [
                selector.SelectOptionDict(
                    value=sensor,
                    label=get_sensor_label(sensor),
                )
                for sensor in sensors
            ]

            # Standardmäßig ALLE auswählen, damit der User sieht was er bekommt
            # und explizit abwählen muss. Das verhindert Verwirrung.
            schema[vol.Optional(group, default=sensors)] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=options,
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        return vol.Schema(schema)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options Flow für Violet Pool Controller."""

    def __init__(self) -> None:
        """Initialize options flow."""
        self._sensor_data: dict[str, list[str]] = {}
        self._updated_options: dict[str, Any] = {}

    @property
    def current_config(self) -> dict[str, Any]:
        """Get current configuration merged from data and options."""
        return {**self.config_entry.data, **self.config_entry.options}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle the initial options menu - let user choose what to configure.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input is not None:
            choice = user_input.get("config_option", "settings")

            if choice == "features":
                return await self.async_step_features()
            elif choice == "sensors":
                return await self.async_step_sensors()
            else:  # settings
                return await self.async_step_settings()

        # Show menu with configuration options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "config_option", default="settings"
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value="features",
                                    label="🎛️ Features aktivieren/deaktivieren",
                                ),
                                selector.SelectOptionDict(
                                    value="sensors", label="📊 Sensoren auswählen"
                                ),
                                selector.SelectOptionDict(
                                    value="settings", label="⚙️ Einstellungen ändern"
                                ),
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
        )

    async def async_step_features(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle feature selection in options flow.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input is not None:
            # Store selected features
            selected_features = user_input.get(CONF_ACTIVE_FEATURES, [])
            self._updated_options[CONF_ACTIVE_FEATURES] = selected_features

            _LOGGER.info(
                "Features in Optionen aktualisiert: %s", ", ".join(selected_features)
            )

            # Merge with existing options and create entry
            final_options = {**self.current_config, **self._updated_options}
            return self.async_create_entry(title="", data=final_options)

        # Get currently active features
        current_features = self.current_config.get(CONF_ACTIVE_FEATURES, [])

        # Build feature options with enhanced display
        feature_options = []
        for feature in AVAILABLE_FEATURES:
            feature_id = str(feature["id"])
            if feature_id in ENHANCED_FEATURES:
                info = ENHANCED_FEATURES[feature_id]
                label = f"{info['icon']} {info['name']}"
            else:
                label = str(feature["name"])

            feature_options.append(
                selector.SelectOptionDict(value=feature_id, label=label)
            )

        return self.async_show_form(
            step_id="features",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ACTIVE_FEATURES,
                        default=current_features,
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=feature_options,
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
            description_placeholders={
                "info": "Wählen Sie die Features, die Sie nutzen möchten. "
                "Deaktivierte Features werden ausgeblendet."
            },
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle sensor selection in options flow.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input is not None:
            # Trenne Sensor-Auswahl von anderen Optionen
            selected_sensors = []
            for key, value in user_input.items():
                if key in self._sensor_data:  # Key ist eine Sensor-Gruppe
                    if (
                        isinstance(value, list) and value
                    ):  # Prüfe ob Liste und nicht leer
                        selected_sensors.extend(value)

            # Store selected sensors
            self._updated_options[CONF_SELECTED_SENSORS] = selected_sensors

            if selected_sensors:
                _LOGGER.info(
                    "%d Sensoren in Optionen gespeichert", len(selected_sensors)
                )
            else:
                _LOGGER.info("Keine Sensoren in Optionen ausgewählt.")

            # Merge with existing options and create entry
            final_options = {**self.current_config, **self._updated_options}
            return self.async_create_entry(title="", data=final_options)

        # Lade Sensoren für die Anzeige im Options-Flow
        self._sensor_data = await self._get_grouped_sensors()

        return self.async_show_form(
            step_id="sensors",
            data_schema=self._get_sensor_schema(),
        )

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """
        Handle general settings in options flow.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input is not None:
            # Store settings
            self._updated_options.update(user_input)

            # Merge with existing options and create entry
            final_options = {**self.current_config, **self._updated_options}
            return self.async_create_entry(title="", data=final_options)

        return self.async_show_form(
            step_id="settings",
            data_schema=self._get_settings_schema(),
        )

    async def _get_grouped_sensors(self) -> dict[str, list[str]]:
        """
        Fetch sensors for the options flow.

        Returns:
            A dictionary mapping groups to lists of sensor keys.
        """
        return await get_grouped_sensors(self.hass, self.current_config)

    def _get_settings_schema(self) -> vol.Schema:
        """
        Get the schema for general settings.

        Returns:
            The voluptuous schema.
        """
        return vol.Schema(
            {
                vol.Optional(
                    CONF_CONTROLLER_NAME,
                    default=self.current_config.get(
                        CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME
                    ),
                ): str,
                vol.Optional(
                    CONF_POLLING_INTERVAL,
                    default=self.current_config.get(
                        CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_POLLING_INTERVAL,
                        max=MAX_POLLING_INTERVAL,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_TIMEOUT_DURATION,
                    default=self.current_config.get(
                        CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_TIMEOUT,
                        max=MAX_TIMEOUT,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_RETRY_ATTEMPTS,
                    default=self.current_config.get(
                        CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_RETRIES,
                        max=MAX_RETRIES,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

    def _get_sensor_schema(self) -> vol.Schema:
        """
        Get the schema for sensor selection.

        Returns:
            The voluptuous schema.
        """
        schema = {}

        # Dynamische Sensor-Auswahl hinzufügen
        # None (Legacy) bedeutet ALLE Sensoren sind ausgewählt.
        stored_sensors = self.current_config.get(CONF_SELECTED_SENSORS)
        is_all_selected = stored_sensors is None

        for group, sensors in self._sensor_data.items():
            # Erstelle Optionen mit freundlichen Namen
            options = [
                selector.SelectOptionDict(
                    value=sensor,
                    label=get_sensor_label(sensor),
                )
                for sensor in sensors
            ]

            # Wenn ALLE ausgewählt (None), dann wähle alle in dieser Gruppe.
            # Ansonsten nimm die gespeicherte Liste.
            if is_all_selected:
                default_selection = sensors
            else:
                default_selection = [
                    s for s in sensors if stored_sensors and s in stored_sensors
                ]

            schema[vol.Optional(group, default=default_selection)] = (
                selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            )

        return vol.Schema(schema)
