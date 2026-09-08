# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Select platform for Violet Pool Controller."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from violet_poolcontroller_api.api import VioletPoolAPIError

from .const import (
    ACTION_AUTO,
    ACTION_OFF,
    ACTION_ON,
    CONF_ACTIVE_FEATURES,
    DOMAIN,
    SELECT_CONTROLS,
)
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity, parse_state_code
from .entity_cleanup import track_provided_entities
from .entity_selection import async_get_selection
from .state_constants import ON_STATES

_LOGGER = logging.getLogger(__name__)

BINARY_DOSING_CONFIG_KEYS = {
    "DOS_6_FLOC": "DOSAGE_floc_use",
}

DOSING_CONFIG_KEYS = {
    "DOS_1_CL": {"prefix": "DOSAGE_chlorine", "type": "Chlor"},
    "DOS_2_ELO": {"prefix": "DOSAGE_electrolysis", "type": "Elektrolyse"},
    "DOS_4_PHM": {"prefix": "DOSAGE_phminus", "type": "pH-"},
    "DOS_5_PHP": {"prefix": "DOSAGE_phplus", "type": "pH+"},
}

# Coordinator-based platforms; HA should not throttle entity state writes
PARALLEL_UPDATES = 0

# Mode Constants
MODE_OFF = "off"
MODE_ON = "on"
MODE_AUTO = "auto"

# State to Mode Mapping (matches DEVICE_STATE_MAPPING from API library)
# 0 = Auto - Standby (OFF)
# 1 = Auto - Active (Scheduled) (ON)
# 2 = Auto - Priority OFF / Rule Blocked (OFF)
# 3 = Auto - Priority ON / Emergency Rule (ON)
# 4 = Manual ON (Forced)
# 5 = Auto - Rule OFF / Emergency Rule (OFF)
# 6 = Manual OFF
STATE_TO_MODE = {
    0: MODE_AUTO,
    1: MODE_AUTO,
    2: MODE_AUTO,
    3: MODE_AUTO,
    4: MODE_ON,
    5: MODE_AUTO,
    6: MODE_OFF,
}

# Mode to Action Mapping
MODE_TO_ACTION = {
    MODE_OFF: ACTION_OFF,
    MODE_ON: ACTION_ON,
    MODE_AUTO: ACTION_AUTO,
}

REFRESH_DELAY = 0.5
REFRESH_DELAY_EXT = 1.5


