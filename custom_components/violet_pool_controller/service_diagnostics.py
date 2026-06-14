"""Diagnostic service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .service_helpers import (
    as_device_id_list,
    read_recent_violet_log_lines,
    write_text_file,
)

_LOGGER = logging.getLogger(__name__)
_POLL_SNAPSHOT_FIELDS = (
    "Pool Temp",
    "Redox",
    "pH",
    "Chlorine",
    "Overflow",
    "Flow",
    "Inflow",
)


class VioletDiagnosticServiceHandlers:
    """Handlers for diagnostic and response-oriented services."""

    hass: Any
    manager: Any

    async def _get_first_coordinator(self, device_ids: list[str]) -> Any:
        """Return the first coordinator found for any provided device id."""
        for device_id in device_ids:
            coordinator = await self.manager.get_coordinator_for_device(device_id)
            if coordinator:
                return coordinator
        raise HomeAssistantError(f"Device not found: {device_ids[0]}")

    async def _get_device_for_id(self, device_id: str) -> Any:
        """Resolve and validate a device object for a given device id."""
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator or not hasattr(coordinator, "device"):
            raise HomeAssistantError(f"Device {device_id} not found")
        return coordinator.device

    @staticmethod
    def _device_label(device: Any) -> str:
        """Return a stable device name for response payloads."""
        return getattr(device, "device_name", "Unknown")

    async def handle_export_diagnostic_logs(self, call: ServiceCall) -> dict[str, Any]:
        """Handle the export diagnostic logs service."""
        device_ids = as_device_id_list(call.data[ATTR_DEVICE_ID])
        lines = max(10, min(10000, int(call.data.get("lines", 100))))
        include_timestamps = call.data.get("include_timestamps", True)
        include_config = call.data.get("include_config", True)
        include_history = call.data.get("include_history", True)
        include_states = call.data.get("include_states", True)
        include_raw_data = call.data.get("include_raw_data", True)
        save_to_file = call.data.get("save_to_file", False)

        coordinator = await self._get_first_coordinator(device_ids)

        try:
            log_entries: list[str] = []
            device_name = coordinator.device.device_name

            log_path = self.hass.config.path("home-assistant.log")
            try:
                log_entries.extend(
                    await self.hass.async_add_executor_job(
                        self._read_recent_violet_log_lines,
                        log_path,
                        lines,
                        include_timestamps,
                    )
                )
            except Exception as err:
                _LOGGER.warning("Could not read log file: %s", err)

            if not log_entries:
                self._append_system_snapshot(
                    log_entries,
                    coordinator,
                    include_config=include_config,
                    include_history=include_history,
                    include_states=include_states,
                    include_raw_data=include_raw_data,
                )

            export_text = self._build_export_text(device_name, log_entries)

            if save_to_file:
                filename = (
                    f"violet_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
                filepath = f"/config/{filename}"

                try:
                    await self.hass.async_add_executor_job(
                        write_text_file, filepath, export_text
                    )
                except Exception as err:
                    _LOGGER.error("Failed to save log file: %s", err)
                    raise HomeAssistantError(f"Failed to save log file: {err}") from err

                _LOGGER.info(
                    "Diagnostic logs exported to file: %s (%d lines)",
                    filename,
                    len(log_entries),
                )
                return {
                    "success": True,
                    "filename": filename,
                    "filepath": filepath,
                    "lines_exported": len(log_entries),
                    "message": f"Logs saved to {filename} ({len(log_entries)} lines)",
                }

            _LOGGER.info(
                "Diagnostic logs exported: %d lines for device %s",
                len(log_entries),
                device_name,
            )
            return {
                "success": True,
                "lines_exported": len(log_entries),
                "logs": export_text,
                "message": f"Exported {len(log_entries)} log lines",
            }

        except Exception as err:
            _LOGGER.error("Log export error: %s", err)
            raise HomeAssistantError(f"Log export failed: {err}") from err

    async def handle_get_connection_status(self, call: ServiceCall) -> dict[str, Any]:
        """Handle get connection status diagnostic service."""
        from .error_handler import get_enhanced_error_handler

        device_ids = as_device_id_list(call.data[ATTR_DEVICE_ID])
        results = []

        for device_id in device_ids:
            try:
                device = await self._get_device_for_id(device_id)
                error_handler = get_enhanced_error_handler()

                results.append(
                    {
                        "device_name": self._device_label(device),
                        "device_id": device_id,
                        "available": getattr(device, "_available", False),
                        "last_update": getattr(device, "_last_update_time", 0),
                        "connection_latency_ms": getattr(
                            device, "_connection_latency", 0
                        ),
                        "system_health": getattr(device, "_system_health", 0),
                        "consecutive_failures": getattr(
                            device, "_consecutive_failures", 0
                        ),
                        "api_url": getattr(device, "api_url", "Unknown"),
                        "use_ssl": getattr(device, "use_ssl", False),
                        "error_summary": error_handler.get_error_summary(),
                    }
                )

            except Exception as err:
                _LOGGER.error("Get connection status error: %s", err)
                raise HomeAssistantError(
                    f"Failed to get connection status: {err}"
                ) from err

        return {
            "success": True,
            "devices": results,
            "message": f"Retrieved status for {len(results)} device(s)",
        }

    async def handle_get_error_summary(self, call: ServiceCall) -> dict[str, Any]:
        """Handle get error summary diagnostic service."""
        from .error_handler import get_enhanced_error_handler

        device_ids = as_device_id_list(call.data[ATTR_DEVICE_ID])
        include_history = call.data.get("include_history", False)
        results = []

        for device_id in device_ids:
            try:
                device = await self._get_device_for_id(device_id)
                error_handler = get_enhanced_error_handler()

                result: dict[str, Any] = {
                    "device_name": self._device_label(device),
                    "device_id": device_id,
                    "error_summary": error_handler.get_error_summary(),
                    "recovery_suggestion": error_handler.get_recovery_suggestion(),
                }

                if include_history:
                    recent_errors = error_handler.get_recent_errors(count=10)
                    result["error_history"] = [err.to_dict() for err in recent_errors]

                results.append(result)

            except Exception as err:
                _LOGGER.error("Get error summary error: %s", err)
                raise HomeAssistantError(f"Failed to get error summary: {err}") from err

        return {
            "success": True,
            "devices": results,
            "message": f"Retrieved error summary for {len(results)} device(s)",
        }

    async def handle_test_connection(self, call: ServiceCall) -> dict[str, Any]:
        """Handle test connection diagnostic service."""
        import time

        device_ids = as_device_id_list(call.data[ATTR_DEVICE_ID])
        results = []

        for device_id in device_ids:
            try:
                device = await self._get_device_for_id(device_id)
                api = getattr(device, "api", None)
                if not api:
                    raise HomeAssistantError("API not available")

                start_time = time.monotonic()

                try:
                    readings = await api.get_readings()
                    latency_ms = (time.monotonic() - start_time) * 1000
                    result = {
                        "device_name": self._device_label(device),
                        "device_id": device_id,
                        "success": True,
                        "latency_ms": round(latency_ms, 2),
                        "keys_received": len(readings)
                        if isinstance(readings, dict)
                        else 0,
                        "message": "Connection successful",
                    }
                except Exception as api_err:
                    result = {
                        "device_name": self._device_label(device),
                        "device_id": device_id,
                        "success": False,
                        "error": str(api_err),
                        "message": f"Connection failed: {api_err}",
                    }

                results.append(result)

            except Exception as err:
                _LOGGER.error("Test connection error: %s", err)
                raise HomeAssistantError(f"Failed to test connection: {err}") from err

        return {
            "success": True,
            "tests": results,
            "message": f"Tested connection for {len(results)} device(s)",
        }

    async def handle_clear_error_history(self, call: ServiceCall) -> dict[str, Any]:
        """Handle clear error history service."""
        from .error_handler import get_enhanced_error_handler

        device_ids = as_device_id_list(call.data[ATTR_DEVICE_ID])
        cleared_count = 0

        for device_id in device_ids:
            try:
                await self._get_device_for_id(device_id)

                error_handler = get_enhanced_error_handler()
                error_handler.clear_history()
                cleared_count += 1

            except Exception as err:
                _LOGGER.error("Clear error history error: %s", err)
                raise HomeAssistantError(
                    f"Failed to clear error history: {err}"
                ) from err

        _LOGGER.info("Cleared error history for %d device(s)", cleared_count)
        return {
            "success": True,
            "cleared_count": cleared_count,
            "message": f"Cleared error history for {cleared_count} device(s)",
        }

    async def handle_get_calibration_status(
        self, call: ServiceCall
    ) -> dict[str, Any]:
        """Get sensor calibration status."""
        from .calibration_helper import parse_calibration_data

        coordinator = await self._get_first_coordinator(
            as_device_id_list(call.data.get(ATTR_DEVICE_ID))
        )

        if not coordinator.data:
            raise HomeAssistantError("No data available from controller")

        calibrations = parse_calibration_data(coordinator.data)

        return {
            "success": True,
            "device": coordinator.device.device_name,
            "calibrations": {
                name: status.to_dict() for name, status in calibrations.items()
            },
            "message": f"Retrieved calibration status for {len(calibrations)} sensors",
        }

    async def handle_get_backwash_status(self, call: ServiceCall) -> dict[str, Any]:
        """Get backwash maintenance status."""
        from .sensor_organization import BACKWASH_STATES, BACKWASH_STEPS

        coordinator = await self._get_first_coordinator(
            as_device_id_list(call.data.get(ATTR_DEVICE_ID))
        )

        if not coordinator.data:
            raise HomeAssistantError("No data available from controller")

        backwash_state = coordinator.data.get("BACKWASH_STATE", 0)
        backwash_step = coordinator.data.get("BACKWASH_STEP", 0)
        last_auto_run = coordinator.data.get("BACKWASH_LAST_AUTO_RUN")
        last_manual_run = coordinator.data.get("BACKWASH_LAST_MANUAL_RUN")
        filter_pressure = coordinator.data.get("FILTER_PRESSURE", 0)

        return {
            "success": True,
            "device": coordinator.device.device_name,
            "backwash_state": BACKWASH_STATES.get(int(backwash_state), "Unknown"),
            "backwash_step": BACKWASH_STEPS.get(int(backwash_step), "Unknown"),
            "is_running": int(backwash_state) == 1,
            "last_auto_run": last_auto_run,
            "last_manual_run": last_manual_run,
            "filter_pressure": filter_pressure,
            "message": f"Backwash status: {BACKWASH_STATES.get(int(backwash_state), 'Unknown')}",
        }

    async def handle_get_system_update_status(
        self, call: ServiceCall
    ) -> dict[str, Any]:
        """Get system firmware update status."""
        from .update_helper import parse_firmware_info

        coordinator = await self._get_first_coordinator(
            as_device_id_list(call.data.get(ATTR_DEVICE_ID))
        )

        if not coordinator.data:
            raise HomeAssistantError("No data available from controller")

        firmware_info = parse_firmware_info(coordinator.data)

        return {
            "success": True,
            "device": coordinator.device.device_name,
            "installed_version": firmware_info.installed_version,
            "available_version": firmware_info.available_version,
            "update_available": firmware_info.update_available,
            "carrier_version": firmware_info.carrier_version,
            "message": firmware_info.update_description,
            "release_notes": firmware_info.release_notes,
        }

    @staticmethod
    def _read_recent_violet_log_lines(
        log_path: str, lines: int, include_timestamps: bool
    ) -> list[str]:
        """Wrapper kept local for stable executor introspection in tests."""
        return read_recent_violet_log_lines(log_path, lines, include_timestamps)

    def _append_system_snapshot(
        self,
        log_entries: list[str],
        coordinator: Any,
        *,
        include_config: bool,
        include_history: bool,
        include_states: bool,
        include_raw_data: bool,
    ) -> None:
        """Populate fallback diagnostic details when no raw HA logs are found."""
        log_entries.append("=== Violet Pool Controller Diagnostic Export ===")
        log_entries.append(f"Device: {coordinator.device.device_name}")
        log_entries.append(f"Timestamp: {datetime.now().isoformat()}")
        log_entries.append("")
        log_entries.append("Controller Information:")
        log_entries.append(f"  Name: {coordinator.device.controller_name}")
        log_entries.append(f"  API URL: {coordinator.device.api_url}")
        log_entries.append(f"  Device ID: {coordinator.device.device_id}")
        log_entries.append(f"  Available: {coordinator.device.available}")
        log_entries.append(
            f"  Firmware: {coordinator.device.firmware_version or 'Unknown'}"
        )
        log_entries.append(
            f"  Last Update: {coordinator.device.last_event_age:.1f}s ago"
        )
        log_entries.append(
            f"  Connection Latency: {coordinator.device.connection_latency:.1f}ms"
        )
        log_entries.append(f"  System Health: {coordinator.device.system_health:.0f}%")
        log_entries.append(f"  Update Counter: {coordinator.device._update_counter}")
        log_entries.append(
            f"  Consecutive Failures: {coordinator.device.consecutive_failures}"
        )
        log_entries.append("")

        self._append_system_info(log_entries)

        if include_config:
            self._append_config_info(log_entries, coordinator)
        if include_history:
            self._append_poll_history(log_entries, coordinator)
        if include_states:
            self._append_entity_states(log_entries, coordinator)
        if include_raw_data:
            self._append_raw_data(log_entries, coordinator)

        log_entries.append("No detailed log entries found in home-assistant.log.")
        log_entries.append("Logs may have been rotated or not contain recent entries.")

        try:
            logger = logging.getLogger("custom_components.violet_pool_controller")
            if logger.getEffectiveLevel() > logging.DEBUG:
                log_entries.append("")
                log_entries.append("NOTE: Debug logging is currently disabled.")
                log_entries.append(
                    "To see more details, enable debug logging for this integration."
                )
        except Exception:
            pass

    def _append_system_info(self, log_entries: list[str]) -> None:
        """Append generic Home Assistant system information."""
        log_entries.append("System Information:")
        try:
            log_entries.append(f"  Home Assistant: {HA_VERSION}")

            hacs = self.hass.data.get("hacs")
            if hacs:
                hacs_version = getattr(hacs, "version", None) or getattr(
                    hacs, "integration_version", "Unknown"
                )
                log_entries.append(f"  HACS: {hacs_version}")

            if "hassio" in self.hass.config.components:
                log_entries.append(
                    "  Installation Type: Home Assistant OS / Supervised"
                )
            else:
                log_entries.append("  Installation Type: Core / Container (likely)")

            log_entries.append(f"  Timezone: {self.hass.config.time_zone}")

            components = sorted(self.hass.config.components)
            log_entries.append(f"  Loaded Components ({len(components)}):")
            chunk_size = 5
            for index in range(0, len(components), chunk_size):
                chunk = components[index : index + chunk_size]
                log_entries.append(f"    {', '.join(chunk)}")

        except Exception as err:
            log_entries.append(f"  Error retrieving system info: {err}")

        log_entries.append("")

    def _append_config_info(self, log_entries: list[str], coordinator: Any) -> None:
        """Append sanitized configuration details."""
        if not hasattr(coordinator, "config_entry") or not coordinator.config_entry:
            return

        from .const import (
            CONF_ACTIVE_FEATURES,
            CONF_DISINFECTION_METHOD,
            CONF_FORCE_UPDATE,
            CONF_POLLING_INTERVAL,
            CONF_POOL_SIZE,
            CONF_POOL_TYPE,
            CONF_RETRY_ATTEMPTS,
            CONF_SELECTED_SENSORS,
            CONF_TIMEOUT_DURATION,
            CONF_USE_SSL,
            CONF_VERIFY_SSL,
        )
        from .const_features import AVAILABLE_FEATURES

        config = coordinator.config_entry.data
        log_entries.append("Configuration Settings:")

        safe_keys = {
            "Polling Interval": CONF_POLLING_INTERVAL,
            "Timeout": CONF_TIMEOUT_DURATION,
            "Retries": CONF_RETRY_ATTEMPTS,
            "Force Update": CONF_FORCE_UPDATE,
            "Use SSL": CONF_USE_SSL,
            "Verify SSL": CONF_VERIFY_SSL,
            "Pool Size": CONF_POOL_SIZE,
            "Pool Type": CONF_POOL_TYPE,
            "Disinfection": CONF_DISINFECTION_METHOD,
        }

        for label, key in safe_keys.items():
            if key in config:
                log_entries.append(f"  {label}: {config[key]}")

        if CONF_ACTIVE_FEATURES in config and isinstance(
            config[CONF_ACTIVE_FEATURES], list
        ):
            features = config[CONF_ACTIVE_FEATURES]
            enabled_features: list[str] = []
            disabled_features: list[str] = []

            for feature in AVAILABLE_FEATURES:
                if feature["id"] in features:
                    enabled_features.append(str(feature["name"]))
                else:
                    disabled_features.append(str(feature["name"]))

            log_entries.append(f"  Active Features: {len(enabled_features)} enabled")
            if enabled_features:
                log_entries.append(
                    f"    Enabled: {', '.join(sorted(enabled_features))}"
                )
            if disabled_features:
                log_entries.append(
                    f"    Disabled: {', '.join(sorted(disabled_features))}"
                )

        if CONF_SELECTED_SENSORS in config and isinstance(
            config[CONF_SELECTED_SENSORS], list
        ):
            sensors = config[CONF_SELECTED_SENSORS]
            log_entries.append(f"  Selected Sensors: {len(sensors)} enabled")

        log_entries.append("")

    @staticmethod
    def _append_poll_history(log_entries: list[str], coordinator: Any) -> None:
        """Append recent polling history when available."""
        if (
            not hasattr(coordinator.device, "_first_poll")
            or not coordinator.device._first_poll
        ):
            return

        log_entries.append("Polling History:")
        log_entries.append(
            f"  First Poll:"
            f" {coordinator.device._first_poll.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if (
            hasattr(coordinator.device, "_poll_history")
            and coordinator.device._poll_history
        ):
            history = coordinator.device._poll_history
            log_entries.append(f"  Last {len(history)} Polls:")
            for item in history:
                if len(item) == 4:
                    timestamp, count, latency, snapshot = item
                    details = []
                    if isinstance(snapshot, dict):
                        for key in _POLL_SNAPSHOT_FIELDS:
                            if key in snapshot:
                                details.append(f"{key}: {snapshot[key]}")
                    else:
                        for key, value in zip(_POLL_SNAPSHOT_FIELDS, snapshot):
                            if value is not None:
                                details.append(f"{key}: {value}")

                    detail_str = " | ".join(details)
                    log_entries.append(
                        f"    - {timestamp.strftime('%H:%M:%S')}:"
                        f" {count} items ({latency:.1f}ms) -> {detail_str}"
                    )
                else:
                    timestamp, count, latency = item
                    log_entries.append(
                        f"    - {timestamp.strftime('%H:%M:%S')}:"
                        f" {count} items ({latency:.1f}ms)"
                    )
        else:
            log_entries.append("  No history available.")

        log_entries.append("")

    def _append_entity_states(self, log_entries: list[str], coordinator: Any) -> None:
        """Append entity state dump for the config entry."""
        try:
            if not hasattr(coordinator, "config_entry") or not coordinator.config_entry:
                return

            entry_id = coordinator.config_entry.entry_id
            registry = er.async_get(self.hass)
            entities = er.async_entries_for_config_entry(registry, entry_id)

            if not entities:
                return

            log_entries.append("Entity States:")
            sorted_entities = sorted(entities, key=lambda entity: entity.entity_id)

            for entity in sorted_entities:
                state = self.hass.states.get(entity.entity_id)
                if state:
                    attrs = dict(state.attributes)
                    attr_str = str(attrs)
                    if len(attr_str) > 200:
                        attr_str = attr_str[:197] + "..."

                    log_entries.append(
                        f"  - {entity.entity_id}: {state.state} (attrs: {attr_str})"
                    )
                else:
                    log_entries.append(f"  - {entity.entity_id}: <No State>")

            log_entries.append("")
        except Exception as err:
            _LOGGER.warning("Could not dump entity states: %s", err)
            log_entries.append(f"Error dumping entity states: {err}")
            log_entries.append("")

    @staticmethod
    def _append_raw_data(log_entries: list[str], coordinator: Any) -> None:
        """Append redacted raw coordinator data."""
        try:
            import json

            if not hasattr(coordinator, "data") or not coordinator.data:
                return

            log_entries.append("Latest Raw Data:")
            raw_data = dict(coordinator.data)
            sensitive_keys = ["wifi_password", "password", "key", "token", "secret"]

            redacted_data = {}
            for key, value in raw_data.items():
                lower_key = str(key).lower()
                if any(sensitive in lower_key for sensitive in sensitive_keys):
                    redacted_data[key] = "***REDACTED***"
                else:
                    redacted_data[key] = value

            log_entries.append(
                json.dumps(redacted_data, indent=2, default=str, sort_keys=True)
            )
            log_entries.append("")
        except Exception as err:
            _LOGGER.warning("Could not dump raw data: %s", err)
            log_entries.append(f"Error dumping raw data: {err}")
            log_entries.append("")

    @staticmethod
    def _build_export_text(device_name: str, log_entries: list[str]) -> str:
        """Build the final exported text block."""
        export_header = f"""
{"=" * 80}
Violet Pool Controller - Diagnostic Log Export
{"=" * 80}
Device: {device_name}
Exported: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Lines: {len(log_entries)}
{"=" * 80}
"""
        return export_header + "\n".join(log_entries)
