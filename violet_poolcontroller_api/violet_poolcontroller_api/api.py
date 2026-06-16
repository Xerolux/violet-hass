# violet-poolController-api - API f├╝r Violet Pool Controller
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
import ipaddress
import json
import logging
import math
import random
import re
import ssl
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import quote, urlparse, urlunparse

import aiohttp

from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from .const_api import (
    ACTION_ALLAUTO,
    ACTION_ALLOFF,
    ACTION_ALLON,
    ACTION_AUTO,
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
    API_GET_LIVE_TRACE,
    API_GET_LOG,
    API_GET_NOTIFICATIONS,
    API_GET_OUTPUT_RUNTIMES,
    API_GET_OUTPUT_STATES,
    API_GET_OVERALL_DOSING,
    API_GET_RS485_PUMP_DATA,
    API_GET_SERVICE_STATES,
    API_GET_UPDATE_HISTORY,
    API_GET_UPDATE_STATE,
    API_GET_WEATHER_DATA,
    API_INIT_UPDATE,
    API_PRIORITY_CRITICAL,
    API_PRIORITY_NORMAL,
    API_READINGS,
    API_RESET_BLOCKING,
    API_RESTORE_CALIBRATION,
    API_SET_CAN_AMOUNT,
    API_SET_CONFIG,
    API_SET_FUNCTION_MANUALLY,
    API_SET_OUTPUT_TESTMODE,
    API_SET_RS485_LIVE,
    API_TRIGGER_MANUAL_DOSING,
    DOSING_CANISTER_ID,
    DOSING_CONFIG_PREFIX,
    DOSING_FUNCTIONS,
    DOSING_OUTPUT_INDEX,
    ERROR_CODES,
    ERROR_SEVERITY_ALARM,
    ERROR_SEVERITY_INFO,
    ERROR_SEVERITY_REMINDER,
    ERROR_SEVERITY_WARNING,
    OMNI_POSITIONS,
    RS485_PUMP_MODES,
    RS485_PUMP_NAMES,
    SYSTEM_SERVICES,
    TARGET_MIN_CHLORINE,
    TARGET_ORP,
    TARGET_PH,
)
from .const_devices import COVER_FUNCTIONS, DEVICE_PARAMETERS
from .readings import VioletReadings
from .utils_rate_limiter import get_global_rate_limiter
from .utils_sanitizer import InputSanitizer

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

_LOGGER = logging.getLogger(__name__)

_MAX_HOSTNAME_LENGTH = 253
_HTTP_SERVER_ERROR = 500
_HTTP_CLIENT_ERROR = 400
_HTTP_TOO_MANY_REQUESTS = 429
_HTTP_UNAUTHORIZED = 401
_HTTP_FORBIDDEN = 403
_MIN_CALIB_HISTORY_PARTS = 3

# Valid setpoint ranges for each configurable target key (inclusive bounds).
# Values outside these ranges or non-finite values are rejected before the
# HTTP call to avoid surprising controller behaviour.
SETPOINT_RANGES: dict[str, tuple[float, float]] = {
    TARGET_PH: (6.0, 8.0),
    TARGET_ORP: (500.0, 900.0),
    TARGET_MIN_CHLORINE: (0.0, 5.0),
    "HEATER_set_temp": (5.0, 45.0),
    "SOLAR_maxtemp": (5.0, 55.0),
}


# =============================================================================
# Exception hierarchy
# =============================================================================


class VioletPoolAPIError(Exception):
    """Base exception for all Violet Pool Controller API errors.

    Callers can catch this base class to handle any API failure, or use
    the specific subclasses for more targeted error handling.
    """


class VioletAuthError(VioletPoolAPIError):
    """Raised when the controller rejects credentials (HTTP 401 or 403)."""


class VioletTimeoutError(VioletPoolAPIError):
    """Raised when an HTTP request to the controller exceeds the timeout."""


class VioletPayloadError(VioletPoolAPIError):
    """Raised when the controller returns a malformed or unparseable response."""


class VioletSetpointError(VioletPoolAPIError, ValueError):
    """Raised when a setpoint value is outside its documented valid range.

    Inherits from both ``VioletPoolAPIError`` and ``ValueError`` so callers
    can catch it as either.
    """


class VioletUnsafeOperationError(VioletPoolAPIError):
    """Raised for potentially dangerous operations without explicit acknowledgment.

    Pass ``acknowledge_unsafe=True`` to the relevant method to confirm that
    the caller is aware of the risk (e.g. motorised cover movement).
    """


class _DeterministicClientError(Exception):
    """Internal marker for 4xx client errors.

    Deliberately inherits from neither VioletPoolAPIError nor
    aiohttp.ClientError so it bypasses both the retry loop and the
    circuit breaker failure count: 4xx responses are deterministic
    (bad credentials, unknown endpoint) and must not open the breaker
    that protects against a down controller or network.  It is
    translated to the appropriate VioletPoolAPIError subclass before
    reaching the caller.
    """

    def __init__(self, msg: str, *, is_auth: bool = False) -> None:
        super().__init__(msg)
        self.is_auth = is_auth


