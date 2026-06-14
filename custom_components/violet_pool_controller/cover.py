# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

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
from violet_poolcontroller_api.api import VioletPoolAPIError

try:
    from violet_poolcontroller_api.api import VioletUnsafeOperationError
except ImportError:

    class VioletUnsafeOperationError(VioletPoolAPIError):
        """Fallback for older violet-poolController-api releases."""


from .const import (
    ACTION_PUSH,
    CONF_ACTIVE_FEATURES,
    COVER_FUNCTIONS,
    COVER_STATE_MAP,
    DOMAIN,
)
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity
from .entity_names import EntityNameResolver

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
        # Apply dynamic naming from hardware config
        name_resolver = EntityNameResolver(
            coordinator.device.hardware_config if coordinator.device else None
        )
        name = name_resolver.resolve_entity_name("cover", "COVER", "Pool Cover") or "Pool Cover"

        entity_description = CoverEntityDescription(
            key="COVER_STATE",
            name=name,
            icon="mdi:window-shutter",
            translation_key="pool_cover",
        )
        super().__init__(coordinator, config_entry, entity_description)
        self._last_action: str | None = None
        _LOGGER.debug("Cover entity initialized for %s", config_entry.title)

    def _map_cover_state(self) -> str:
        """Map COVER_STATE to normalized value, case-insensitive."""
        raw = self.get_str_value("COVER_STATE", "") or ""
        state = COVER_STATE_MAP.get(raw)
        if state is not None:
            return state
        return COVER_STATE_MAP.get(raw.upper(), "")

    @property
    def is_closed(self) -> bool | None:
        """Return True if the cover is closed, None if the state is unknown."""
        state = self._map_cover_state()
        if not state:
            # Unknown/unmapped COVER_STATE must not be reported as "open"
            return None
        return state == "closed"

    @property
    def is_opening(self) -> bool:
        """Return True if the cover is opening."""
        return self._map_cover_state() == "opening"

    @property
    def is_closing(self) -> bool:
        """Return True if the cover is closing."""
        return self._map_cover_state() == "closing"

    @property
    def is_open(self) -> bool:
        """Return True if the cover is open."""
        return self._map_cover_state() == "open"

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
        self._last_action = action

        try:
            _LOGGER.debug("Sending cover command: %s", action)

            # acknowledge_unsafe=True: HA only exposes cover controls to users
            # who have explicitly enabled the cover feature in the config flow,
            # so the safety acknowledgment is implicitly given at setup time.
            api = self.device.api
            if hasattr(api, "set_cover_command"):
                result = await api.set_cover_command(action, acknowledge_unsafe=True)
            else:
                cover_key = COVER_FUNCTIONS.get(action.strip().upper())
                if not cover_key:
                    msg = f"Unknown cover action '{action}'."
                    raise VioletPoolAPIError(msg)
                result = await api.set_switch_state(cover_key, ACTION_PUSH)

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

        except VioletUnsafeOperationError as err:
            _LOGGER.error("Cover command '%s' refused (unsafe): %s", action, err)
            raise HomeAssistantError(
                translation_key="api_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err

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
