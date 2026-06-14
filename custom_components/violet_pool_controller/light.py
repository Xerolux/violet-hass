# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Light platform for Violet Pool Controller (DMX scenes)."""

from __future__ import annotations

import logging
from typing import Any, cast

from homeassistant.components.light import ColorMode, LightEntity, LightEntityDescription
from homeassistant.config_entries import ConfigEntry
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
from .entity_names import EntityNameResolver

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platform; HA should not throttle entity state writes
PARALLEL_UPDATES = 0

# States where the DMX channel is active (matches DEVICE_STATE_MAPPING)
_DMX_ON_STATES = {1, 3, 4}


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
        _LOGGER.debug("DMX light initialized: %s", description.key)

    @property
    def is_on(self) -> bool | None:
        """Return True when the DMX scene is active."""
        raw = self.get_value(self.entity_description.key)
        if raw is None:
            return None
        try:
            return int(raw) in _DMX_ON_STATES
        except (ValueError, TypeError):
            return None

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
            else:
                _LOGGER.warning("DMX %s %s: %s", key, action, result.get("response", result))
            await self.coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API error for DMX %s %s: %s", key, action, err)
            raise HomeAssistantError(
                translation_key="api_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err
        except Exception as err:
            _LOGGER.exception("Unexpected error for DMX %s %s: %s", key, action, err)
            raise HomeAssistantError(
                translation_key="unexpected_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DMX light entities from a config entry."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )

    if "led_lighting" not in active_features:
        _LOGGER.debug("LED lighting feature not enabled; skipping DMX lights")
        return

    if coordinator.data is None:
        _LOGGER.warning("Coordinator data is None; skipping DMX light setup")
        return

    hw_config = coordinator.device.hardware_config if coordinator.device else None
    name_resolver = EntityNameResolver(hw_config)

    entities: list[LightEntity] = []
    for light_config in DMX_LIGHTS:
        key = cast(str, light_config["key"])
        if key not in coordinator.data:
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

    if entities:
        async_add_entities(entities)
        _LOGGER.info("%d DMX light entities added for '%s'", len(entities), config_entry.title)
