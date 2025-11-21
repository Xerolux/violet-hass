"""Config flow for Violet Pool Controller."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import VioletPoolAPI, VioletPoolAPIError
from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_USE_SSL,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_CONTROLLER_NAME,
    CONF_POOL_SIZE,
    CONF_POLLING_INTERVAL,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_ACTIVE_FEATURES,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_POOL_SIZE,
    DEFAULT_POLLING_INTERVAL,
    AVAILABLE_FEATURES,
)
from .error_codes import async_get_error_message
from .const_sensors import (
    ANALOG_SENSORS,
    RUNTIME_SENSORS,
    SYSTEM_SENSORS,
    TEMP_SENSORS,
    TIMESTAMP_SENSORS,
    WATER_CHEM_SENSORS,
)

_LOGGER = logging.getLogger(__name__)

DEVICE_MODEL_NAME = "Violet Pool Controller"
ERROR_INVALID_AUTH = "invalid_auth"
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_UNKNOWN = "unknown"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


async def _async_get_sensor_data() -> dict[str, list[str]]:
    """Fetch available sensor keys grouped by category."""

    return {
        "temperature_sensors": list(TEMP_SENSORS.keys()),
        "water_chemistry": list(WATER_CHEM_SENSORS.keys()),
        "analog_sensors": list(ANALOG_SENSORS.keys()),
        "system_sensors": list(SYSTEM_SENSORS.keys()),
        "runtime_sensors": list(RUNTIME_SENSORS.keys()),
        "timestamp_sensors": list(TIMESTAMP_SENSORS.keys()),
    }


# =============================================================================
# SCHEMA DEFINITIONS
# =============================================================================

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME, default=""): str,
        vol.Optional(CONF_PASSWORD, default=""): str,
        vol.Optional(CONF_USE_SSL, default=False): bool,
        vol.Optional(CONF_TIMEOUT_DURATION, default=DEFAULT_TIMEOUT_DURATION): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=60)
        ),
        vol.Optional(CONF_RETRY_ATTEMPTS, default=DEFAULT_RETRY_ATTEMPTS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=10)
        ),
        vol.Optional(CONF_POOL_SIZE, default=DEFAULT_POOL_SIZE): vol.All(
            vol.Coerce(float), vol.Range(min=0.1, max=1000.0)
        ),
        vol.Optional(
            CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
        ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
    }
)


# =============================================================================
# CONFIG FLOW
# =============================================================================


class VioletPoolControllerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Violet Pool Controller."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self.config_data: dict[str, Any] = {}
        self._sensor_data: dict[str, Any] = {}

    # --------------------------------------------------------------------------
    # Step 1: User Input (Connection Details)
    # --------------------------------------------------------------------------

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            username = user_input.get(CONF_USERNAME, "")
            password = user_input.get(CONF_PASSWORD, "")
            use_ssl = user_input.get(CONF_USE_SSL, False)
            timeout = user_input.get(CONF_TIMEOUT_DURATION)
            retries = user_input.get(CONF_RETRY_ATTEMPTS)

            self.config_data = {**user_input}
            self.config_data[CONF_API_URL] = f"{'https' if use_ssl else 'http'}://{host}"

            # Check connection to the API
            try:
                await self._async_test_connection(
                    host=host,
                    username=username,
                    password=password,
                    use_ssl=use_ssl,
                    timeout=timeout,
                    retries=retries,
                )
            except VioletPoolAPIError as e:
                _LOGGER.warning("Connection failed: %s", e)
                if e.error_code == "invalid_auth":
                    errors["base"] = ERROR_INVALID_AUTH
                elif e.error_code == "cannot_connect":
                    errors["base"] = ERROR_CANNOT_CONNECT
                else:
                    errors["base"] = ERROR_UNKNOWN
            except Exception as e:  # Catch unexpected errors
                _LOGGER.exception("Unexpected error during connection test: %s", e)
                errors["base"] = ERROR_UNKNOWN

            if not errors:
                # Connection successful, proceed to feature selection
                return await self.async_step_features()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    # --------------------------------------------------------------------------
    # Step 2: Feature Selection
    # --------------------------------------------------------------------------

    async def async_step_features(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step for selecting active features (switches, climate, cover, etc.)."""
        if user_input is not None:
            # Filter "enable_" fields to build CONF_ACTIVE_FEATURES
            active_features = [
                feature_id
                for key, enabled in user_input.items()
                if key.startswith("enable_") and enabled
                for feature_id in [key[7:]]  # Remove "enable_" prefix
            ]

            self.config_data[CONF_ACTIVE_FEATURES] = active_features

            # Proceed to sensor selection
            return await self.async_step_sensors()

        # Show form for feature selection
        return self.async_show_form(
            step_id="features", data_schema=self._get_feature_selection_schema()
        )

    # --------------------------------------------------------------------------
    # Step 3: Sensor Selection
    # --------------------------------------------------------------------------

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step for selecting which sensors to show."""
        errors: dict[str, str] = {}

        if not self._sensor_data:
            # Fetch available sensors and their keys
            try:
                self._sensor_data = await _async_get_sensor_data()
            except VioletPoolAPIError as e:
                errors["base"] = async_get_error_message(e.error_code)
                # On API error, return to the user step (likely auth issue)
                return self.async_show_form(
                    step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
                )
            except Exception:
                errors["base"] = ERROR_UNKNOWN
                return self.async_show_form(
                    step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
                )

        if user_input is not None:
            # user_input contains selected sensor keys grouped by group name
            selected_sensors: list[str] = []
            for group, keys in user_input.items():
                selected_sensors.extend(keys)

            # Store final list of all sensor keys in the configuration
            self.config_data["selected_sensors"] = selected_sensors

            # Proceed to finish step
            return self.async_step_finish()

        # Show form for sensor selection
        return self.async_show_form(
            step_id="sensors", data_schema=self._get_sensor_selection_schema()
        )

    # --------------------------------------------------------------------------
    # Step 4: Finish (Final Details & Create Entry)
    # --------------------------------------------------------------------------

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step for entering the final device name and completing the flow."""

        # Generate a standardized default device name
        default_name = f"{DEVICE_MODEL_NAME} {self.config_data.get(CONF_DEVICE_ID, '1')}"

        finish_schema = vol.Schema(
            {
                # CONF_CONTROLLER_NAME is used for UI display
                vol.Required(CONF_CONTROLLER_NAME, default=default_name): str,
                # CONF_DEVICE_NAME is the underlying device name (e.g. for logs)
                vol.Optional(CONF_DEVICE_NAME, default=default_name): str,
            }
        )

        if user_input is not None:
            # Merge final names into configuration
            self.config_data.update(user_input)

            # Config entry is created; unique_id was already set in _async_test_connection
            return self.async_create_entry(
                title=self.config_data[CONF_CONTROLLER_NAME],
                data=self.config_data,
            )

        return self.async_show_form(step_id="finish", data_schema=finish_schema)

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def _get_feature_selection_schema(self) -> vol.Schema:
        """Create the schema for feature selection (fixed version)."""
        feature_schema: dict[Any, Any] = {}

        # Use explicit loop so voluptuous correctly registers dynamic keys
        for f in AVAILABLE_FEATURES:
            key_name = f"enable_{f['id']}"
            default_value = f.get("default", False)

            feature_schema[vol.Optional(key_name, default=default_value)] = bool

        return vol.Schema(feature_schema)

    def _get_sensor_selection_schema(self) -> vol.Schema:
        """Create the schema for sensor selection (fixed version)."""
        schema: dict[Any, Any] = {}

        for group, sensors in self._sensor_data.items():
            # Each group is a multi-select over its sensor keys.
            # Using cv.multi_select so voluptuous-serialize can build the UI
            # representation without raising conversion errors.
            schema[vol.Optional(group, default=sensors)] = cv.multi_select(sensors)

        return vol.Schema(schema)

    async def _async_test_connection(
        self,
        host: str,
        username: str,
        password: str,
        use_ssl: bool,
        timeout: int,
        retries: int,
    ) -> None:
        """Test the connection to the API and fetch device details."""

        test_api = VioletPoolAPI(
            host=host,
            session=async_get_clientsession(self.hass),
            username=username,
            password=password,
            use_ssl=use_ssl,
            timeout=timeout,
            max_retries=retries,
        )

        try:
            # Call a simple authenticated endpoint to verify auth/connection
            device_info = await test_api.get_device_info()

            # Store data discovered during the test for the config entry
            self.config_data[CONF_DEVICE_ID] = device_info.get("device_id", 1)
            self.config_data[CONF_DEVICE_NAME] = device_info.get(
                "device_name", "Violet Pool Controller"
            )

            # Ensure uniqueness based on HOST + DEVICE_ID
            unique_id = f"{host}_{self.config_data[CONF_DEVICE_ID]}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            _LOGGER.info(
                "Connection successful. Detected device ID: %s, name: %s",
                self.config_data[CONF_DEVICE_ID],
                self.config_data[CONF_DEVICE_NAME],
            )

        except VioletPoolAPIError as e:
            _LOGGER.error("API connection test failed: %s", e)
            raise
        except Exception as e:
            _LOGGER.exception("Unexpected error during connection test")
            raise VioletPoolAPIError(f"Unexpected error: {e}", "unexpected_error")

    # =============================================================================
    # OPTIONS FLOW
    # =============================================================================

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return VioletPoolControllerOptionsFlow(config_entry)


class VioletPoolControllerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Violet Pool Controller."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self.config = dict(config_entry.data)
        self._sensor_data: dict[str, Any] = {}

    # --------------------------------------------------------------------------
    # Step 1: Options (Polling, Timeout, Retries)
    # --------------------------------------------------------------------------

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial options step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.options.update(user_input)

            # Proceed to feature selection options
            return await self.async_step_options_features()

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_POLLING_INTERVAL,
                    default=self.options.get(
                        CONF_POLLING_INTERVAL,
                        self.config.get(
                            CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL
                        ),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                vol.Optional(
                    CONF_TIMEOUT_DURATION,
                    default=self.options.get(
                        CONF_TIMEOUT_DURATION,
                        self.config.get(
                            CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION
                        ),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
                vol.Optional(
                    CONF_RETRY_ATTEMPTS,
                    default=self.options.get(
                        CONF_RETRY_ATTEMPTS,
                        self.config.get(
                            CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS
                        ),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            }
        )

        # Show the options form
        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )

    # --------------------------------------------------------------------------
    # Step 2: Options Feature Selection
    # --------------------------------------------------------------------------

    async def async_step_options_features(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Options step for selecting active features."""

        if user_input is not None:
            active_features = [
                feature_id
                for key, enabled in user_input.items()
                if key.startswith("enable_") and enabled
                for feature_id in [key[7:]]
            ]

            self.options[CONF_ACTIVE_FEATURES] = active_features

            # Proceed to sensor selection options
            return await self.async_step_options_sensors()

        current_active_features = self.options.get(
            CONF_ACTIVE_FEATURES, self.config.get(CONF_ACTIVE_FEATURES, [])
        )

        options_schema = self._get_options_feature_selection_schema(
            current_active_features
        )

        return self.async_show_form(
            step_id="options_features", data_schema=options_schema
        )

    # --------------------------------------------------------------------------
    # Step 3: Options Sensor Selection
    # --------------------------------------------------------------------------

    async def async_step_options_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Options step for selecting sensors."""

        if not self._sensor_data:
            # Reuse the shared helper to determine sensor data
            self._sensor_data = await _async_get_sensor_data()

        if user_input is not None:
            selected_sensors: list[str] = []
            for group, keys in user_input.items():
                selected_sensors.extend(keys)

            self.options["selected_sensors"] = selected_sensors

            # Create options entry and finish
            return self.async_create_entry(title="", data=self.options)

        current_selected_sensors = self.options.get(
            "selected_sensors", self.config.get("selected_sensors", [])
        )

        options_schema = self._get_options_sensor_selection_schema(
            current_selected_sensors
        )

        return self.async_show_form(
            step_id="options_sensors", data_schema=options_schema
        )

    # --------------------------------------------------------------------------
    # Options Helpers
    # --------------------------------------------------------------------------

    def _get_options_feature_selection_schema(
        self, current_active_features: list[str]
    ) -> vol.Schema:
        """Create the schema for feature selection (options flow)."""
        feature_schema: dict[Any, Any] = {}

        for f in AVAILABLE_FEATURES:
            key_name = f"enable_{f['id']}"
            is_active = f["id"] in current_active_features
            feature_schema[vol.Optional(key_name, default=is_active)] = bool

        return vol.Schema(feature_schema)

    def _get_options_sensor_selection_schema(
        self, current_selected_sensors: list[str]
    ) -> vol.Schema:
        """Create the schema for sensor selection (options flow)."""
        schema: dict[Any, Any] = {}

        for group, available_sensors in self._sensor_data.items():
            # Preselect currently selected sensors in this group
            default_selection = [
                key for key in available_sensors if key in current_selected_sensors
            ]

            # If none selected, default to all available
            if not default_selection:
                default_selection = available_sensors

            schema[vol.Optional(group, default=default_selection)] = cv.multi_select(
                available_sensors
            )

        return vol.Schema(schema)


# EOF
