
"""Climate platform for Violet Pool Controller."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import VioletPoolAPIError
from .const import ACTION_AUTO, ACTION_OFF, ACTION_ON, CONF_ACTIVE_FEATURES, DOMAIN
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platforms; HA should not throttle entity state writes
PARALLEL_UPDATES = 0

# State Constants
STATE_OFF = 0
STATE_AUTO_HEATING = 1
STATE_AUTO_IDLE = 2
STATE_AUTO_ACTIVE = 3
STATE_MANUAL_ON = 4
STATE_AUTO_OFF = 5
STATE_MANUAL_OFF = 6

# Temperature limits
DEFAULT_MIN_TEMP = 20.0
DEFAULT_MAX_TEMP = 35.0
DEFAULT_TARGET_TEMP = 28.0
TEMP_STEP = 0.5

REFRESH_DELAY = 0.3

# HVAC Mode Mapping
HEATER_HVAC_MODES = {
    STATE_OFF: HVACMode.AUTO,
    STATE_AUTO_HEATING: HVACMode.AUTO,
    STATE_AUTO_IDLE: HVACMode.AUTO,
    STATE_AUTO_ACTIVE: HVACMode.AUTO,
    STATE_MANUAL_ON: HVACMode.HEAT,
    STATE_AUTO_OFF: HVACMode.AUTO,
    STATE_MANUAL_OFF: HVACMode.OFF,
}

HEATER_HVAC_ACTIONS = {
    STATE_OFF: HVACAction.IDLE,
    STATE_AUTO_HEATING: HVACAction.HEATING,
    STATE_AUTO_IDLE: HVACAction.IDLE,
    STATE_AUTO_ACTIVE: HVACAction.HEATING,
    STATE_MANUAL_ON: HVACAction.HEATING,
    STATE_AUTO_OFF: HVACAction.IDLE,
    STATE_MANUAL_OFF: HVACAction.OFF,
}

CLIMATE_FEATURE_MAP = {
    "HEATER": "heating",
    "SOLAR": "solar",
}

WATER_TEMP_SENSORS = [
    "onewire1_value",
    "water_temp",
    "WATER_TEMPERATURE",
    "temp_value",
]


class VioletClimateEntity(VioletPoolControllerEntity, ClimateEntity):
    """Climate Entity - FULLY PROTECTED & THREAD-SAFE VERSION."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_min_temp = DEFAULT_MIN_TEMP
    _attr_max_temp = DEFAULT_MAX_TEMP
    _attr_target_temperature_step = TEMP_STEP

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        climate_type: str,
    ) -> None:
        """Initialize the climate entity."""
        name = "Heater" if climate_type == "HEATER" else "Solar Absorber"
        icon = "mdi:radiator" if climate_type == "HEATER" else "mdi:solar-power"

        climate_description = ClimateEntityDescription(
            key=climate_type,
            name=name,
            icon=icon,
        )

        super().__init__(coordinator, config_entry, climate_description)
        self.climate_type = climate_type

        # ✅ FIXED: Lokale Cache-Variablen für optimistisches Update
        self._optimistic_target_temp: float | None = None
        self._optimistic_hvac_mode: str | None = None

        self._attr_target_temperature = self._get_target_temperature()
        self._attr_hvac_mode = self._get_hvac_mode()

        _LOGGER.debug(
            "%s initialized: target=%.1f°C, mode=%s",
            name,
            self._attr_target_temperature,
            self._attr_hvac_mode,
        )

    def _get_target_temperature(self) -> float:
        """Return the target temperature."""
        # Check optimistic cache first
        if self._optimistic_target_temp is not None:
            return self._optimistic_target_temp

        # None-check before data access
        if self.coordinator.data is None:
            _LOGGER.debug(
                "Coordinator data is None - returning default target %.1f°C",
                DEFAULT_TARGET_TEMP,
            )
            return DEFAULT_TARGET_TEMP

        key = f"{self.climate_type}_TARGET_TEMP"
        target = self.get_float_value(key, DEFAULT_TARGET_TEMP)
        if target is None:
            return DEFAULT_TARGET_TEMP

        # Validate temperature range
        if not self.min_temp <= target <= self.max_temp:
            _LOGGER.warning(
                "Target temperature %.1f°C out of range (%.1f-%.1f°C), using %.1f°C",
                target,
                self.min_temp,
                self.max_temp,
                DEFAULT_TARGET_TEMP,
            )
            return DEFAULT_TARGET_TEMP

        return target

    def _get_hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        # Check optimistic cache first
        if self._optimistic_hvac_mode is not None:
            # We assume optimistic_hvac_mode is always a valid HVACMode
            return HVACMode(self._optimistic_hvac_mode)

        if self.coordinator.data is None:
            _LOGGER.debug("Coordinator data is None - returning OFF mode")
            return HVACMode.OFF

        state = self.get_int_value(self.climate_type, STATE_OFF) or STATE_OFF
        mode = HEATER_HVAC_MODES.get(state, HVACMode.OFF)

        _LOGGER.debug("%s State %d → HVAC Mode %s", self.climate_type, state, mode)
        return mode

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        return self._get_hvac_mode()

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action."""
        if self.coordinator.data is None:
            _LOGGER.debug("Coordinator data is None - returning IDLE action")
            return HVACAction.IDLE

        state = self.get_int_value(self.climate_type, STATE_OFF) or STATE_OFF
        action = HEATER_HVAC_ACTIONS.get(state, HVACAction.IDLE)

        _LOGGER.debug("%s State %d → HVAC Action %s", self.climate_type, state, action)
        return action

    @property
    def current_temperature(self) -> float | None:
        """Return the current water temperature."""
        if self.coordinator.data is None:
            _LOGGER.debug("Coordinator data is None - no current temperature available")
            return None

        for sensor_key in WATER_TEMP_SENSORS:
            value = self.get_float_value(sensor_key, None)
            if value is not None:
                _LOGGER.debug("Water temperature from '%s': %.1f°C", sensor_key, value)
                return value

        _LOGGER.debug("No water temperature found in: %s", WATER_TEMP_SENSORS)
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        return self._get_target_temperature()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {
                "state_type": "unavailable",
                "note": "Coordinator data not available",
            }

        state = self.get_int_value(self.climate_type, STATE_OFF)

        attributes = {
            "raw_state": state,
            "hvac_mode_from_state": HEATER_HVAC_MODES.get(state or STATE_OFF, "unknown"),
            "hvac_action_from_state": HEATER_HVAC_ACTIONS.get(state or STATE_OFF, "unknown"),
        }

        # Show optimistic cache status
        if self._optimistic_target_temp is not None:
            attributes["optimistic_target"] = self._optimistic_target_temp
            attributes["pending_update"] = True

        # Runtime information mit None-Check
        runtime_key = f"{self.climate_type}_RUNTIME"
        if runtime_key in self.coordinator.data:
            attributes["runtime"] = self.get_str_value(runtime_key, "00h 00m 00s")

        return attributes

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        temperature = kwargs.get("temperature")
        if temperature is None:
            _LOGGER.warning("No temperature provided in kwargs")
            return

        if not self._validate_temperature(temperature):
            return

        try:
            _LOGGER.info(
                "Setting %s temperature to %.1f°C",
                self.climate_type,
                temperature,
            )

            result = await self.device.api.set_device_temperature(
                self.climate_type, temperature
            )

            if result.get("success") is True:
                _LOGGER.debug("Temperature set successfully: %s", result)

                self._optimistic_target_temp = temperature
                self._attr_target_temperature = temperature
                self.async_write_ha_state()

                _LOGGER.debug(
                    "Optimistic update: %.1f°C (local cache, coordinator.data not mutated)",
                    temperature,
                )

                task = asyncio.create_task(self._delayed_refresh())
                task.add_done_callback(self._handle_refresh_error)
            else:
                error_msg = result.get("response", "Unknown error")
                _LOGGER.warning("Failed to set temperature: %s", error_msg)
                raise HomeAssistantError(
                    translation_key="failed_to_set_value",
                    translation_domain=DOMAIN,
                    translation_placeholders={"detail": str(error_msg)},
                )

        except VioletPoolAPIError as err:
            _LOGGER.error("API error setting temperature: %s", err)
            raise HomeAssistantError(
                translation_key="api_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise HomeAssistantError(
                translation_key="unexpected_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        mode_action_map = {
            HVACMode.HEAT: ACTION_ON,
            HVACMode.OFF: ACTION_OFF,
            HVACMode.AUTO: ACTION_AUTO,
        }

        api_action = mode_action_map.get(hvac_mode)
        if not api_action:
            _LOGGER.warning("Unsupported HVAC mode: %s", hvac_mode)
            return

        try:
            _LOGGER.info(
                "Setting %s mode to %s (API action: %s)",
                self.climate_type,
                hvac_mode,
                api_action,
            )

            result = await self.device.api.set_switch_state(
                self.climate_type, api_action
            )

            if result.get("success") is True:
                _LOGGER.debug("HVAC mode set successfully: %s", result)

                self._optimistic_hvac_mode = hvac_mode
                self._attr_hvac_mode = hvac_mode
                self.async_write_ha_state()

                _LOGGER.debug(
                    "Optimistic update: %s (local cache, coordinator.data not mutated)",
                    hvac_mode,
                )

                task = asyncio.create_task(self._delayed_refresh())
                task.add_done_callback(self._handle_refresh_error)
            else:
                error_msg = result.get("response", "Unknown error")
                _LOGGER.warning("Failed to set HVAC mode: %s", error_msg)
                raise HomeAssistantError(
                    translation_key="failed_to_set_value",
                    translation_domain=DOMAIN,
                    translation_placeholders={"detail": str(error_msg)},
                )

        except VioletPoolAPIError as err:
            _LOGGER.error("API error setting HVAC mode: %s", err)
            raise HomeAssistantError(
                translation_key="api_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise HomeAssistantError(
                translation_key="unexpected_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err

    def _validate_temperature(self, temperature: float) -> bool:
        """Validate temperature is within the allowed range."""
        if not self.min_temp <= temperature <= self.max_temp:
            _LOGGER.warning(
                "Temperature %.1f°C outside allowed range (%.1f-%.1f°C)",
                temperature,
                self.min_temp,
                self.max_temp,
            )
            return False
        return True

    def _get_expected_state(self, action: str) -> int:
        """Return the expected state for a given action."""
        action_state_map = {
            ACTION_ON: STATE_MANUAL_ON,
            ACTION_OFF: STATE_MANUAL_OFF,
            ACTION_AUTO: STATE_AUTO_IDLE,
        }
        return action_state_map.get(action, STATE_OFF)

    async def _delayed_refresh(self) -> None:
        """Perform a delayed coordinator refresh and clear optimistic cache."""
        try:
            await self._request_coordinator_refresh(
                delay=REFRESH_DELAY, log_context=self.climate_type
            )
            if self.coordinator.data is not None:
                _LOGGER.debug(
                    "State after refresh: %s=%s, target=%s",
                    self.climate_type,
                    self.coordinator.data.get(self.climate_type, "UNKNOWN"),
                    self.coordinator.data.get(
                        f"{self.climate_type}_TARGET_TEMP", "UNKNOWN"
                    ),
                )
        finally:
            # Always clear optimistic caches — even on CancelledError during HA reload
            old_temp = self._optimistic_target_temp
            old_mode = self._optimistic_hvac_mode
            self._optimistic_target_temp = None
            self._optimistic_hvac_mode = None
            if old_temp is not None or old_mode is not None:
                _LOGGER.debug(
                    "Optimistic cache cleared (temp: %s, mode: %s)",
                    old_temp,
                    old_mode,
                )

    def _handle_refresh_error(self, task: asyncio.Task) -> None:
        """
        Handle errors in the refresh task.

        Args:
            task: The task object.
        """
        try:
            if not task.cancelled():
                exc = task.exception()
                if exc is not None:
                    _LOGGER.debug(
                        "Refresh task failed for %s: %s", self.climate_type, exc
                    )
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            pass  # Normal during HA reload, no log needed


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate entities from a config entry."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities = []

    _LOGGER.info("Climate Setup - Active features: %s", active_features)

    if coordinator.data is not None:
        _LOGGER.debug("Coordinator data keys: %d", len(coordinator.data.keys()))
    else:
        _LOGGER.warning("Coordinator data is None during climate setup")

    for climate_type, feature in CLIMATE_FEATURE_MAP.items():
        if feature not in active_features:
            _LOGGER.debug(
                "%s entity not created: feature '%s' not active",
                climate_type,
                feature,
            )
            continue

        if coordinator.data is not None:
            if climate_type not in coordinator.data:
                _LOGGER.debug(
                    "%s entity not created: no data available",
                    climate_type,
                )
                continue
        else:
            _LOGGER.debug(
                "%s entity created despite missing data (coordinator offline?)",
                climate_type,
            )

        _LOGGER.debug("Creating %s entity: feature '%s' active", climate_type, feature)
        entities.append(VioletClimateEntity(coordinator, config_entry, climate_type))

    if entities:
        async_add_entities(entities)
        _LOGGER.info(
            "%d climate entities added: %s",
            len(entities),
            [e.name for e in entities],
        )
    else:
        _LOGGER.debug(
            "No climate entities set up (no features active or no data available)"
        )
