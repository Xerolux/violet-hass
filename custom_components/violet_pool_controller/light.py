# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Light platform for Violet Pool Controller (DMX scenes)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

from homeassistant.components.light import ColorMode, LightEntity, LightEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from violet_poolcontroller_api.api import VioletPoolAPIError

from .const import (
    ACTION_OFF,
    ACTION_ON,
    CONF_ACTIVE_FEATURES,
    DMX_LIGHTS,
    DOMAIN,
)
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity
from .entity_cleanup import track_provided_entities
from .entity_names import EntityNameResolver
from .entity_selection import async_get_selection

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platform; HA should not throttle entity state writes
PARALLEL_UPDATES = 0

# States where the DMX channel is active (matches DEVICE_STATE_MAPPING)
_DMX_ON_STATES = {1, 3, 4}

REFRESH_DELAY = 0.3
# The controller can serve a stale readings snapshot for several seconds
# after it applies a command (same rationale as the switch platform): keep
# refreshing (and keep the optimistic state) until the reported state
# confirms the commanded one, or the attempts run out.
REFRESH_CONFIRM_ATTEMPTS = 3
REFRESH_CONFIRM_RETRY_DELAY = 2.0


class VioletDmxLight(VioletPoolControllerEntity, LightEntity):
    """DMX scene exposed as a simple on/off light entity."""

    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: LightEntityDescription,
    ) -> None:
        """Initialize the DMX light entity."""
        super().__init__(coordinator, config_entry, description)
        # Optimistic command state with a generation counter, mirroring the
        # switch platform: only the confirmation task of the most recent
        # command may clear the optimistic state.
        self._optimistic_state: bool | None = None
        self._optimistic_generation: int = 0
        _LOGGER.debug("DMX light initialized: %s", description.key)

    @property
    def is_on(self) -> bool | None:
        """Return True when the DMX scene is active."""
        if self._optimistic_state is not None:
            return self._optimistic_state
        return self._reported_state()

    def _reported_state(self) -> bool | None:
        """Interpret the coordinator data as scene active/inactive."""
        # Composite values such as "4|DMX_SCENE_MANUAL" carry the state code in
        # their leading part.
        code = self.get_state_code(self.entity_description.key)
        if code is None:
            return None
        return code in _DMX_ON_STATES

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Activate the DMX scene."""
        await self._send_dmx_command(ACTION_ON)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Deactivate the DMX scene."""
        await self._send_dmx_command(ACTION_OFF)

    async def _send_dmx_command(self, action: str) -> None:
        """Send a command to the DMX scene channel."""
        key = self.entity_description.key
        try:
            _LOGGER.debug("DMX command %s → %s", key, action)
            result = await self.device.api.set_switch_state(key=key, action=action)
            if result.get("success") is True:
                _LOGGER.info("DMX %s %s succeeded", key, action)
                self._optimistic_state = action == ACTION_ON
                self._optimistic_generation += 1
                self.async_write_ha_state()
                task = asyncio.create_task(
                    self._confirm_command(key, self._optimistic_generation)
                )
                task.add_done_callback(self._handle_refresh_error)
            else:
                self._optimistic_state = None
                self._optimistic_generation += 1
                _LOGGER.warning("DMX %s %s: %s", key, action, result.get("response", result))
                raise HomeAssistantError(
                    translation_key="api_error",
                    translation_domain=DOMAIN,
                    translation_placeholders={
                        "detail": str(result.get("response", "Command failed"))
                    },
                )
        except VioletPoolAPIError as err:
            _LOGGER.error("API error for DMX %s %s: %s", key, action, err)
            self._optimistic_state = None
            self._optimistic_generation += 1
            raise HomeAssistantError(
                translation_key="api_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err
        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.exception("Unexpected error for DMX %s %s: %s", key, action, err)
            self._optimistic_state = None
            self._optimistic_generation += 1
            raise HomeAssistantError(
                translation_key="unexpected_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err

    async def _confirm_command(self, key: str, generation: int) -> None:
        """
        Confirm a commanded DMX state, with retries against stale data.

        The controller can serve a stale readings snapshot for several
        seconds after applying a command, so the optimistic state is kept
        and the refresh repeated until the reported state confirms the
        command.  When the attempts run out, the reported state wins.

        Args:
            key: The DMX scene key.
            generation: The optimistic generation of the commanding task; when
                a newer command supersedes it, this task stops and may not
                clear the newer command's optimistic state.
        """
        try:
            for attempt in range(REFRESH_CONFIRM_ATTEMPTS):
                if generation != self._optimistic_generation:
                    _LOGGER.debug(
                        "Refresh for %s superseded by a newer command; aborting",
                        key,
                    )
                    return
                target = self._optimistic_state
                if target is None:
                    return

                success = await self._request_coordinator_refresh(
                    delay=REFRESH_DELAY if attempt == 0 else REFRESH_CONFIRM_RETRY_DELAY,
                    log_context=key,
                )

                if success and self.coordinator.data is not None:
                    if self._reported_state() == target:
                        _LOGGER.debug(
                            "DMX %s confirmed as %s (attempt %d)",
                            key,
                            "ON" if target else "OFF",
                            attempt + 1,
                        )
                        break
                    _LOGGER.debug(
                        "DMX command confirmation pending for %s (attempt %d/%d)",
                        key,
                        attempt + 1,
                        REFRESH_CONFIRM_ATTEMPTS,
                    )
        finally:
            if generation == self._optimistic_generation:
                self._optimistic_state = None
            self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DMX light entities from a config entry."""
    coordinator = config_entry.runtime_data.coordinator

    selection = async_get_selection(config_entry)
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )

    if coordinator.data is None:
        _LOGGER.warning("Coordinator data is None; skipping DMX light setup")
        track_provided_entities(hass, config_entry, Platform.LIGHT, [])
        return

    hw_config = coordinator.device.hardware_config if coordinator.device else None
    name_resolver = EntityNameResolver(hw_config)

    entities: list[LightEntity] = []
    for light_config in DMX_LIGHTS:
        key = cast(str, light_config["key"])
        if key not in coordinator.data:
            continue

        # Each scene declares the feature it belongs to ("dmx_scenes"). The
        # platform used to gate on "led_lighting" instead, so turning the DMX
        # scenes off left twelve lights in place and turning the pool light off
        # removed them.
        feature_id = light_config.get("feature_id")
        if feature_id and feature_id not in active_features:
            _LOGGER.debug("Skipping light %s: feature %s not active", key, feature_id)
            continue

        if not selection.allows(key):
            _LOGGER.debug("Skipping light %s: datapoint not selected", key)
            continue

        entity_name = cast(str, light_config["name"])
        resolved = name_resolver.resolve_entity_name("light", key, entity_name)
        if resolved:
            entity_name = resolved

        description = LightEntityDescription(
            key=key,
            name=entity_name,
            translation_key=cast(str | None, light_config.get("translation_key")),
            icon=cast(str | None, light_config.get("icon")),
        )
        entities.append(VioletDmxLight(coordinator, config_entry, description))

    track_provided_entities(hass, config_entry, Platform.LIGHT, entities)

    if entities:
        async_add_entities(entities)
        _LOGGER.info("%d DMX light entities added for '%s'", len(entities), config_entry.title)
