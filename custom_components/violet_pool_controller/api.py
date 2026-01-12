"""HTTP client utilities for the Violet Pool Controller."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Mapping
from urllib.parse import quote, urlparse, urlunparse

import aiohttp

from .const import (
    ACTION_ALLAUTO,
    ACTION_ALLOFF,
    ACTION_ALLON,
    ACTION_COLOR,
    ACTION_LOCK,
    ACTION_OFF,
    ACTION_ON,
    ACTION_PUSH,
    ACTION_UNLOCK,
    API_GET_CALIB_HISTORY,
    API_GET_CALIB_RAW_VALUES,
    API_GET_CONFIG,
    API_GET_HISTORY,
    API_GET_OUTPUT_STATES,
    API_GET_OVERALL_DOSING,
    API_GET_WEATHER_DATA,
    API_PRIORITY_NORMAL,
    API_READINGS,
    API_RESTORE_CALIBRATION,
    API_SET_CONFIG,
    API_SET_DOSING_PARAMETERS,
    API_SET_FUNCTION_MANUALLY,
    API_SET_OUTPUT_TESTMODE,
    API_SET_TARGET_VALUES,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEVICE_PARAMETERS,
    DOSING_FUNCTIONS,
    TARGET_MIN_CHLORINE,
    TARGET_ORP,
    TARGET_PH,
)
from .utils_rate_limiter import get_global_rate_limiter

_LOGGER = logging.getLogger(__name__)


class VioletPoolAPIError(Exception):
    """Raised when the Violet Pool Controller API returns an error."""


class VioletPoolAPI:
    """A small HTTP client for interacting with the Violet Pool Controller.

    This class handles API requests, including authentication, rate limiting,
    and error handling. It provides methods for accessing various controller
    endpoints.
    """

    def __init__(
        self,
        *,
        host: str,
        session: aiohttp.ClientSession,
        username: str | None = None,
        password: str | None = None,
        use_ssl: bool = False,
        timeout: int = DEFAULT_TIMEOUT_DURATION,
        max_retries: int = DEFAULT_RETRY_ATTEMPTS,
    ) -> None:
        """Initializes the API helper.

        Args:
            host: The hostname or IP address of the controller.
            session: The aiohttp client session.
            username: The username for authentication.
            password: The password for authentication.
            use_ssl: Whether to use SSL for the connection.
            timeout: The request timeout in seconds.
            max_retries: The maximum number of retries for failed requests.
        """
        if session is None:
            raise ValueError("A valid aiohttp session must be provided")

        self._base_url = self._build_secure_base_url(host, use_ssl).rstrip("/")

        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=max(float(timeout), 1.0))
        self._max_retries = max(1, int(max_retries))
        self._auth = None
        if username:
            self._auth = aiohttp.BasicAuth(username, password or "")

        # Rate limiting to protect the controller from being overloaded
        self._rate_limiter = get_global_rate_limiter()
        _LOGGER.debug("API initialized with rate limiting enabled")

    # ---------------------------------------------------------------------
    # Generic helpers
    # ---------------------------------------------------------------------

    def _build_secure_base_url(self, host: str, use_ssl: bool) -> str:
        """Securely construct base URL with comprehensive validation."""
        # Strip existing protocols to prevent override
        host = host.strip()
        if host.startswith(("http://", "https://")):
            parsed = urlparse(host)
            host = parsed.netloc
        
        # Validate hostname format
        if not re.match(r'^[a-zA-Z0-9.-]+$', host):
            raise ValueError(f"Invalid hostname format: {host}")
        
        # SSRF Protection - Block private networks in production
        if any(host.startswith(prefix) for prefix in ['127.', '192.168.', '10.', '172.', '169.254.']):
            _LOGGER.warning("Connection to private network blocked: %s", host)
            raise ValueError("Connection to private networks not allowed")
        
        # Additional validation
        if len(host) > 253 or '..' in host or '//' in host:
            raise ValueError(f"Invalid hostname: {host}")
        
        protocol = "https" if use_ssl else "http"
        return urlunparse((protocol, host, "", "", "", ""))

    def _build_url(self, endpoint: str) -> str:
        """Constructs the full URL for a given endpoint.

        Args:
            endpoint: The API endpoint.

        Returns:
            The full URL.
        """
        endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"{self._base_url}{endpoint}"

    async def _request(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        params: Mapping[str, Any] | None = None,
        query: str | None = None,
        json_payload: Any | None = None,
        expect_json: bool = False,
        priority: int = API_PRIORITY_NORMAL,
    ) -> Any:
        """Performs a request with rate limiting, retries, and error handling.

        This method automatically waits if the request limit is reached.

        Args:
            endpoint: The API endpoint to request.
            method: The HTTP method to use.
            params: A mapping of URL parameters.
            query: A raw query string.
            json_payload: The JSON payload for POST requests.
            expect_json: Whether to expect a JSON response.
            priority: The request priority for rate limiting.

        Returns:
            The API response, either as JSON or text.

        Raises:
            VioletPoolAPIError: If the API returns an error or the request fails.
        """
        if params and query:
            raise ValueError("'params' and 'query' are mutually exclusive")

        # Wait if the rate limit is reached
        try:
            await self._rate_limiter.wait_if_needed(priority=priority, timeout=10.0)
        except asyncio.TimeoutError:
            _LOGGER.warning(
                "Rate limiter timeout for %s (priority: %d) - continuing",
                endpoint,
                priority,
            )

        url = self._build_url(endpoint)
        if query:
            url = f"{url}?{query}"

        last_error: VioletPoolAPIError | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                async with self._session.request(
                    method,
                    url,
                    params=params,
                    json=json_payload,
                    auth=self._auth,
                    timeout=self._timeout,
                ) as response:
                    if response.status >= 400:
                        body = await response.text()
                        raise VioletPoolAPIError(
                            f"HTTP {response.status} for {endpoint}: {body.strip()}"
                        )

                    if expect_json:
                        try:
                            return await response.json(content_type=None)
                        except (aiohttp.ContentTypeError, json.JSONDecodeError) as err:
                            body = await response.text()
                            raise VioletPoolAPIError(
                                f"Invalid JSON payload for {endpoint}: {body.strip()}"
                            ) from err

                    return await response.text()

            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                last_error = VioletPoolAPIError(
                    f"Error communicating with Violet controller: {err}"
                )
                _LOGGER.debug("Attempt %d for %s failed: %s", attempt, endpoint, err)
                if attempt == self._max_retries:
                    raise last_error
                # Exponential backoff with jitter
                delay = min(2.0, 0.2 * (2 ** (attempt - 1)))
                await asyncio.sleep(delay)

        # If we reach here, all retries succeeded but returned no data
        # This should not happen in normal operation
        raise VioletPoolAPIError("Request completed but returned no data")

    @staticmethod
    def _command_result(body: str) -> dict[str, Any]:
        """Normalizes the controller's response for command-style requests.

        Args:
            body: The raw response body.

        Returns:
            A dictionary indicating success and the response text.
        """
        text = (body or "").strip()
        success = not text or "error" not in text.lower()
        return {"success": success, "response": text}

    def _build_manual_command(
        self,
        key: str,
        action: str,
        *,
        duration: int | float | None = None,
        last_value: int | float | None = None,
    ) -> str:
        """Renders the command payload based on the device parameter template.

        Args:
            key: The device key.
            action: The action to perform (e.g., ON, OFF).
            duration: The duration for the action.
            last_value: The last value (e.g., speed).

        Returns:
            The formatted command payload.

        Raises:
            VioletPoolAPIError: If the template is misconfigured.
        """
        from typing import cast

        template = cast(
            str,
            DEVICE_PARAMETERS.get(key, {}).get(
                "api_template", f"{key},{{action}},{{duration}},{{value}}"
            ),
        )
        payload_data = {
            "action": action,
            "duration": int(duration or 0),
            "speed": int(last_value or 0),
            "value": int(last_value or 0),
        }
        try:
            return template.format_map(payload_data)
        except KeyError as err:
            raise VioletPoolAPIError(
                f"Template for {key} requires missing field: {err.args[0]}"
            ) from err

    # ---------------------------------------------------------------------
    # Public API surface
    # ---------------------------------------------------------------------

    async def get_readings(self) -> dict[str, Any]:
        """Returns the complete dataset from the controller.

        Returns:
            A dictionary containing all readings.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.
        """
        response = await self._request(
            API_READINGS,
            params={"ALL": ""},
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getReadings")
        return response

    async def get_specific_readings(
        self, categories: list[str] | tuple[str, ...]
    ) -> dict[str, Any]:
        """Returns a reduced dataset for the provided categories.

        Args:
            categories: A list or tuple of category strings to fetch.

        Returns:
            A dictionary containing the requested readings.

        Raises:
            VioletPoolAPIError: If no categories are provided or the payload is unexpected.
        """
        if not categories:
            raise VioletPoolAPIError("At least one category must be provided")

        query = ",".join(category.strip() for category in categories if category)
        if not query:
            raise VioletPoolAPIError("No valid categories provided")

        response = await self._request(
            API_READINGS,
            query=query,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getReadings")
        return response

    async def get_history(
        self, *, hours: int = 24, sensor: str = "ALL"
    ) -> dict[str, Any]:
        """Fetches historical readings from the controller.

        Args:
            hours: The number of hours of history to fetch.
            sensor: The specific sensor to fetch history for, or "ALL".

        Returns:
            A dictionary containing the history data.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.
        """
        safe_hours = max(1, int(hours))
        params = {"hours": safe_hours, "sensor": sensor or "ALL"}
        response = await self._request(
            API_GET_HISTORY,
            params=params,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getHistory")
        return response

    async def get_weather_data(self) -> dict[str, Any]:
        """Returns the current weather information used by the controller.

        Returns:
            A dictionary containing weather data.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.
        """
        response = await self._request(
            API_GET_WEATHER_DATA,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getWeatherdata")
        return response

    async def get_overall_dosing(self) -> dict[str, Any]:
        """Returns aggregated dosing statistics.

        Returns:
            A dictionary containing overall dosing statistics.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.
        """
        response = await self._request(
            API_GET_OVERALL_DOSING,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError(
                "Unexpected payload returned from getOverallDosing"
            )
        return response

    async def get_output_states(self) -> dict[str, Any]:
        """Returns detailed information about output states.

        Returns:
            A dictionary containing output states.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.
        """
        response = await self._request(
            API_GET_OUTPUT_STATES,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getOutputstates")
        return response

    async def get_config(
        self, parameters: list[str] | tuple[str, ...]
    ) -> dict[str, Any]:
        """Fetches controller configuration values for the provided keys.

        Args:
            parameters: A list or tuple of configuration keys to fetch.

        Returns:
            A dictionary containing the configuration values.

        Raises:
            VioletPoolAPIError: If no keys are provided or the payload is unexpected.
        """
        if not parameters:
            raise VioletPoolAPIError("At least one configuration key is required")

        query = ",".join(param.strip() for param in parameters if param)
        if not query:
            raise VioletPoolAPIError("No valid configuration keys provided")

        response = await self._request(
            API_GET_CONFIG,
            query=query,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getConfig")
        return response

async def set_config(self, config: Mapping[str, Any]) -> dict[str, Any]:
        """Updates controller configuration values.

        Args:
            config: A mapping of configuration keys and values to update.

        Returns:
            A dictionary with command result.

        Raises:
            VioletPoolAPIError: If configuration payload is empty.
        """
if not config:
            raise VioletPoolAPIError("Configuration payload must not be empty")
        
        # Sanitize all configuration parameters
        sanitized_config = {}
        from .utils_sanitizer import InputSanitizer
        
        for key, value in config.items():
            try:
                sanitized_key = InputSanitizer.validate_api_parameter(str(key))
                
                if isinstance(value, str):
                    sanitized_value = InputSanitizer.sanitize_string(
                        value, 
                        max_length=1000, 
                        escape_html=True
                    )
                elif isinstance(value, (int, float)):
                    sanitized_value = InputSanitizer.sanitize_numeric(value)
                else:
                    sanitized_value = InputSanitizer.sanitize_string(str(value))
                
                sanitized_config[sanitized_key] = sanitized_value
                
            except ValueError as err:
                _LOGGER.error("Invalid config parameter %s: %s", key, err)
                raise VioletPoolAPIError(f"Invalid configuration parameter: {key}") from err
        
        body = await self._request(
            API_SET_CONFIG,
            method="POST",
            json_payload=sanitized_config,
        )
        return self._command_result(body)

    async def get_calibration_raw_values(self) -> dict[str, Any]:
        """Returns the current raw values for all calibration sensors.

        Returns:
            A dictionary containing raw calibration values.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.
        """
        response = await self._request(
            API_GET_CALIB_RAW_VALUES,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError(
                "Unexpected payload returned from getCalibRawValues"
            )
        return response

    async def get_calibration_history(self, sensor: str) -> list[dict[str, str]]:
        """Returns the calibration history for the provided sensor.

        Args:
            sensor: The name of the sensor.

        Returns:
            A list of dictionaries representing the history entries.

        Raises:
            VioletPoolAPIError: If the sensor name is missing.
        """
        if not sensor:
            raise VioletPoolAPIError("Sensor name required for calibration history")

        response = await self._request(
            API_GET_CALIB_HISTORY,
            query=sensor,
            expect_json=False,
        )

        entries: list[dict[str, str]] = []
        for line in (response or "").strip().splitlines():
            parts = [part.strip() for part in line.split("|")]
            if len(parts) >= 3:
                entries.append(
                    {
                        "timestamp": parts[0],
                        "value": parts[1],
                        "type": parts[2],
                    }
                )
        return entries

    async def restore_calibration(self, sensor: str, timestamp: str) -> dict[str, Any]:
        """Restores a previous calibration entry for the given sensor.

        Args:
            sensor: The name of the sensor.
            timestamp: The timestamp of the calibration to restore.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the sensor or timestamp is missing.
        """
        if not sensor or not timestamp:
            raise VioletPoolAPIError(
                "Sensor and timestamp are required for calibration restore"
            )

        body = await self._request(
            API_RESTORE_CALIBRATION,
            method="POST",
            json_payload={"sensor": sensor, "timestamp": timestamp},
        )
        return self._command_result(body)

    async def set_output_test_mode(
        self,
        *,
        output: str,
        mode: str = "SWITCH",
        duration: int = 120,
    ) -> dict[str, Any]:
        """Activates the controller's output test mode.

        Args:
            output: The identifier of the output.
            mode: The test mode (default is "SWITCH").
            duration: The duration in seconds (default is 120).

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the output is missing.
        """
        if not output:
            raise VioletPoolAPIError("Output identifier is required")

        duration_ms = max(0, int(duration)) * 1000
        payload = f"{output},{mode},{duration_ms}"
        body = await self._request(
            API_SET_OUTPUT_TESTMODE,
            query=payload,
        )
        return self._command_result(body)

    async def set_switch_state(
        self,
        key: str,
        action: str,
        *,
        duration: int | float | None = None,
        last_value: int | float | None = None,
    ) -> dict[str, Any]:
        """Controls a function output via /setFunctionManually.

        Args:
            key: The device key.
            action: The action to perform (e.g., ON, OFF, AUTO).
            duration: An optional duration for the action.
            last_value: An optional last value (e.g., speed).

        Returns:
            A dictionary with the command result.
        """
        payload = self._build_manual_command(
            key,
            action,
            duration=duration,
            last_value=last_value,
        )
        query = quote(payload, safe=",")
        body = await self._request(
            API_SET_FUNCTION_MANUALLY,
            query=query,
        )
        return self._command_result(body)

    async def manual_dosing(self, dosing_type: str, duration: int) -> dict[str, Any]:
        """Triggers a dosing run using the manual function endpoint.

        Args:
            dosing_type: The type of dosing (e.g., "Chlor").
            duration: The duration in seconds.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the dosing type is unknown.
        """
        device_key = DOSING_FUNCTIONS.get(dosing_type)
        if not device_key:
            raise VioletPoolAPIError(f"Unknown dosing type: {dosing_type}")

        return await self.set_switch_state(
            device_key,
            ACTION_ON,
            duration=duration,
        )

    async def set_pv_surplus(
        self,
        *,
        active: bool,
        pump_speed: int | None = None,
    ) -> dict[str, Any]:
        """Enables or disables PV surplus mode.

        Args:
            active: Whether to activate PV surplus mode.
            pump_speed: An optional pump speed.

        Returns:
            A dictionary with the command result.
        """
        return await self.set_switch_state(
            "PVSURPLUS",
            ACTION_ON if active else ACTION_OFF,
            last_value=pump_speed,
        )

    async def set_all_dmx_scenes(self, action: str) -> dict[str, Any]:
        """Sends the same command to all DMX scenes.

        Args:
            action: The action to perform (ALLON, ALLOFF, ALLAUTO).

        Returns:
            A dictionary with the combined command results.

        Raises:
            VioletPoolAPIError: If the action is unsupported.
        """
        if action not in {ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO}:
            raise VioletPoolAPIError(f"Unsupported DMX action: {action}")

        results = []
        for scene in range(1, 13):
            key = f"DMX_SCENE{scene}"
            try:
                results.append(await self.set_switch_state(key, action))
            except VioletPoolAPIError as e:
                results.append({"success": False, "response": str(e)})

        success = all(result.get("success") is True for result in results)
        response = ", ".join(
            result.get("response", "") for result in results if result.get("response")
        )
        return {"success": success, "response": response}

    async def set_light_color_pulse(self) -> dict[str, Any]:
        """Triggers the color pulse animation for the pool light.

        Returns:
            A dictionary with the command result.
        """
        return await self.set_switch_state("LIGHT", ACTION_COLOR)

    async def trigger_digital_input_rule(self, rule_key: str) -> dict[str, Any]:
        """Triggers a digital input rule via a PUSH action.

        Args:
            rule_key: The rule key (e.g., DIRULE_1).

        Returns:
            A dictionary with the command result.
        """
        return await self.set_switch_state(rule_key, ACTION_PUSH)

    async def set_digital_input_rule_lock(
        self,
        rule_key: str,
        locked: bool,
    ) -> dict[str, Any]:
        """Locks or unlocks a digital input rule.

        Args:
            rule_key: The rule key.
            locked: True to lock, False to unlock.

        Returns:
            A dictionary with the command result.
        """
        return await self.set_switch_state(
            rule_key,
            ACTION_LOCK if locked else ACTION_UNLOCK,
        )

    async def set_device_temperature(
        self,
        climate_key: str,
        temperature: float,
    ) -> dict[str, Any]:
        """Sets the target temperature for heater or solar circuits.

        Args:
            climate_key: The climate key (HEATER or SOLAR).
            temperature: The target temperature.

        Returns:
            A dictionary with the command result.
        """
        target_key = f"{climate_key}_TARGET_TEMP"
        return await self.set_target_value(target_key, float(temperature))

    async def set_ph_target(self, value: float) -> dict[str, Any]:
        """Updates the pH setpoint.

        Args:
            value: The new pH target value.

        Returns:
            A dictionary with the command result.
        """
        return await self.set_target_value(TARGET_PH, float(value))

    async def set_orp_target(self, value: int) -> dict[str, Any]:
        """Updates the ORP setpoint.

        Args:
            value: The new ORP target value.

        Returns:
            A dictionary with the command result.
        """
        return await self.set_target_value(TARGET_ORP, int(value))

    async def set_min_chlorine_level(self, value: float) -> dict[str, Any]:
        """Updates the minimum chlorine level.

        Args:
            value: The new minimum chlorine level.

        Returns:
            A dictionary with the command result.
        """
        return await self.set_target_value(TARGET_MIN_CHLORINE, float(value))

    async def set_target_value(self, key: str, value: float | int) -> dict[str, Any]:
        """Sends a generic target value update to the controller.

        Args:
            key: The target key.
            value: The new value.

        Returns:
            A dictionary with the command result.
        """
        params = {"target": key, "value": value}
        body = await self._request(
            API_SET_TARGET_VALUES,
            params=params,
        )
        return self._command_result(body)

    async def set_dosing_parameters(
        self,
        parameters: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Updates dosing parameters via the dedicated endpoint.

        Args:
            parameters: A mapping of dosing parameters.

        Returns:
            A dictionary with the command result.
        """
        body = await self._request(
            API_SET_DOSING_PARAMETERS,
            method="POST",
            json_payload=dict(parameters),
        )
        return self._command_result(body)

    async def set_pump_speed(
        self,
        speed: int,
        duration: int = 0,
    ) -> dict[str, Any]:
        """Sets the pump speed.

        Args:
            speed: The pump speed (1-3, where 1=ECO, 2=Normal, 3=Boost).
            duration: Optional duration in seconds (0 = permanent).

        Returns:
            A dictionary with the command result.
        """
        safe_speed = max(1, min(3, int(speed)))
        safe_duration = max(0, int(duration))

        return await self.set_switch_state(
            key="PUMP",
            action=ACTION_ON,
            duration=safe_duration,
            last_value=safe_speed,
        )

    async def control_pump(
        self,
        action: str,
        speed: int | None = None,
        duration: int = 0,
    ) -> dict[str, Any]:
        """Controls the pump with optional speed and duration.

        Args:
            action: The action to perform (ON, OFF, AUTO).
            speed: Optional pump speed (1-3).
            duration: Optional duration in seconds.

        Returns:
            A dictionary with the command result.
        """
        return await self.set_switch_state(
            key="PUMP",
            action=action,
            duration=duration,
            last_value=speed,
        )
