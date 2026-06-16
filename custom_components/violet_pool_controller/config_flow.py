# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Config flow for Violet Pool Controller integration."""

from __future__ import annotations

import ipaddress
import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client, selector
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from violet_poolcontroller_api.api import VioletPoolAPI

from .config_flow_support import (
    ConfigFlowSchemaMixin,
    ConfigFlowTextMixin,
    OptionsFlowHandler,
)
from .config_flow_utils import (
    MAX_POLLING_INTERVAL,
    MAX_RETRIES,
    MAX_TIMEOUT,
    MIN_POLLING_INTERVAL,
    MIN_RETRIES,
    MIN_TIMEOUT,
    constants,
    get_grouped_sensors,
    validators,
)
from .const import (
    AVAILABLE_FEATURES,
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_DISINFECTION_METHOD,
    CONF_DOSING_STANDALONE,
    CONF_PASSWORD,
    CONF_POLLING_INTERVAL,
    CONF_POOL_SIZE,
    CONF_POOL_TYPE,
    CONF_PORT,
    CONF_RETRY_ATTEMPTS,
    CONF_SELECTED_SENSORS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_CONTROLLER_NAME,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_USE_SSL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(
    ConfigFlowSchemaMixin,
    ConfigFlowTextMixin,
    config_entries.ConfigFlow,
    domain=DOMAIN,
):  # type: ignore[call-arg]
    """Config flow for Violet Pool Controller."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._config_data: dict[str, Any] = {}
        self._sensor_data: dict[str, list[str]] = {}
        self._title_placeholders: dict[str, str] = {}
        self._reauth_entry: config_entries.ConfigEntry | None = None
        _LOGGER.debug("Violet Pool Controller setup started")

    @staticmethod
    def _build_unique_id(host: str, device_id: int | str) -> str:
        """Build a stable unique ID shared by manual and zeroconf setup."""
        return f"{host}-{int(device_id)}"

    @staticmethod
    def _is_ip_literal(host: str) -> bool:
        """Return True when host is an IPv4/IPv6 literal."""
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return OptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user-initiated setup start step."""
        if user_input:
            action = user_input.get("action", constants.MENU_ACTION_START)
            if action == constants.MENU_ACTION_HELP:
                return await self.async_step_help()
            return await self.async_step_disclaimer()

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_main_menu_schema(),
            description_placeholders=self._get_help_links(),
        )

    async def async_step_disclaimer(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the disclaimer and terms of use step."""
        if user_input and user_input.get("agreement"):
            return await self.async_step_connection()
        if user_input is not None:
            return self.async_abort(reason=constants.ERROR_AGREEMENT_DECLINED)

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
        """Display additional help."""
        if user_input is not None:
            return await self.async_step_user()

        return self.async_show_form(
            step_id="help",
            data_schema=vol.Schema({}),
            description_placeholders=self._get_help_links(),
        )

    async def async_step_connection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the controller connection step."""
        errors = {}
        error_hints = {}

        if user_input:
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            if self._is_duplicate_entry(
                user_input[CONF_API_URL], port, int(user_input.get(CONF_DEVICE_ID, 1))
            ):
                errors["base"] = constants.ERROR_ALREADY_CONFIGURED
                error_hints["base"] = (
                    "This controller is already configured."
                    " Please check your integrations list."
                )
            elif not validators.validate_ip_address(user_input[CONF_API_URL]):
                errors[CONF_API_URL] = constants.ERROR_INVALID_IP
                error_hints[CONF_API_URL] = (
                    "Please enter a valid IP address (e.g., 192.168.1.100) or hostname."
                )
            else:
                self._config_data = self._build_config_data(user_input)
                await self.async_set_unique_id(
                    self._build_unique_id(
                        self._config_data[CONF_API_URL],
                        self._config_data[CONF_DEVICE_ID],
                    )
                )
                self._abort_if_unique_id_configured()
                if await self._test_connection():
                    return await self.async_step_pool_setup()
                errors["base"] = constants.ERROR_CANNOT_CONNECT
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
        """Handle the pool configuration step."""
        if user_input:
            self._config_data.update(
                {
                    CONF_POOL_SIZE: float(user_input[CONF_POOL_SIZE]),
                    CONF_POOL_TYPE: user_input[CONF_POOL_TYPE],
                    CONF_DISINFECTION_METHOD: user_input[CONF_DISINFECTION_METHOD],
                }
            )
            return await self._auto_configure_entities()

        return self.async_show_form(
            step_id="pool_setup",
            data_schema=self._get_pool_setup_schema(),
            description_placeholders={
                "step_progress": "Step 2 of 3",
                "step_title": "Pool Configuration",
            },
        )

    async def async_step_feature_selection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Compatibility step: features are now detected automatically."""
        return await self._auto_configure_entities()

    async def async_step_sensor_selection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the dynamic sensor selection step."""
        if user_input:
            selected_sensors = []
            for key, value in user_input.items():
                if isinstance(value, list) and value:
                    selected_sensors.extend(value)

            self._config_data[CONF_SELECTED_SENSORS] = selected_sensors
            if selected_sensors:
                _LOGGER.info("%d dynamic sensors selected", len(selected_sensors))
            else:
                _LOGGER.info("No dynamic sensors selected.")

            return self.async_create_entry(
                title=self._generate_entry_title(), data=self._config_data
            )

        return self.async_show_form(
            step_id="sensor_selection",
            data_schema=self._get_sensor_selection_schema(),
            description_placeholders={
                "step_progress": "Step 3 of 3",
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
        """Handle reauthentication when credentials have changed or expired."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        if self._reauth_entry is None:
            return self.async_abort(reason="reauth_failed")
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reauthentication confirmation and credential update."""
        errors = {}

        if user_input:
            if self._reauth_entry is None:
                return self.async_abort(reason="reauth_failed")
            existing_data = dict(self._reauth_entry.data)
            existing_data[CONF_USERNAME] = user_input.get(CONF_USERNAME, "")
            existing_data[CONF_PASSWORD] = user_input.get(CONF_PASSWORD, "")
            self._config_data = existing_data
            if await self._test_connection():
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry,
                    data=existing_data,
                )
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

            errors["base"] = constants.ERROR_CANNOT_CONNECT

        if self._reauth_entry is None:
            return self.async_abort(reason="reauth_failed")
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
                "api_url": self._reauth_entry.data.get(CONF_API_URL, "Unknown"),
            },
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery of a Violet Pool Controller."""
        host = str(discovery_info.ip_address)
        name = discovery_info.name

        _LOGGER.info(
            "Zeroconf discovery: Violet Pool Controller '%s' at %s", name, host
        )

        port = discovery_info.port or DEFAULT_PORT
        device_id = 1
        await self.async_set_unique_id(self._build_unique_id(host, device_id))
        self._abort_if_unique_id_configured(
            updates={CONF_API_URL: host, CONF_DEVICE_ID: device_id},
            reload_on_update=True,
        )

        self._config_data = {
            CONF_API_URL: host,
            CONF_PORT: port,
            CONF_USE_SSL: DEFAULT_USE_SSL,
            CONF_DEVICE_NAME: name.split(".")[0] if "." in name else name,
            CONF_CONTROLLER_NAME: DEFAULT_CONTROLLER_NAME,
            CONF_USERNAME: "",
            CONF_PASSWORD: "",
            CONF_DEVICE_ID: device_id,
            CONF_POLLING_INTERVAL: DEFAULT_POLLING_INTERVAL,
            CONF_TIMEOUT_DURATION: DEFAULT_TIMEOUT_DURATION,
            CONF_RETRY_ATTEMPTS: DEFAULT_RETRY_ATTEMPTS,
        }

        self._title_placeholders = {
            "name": name,
            "host": f"{host}:{port}" if port not in (80, 443) else host,
        }
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm zeroconf discovered Violet Pool Controller."""
        placeholders = self._title_placeholders or dict(
            self.context.get("title_placeholders", {})
        )
        if user_input is not None:
            if await self._test_connection():
                return await self.async_step_pool_setup()
            return self.async_show_form(
                step_id="zeroconf_confirm",
                description_placeholders=placeholders,
                errors={"base": constants.ERROR_CANNOT_CONNECT},
            )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders=placeholders,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of connection settings."""
        errors = {}
        reconfigure_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        if reconfigure_entry is None:
            return self.async_abort(reason="reconfigure_failed")

        if user_input:
            api_url = user_input.get(CONF_API_URL) or user_input.get("api_url")
            if (
                not api_url
                or not validators.validate_ip_address(api_url)
                or (not self._is_ip_literal(api_url) and "." not in api_url)
            ):
                errors[CONF_API_URL] = "invalid_ip"
            else:
                updated_data = dict(reconfigure_entry.data)
                updated_data[CONF_API_URL] = api_url
                updated_data[CONF_PORT] = int(user_input.get(CONF_PORT, DEFAULT_PORT))
                updated_data[CONF_USE_SSL] = user_input.get(
                    CONF_USE_SSL, DEFAULT_USE_SSL
                )
                updated_data[CONF_VERIFY_SSL] = user_input.get(
                    CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL
                )
                updated_data[CONF_USERNAME] = user_input.get(
                    CONF_USERNAME, reconfigure_entry.data.get(CONF_USERNAME, "")
                )
                updated_data[CONF_PASSWORD] = user_input.get(
                    CONF_PASSWORD, reconfigure_entry.data.get(CONF_PASSWORD, "")
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

                self._config_data = updated_data
                if await self._test_connection():
                    self.hass.config_entries.async_update_entry(
                        reconfigure_entry,
                        data=updated_data,
                    )
                    await self.hass.config_entries.async_reload(
                        reconfigure_entry.entry_id
                    )
                    return self.async_abort(reason="reconfigure_successful")

                errors["base"] = constants.ERROR_CANNOT_CONNECT

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_URL,
                        default=reconfigure_entry.data.get(CONF_API_URL, ""),
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        default=reconfigure_entry.data.get(CONF_PORT, DEFAULT_PORT),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_USERNAME,
                        default=reconfigure_entry.data.get(CONF_USERNAME, ""),
                    ): str,
                    vol.Optional(
                        CONF_PASSWORD,
                        default=reconfigure_entry.data.get(CONF_PASSWORD, ""),
                    ): str,
                    vol.Required(
                        CONF_USE_SSL,
                        default=reconfigure_entry.data.get(
                            CONF_USE_SSL, DEFAULT_USE_SSL
                        ),
                    ): bool,
                    vol.Required(
                        CONF_VERIFY_SSL,
                        default=reconfigure_entry.data.get(
                            CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL
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

    async def async_step_repair(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle repair flow for controller_unavailable issue."""
        errors: dict[str, str] = {}
        repair_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        if repair_entry is None:
            return self.async_abort(reason="repair_failed")

        if user_input:
            updated_data = dict(repair_entry.data)
            updated_data[CONF_API_URL] = user_input[CONF_API_URL]
            updated_data[CONF_PORT] = int(user_input.get(CONF_PORT, DEFAULT_PORT))
            updated_data[CONF_USERNAME] = user_input.get(CONF_USERNAME, "")
            updated_data[CONF_PASSWORD] = user_input.get(CONF_PASSWORD, "")
            self._config_data = updated_data
            if await self._test_connection():
                self.hass.config_entries.async_update_entry(
                    repair_entry, data=updated_data
                )
                await self.hass.config_entries.async_reload(repair_entry.entry_id)
                return self.async_abort(reason="repair_successful")
            errors["base"] = constants.ERROR_CANNOT_CONNECT

        return self.async_show_form(
            step_id="repair",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_URL,
                        default=repair_entry.data.get(CONF_API_URL, ""),
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        default=repair_entry.data.get(CONF_PORT, DEFAULT_PORT),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_USERNAME,
                        default=repair_entry.data.get(CONF_USERNAME, ""),
                    ): str,
                    vol.Optional(
                        CONF_PASSWORD,
                        default=repair_entry.data.get(CONF_PASSWORD, ""),
                    ): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "controller_name": repair_entry.data.get(
                    CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME
                ),
            },
        )

    def _is_duplicate_entry(self, ip: str, port: int, device_id: int = 1) -> bool:
        """Check if the IP + Port + Device ID combination already exists."""
        return any(
            entry.data.get(CONF_API_URL) == ip
            and entry.data.get(CONF_PORT, DEFAULT_PORT) == port
            and entry.data.get(CONF_DEVICE_ID, 1) == device_id
            for entry in self._async_current_entries()
        )

    def _build_config_data(self, ui: dict) -> dict:
        """Build the configuration data dictionary."""
        config_data = {
            CONF_API_URL: ui[CONF_API_URL],
            CONF_PORT: int(ui.get(CONF_PORT, DEFAULT_PORT)),
            CONF_USE_SSL: ui.get(CONF_USE_SSL, DEFAULT_USE_SSL),
            CONF_DEVICE_NAME: ui.get(CONF_DEVICE_NAME, "Pool Controller"),
            CONF_CONTROLLER_NAME: ui.get(CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME),
            CONF_USERNAME: ui.get(CONF_USERNAME) or None,
            CONF_PASSWORD: ui.get(CONF_PASSWORD) or None,
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
        return config_data

    async def _test_connection(self) -> bool:
        """Test the connection to the controller."""
        try:
            host = self._config_data[CONF_API_URL]
            port = self._config_data.get(CONF_PORT, DEFAULT_PORT)
            if port not in (80, 443):
                host = f"{host}:{port}"
            api = VioletPoolAPI(
                host=host,
                session=aiohttp_client.async_get_clientsession(self.hass),
                username=self._config_data.get(CONF_USERNAME),
                password=self._config_data.get(CONF_PASSWORD),
                use_ssl=self._config_data[CONF_USE_SSL],
                verify_ssl=self._config_data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                timeout=self._config_data[CONF_TIMEOUT_DURATION],
                max_retries=self._config_data[CONF_RETRY_ATTEMPTS],
            )
            await api.get_readings()
            self._config_data[CONF_DOSING_STANDALONE] = api.dosing_standalone
            return True
        except Exception:
            return False

    async def _get_grouped_sensors(self) -> dict[str, list[str]]:
        """Fetch and group sensors."""
        return await get_grouped_sensors(self.hass, self._config_data)

    async def _auto_configure_entities(self) -> ConfigFlowResult:
        """Auto-detect available features and sensors, then create entry."""
        sensor_data = await self._get_grouped_sensors()
        self._sensor_data = sensor_data
        detected_keys = {key for sensors in sensor_data.values() for key in sensors}
        self._config_data[CONF_ACTIVE_FEATURES] = self._detect_active_features(
            detected_keys
        )
        self._config_data[CONF_SELECTED_SENSORS] = list(detected_keys)

        return self.async_create_entry(
            title=self._generate_entry_title(),
            data=self._config_data,
        )

    def _detect_active_features(self, detected_keys: set[str]) -> list[str]:
        """Derive active features from controller data instead of user choices."""
        feature_ids = {str(feature["id"]) for feature in AVAILABLE_FEATURES}
        active: set[str] = set()

        if not detected_keys:
            return [str(feature["id"]) for feature in AVAILABLE_FEATURES if feature["default"]]

        feature_key_map = {
            "filter_control": ("PUMP", "PUMPSTATE", "PUMP_RUNTIME"),
            "solar": ("SOLAR", "SOLARSTATE", "SOLAR_RUNTIME", "onewire3", "onewire4"),
            "heating": ("HEATER", "HEATERSTATE", "HEATER_RUNTIME", "onewire5", "onewire6"),
            "led_lighting": ("LIGHT", "LIGHT_RUNTIME", "DMX_", "DMX_SCENE"),
            "ph_control": ("pH", "PH", "DOS_4_PHM", "DOS_5_PHP"),
            "chlorine_control": ("orp", "ORP", "pot", "DOS_1_CL", "DOS_2_ELO"),
            "flocculation": ("DOS_6_FLOC",),
            "cover_control": ("COVER", "COVER_STATE"),
            "backwash": ("BACKWASH", "BACKWASHRINSE"),
            "pv_surplus": ("PVSURPLUS",),
            "water_level": ("WATER_LEVEL", "LEVEL"),
            "water_refill": ("REFILL",),
            "digital_inputs": ("INPUT", "DIGITALINPUTRULE_STATE", "DIRULE_"),
            "extension_outputs": ("EXT1_", "EXT2_", "OMNI_DC"),
        }

        for feature_id, markers in feature_key_map.items():
            if feature_id in feature_ids and any(
                key.startswith(marker) or marker in key for key in detected_keys for marker in markers
            ):
                active.add(feature_id)

        return sorted(active)

    def _extract_active_features(self, ui: dict) -> list:
        """Extract active features from legacy user input."""
        return [
            feature["id"]
            for feature in AVAILABLE_FEATURES
            if ui.get(f"enable_{feature['id']}", feature["default"])
        ]

    def _generate_entry_title(self) -> str:
        """Generate the title for the config entry."""
        controller_name = self._config_data.get(
            CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME
        )
        pool_size = self._config_data.get(CONF_POOL_SIZE)
        return f"{controller_name} • {pool_size}m³"