def validate_setpoint(field: str, value: float) -> None:
    """Validate a setpoint value against documented controller ranges.

    Args:
        field: The configuration key (e.g. ``"DOSAGE_phminus_setpoint"``).
        value: The numeric value to validate.

    Raises:
        VioletSetpointError: If ``value`` is non-finite or outside the
            documented valid range for ``field``.  Fields with no registered
            range are accepted without range checking.
    """
    if not math.isfinite(value):
        msg = f"Invalid setpoint for '{field}': {value!r} is not a finite number"
        raise VioletSetpointError(msg)

    bounds = SETPOINT_RANGES.get(field)
    if bounds is None:
        return  # No documented range — accept any finite value

    lo, hi = bounds
    if not lo <= value <= hi:
        msg = f"Setpoint '{field}' value {value} is outside the valid range [{lo}, {hi}]"
        raise VioletSetpointError(msg)


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
        self._use_ssl = use_ssl
        self._ssl_context: ssl.SSLContext | None = None
        if use_ssl and not verify_ssl:
            _LOGGER.warning(
                "SSL certificate verification is DISABLED. "
                "This is a security risk and should only be used for testing "
                "or with self-signed certificates in trusted networks.",
            )
            self._ssl_context = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

        # Rate limiting to protect the controller from being overloaded
        self._rate_limiter = get_global_rate_limiter()
        self._circuit_breaker = CircuitBreaker(
            expected_exception=VioletPoolAPIError,
            ignored_exceptions=(_DeterministicClientError,),
        )
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

    @property
    def _ssl_param(self) -> ssl.SSLContext | bool:
        """Return the SSL parameter for aiohttp requests.

        For plain-HTTP connections the value is ignored by aiohttp, so the
        library default (True) is returned.
        """
        if not self._use_ssl:
            return True
        if self._ssl_context is not None:
            return self._ssl_context
        return True

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

        try:
            literal_ip = ipaddress.ip_address(host)
        except ValueError:
            literal_ip = None
        if literal_ip is not None and literal_ip.version == 6:
            protocol = "https" if use_ssl else "http"
            return urlunparse((protocol, f"[{host}]", "", "", "", ""))

        try:
            parsed_host = urlparse(f"//{host}")
        except ValueError as err:
            msg = f"Invalid hostname format: {host}"
            raise ValueError(msg) from err

        if parsed_host.username or parsed_host.password:
            msg = f"Invalid hostname format: {host}"
            raise ValueError(msg)
        if parsed_host.path or parsed_host.query or parsed_host.fragment:
            msg = f"Invalid hostname format: {host}"
            raise ValueError(msg)

        hostname = parsed_host.hostname
        if not hostname:
            msg = f"Invalid hostname format: {host}"
            raise ValueError(msg)

        try:
            port = parsed_host.port
        except ValueError as err:
            msg = f"Invalid port in hostname: {host}"
            raise ValueError(msg) from err

        if port is not None and not 1 <= port <= 65535:
            msg = f"Invalid port in hostname: {host}"
            raise ValueError(msg)

        try:
            ipaddress.ip_address(hostname)
            is_ip_literal = True
        except ValueError:
            is_ip_literal = False

        if not is_ip_literal and not re.match(r"^[a-zA-Z0-9.-]+$", hostname):
            msg = f"Invalid hostname format: {host}"
            raise ValueError(msg)

        # Additional validation
        if len(hostname) > _MAX_HOSTNAME_LENGTH or ".." in hostname or "//" in host:
            msg = f"Invalid hostname: {host}"
            raise ValueError(msg)

        netloc = f"[{hostname}]" if ":" in hostname else hostname
        if port is not None:
            netloc = f"{netloc}:{port}"

        protocol = "https" if use_ssl else "http"
        return urlunparse((protocol, netloc, "", "", "", ""))

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
                        ssl=self._ssl_param,
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
                            # Client errors (4xx, except 429 handled above) are
                            # deterministic - fail fast instead of retrying.
                            body = await response.text()
                            msg = f"HTTP {response.status} for {endpoint}: {body.strip()}"
                            is_auth = response.status in (
                                _HTTP_UNAUTHORIZED,
                                _HTTP_FORBIDDEN,
                            )
                            raise _DeterministicClientError(msg, is_auth=is_auth)

                        if expect_json:
                            try:
                                return await response.json(content_type=None)
                            except (
                                aiohttp.ContentTypeError,
                                json.JSONDecodeError,
                            ) as err:
                                body = await response.text()
                                msg = f"Invalid JSON payload for {endpoint}: {body.strip()}"
                                raise VioletPayloadError(msg) from err

                        return await response.text()

                except (TimeoutError, aiohttp.ServerTimeoutError) as err:
                    last_error = VioletTimeoutError(
                        f"Request to {endpoint} timed out: {err}",
                    )
                    _LOGGER.debug(
                        "Attempt %d for %s timed out: %s",
                        attempt,
                        endpoint,
                        err,
                    )
                    if attempt == self._max_retries:
                        raise last_error from None
                    delay = min(2.0, 0.2 * (2 ** (attempt - 1)))
                    jitter = random.uniform(0, delay * 0.1)  # Add 0-10% jitter
                    await asyncio.sleep(delay + jitter)
                except aiohttp.ClientError as err:
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
                    jitter = random.uniform(0, delay * 0.1)  # Add 0-10% jitter
                    await asyncio.sleep(delay + jitter)

            msg = "All retry attempts exhausted"
            raise VioletPoolAPIError(msg)

        try:
            return await self._circuit_breaker.call(_execute_request)
        except _DeterministicClientError as err:
            if err.is_auth:
                raise VioletAuthError(str(err)) from err
            raise VioletPoolAPIError(str(err)) from err
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
        lines = text.splitlines() if text else []
        first_line = lines[0].strip().upper() if lines else ""

        # Manual section 26.2: line 1 of the response is "OK" or "ERROR".
        # Dosing responses use "MANDOS_STARTED\nOK" instead, so fall back to
        # a substring check when the first line is neither marker.
        if first_line.startswith("ERROR"):
            success = False
        elif first_line == "OK":
            success = True
        else:
            success = not text or "error" not in text.lower()

        result: dict[str, Any] = {"success": success, "response": text}
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

        if not ext1_alive:
            readings = {k: v for k, v in readings.items() if not k.startswith("EXT1")}
        if not ext2_alive:
            readings = {k: v for k, v in readings.items() if not k.startswith("EXT2")}
        return readings

    async def get_readings(self) -> VioletReadings:
        """Return the complete dataset from the controller as a typed snapshot.

        The returned :class:`~violet_poolcontroller_api.readings.VioletReadings`
        object implements :class:`~collections.abc.Mapping`, so all existing
        code that accesses ``data.get("KEY")`` or ``"KEY" in data`` continues
        to work unchanged.  Typed properties (``readings.pump``,
        ``readings.ph``, etc.) are available as an additive convenience.

        Returns:
            A :class:`VioletReadings` instance wrapping all readings.

        Raises:
            VioletPoolAPIError: If the payload is unexpected.

        """
        response = await self._request_json_dict(
            API_READINGS,
            query="ALL",
            payload_name="getReadings",
        )
        flat = self._flatten_getreadings_response(response)
        return VioletReadings(flat)

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
        # Use flat dict directly (VioletReadings wrapping not needed here)
        flat = self._flatten_getreadings_response(response)

        has_base = not self._dosing_standalone and bool(flat)
        return {
            "base_module": has_base,
            "dosing_module": self._dosing_standalone or "SYSTEM_dosagemodule_alive_count" in flat,
            "extension_module_1": "SYSTEM_ext1module_alive_count" in flat,
            "extension_module_2": "SYSTEM_ext2module_alive_count" in flat,
        }

    async def get_specific_readings(
        self,
        categories: list[str] | tuple[str, ...],
    ) -> VioletReadings:
        """Return a reduced typed snapshot for the provided categories.

        Categories are joined with ``,`` and sent as the query string of
        ``/getReadings?<categories>``.  See
        :data:`~violet_poolcontroller_api.const_api.SPECIFIC_READING_GROUPS`
        for the special tokens (``DOSAGE``, ``RUNTIMES``, ``PUMPPRIOSTATE``,
        ``BACKWASH``, ``SYSTEM``) that act as feature flags rather than
        regex matchers – without them the corresponding computed fields are
        NOT included in the response, even when ``ALL`` is present.

        Args:
            categories: A list or tuple of category strings to fetch.  To
                receive computed dosing stats, runtimes, or priority states,
                include ``ALL`` plus the respective token
                (e.g. ``["ALL", "DOSAGE"]``).

        Returns:
            A :class:`VioletReadings` instance for the requested categories.

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
        return VioletReadings(self._flatten_getreadings_response(response))

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

        if key == "PVSURPLUS":
            action = self._normalize_pv_surplus_action(action)

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

        setFunctionManually does not work for dosing outputs (confirmed by
        PoolDigital in the support forum): neither ON nor AUTO has any
        effect there. Starting AND stopping a manual dosing run must both
        go through /triggerManualDosing.

        Args:
            key: The dosing pump key (e.g. DOS_6_FLOC).
            action: ON/START ÔåÆ DOSSTART; OFF/STOP/AUTO ÔåÆ DOSSTOP
                (stopping a run returns the channel to automatic mode).
            duration: Duration in seconds.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the dosing key or action is unknown.

        """
        output_index = DOSING_OUTPUT_INDEX.get(key)
        if output_index is None:
            msg = f"Unknown dosing output key: {key}"
            raise VioletPoolAPIError(msg)

        action_upper = action.strip().upper()
        if action_upper in ("OFF", "STOP", "AUTO", "DOSSTOP"):
            dos_action = "DOSSTOP"
        elif action_upper in ("ON", "START", "DOSSTART"):
            dos_action = "DOSSTART"
        else:
            # Never default to DOSSTART: an unexpected action must not
            # start a chemical dosing run.
            msg = f"Unsupported dosing action for {key}: {action}"
            raise VioletPoolAPIError(msg)

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

        # /triggerManualDosing requires an explicit runtime; duration <= 0
        # stops a running manual dosing instead (documented behavior).
        if duration <= 0:
            return await self.set_switch_state(device_key, ACTION_OFF)

        return await self.set_switch_state(
            device_key,
            ACTION_ON,
            duration=duration,
        )

    @staticmethod
    def _normalize_pv_surplus_action(action: str) -> str:
        """Normalize an action for the PVSURPLUS function.

        Manual section 26.3 only documents ON and OFF for PVSURPLUS; there is
        no AUTO mode (the getReadings PVSURPLUS state is 0/1/2 - off,
        triggered by digital input, or triggered by HTTP).  Sending AUTO is
        therefore mapped to OFF, which releases the HTTP trigger and returns
        control to the configured digital input / controller logic.

        Args:
            action: The requested action.

        Returns:
            The spec-conform action (ON or OFF).

        Raises:
            VioletPoolAPIError: If the action cannot be mapped to ON or OFF.

        """
        normalized = (action or "").strip().upper()
        if normalized == ACTION_AUTO:
            _LOGGER.warning(
                "PVSURPLUS does not support AUTO (manual section 26.3); "
                "sending OFF to release the HTTP trigger instead",
            )
            return ACTION_OFF
        if normalized not in (ACTION_ON, ACTION_OFF):
            msg = (
                f"Unsupported PVSURPLUS action '{action}': "
                "manual section 26.3 only documents ON and OFF"
            )
            raise VioletPoolAPIError(msg)
        return normalized

    async def set_pv_surplus(
        self,
        *,
        active: bool,
        pump_speed: int | None = None,
    ) -> dict[str, Any]:
        """Enable or disable PV surplus mode.

        Per manual section 26.3 the command format is
        ``PVSURPLUS,{ON|OFF},{speed},0`` where the speed (1-3) is only
        evaluated for variable-speed pumps.  If no speed is provided the
        controller falls back to the speed configured in its GUI.

        Args:
            active: Whether to activate PV surplus mode.
            pump_speed: An optional pump speed (1-3).

        Returns:
            A dictionary with the command result.

        """
        speed: int | None = None
        if pump_speed is not None:
            speed = max(1, min(3, int(pump_speed)))
        return await self.set_switch_state(
            "PVSURPLUS",
            ACTION_ON if active else ACTION_OFF,
            last_value=speed,
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

    async def set_cover_command(
        self,
        action: str,
        *,
        acknowledge_unsafe: bool = False,
    ) -> dict[str, Any]:
        """Send an open, close, or stop command to the pool cover.

        Cover movement is a potentially hazardous operation (motorised cover,
        risk of entrapment).  Callers must explicitly pass
        ``acknowledge_unsafe=True`` to confirm they are aware of the risk and
        have taken appropriate safety precautions.

        Args:
            action: ``"OPEN"``, ``"CLOSE"``, or ``"STOP"`` (case-insensitive).
            acknowledge_unsafe: Must be ``True`` to allow the command.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletUnsafeOperationError: If ``acknowledge_unsafe`` is ``False``.
            VioletPoolAPIError: If ``action`` is not a known cover action.

        """
        if not acknowledge_unsafe:
            msg = (
                "Cover movement is a potentially unsafe operation. "
                "Pass acknowledge_unsafe=True to confirm you are aware of the risk."
            )
            raise VioletUnsafeOperationError(msg)

        cover_key = COVER_FUNCTIONS.get(action.strip().upper())
        if not cover_key:
            msg = f"Unknown cover action '{action}'. Valid: {list(COVER_FUNCTIONS)}"
            raise VioletPoolAPIError(msg)

        return await self.set_switch_state(cover_key, ACTION_PUSH)

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
            temperature: The target temperature in °C.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletSetpointError: If ``temperature`` is outside the valid range
                (5–45 °C for heater, 5–55 °C for solar).

        """
        config_key = (
            "SOLAR_maxtemp" if climate_key.upper() == "SOLAR" else f"{climate_key}_set_temp"
        )
        return await self.set_target_value(config_key, float(temperature))

    async def set_ph_target(self, value: float) -> dict[str, Any]:
        """Update the pH setpoint.

        Args:
            value: The new pH target value (valid range: 6.0–8.0).

        Returns:
            A dictionary with the command result.

        Raises:
            VioletSetpointError: If ``value`` is outside the valid range or
                is not a finite number.

        """
        validate_setpoint(TARGET_PH, float(value))
        return await self.set_target_value(TARGET_PH, float(value))

    async def set_orp_target(self, value: int) -> dict[str, Any]:
        """Update the ORP setpoint.

        Args:
            value: The new ORP target value in mV (valid range: 500–900).

        Returns:
            A dictionary with the command result.

        Raises:
            VioletSetpointError: If ``value`` is outside the valid range or
                is not a finite number.

        """
        validate_setpoint(TARGET_ORP, float(value))
        return await self.set_target_value(TARGET_ORP, int(value))

    async def set_min_chlorine_level(self, value: float) -> dict[str, Any]:
        """Update the minimum chlorine level.

        Args:
            value: The new minimum chlorine level in mg/L (valid range: 0.0–5.0).

        Returns:
            A dictionary with the command result.

        Raises:
            VioletSetpointError: If ``value`` is outside the valid range or
                is not a finite number.

        """
        validate_setpoint(TARGET_MIN_CHLORINE, float(value))
        return await self.set_target_value(TARGET_MIN_CHLORINE, float(value))

    async def set_target_value(self, key: str, value: float) -> dict[str, Any]:
        """Send a generic target value update to the controller.

        For known setpoint keys (see ``SETPOINT_RANGES``), validation is
        performed automatically.  Call ``validate_setpoint()`` directly for
        keys not covered by the convenience methods.

        Args:
            key: The target key.
            value: The new value.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletSetpointError: If ``value`` is non-finite or outside a
                known valid range for ``key``.

        """
        validate_setpoint(key, float(value))
        return await self.set_config({key: value})

    async def set_dosing_parameters(
        self,
        parameters: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Update dosing parameters via /setConfig.

        The /setDosingParameters endpoint does not exist on the controller
        (firmware 1.1.9). All dosing parameters are written through
        POST /setConfig, just like other configuration values.

        Args:
            parameters: A mapping of dosing parameters.

        Returns:
            A dictionary with the command result.

        """
        return await self.set_config(dict(parameters))

    async def set_dosage_enabled(
        self,
        dosing_type: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Enable or disable a dosing function.

        Args:
            dosing_type: One of ``"pH-"``, ``"pH+"``, ``"Chlor"``,
                ``"Elektrolyse"``, ``"Flockmittel"``, ``"H2O2"``.
            enabled: True to enable, False to disable.

        Returns:
            A dictionary with the command result.

        Raises:
            VioletPoolAPIError: If the dosing type is unknown.

        """
        prefix = DOSING_CONFIG_PREFIX.get(dosing_type)
        if prefix is None:
            msg = f"Unknown dosing type '{dosing_type}'. Valid: {list(DOSING_CONFIG_PREFIX)}"
            raise VioletPoolAPIError(msg)

        return await self.set_config({f"{prefix}_use": 1 if enabled else 0})

    async def is_dosage_enabled(self, dosing_type: str) -> bool:
        """Check whether a dosing function is enabled.

        Args:
            dosing_type: One of ``"pH-"``, ``"pH+"``, ``"Chlor"``,
                ``"Elektrolyse"``, ``"Flockmittel"``, ``"H2O2"``.

        Returns:
            True if the dosing function is enabled.

        Raises:
            VioletPoolAPIError: If the dosing type is unknown.

        """
        prefix = DOSING_CONFIG_PREFIX.get(dosing_type)
        if prefix is None:
            msg = f"Unknown dosing type '{dosing_type}'. Valid: {list(DOSING_CONFIG_PREFIX)}"
            raise VioletPoolAPIError(msg)

        result = await self._request_json_dict(
            API_GET_CONFIG,
            query=f"{prefix}_use",
            payload_name="getConfig",
        )
        return bool(int(result.get(f"{prefix}_use", 0)))

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
            A dict with keys: code, severity, message, is_alarm, is_warning,
            is_info, is_reminder.

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
            "is_reminder": severity == ERROR_SEVERITY_REMINDER,
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

    async def get_log(
        self,
        log_type: str,
        page: int = 0,
    ) -> dict[str, Any]:
        """Fetch log entries from the controller.

        Args:
            log_type: One of ``LOG_TYPE_ACTIONS``, ``LOG_TYPE_SWITCHING``,
                ``LOG_TYPE_ONEWIRE`` (``"actions"``, ``"switching"``,
                ``"onewire"``).
            page: Page number (0-based). Use -1 to download the full
                actions log instead of paginated text.

        Returns:
            A dict with keys:
            - ``lines``: list of pipe-delimited log line strings
            - ``has_more``: True when ``LOAD_MORE`` sentinel was present
            - ``raw``: the raw text response

        """
        if page < 0 and log_type == "actions":
            query = "downloadActionsLog"
        else:
            query = f"{log_type}&{page}"

        resp = await self._request(
            API_GET_LOG,
            query=query,
            priority=API_PRIORITY_NORMAL,
        )
        text = resp.strip() if resp else ""
        lines = text.split("\n") if text else []
        has_more = lines and lines[-1].strip() == "LOAD_MORE"
        if has_more:
            lines = lines[:-1]
        lines = [ln for ln in lines if ln.strip()]
        return {"lines": lines, "has_more": has_more, "raw": text}

    async def get_notifications(self) -> dict[str, Any]:
        """Fetch all notification history from the controller.

        Returns:
            The JSON response dict where each key is a numeric ID and each
            value is a notification record with fields like DATE, TIME,
            SENSOR_ID, TYPE, TEXT, MAIL_STATE, etc.

        """
        return await self._request_json_dict(
            API_GET_NOTIFICATIONS,
            query="ALL",
            payload_name="getNotifications",
        )

    async def reset_blocking(self) -> dict[str, Any]:
        """Clear fault-induced blockings on the controller.

        Clears the ``BLOCKED_BY_ESC`` flag raised by empty-canister alarms
        and similar fault states so that dosing/control resumes after the
        underlying issue has been fixed (e.g. after refilling a canister).
        Equivalent to clicking "Reset" on the controller's web UI error page.

        Returns:
            A dict with the command result (``success`` flag and ``response``
            text from the controller).

        Raises:
            VioletPoolAPIError: If the API request fails.

        """
        body = await self._request(
            API_RESET_BLOCKING,
            method="GET",
            priority=API_PRIORITY_CRITICAL,
        )
        return self._command_result(body)

    async def set_can_amount(
        self,
        dosing_key: str,
        amount_ml: int,
        *,
        reset: bool = False,
    ) -> dict[str, Any]:
        """Set or reset the canister fill level for a dosing channel.

        Used after refilling or replacing a chemical canister so the
        controller's remaining-range calculation is accurate.

        Args:
            dosing_key: One of ``DOS_1_CL``, ``DOS_2_ELO``, ``DOS_4_PHM``,
                ``DOS_5_PHP``, ``DOS_6_FLOC``.  H2O2 shares ``DOS_1_CL``
                with Chlorine and is not a separate key here.
            amount_ml: New fill level in millilitres (must be > 0).
            reset: When True, also resets the daily-dosing counter and the
                "last can reset" timestamp (firmware action ``RESET``).
                When False (default), only adjusts the fill level
                (firmware action ``ADJUST``) and leaves the daily counter
                untouched.

        Returns:
            A dict with the command result.

        Raises:
            VioletPoolAPIError: If ``dosing_key`` is unknown or the API
                request fails.
            ValueError: If ``amount_ml`` is not positive.

        """
        cid = DOSING_CANISTER_ID.get(dosing_key)
        if cid is None:
            msg = (
                f"Unknown dosing key for set_can_amount: {dosing_key!r}. "
                f"Expected one of: {sorted(DOSING_CANISTER_ID)}"
            )
            raise VioletPoolAPIError(msg)
        if amount_ml <= 0:
            raise ValueError(f"amount_ml must be > 0, got {amount_ml}")

        action = "RESET" if reset else "ADJUST"
        form_data = {
            "action": action,
            "which": dosing_key,
            "amount": str(int(amount_ml)),
            "cid": str(cid),
        }
        body = await self._request(
            API_SET_CAN_AMOUNT,
            method="POST",
            data=form_data,
            priority=API_PRIORITY_CRITICAL,
        )
        return self._command_result(body)

    async def set_system_service(
        self,
        service: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """Enable or disable a controller-side system service.

        The controller exposes per-service ``/enable*`` and ``/disable*``
        endpoints (FTP, Samba, SSH, Shairport/AirPlay, Homebridge/HomeKit,
        Alexa, cloud tunnel, support tunnel).  State can be queried via
        :meth:`get_system_services`.

        Args:
            service: One of the keys in
                :data:`~violet_poolcontroller_api.const_api.SYSTEM_SERVICES`
                (``"ftp"``, ``"samba"``, ``"ssh"``, ``"shairport"``,
                ``"homebridge"``, ``"alexa"``, ``"tunnel"``,
                ``"support_tunnel"``).
            enabled: True to enable, False to disable.

        Returns:
            A dict with the command result.

        Raises:
            VioletPoolAPIError: If ``service`` is unknown or the request fails.

        """
        info = SYSTEM_SERVICES.get(service)
        if info is None:
            msg = (
                f"Unknown system service: {service!r}. "
                f"Expected one of: {sorted(SYSTEM_SERVICES)}"
            )
            raise VioletPoolAPIError(msg)

        endpoint = info["enable_endpoint"] if enabled else info["disable_endpoint"]
        body = await self._request(
            endpoint,
            method="GET",
            priority=API_PRIORITY_CRITICAL,
        )
        return self._command_result(body)

    async def get_system_services(self) -> dict[str, bool]:
        """Return the live state of all controller-side system services.

        Wraps ``GET /getServiceStates`` and normalises each value to a
        boolean.  Services whose state is not reported by the controller
        (currently only Alexa) are absent from the returned dict.

        Returns:
            A dict mapping service key (``"ftp"``, ``"samba"``, ...) to a
            boolean enabled state.

        Raises:
            VioletPoolAPIError: If the request fails or the payload is
                missing the expected keys.

        """
        raw = await self._request_json_dict(
            API_GET_SERVICE_STATES,
            payload_name="getServiceStates",
        )

        result: dict[str, bool] = {}
        for service, info in SYSTEM_SERVICES.items():
            state_key = info.get("state_key", "")
            if not state_key:
                continue
            if state_key in raw:
                result[service] = bool(int(raw[state_key]))
        return result

    # ------------------------------------------------------------------
    # OmniTronic multi-port valve + RS485 pump + live trace
    # ------------------------------------------------------------------

    async def set_omni_position(self, position: int) -> dict[str, Any]:
        """Drive the OmniTronic multi-port valve to a fixed position.

        Sends ``setFunctionManually?OMNI,OMNI_DC<N>``.  The controller
        physically rotates the valve; the pump and dependent outputs
        (heater/solar/dosing) are blocked with priority 5 while the valve
        is moving.  Typical change-over is ~3 s per step.

        Position 0 ("Filtration") has a special meaning: it also clears the
        BACKWASH_RULE and releases any manual override, returning the
        controller to automatic mode.  Use it after a manual backwash or
        after positioning the valve at any other port.

        Args:
            position: Valve position (0-5).  0=Filtration/AUTO,
                1-5=other physical ports (backwash, rinse, waste, ... –
                exact meaning depends on the valve's plumbing).

        Returns:
            A dict with the command result.

        Raises:
            VioletPoolAPIError: If ``position`` is out of range or the
                request fails.

        """
        if position not in OMNI_POSITIONS:
            msg = (
                f"Invalid OmniTronic position: {position!r}. "
                f"Must be one of {sorted(OMNI_POSITIONS)}"
            )
            raise VioletPoolAPIError(msg)
        state_token = OMNI_POSITIONS[position]
        url = f"{API_SET_FUNCTION_MANUALLY}?OMNI,{state_token},0,0"
        body = await self._request(
            url,
            method="GET",
            priority=API_PRIORITY_CRITICAL,
        )
        return self._command_result(body)

    async def get_rs485_pump_data(
        self,
        pump_name: str,
    ) -> dict[str, Any]:
        """Return live data and register config for an RS485 pump.

        Wraps ``GET /getRS485PumpData?<pumpName>``.  The response combines
        the static register map from ``config/RS485_PUMP/<NAME>.json`` with
        live values: pump power consumption (Watts), flow rate (depending on
        the configured flow monitor), pump-blocked flag, BACKWASH_STEP and
        a SLAVE_PRESENT flag.

        Args:
            pump_name: Pump model identifier (e.g. ``"BADU_ECO_DRIVE_II"``).
                See :data:`~violet_poolcontroller_api.const_api.RS485_PUMP_NAMES`
                for the known names.

        Returns:
            The full JSON dict returned by the controller.

        Raises:
            VioletPoolAPIError: If ``pump_name`` is unknown or the request
                fails.

        """
        if pump_name not in RS485_PUMP_NAMES:
            msg = (
                f"Unknown RS485 pump name: {pump_name!r}. "
                f"Expected one of {RS485_PUMP_NAMES}"
            )
            raise VioletPoolAPIError(msg)
        url = f"{API_GET_RS485_PUMP_DATA}?{pump_name}"
        body = await self._request(
            url,
            method="GET",
            priority=API_PRIORITY_NORMAL,
            expect_json=True,
        )
        if isinstance(body, dict):
            return body
        return {"raw": body}

    async def set_rs485_live(
        self,
        pump_name: str,
        slave_id: int,
        mode: str,
        level: float,
    ) -> str:
        """Send live control data to an RS485 variable-speed pump.

        Wraps ``GET /setRS485Live?<pumpName>,<slaveID>,<mode>,<level>``.
        While live mode is active the controller blocks its normal RS485
        polling for ~3 s after each call – call :meth:`end_rs485_live`
        when you're done to release the bus.

        Args:
            pump_name: Pump model identifier (see
                :data:`~violet_poolcontroller_api.const_api.RS485_PUMP_NAMES`).
            slave_id: Modbus slave ID of the pump (usually 1).
            mode: Control mode – one of ``"rpm"``, ``"pwr"`` or ``"hz"``.
                Which modes are valid depends on the pump model (most BADU
                pumps expose only ``"hz"`` – check
                ``MOTIONCONTROLMODE_VALIDMODES`` in the pump config).
            level: Target value (RPM, kW, or Hz).  Clamped to the pump's
                ``SETTARGET_*_VALIDMIN`` / ``VALIDMAX`` on the controller.

        Returns:
            The register/value string the controller forwards to the pump's
            modbus interface (e.g. ``"1|0,0|2,4500"``).

        Raises:
            VioletPoolAPIError: If arguments are invalid or the request fails.

        """
        if pump_name not in RS485_PUMP_NAMES:
            msg = (
                f"Unknown RS485 pump name: {pump_name!r}. "
                f"Expected one of {RS485_PUMP_NAMES}"
            )
            raise VioletPoolAPIError(msg)
        if mode.lower() not in RS485_PUMP_MODES:
            msg = (
                f"Invalid RS485 mode: {mode!r}. "
                f"Expected one of {RS485_PUMP_MODES}"
            )
            raise VioletPoolAPIError(msg)
        if slave_id < 1 or slave_id > 247:
            raise ValueError(f"slave_id must be 1-247, got {slave_id}")

        url = (
            f"{API_SET_RS485_LIVE}?{pump_name},{int(slave_id)},"
            f"{mode.lower()},{level}"
        )
        body = await self._request(
            url,
            method="GET",
            priority=API_PRIORITY_CRITICAL,
        )
        text = str(body) if body is not None else ""
        # Firmware JSON-encodes the response (res.write(JSON.stringify(...))),
        # so strip surrounding quotes for the common single-string case.
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        return text

    async def end_rs485_live(self) -> str:
        """End an RS485 live-control session and release the bus.

        Sends ``GET /setRS485Live?DONE``.  Always call this when finished
        with :meth:`set_rs485_live`, otherwise the controller keeps the
        normal RS485 polling paused for ~3 s after each call.

        Returns:
            The response string from the controller (usually ``"DONE"``).

        """
        body = await self._request(
            f"{API_SET_RS485_LIVE}?DONE",
            method="GET",
            priority=API_PRIORITY_CRITICAL,
        )
        text = str(body) if body is not None else ""
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        return text

    async def get_live_trace(self) -> dict[str, str]:
        """Return a single-row snapshot of every controller reading.

        Wraps ``GET /getLiveTrace``.  The controller returns a 3-line
        text/plain body (header row, units row, values row) with
        semicolon-separated fields and German decimal commas.  This method
        splits the rows and zips header→value into a dict (parsing values
        as ``float`` when possible, falling back to the raw string).

        Useful for ad-hoc troubleshooting dashboards – the controller does
        not document this endpoint as stable, so prefer the typed
        :meth:`get_readings` for production use.

        Returns:
            A dict mapping the header field names to their current values.

        Raises:
            VioletPoolAPIError: If the request fails or the payload is
                malformed.

        """
        body = await self._request(
            API_GET_LIVE_TRACE,
            method="GET",
            priority=API_PRIORITY_NORMAL,
        )
        text = str(body) if body is not None else ""
        lines = text.splitlines()
        if len(lines) < 3:
            msg = f"Malformed getLiveTrace payload: expected 3 lines, got {len(lines)}"
            raise VioletPoolAPIError(msg)
        header = lines[0].split(";")
        values = lines[2].split(";")
        result: dict[str, str] = {}
        for key, raw_value in zip(header, values, strict=False):
            key = key.strip()
            if not key:
                continue
            result[key] = raw_value.replace(",", ".").strip()
        return result

    async def init_update(self) -> str:
        """Trigger firmware update installation on the controller.

        The controller downloads and installs the update, then restarts
        (takes ~30 seconds). Returns "STARTING" on success.

        Returns:
            Response string from the controller (e.g. "STARTING").

        Raises:
            VioletPoolAPIError: If the API call fails or auth is rejected.

        """
        resp = await self._request(
            API_INIT_UPDATE,
            method="GET",
            priority=API_PRIORITY_CRITICAL,
        )
        return str(resp).strip() if resp else ""

    async def get_update_state(self) -> str:
        """Fetch the current firmware update progress log.

        The controller writes progress to /home/violet/log/update.log
        during an active update. Returns "STANDBY" when no update is running.

        Returns:
            Raw update log string or "STANDBY".

        Raises:
            VioletPoolAPIError: If the API call fails.

        """
        resp = await self._request(
            API_GET_UPDATE_STATE,
            method="GET",
            priority=API_PRIORITY_NORMAL,
        )
        return str(resp).strip() if resp else "STANDBY"

    async def get_update_history(self) -> str:
        """Fetch formatted release notes for recent firmware versions.

        The controller fetches notes from the PoolDigital update server and
        returns them pre-formatted with HTML bullet points.

        Returns:
            HTML-formatted release notes string, or empty string on error.

        Raises:
            VioletPoolAPIError: If the API call fails.

        """
        resp = await self._request(
            API_GET_UPDATE_HISTORY,
            method="GET",
            priority=API_PRIORITY_NORMAL,
        )
        return str(resp).strip() if resp else ""

    async def get_output_runtimes(self) -> dict[str, Any]:
        """Fetch output runtime statistics from the controller.

        Returns a flat dict with runtime (HH:MM:SS format) and last-on/off
        (ISO datetime strings) for all outputs: PUMP, SOLAR, HEATER, BACKWASH,
        REFILL, LIGHT, ECO, all dosing outputs, OMNI_DC channels, and extension
        relay channels.  Also includes CPU_UPTIME, LOAD_AVG, and version fields.

        Returns:
            Dict with runtime/timestamp strings for all outputs, or empty dict
            on error.

        Raises:
            VioletPoolAPIError: If the API call fails.

        """
        resp = await self._request(
            API_GET_OUTPUT_RUNTIMES,
            method="GET",
            priority=API_PRIORITY_NORMAL,
        )
        if isinstance(resp, dict):
            return resp
        return {}
