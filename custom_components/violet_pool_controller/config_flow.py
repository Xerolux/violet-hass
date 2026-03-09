"""Config flow for Violet Pool Controller integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.zeroconf import AsyncServiceInfo, info_from_service
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client, selector

from .api import VioletPoolAPI
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
    CONF_RETRY_ATTEMPTS,
    CONF_SELECTED_SENSORS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    DEFAULT_CONTROLLER_NAME,
    DEFAULT_DISINFECTION_METHOD,
    DEFAULT_ENABLE_DIAGNOSTIC_LOGGING,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_POOL_SIZE,
    DEFAULT_POOL_TYPE,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_USE_SSL,
    DOMAIN,
)
# Import refactored config flow modules
from .config_flow_utils import (
    constants,
    validators,
    get_grouped_sensors,
    MIN_POLLING_INTERVAL,
    MAX_POLLING_INTERVAL,
    MIN_TIMEOUT,
    MAX_TIMEOUT,
    MIN_RETRIES,
    MAX_RETRIES,
    MIN_DEVICE_ID,
    MAX_DEVICE_ID,
    MIN_POOL_SIZE,
    MAX_POOL_SIZE,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Config flow for Violet Pool Controller."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._config_data: dict[str, Any] = {}
        self._sensor_data: dict[str, list[str]] = {}
        self._reauth_entry: config_entries.ConfigEntry | None = None
        _LOGGER.info("Violet Pool Controller setup started")

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
        """
        Handle the user-initiated setup start step.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
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
                errors["base"] = constants.ERROR_ALREADY_CONFIGURED
                error_hints["base"] = (
                    "This controller is already configured. "
                    "Please check your integrations list."
                )
            elif not validators.validate_ip_address(user_input[CONF_API_URL]):
                errors[CONF_API_URL] = constants.ERROR_INVALID_IP
                error_hints[CONF_API_URL] = (
                    "Please enter a valid IP address (e.g., 192.168.1.100) or hostname."
                )
            else:
                self._config_data = self._build_config_data(user_input)
                await self.async_set_unique_id(
                    f"{self._config_data[CONF_API_URL]}-{self._config_data[CONF_DEVICE_ID]}"
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

            sensor_data = await self._get_grouped_sensors()
            self._sensor_data = sensor_data
            if not self._sensor_data:
                _LOGGER.warning(
                    "No dynamic sensors found. Skipping sensor selection."
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
                if isinstance(value, list) and value:
                    selected_sensors.extend(value)

            # Store selection directly. Empty list = no sensors selected.
            # None is reserved for legacy configs where it means "all sensors".
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
            if self._reauth_entry is None:
                return self.async_abort(reason="reauth_failed")
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

            errors["base"] = constants.ERROR_CANNOT_CONNECT

        # Show form with current values
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
                "api_url": self._reauth_entry.data.get(CONF_API_URL),
            },
        )

    async def async_step_zeroconf(
        self, discovery_info: AsyncServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery of a Violet Pool Controller.

        Args:
            discovery_info: The zeroconf service discovery info.

        Returns:
            The flow result.
        """
        # Convert AsyncServiceInfo to ZeroconfServiceInfo using helper
        service_info = info_from_service(discovery_info)
        if service_info is None:
            return self.async_abort(reason="invalid_discovery_info")
        
        host = str(service_info.ip_address)
        name = discovery_info.name

        _LOGGER.info(
            "Zeroconf discovery: Violet Pool Controller '%s' at %s", name, host
        )

        # Check if this host is already configured
        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured(
            updates={CONF_API_URL: host},
            reload_on_update=True,
        )

        # Store discovered info for the confirmation step
        self._config_data = {
            CONF_API_URL: host,
            CONF_USE_SSL: DEFAULT_USE_SSL,
            CONF_DEVICE_NAME: name.split(".")[0] if "." in name else name,
            CONF_CONTROLLER_NAME: DEFAULT_CONTROLLER_NAME,
            CONF_USERNAME: "",
            CONF_PASSWORD: "",
            CONF_DEVICE_ID: 1,
            CONF_POLLING_INTERVAL: DEFAULT_POLLING_INTERVAL,
            CONF_TIMEOUT_DURATION: DEFAULT_TIMEOUT_DURATION,
            CONF_RETRY_ATTEMPTS: DEFAULT_RETRY_ATTEMPTS,
        }

        self.context["title_placeholders"] = {
            "name": name,
            "host": host,
        }

        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm zeroconf discovered Violet Pool Controller.

        Args:
            user_input: The user input dictionary.

        Returns:
            The flow result.
        """
        if user_input is not None:
            if await self._test_connection():
                return await self.async_step_pool_setup()
            return self.async_show_form(
                step_id="zeroconf_confirm",
                description_placeholders=self.context.get("title_placeholders", {}),
                errors={"base": constants.ERROR_CANNOT_CONNECT},
            )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders=self.context.get("title_placeholders", {}),
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
        if reconfigure_entry is None:
            return self.async_abort(reason="reconfigure_failed")

        if user_input:
            # Validate IP address
            api_url = user_input.get(CONF_API_URL) or user_input.get("api_url")
            if not api_url or not validators.validate_ip_address(api_url):
                errors[CONF_API_URL] = constants.ERROR_INVALID_IP
            else:
                # Build updated config
                updated_data = dict(reconfigure_entry.data)
                updated_data[CONF_API_URL] = api_url
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

                errors["base"] = constants.ERROR_CANNOT_CONNECT

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
            api = VioletPoolAPI(
                host=self._config_data[CONF_API_URL],
                session=aiohttp_client.async_get_clientsession(self.hass),
                username=self._config_data.get(CONF_USERNAME),
                password=self._config_data.get(CONF_PASSWORD),
                use_ssl=self._config_data[CONF_USE_SSL],
                verify_ssl=True,
                timeout=self._config_data[CONF_TIMEOUT_DURATION],
                max_retries=self._config_data[CONF_RETRY_ATTEMPTS],
            )
            await api.get_readings()
            return True
        except Exception:
            return False

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
            "⚠️ **Sicherheitswarnung & Haftungsausschluss / Safety Warning & Liability Disclaimer**\n\n"
            "**🇩🇪 DEUTSCH:**\n\n"
            "Die Nutzung dieser Software-Integration erfolgt auf eigene Verantwortung und Gefahr. "
            "Diese Integration ermöglicht die Fernsteuerung von Poolausrüstung einschließlich Pumpen, "
            "Heizungen, Beleuchtung und chemischen Dosieranlagen.\n\n"
            "**Risiken beachten:** Falsche Konfiguration oder自动化fehler können zu Sachschäden, "
            "Verletzungen durch elektrischen Schlag, chemischen Überdosierungen oder anderen "
            "Gefährdungen führen.\n\n"
            "**Deine Verantwortung:**\n"
            "• Stelle sicher, dass du alle Schutzmechanismen verstehst\n"
            "• Halte jederzeit manuelle Not-Abschalter bereit\n"
            "• Beachte die Sicherheitsdatenblätter aller verwendeten Chemikalien\n"
            "• Befolge die Dokumentation deines Pool-Herstellers\n"
            "• Beachte lokale Vorschriften (DIN/EN Normen, Elektro- und Chemikalienrecht)\n"
            "• Überwache deine Anlage regelmäßig persönlich, auch bei aktiver Automation\n"
            "• Erstelle regelmäßige Backups deiner Konfiguration\n\n"
            "**Haftungsausschluss:**\n"
            "Der Entwickler dieser Integration übernimmt keinerlei Gewährleistung für die "
            "Funktionsfähigkeit, Sicherheit oder Vollständigkeit. Die Nutzung erfolgt auf "
            "eigenes Risiko. Der Entwickler ist nicht haftbar für Schäden jeder Art, einschließlich "
            "aber nicht beschränkt auf Sachschäden, Personenschäden oder finanzielle Verluste, "
            "die aus der Nutzung oder Nicht-Nutzung dieser Software resultieren.\n\n"
            "Dies ist eine Open-Source-Software ohne kommerzielle Garantien. Bei Unsicherheiten "
            "solltest du einen Fachbetrieb konsultieren.\n\n"
            "Durch Bestätigung erklärst du, dass du diese Warnung gelesen, verstanden und "
            "akzeptiert hast. Vollständige Hinweise findest du hier: {docs_de}\n\n"
            "---\n\n"
            "**🇬🇧 ENGLISH:**\n\n"
            "Use of this software integration is at your own risk and responsibility. "
            "This integration enables remote control of pool equipment including pumps, "
            "heaters, lighting and chemical dosing systems.\n\n"
            "**Risks involved:** Incorrect configuration or automation errors may cause "
            "property damage, injury from electric shock, chemical overdosing or other hazards.\n\n"
            "**Your responsibilities:**\n"
            "• Ensure you understand all safety mechanisms\n"
            "• Keep manual emergency shut-offs accessible at all times\n"
            "• Follow safety data sheets for all chemicals used\n"
            "• Comply with your pool manufacturer's documentation\n"
            "• Observe local regulations (DIN/EN standards, electrical and chemical laws)\n"
            "• Regularly monitor your installation personally, even with active automation\n"
            "• Create regular backups of your configuration\n\n"
            "**Disclaimer of liability:**\n"
            "The developer of this integration provides NO warranty regarding functionality, "
            "safety or completeness. Use is entirely at your own risk. The developer is not "
            "liable for any damages whatsoever, including but not limited to property damage, "
            "personal injury or financial loss resulting from use or non-use of this software.\n\n"
            "This is open-source software without commercial guarantees. Consult a professional "
            "if you are uncertain.\n\n"
            "By confirming, you acknowledge that you have read, understood and accepted this "
            "warning. Full details available at: {docs_en}"
        )
        return template.format(**self._get_help_links())

    def _get_help_links(self) -> dict[str, str]:
        """
        Get helper links.

        Returns:
            A dictionary of help links.
        """
        return {
            "docs_de": constants.HELP_DOC_DE_URL,
            "docs_en": constants.HELP_DOC_EN_URL,
            "github_url": constants.GITHUB_BASE_URL,
            "issues_url": constants.SUPPORT_URL,
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
                    "action", default=constants.MENU_ACTION_START
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value=constants.MENU_ACTION_START,
                                label="⚙️ Setup starten / Start setup",
                            ),
                            selector.SelectOptionDict(
                                value=constants.MENU_ACTION_HELP,
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
                    constants.POOL_TYPE_OPTIONS
                ),
                vol.Required(
                    CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD
                ): vol.In(constants.DISINFECTION_OPTIONS),
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
            # Create options with friendly names
            options = [
                selector.SelectOptionDict(
                    value=sensor,
                    label=validators.get_sensor_label(sensor),
                )
                for sensor in sensors
            ]

            # Pre-select ALL sensors so the user can see what they get
            # and explicitly deselect. This prevents confusion.
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
                "Features updated in options: %s", ", ".join(selected_features)
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
                "info": "Select the features you want to use. "
                "Disabled features will be hidden."
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
            selected_sensors = []
            for key, value in user_input.items():
                if key in self._sensor_data:  # key is a sensor group
                    if isinstance(value, list) and value:
                        selected_sensors.extend(value)

            self._updated_options[CONF_SELECTED_SENSORS] = selected_sensors

            if selected_sensors:
                _LOGGER.info(
                    "%d sensors saved in options", len(selected_sensors)
                )
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
                vol.Optional(
                    CONF_ENABLE_DIAGNOSTIC_LOGGING,
                    default=self.current_config.get(
                        CONF_ENABLE_DIAGNOSTIC_LOGGING, DEFAULT_ENABLE_DIAGNOSTIC_LOGGING
                    ),
                ): selector.BooleanSelector(
                    selector.BooleanSelectorConfig(),
                ),
                vol.Optional(
                    CONF_FORCE_UPDATE,
                    default=self.current_config.get(
                        CONF_FORCE_UPDATE, DEFAULT_FORCE_UPDATE
                    ),
                ): selector.BooleanSelector(
                    selector.BooleanSelectorConfig(),
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

        # None (legacy) means ALL sensors are selected.
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
