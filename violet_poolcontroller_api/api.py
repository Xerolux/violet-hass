# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024–2026  Xerolux
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
from collections.abc import Iterable, Mapping
from typing import Any, cast
from urllib.parse import quote, urlparse, urlunparse

import aiohttp

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
    API_PRIORITY_NORMAL,
    API_RATE_LIMIT_BURST,
    API_RATE_LIMIT_REQUESTS,
    API_RATE_LIMIT_RETRY_AFTER,
    API_RATE_LIMIT_WINDOW,
    API_READINGS,
    API_RESTORE_CALIBRATION,
    API_SET_CONFIG,
    API_SET_DOSING_PARAMETERS,
    API_SET_FUNCTION_MANUALLY,
    API_SET_OUTPUT_TESTMODE,
    API_SET_TARGET_VALUES,
    DMX_SCENE_COUNT,
    DOSING_FUNCTIONS,
    TARGET_MIN_CHLORINE,
    TARGET_ORP,
    TARGET_PH,
)
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from .const_devices import DEVICE_PARAMETERS
from .utils_rate_limiter import RateLimiter
from .utils_sanitizer import InputSanitizer

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
        verify_ssl: bool = True,
        timeout: int = 10,
        max_retries: int = 3,
        dosing_standalone: bool = False,
    ) -> None:
        """Initializes the API helper.

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
            raise ValueError("A valid aiohttp session must be provided")

        self._base_url = self._build_secure_base_url(host, use_ssl).rstrip("/")

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
                "or with self-signed certificates in trusted networks."
            )
            import ssl

            self._ssl_context = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

        # Per-instance rate limiter: each controller gets its own token bucket.
        # Using a global singleton would starve all controllers equally when
        # running multiple API instances against different controllers.
        self._rate_limiter = RateLimiter(
            max_requests=API_RATE_LIMIT_REQUESTS,
            time_window=API_RATE_LIMIT_WINDOW,
            burst_size=API_RATE_LIMIT_BURST,
            retry_after=API_RATE_LIMIT_RETRY_AFTER,
        )
        self._circuit_breaker = CircuitBreaker(expected_exception=VioletPoolAPIError)
        _LOGGER.debug(
            "API initialized: host=%s, SSL=%s, verify_ssl=%s, standalone=%s",
            host,
            use_ssl,
            verify_ssl,
            dosing_standalone,
        )

    # ---------------------------------------------------------------------
    # Public Properties
    # ---------------------------------------------------------------------

    @property
    def timeout(self) -> float:
        """Get current timeout in seconds."""
        return self._timeout.total or 0.0

    @property
    def max_retries(self) -> int:
        """Get maximum retry attempts."""
        return self._max_retries

    @property
    def dosing_standalone(self) -> bool:
        """Return whether dosing-standalone mode is enabled."""
        return self._dosing_standalone

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

        # Validate hostname format (allowing optional port)
        if not re.match(r"^[a-zA-Z0-9.-]+(?::[0-9]{1,5})?$", host):
            raise ValueError(f"Invalid hostname format: {host}")

        # Additional validation
        if len(host) > 253 or ".." in host or "//" in host:
            raise ValueError(f"Invalid hostname: {host}")

        protocol = "https" if use_ssl else "http"
        return urlunparse((protocol, host, "", "", "", ""))

    def _build_url(self, endpoint: str) -> str:
        """Constructs the full URL for a given endpoint."""
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
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

        Errors are always propagated as ``VioletPoolAPIError`` — the caller
        decides what to do.  This method never silently ignores failures or
        returns a fallback value on error.

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

        async def _execute_request() -> Any:
            # Wait for a rate-limiter token; continue on timeout (best-effort)
            try:
                await self._rate_limiter.wait_if_needed(priority=priority, timeout=10.0)
            except asyncio.TimeoutError:
                _LOGGER.warning(
                    "Rate limiter timeout for %s (priority: %d) — proceeding anyway",
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
                        ssl=self._ssl_context,  # type: ignore[arg-type]
                    ) as response:
                        # 5xx and 429 → retry via ClientError
                        if response.status >= 500 or response.status == 429:
                            response.raise_for_status()

                        # 4xx (except 429) → permanent client error, no retry
                        if 400 <= response.status < 500:
                            body = await response.text()
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message=(
                                    f"HTTP {response.status} for {endpoint}: "
                                    f"{body.strip()}"
                                ),
                            )

                        if expect_json:
                            try:
                                return await response.json(content_type=None)
                            except (aiohttp.ContentTypeError, json.JSONDecodeError) as err:
                                body = await response.text()
                                raise VioletPoolAPIError(
                                    f"Invalid JSON from {endpoint}: {body.strip()!r}"
                                ) from err

                        return await response.text()

                except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                    last_error = VioletPoolAPIError(
                        f"Error communicating with Violet controller: {err}"
                    )
                    _LOGGER.debug(
                        "Attempt %d/%d for %s failed: %s",
                        attempt,
                        self._max_retries,
                        endpoint,
                        err,
                    )
                    if attempt == self._max_retries:
                        raise last_error
                    # Exponential backoff with jitter
                    delay = min(2.0, 0.2 * (2 ** (attempt - 1)))
                    await asyncio.sleep(delay)

            raise VioletPoolAPIError("All retry attempts exhausted")

        try:
            return await self._circuit_breaker.call(_execute_request)
        except CircuitBreakerOpenError as err:
            raise VioletPoolAPIError(
                "Circuit breaker is open due to repeated communication failures"
            ) from err

    @staticmethod
    def _command_result(body: str | dict[str, Any]) -> dict[str, Any]:
        """Normalizes the controller's response for command-style requests.

        Args:
            body: The raw response body or dict.

        Returns:
            A dictionary with ``success`` (bool) and ``response`` (str).
        """
        if isinstance(body, dict):
            return body

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
        """Renders the command payload from the device parameter template.

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

    @staticmethod
    def _csv_query_from_values(values: Iterable[str], *, field_name: str) -> str:
        """Build a comma-separated query string from a collection of values."""
        query = ",".join([v for value in values if (v := value.strip())])
        if not query:
            raise VioletPoolAPIError(f"No valid {field_name} provided")
        return query

    async def _request_json_dict(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
        query: str | None = None,
        payload_name: str,
    ) -> dict[str, Any]:
        """Request JSON content and enforce a dictionary response shape.

        Raises:
            VioletPoolAPIError: If the response is not a JSON object.
        """
        response = await self._request(
            endpoint,
            params=params,
            query=query,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError(
                f"Expected a JSON object from {payload_name}, "
                f"got {type(response).__name__}"
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
                _LOGGER.error("Invalid config parameter %r: %s", key, err)
                raise VioletPoolAPIError(
                    f"Invalid configuration parameter: {key}"
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

    def _flatten_getreadings_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Flattens the getReadings response to a plain key-value dict.

        The controller can return data in two formats:
        - **Dict format** (base module): ``{"getReadings": {"KEY": value, …}}``
        - **List format** (dosing standalone): ``{"getReadings": [{"VALUE NAME": …}, …]}``

        When no ``getReadings`` key is present the response is assumed to already
        be a flat key-value mapping and is returned unchanged.

        The ``_dosing_standalone`` flag is updated whenever a clear format
        signal is received so the API can adapt if the controller changes mode.

        Args:
            response: The raw JSON object from the controller.

        Returns:
            A flat ``{key: value}`` dictionary ready for hardware-profile
            detection and filtering.
        """
        # No getReadings wrapper → treat as already-flat response
        if "getReadings" not in response:
            return response

        readings = response["getReadings"]

        # --- Dict format (base module firmware) ---
        if isinstance(readings, dict):
            if self._dosing_standalone:
                _LOGGER.info(
                    "Controller switched from dosing-standalone to base-module mode "
                    "(received dict-format getReadings)"
                )
            self._dosing_standalone = False
            return readings

        # --- List format (dosing-standalone firmware) ---
        if isinstance(readings, list):
            if not self._dosing_standalone:
                _LOGGER.info(
                    "Controller switched to dosing-standalone mode "
                    "(received list-format getReadings)"
                )
            self._dosing_standalone = True
            flat_dict: dict[str, Any] = {}
            for item in readings:
                if not isinstance(item, dict):
                    continue
                raw_name = item.get("VALUE NAME")
                if raw_name is None:
                    continue
                key = str(raw_name).strip().strip('"')
                if not key:
                    continue
                val = item.get("VALUE", item.get("VALUE ", item.get("value")))
                flat_dict[key] = val
            return flat_dict

        # --- Unexpected type ---
        _LOGGER.warning(
            "Unexpected getReadings type %s — ignoring payload",
            type(readings).__name__,
        )
        return {}

    def _build_hardware_profile(self, flattened: dict[str, Any]) -> dict[str, bool]:
        """Build a hardware presence profile from flattened getReadings data.

        Uses the controller's alive-counters (``SYSTEM_*_alive_count``) to
        reliably detect connected hardware modules.  The controller always
        emits relay keys (``EXT1_1``, ``EXT2_1``, …) with a default value of
        ``0`` even when the physical module is absent, so checking those keys
        would yield false positives.

        The counter starts at ``0`` on boot and the controller only emits
        alive-count keys for modules that are physically attached, so checking
        ``value > 0`` would produce false negatives immediately after a restart.

        Args:
            flattened: The flattened key-value readings dict.

        Returns:
            A dictionary with boolean flags for connected hardware components.
        """
        def _module_alive(alive_key: str) -> bool:
            return alive_key in flattened

        def _any_relay_used(prefix: str) -> bool:
            for key in flattened:
                if not key.startswith(prefix):
                    continue
                if "_LAST_ON" in key or "_LAST_OFF" in key or "_RUNTIME" in key:
                    continue
                last_on = flattened.get(f"{key}_LAST_ON")
                if last_on is None:
                    continue
                try:
                    if float(str(last_on).strip()) > 0:
                        return True
                except (ValueError, TypeError):
                    pass
            return False

        ext1 = _module_alive("SYSTEM_ext1module_alive_count") or _any_relay_used("EXT1_")
        ext2 = _module_alive("SYSTEM_ext2module_alive_count") or _any_relay_used("EXT2_")
        dosing = self.dosing_standalone or _module_alive("SYSTEM_dosagemodule_alive_count")

        return {
            "base_module": not self.dosing_standalone,
            "dosing_module": dosing,
            "extension_module_1": ext1,
            "extension_module_2": ext2,
        }

    def _filter_unsupported_readings(
        self, readings: dict[str, Any], profile: dict[str, bool]
    ) -> dict[str, Any]:
        """Filter out readings for hardware modules that are not present.

        Keys for absent modules are silently dropped so that the caller never
        receives stale or meaningless values.  No fallback values are inserted
        — if a reading is unavailable, it is simply absent from the result.

        Args:
            readings: The full flattened readings dict.
            profile: Hardware presence flags from ``_build_hardware_profile``.

        Returns:
            The filtered readings dict.
        """
        if not isinstance(readings, dict):
            return readings

        filtered: dict[str, Any] = {}
        for key, value in readings.items():
            norm = key.upper()

            # Base module keys — skip when no base module is present
            if not profile.get("base_module"):
                if norm in {
                    "PUMPSTATE", "PUMP_SPEED", "HEATER", "LIGHT", "ECO",
                    "BACKWASH", "BACKWASHRINSE", "REFILL", "PVSURPLUS", "TEMP_PUMP",
                } or (
                    norm.startswith("SYSTEM_")
                    and norm != "SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE"
                ):
                    continue

            # Extension module 1
            if not profile.get("extension_module_1") and norm.startswith("EXT1_"):
                continue

            # Extension module 2
            if not profile.get("extension_module_2") and norm.startswith("EXT2_"):
                continue

            # Dosing module
            if not profile.get("dosing_module"):
                if norm.startswith("DOS_") or norm == "SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE":
                    continue

            filtered[key] = value

        return filtered

    async def get_readings(self) -> dict[str, Any]:
        """Returns the complete dataset from the controller.

        Returns:
            A dictionary containing all readings filtered to the detected
            hardware configuration.

        Raises:
            VioletPoolAPIError: If the request fails or the payload is unexpected.
        """
        response = await self._request_json_dict(
            API_READINGS,
            query="ALL",
            payload_name="getReadings",
        )
        flattened = self._flatten_getreadings_response(response)
        profile = self._build_hardware_profile(flattened)
        return self._filter_unsupported_readings(flattened, profile)

    async def get_specific_readings(
        self, categories: list[str] | tuple[str, ...]
    ) -> dict[str, Any]:
        """Returns a reduced dataset for the provided categories.

        Args:
            categories: A list or tuple of category strings to fetch.

        Returns:
            A dictionary containing the requested readings.

        Raises:
            VioletPoolAPIError: If no categories are provided or the request fails.
        """
        if not categories:
            raise VioletPoolAPIError("At least one category must be provided")

        query = self._csv_query_from_values(categories, field_name="categories")
        response = await self._request_json_dict(
            API_READINGS,
            query=query,
            payload_name="getReadings",
        )
        return self._flatten_getreadings_response(response)

    async def get_history(
        self, *, hours: int = 24, sensor: str = "ALL"
    ) -> dict[str, Any]:
        """Fetches historical readings from the controller.

        Args:
            hours: The number of hours of history to fetch (minimum 1).
            sensor: The specific sensor to fetch history for, or "ALL".

        Returns:
            A dictionary containing the history data.

        Raises:
            VioletPoolAPIError: If the request fails or the payload is unexpected.
        """
        safe_hours = max(1, int(hours))
        params = {"hours": safe_hours, "sensor": sensor or "ALL"}
        return await self._request_json_dict(
            API_GET_HISTORY,
            params=params,
            payload_name="getHistory",
        )

    async def get_weather_data(self) -> dict[str, Any]:
        """Returns the current weather information used by the controller.

        Returns:
            A dictionary containing weather data.

        Raises:
            VioletPoolAPIError: If the request fails or the payload is unexpected.
        """
        return await self._request_json_dict(
            API_GET_WEATHER_DATA,
            payload_name="getWeatherdata",
        )

    async def get_hardware_profile(self) -> dict[str, bool]:
        """Detects connected hardware based on available readings.

        Returns:
            A dictionary with boolean flags for connected hardware components:
            - ``base_module``: True if the base module is present.
            - ``dosing_module``: True if the dosing module is present.
            - ``extension_module_1``: True if the first relay extension is present.
            - ``extension_module_2``: True if the second relay extension is present.

        Raises:
            VioletPoolAPIError: If the request fails.
        """
        response = await self._request_json_dict(
            API_READINGS,
            query="ALL",
            payload_name="getReadings",
        )
        flattened = self._flatten_getreadings_response(response)
        return self._build_hardware_profile(flattened)

    async def get_overall_dosing(self) -> dict[str, Any]:
        """Returns aggregated dosing statistics.

        Returns:
            A dictionary containing overall dosing statistics.

        Raises:
            VioletPoolAPIError: If the request fails or the payload is unexpected.
        """
        return await self._request_json_dict(
            API_GET_OVERALL_DOSING,
            payload_name="getOverallDosing",
        )

    async def get_output_states(self) -> dict[str, Any]:
        """Returns detailed information about output states.

        Returns:
            A dictionary containing output states.

        Raises:
            VioletPoolAPIError: If the request fails or the payload is unexpected.
        """
        return await self._request_json_dict(
            API_GET_OUTPUT_STATES,
            payload_name="getOutputstates",
        )

    async def get_config(
        self, parameters: list[str] | tuple[str, ...]
    ) -> dict[str, Any]:
        """Fetches controller configuration values for the provided keys.

        Args:
            parameters: A list or tuple of configuration keys to fetch.

        Returns:
            A dictionary containing the configuration values.

        Raises:
            VioletPoolAPIError: If no keys are provided or the request fails.
        """
        if not parameters:
            raise VioletPoolAPIError("At least one configuration key is required")

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
        """Updates controller configuration values.

        Args:
            config: A mapping of configuration keys and values to update.

        Returns:
            A dictionary with command result.

        Raises:
            VioletPoolAPIError: If configuration payload is empty or invalid.
        """
        if not config:
            raise VioletPoolAPIError("Configuration payload must not be empty")

        sanitized_config = self._sanitize_config_payload(config)

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
            VioletPoolAPIError: If the request fails or the payload is unexpected.
        """
        return await self._request_json_dict(
            API_GET_CALIB_RAW_VALUES,
            payload_name="getCalibRawValues",
        )

    async def get_calibration_history(self, sensor: str) -> list[dict[str, str]]:
        """Returns the calibration history for the provided sensor.

        Args:
            sensor: The name of the sensor.

        Returns:
            A list of dictionaries representing the history entries.

        Raises:
            VioletPoolAPIError: If the sensor name is missing or the request fails.
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
            try:
                parts = [part.strip() for part in line.split("|")]
                if len(parts) >= 3:
                    entries.append(
                        {
                            "timestamp": parts[0],
                            "value": parts[1],
                            "type": parts[2],
                        }
                    )
                else:
                    _LOGGER.warning(
                        "Skipping malformed calibration history line: %r", line
                    )
            except (IndexError, AttributeError) as err:
                _LOGGER.warning(
                    "Error parsing calibration history line %r: %s",
                    line,
                    err or type(err).__name__,
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
            duration: The duration in seconds (default is 120, max 86400).

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the output is missing.
        """
        if not output:
            raise VioletPoolAPIError("Output identifier is required")

        safe_duration = max(0, min(86400, int(duration)))  # cap at 24 h
        duration_ms = safe_duration * 1000
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

        Raises:
            VioletPoolAPIError: If the function is unavailable in standalone mode
                or if the request fails.
        """
        if self._dosing_standalone and self._is_base_module_function(key):
            raise VioletPoolAPIError(
                f"Function '{key}' requires the Violet base module and is not "
                "available in dosing-standalone mode"
            )

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
            dosing_type: The type of dosing (e.g., "Chlor", "pH-", "pH+").
            duration: The duration in seconds.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the dosing type is unknown or the request fails.
        """
        device_key = DOSING_FUNCTIONS.get(dosing_type)
        if not device_key:
            raise VioletPoolAPIError(f"Unknown dosing type: {dosing_type!r}")

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
            raise VioletPoolAPIError(f"Unsupported DMX action: {action!r}")

        tasks = [
            self.set_switch_state(f"DMX_SCENE{scene}", action)
            for scene in range(1, DMX_SCENE_COUNT + 1)
        ]

        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[dict[str, Any]] = []
        for res in raw_results:
            if isinstance(res, Exception):
                results.append(
                    {"success": False, "response": f"{type(res).__name__}: {res}"}
                )
            elif isinstance(res, dict):
                results.append(res)

        success = all(r.get("success") is True for r in results)
        response = ", ".join(
            str(r.get("response", "")) for r in results if r.get("response")
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
            value: The new ORP target value in mV.

        Returns:
            A dictionary with the command result.
        """
        return await self.set_target_value(TARGET_ORP, int(value))

    async def set_min_chlorine_level(self, value: float) -> dict[str, Any]:
        """Updates the minimum chlorine level.

        Args:
            value: The new minimum chlorine level in mg/l.

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
