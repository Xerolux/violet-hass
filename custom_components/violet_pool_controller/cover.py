"""Cover Integration für den Violet Pool Controller - COMPLETE FIX."""
import logging

from homeassistant.components.cover import CoverEntity, CoverDeviceClass, CoverEntityFeature, CoverEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_ACTIVE_FEATURES, COVER_FUNCTIONS
from .api import ACTION_PUSH, VioletPoolAPIError
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

COVER_STATE_MAP = {
    "CLOSED": "closed", "OPEN": "open", "CLOSING": "closing", "OPENING": "opening",
    "STOPPED": "stopped", "0": "open", "1": "opening", "2": "closed", "3": "closing", "4": "stopped"
}

class VioletCover(VioletPoolControllerEntity, CoverEntity):
    """Repräsentation der Pool-Abdeckung."""
    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry) -> None:
        """Initialisiert die Cover-Entity."""
        entity_description = CoverEntityDescription(
            key="COVER_STATE",
            name="Cover",
            icon="mdi:window-shutter",
        )
        super().__init__(coordinator, config_entry, entity_description)
        self._last_action: str | None = None

    @property
    def is_closed(self) -> bool:
        """Gibt True zurück, wenn das Cover geschlossen ist."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", ""), "")
        return state == "closed"

    @property
    def is_opening(self) -> bool:
        """Gibt True zurück, wenn das Cover öffnet."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", ""), "")
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "")
        return state == "opening" or (self._last_action == "OPEN" and not self.is_open) or (direction == "OPEN" and not self.is_closed and not self.is_open)

    @property
    def is_closing(self) -> bool:
        """Gibt True zurück, wenn das Cover schließt."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", ""), "")
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "")
        return state == "closing" or (self._last_action == "CLOSE" and not self.is_closed) or (direction == "CLOSE" and not self.is_closed and not self.is_open)

    @property
    def is_open(self) -> bool:
        """Gibt True zurück, wenn das Cover geöffnet ist."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", ""), "")
        return state == "open"

    async def async_open_cover(self, **kwargs) -> None:
        """Öffnet das Cover."""
        await self._send_cover_command("OPEN")

    async def async_close_cover(self, **kwargs) -> None:
        """Schließt das Cover."""
        await self._send_cover_command("CLOSE")

    async def async_stop_cover(self, **kwargs) -> None:
        """Stoppt das Cover."""
        await self._send_cover_command("STOP")

    async def _send_cover_command(self, action: str) -> None:
        """Sendet Cover-Befehl."""
        cover_api_key = COVER_FUNCTIONS.get(action.upper())
        if not cover_api_key:
            _LOGGER.error("Ungültige Aktion: %s", action)
            return

        self._last_action = action
        try:
            _LOGGER.debug("Sende Cover-Befehl: %s (API-Key: %s)", action, cover_api_key)
            result = await self.device.api.set_switch_state(key=cover_api_key, action=ACTION_PUSH)
            if result.get("success", True):
                _LOGGER.info("Cover-Befehl %s gesendet", action)
            else:
                _LOGGER.warning("Cover-Befehl %s möglicherweise fehlgeschlagen: %s", action, result.get("response", result))
            await self.coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler bei Cover-Befehl %s: %s", action, err)
            raise HomeAssistantError(f"Cover-Aktion {action} fehlgeschlagen: {err}") from err

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Richtet Cover-Entity ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    if "cover_control" in active_features and "COVER_STATE" in coordinator.data:
        async_add_entities([VioletCover(coordinator, config_entry)])
        _LOGGER.info("Cover-Entity hinzugefügt")
    else:
        _LOGGER.info("Cover-Control inaktiv oder keine Daten")