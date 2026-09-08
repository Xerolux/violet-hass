# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Violet Pool Controller device management."""

from __future__ import annotations

import asyncio
import collections
import logging
import time
from datetime import datetime, timedelta
from typing import Any, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from violet_poolcontroller_api.api import (
    VioletAuthError,
    VioletPoolAPI,
    VioletPoolAPIError,
)
from violet_poolcontroller_api.readings import VioletReadings

from .auth_guard import AuthReportingAPI
from .config_entry_helpers import (
    extract_api_host,
    get_entry_value,
    with_non_default_port,
)
from .config_flow_utils.constants import (
    MAX_POLLING_INTERVAL,
    MAX_RETRIES,
    MAX_TIMEOUT,
    MIN_RETRIES,
    MIN_TIMEOUT,
)
from .const import (
    ADAPTIVE_ACTIVITY_KEYS,
    ADAPTIVE_IDLE_FACTOR,
    ADAPTIVE_IDLE_MAX_INTERVAL,
    CONF_ADAPTIVE_POLLING,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_DOSING_STANDALONE,
    CONF_PASSWORD,
    CONF_POLLING_INTERVAL,
    CONF_PORT,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    CONFIG_REFRESH_INTERVAL,
    DEFAULT_ADAPTIVE_POLLING,
    DEFAULT_CONTROLLER_NAME,
    DEFAULT_DOSING_STANDALONE,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_USE_SSL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    FIRMWARE_VERSION_REFRESH_FETCHES,
    MIN_SUPPORTED_POLLING_INTERVAL,
)
from .error_handler import EnhancedErrorHandler
from .hardware_config import HardwareConfig

_LOGGER = logging.getLogger(__name__)

FAILURE_LOG_INTERVAL = 300  # Log repeated failures at most every 5 minutes


def _clamp_polling_interval(seconds: Any) -> int:
    """Return a polling interval inside the supported range.

    Guards the coordinator against out-of-range or non-numeric values stored in
    a config entry, so a bad setting can never turn into a hot polling loop.
    """
    try:
        value = int(float(seconds))
    except (TypeError, ValueError):
        return DEFAULT_POLLING_INTERVAL
    return max(MIN_SUPPORTED_POLLING_INTERVAL, min(MAX_POLLING_INTERVAL, value))


def _clamp_int(value: Any, minimum: int, maximum: int, default: int) -> int:
    """Return an int setting clamped into its supported range."""
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def connection_settings(config_entry: ConfigEntry) -> dict[str, Any]:
    """Return every setting the API client is built from.

    Two snapshots comparing equal means the running API client is still the
    right one; any difference requires a new client, i.e. a reload of the
    config entry.
    """
    entry_data = config_entry.data
    return {
        "host": with_non_default_port(
            extract_api_host(entry_data),
            entry_data.get(CONF_PORT, DEFAULT_PORT),
        ),
        "use_ssl": bool(entry_data.get(CONF_USE_SSL, DEFAULT_USE_SSL)),
        "verify_ssl": bool(entry_data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)),
        "username": entry_data.get(CONF_USERNAME) or None,
        "password": entry_data.get(CONF_PASSWORD) or None,
        "dosing_standalone": bool(
            get_entry_value(config_entry, CONF_DOSING_STANDALONE, DEFAULT_DOSING_STANDALONE)
        ),
        "timeout": _clamp_int(
            get_entry_value(config_entry, CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION),
            MIN_TIMEOUT,
            MAX_TIMEOUT,
            DEFAULT_TIMEOUT_DURATION,
        ),
        "retries": _clamp_int(
            get_entry_value(config_entry, CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS),
            MIN_RETRIES,
            MAX_RETRIES,
            DEFAULT_RETRY_ATTEMPTS,
        ),
    }


POLL_SNAPSHOT_FIELDS = (
    "Pool Temp",
    "Redox",
    "pH",
    "Chlorine",
    "Overflow",
    "Flow",
    "Inflow",
)