class VioletSelect(VioletPoolControllerEntity, SelectEntity):
    """Select entity for ON/OFF/AUTO control of pool devices."""

    entity_description: SelectEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SelectEntityDescription,
        device_key: str,
        is_binary: bool = False,
        is_read_only: bool = False,
    ) -> None:
        """
        Initialize the select entity.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            description: The entity description.
            device_key: The device key (e.g., PUMP, HEATER).
            is_binary: If True, only OFF/ON options (no AUTO).
            is_read_only: If True, entity reports state but cannot be changed.
        """
        super().__init__(coordinator, config_entry, description)
        self._device_key = device_key
        self._is_binary = is_binary
        self._is_read_only = is_read_only
        if device_key in DOSING_CONFIG_KEYS:
            # A dosing channel is either enabled (the controller doses on its
            # own rules) or disabled. There is no "on" command: picking it sent
            # the very same enable request as "auto", and the read path could
            # never report "on", so the option snapped back on the next poll.
            self._attr_options = [MODE_OFF, MODE_AUTO]
        elif self._is_binary:
            self._attr_options = [MODE_OFF, MODE_ON]
        else:
            self._attr_options = [MODE_OFF, MODE_ON, MODE_AUTO]

        # Optimistic state cache
        self._optimistic_mode: str | None = None

        _LOGGER.debug(
            "Select entity initialized: %s (Device: %s)",
            getattr(self, "entity_id", description.key),
            device_key,
        )

    @property
    def current_option(self) -> str | None:
        """Return the current selected option.

        The result is always one of ``options``: Home Assistant rejects a state
        the entity does not offer, and a dosing channel whose output is
        manually forced on still maps onto "auto" - the channel is enabled.
        """
        option = self._resolve_option()
        if option is None or option in self._attr_options:
            return option
        if option == MODE_ON:
            return MODE_AUTO if MODE_AUTO in self._attr_options else MODE_OFF
        return MODE_OFF

    def _resolve_option(self) -> str | None:
        """Return the mode the controller reports, before clamping to options."""
        if self.coordinator.data is None:
            self._optimistic_mode = None
            return None

        if self._optimistic_mode is not None:
            return self._optimistic_mode

        # A select that writes a config flag must read that same flag back.
        # Reading the output state instead reported "off" for an enabled but
        # currently idle channel, e.g. flocculant between two doses.
        config_key = self._config_read_key()
        if config_key is not None:
            use_code = parse_state_code(self.get_value(config_key))
            if use_code is not None:
                if use_code != 1:
                    return MODE_OFF
                return MODE_ON if self._is_binary else MODE_AUTO

        raw_state = self.get_value(self._device_key, "")

        # Composite states such as "3|PUMP_ANTI_FREEZE" carry the state code in
        # their leading part.
        state_int = parse_state_code(raw_state)
        if state_int is None:
            state_str = str(raw_state).upper().strip()
            if state_str in ("ON", "MANUAL", "MAN"):
                return MODE_ON
            if state_str in ("OFF", "STOPPED"):
                return MODE_OFF
            if state_str in ("AUTO", "AUTOMATIC"):
                return MODE_ON if self._is_binary else MODE_AUTO
            return MODE_OFF if self._is_binary else MODE_AUTO

        # PVSURPLUS uses its own scheme: 0 = off, 1/2 = on (not the
        # 0-6 output states)
        if self._device_key == "PVSURPLUS":
            return MODE_ON if state_int in (1, 2) else MODE_OFF

        if self._is_binary:
            # Active states per DEVICE_STATE_MAPPING; 2 = rule-blocked OFF
            return MODE_ON if state_int in ON_STATES else MODE_OFF

        return STATE_TO_MODE.get(state_int, MODE_AUTO)

    def _config_read_key(self) -> str | None:
        """Return the config key this select reads and writes, if it has one."""
        if self._device_key in BINARY_DOSING_CONFIG_KEYS:
            return BINARY_DOSING_CONFIG_KEYS[self._device_key]
        if self._device_key in DOSING_CONFIG_KEYS:
            return f"{DOSING_CONFIG_KEYS[self._device_key]['prefix']}_use"
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}

        raw_state = self.get_value(self._device_key, "")

        attributes: dict[str, Any] = {
            "raw_state": str(raw_state) if raw_state is not None else "None",
            "device_key": self._device_key,
        }

        # Optimistic state indicator
        if self._optimistic_mode is not None:
            attributes["pending_update"] = True
            attributes["target_mode"] = self._optimistic_mode

        # Device-specific attributes. The keys read here are the ones the
        # controller actually reports - HEATER_TARGET_TEMP / SOLAR_TARGET_TEMP
        # never existed, so those attributes only ever showed their fallback.
        if self._device_key == "PUMP":
            attributes.update(
                {
                    "runtime": self.get_str_value("PUMP_RUNTIME"),
                    "speed": self.get_active_pump_speed(),
                }
            )
        elif self._device_key == "HEATER":
            attributes.update(
                {
                    "runtime": self.get_str_value("HEATER_RUNTIME"),
                    "target_temp": self.get_float_value("HEATER_set_temp"),
                }
            )
        elif self._device_key == "SOLAR":
            attributes.update(
                {
                    "runtime": self.get_str_value("SOLAR_RUNTIME"),
                    "target_temp": self.get_float_value("SOLAR_maxtemp"),
                }
            )

        return attributes

    async def async_select_option(self, option: str) -> None:
        """
        Change the selected option.

        Args:
            option: The new option (off, on, auto).

        Raises:
            HomeAssistantError: If the action fails.
        """
        if self._is_read_only:
            raise HomeAssistantError(
                translation_key="read_only_entity",
                translation_domain=DOMAIN,
                translation_placeholders={"entity": str(self._device_key)},
            )

        if option not in self._attr_options:
            raise HomeAssistantError(
                translation_key="invalid_action",
                translation_domain=DOMAIN,
                translation_placeholders={"action": option},
            )

        action = MODE_TO_ACTION[option]

        try:
            _LOGGER.info("Setting %s to mode '%s' (action: %s)", self._device_key, option, action)

            writes_config = self._config_read_key() is not None

            if self._is_binary and self._device_key in BINARY_DOSING_CONFIG_KEYS:
                config_key = BINARY_DOSING_CONFIG_KEYS[self._device_key]
                config_val = "1" if option == MODE_ON else "0"
                result = await self.device.api.set_config({config_key: config_val})
            elif self._device_key in DOSING_CONFIG_KEYS:
                dosing_type = DOSING_CONFIG_KEYS[self._device_key]["type"]
                result = await self.device.api.set_dosage_enabled(
                    dosing_type, enabled=option == MODE_AUTO
                )
            else:
                result = await self.device.api.set_switch_state(key=self._device_key, action=action)

            if result.get("success") is True:
                _LOGGER.debug("%s successfully set to mode '%s'", self._device_key, option)

                # Config values live behind a second request that is only
                # re-read every CONFIG_REFRESH_INTERVAL seconds. Without this,
                # the delayed refresh returns the stale cached flag and the
                # selection visibly jumps back for up to a minute.
                if writes_config:
                    self.coordinator.device.request_config_refresh()

                # Optimistic update
                self._optimistic_mode = option
                self.async_write_ha_state()

                # Delayed refresh
                task = asyncio.create_task(self._delayed_refresh())
                task.add_done_callback(self._handle_refresh_error)
            else:
                error_msg = result.get("response", "Unknown error")
                _LOGGER.warning(
                    "%s mode switch to '%s' failed: %s",
                    self._device_key,
                    option,
                    error_msg,
                )
                raise HomeAssistantError(
                    translation_key="failed_to_set_value",
                    translation_domain=DOMAIN,
                    translation_placeholders={"detail": str(error_msg)},
                )

        except VioletPoolAPIError as err:
            _LOGGER.error(
                "API error setting %s to mode '%s': %s",
                self._device_key,
                option,
                err,
            )
            self._optimistic_mode = None
            raise HomeAssistantError(
                translation_key="failed_to_set_value",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err
        except HomeAssistantError:
            # Already a translated, user-facing message - keep it as it is
            # instead of re-wrapping it as an "unexpected error".
            self._optimistic_mode = None
            raise
        except Exception as err:
            _LOGGER.error(
                "Unexpected error setting %s to mode '%s': %s",
                self._device_key,
                option,
                err,
            )
            self._optimistic_mode = None
            raise HomeAssistantError(
                translation_key="unexpected_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err

    async def _delayed_refresh(self) -> None:
        """
        Perform a delayed refresh with optimistic cache reset.

        ✅ SHARED CODE: Uses base _request_coordinator_refresh method.
        """
        # ✅ SHARED CODE: Use base refresh method
        delay = REFRESH_DELAY_EXT if self._device_key.startswith("EXT") else REFRESH_DELAY
        try:
            await self._request_coordinator_refresh(delay=delay, log_context=self._device_key)
        finally:
            # Always clear optimistic cache — even on CancelledError during HA reload
            old_mode = self._optimistic_mode
            self._optimistic_mode = None
            if old_mode is not None:
                _LOGGER.debug(
                    "Optimistic cache cleared for %s (was: %s)",
                    self._device_key,
                    old_mode,
                )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up select entities for the config entry.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry.
        async_add_entities: Callback to add entities.
    """
    coordinator = config_entry.runtime_data.coordinator
    selection = async_get_selection(config_entry)
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities: list[SelectEntity] = []

    _LOGGER.debug("Select Setup - Active features: %s", active_features)

    # Create select entities
    for select_config in SELECT_CONTROLS:
        # Selects are named after the control, but they read a controller key.
        if not selection.allows(str(select_config.get("device_key") or "")):
            _LOGGER.debug("Skipping select %s: datapoint not selected", select_config["key"])
            continue

        feature_id = select_config.get("feature_id")

        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Skipping select %s: feature %s not active",
                select_config["key"],
                feature_id,
            )
            continue

        description = SelectEntityDescription(
            key=select_config["key"],
            name=select_config["name"],
            icon=select_config.get("icon"),
            entity_category=select_config.get("entity_category"),
            entity_registry_enabled_default=select_config.get(
                "entity_registry_enabled_default", True
            ),
            translation_key=select_config.get("translation_key"),
        )

        entities.append(
            VioletSelect(
                coordinator,
                config_entry,
                description,
                select_config["device_key"],
                is_binary=select_config.get("binary", False),
                is_read_only=select_config.get("is_read_only", False),
            )
        )

    track_provided_entities(hass, config_entry, Platform.SELECT, entities)

    if entities:
        async_add_entities(entities)
        _LOGGER.debug("%d select entities set up", len(entities))
    else:
        _LOGGER.warning("No select entities set up")
