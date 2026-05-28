# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024-2026  Xerolux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""HTTP client utilities for the Violet Pool Controller."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import quote, urlparse, urlunparse

import aiohttp

from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from .const_api import (
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
    API_PRIORITY_CRITICAL,
    API_PRIORITY_NORMAL,
    API_READINGS,
    API_RESTORE_CALIBRATION,
    API_SET_CONFIG,
    API_SET_DOSING_PARAMETERS,
    API_SET_FUNCTION_MANUALLY,
    API_SET_OUTPUT_TESTMODE,
    API_TRIGGER_MANUAL_DOSING,
    DOSING_FUNCTIONS,
    DOSING_OUTPUT_INDEX,
    ERROR_CODES,
    ERROR_SEVERITY_ALARM,
    ERROR_SEVERITY_INFO,
    ERROR_SEVERITY_WARNING,
    TARGET_MIN_CHLORINE,
    TARGET_ORP,
    TARGET_PH,
)
from .const_devices import DEVICE_PARAMETERS
from .utils_rate_limiter import get_global_rate_limiter
from .utils_sanitizer import InputSanitizer

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

_LOGGER = logging.getLogger(__name__)

_MAX_HOSTNAME_LENGTH = 253
_HTTP_SERVER_ERROR = 500
_HTTP_CLIENT_ERROR = 400
_HTTP_TOO_MANY_REQUESTS = 429
_MIN_CALIB_HISTORY_PARTS = 3


class VioletPoolAPIError(Exception):
    """Raised when the Violet Pool Controller API returns an error."""


