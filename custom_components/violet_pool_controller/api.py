"""HTTP client utilities for the Violet Pool Controller."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Mapping
from urllib.parse import quote

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
    API_GET_HISTORY,
    API_GET_OUTPUT_STATES,
    API_GET_OVERALL_DOSING,
    API_GET_WEATHER_DATA,
    API_GET_CALIB_HISTORY,
    API_GET_CALIB_RAW_VALUES,
    API_GET_CONFIG,
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
    TARGET_MIN_CHLORINE,
    TARGET_ORP,
    TARGET_PH,
    API_PRIORITY_NORMAL,
    API_PRIORITY_HIGH,
    API_PRIORITY_CRITICAL,
)
from .utils_rate_limiter import get_global_rate_limiter

_LOGGER = logging.getLogger(__name__)


class VioletPoolAPIError(Exception):
    """Raised when the Violet Pool Controller API returns an error."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        """Store a message and an optional machine-readable error code."""

        super().__init__(message)
        self.error_code = (error_code or "unknown").lower()


class VioletPoolAPI:
    """Tiny HTTP client used by the integration to talk to the controller."""

    _DOSING_TYPE_TO_KEY = {
        "pH-": "DOS_4_PHM",
        "pH+": "DOS_5_PHP",
        "Chlor": "DOS_1_CL",
        "Flockmittel": "DOS_6_FLOC",
    }

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
        """Initialise the API helper."""

        if session is None:
            raise ValueError("A valid aiohttp session must be provided")

        protocol = "https" if use_ssl else "http"
        if host.startswith("http://") or host.startswith("https://"):
            base = host
        else:
            base = f"{protocol}://{host}"
        self._base_url = base.rstrip("/")

        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=max(float(timeout), 1.0))
        self._max_retries = max(1, int(max_retries))
        self._auth = None
        if username:
            self._auth = aiohttp.BasicAuth(username, password or "")

        # ✅ RATE LIMITING: Schützt Controller vor Überlastung
        self._rate_limiter = get_global_rate_limiter()
        _LOGGER.debug("API initialized with rate limiting enabled")

    # ---------------------------------------------------------------------
    # Generic helpers
    # ---------------------------------------------------------------------

    def _build_url(self, endpoint: str) -> str:
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
        """
        Perform a request and handle retries as well as error reporting.

        ✅ RATE LIMITING: Wartet automatisch wenn Request-Limit erreicht ist.

        Args:
            endpoint: API-Endpoint
            method: HTTP-Methode
            params: URL-Parameter
            query: Query-String
            json_payload: JSON-Payload
            expect_json: Erwarte JSON-Response
            priority: Request-Priorität (1=critical, 2=high, 3=normal, 4=low)

        Returns:
            API-Response (JSON oder Text)

        Raises:
            VioletPoolAPIError: Bei API-Fehlern
        """

        if params and query:
            raise ValueError("'params' and 'query' are mutually exclusive")

        # ✅ RATE LIMITING: Warte wenn nötig (max 10s timeout)
        try:
            await self._rate_limiter.wait_if_needed(priority=priority, timeout=10.0)
        except asyncio.TimeoutError:
            _LOGGER.warning(
                "Rate limiter timeout für %s (priority: %d) - fahre fort",
                endpoint,
                priority
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

            except (aiohttp.ClientError, asyncio.TimeoutError) as err:  # pragma: no cover - network failure
                last_error = VioletPoolAPIError(
                    f"Error communicating with Violet controller: {err}"
                )
                _LOGGER.debug("Attempt %d for %s failed: %s", attempt, endpoint, err)
                if attempt == self._max_retries:
                    raise last_error
                # ✅ PERFORMANCE: Exponential backoff with jitter (0.2s, 0.4s, 0.8s, 1.6s, max 2.0s)
                delay = min(2.0, 0.2 * (2 ** (attempt - 1)))
                await asyncio.sleep(delay)

        if last_error:
            raise last_error
        raise VioletPoolAPIError("Request failed without raising an error")

    @staticmethod
    def _command_result(body: str) -> dict[str, Any]:
        """Normalise the controller response for command style requests."""

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
        """Render the command payload according to the device parameter template."""

        template = DEVICE_PARAMETERS.get(key, {}).get(
            "api_template", f"{key},{{action}},{{duration}},{{value}}"
        )
        payload_data = {
            "action": action,
            "duration": int(duration or 0),
            "speed": int(last_value or 0),
            "value": int(last_value or 0),
        }
        try:
            return template.format_map(payload_data)
        except KeyError as err:  # pragma: no cover - template misconfiguration
            raise VioletPoolAPIError(
                f"Template for {key} requires missing field: {err.args[0]}"
            ) from err

    # ---------------------------------------------------------------------
    # Public API surface
    # ---------------------------------------------------------------------

    async def get_readings(self) -> dict[str, Any]:
        """Return the complete data set from the controller."""

        response = await self._request(
            API_READINGS,
            params={"ALL": ""},
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getReadings")
        return response

    async def get_device_info(self) -> dict[str, Any]:
        """Fetch basic device metadata to verify connectivity."""

        data = await self.get_readings()

        def _lookup(keys: tuple[str, ...]) -> Any:
            """Search common sections for the first matching key."""

            sections: tuple[Mapping[str, Any] | Any, ...] = (
                data,
                data.get("DEVICE", {}),
                data.get("SYSTEM", {}),
                data.get("NETWORK", {}),
            )

            for key in keys:
                for section in sections:
                    if isinstance(section, Mapping) and key in section:
                        return section[key]
            return None

        raw_device_id = _lookup(("device_id", "DEVICE_ID", "deviceId", "SERIAL_NUMBER", "serial"))
        try:
            device_id = int(str(raw_device_id).strip()) if raw_device_id is not None else 1
        except (ValueError, TypeError):
            device_id = 1

        raw_name = _lookup(("device_name", "DEVICE_NAME", "name", "controller_name"))
        device_name = str(raw_name).strip() if raw_name else "Violet Pool Controller"

        return {"device_id": device_id, "device_name": device_name}

    async def get_specific_readings(self, categories: list[str] | tuple[str, ...]) -> dict[str, Any]:
        """Return a reduced data set for the provided categories."""

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

    async def get_history(self, *, hours: int = 24, sensor: str = "ALL") -> dict[str, Any]:
        """Fetch historical readings from the controller."""

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
        """Return the current weather information used by the controller."""

        response = await self._request(
            API_GET_WEATHER_DATA,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getWeatherdata")
        return response

    async def get_overall_dosing(self) -> dict[str, Any]:
        """Return aggregated dosing statistics."""

        response = await self._request(
            API_GET_OVERALL_DOSING,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getOverallDosing")
        return response

    async def get_output_states(self) -> dict[str, Any]:
        """Return detailed information about output states."""

        response = await self._request(
            API_GET_OUTPUT_STATES,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getOutputstates")
        return response

    async def get_config(self, parameters: list[str] | tuple[str, ...]) -> dict[str, Any]:
        """Fetch controller configuration values for the provided keys."""

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
        """Update controller configuration values."""

        if not config:
            raise VioletPoolAPIError("Configuration payload must not be empty")

        body = await self._request(
            API_SET_CONFIG,
            method="POST",
            json_payload=dict(config),
        )
        return self._command_result(body)

    async def get_calibration_raw_values(self) -> dict[str, Any]:
        """Return current raw values for all calibration sensors."""

        response = await self._request(
            API_GET_CALIB_RAW_VALUES,
            expect_json=True,
        )
        if not isinstance(response, dict):
            raise VioletPoolAPIError("Unexpected payload returned from getCalibRawValues")
        return response

    async def get_calibration_history(self, sensor: str) -> list[dict[str, str]]:
        """Return the calibration history for the provided sensor."""

        if not sensor:
            raise VioletPoolAPIError("Sensor name required for calibration history")

        response = await self._request(
            API_GET_CALIB_HISTORY,
            query=sensor,
            expect_json=False,
        )

        entries: list[dict[str, str]] = []
        for line in (response or "").strip().splitlines():
            parts = [part.strip() for part in line.split("|") if part.strip()]
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
        """Restore a previous calibration entry for the given sensor."""

        if not sensor or not timestamp:
            raise VioletPoolAPIError("Sensor and timestamp are required for calibration restore")

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
        """Activate the controller output test mode."""

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
        """Control a function output via /setFunctionManually."""

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
        """Trigger a dosing run using the manual function endpoint."""

        device_key = self._DOSING_TYPE_TO_KEY.get(dosing_type)
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
        """Enable or disable PV surplus mode."""

        return await self.set_switch_state(
            "PVSURPLUS",
            ACTION_ON if active else ACTION_OFF,
            last_value=pump_speed,
        )

    async def set_all_dmx_scenes(self, action: str) -> dict[str, Any]:
        """Send the same command to all DMX scenes."""

        if action not in {ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO}:
            raise VioletPoolAPIError(f"Unsupported DMX action: {action}")

        results = []
        for scene in range(1, 13):
            key = f"DMX_SCENE{scene}"
            results.append(await self.set_switch_state(key, action))

        success = all(result.get("success", True) for result in results)
        response = ", ".join(result.get("response", "") for result in results if result.get("response"))
        return {"success": success, "response": response}

    async def set_light_color_pulse(self) -> dict[str, Any]:
        """Trigger the colour pulse animation for the pool light."""

        return await self.set_switch_state("LIGHT", ACTION_COLOR)

    async def trigger_digital_input_rule(self, rule_key: str) -> dict[str, Any]:
        """Trigger a digital input rule via PUSH action."""

        return await self.set_switch_state(rule_key, ACTION_PUSH)

    async def set_digital_input_rule_lock(
        self,
        rule_key: str,
        locked: bool,
    ) -> dict[str, Any]:
        """Lock or unlock a digital input rule."""

        return await self.set_switch_state(
            rule_key,
            ACTION_LOCK if locked else ACTION_UNLOCK,
        )

    async def set_device_temperature(
        self,
        climate_key: str,
        temperature: float,
    ) -> dict[str, Any]:
        """Set the target temperature for heater or solar circuits."""

        target_key = f"{climate_key}_TARGET_TEMP"
        return await self.set_target_value(target_key, float(temperature))

    async def set_ph_target(self, value: float) -> dict[str, Any]:
        """Update the pH set point."""

        return await self.set_target_value(TARGET_PH, float(value))

    async def set_orp_target(self, value: int) -> dict[str, Any]:
        """Update the ORP set point."""

        return await self.set_target_value(TARGET_ORP, int(value))

    async def set_min_chlorine_level(self, value: float) -> dict[str, Any]:
        """Update the minimum chlorine level."""

        return await self.set_target_value(TARGET_MIN_CHLORINE, float(value))

    async def set_target_value(self, key: str, value: float | int) -> dict[str, Any]:
        """Send a generic target value update to the controller."""

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
        """Update dosing parameters via the dedicated endpoint."""

        body = await self._request(
            API_SET_DOSING_PARAMETERS,
            method="POST",
            json_payload=dict(parameters),
        )
        return self._command_result(body)
