
"""Cover platform for Violet Pool Controller."""
from __future__ import annotations

import logging

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityDescription,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .violet_pool_api.api import VioletPoolAPIError
from .const import (
    ACTION_PUSH,
    CONF_ACTIVE_FEATURES,
    COVER_FUNCTIONS,
    COVER_STATE_MAP,
    DOMAIN,
)
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platforms; HA should not throttle entity state writes
PARALLEL_UPDATES = 0


class VioletCover(VioletPoolControllerEntity, CoverEntity):
    """Representation of the pool cover."""

    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_supported_features = (
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
    )

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the cover entity."""
        entity_description = CoverEntityDescription(
            key="COVER_STATE",
            name="Pool Cover",
            icon="mdi:window-shutter",
        )
        super().__init__(coordinator, config_entry, entity_description)
        self._last_action: str | None = None
        _LOGGER.debug("Cover entity initialized for %s", config_entry.title)

    @property
    def is_closed(self) -> bool:
        """Return True if the cover is closed."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", "") or "", "")
        return state == "closed"

    @property
    def is_opening(self) -> bool:
        """Return True if the cover is opening."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", "") or "", "")
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "") or ""

        # Cover is opening when:
        # 1. State is explicitly "opening"
        # 2. Last action was OPEN and cover is not yet open
        # 3. Movement direction is OPEN and cover is in motion
        return (
            state == "opening"
            or (self._last_action == "OPEN" and not self.is_open)
            or (direction == "OPEN" and not self.is_closed and not self.is_open)
        )

    @property
    def is_closing(self) -> bool:
        """Return True if the cover is closing."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", "") or "", "")
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "") or ""

        # Cover is closing when:
        # 1. State is explicitly "closing"
        # 2. Last action was CLOSE and cover is not yet closed
        # 3. Movement direction is CLOSE and cover is in motion
        return (
            state == "closing"
            or (self._last_action == "CLOSE" and not self.is_closed)
            or (direction == "CLOSE" and not self.is_closed and not self.is_open)
        )

    @property
    def is_open(self) -> bool:
        """Return True if the cover is open."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", "") or "", "")
        return state == "open"

    async def async_open_cover(self, **kwargs) -> None:
        """Open the pool cover."""
        _LOGGER.info("Opening pool cover")
        await self._send_cover_command("OPEN")

    async def async_close_cover(self, **kwargs) -> None:
        """Close the pool cover."""
        _LOGGER.info("Closing pool cover")
        await self._send_cover_command("CLOSE")

    async def async_stop_cover(self, **kwargs) -> None:
        """Stop the pool cover."""
        _LOGGER.info("Stopping pool cover")
        await self._send_cover_command("STOP")

    async def _send_cover_command(self, action: str) -> None:
        """Send cover command to the controller.

        Args:
            action: Action (OPEN, CLOSE, STOP)

        Raises:
            HomeAssistantError: On API errors.
        """
        cover_api_key = COVER_FUNCTIONS.get(action.upper())

        if not cover_api_key:
            _LOGGER.error("Invalid cover action: %s", action)
            raise HomeAssistantError(
                translation_key="invalid_action",
                translation_domain=DOMAIN,
                translation_placeholders={"action": action},
            )

        self._last_action = action

        try:
            _LOGGER.debug("Sending cover command: %s", action)

            result = await self.device.api.set_switch_state(
                key=cover_api_key, action=ACTION_PUSH
            )

            if result.get("success") is True:
                _LOGGER.info("Cover command '%s' sent successfully", action)
            else:
                error_msg = result.get("response", result)
                _LOGGER.warning(
                    "Cover command '%s' may have failed: %s",
                    action,
                    error_msg,
                )

            # Refresh data after command
            await self.coordinator.async_request_refresh()

        except VioletPoolAPIError as err:
            _LOGGER.error("API error for cover command '%s': %s", action, err)
            raise HomeAssistantError(
                translation_key="api_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err

        except Exception as err:
            _LOGGER.exception(
                "Unexpected error for cover command '%s': %s", action, err
            )
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
    """Set up cover entity from a config entry."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # Get features from options or data
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )

    # Check if cover control is enabled and data is available
    if "cover_control" in active_features:
        # None-check for coordinator.data
        if coordinator.data is None:
            _LOGGER.warning(
                "Cover control enabled but coordinator data is None. "
                "Cover entity will not be created."
            )
            return

        if "COVER_STATE" in coordinator.data:
            async_add_entities([VioletCover(coordinator, config_entry)])
            _LOGGER.info("Cover entity added for '%s'", config_entry.title)
        else:
            _LOGGER.info(
                "Cover control enabled but controller provides no COVER_STATE data. "
                "This is normal when no cover is configured."
            )
    else:
        _LOGGER.debug("Cover control not enabled")