class VioletPoolAPI:
    """A small HTTP client for interacting with the Violet Pool Controller.

    This class handles API requests, including authentication, rate limiting,
    and error handling. It provides methods for accessing various controller
    endpoints.
    """

    def __init__(  # noqa: PLR0913
        self,
        *,
        host: str,
        session: aiohttp.ClientSession,
        username: str | None = None,
        password: str | None = None,
        use_ssl: bool = False,
        verify_ssl: bool = True,
        timeout: int = 10,
        max_retries: int = 3,
        dosing_standalone: bool = False,
    ) -> None:
        """Initialize the API helper.

        Args:
            host: The hostname or IP address of the controller.
            session: The aiohttp client session.
            username: The username for authentication.
            password: The password for authentication.
            use_ssl: Whether to use SSL for the connection.
            verify_ssl: Whether to verify SSL certificates (security feature).
            timeout: The request timeout in seconds.
            max_retries: The maximum number of retries for failed requests.
            dosing_standalone: Whether the controller runs in dosing-standalone
                mode without a connected base module.

        """
        if session is None:
            msg = "A valid aiohttp session must be provided"
            raise ValueError(msg)

        self._base_url = self._build_secure_base_url(host, use_ssl=use_ssl).rstrip("/")

        self._session = session
        total_timeout = max(float(timeout), 1.0)
        self._timeout = aiohttp.ClientTimeout(total=total_timeout)
        self._max_retries = max(1, int(max_retries))
        self._dosing_standalone = bool(dosing_standalone)
        self._auth = None
        if username:
            self._auth = aiohttp.BasicAuth(username, password or "")

        # SSL/TLS security configuration
        self._verify_ssl = verify_ssl
        self._ssl_context = None
        if use_ssl and not verify_ssl:
            _LOGGER.warning(
                "SSL certificate verification is DISABLED. "
                "This is a security risk and should only be used for testing "
                "or with self-signed certificates in trusted networks.",
            )
            import ssl  # noqa: PLC0415

            self._ssl_context = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

        # Rate limiting to protect the controller from being overloaded
        self._rate_limiter = get_global_rate_limiter()
        self._circuit_breaker = CircuitBreaker(expected_exception=VioletPoolAPIError)
        _LOGGER.debug(
            "API initialized with rate limiting enabled, SSL=%s, verify_ssl=%s",
            use_ssl,
            verify_ssl,
        )

    # ---------------------------------------------------------------------
    # Public Properties
    # ---------------------------------------------------------------------

    @property
    def timeout(self) -> float:
        """Get current timeout in seconds.

        Returns:
            The timeout value in seconds.

        """
        return self._timeout.total or 0.0

    @property
    def max_retries(self) -> int:
        """Get maximum retry attempts.

        Returns:
            The maximum number of retry attempts.

        """
        return self._max_retries

    @property
    def dosing_standalone(self) -> bool:
        """Return whether dosing-standalone mode is enabled."""
        return self._dosing_standalone

    # ---------------------------------------------------------------------
    # Generic helpers
    # ---------------------------------------------------------------------

    def _build_secure_base_url(self, host: str, *, use_ssl: bool) -> str:
        """Securely construct base URL with comprehensive validation."""
        # Strip existing protocols to prevent override
        host = host.strip()
        if host.startswith(("http://", "https://")):
            parsed = urlparse(host)
            host = parsed.netloc

        # Validate hostname format (allowing optional port)
        if not re.match(r"^[a-zA-Z0-9.-]+(?::[0-9]{1,5})?$", host):
            msg = f"Invalid hostname format: {host}"
            raise ValueError(msg)

        # Additional validation
        if len(host) > _MAX_HOSTNAME_LENGTH or ".." in host or "//" in host:
            msg = f"Invalid hostname: {host}"
            raise ValueError(msg)

        protocol = "https" if use_ssl else "http"
        return urlunparse((protocol, host, "", "", "", ""))

    def _build_url(self, endpoint: str) -> str:
        """Construct the full URL for a given endpoint.

        Args:
            endpoint: The API endpoint.

        Returns:
            The full URL.

        """
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return f"{self._base_url}{endpoint}"

    async def _request(  # noqa: C901, PLR0913
        self,
        endpoint: str,
        *,
        method: str = "GET",
        params: Mapping[str, Any] | None = None,
        query: str | None = None,
        json_payload: Any | None = None,  # noqa: ANN401
        data: Any | None = None,  # noqa: ANN401
        expect_json: bool = False,
        priority: int = API_PRIORITY_NORMAL,
    ) -> Any:  # noqa: ANN401
        """Perform a request with rate limiting, retries, and error handling.

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
            msg = "'params' and 'query' are mutually exclusive"
            raise ValueError(msg)

        async def _execute_request() -> Any:  # noqa: ANN401
            # Wait if the rate limit is reached
            try:
                await self._rate_limiter.wait_if_needed(priority=priority, timeout=10.0)
            except TimeoutError:
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
                        data=data,
                        auth=self._auth,
                        timeout=self._timeout,
                        ssl=self._ssl_context,  # type: ignore[arg-type]
                    ) as response:
                        if (
                            response.status >= _HTTP_SERVER_ERROR
                            or response.status == _HTTP_TOO_MANY_REQUESTS
                        ):
                            # Server error or rate limit
                            # -> trigger retry via ClientError
                            response.raise_for_status()

                        if (
                            response.status >= _HTTP_CLIENT_ERROR
                            and response.status < _HTTP_SERVER_ERROR
                        ):
                            body = await response.text()
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message=(f"HTTP {response.status} for {endpoint}: {body.strip()}"),
                            )

                        if expect_json:
                            try:
                                return await response.json(content_type=None)
                            except (
                                aiohttp.ContentTypeError,
                                json.JSONDecodeError,
                            ) as err:
                                body = await response.text()
                                msg = f"Invalid JSON payload for {endpoint}: {body.strip()}"
                                raise VioletPoolAPIError(
                                    msg,
                                ) from err

                        return await response.text()

                except (TimeoutError, aiohttp.ClientError) as err:
                    last_error = VioletPoolAPIError(
                        f"Error communicating with Violet controller: {err}",
                    )
                    _LOGGER.debug(
                        "Attempt %d for %s failed: %s",
                        attempt,
                        endpoint,
                        err,
                    )
                    if attempt == self._max_retries:
                        raise last_error from None
                    # Exponential backoff with jitter
                    delay = min(2.0, 0.2 * (2 ** (attempt - 1)))
                    await asyncio.sleep(delay)

            msg = "All retry attempts exhausted"
            raise VioletPoolAPIError(msg)

        try:
            return await self._circuit_breaker.call(_execute_request)
        except CircuitBreakerOpenError as err:
            msg = "Circuit breaker is open due to repeated communication failures"
            raise VioletPoolAPIError(
                msg,
            ) from err

    @staticmethod
    def _command_result(body: str | dict[str, Any]) -> dict[str, Any]:
        """Normalize the controller's response for command-style requests.

        The controller responds with up to 4 lines of text/plain:
          Line 1: OK or ERROR
          Line 2: Output name (e.g. PUMP, DOS_1_CL)
          Line 3+: Status message

        For dosing: MANDOS_STARTED\\nOK or MANDOS_STOPPED\\nOK

        Args:
            body: The raw response body or dict.

        Returns:
            A dictionary with success status, response text, and optional
            parsed output/message fields.

        """
        if isinstance(body, dict):
            return body

        text = (body or "").strip()
        success = not text or "error" not in text.lower()

        result: dict[str, Any] = {"success": success, "response": text}

        lines = text.splitlines() if text else []
        if len(lines) >= 2:
            result["output"] = lines[1].strip()
        if len(lines) >= 3:
            result["message"] = "\n".join(line.strip() for line in lines[2:])

        return result

    def _build_manual_command(
        self,
        key: str,
        action: str,
        *,
        duration: float | None = None,
        last_value: float | None = None,
    ) -> str:
        """Render the command payload based on the device parameter template.

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
        template = cast(
            "str",
            DEVICE_PARAMETERS.get(key, {}).get(
                "api_template",
                f"{key},{{action}},{{duration}},{{value}}",
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
            msg = f"Template for {key} requires missing field: {err.args[0]}"
            raise VioletPoolAPIError(
                msg,
            ) from err

    @staticmethod
    def _csv_query_from_values(values: Iterable[str], *, field_name: str) -> str:
        """Build a comma-separated query string from a collection of values."""
        query = ",".join([v for value in values if (v := value.strip())])
        if not query:
            msg = f"No valid {field_name} provided"
            raise VioletPoolAPIError(msg)
        return query

    async def _request_json_dict(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
        query: str | None = None,
        payload_name: str,
    ) -> dict[str, Any]:
        """Request JSON content and enforce a dictionary response shape."""
        response = await self._request(
            endpoint,
            params=params,
            query=query,
            expect_json=True,
        )
        if not isinstance(response, dict):
            msg = f"Unexpected payload returned from {payload_name}"
            raise VioletPoolAPIError(
                msg,
            )
        return response

    def _sanitize_config_payload(self, config: Mapping[str, Any]) -> dict[str, Any]:
        """Sanitize and validate configuration payload before POSTing it."""
        sanitized_config: dict[str, str | int | float] = {}

        for key, value in config.items():
            try:
                sanitized_key = InputSanitizer.validate_api_parameter(str(key))
                sanitized_value: str | int | float

                if isinstance(value, str):
                    sanitized_value = InputSanitizer.sanitize_string(
                        value,
                        max_length=1000,
                        allow_special_chars=True,
                        escape_html=False,
                    )
                elif isinstance(value, (int, float)):
                    sanitized_value = InputSanitizer.sanitize_numeric(value)
                else:
                    sanitized_value = InputSanitizer.sanitize_string(str(value))

                sanitized_config[sanitized_key] = sanitized_value
            except ValueError as err:
                _LOGGER.exception("Invalid config parameter %s", key)
                msg = f"Invalid configuration parameter: {key}"
                raise VioletPoolAPIError(
                    msg,
                ) from err

        return sanitized_config

    def _is_base_module_function(self, key: str) -> bool:
        """Return True if the function depends on the base module."""
        normalized = (key or "").strip().upper()
        if not normalized:
            return False

        if normalized.startswith("DOS_"):
            return False

        if normalized.startswith(("EXT", "DMX_SCENE", "DIRULE_", "OMNI_DC")):
            return True

        return normalized in {
            "PUMP",
            "SOLAR",
            "HEATER",
            "LIGHT",
            "ECO",
            "BACKWASH",
            "BACKWASHRINSE",
            "REFILL",
            "PVSURPLUS",
        }

    # ---------------------------------------------------------------------
    # Public API surface
    # ---------------------------------------------------------------------

    def _flatten_getreadings_response(
        self,
        response: dict[str, Any],
    ) -> dict[str, Any]:
        """Flatten the getReadings list response for standalone firmware.

        Args:
            response: The raw response dictionary from the controller.

        Returns:
            The flattened key-value dictionary,
            or the original response if not applicable.

        """
        readings = response.get("getReadings")
        if not readings:
            return response

        if isinstance(readings, dict):
            self._dosing_standalone = False
            return self._filter_orphan_extension_keys(readings)

        if isinstance(readings, list):
            self._dosing_standalone = True
            flat_dict: dict[str, Any] = {}
            for item in readings:
                if isinstance(item, dict) and item.get("VALUE NAME"):
                    key = str(item["VALUE NAME"]).strip().strip('"')
                    val = item.get("VALUE", item.get("VALUE ", item.get("value")))
                    flat_dict[key] = val
            return flat_dict

        return response

    @staticmethod
    def _filter_orphan_extension_keys(readings: dict[str, Any]) -> dict[str, Any]:
        """Remove EXT*_ keys when the corresponding module is not connected.

        The controller always returns EXT*_ keys even when no hardware module
        is physically present.  We only keep them when the matching
        ``SYSTEM_ext*module_alive_count`` key exists in the payload.
        """
        ext1_alive = "SYSTEM_ext1module_alive_count" in readings
        ext2_alive = "SYSTEM_ext2module_alive_count" in readings

        if ext1_alive and ext2_alive:
            return readings

        return {
            k: v
            for k, v in readings.items()
            if (ext1_alive or not k.startswith("EXT1")) and (ext2_alive or not k.startswith("EXT2"))
        }

    async def get_readings(self) -> dict[str, Any]:
        """Return the complete dataset from the controller.

        Returns:
            A dictionary containing all readings.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.

        """
        response = await self._request_json_dict(
            API_READINGS,
            query="ALL",
            payload_name="getReadings",
        )
        return self._flatten_getreadings_response(response)

    async def get_hardware_profile(self) -> dict[str, bool]:
        """Detect connected hardware modules from the controller readings.

        Uses ``SYSTEM_*_alive_count`` keys to determine which modules are
        physically present.  For standalone dosing setups (list-format
        payloads) the base module is always reported as absent.

        Returns:
            A dictionary with keys ``base_module``, ``dosing_module``,
            ``extension_module_1``, and ``extension_module_2``.
        """
        response = await self._request_json_dict(
            API_READINGS,
            query="ALL",
            payload_name="getReadings",
        )
        readings = self._flatten_getreadings_response(response)

        has_base = not self._dosing_standalone and bool(readings)
        return {
            "base_module": has_base,
            "dosing_module": self._dosing_standalone
            or "SYSTEM_dosagemodule_alive_count" in readings,
            "extension_module_1": "SYSTEM_ext1module_alive_count" in readings,
            "extension_module_2": "SYSTEM_ext2module_alive_count" in readings,
        }

    async def get_specific_readings(
        self,
        categories: list[str] | tuple[str, ...],
    ) -> dict[str, Any]:
        """Return a reduced dataset for the provided categories.

        Args:
            categories: A list or tuple of category strings to fetch.

        Returns:
            A dictionary containing the requested readings.

        Raises:
            VioletPoolAPIError: If no categories are provided
                or the payload is unexpected.

        """
        if not categories:
            msg = "At least one category must be provided"
            raise VioletPoolAPIError(msg)

        query = self._csv_query_from_values(categories, field_name="categories")
        response = await self._request_json_dict(
            API_READINGS,
            query=query,
            payload_name="getReadings",
        )
        return self._flatten_getreadings_response(response)

    async def get_history(
        self,
        *,
        hours: int = 24,
        sensor: str = "ALL",
    ) -> dict[str, Any]:
        """Fetch historical readings from the controller.

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
        return await self._request_json_dict(
            API_GET_HISTORY,
            params=params,
            payload_name="getHistory",
        )

    async def get_weather_data(self) -> dict[str, Any]:
        """Return the current weather information used by the controller.

        Returns:
            A dictionary containing weather data.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.

        """
        return await self._request_json_dict(
            API_GET_WEATHER_DATA,
            payload_name="getWeatherdata",
        )

    async def get_overall_dosing(self) -> dict[str, Any]:
        """Return aggregated dosing statistics.

        Returns:
            A dictionary containing overall dosing statistics.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.

        """
        return await self._request_json_dict(
            API_GET_OVERALL_DOSING,
            payload_name="getOverallDosing",
        )

    async def get_output_states(self) -> dict[str, Any]:
        """Return detailed information about output states.

        Returns:
            A dictionary containing output states.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.

        """
        return await self._request_json_dict(
            API_GET_OUTPUT_STATES,
            payload_name="getOutputstates",
        )

    async def get_config(
        self,
        parameters: list[str] | tuple[str, ...],
    ) -> dict[str, Any]:
        """Fetch controller configuration values for the provided keys.

        Args:
            parameters: A list or tuple of configuration keys to fetch.

        Returns:
            A dictionary containing the configuration values.

        Raises:
            VioletPoolAPIError: If no keys are provided or the payload is unexpected.

        """
        if not parameters:
            msg = "At least one configuration key is required"
            raise VioletPoolAPIError(msg)

        query = self._csv_query_from_values(
            parameters,
            field_name="configuration keys",
        )
        return await self._request_json_dict(
            API_GET_CONFIG,
            query=query,
            payload_name="getConfig",
        )

    async def set_config(self, config: Mapping[str, Any]) -> dict[str, Any]:
        """Update controller configuration values.

        Args:
            config: A mapping of configuration keys and values to update.

        Returns:
            A dictionary with command result.

        Raises:
            VioletPoolAPIError: If configuration payload is empty.

        """
        if not config:
            msg = "Configuration payload must not be empty"
            raise VioletPoolAPIError(msg)

        sanitized_config = self._sanitize_config_payload(config)

        body = await self._request(
            API_SET_CONFIG,
            method="POST",
            data=sanitized_config,
        )
        return self._command_result(body)

    async def get_calibration_raw_values(self) -> dict[str, Any]:
        """Return the current raw values for all calibration sensors.

        Returns:
            A dictionary containing raw calibration values.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.

        """
        return await self._request_json_dict(
            API_GET_CALIB_RAW_VALUES,
            payload_name="getCalibRawValues",
        )

    async def get_calibration_history(self, sensor: str) -> list[dict[str, str]]:
        """Return the calibration history for the provided sensor.

        Args:
            sensor: The name of the sensor.

        Returns:
            A list of dictionaries representing the history entries.

        Raises:
            VioletPoolAPIError: If the sensor name is missing.

        """
        if not sensor:
            msg = "Sensor name required for calibration history"
            raise VioletPoolAPIError(msg)

        response = await self._request(
            API_GET_CALIB_HISTORY,
            query=sensor,
            expect_json=False,
        )

        entries: list[dict[str, str]] = []
        for line in (response or "").strip().splitlines():
            try:
                parts = [part.strip() for part in line.split("|")]
                if len(parts) >= _MIN_CALIB_HISTORY_PARTS:
                    entries.append(
                        {
                            "timestamp": parts[0],
                            "value": parts[1],
                            "type": parts[2],
                        },
                    )
                else:
                    _LOGGER.warning(
                        "Skipping malformed calibration history line: %s",
                        line,
                    )
            except (IndexError, AttributeError) as err:
                err_msg = str(err) or type(err).__name__
                _LOGGER.warning(
                    "Error parsing calibration history line '%s': %s",
                    line,
                    err_msg,
                )
        return entries

    async def restore_calibration(self, sensor: str, timestamp: str) -> dict[str, Any]:
        """Restore a previous calibration entry for the given sensor.

        Args:
            sensor: The name of the sensor.
            timestamp: The timestamp of the calibration to restore.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the sensor or timestamp is missing.

        """
        if not sensor or not timestamp:
            msg = "Sensor and timestamp are required for calibration restore"
            raise VioletPoolAPIError(
                msg,
            )

        body = await self._request(
            API_RESTORE_CALIBRATION,
            method="POST",
            data={"sensor": sensor, "timestamp": timestamp},
        )
        return self._command_result(body)

    async def set_output_test_mode(
        self,
        *,
        output: str,
        mode: str = "SWITCH",
        duration: int = 120,
    ) -> dict[str, Any]:
        """Activate the controller's output test mode.

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
            msg = "Output identifier is required"
            raise VioletPoolAPIError(msg)

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
        duration: float | None = None,
        last_value: float | None = None,
    ) -> dict[str, Any]:
        """Control a function output.

        Uses /triggerManualDosing for dosing pumps (DOS_*) and
        /setFunctionManually for all other functions.

        Args:
            key: The device key.
            action: The action to perform (e.g., ON, OFF, AUTO).
            duration: An optional duration for the action.
            last_value: An optional last value (e.g., speed).

        Returns:
            A dictionary with the command result.

        """
        if self._dosing_standalone and self._is_base_module_function(key):
            msg = (
                f"Function '{key}' requires the Violet base module and is not "
                "available in dosing-standalone mode"
            )
            raise VioletPoolAPIError(
                msg,
            )

        if key.startswith("DOS_"):
            return await self._trigger_dosing(key, action, duration=duration)

        payload = self._build_manual_command(
            key,
            action,
            duration=duration,
            last_value=last_value,
        )
        query = quote(payload, safe=",")
        body = await self._request(API_SET_FUNCTION_MANUALLY, query=query)
        return self._command_result(body)

    async def _trigger_dosing(
        self,
        key: str,
        action: str,
        *,
        duration: float | None = None,
    ) -> dict[str, Any]:
        """Trigger or stop a manual dosing run via /triggerManualDosing.

        Args:
            key: The dosing pump key (e.g. DOS_6_FLOC).
            action: The action (ON/START → DOSSTART, OFF/STOP → DOSSTOP).
            duration: Duration in seconds.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the dosing key is unknown.

        """
        output_index = DOSING_OUTPUT_INDEX.get(key)
        if output_index is None:
            msg = f"Unknown dosing output key: {key}"
            raise VioletPoolAPIError(msg)

        dos_action = "DOSSTOP" if action.upper() in ("OFF", "STOP") else "DOSSTART"
        dos_duration = int(duration) if duration else 0

        form_data = {
            "action": dos_action,
            "output": str(output_index),
            "runtime": str(dos_duration),
            "from": "1",
            "runtime_formatted": f"{dos_duration // 60:02d}:{dos_duration % 60:02d}",
        }
        body = await self._request(
            API_TRIGGER_MANUAL_DOSING,
            method="POST",
            data=form_data,
            priority=API_PRIORITY_CRITICAL,
        )
        return self._command_result(body)

    async def manual_dosing(self, dosing_type: str, duration: int) -> dict[str, Any]:
        """Trigger a dosing run using the manual function endpoint.

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
            msg = f"Unknown dosing type: {dosing_type}"
            raise VioletPoolAPIError(msg)

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
        """Enable or disable PV surplus mode.

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
        """Send a global DMX command that affects all scenes and the LIGHT output.

        The controller treats ALLON/ALLOFF/ALLAUTO as global actions: a single
        request to any DMX_SCENE key switches all 12 scenes and LIGHT at once.

        Args:
            action: The action to perform (ALLON, ALLOFF, ALLAUTO).

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the action is unsupported.

        """
        if action not in {ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO}:
            msg = f"Unsupported DMX action: {action}"
            raise VioletPoolAPIError(msg)

        return await self.set_switch_state("DMX_SCENE1", action)

    async def set_light_color_pulse(self) -> dict[str, Any]:
        """Trigger the color pulse animation for the pool light.

        Returns:
            A dictionary with the command result.

        """
        return await self.set_switch_state("LIGHT", ACTION_COLOR)

    async def trigger_digital_input_rule(self, rule_key: str) -> dict[str, Any]:
        """Trigger a digital input rule via a PUSH action.

        Args:
            rule_key: The rule key (e.g., DIRULE_1).

        Returns:
            A dictionary with the command result.

        """
        return await self.set_switch_state(rule_key, ACTION_PUSH)

    async def set_digital_input_rule_lock(
        self,
        rule_key: str,
        *,
        locked: bool,
    ) -> dict[str, Any]:
        """Lock or unlock a digital input rule.

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
        """Set the target temperature for heater or solar circuits.

        Args:
            climate_key: The climate key (HEATER or SOLAR).
            temperature: The target temperature.

        Returns:
            A dictionary with the command result.

        """
        target_key = f"{climate_key}_TARGET_TEMP"
        return await self.set_target_value(target_key, float(temperature))

    async def set_ph_target(self, value: float) -> dict[str, Any]:
        """Update the pH setpoint.

        Args:
            value: The new pH target value.

        Returns:
            A dictionary with the command result.

        """
        return await self.set_target_value(TARGET_PH, float(value))

    async def set_orp_target(self, value: int) -> dict[str, Any]:
        """Update the ORP setpoint.

        Args:
            value: The new ORP target value.

        Returns:
            A dictionary with the command result.

        """
        return await self.set_target_value(TARGET_ORP, int(value))

    async def set_min_chlorine_level(self, value: float) -> dict[str, Any]:
        """Update the minimum chlorine level.

        Args:
            value: The new minimum chlorine level.

        Returns:
            A dictionary with the command result.

        """
        return await self.set_target_value(TARGET_MIN_CHLORINE, float(value))

    async def set_target_value(self, key: str, value: float) -> dict[str, Any]:
        """Send a generic target value update to the controller.

        Args:
            key: The target key.
            value: The new value.

        Returns:
            A dictionary with the command result.

        """
        return await self.set_config({key: value})

    async def set_dosing_parameters(
        self,
        parameters: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Update dosing parameters via the dedicated endpoint.

        Args:
            parameters: A mapping of dosing parameters.

        Returns:
            A dictionary with the command result.

        """
        body = await self._request(
            API_SET_DOSING_PARAMETERS,
            method="POST",
            data=dict(parameters),
        )
        return self._command_result(body)

    async def set_pump_speed(
        self,
        speed: int,
        duration: int = 0,
    ) -> dict[str, Any]:
        """Set the pump speed.

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
        """Control the pump with optional speed and duration.

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

    @staticmethod
    def parse_error_notification(
        error_code: str,
        subject: str | None = None,
    ) -> dict[str, Any]:
        """Parse an error notification received from the controller.

        The controller sends outbound HTTP requests with ERRORCODE and SUBJECT
        fields when warnings/alarms occur.  This method decodes them into a
        structured dict suitable for display as a sensor entity.

        Args:
            error_code: The 4-digit error code string (e.g. "0020").
            subject: The SUBJECT field from the controller (optional fallback).

        Returns:
            A dict with keys: code, severity, message, is_alarm, is_warning.

        """
        code = str(error_code).strip().zfill(4)
        info = ERROR_CODES.get(code)

        if info:
            severity = info["severity"]
            message = info["message"]
        else:
            severity = ERROR_SEVERITY_WARNING
            message = subject or f"Unbekannter Fehlercode {code}"

        return {
            "code": code,
            "severity": severity,
            "message": message,
            "is_alarm": severity == ERROR_SEVERITY_ALARM,
            "is_warning": severity == ERROR_SEVERITY_WARNING,
            "is_info": severity == ERROR_SEVERITY_INFO,
        }

    @staticmethod
    def parse_multiple_errors(
        error_data: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        """Parse multiple error codes from a notification payload.

        Handles payloads where ERRORCODE may contain multiple comma-separated
        codes or where multiple error fields are present.

        Args:
            error_data: The full notification payload dict.

        Returns:
            A list of parsed error dicts.

        """
        results: list[dict[str, Any]] = []
        raw_code = str(error_data.get("ERRORCODE", ""))
        subject = str(error_data.get("SUBJECT", ""))

        if not raw_code or raw_code == "0":
            return results

        for code in raw_code.split(","):
            code = code.strip()
            if code and code != "0":
                results.append(
                    VioletPoolAPI.parse_error_notification(code, subject),
                )

        return results
