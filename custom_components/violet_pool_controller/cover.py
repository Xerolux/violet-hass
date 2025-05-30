"""Cover Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Final, ClassVar
from dataclasses import dataclass

from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
    CoverEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_ACTIVE_FEATURES,
    COVER_FUNCTIONS, 
)
from .api import (
    ACTION_PUSH,
    VioletPoolAPIError, VioletPoolConnectionError, VioletPoolCommandError
)
from homeassistant.exceptions import HomeAssistantError # Import HomeAssistantError
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

COVER_STATE_MAP: Final[Dict[str, str]] = {
    "CLOSED": "closed",
    "OPEN": "open",
    "CLOSING": "closing",
    "OPENING": "opening",
    "STOPPED": "stopped",
    "0": "open",
    "1": "opening",
    "2": "closed",
    "3": "closing",
    "4": "stopped",
}

@dataclass
class VioletCoverEntityDescription(CoverEntityDescription):
    """Beschreibung der Violet Pool Cover-Entities."""
    feature_id: Optional[str] = None

class VioletCover(VioletPoolControllerEntity, CoverEntity):
    """Repräsentation der Pool-Abdeckung (Cover)."""
    _attr_device_class: ClassVar[str] = CoverDeviceClass.SHUTTER
    _attr_supported_features: ClassVar[int] = (
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
    )
    entity_description: VioletCoverEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry
    ):
        """Initialisiert die Cover-Entity."""
        entity_description = VioletCoverEntityDescription(
            key="COVER_STATE",
            name="Cover",
            icon="mdi:window-shutter",
            feature_id="cover_control",
        )
        super().__init__(coordinator, config_entry, entity_description)
        self._last_action = None
        self._last_response = None

    @property
    def is_closed(self) -> bool:
        """Gibt True zurück, wenn das Cover geschlossen ist."""
        raw_state = self.get_str_value("COVER_STATE", "")
        state = COVER_STATE_MAP.get(raw_state, "")
        return state == "closed" or raw_state in ["CLOSED", "2", 2]

    @property
    def is_opening(self) -> bool:
        """Gibt True zurück, wenn das Cover gerade öffnet."""
        # This logic uses COVER_STATE and LAST_MOVING_DIRECTION from the device,
        # and self._last_action for optimistic immediate feedback after a command.
        raw_state = self.get_str_value("COVER_STATE", "")
        state = COVER_STATE_MAP.get(raw_state, "")
        if state == "opening" or raw_state in ["OPENING", "1", 1]:
            return True
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "")
        # Optimistic check based on last action, useful if state update is delayed
        if not self.is_open and self._last_action == "OPEN": # OPEN is the HA service call action
            return True
        return direction == "OPEN" and not self.is_closed and not self.is_open

    @property
    def is_closing(self) -> bool:
        """Gibt True zurück, wenn das Cover gerade schließt."""
        # This logic uses COVER_STATE and LAST_MOVING_DIRECTION from the device,
        # and self._last_action for optimistic immediate feedback after a command.
        raw_state = self.get_str_value("COVER_STATE", "")
        state = COVER_STATE_MAP.get(raw_state, "")
        if state == "closing" or raw_state in ["CLOSING", "3", 3]:
            return True
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "")
        # Optimistic check based on last action
        if not self.is_closed and self._last_action == "CLOSE": # CLOSE is the HA service call action
            return True
        return direction == "CLOSE" and not self.is_closed and not self.is_open

    @property
    def is_open(self) -> bool:
        """Gibt True zurück, wenn das Cover vollständig geöffnet ist."""
        raw_state = self.get_str_value("COVER_STATE", "")
        state = COVER_STATE_MAP.get(raw_state, "")
        return state == "open" or raw_state in ["OPEN", "0", 0]

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Öffnet das Cover."""
        await self._send_cover_command("OPEN")

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Schließt das Cover."""
        await self._send_cover_command("CLOSE")

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stoppt das Cover."""
        await self._send_cover_command("STOP")

    async def _send_cover_command(self, action: str) -> None:
        """Sendet einen Befehl an das Cover über die VioletPoolAPI."""
        # 'action' here refers to "OPEN", "CLOSE", "STOP" from Home Assistant services.
        self._last_action = action # For optimistic state updates
        
        cover_api_key = COVER_FUNCTIONS.get(action.upper()) # Ensure action is uppercase for dict lookup
        
        if not cover_api_key:
            self._logger.error(f"Ungültige Cover-Aktion '{action}'. Nicht in COVER_FUNCTIONS gefunden.")
            return

        try:
            self._logger.debug(f"Sende Cover-Befehl: Aktion='{action}', API-Key='{cover_api_key}', API-Aktion='{ACTION_PUSH}'")
            
            result = await self.device.api.set_switch_state(
                key=cover_api_key,
                action=ACTION_PUSH, # All cover actions use PUSH
                duration=0,
                last_value=0
            )
            self._last_response = result # Store for debugging or other purposes if needed

            if result.get("success", True): # Assume success if not explicitly false
                self._logger.info("Cover-Befehl '%s' (API-Key: %s) erfolgreich gesendet.", action, cover_api_key)
            else:
                self._logger.warning(
                    "Cover-Befehl '%s' (API-Key: %s) möglicherweise fehlgeschlagen: %s",
                    action,
                    cover_api_key,
                    result.get("response", result)
                )
            await self.coordinator.async_request_refresh()
        except (VioletPoolConnectionError, VioletPoolCommandError) as err:
            self._logger.error(f"API-Fehler bei Cover-Befehl '{action}' (API-Key: {cover_api_key}): {err}")
            # self._last_action = None # Consider if resetting _last_action on error is desired
            raise HomeAssistantError(f"Cover-Aktion '{action}' fehlgeschlagen: {err}") from err
        except Exception as err: # Catch any other unexpected errors
            self._logger.exception(f"Unerwarteter Fehler bei Cover-Befehl '{action}' (API-Key: {cover_api_key}): {err}")
            # self._last_action = None
            raise HomeAssistantError(f"Unerwarteter Fehler bei Cover-Aktion '{action}': {err}") from err

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Richtet die Cover-Entity basierend auf der Config Entry ein."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    if "cover_control" in active_features and "COVER_STATE" in coordinator.data:
        async_add_entities([VioletCover(coordinator, config_entry)])
        _LOGGER.info("Pool-Abdeckungssteuerung hinzugefügt")
    else:
        _LOGGER.info("Cover-Control-Feature nicht aktiviert oder keine Cover-Daten gefunden")