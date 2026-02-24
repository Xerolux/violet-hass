"""Violet Pool Controller Device Module - SMART FAILURE LOGGING + AUTO RECOVERY."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any, Mapping

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VioletPoolAPI, VioletPoolAPIError
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

# ✅ LOGGING OPTIMIZATION: Throttling constants
FAILURE_LOG_INTERVAL = 300  # Only every 5 minutes for repeated errors

# ✅ RECOVERY OPTIMIZATION: Auto-recovery constants
RECOVERY_MAX_ATTEMPTS = 10  # Maximum recovery attempts
RECOVERY_BASE_DELAY = 10.0  # Base delay for exponential backoff (10s)
RECOVERY_MAX_DELAY = 300.0  # Maximum delay between attempts (5 min)

# =============================================================================
# THREAD SAFETY & LOCK ORDERING
# =============================================================================
# To prevent deadlocks, ALWAYS acquire locks in this order:
# 1. _api_lock - protects API calls and data updates
# 2. _recovery_lock - protects recovery state and attempts
#
# NEVER:
# - Acquire _recovery_lock while holding _api_lock
# - Acquire _api_lock while holding _recovery_lock
# - Nest locks without releasing the first one
#
# SAFE PATTERNS:
# - async with self._api_lock: ... (standalone)
# - async with self._recovery_lock: ... (standalone)
# - If both needed: acquire one, release, then acquire the other
# =============================================================================


class VioletPoolControllerDevice:
    """Violet Pool Controller Device - SMART LOGGING + AUTO RECOVERY."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, api: VioletPoolAPI
    ) -> None:
        """Initialize device instance with smart logging and auto-recovery."""
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

        # ✅ LOGGING OPTIMIZATION: Smart Failure Tracking
        self._last_failure_log = 0.0  # Timestamp for throttling
        self._first_failure_logged = False  # Flag for first warning
        self._recovery_logged = False  # Flag for recovery message
        self._fw_logged = False  # Flag for firmware version logging

        # ✅ RECOVERY OPTIMIZATION: Auto-Recovery Tracking
        self._recovery_attempts = 0  # Counter for recovery attempts
        self._in_recovery_mode = False  # Flag for recovery mode
        self._last_recovery_attempt = 0.0  # Timestamp last recovery attempt
        self._recovery_task: asyncio.Task | None = None  # Recovery task
        self._recovery_lock = asyncio.Lock()  # ✅ Lock for thread-safe recovery

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
        self._recovery_success_count = 0  # Successful recoveries
        self._recovery_failure_count = 0  # Failed recoveries

        # Extract configuration (with options support)
        entry_data = config_entry.data
        entry_options = config_entry.options
        self.api_url = self._extract_api_url(entry_data)
        self.use_ssl = entry_data.get(CONF_USE_SSL, True)
        self.device_id = entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        # ✅ MULTI-CONTROLLER: Prioritize options (runtime changes), then data
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
        from .api import VioletPoolAPI
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
        Updates device data from controller - SMART FAILURE LOGGING.

        Returns a NEW dict copy on every successful update so that
        HA's DataUpdateCoordinator detects a data change and notifies
        all entity listeners.  Returning the same mutable reference
        caused HA 2025.12+ to skip entity state writes because
        ``self.data is new_data`` evaluated to True.

        ✅ LOGGING OPTIMIZATION:
        - First warning immediately
        - Intermediate warnings only every 5 minutes
        - Critical error at max failures
        - Recovery info after restoration
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

                # Validate data
                if not data or not isinstance(data, dict):
                    self._consecutive_failures += 1

                    # ✅ LOGGING OPTIMIZATION: Intelligent failure logging
                    if self._consecutive_failures == 1:
                        # First warning only if was available (not first setup)
                        if self._available or len(self._data) > 0:
                            _LOGGER.warning(
                                "Controller '%s' returned empty/invalid data (attempt %d)",
                                self.device_name,
                                self._consecutive_failures,
                            )
                            self._first_failure_logged = True
                            self._recovery_logged = False
                        else:
                            # Only debug level during first setup
                            _LOGGER.debug(
                                "Controller '%s' not responding (setup phase)",
                                self.device_name,
                            )

                    elif self._consecutive_failures >= self._max_consecutive_failures:
                        # Critical: Becoming unavailable - ALWAYS log
                        _LOGGER.error(
                            "Controller '%s' marked unavailable after %d consecutive failures. "
                            "Starting auto-recovery...",
                            self.device_name,
                            self._consecutive_failures,
                        )
                        self._available = False

                        # ✅ RECOVERY: Start automatic recovery
                        await self._start_recovery_background_task()

                        raise UpdateFailed(
                            f"Controller '{self.device_name}' unreachable "
                            f"({self._consecutive_failures} errors), Recovery started"
                        )

                    elif self._should_log_failure():
                        # Intermediate warnings throttled
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

                # ✅ LOGGING OPTIMIZATION: Success after failures = important info
                if self._consecutive_failures > 0 and not self._recovery_logged:
                    _LOGGER.info(
                        "Controller '%s' reachable again (after %d failure%s)",
                        self.device_name,
                        self._consecutive_failures,
                        "s" if self._consecutive_failures > 1 else "",
                    )
                    self._recovery_logged = True
                    self._first_failure_logged = False

                # ✅ FIX: Always replace _data with a fresh dict to ensure
                # HA's DataUpdateCoordinator detects the change.
                self._data = dict(data)
                self._available = True
                self._consecutive_failures = 0
                self._last_error = None

                # ✅ DIAGNOSTIC: Update health metrics
                self._last_update_time = time.monotonic()
                self._system_health = 100.0  # Perfect health

                # Extract firmware version (multiple fallbacks)
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

                # Debug log only if firmware found and not yet logged
                if self._firmware_version and not self._fw_logged:
                    _LOGGER.debug(
                        "Firmware version detected: %s", self._firmware_version
                    )
                    self._fw_logged = True

                # ✅ FIX: Return a NEW dict so the coordinator always
                # receives a distinct object, triggering entity updates.
                self._update_counter += 1

                # Standard debug log (always active)
                _LOGGER.debug(
                    "Update #%d for '%s': %d keys fetched in %.3fs",
                    self._update_counter,
                    self.device_name,
                    len(data),
                    self._connection_latency / 1000,  # Convert ms to seconds
                )

                # ✅ DIAGNOSTIC LOGGING: Extended information (optional)
                if self._enable_diagnostic_logging:
                    # List of changed keys since last update
                    changed_keys = set(data.keys()) - set(self._data.keys()) if self._data else set(data.keys())
                    if changed_keys:
                        _LOGGER.info(
                            "📊 Update #%d: %d new/changed keys: %s%s",
                            self._update_counter,
                            len(changed_keys),
                            ", ".join(sorted(changed_keys)[:20]),  # Max 20 keys
                            "..." if len(changed_keys) > 20 else "",
                        )

                    # Connection metrics
                    _LOGGER.info(
                        "📈 Connection: %.1fms latency, %.0f%% health, %.2f req/min",
                        self._connection_latency,
                        self._system_health,
                        self.api_request_rate,
                    )

                    # Sample keys (for debug purposes)
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
                # Beim ersten Setup nur Debug, sonst Error
                if not self._available and len(self._data) == 0:
                    _LOGGER.debug(
                        "API-Fehler bei Setup von '%s': %s",
                        self.device_name,
                        str(err)[:200],
                    )
                else:
                    _LOGGER.error(
                        "API-Fehler bei Update von '%s': %s",
                        self.device_name,
                        str(err)[:200],  # Gekürzt auf 200 Zeichen
                    )
            elif self._consecutive_failures >= self._max_consecutive_failures:
                _LOGGER.error(
                    "Controller '%s' nach %d API-Fehlern nicht mehr verfügbar",
                    self.device_name,
                    self._consecutive_failures,
                )
                self._available = False
                raise UpdateFailed(f"Controller nicht erreichbar: {err}") from err
            elif self._should_log_failure():
                _LOGGER.warning(
                    "Anhaltende API-Probleme bei '%s' (%d/%d Fehler)",
                    self.device_name,
                    self._consecutive_failures,
                    self._max_consecutive_failures,
                )

            # ✅ FIX: Return a COPY of stale data
            return dict(self._data) if self._data else {}

        except Exception as err:
            self._last_error = str(err)
            self._consecutive_failures += 1

            # ✅ LOGGING: Unexpected errors always logged
            if self._consecutive_failures == 1:
                # Beim ersten Setup nur Debug, sonst volle Exception
                if not self._available and len(self._data) == 0:
                    _LOGGER.debug(
                        "Fehler bei Setup von '%s': %s", self.device_name, err
                    )
                else:
                    _LOGGER.exception(
                        "Unerwarteter Fehler bei Update von '%s'", self.device_name
                    )
            elif self._consecutive_failures >= self._max_consecutive_failures:
                _LOGGER.error(
                    "Controller '%s' nach %d unerwarteten Fehlern nicht verfügbar",
                    self.device_name,
                    self._consecutive_failures,
                )
                self._available = False
                raise UpdateFailed(f"Update error: {err}") from err
            elif self._should_log_failure():
                _LOGGER.warning(
                    "Anhaltende Probleme bei '%s': %s (%d/%d Fehler)",
                    self.device_name,
                    type(err).__name__,  # Nur Exception-Typ, nicht full trace
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
        """Returns availability status."""
        return self._available

    @property
    def firmware_version(self) -> str | None:
        """Returns firmware version."""
        return self._firmware_version

    @property
    def data(self) -> dict[str, Any]:
        """Returns current data."""
        return self._data

    @property
    def last_error(self) -> str | None:
        """Returns last error."""
        return self._last_error

    @property
    def consecutive_failures(self) -> int:
        """Returns number of consecutive failures."""
        return self._consecutive_failures

    @property
    def device_info(self) -> dict[str, Any]:
        """
        Returns device info for Home Assistant.

        ✅ MULTI-CONTROLLER SUPPORT:
        - Uses controller_name for visual distinction
        - suggested_area enables automatic area assignment
        - No caching, so option changes take effect immediately
        """
        return {
            "identifiers": {(DOMAIN, f"{self.api_url}_{self.device_id}")},
            # ✅ Uses Controller-Name instead of Device-Name
            "name": self.controller_name,
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Pool Controller",
            "sw_version": self._firmware_version or "Unknown",
            "suggested_area": self.controller_name,  # ✅ Auto-area for multi-controller
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

    @property
    def recovery_success_rate(self) -> float:
        """
        Return recovery success rate as percentage (0-100).

        ✅ DIAGNOSTIC SENSOR: Recovery effectiveness.
        """
        total = self._recovery_success_count + self._recovery_failure_count
        if total == 0:
            return 100.0  # No recovery attempts = 100% success
        return (self._recovery_success_count / total) * 100

    async def _attempt_recovery(self) -> bool:
        """
        Attempt automatic connection recovery.

        ✅ RECOVERY OPTIMIZATION:
        - Exponential backoff for recovery attempts.
        - Thread-safe with asyncio.Lock (Race Condition Fix).

        Returns:
            True if recovery was successful, False otherwise.
        """
        # ✅ RACE CONDITION FIX: Complete atomic recovery with proper lock protection
        async with self._recovery_lock:
            # Atomic check-and-set under same lock
            if self._in_recovery_mode:
                _LOGGER.debug("Recovery already in progress, skipping")
                return False

            if self._recovery_attempts > RECOVERY_MAX_ATTEMPTS:
                _LOGGER.warning("Maximum recovery attempts reached")
                return False

            # Set recovery state atomically
            self._in_recovery_mode = True
            self._recovery_attempts += 1
            current_attempt = self._recovery_attempts

        try:
            # Calculate exponential backoff delay
            delay = min(
                RECOVERY_MAX_DELAY,
                RECOVERY_BASE_DELAY * (2 ** (current_attempt - 1)),
            )

            _LOGGER.info(
                "🔄 Recovery attempt %d/%d for '%s' (Delay: %.1fs)",
                current_attempt,
                RECOVERY_MAX_ATTEMPTS,
                self.device_name,
                delay,
            )

            await asyncio.sleep(delay)

            # Attempt data retrieval under _api_lock to prevent concurrent API calls.
            # Lock ordering: _api_lock first, _recovery_lock second — never nest them.
            # We are NOT holding _recovery_lock here, so acquiring _api_lock is safe.
            async with self._api_lock:
                data = await self._fetch_controller_data()

            if data and isinstance(data, dict):
                # Recovery successful - merge data and reset state atomically
                async with self._recovery_lock:
                    # ✅ FIX: Store recovered data so entities update immediately
                    # without waiting for the next normal coordinator poll cycle.
                    if self._data:
                        merged = dict(self._data)
                        merged.update(data)
                        self._data = merged
                    else:
                        self._data = dict(data)
                    self._consecutive_failures = 0
                    self._recovery_attempts = 0
                    self._available = True
                    self._recovery_logged = True
                    self._recovery_success_count += 1  # ✅ DIAGNOSTIC: Track success

                _LOGGER.info("Recovery successful for '%s'", self.device_name)
                return True

            # Recovery attempt failed (no valid data returned)
            async with self._recovery_lock:
                self._recovery_failure_count += 1  # ✅ DIAGNOSTIC: Track failure
            return False

        except Exception as err:
            _LOGGER.debug(
                "Recovery attempt %d failed: %s",
                current_attempt,
                err,
            )
            async with self._recovery_lock:
                self._recovery_failure_count += 1  # ✅ DIAGNOSTIC: Track failure
            return False

        finally:
            # Always ensure recovery state is reset under lock protection
            async with self._recovery_lock:
                self._in_recovery_mode = False
                self._last_recovery_attempt = time.monotonic()

    async def _cleanup_recovery_task(self) -> None:
        """
        Cancel existing recovery task if running.

        ✅ TASK CLEANUP: Ensures old recovery tasks are properly cancelled
        before starting new ones, preventing resource leaks.

        This should be called before creating a new recovery task to ensure
        any existing task is properly cancelled.
        """
        if self._recovery_task and not self._recovery_task.done():
            _LOGGER.debug("Cancelling existing recovery task before creating new one")
            self._recovery_task.cancel()
            try:
                await self._recovery_task
            except asyncio.CancelledError:
                _LOGGER.debug("Recovery task successfully cancelled")
            except Exception as err:
                _LOGGER.warning("Error cancelling recovery task: %s", err)
        self._recovery_task = None

    async def _start_recovery_background_task(self) -> None:
        """
        Start recovery in the background.

        ✅ RECOVERY OPTIMIZATION: Prevents blocking normal updates.
        """
        # Clean up any existing task before starting a new one
        await self._cleanup_recovery_task()

        if self._recovery_attempts >= RECOVERY_MAX_ATTEMPTS:
            _LOGGER.warning(
                "⚠️ Maximum recovery attempts (%d) reached for '%s'. "
                "Manual intervention required.",
                RECOVERY_MAX_ATTEMPTS,
                self.device_name,
            )
            return

        async def recovery_loop() -> None:
            """Recovery loop in background."""
            while self._recovery_attempts < RECOVERY_MAX_ATTEMPTS:
                if await self._attempt_recovery():
                    _LOGGER.info(
                        "✅ Background recovery successful for '%s'",
                        self.device_name,
                    )
                    return

                # Wait before next attempt
                await asyncio.sleep(5)

            _LOGGER.error(
                "❌ Background recovery failed for '%s' after %d attempts",
                self.device_name,
                RECOVERY_MAX_ATTEMPTS,
            )

        self._recovery_task = asyncio.create_task(recovery_loop())
        _LOGGER.info(
            "🔄 Background recovery started for '%s'",
            self.device_name,
        )

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


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data Update Coordinator - SMART FAILURE LOGGING."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: VioletPoolControllerDevice,
        name: str,
        polling_interval: int = DEFAULT_POLLING_INTERVAL,
    ) -> None:
        """Initialize coordinator with smart logging."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=polling_interval),
        )
        self.device = device

        _LOGGER.info(
            "Coordinator initialized for '%s' (polling every %ds)",
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
    """
    Setup of Violet Pool Controller Device - SMART FAILURE LOGGING + RETRY LOGIC.

    ✅ LOGGING OPTIMIZATION: Focus on setup success/failure, not details.
    ✅ RETRY LOGIC: Multiple attempts during first setup for better reliability.
    """
    try:
        # Create device
        device = VioletPoolControllerDevice(hass, config_entry, api)

        # Perform first update with retry logic (max 3 attempts)
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
                    _LOGGER.debug("Setup attempt %d successful", attempt)
                    break

            except Exception as err:
                last_error = err
                _LOGGER.debug("Setup attempt %d failed: %s", attempt, err)

            # Wait between attempts (except after the last one)
            if attempt < max_retries:
                await asyncio.sleep(2)

        if not device.available:
            # ✅ Clear setup error message after all attempts
            error_msg = (
                f"Controller '{device.device_name}' unreachable after "
                f"{max_retries} attempts. "
                f"Please check connection and controller status."
            )
            if last_error:
                error_msg += f" Last error: {last_error}"

            raise ConfigEntryNotReady(error_msg)

        # Get polling interval from options or data
        polling_interval = config_entry.options.get(
            CONF_POLLING_INTERVAL,
            config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        )

        # Create coordinator
        coordinator = VioletPoolDataUpdateCoordinator(
            hass,
            device,
            config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
            polling_interval,
        )

        # Perform first refresh
        await coordinator.async_config_entry_first_refresh()

        # ✅ Successful setup = important info
        _LOGGER.info(
            "✓ Device setup successful: '%s' (FW: %s, %d data points)",
            device.device_name,
            device.firmware_version or "Unknown",
            len(device.data) if device.data else 0,
        )

        return coordinator

    except ConfigEntryNotReady:
        # Re-raise already correctly formatted exception
        raise

    except Exception as err:
        # ✅ Always log setup errors (critical)
        _LOGGER.exception("Device setup failed: %s", err)
        raise ConfigEntryNotReady(f"Setup error: {err}") from err
