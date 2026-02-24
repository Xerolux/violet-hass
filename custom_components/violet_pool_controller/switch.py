"""Switch Integration for the Violet Pool Controller - CHANGE-ONLY LOGGING & THREAD-SAFE."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import VioletPoolAPIError
from .const import ACTION_OFF, ACTION_ON, CONF_ACTIVE_FEATURES, DOMAIN, SWITCHES
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity, interpret_state_as_bool

_LOGGER = logging.getLogger(__name__)

# State Constants
# The Violet Pool Controller uses different states for devices:
# - 0: AUTO_OFF - Automatic mode, device is off
# - 1: AUTO_ON - Automatic mode, device is on (e.g. by schedule)
# - 2-3: Other AUTO states (e.g. warming up, preparing)
# - 4: MANUAL_ON - Manual mode, device is on
# - 5: AUTO_OFF - Alternative AUTO-OFF representation
# - 6: MANUAL_OFF - Manual mode, device is off
#
# IMPORTANT: State "4" is treated as ON, not as ERROR/UNDEFINED.
# This is a normal state for manually switched on devices.
STATE_OFF = 0
STATE_AUTO_ON = 1
STATE_MANUAL_ON = 4
STATE_AUTO_OFF = 5
STATE_MANUAL_OFF = 6

# ON_STATES: All states where the device is active (1-4)
ON_STATES = {1, 2, 3, 4}
# OFF_STATES: All states where the device is inactive (0, 5, 6)
OFF_STATES = {0, 5, 6}

REFRESH_DELAY = 0.3


class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Switch with change-only logging and thread safety."""

    entity_description: SwitchEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SwitchEntityDescription,
    ) -> None:
        """
        Initialize the switch.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            description: The switch entity description.
        """
        super().__init__(coordinator, config_entry, description)

        # ✅ LOGGING OPTIMIZATION: State-Change Detection
        self._last_logged_state: bool | None = None
        self._last_logged_raw: Any = None

        # ✅ FIXED: Local cache variable for optimistic update
        self._optimistic_state: bool | None = None

        # ✅ Log setup only, not every access
        _LOGGER.debug("Switch initialized: %s", self.entity_id)

    @property
    def is_on(self) -> bool:
        """
        Return True if the switch is on.

        Returns:
            True if on, False otherwise.
        """
        if self.coordinator.data is None:
            return False

        return self._get_switch_state()

    def _get_switch_state(self) -> bool:
        """
        Get the switch state with change-only logging and optimistic cache.

        Returns:
            The boolean state of the switch.
        """
        # Use optimistic cache while waiting for API confirmation
        if self._optimistic_state is not None:
            return self._optimistic_state

        key = self.entity_description.key
        raw_state = self.get_value(key)

        # No data available for this key
        if raw_state is None:
            return False

        # Use shared utility function
        result = interpret_state_as_bool(raw_state, key)

        # Change-Only Logging
        if result != self._last_logged_state or raw_state != self._last_logged_raw:
            _LOGGER.info(
                "Switch %s: %s → %s (raw: %s)",
                key,
                "ON"
                if self._last_logged_state
                else "OFF"
                if self._last_logged_state is not None
                else "INIT",
                "ON" if result else "OFF",
                raw_state,
            )
            self._last_logged_state = result
            self._last_logged_raw = raw_state

        return result

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """
        Return additional state attributes with descriptive status information.

        Provides human-readable mode, state description, runtime, and
        device-specific details (pump speed, dosing status, backwash info).

        Returns:
            A dictionary of attributes.
        """
        if self.coordinator.data is None:
            return {
                "status_description": "Not available",
                "mode": "unknown",
            }

        key = self.entity_description.key
        raw_state = self.get_value(key)

        # --- Base attributes: mode & description from state mapping ---
        mode, description = self._get_mode_and_description(key, raw_state)

        attributes: dict[str, Any] = {
            "mode": mode,
            "status_description": description,
            "raw_state": str(raw_state) if raw_state is not None else "None",
        }

        # Optimistic cache indicator
        if self._optimistic_state is not None:
            attributes["pending_update"] = True

        # --- Device-specific enrichment ---
        if key == "PUMP":
            self._enrich_pump_attributes(attributes)
        elif key == "HEATER":
            self._enrich_heater_attributes(attributes)
        elif key == "SOLAR":
            self._enrich_solar_attributes(attributes)
        elif key.startswith("DOS_"):
            self._enrich_dosing_attributes(attributes, key)
        elif key == "BACKWASH":
            self._enrich_backwash_attributes(attributes)

        # --- Runtime (for any switch that has it) ---
        runtime_key = f"{key}_RUNTIME"
        runtime_val = self.get_value(runtime_key)
        if runtime_val is not None:
            attributes["runtime"] = str(runtime_val)

        return attributes

    # -----------------------------------------------------------------
    # State description helpers
    # -----------------------------------------------------------------

    # Numeric state descriptions
    _STATE_DESC: dict[int, str] = {
        0: "Automatic – Standby",
        1: "Manual On",
        2: "Automatic – Active",
        3: "Automatic – Active (Timer)",
        4: "Manual On (Forced)",
        5: "Automatic – Waiting",
        6: "Manual Off",
    }

    # Common *STATE detail suffixes
    _DETAIL: dict[str, str] = {
        "PUMP_ANTI_FREEZE": "Anti-Freeze",
        "BLOCKED_BY_OUTSIDE_TEMP": "Blocked (Outside Temp)",
        "BLOCKED_BY_TRESHOLDS": "Blocked (Limits)",
        "TRESHOLDS_REACHED": "Limits Reached",
        "BLOCKED_BY_PUMP": "Blocked (Pump Off)",
        "BLOCKED_BY_FLOW": "Blocked (Flow)",
        "BLOCKED_BY_SOLAR": "Blocked (Solar)",
        "BLOCKED_BY_HEATER": "Blocked (Heater)",
        "WAITING_FOR_PUMP": "Waiting for Pump",
        "WAITING_FOR_FLOW": "Waiting for Flow",
        "DOSING": "Dosing",
        "DOSING_PAUSED": "Dosing Paused",
        "MANUAL_DOSING": "Manual Dosing",
    }

    def _get_mode_and_description(
        self, key: str, raw_state: Any
    ) -> tuple[str, str]:
        """
        Derive human-readable mode and description from the raw state.

        Uses the detailed *STATE key (e.g., PUMPSTATE, HEATERSTATE) if
        available, otherwise falls back to the numeric state mapping.

        Returns:
            Tuple of (mode_string, description_string).
        """
        # Try the detailed STATE key first (e.g., PUMPSTATE = "3|PUMP_ANTI_FREEZE")
        detail_state_key = f"{key}STATE"
        detail_val = self.get_value(detail_state_key)

        state_num = None
        extra_detail = ""

        if detail_val is not None and str(detail_val).strip() not in ("", "[]"):
            detail_str = str(detail_val).strip()
            if "|" in detail_str:
                parts = detail_str.split("|", 1)
                try:
                    state_num = int(parts[0])
                except (ValueError, TypeError):
                    pass
                if len(parts) > 1:
                    raw_detail = parts[1].strip()
                    extra_detail = self._DETAIL.get(
                        raw_detail, raw_detail.replace("_", " ").title()
                    )
            else:
                try:
                    state_num = int(detail_str)
                except (ValueError, TypeError):
                    raw_detail = detail_str.strip()
                    extra_detail = self._DETAIL.get(
                        raw_detail, raw_detail.replace("_", " ").title()
                    )

        # Fall back to the raw numeric state
        if state_num is None and raw_state is not None:
            try:
                state_num = int(raw_state)
            except (ValueError, TypeError):
                pass

        # Map numeric state to mode + description
        mode = "Unknown"
        desc = "Unknown"

        if state_num is not None:
            # Mode from numeric state
            mode_map = {
                0: "Automatic",
                1: "Manual",
                2: "Automatic",
                3: "Automatic",
                4: "Manual",
                5: "Automatic",
                6: "Manual",
            }
            mode = mode_map.get(state_num, "Unknown")
            desc = self._STATE_DESC.get(state_num, f"State {state_num}")

        # Append extra detail from *STATE field
        if extra_detail:
            desc = f"{desc} ({extra_detail})" if desc else extra_detail

        return mode, desc

    def _enrich_pump_attributes(self, attributes: dict[str, Any]) -> None:
        """Add pump-specific attributes: speed, RPM level, last on/off."""
        # Determine active RPM level
        active_speed = None
        for level in range(4):
            rpm_key = f"PUMP_RPM_{level}"
            rpm_val = self.get_value(rpm_key)
            if rpm_val is not None:
                try:
                    if int(rpm_val) > 0:
                        active_speed = level
                except (ValueError, TypeError):
                    pass

        if active_speed is not None:
            attributes["pump_speed_level"] = active_speed
            attributes["status_description"] += f" | Level {active_speed}"

    def _enrich_heater_attributes(self, attributes: dict[str, Any]) -> None:
        """Add heater-specific attributes: target temp, postrun."""
        target = self.get_value("HEATER_TARGET_TEMP")
        if target is not None:
            attributes["target_temperature"] = target
        postrun = self.get_value("HEATER_POSTRUN_TIME")
        if postrun is not None and str(postrun).upper() != "NONE":
            attributes["postrun_time"] = str(postrun)

    def _enrich_solar_attributes(self, attributes: dict[str, Any]) -> None:
        """Add solar-specific attributes: target temp."""
        target = self.get_value("SOLAR_TARGET_TEMP")
        if target is not None:
            attributes["target_temperature"] = target

    def _enrich_dosing_attributes(
        self, attributes: dict[str, Any], key: str
    ) -> None:
        """Add dosing-specific attributes: state details, remaining range, daily amount."""
        # Dosing state (e.g., DOS_1_CL_STATE = ['BLOCKED_BY_TRESHOLDS', ...])
        state_key = f"{key}_STATE"
        state_val = self.get_value(state_key)
        if state_val is not None:
            if isinstance(state_val, list):
                if state_val:
                    # Translate state entries
                    readable = [
                        self._DETAIL.get(s, s.replace("_", " ").title())
                        for s in state_val
                    ]
                    attributes["dosing_status"] = ", ".join(readable)
            elif str(state_val).strip() not in ("", "[]"):
                raw_s = str(state_val).strip()
                attributes["dosing_status"] = self._DETAIL.get(
                    raw_s, raw_s.replace("_", " ").title()
                )

        # Remaining range (e.g., ">99d")
        range_key = f"{key}_REMAINING_RANGE"
        range_val = self.get_value(range_key)
        if range_val is not None:
            attributes["remaining_range"] = str(range_val)

        # Daily amount
        daily_key = f"{key}_DAILY_AMOUNT"
        daily_val = self.get_value(daily_key)
        if daily_val is not None:
            attributes["daily_amount_ml"] = daily_val

        # Total canister volume
        can_key = f"{key}_TOTAL_CAN_AMOUNT_ML"
        can_val = self.get_value(can_key)
        if can_val is not None:
            attributes["canister_volume_ml"] = can_val

    def _enrich_backwash_attributes(self, attributes: dict[str, Any]) -> None:
        """Add backwash-specific attributes: schedule info, step."""
        bw_state = self.get_value("BACKWASH_STATE")
        if bw_state is not None and str(bw_state).strip():
            attributes["backwash_info"] = str(bw_state)
        bw_step = self.get_value("BACKWASH_STEP")
        if bw_step is not None:
            attributes["backwash_step"] = bw_step

    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Turn the switch on.

        Args:
            **kwargs: Additional arguments.
        """
        await self._set_switch_state(ACTION_ON, **kwargs)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """
        Turn the switch off.

        Args:
            **kwargs: Additional arguments.
        """
        await self._set_switch_state(ACTION_OFF, **kwargs)

    async def _set_switch_state(self, action: str, **kwargs: Any) -> None:
        """
        Set the switch state.

        Args:
            action: The action to perform (e.g., ACTION_ON, ACTION_OFF).
            **kwargs: Additional arguments.

        Raises:
            HomeAssistantError: If the action fails.
        """
        key = self.entity_description.key

        try:
            # ✅ User action = always log (INFO)
            _LOGGER.info("Set switch %s to %s", key, action)

            # For PUMP: Support extended parameters
            if key == "PUMP" and action == ACTION_ON:
                speed = self._validate_speed(kwargs.get("speed", 2))
                duration = self._validate_duration(kwargs.get("duration", 0))

                result = await self.device.api.set_switch_state(
                    key=key, action=action, duration=duration, last_value=speed
                )
            elif key == "PVSURPLUS" and action == ACTION_ON:
                rpm = self._validate_pv_rpm(kwargs.get("rpm"))

                result = await self.device.api.set_switch_state(
                    key=key,
                    action=action,
                    last_value=rpm,
                )
            else:
                result = await self.device.api.set_switch_state(key=key, action=action)

            if result.get("success") is True:
                # ✅ Log success only at debug (API already logs)
                _LOGGER.debug("Switch %s successfully set to %s", key, action)

                # ✅ FIXED: ONLY set local variable, NO coordinator.data mutation!
                self._optimistic_state = action == ACTION_ON
                self.async_write_ha_state()

                _LOGGER.debug(
                    "Optimistic update: %s = %s (local cache, no coordinator.data mutation)",
                    key,
                    "ON" if self._optimistic_state else "OFF",
                )

                # Asynchronous refresh fetches real data and resets cache
                task = asyncio.create_task(self._delayed_refresh(key))
                task.add_done_callback(lambda t: self._handle_refresh_error(t, key))
            else:
                error_msg = result.get("response", "Unknown error")
                # ✅ Error = WARNING (User-relevant)
                _LOGGER.warning(
                    "Switch %s action %s failed: %s", key, action, error_msg
                )
                task = asyncio.create_task(self._delayed_refresh(key))
                task.add_done_callback(lambda t: self._handle_refresh_error(t, key))

        except VioletPoolAPIError as err:
            # ✅ API Error = ERROR (critical)
            _LOGGER.error(
                "API error setting switch %s to %s: %s", key, action, err
            )
            # Clear cache on error
            self._optimistic_state = None
            raise HomeAssistantError(f"Switch action failed: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error setting switch %s: %s", key, err)
            # Clear cache on error
            self._optimistic_state = None
            raise HomeAssistantError(f"Switch error: {err}") from err

    async def _delayed_refresh(self, key: str) -> None:
        """
        Perform a delayed refresh with optimistic cache reset.

        Args:
            key: The switch key.
        """
        # ✅ SHARED CODE: Use base refresh method
        try:
            success = await self._request_coordinator_refresh(
                delay=REFRESH_DELAY, log_context=key
            )

            if success and self.coordinator.data is not None:
                new_state = self.coordinator.data.get(key, "UNKNOWN")
                _LOGGER.debug("State after refresh: %s = %s", key, new_state)
        finally:
            # Always clear optimistic cache — even on CancelledError during HA reload
            old_optimistic = self._optimistic_state
            self._optimistic_state = None
            if old_optimistic is not None:
                _LOGGER.debug(
                    "Optimistic cache cleared for %s (was: %s)",
                    key,
                    "ON" if old_optimistic else "OFF",
                )

    def _handle_refresh_error(self, task: asyncio.Task, key: str) -> None:
        """
        Handle errors in the refresh task.

        Args:
            task: The task object.
            key: The switch key.
        """
        try:
            if not task.cancelled():
                exc = task.exception()
                if exc is not None:
                    # ✅ Log only actual problems
                    _LOGGER.debug("Refresh task failed for %s: %s", key, exc)
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            pass  # Normal, no log needed
        except Exception as err:
            _LOGGER.debug("Error handling refresh task for %s: %s", key, err)

    def _validate_speed(self, speed: Any) -> int:
        """
        Validate the speed parameter.

        Args:
            speed: The speed value.

        Returns:
            The validated speed integer.
        """
        try:
            speed_int = int(speed)
            # Controller supports speeds 0-3 (PUMP_RPM_0 to PUMP_RPM_3)
            if 0 <= speed_int <= 3:
                return speed_int
            _LOGGER.warning(
                "Invalid speed value %s (allowed: 0-3), using default 2", speed
            )
            return 2
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid speed type %s, using default 2", type(speed))
            return 2

    def _validate_duration(self, duration: Any) -> int:
        """
        Validate the duration parameter.

        Args:
            duration: The duration value.

        Returns:
            The validated duration integer.
        """
        try:
            duration_int = int(duration)
            if duration_int >= 0:
                return duration_int
            _LOGGER.warning("Negative duration %s, using 0", duration)
            return 0
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid duration type %s, using 0", type(duration))
            return 0

    def _validate_pv_rpm(self, rpm: Any | None) -> int:
        """
        Validate the PV surplus RPM parameter.

        Args:
            rpm: The RPM value.

        Returns:
            The validated RPM integer.
        """
        if rpm is None:
            return 2
        try:
            rpm_int = int(rpm)
        except (TypeError, ValueError):
            _LOGGER.debug("Invalid PV Surplus RPM %s, using default 2", rpm)
            return 2

        if 1 <= rpm_int <= 3:
            return rpm_int

        _LOGGER.debug(
            "PV Surplus RPM %s out of valid range, using default 2", rpm
        )
        return 2

    async def async_added_to_hass(self) -> None:
        """Called when the entity is added to Home Assistant."""
        await super().async_added_to_hass()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up switches for the config entry.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry.
        async_add_entities: Callback to add entities.
    """
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities: list[SwitchEntity] = []

    # ✅ Setup = INFO (important for user)
    _LOGGER.info("Switch Setup - Active features: %s", active_features)

    # Diagnostics only if data available
    if coordinator.data is not None:
        # ✅ Diagnostics = DEBUG (only for developers)
        _LOGGER.debug("Coordinator data keys: %d", len(coordinator.data.keys()))

        # State diagnostics only for important switches
        for key in ["PUMP", "SOLAR", "HEATER"]:
            if key in coordinator.data:
                try:
                    value = coordinator.data[key]
                    state_int = (
                        int(value)
                        if isinstance(value, (int, float)) or str(value).isdigit()
                        else None
                    )
                    expected = (
                        "ON"
                        if state_int in ON_STATES
                        else "OFF"
                        if state_int in OFF_STATES
                        else "UNKNOWN"
                    )
                    _LOGGER.debug("%s: raw=%s → %s", key, value, expected)
                except (ValueError, KeyError, TypeError) as err:
                    _LOGGER.debug("Diagnostic error for %s: %s", key, err)
    else:
        _LOGGER.warning("Coordinator data is None during Switch Setup")

    # Create switches
    for switch_config in SWITCHES:
        # Map entity_category string to EntityCategory enum
        entity_category = None
        if "entity_category" in switch_config:
            category_str = switch_config["entity_category"]
            if category_str == "diagnostic":
                entity_category = EntityCategory.DIAGNOSTIC
            elif category_str == "config":
                entity_category = EntityCategory.CONFIG

        description = SwitchEntityDescription(
            key=switch_config["key"],
            name=switch_config["name"],
            # translation_key=switch_config["key"].lower(), # I will enable this later if I update strings.json for all switches
            icon=switch_config.get("icon"),
            entity_category=entity_category,
        )

        feature_id = switch_config.get("feature_id")

        if feature_id and feature_id not in active_features:
            # ✅ DEBUG: Unimportant info
            _LOGGER.debug(
                "Skipping Switch %s: Feature %s not active",
                description.key,
                feature_id,
            )
            continue

        entities.append(VioletSwitch(coordinator, config_entry, description))

    if entities:
        async_add_entities(entities)
        # ✅ INFO: Successful setup
        _LOGGER.info("✓ %d Switches successfully set up", len(entities))

        # Final check only on DEBUG
        if coordinator.data is not None:
            for entity in entities:
                key = entity.entity_description.key
                if key in ["PUMP", "SOLAR", "HEATER"] and key in coordinator.data:
                    try:
                        raw_state = coordinator.data[key]
                        # Type cast to access specific method
                        should_be_on = entity._get_switch_state()  # type: ignore[attr-defined]
                        _LOGGER.debug(
                            "Final check %s: raw=%s → display=%s",
                            key,
                            raw_state,
                            "ON" if should_be_on else "OFF",
                        )
                    except (ValueError, KeyError, TypeError, AttributeError) as err:
                        _LOGGER.debug("Final check error for %s: %s", key, err)
    else:
        # ✅ WARNING: Potential problem
        _LOGGER.warning("⚠ No switches set up")