class VioletPoolControllerDevice:
    """Violet Pool Controller Device - SMART LOGGING + AUTO RECOVERY."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, api: VioletPoolAPI) -> None:
        """Initialize the device instance."""
        self.hass = hass
        self.config_entry = config_entry
        # Guarded so a command rejected for missing credentials surfaces as a
        # repair issue instead of a generic API error (see auth_guard.py).
        self.api = AuthReportingAPI(api, hass, config_entry)  # type: ignore[assignment]
        self._available = False
        self._session = async_get_clientsession(hass)
        self._data: dict[str, Any] = {}
        self._firmware_version: str | None = None
        self._last_error: str | None = None
        self._api_lock = asyncio.Lock()
        self._consecutive_failures = 0
        self._max_consecutive_failures = 5
        self._update_counter = 0
        # Counts getConfig fetches (NOT poll cycles) and throttles the
        # SYSTEM_availableversion request (see _build_config_keys). Resets on
        # every coordinator reload.
        self._config_fetch_counter: int = 0
        # Last values read via getConfig, plus when they were read. Setpoints
        # only change on a write, so they are refreshed on a timer rather than
        # on every poll (see _fetch_config_values).
        self._config_cache: dict[str, Any] = {}
        self._last_config_fetch = 0.0
        self._force_config_fetch = False
        # Store poll snapshots as fixed-position tuples to reduce per-entry overhead.
        self._poll_history: collections.deque[tuple[datetime, int, float, tuple[Any, ...]]] = (
            collections.deque(maxlen=1000)
        )
        self._first_poll: datetime | None = None

        self._last_failure_log = 0.0  # Timestamp for throttling
        self._recovery_logged = False  # Flag for recovery message
        self._unavailable_reported = False  # Flag for the "unavailable" error log
        self._fw_logged = False  # Flag for firmware version logging

        # Per-device error statistics. One handler per controller, so a second
        # controller's outage never shows up in this device's diagnostics.
        self._error_handler = EnhancedErrorHandler()

        # ✅ DIAGNOSTIC SENSORS: Connection health monitoring
        self._last_update_time = 0.0  # Timestamp of last successful update
        self._connection_latency = 0.0  # Last connection latency in milliseconds
        self._system_health = 100.0  # System health percentage (0-100)

        # Sticky hardware module detection: once a module is detected it is never
        # de-detected within the same HA session.  The API package (0.0.12+) filters
        # EXT1/EXT2 keys when the module looks absent (e.g. LAST_ON == 0 for a
        # freshly connected, never-used relay board).  Without this cache those keys
        # would disappear from coordinator.data and switch entities would silently
        # revert to OFF even though the relay board is physically present.
        self._hw_detected: set[str] = set()

        # ✅ DIAGNOSTIC SENSORS: Advanced metrics
        self._api_request_count = 0  # Total API requests
        self._api_request_start_time = time.monotonic()  # For rate calculation
        # 360 samples = 1 hour of history (at default 10s polling interval)
        self._latency_history: collections.deque[float] = collections.deque(maxlen=360)

        # ✅ HARDWARE CONFIGURATION: Cache all hardware configs (DI, relays, scenes, etc.)
        self._hardware_config: dict[str, Any] | None = None
        self._hardware_config_loaded = False

        entry_data = config_entry.data
        self.api_url = with_non_default_port(
            extract_api_host(entry_data),
            entry_data.get(CONF_PORT, DEFAULT_PORT),
        )
        self.use_ssl = entry_data.get(CONF_USE_SSL, DEFAULT_USE_SSL)
        self.device_id = entry_data.get(CONF_DEVICE_ID, 1)
        self.device_name = entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        # Prefer options (later changes) over data
        self.controller_name = get_entry_value(
            config_entry,
            CONF_CONTROLLER_NAME,
            DEFAULT_CONTROLLER_NAME,
        )
        _LOGGER.info(
            "Device initialized: '%s' (Controller: %s, URL: %s, SSL: %s, Device-ID: %d)",
            self.device_name,
            self.controller_name,
            self.api_url,
            self.use_ssl,
            self.device_id,
        )

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

    async def _fetch_controller_data(self) -> dict[str, Any]:
        """Fetch all controller data.

        Always uses full refresh (?ALL) because the controller returns all
        data in a single compact response (~403 keys) and partial category
        queries miss many important keys (PUMP, SOLAR, fw, etc.).

        API 0.0.11 note: get_readings() now internally builds a hardware
        profile and filters out readings for absent modules.  The HW_* flags
        below are derived from what is actually present in the returned data,
        which is reliable because the API filter only removes keys whose
        module is absent.
        """
        _readings = await self.api.get_readings()
        # get_readings() hands back a fresh mapping per call, so a plain dict can
        # be adopted as-is instead of copying ~400 keys on every poll.
        data: dict[str, Any] = (
            _readings if isinstance(_readings, dict) else dict(_readings or {})
        )

        try:
            runtimes = await self.api.get_output_runtimes()
            if runtimes:
                for key, value in runtimes.items():
                    if key not in data:
                        data[key] = value
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Optional getOutputRuntimes fetch failed for '%s': %s",
                self.device_name,
                err,
            )

        if data and isinstance(data, dict):

            def is_valid(val: Any) -> bool:
                return val is not None and str(val).strip().upper() != "N/A"

            # --- Dosing module ---
            has_dosing_now = (
                "SYSTEM_dosagemodule_alive_count" in data
                or is_valid(data.get("SYSTEM_dosagemodule_cpu_temperature"))
                or any(k.startswith("DOS_") and is_valid(v) for k, v in data.items())
            )
            if self.api.dosing_standalone or has_dosing_now:
                self._hw_detected.add("DOSING")
            has_dosing = "DOSING" in self._hw_detected or self.api.dosing_standalone

            # --- Relay extensions ---
            # Presence follows the alive-count keys: the carrier reports every
            # EXT*_ key with stale values even for modules that are not
            # connected, and the runtimes merge above re-imports them, so
            # prefix matching reported a second extension that does not exist.
            has_ext1_now = "SYSTEM_ext1module_alive_count" in data
            if has_ext1_now:
                self._hw_detected.add("EXT1")
            has_ext1 = "EXT1" in self._hw_detected

            has_ext2_now = "SYSTEM_ext2module_alive_count" in data
            if has_ext2_now:
                self._hw_detected.add("EXT2")
            has_ext2 = "EXT2" in self._hw_detected

            # --- DMX lighting module ---
            has_dmx_now = any(k.startswith("DMX_") and is_valid(v) for k, v in data.items())
            if has_dmx_now:
                self._hw_detected.add("DMX")
            has_dmx = "DMX" in self._hw_detected

            # --- Digital input rules ---
            has_dirule_now = any(
                k.startswith("DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_") and is_valid(v)
                for k, v in data.items()
            )
            if has_dirule_now:
                self._hw_detected.add("DIRULE")
            has_dirule = "DIRULE" in self._hw_detected

            # ---- Generic key restoration for all optional modules ----
            _optional_modules: list[tuple[str, str, bool]] = [
                ("DOSING", "DOS_", has_dosing_now),
                ("EXT1", "EXT1_", has_ext1_now),
                ("EXT2", "EXT2_", has_ext2_now),
                ("DMX", "DMX_", has_dmx_now),
                ("DIRULE", "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_", has_dirule_now),
            ]
            for _tag, _prefix, _present_now in _optional_modules:
                if _tag in self._hw_detected and not _present_now:
                    restored = 0
                    for prev_key, prev_val in self._data.items():
                        if prev_key.startswith(_prefix) and prev_key not in data:
                            data[prev_key] = prev_val
                            restored += 1
                    if restored:
                        _LOGGER.debug(
                            "%s module temporarily absent from API response; "
                            "restored %d %s* keys from previous poll",
                            _tag,
                            restored,
                            _prefix,
                        )

            is_standalone = self.api.dosing_standalone

            data["HW_BASE_MODULE"] = not is_standalone
            data["HW_DOSING_MODULE"] = has_dosing
            data["HW_EXTENSION_MODULE_1"] = has_ext1
            data["HW_EXTENSION_MODULE_2"] = has_ext2
            data["HW_DMX_MODULE"] = has_dmx
            data["HW_DIRULE_MODULE"] = has_dirule
            data["HW_STANDALONE_MODE"] = is_standalone

        return cast(dict[str, Any], data)

    def _build_config_keys(self) -> list[str]:
        """Build the getConfig key list for the current poll cycle.

        Always includes the setpoint keys and SYSTEM_swversion (the latter is a
        local cached value used for device-registry resolution). SYSTEM_availableversion
        is appended only on the first poll and then once every
        FIRMWARE_VERSION_REFRESH_FETCHES getConfig fetches, because fetching it triggers a
        server-side refresh on the controller. SYSTEM_updateavailable is NEVER
        requested: it forces a live backend check and its value is discarded —
        the update-available decision is made by numeric version comparison in
        update_helper.py.
        """
        keys = [
            # Setpoints (controller exposes these via getConfig, not getReadings)
            "HEATER_set_temp",
            "SOLAR_maxtemp",
            "DOSAGE_phminus_setpoint",
            "DOSAGE_chlorine_setpoint_orp",
            "DOSAGE_chlorine_lowerval_cl",
            # Electrolysis keeps its own copies of the ORP/chlorine setpoints;
            # they are the ones in charge on a pool without a chlorine pump
            # (see dosing_channel.py).
            "DOSAGE_electrolysis_setpoint_orp",
            "DOSAGE_electrolysis_setpoint_chlorine",
            "DOSAGE_chlorine_use",
            "DOSAGE_electrolysis_use",
            "DOSAGE_phminus_use",
            "DOSAGE_phplus_use",
            "DOSAGE_floc_use",
            # Firmware version (local cached value, cheap to read)
            "SYSTEM_swversion",
        ]
        if self._config_fetch_counter % FIRMWARE_VERSION_REFRESH_FETCHES == 0:
            keys.append("SYSTEM_availableversion")
        self._config_fetch_counter += 1
        return keys

    def request_config_refresh(self) -> None:
        """Force the next poll to re-read the setpoints from the controller.

        Called after a setpoint write so the value the controller actually
        stored is confirmed on the following poll instead of after the regular
        refresh interval.
        """
        self._force_config_fetch = True

    def _config_fetch_due(self) -> bool:
        """Return True if the setpoints should be re-read on this poll."""
        if self._force_config_fetch or not self._config_cache:
            return True
        return (time.monotonic() - self._last_config_fetch) >= CONFIG_REFRESH_INTERVAL

    async def _fetch_config_values(self) -> dict[str, Any]:
        """Return the setpoint/firmware values, refreshing them when due.

        These values live behind a second HTTP request and only change when
        somebody writes them, so they are re-read at most every
        CONFIG_REFRESH_INTERVAL seconds. In between, the previously fetched
        values are reused, which removes one request per poll cycle - at the
        default 10s interval that is five of every six requests.
        """
        if not self._config_fetch_due():
            return dict(self._config_cache)

        try:
            config_data = await self.api.get_config(self._build_config_keys())
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning(
                "Optional getConfig fetch failed for '%s': %s",
                self.device_name,
                err,
            )
            # Keep serving the last known values instead of dropping the keys.
            return dict(self._config_cache)

        self._last_config_fetch = time.monotonic()
        self._force_config_fetch = False
        if isinstance(config_data, dict):
            # Merge instead of replace: SYSTEM_availableversion is only part of
            # some fetches and must survive the cycles that omit it.
            self._config_cache.update(config_data)

        return dict(self._config_cache)

    def _record_failure(self, reason: str, err: Exception | None = None) -> UpdateFailed:
        """Count one failed poll and return the UpdateFailed to raise for it.

        Every failed poll must raise: the DataUpdateCoordinator already keeps
        the last good data and flips entity availability on its own, so
        returning the previous readings here would republish them as freshly
        read values. The failure counter therefore only decides how loudly the
        failure is logged and when the controller is declared unavailable.

        Args:
            reason: Short, human-readable description of what went wrong.
            err: The originating exception, if there was one.

        Returns:
            The ``UpdateFailed`` the caller is expected to raise.
        """
        self._last_error = reason
        self._consecutive_failures += 1
        # Allow the recovery message and the issue cleanup to fire again after
        # this new outage.
        self._recovery_logged = False
        self._system_health = max(0.0, 100.0 - (self._consecutive_failures * 20.0))
        self._error_handler.record_error(self._error_handler.classify_error(err or Exception(reason)))

        message = f"Controller '{self.device_name}' update failed: {reason}"

        if self._consecutive_failures >= self._max_consecutive_failures:
            if not self._unavailable_reported:
                _LOGGER.error(
                    "Controller '%s' marked unavailable after %d consecutive failures: %s",
                    self.device_name,
                    self._consecutive_failures,
                    reason,
                )
                self._unavailable_reported = True
            self._available = False
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
        elif self._consecutive_failures == 1:
            # A failure before the controller has ever answered is ordinary
            # setup noise - Home Assistant retries the entry on its own.
            if self._available or self._data:
                _LOGGER.warning("%s", message)
            else:
                _LOGGER.debug("%s", message)
        elif self._should_log_failure():
            _LOGGER.warning(
                "Controller '%s' still unreachable (%d/%d failures): %s",
                self.device_name,
                self._consecutive_failures,
                self._max_consecutive_failures,
                reason,
            )

        return UpdateFailed(message)

    async def async_update(self) -> dict[str, Any]:
        """Fetch and return updated device data from the controller.

        Returns:
            The current controller data.

        Raises:
            VioletAuthError: When the controller rejects the credentials, so
                the coordinator can start the re-auth flow.
            UpdateFailed: On every failed poll. Stale readings are never
                returned as a successful update.
        """
        try:
            async with self._api_lock:
                start_time = time.monotonic()
                self._api_request_count += 1
                data = await self._fetch_controller_data()
                self._connection_latency = (time.monotonic() - start_time) * 1000
                self._latency_history.append(self._connection_latency)

                if not data or not isinstance(data, dict):
                    raise self._record_failure(
                        "empty or invalid response",
                        VioletPoolAPIError("Controller returned empty or invalid data"),
                    )

                # Merge the config-based setpoints and the firmware version.
                # They are re-read only every CONFIG_REFRESH_INTERVAL seconds
                # (see _fetch_config_values) because each read is a second HTTP
                # request and the values only change on a write.
                data.update(await self._fetch_config_values())

                if self._consecutive_failures > 0 and not self._recovery_logged:
                    _LOGGER.info(
                        "Controller '%s' reachable again (after %d failure%s)",
                        self.device_name,
                        self._consecutive_failures,
                        "s" if self._consecutive_failures > 1 else "",
                    )
                    self._recovery_logged = True
                    async_delete_issue(
                        self.hass,
                        DOMAIN,
                        f"controller_unavailable_{self.config_entry.entry_id}",
                    )

                self._data = data
                self._available = True
                self._consecutive_failures = 0
                self._unavailable_reported = False
                self._last_error = None
                self._last_update_time = time.monotonic()
                self._system_health = 100.0
                self._error_handler.record_success()

                fw_candidates = [
                    data.get("SYSTEM_swversion"),
                    data.get("FW"),
                    data.get("fw"),
                    data.get("SW_VERSION"),
                    data.get("sw_version"),
                    data.get("VERSION"),
                    data.get("version"),
                    data.get("SYSTEM_carrierboard_swversion"),
                    data.get("SW_VERSION_CARRIER"),
                    data.get("FIRMWARE_VERSION"),
                    data.get("firmware_version"),
                ]
                for candidate in fw_candidates:
                    if candidate is not None and str(candidate).strip():
                        self._firmware_version = str(candidate).strip()
                        break

                if self._firmware_version and not self._fw_logged:
                    _LOGGER.debug("Firmware version detected: %s", self._firmware_version)
                    self._fw_logged = True

                self._update_counter += 1
                now_dt = dt_util.utcnow()
                if self._first_poll is None:
                    self._first_poll = now_dt

                flow_value = (
                    data.get("IMP2_value")
                    if data.get("IMP2_value") is not None
                    else data.get("ADC3_value")
                )
                snapshot = (
                    data.get("onewire1_value"),
                    data.get("orp_value"),
                    data.get("pH_value"),
                    data.get("pot_value"),
                    data.get("ADC2_value"),
                    flow_value,
                    data.get("IMP1_value"),
                )
                self._poll_history.append((now_dt, len(data), self._connection_latency, snapshot))

                _LOGGER.debug(
                    "Update #%d for '%s': %d keys fetched in %.3fs",
                    self._update_counter,
                    self.device_name,
                    len(data),
                    self._connection_latency / 1000,
                )

                return self._data

        except UpdateFailed:
            # Already counted and logged by _record_failure.
            raise
        except VioletAuthError:
            # Auth errors must surface immediately so HA can trigger re-auth
            raise
        except VioletPoolAPIError as err:
            raise self._record_failure(str(err)[:200], err) from err

        except Exception as err:
            if self._consecutive_failures == 0:
                # One traceback per outage; _record_failure throttles the rest.
                _LOGGER.debug(
                    "Unexpected error during update of '%s'",
                    self.device_name,
                    exc_info=err,
                )
            raise self._record_failure(f"{type(err).__name__}: {err}", err) from err

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
    def error_handler(self) -> EnhancedErrorHandler:
        """Return this controller's error statistics handler.

        One handler per device, fed by every failed and successful poll, so
        diagnostics and the ``get_error_summary`` service report the errors of
        this controller alone instead of a process-wide mixture.
        """
        return self._error_handler

    def _detect_current_hardware_modules(self) -> list[str]:
        """Detect currently present hardware modules from API data (not cached).

        Returns list of module names based on actual API keys present,
        not on historical detections. Module names follow the products
        PoolDigital sells (Basis-Modul, Dosier-Modul, Relais-Erweiterung).
        """
        extra_modules = []

        def has_keys(prefix: str) -> bool:
            """Check if any valid keys start with the given prefix."""
            return any(k.startswith(prefix) and self._data.get(k) is not None for k in self._data)

        # Relay extensions: the firmware reports every EXT*_ key - with
        # stale values for relays of modules that are not connected - so
        # presence follows the alive-count keys, which the carrier only
        # sends for attached modules (same rule the API package applies
        # to getReadings).
        extensions = [
            index
            for index in (1, 2)
            if f"SYSTEM_ext{index}module_alive_count" in self._data
        ]
        if len(extensions) == 1:
            extra_modules.append("Relais-Erweiterung")
        elif len(extensions) == 2:
            extra_modules.extend(("Relais-Erweiterung 1", "Relais-Erweiterung 2"))

        # Dosing module (integrated dosing on the base module is a
        # function, not the plug-in Dosier-Modul).
        if self._data.get("HW_STANDALONE_MODE"):
            extra_modules.append("Dosier-Funktion")
        elif "SYSTEM_dosagemodule_alive_count" in self._data or has_keys("DOS_"):
            extra_modules.append("Dosier-Modul")

        # Check DMX module
        if has_keys("DMX_"):
            extra_modules.append("DMX-Modul")

        # Check Digital Input Rules module
        if has_keys("DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_"):
            extra_modules.append("DiRule")

        return extra_modules

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for Home Assistant."""
        # Build a readable model string from currently detected hardware modules.
        # "Base" is omitted when it is the only module to avoid redundancy.
        extra_modules = self._detect_current_hardware_modules()

        model_str = (
            "Violet Pool Controller (" + ", ".join(extra_modules) + ")"
            if extra_modules
            else "Violet Pool Controller"
        )

        info = DeviceInfo(
            # Keyed on the config entry, never on host/port: a reconfigure that
            # moves the controller to a new IP must keep the very same device,
            # with the name and area the user gave it.
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=self.controller_name,
            manufacturer="PoolDigital GmbH & Co. KG",
            model=model_str,
            sw_version=self._firmware_version or "Unknown",
            suggested_area=self.controller_name,
        )
        for _serial_key in ("SERIAL", "SERIAL_NUMBER", "serial", "serial_number", "HW_SERIAL"):
            _serial_val = self._data.get(_serial_key)
            if _serial_val:
                info["serial_number"] = str(_serial_val)
                break
        return info

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
    def hardware_config(self) -> dict[str, Any] | None:
        """Get cached complete hardware configuration."""
        return self._hardware_config

    async def load_hardware_config(self) -> dict[str, Any] | None:
        """Load complete hardware configuration from controller.

        Reads ALL configurable names and parameters:
        - Digital Inputs (DI1-12)
        - Extension Relays (EXT1_1-8, EXT2_1-8)
        - DMX Scenes (LIGHT_SCENE_1-12)
        - Dosing Systems (Chlorine, pH±, Flocculant, etc.)
        - Temperature Sensors (1-8)
        - Analog Inputs (AI1-8)
        - Output Parameters (Pump, Heater, Solar, etc.)
        - Pool Configuration

        Caches result in _hardware_config.
        """
        if self._hardware_config_loaded:
            return self._hardware_config

        try:
            # Request all configuration keys (wildcard patterns)
            config_keys = [
                "NAMES_",  # All named elements
                "SWITCHINGRULE_",  # Digital input rules
                "LIGHT_prog",  # DMX scenes
                "DOSAGE_",  # Dosing systems
                "EXT",  # Extension relays
                "POOL_",  # Pool config
                "onewire",  # Temperature sensors
                "AI",  # Analog inputs
                "PUMP_",
                "HEATER_",
                "SOLAR_",
                "COVER_",
                "BACKWASH_",  # Outputs
            ]

            config_response = await self.api.get_config(config_keys)

            if not config_response:
                _LOGGER.warning("No hardware configuration returned from controller")
                self._hardware_config_loaded = True
                return None

            # Parse complete hardware configuration
            hw_config = HardwareConfig(config_response)
            self._hardware_config = hw_config.get_all_configs()

            # Log summary
            _LOGGER.info(
                "Loaded hardware configuration:\n%s",
                hw_config.summary(),
            )

            enabled = hw_config.get_enabled_features()
            _LOGGER.debug(
                "Enabled features: DI=%d, Relays=%d, Dosing=%d, Scenes=%d",
                len(enabled["digital_inputs"]),
                len(enabled["extension_relays"]),
                len(enabled["dosing_systems"]),
                len(enabled["dmx_scenes"]),
            )

            self._hardware_config_loaded = True
            return self._hardware_config

        except Exception as err:
            # Deliberately NOT marking the config as loaded: a transient error
            # here would otherwise cost every controller-provided name until
            # the next restart. The next reload retries instead.
            _LOGGER.error("Failed to load hardware configuration: %s", err)
            return None

    # Convenience property for backward compatibility
    @property
    def di_config(self) -> dict[str, Any] | None:
        """Get cached digital input configuration (from hardware_config)."""
        if self._hardware_config:
            return self._hardware_config.get("digital_inputs")
        return None


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator[VioletReadings]):
    """Data update coordinator for the Violet Pool Controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: VioletPoolControllerDevice,
        name: str,
        polling_interval: int = DEFAULT_POLLING_INTERVAL,
        adaptive_polling: bool = DEFAULT_ADAPTIVE_POLLING,
    ) -> None:
        """Initialize the coordinator."""
        # The configured interval. update_interval may be stretched beyond it
        # while the controller is idle, but never falls below it. Clamped
        # before it reaches the coordinator so a bad stored value can never
        # turn into a hot polling loop.
        base_interval = _clamp_polling_interval(polling_interval)
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=base_interval),
            config_entry=device.config_entry,
        )
        self.device = device
        self._setpoint_cache: dict[str, float] = {}
        self._base_interval = base_interval
        self._adaptive_polling = bool(adaptive_polling)

        _LOGGER.info(
            "Coordinator initialized for '%s' (polling every %ds, adaptive: %s)",
            name,
            self._base_interval,
            self._adaptive_polling,
        )

    @property
    def base_interval(self) -> int:
        """Return the configured polling interval in seconds.

        ``update_interval`` can be larger than this while the controller is
        idle, so this is the value to compare configuration changes against.
        """
        return self._base_interval

    @property
    def adaptive_polling(self) -> bool:
        """Return whether idle back-off is enabled."""
        return self._adaptive_polling

    def apply_polling_options(self, polling_interval: int, adaptive_polling: bool) -> bool:
        """Apply changed polling options to the running coordinator.

        Returns:
            True if anything changed, False otherwise.
        """
        new_interval = _clamp_polling_interval(polling_interval)
        changed = (
            new_interval != self._base_interval
            or bool(adaptive_polling) != self._adaptive_polling
        )
        if not changed:
            return False

        self._base_interval = new_interval
        self._adaptive_polling = bool(adaptive_polling)
        # Take effect right away; the next poll re-evaluates the idle back-off.
        self.update_interval = timedelta(seconds=new_interval)
        return True

    def _is_controller_active(self, data: dict[str, Any]) -> bool:
        """Return True if any pool output is currently running.

        Values arrive as ints, numeric strings or composite strings such as
        ``"3|PUMP_ANTI_FREEZE"``, so they are interpreted with the same helper
        the switch entities use instead of being compared numerically.
        """
        # Imported here on purpose: entity.py imports this module at import
        # time, so a module-level import would be circular.
        from .entity import interpret_state_as_bool

        return any(interpret_state_as_bool(data.get(key), key) for key in ADAPTIVE_ACTIVITY_KEYS)

    def _resolve_update_interval(self, is_active: bool) -> timedelta:
        """Return the interval to use until the next poll.

        The configured interval is the fastest rate; while nothing is running
        the controller is polled less often to keep load off its web server.
        """
        if not self._adaptive_polling or is_active:
            return timedelta(seconds=self._base_interval)

        idle_interval = min(self._base_interval * ADAPTIVE_IDLE_FACTOR, ADAPTIVE_IDLE_MAX_INTERVAL)
        return timedelta(seconds=max(self._base_interval, idle_interval))

    def update_setpoint_cache(self, key: str, value: float) -> None:
        """Cache a setpoint write and immediately notify all listeners.

        This lets entities show the new value without waiting for the next
        poll cycle. The cache entry persists until the next successful poll
        returns the key, at which point coordinator.data takes precedence.
        """
        self._setpoint_cache[key] = value
        # Setpoints are read on a timer; confirm this write on the next poll.
        self.device.request_config_refresh()
        self.async_update_listeners()

    async def _async_update_data(self) -> VioletReadings:
        """
        Update data from the device.

        Returns a VioletReadings snapshot on every call so that
        HA's DataUpdateCoordinator always sees a new data object and
        triggers entity listener callbacks.

        Returns:
            A VioletReadings snapshot of the updated data.

        Raises:
            ConfigEntryAuthFailed: On HTTP 401/403 (triggers re-auth flow).
            UpdateFailed: If the update fails for any other reason.
        """
        try:
            data = await self.device.async_update()
            if not data:
                raise UpdateFailed(f"Empty data returned for '{self.device.device_name}'")

            # Stretch the interval while the pool equipment is idle. Never
            # polls faster than the interval the user configured.
            is_active = self._is_controller_active(data)
            new_interval = self._resolve_update_interval(is_active)
            if self.update_interval != new_interval:
                self.update_interval = new_interval
                _LOGGER.debug(
                    "Polling interval changed to %ds (configured: %ds, active: %s)",
                    new_interval.total_seconds(),
                    self._base_interval,
                    is_active,
                )

            # Invalidate setpoint cache entries that now exist in fresh data.
            # This ensures: after writes show cached values, but polls restore live data.
            for key in list(self._setpoint_cache.keys()):
                if key in data:
                    del self._setpoint_cache[key]

            return VioletReadings(data)
        except ConfigEntryAuthFailed:
            raise
        except VioletAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
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
    """Set up the Violet Pool Controller device and return a coordinator.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry being set up.
        api: The API client to talk to the controller with.

    Returns:
        The coordinator driving this controller.

    Raises:
        ConfigEntryAuthFailed: When the controller rejects the credentials, so
            Home Assistant opens the re-auth flow instead of retrying forever.
        ConfigEntryNotReady: When the controller cannot be reached.
    """
    try:
        device = VioletPoolControllerDevice(hass, config_entry, api)

        polling_interval = get_entry_value(
            config_entry,
            CONF_POLLING_INTERVAL,
            DEFAULT_POLLING_INTERVAL,
        )
        adaptive_polling = get_entry_value(
            config_entry,
            CONF_ADAPTIVE_POLLING,
            DEFAULT_ADAPTIVE_POLLING,
        )

        coordinator = VioletPoolDataUpdateCoordinator(
            hass,
            device,
            config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
            polling_interval,
            adaptive_polling,
        )

        # Exactly one attempt. Home Assistant already retries
        # ConfigEntryNotReady with an exponential backoff, so a second retry
        # loop here would only cost four to six extra requests per start - and
        # it used to swallow the auth failure that must reach the re-auth flow.
        await coordinator.async_config_entry_first_refresh()

        # The controller answered, so a "controller unavailable" repair issue
        # left over from an earlier outage is stale. It has to be removed here
        # rather than only in the device that raised it: after a restart the
        # recovering device object is a different one, and the issue would sit
        # in the repairs list until the user clicked "Fix".
        async_delete_issue(hass, DOMAIN, f"controller_unavailable_{config_entry.entry_id}")

        # Load complete hardware configuration for dynamic entity naming
        await device.load_hardware_config()

        _LOGGER.info(
            "Device setup successful: '%s' (FW: %s, %d data points)",
            device.device_name,
            device.firmware_version or "Unknown",
            len(device.data) if device.data else 0,
        )

        return coordinator

    except ConfigEntryAuthFailed:
        # Must not be turned into ConfigEntryNotReady - that would retry a
        # wrong password forever instead of asking the user for a new one.
        raise

    except ConfigEntryNotReady:
        raise

    except VioletAuthError as err:
        raise ConfigEntryAuthFailed(str(err)) from err

    except Exception as err:
        _LOGGER.exception("Device setup failed: %s", err)
        raise ConfigEntryNotReady(f"Setup error: {err}") from err
