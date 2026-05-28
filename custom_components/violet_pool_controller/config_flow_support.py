"""Support classes for the Violet Pool Controller config flow."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import selector

from .const import (
    AVAILABLE_FEATURES,
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_DISINFECTION_METHOD,
    CONF_ENABLE_DIAGNOSTIC_LOGGING,
    CONF_FORCE_UPDATE,
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
    DEFAULT_DISINFECTION_METHOD,
    DEFAULT_ENABLE_DIAGNOSTIC_LOGGING,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_POOL_SIZE,
    DEFAULT_POOL_TYPE,
    DEFAULT_PORT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_USE_SSL,
    DEFAULT_VERIFY_SSL,
)
from .config_flow_utils import (
    MAX_DEVICE_ID,
    MAX_POLLING_INTERVAL,
    MAX_POOL_SIZE,
    MAX_RETRIES,
    MAX_TIMEOUT,
    MIN_DEVICE_ID,
    MIN_POLLING_INTERVAL,
    MIN_POOL_SIZE,
    MIN_RETRIES,
    MIN_TIMEOUT,
    constants,
    get_grouped_sensors,
    validators,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlowTextMixin:
    """Shared text and link helpers for the config flow."""

    def _get_disclaimer_text(self) -> str:
        """Get the disclaimer text."""
        template = (
            "⚠️ **Safety Warning & Liability Disclaimer**\n\n"
            "Use of this software integration is at your own risk and responsibility. "
            "This integration enables remote control of pool equipment"
            " including pumps, "
            "heaters, lighting and chemical dosing systems.\n\n"
            "**Risks involved:** Incorrect configuration or automation"
            " errors may cause "
            "property damage, injury from electric shock, chemical overdosing or other "
            "hazards.\n\n"
            "**Your responsibilities:**\n"
            "• Ensure you understand all safety mechanisms\n"
            "• Keep manual emergency shut-offs accessible at all times\n"
            "• Follow safety data sheets for all chemicals used\n"
            "• Comply with your pool manufacturer's documentation\n"
            "• Observe local regulations"
            " (DIN/EN standards, electrical and chemical laws)\n"
            "• Regularly monitor your installation personally,"
            " even with active automation\n"
            "• Create regular backups of your configuration\n\n"
            "**Disclaimer of liability:**\n"
            "The developer of this integration provides NO warranty regarding "
            "functionality, safety or completeness. Use is entirely at your own risk. "
            "The developer is not liable for any damages whatsoever, including but not "
            "limited to property damage, personal injury or financial loss"
            " resulting from "
            "use or non-use of this software.\n\n"
            "This is open-source software without commercial guarantees."
            " Consult a professional if you are uncertain.\n\n"
            "By confirming, you acknowledge that you have read,"
            " understood and accepted "
            "this warning. Full details available at:"
            " {docs_en}"
        )
        return template.format(**self._get_help_links())

    def _get_help_links(self) -> dict[str, str]:
        """Get helper links."""
        return {
            "docs_en": constants.HELP_DOC_EN_URL,
            "github_url": constants.GITHUB_BASE_URL,
            "issues_url": constants.SUPPORT_URL,
        }


class ConfigFlowSchemaMixin:
    """Schema helpers for the primary config flow."""

    def _get_main_menu_schema(self) -> vol.Schema:
        """Get the main menu schema."""
        return vol.Schema(
            {
                vol.Required(
                    "action", default=constants.MENU_ACTION_START
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value=constants.MENU_ACTION_START,
                                label="⚙️ Start setup",
                            ),
                            selector.SelectOptionDict(
                                value=constants.MENU_ACTION_HELP,
                                label="📘 Help & documentation",
                            ),
                        ]
                    )
                )
            }
        )

    def _get_connection_schema(self) -> vol.Schema:
        """Get the connection schema."""
        return vol.Schema(
            {
                vol.Required(CONF_API_URL, default=""): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=65535,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
                vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
                vol.Required(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
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
        """Get the pool setup schema."""
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
                    constants.POOL_TYPE_OPTIONS
                ),
                vol.Required(
                    CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD
                ): vol.In(constants.DISINFECTION_OPTIONS),
            }
        )

    def _get_feature_selection_schema(self) -> vol.Schema:
        """Get the feature selection schema."""
        return vol.Schema(
            {
                vol.Optional(f"enable_{f['id']}", default=f["default"]): bool
                for f in AVAILABLE_FEATURES
            }
        )

    def _get_sensor_selection_schema(self) -> vol.Schema:
        """Create the sensor selection schema."""
        schema = {}
        for group, sensors in self._sensor_data.items():
            options = [
                selector.SelectOptionDict(
                    value=sensor,
                    label=validators.get_sensor_label(sensor),
                )
                for sensor in sensors
            ]
            schema[vol.Optional(group, default=sensors)] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=options,
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        return vol.Schema(schema)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Violet Pool Controller."""

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
        """Handle the initial options menu."""
        if user_input is not None:
            choice = user_input.get("config_option", "settings")
            if choice == "features":
                return await self.async_step_features()
            if choice == "sensors":
                return await self.async_step_sensors()
            return await self.async_step_settings()

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
                                    label="🎛️ Enable/disable features",
                                ),
                                selector.SelectOptionDict(
                                    value="sensors", label="📊 Select sensors"
                                ),
                                selector.SelectOptionDict(
                                    value="settings", label="⚙️ Change settings"
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
        """Handle feature selection in options flow."""
        if user_input is not None:
            selected_features = user_input.get(CONF_ACTIVE_FEATURES, [])
            self._updated_options[CONF_ACTIVE_FEATURES] = selected_features
            _LOGGER.info(
                "Features updated in options: %s", ", ".join(selected_features)
            )
            final_options = {**self.current_config, **self._updated_options}
            return self.async_create_entry(title="", data=final_options)

        current_features = self.current_config.get(CONF_ACTIVE_FEATURES, [])
        feature_options = []
        for feature in AVAILABLE_FEATURES:
            feature_id = str(feature["id"])
            if feature_id in constants.ENHANCED_FEATURES:
                info = constants.ENHANCED_FEATURES[feature_id]
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
                "info": (
                    "Select the features you want to use."
                    " Disabled features will be hidden."
                ),
            },
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle sensor selection in options flow."""
        if user_input is not None:
            selected_sensors = []
            for key, value in user_input.items():
                if key in self._sensor_data and isinstance(value, list) and value:
                    selected_sensors.extend(value)

            self._updated_options[CONF_SELECTED_SENSORS] = selected_sensors
            if selected_sensors:
                _LOGGER.info("%d sensors saved in options", len(selected_sensors))
            else:
                _LOGGER.info("No sensors selected in options.")

            final_options = {**self.current_config, **self._updated_options}
            return self.async_create_entry(title="", data=final_options)

        self._sensor_data = await self._get_grouped_sensors()
        return self.async_show_form(
            step_id="sensors",
            data_schema=self._get_sensor_schema(),
        )

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle general settings in options flow."""
        if user_input is not None:
            self._updated_options.update(user_input)
            final_options = {**self.current_config, **self._updated_options}
            return self.async_create_entry(title="", data=final_options)

        return self.async_show_form(
            step_id="settings",
            data_schema=self._get_settings_schema(),
        )

    async def _get_grouped_sensors(self) -> dict[str, list[str]]:
        """Fetch sensors for the options flow."""
        return await get_grouped_sensors(self.hass, self.current_config)

    def _get_settings_schema(self) -> vol.Schema:
        """Get the schema for general settings."""
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
                vol.Optional(
                    CONF_ENABLE_DIAGNOSTIC_LOGGING,
                    default=self.current_config.get(
                        CONF_ENABLE_DIAGNOSTIC_LOGGING,
                        DEFAULT_ENABLE_DIAGNOSTIC_LOGGING,
                    ),
                ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
                vol.Optional(
                    CONF_FORCE_UPDATE,
                    default=self.current_config.get(
                        CONF_FORCE_UPDATE, DEFAULT_FORCE_UPDATE
                    ),
                ): selector.BooleanSelector(selector.BooleanSelectorConfig()),
            }
        )

    def _get_sensor_schema(self) -> vol.Schema:
        """Get the schema for sensor selection."""
        schema = {}
        stored_sensors = self.current_config.get(CONF_SELECTED_SENSORS)
        is_all_selected = stored_sensors is None

        for group, sensors in self._sensor_data.items():
            options = [
                selector.SelectOptionDict(
                    value=sensor,
                    label=validators.get_sensor_label(sensor),
                )
                for sensor in sensors
            ]

            if is_all_selected:
                default_selection = sensors
            else:
                default_selection = [
                    sensor
                    for sensor in sensors
                    if stored_sensors and sensor in stored_sensors
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
