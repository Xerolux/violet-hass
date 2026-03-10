"""Violet Pool Controller device management."""

from __future__ import annotations

import asyncio
import collections
import logging
import time
from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any

from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue, async_delete_issue
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError
from .const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_ENABLE_DIAGNOSTIC_LOGGING,
    CONF_POLLING_INTERVAL,
    CONF_USE_SSL,
    DEFAULT_CONTROLLER_NAME,
    DEFAULT_ENABLE_DIAGNOSTIC_LOGGING,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

FAILURE_LOG_INTERVAL = 300  # Log repeated failures at most every 5 minutes


class VioletPoolControllerDevice:
    """Violet Pool Controller Device - SMART LOGGING + AUTO RECOVERY."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, api: VioletPoolAPI
    ) -> None:
        """Initialize the device instance."""
        self.hass = hass
        self.config_entry = config_entry
        self.api = api
        self._available = False
        self._session = async_get_clientsession(hass)
        self._data: dict[str, Any] = {}
        self._firmware_version: str | None = None
        self._last_error: str | None = None
        self._api_lock = asyncio.Lock()
        self._consecutive_failures = 0
        self._max_consecutive_failures = 5
        self._update_counter = 0
        # Increased history size to capture more context for troubleshooting
        self._poll_history: collections.deque[tuple[datetime, int, float, dict[str, Any]]] = collections.deque(maxlen=1000)
        self._first_poll: datetime | None = None

        self._last_failure_log = 0.0  # Timestamp for throttling
        self._first_failure_logged = False  # Flag for first warning
        self._recovery_logged = False  # Flag for recovery message
        self._fw_logged = False  # Flag for firmware version logging

        # ✅ DIAGNOSTIC SENSORS: Connection health monitoring
        self._last_update_time = 0.0  # Timestamp of last successful update
        self._connection_latency = 0.0  # Last connection latency in milliseconds
        self._system_health = 100.0  # System health percentage (0-100)

        # ✅ DIAGNOSTIC SENSORS: Advanced metrics
        self._api_request_count = 0  # Total API requests
        self._api_request_start_time = time.monotonic()  # For rate calculation
        self._latency_history: list[
            float
        ] = []  # Rolling window for average latency (max 60 samples)

        entry_data = config_entry.data
        entry_options = config_entry.options
        self.api_url = self._extract_api_url(entry_data)
        self.use_ssl = entry_data.get(CONF_USE_SSL, True)
        self.device_id = entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        # Prefer options (later changes) over data
        self.controller_name = entry_options.get(
            CONF_CONTROLLER_NAME,
            entry_data.get(CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME),
        )
        # ✅ DIAGNOSTIC LOGGING: Read from options (priority), then data, then default
        self._enable_diagnostic_logging = entry_options.get(
            CONF_ENABLE_DIAGNOSTIC_LOGGING,
            entry_data.get(CONF_ENABLE_DIAGNOSTIC_LOGGING, DEFAULT_ENABLE_DIAGNOSTIC_LOGGING),
        )

        _LOGGER.info(
            "Device initialized: '%s' (Controller: %s, URL: %s, SSL: %s, "
            "Device-ID: %d)",
            self.device_name,
            self.controller_name,
            self.api_url,
            self.use_ssl,
            self.device_id,
        )

    async def update_api_config(self, new_config_entry: ConfigEntry) -> bool:
        """Update API configuration dynamically without full reload.

        Args:
            new_config_entry: The updated config entry with new settings.

        Returns:
            True if configuration was updated successfully, False otherwise.
        """
        from violet_poolcontroller_api.api import VioletPoolAPI
        from .const import (
            CONF_ENABLE_DIAGNOSTIC_LOGGING,
            CONF_PASSWORD,
            CONF_RETRY_ATTEMPTS,
            CONF_TIMEOUT_DURATION,
            CONF_USERNAME,
            DEFAULT_ENABLE_DIAGNOSTIC_LOGGING,
            DEFAULT_RETRY_ATTEMPTS,
            DEFAULT_TIMEOUT_DURATION,
        )

        try:
            # Extract new configuration from BOTH data and options
            entry_data = new_config_entry.data
            entry_options = new_config_entry.options

            new_api_url = self._extract_api_url(entry_data)
            new_use_ssl = entry_data.get(CONF_USE_SSL, True)
            new_username = entry_data.get(CONF_USERNAME)
            new_password = entry_data.get(CONF_PASSWORD)

            # Check options first, then data for timeout/retries
            new_timeout = entry_options.get(
                CONF_TIMEOUT_DURATION,
                entry_data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION),
            )
            new_retries = entry_options.get(
                CONF_RETRY_ATTEMPTS,
                entry_data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS),
            )

            # ✅ DIAGNOSTIC LOGGING: Check if setting changed
            new_diagnostic_logging = entry_options.get(
                CONF_ENABLE_DIAGNOSTIC_LOGGING,
                entry_data.get(CONF_ENABLE_DIAGNOSTIC_LOGGING, DEFAULT_ENABLE_DIAGNOSTIC_LOGGING),
            )
            diagnostic_logging_changed = new_diagnostic_logging != self._enable_diagnostic_logging

            # Check if connection settings changed by comparing with current values
            # Note: We compare with device settings, using public API properties
            connection_changed = (
                new_api_url != self.api_url
                or new_use_ssl != self.use_ssl
                or new_timeout != self.api.timeout
                or int(new_retries) != self.api.max_retries
            )

            # Auth changes are harder to detect without storing credentials
            # For username/password changes, we assume change if explicitly provided in options
            # or if they differ from initial setup
            auth_in_options = (
                entry_options.get(CONF_USERNAME) is not None
                or entry_options.get(CONF_PASSWORD) is not None
            )
            if auth_in_options:
                connection_changed = True

            # ✅ DIAGNOSTIC LOGGING: Apply change if detected
            if diagnostic_logging_changed:
                self._enable_diagnostic_logging = new_diagnostic_logging
                _LOGGER.info(
                    "Diagnostic logging %s",
                    "ENABLED 📊" if new_diagnostic_logging else "DISABLED",
                )
                return True

            if not connection_changed:
                _LOGGER.debug("API configuration unchanged, no update needed")
                return False

            _LOGGER.info(
                "Updating API configuration (URL: %s→%s, SSL: %s→%s, Timeout: %s→%s, Retries: %s→%s)",
                self.api_url,
                new_api_url,
                self.use_ssl,
                new_use_ssl,
                self.api.timeout,
                new_timeout,
                self.api.max_retries,
                int(new_retries),
            )

            # Create new API instance with updated configuration
            # IMPORTANT: Do NOT close the session - it's managed by Home Assistant!
            # We just create a new API object that uses the same session
            new_api = VioletPoolAPI(
                host=new_api_url,
                session=self._session,  # Reuse the HA session, don't close it!
                username=new_username,
                password=new_password,
                use_ssl=new_use_ssl,
                verify_ssl=True,  # Always verify SSL
                timeout=new_timeout,
                max_retries=int(new_retries),
            )

            # Replace the old API with the new one
            self.api = new_api

            # Update device configuration
            self.api_url = new_api_url
            self.use_ssl = new_use_ssl

            _LOGGER.info("API configuration updated successfully (new API instance created)")
            return True

        except Exception as err:
            _LOGGER.error("Failed to update API configuration: %s", err)
            return False

    def _should_log_failure(self) -> bool:
        """
        Check if failure should be logged (throttling).

        ✅ LOGGING OPTIMIZATION: Prevents log spam for persistent issues.

        Returns:
            True if failure should be logged, False otherwise.
        """
        now = time.monotonic()

        if now - self._last_failure_log > FAILURE_LOG_INTERVAL:
            self._last_failure_log = now
            return True
        return False

    async def async_update(self) -> dict[str, Any]:
        """
        Fetch and return updated device data from the controller.

        Returns a NEW dict copy on every successful update so that
        HA's DataUpdateCoordinator detects a data change and notifies
        all entity listeners.  Returning the same mutable reference
        caused HA 2025.12+ to skip entity state writes because
        ``self.data is new_data`` evaluated to True.
        """
        try:
            async with self._api_lock:
                # ✅ DIAGNOSTIC: Measure connection latency
                start_time = time.monotonic()
                self._api_request_count += 1  # Track API requests
                data = await self._fetch_controller_data()
                # Convert to milliseconds
                self._connection_latency = (time.monotonic() - start_time) * 1000

                # ✅ DIAGNOSTIC: Update latency history (rolling window of 60 samples)
                self._latency_history.append(self._connection_latency)
                if len(self._latency_history) > 60:
                    self._latency_history.pop(0)

                if not data or not isinstance(data, dict):
                    self._consecutive_failures += 1

                    if self._consecutive_failures == 1:
                        if self._available or len(self._data) > 0:
                            _LOGGER.warning(
                                "Controller '%s' returned empty/invalid data (attempt %d)",
                                self.device_name,
                                self._consecutive_failures,
                            )
                            self._first_failure_logged = True
                            self._recovery_logged = False
                        else:
                            # During initial setup use debug level
                            _LOGGER.debug(
                                "Controller '%s' not responding (setup phase)",
                                self.device_name,
                            )

                    elif self._consecutive_failures >= self._max_consecutive_failures:
                        _LOGGER.error(
                            "Controller '%s' marked unavailable after %d consecutive failures.",
                            self.device_name,
                            self._consecutive_failures,
                        )
                        self._available = False

                        # Create a repair issue so users are notified in HA UI
                        async_create_issue(
                            self.hass,
                            DOMAIN,
                            f"controller_unavailable_{self.config_entry.entry_id}",
                            is_fixable=True,
                            is_persistent=True,
                            severity=IssueSeverity.ERROR,
                            translation_key="controller_unavailable",
                            translation_placeholders={
                                "name": self.device_name,
                                "failures": str(self._consecutive_failures),
                            },
                        )

                        raise UpdateFailed(
                            f"Controller '{self.device_name}' unreachable "
                            f"({self._consecutive_failures} failures)"
                        )

                    elif self._should_log_failure():
                        _LOGGER.warning(
                            "Controller '%s' still unreachable "
                            "(%d/%d consecutive failures)",
                            self.device_name,
                            self._consecutive_failures,
                            self._max_consecutive_failures,
                        )

                    # ✅ DIAGNOSTIC: Degrade system health based on failures
                    self._system_health = max(
                        0.0, 100.0 - (self._consecutive_failures * 20.0)
                    )

                    # Return a COPY of stale data so coordinator sees a new object
                    return dict(self._data) if self._data else {}

                if self._consecutive_failures > 0 and not self._recovery_logged:
                    _LOGGER.info(
                        "Controller '%s' reachable again (after %d failure%s)",
                        self.device_name,
                        self._consecutive_failures,
                        "s" if self._consecutive_failures > 1 else "",
                    )
                    self._recovery_logged = True
                    self._first_failure_logged = False

                    # Delete the repair issue when controller is available again
                    async_delete_issue(
                        self.hass,
                        DOMAIN,
                        f"controller_unavailable_{self.config_entry.entry_id}",
                    )

                # ✅ FIX: Always replace _data with a fresh dict to ensure
                # HA's DataUpdateCoordinator detects the change.
                self._data = dict(data)
                self._available = True
                self._consecutive_failures = 0
                self._last_error = None

                # ✅ DIAGNOSTIC: Update health metrics
                self._last_update_time = time.monotonic()
                self._system_health = 100.0  # Perfect health

                # Firmware-Version extrahieren (mehrere Fallbacks)
                fw_candidates = [
                    data.get("FW"),
                    data.get("fw"),
                    data.get("SW_VERSION"),
                    data.get("sw_version"),
                    data.get("VERSION"),
                    data.get("version"),
                    data.get("SW_VERSION_CARRIER"),
                    data.get("FIRMWARE_VERSION"),
                    data.get("firmware_version"),
                ]
                for candidate in fw_candidates:
                    if candidate is not None and str(candidate).strip():
                        self._firmware_version = str(candidate).strip()
                        break

                # Debug-Log nur wenn Firmware gefunden wurde und noch nicht geloggt
                if self._firmware_version and not self._fw_logged:
                    _LOGGER.debug(
                        "Firmware-Version erkannt: %s", self._firmware_version
                    )
                    self._fw_logged = True

                # ✅ FIX: Return a NEW dict so the coordinator always
                # receives a distinct object, triggering entity updates.
                self._update_counter += 1

                # Record Poll History
                now_dt = datetime.now()
                if self._first_poll is None:
                    self._first_poll = now_dt

                # Create snapshot of key values
                snapshot = {
                    "Pool Temp": data.get("onewire1_value"),
                    "Redox": data.get("orp_value"),
                    "pH": data.get("pH_value"),
                    "Chlorine": data.get("pot_value"),
                    "Overflow": data.get("ADC2_value"),
                    "Flow": data.get("IMP2_value") if data.get("IMP2_value") is not None else data.get("ADC3_value"),
                    "Inflow": data.get("IMP1_value"),
                }
                # Remove None values to save space/cleaner logs
                snapshot = {k: v for k, v in snapshot.items() if v is not None}

                self._poll_history.append((now_dt, len(data), self._connection_latency, snapshot))

                # Standard Debug-Log (immer aktiv)
                _LOGGER.debug(
                    "Update #%d for '%s': %d keys fetched in %.3fs",
                    self._update_counter,
                    self.device_name,
                    len(data),
                    self._connection_latency / 1000,  # Convert ms to seconds
                )

                # ✅ DIAGNOSTIC LOGGING: Erweiterte Informationen (optional)
                if self._enable_diagnostic_logging:
                    # Liste der geänderten Keys seit letztem Update
                    changed_keys = set(data.keys()) - set(self._data.keys()) if self._data else set(data.keys())
                    if changed_keys:
                        _LOGGER.info(
                            "📊 Update #%d: %d new/changed keys: %s%s",
                            self._update_counter,
                            len(changed_keys),
                            ", ".join(sorted(changed_keys)[:20]),  # Max 20 keys
                            "..." if len(changed_keys) > 20 else "",
                        )

                    # Verbindungs-Metriken
                    _LOGGER.info(
                        "📈 Connection: %.1fms latency, %.0f%% health, %.2f req/min",
                        self._connection_latency,
                        self._system_health,
                        self.api_request_rate,
                    )

                    # Beispiel-Keys (zu Debug-Zwecken)
                    sample_keys = sorted(data.keys())[:15]
                    _LOGGER.info(
                        "🔑 Sample keys (%d total): %s",
                        len(data),
                        ", ".join(sample_keys),
                    )

                return dict(self._data)

        except VioletPoolAPIError as err:
            self._last_error = str(err)
            self._consecutive_failures += 1

            # ✅ LOGGING OPTIMIZATION: Konsolidiertes Error-Logging
            if self._consecutive_failures == 1:
                if not self._available and len(self._data) == 0:
                    _LOGGER.debug(
                        "API error during setup of '%s': %s",
                        self.device_name,
                        str(err)[:200],
                    )
                else:
                    _LOGGER.error(
                        "API error during update of '%s': %s",
                        self.device_name,
                        str(err)[:200],
                    )
            elif self._consecutive_failures >= self._max_consecutive_failures:
                _LOGGER.error(
                    "Controller '%s' unavailable after %d API failures",
                    self.device_name,
                    self._consecutive_failures,
                )
                self._available = False
                raise UpdateFailed(f"Controller unreachable: {err}") from err
            elif self._should_log_failure():
                _LOGGER.warning(
                    "Persistent API issues for '%s' (%d/%d failures)",
                    self.device_name,
                    self._consecutive_failures,
                    self._max_consecutive_failures,
                )

            # ✅ FIX: Return a COPY of stale data
            return dict(self._data) if self._data else {}

        except Exception as err:
            self._last_error = str(err)
            self._consecutive_failures += 1

            if self._consecutive_failures == 1:
                if not self._available and len(self._data) == 0:
                    _LOGGER.debug(
                        "Error during setup of '%s': %s", self.device_name, err
                    )
                else:
                    _LOGGER.exception(
                        "Unexpected error during update of '%s'", self.device_name
                    )
            elif self._consecutive_failures >= self._max_consecutive_failures:
                _LOGGER.error(
                    "Controller '%s' unavailable after %d unexpected failures",
                    self.device_name,
                    self._consecutive_failures,
                )
                self._available = False
                raise UpdateFailed(f"Update error: {err}") from err
            elif self._should_log_failure():
                _LOGGER.warning(
                    "Persistent issues for '%s': %s (%d/%d failures)",
                    self.device_name,
                    type(err).__name__,
                    self._consecutive_failures,
                    self._max_consecutive_failures,
                )

            # ✅ FIX: Return a COPY of stale data
            return dict(self._data) if self._data else {}

    async def _fetch_controller_data(self) -> dict[str, Any]:
        """Fetch all controller data.

        Always uses full refresh (?ALL) because the controller returns all
        data in a single compact response (~403 keys) and partial category
        queries miss many important keys (PUMP, SOLAR, fw, etc.).
        """
        return await self.api.get_readings()


    @property
    def available(self) -> bool:
        """Return the availability status."""
        return self._available

    @property
    def firmware_version(self) -> str | None:
        """Return the firmware version."""
        return self._firmware_version

    @property
    def data(self) -> dict[str, Any]:
        """Return the current data."""
        return self._data

    @property
    def last_error(self) -> str | None:
        """Return the last error."""
        return self._last_error

    @property
    def consecutive_failures(self) -> int:
        """Return the number of consecutive failures."""
        return self._consecutive_failures

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information for Home Assistant."""
        return {
            "identifiers": {(DOMAIN, f"{self.api_url}_{self.device_id}")},
            # Uses controller_name for visual distinction in multi-controller setups
            "name": self.controller_name,
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Pool Controller",
            "sw_version": self._firmware_version or "Unbekannt",
            "suggested_area": self.controller_name,  # ✅ Auto-Area für Multi-Controller
        }

    @property
    def system_health(self) -> float:
        """
        Return the system health percentage (0-100).

        ✅ DIAGNOSTIC SENSOR: Overall connection health.
        """
        return self._system_health

    @property
    def connection_latency(self) -> float:
        """
        Return the last connection latency in milliseconds.

        ✅ DIAGNOSTIC SENSOR: Connection response time.
        """
        return self._connection_latency

    @property
    def last_event_age(self) -> float:
        """
        Return seconds since the last successful update.

        ✅ DIAGNOSTIC SENSOR: Data freshness indicator.
        """
        if self._last_update_time == 0.0:
            return 0.0
        return time.monotonic() - self._last_update_time

    @property
    def api_request_rate(self) -> float:
        """
        Return API requests per minute.

        ✅ DIAGNOSTIC SENSOR: API request rate.
        """
        elapsed = time.monotonic() - self._api_request_start_time
        if elapsed < 1:
            return 0.0
        return (self._api_request_count / elapsed) * 60

    @property
    def average_latency(self) -> float:
        """
        Return average connection latency in milliseconds.

        ✅ DIAGNOSTIC SENSOR: Rolling average latency.
        """
        if not self._latency_history:
            return 0.0
        return sum(self._latency_history) / len(self._latency_history)

    def _extract_api_url(self, entry_data: Mapping[str, Any]) -> str:
        """
        Extract the API URL from config data.

        Args:
            entry_data: The configuration data dictionary.

        Returns:
            The API URL.

        Raises:
            ValueError: If no API URL is found.
        """
        url = (
            entry_data.get(CONF_API_URL)
            or entry_data.get("host")
            or entry_data.get("base_ip")
        )

        if not url:
            raise ValueError("No IP address found in config entry")

        if not isinstance(url, str):
            raise ValueError("API URL is not a string")

        return url.strip()


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for the Violet Pool Controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: VioletPoolControllerDevice,
        name: str,
        polling_interval: int = DEFAULT_POLLING_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=polling_interval),
        )
        self.device = device

        _LOGGER.info(
            "Coordinator initialisiert für '%s' (Abruf alle %ds)",
            name,
            polling_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Update data from the device.

        Returns a fresh dict from the device on every call so that
        HA's DataUpdateCoordinator always sees a new data object and
        triggers entity listener callbacks.

        Returns:
            A dictionary containing the updated data.

        Raises:
            UpdateFailed: If the update fails.
        """
        try:
            data = await self.device.async_update()
            if not data:
                raise UpdateFailed(
                    f"Empty data returned for '{self.device.device_name}'"
                )
            return data
        except UpdateFailed:
            raise
        except VioletPoolAPIError as err:
            raise UpdateFailed(f"API error: {err}") from err
        except Exception as err:
            raise UpdateFailed(
                f"Unexpected error updating '{self.device.device_name}': {err}"
            ) from err


async def async_setup_device(
    hass: HomeAssistant, config_entry: ConfigEntry, api: VioletPoolAPI
) -> VioletPoolDataUpdateCoordinator:
    """Set up the Violet Pool Controller device and return a coordinator."""
    try:
        device = VioletPoolControllerDevice(hass, config_entry, api)

        max_retries = 3
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                _LOGGER.debug(
                    "Setup attempt %d/%d for '%s'",
                    attempt,
                    max_retries,
                    device.device_name,
                )

                await device.async_update()

                if device.available:
                    _LOGGER.debug("Setup attempt %d succeeded", attempt)
                    break

            except Exception as err:
                last_error = err
                _LOGGER.debug("Setup attempt %d failed: %s", attempt, err)

            if attempt < max_retries:
                await asyncio.sleep(2)

        if not device.available:
            error_msg = (
                f"Controller '{device.device_name}' not reachable after "
                f"{max_retries} attempts. "
                f"Please check connection and controller status."
            )
            if last_error:
                error_msg += f" Last error: {last_error}"

            raise ConfigEntryNotReady(error_msg)

        polling_interval = config_entry.options.get(
            CONF_POLLING_INTERVAL,
            config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        )

        coordinator = VioletPoolDataUpdateCoordinator(
            hass,
            device,
            config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
            polling_interval,
        )

        await coordinator.async_config_entry_first_refresh()

        _LOGGER.info(
            "Device setup successful: '%s' (FW: %s, %d data points)",
            device.device_name,
            device.firmware_version or "Unknown",
            len(device.data) if device.data else 0,
        )

        return coordinator

    except ConfigEntryNotReady:
        raise

    except Exception as err:
        _LOGGER.exception("Device setup failed: %s", err)
        raise ConfigEntryNotReady(f"Setup error: {err}") from err
