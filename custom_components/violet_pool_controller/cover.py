"""Cover Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, List, Final, ClassVar, cast

from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityDescription

from .const import (
    DOMAIN, 
    CONF_ACTIVE_FEATURES,
    COVER_FUNCTIONS,
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Status-Mapping für verschiedene API-Werte
COVER_STATE_MAP: Final[Dict[str, str]] = {
    "CLOSED": "closed",
    "OPEN": "open",
    "CLOSING": "closing",
    "OPENING": "opening",
    "STOPPED": "stopped",
    # Numerische Werte (als Strings)
    "0": "open",
    "1": "opening",
    "2": "closed",
    "3": "closing",
    "4": "stopped",
}


class VioletCover(VioletPoolControllerEntity, CoverEntity):
    """Repräsentation der Pool-Abdeckung (Cover)."""

    # Klassen-Attribute für Cover-Features
    _attr_device_class: ClassVar[str] = CoverDeviceClass.SHUTTER
    _attr_supported_features: ClassVar[int] = (
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
    )

    def __init__(
        self, 
        coordinator: VioletPoolDataUpdateCoordinator, 
        config_entry: ConfigEntry
    ):
        """Initialisiere die Cover-Entity.
        
        Args:
            coordinator: Der Daten-Koordinator
            config_entry: Die Config Entry des Geräts
        """
        # Erstelle eine EntityDescription für diese Cover-Entity
        entity_description = EntityDescription(
            key="COVER_STATE",
            name="Cover",
            icon="mdi:window-shutter",
        )
        
        # Feature-ID hinzufügen
        setattr(entity_description, "feature_id", "cover_control")
            
        # Initialisiere die Basisklasse
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_description=entity_description,
        )
        
        # Status-Tracking für optimierte Aktualisierungen
        self._last_action = None
        self._last_response = None

    def _update_from_coordinator(self) -> None:
        """Aktualisiere den Zustand der Cover-Entity anhand der Coordinator-Daten."""
        # Die Cover-Entity hat keine spezifischen State-Eigenschaften, die gesetzt werden müssen
        # Stattdessen werden die Eigenschaften is_closed, is_opening, etc. dynamisch berechnet
        pass

    @property
    def is_closed(self) -> bool:
        """Return if the cover is closed.
        
        Returns:
            bool: True, wenn das Cover geschlossen ist
        """
        # Hole den Cover-Status aus den API-Daten
        raw_state = self.get_str_value("COVER_STATE", "")
        state = COVER_STATE_MAP.get(raw_state, "")
        
        # Alternative Datenquellen prüfen, wenn kein direkter Status gefunden
        if not state and "COVER_IS_CLOSED" in self.coordinator.data:
            return self.get_bool_value("COVER_IS_CLOSED", False)
            
        # Alternative Datenquellen prüfen basierend auf COVER_OPEN/COVER_CLOSE
        if not state:
            cover_open = self.get_bool_value("COVER_OPEN", None)
            cover_close = self.get_bool_value("COVER_CLOSE", None)
            
            if cover_open is not None and cover_close is not None:
                # Wenn COVER_OPEN aus und COVER_CLOSE an, dann ist es geschlossen
                if not cover_open and cover_close:
                    return True
                # Wenn COVER_OPEN an und COVER_CLOSE aus, dann ist es offen
                if cover_open and not cover_close:
                    return False
        
        # Standard-Zustandsprüfung
        return state == "closed"

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening.
        
        Returns:
            bool: True, wenn das Cover gerade öffnet
        """
        # Hole den Cover-Status oder die letzte Bewegungsrichtung
        raw_state = self.get_str_value("COVER_STATE", "")
        state = COVER_STATE_MAP.get(raw_state, "")
        
        # Prüfe, ob direkter Status "opening" ist
        if state == "opening":
            return True
            
        # Alternative über Bewegungsrichtung prüfen
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "")
        
        # Wenn gerade ein Öffnungsbefehl gesendet wurde und noch nicht abgeschlossen ist
        if not self.is_open and self._last_action == "OPEN":
            return True
            
        # Standard: Prüfe, ob die Richtung "OPEN" ist und das Cover weder offen noch geschlossen ist
        return direction == "OPEN" and not self.is_closed and not self.is_open
        
    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing.
        
        Returns:
            bool: True, wenn das Cover gerade schließt
        """
        # Hole den Cover-Status oder die letzte Bewegungsrichtung
        raw_state = self.get_str_value("COVER_STATE", "")
        state = COVER_STATE_MAP.get(raw_state, "")
        
        # Prüfe, ob direkter Status "closing" ist
        if state == "closing":
            return True
            
        # Alternative über Bewegungsrichtung prüfen
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "")
        
        # Wenn gerade ein Schließbefehl gesendet wurde und noch nicht abgeschlossen ist
        if not self.is_closed and self._last_action == "CLOSE":
            return True
            
        # Standard: Prüfe, ob die Richtung "CLOSE" ist und das Cover weder offen noch geschlossen ist
        return direction == "CLOSE" and not self.is_closed and not self.is_open
        
    @property
    def is_open(self) -> bool:
        """Return if the cover is fully open.
        
        Returns:
            bool: True, wenn das Cover vollständig geöffnet ist
        """
        # Hole den Cover-Status aus den API-Daten
        raw_state = self.get_str_value("COVER_STATE", "")
        state = COVER_STATE_MAP.get(raw_state, "")
        
        # Alternative Datenquellen prüfen basierend auf COVER_OPEN/COVER_CLOSE
        if not state:
            cover_open = self.get_bool_value("COVER_OPEN", None)
            cover_close = self.get_bool_value("COVER_CLOSE", None)
            
            if cover_open is not None and cover_close is not None:
                # Wenn COVER_OPEN an und COVER_CLOSE aus, dann ist es offen
                if cover_open and not cover_close:
                    return True
        
        # Standard-Zustandsprüfung
        return state == "open"

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover.
        
        Args:
            **kwargs: Zusätzliche Parameter (nicht verwendet)
        """
        await self._send_cover_command("OPEN")

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover.
        
        Args:
            **kwargs: Zusätzliche Parameter (nicht verwendet)
        """
        await self._send_cover_command("CLOSE")

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover.
        
        Args:
            **kwargs: Zusätzliche Parameter (nicht verwendet)
        """
        await self._send_cover_command("STOP")

    async def _send_cover_command(self, action: str) -> None:
        """Send command to the cover.
        
        Args:
            action: Die Aktion für das Cover: "OPEN", "CLOSE" oder "STOP"
        """
        try:
            self._logger.debug("Sende Cover-Befehl: %s", action)
            
            # Speichere die letzte Aktion
            self._last_action = action
            
            # Bestimme den richtigen API-Endpunkt
            endpoint = "/set_cover"
            
            # Bereite die Kommandodaten vor
            command = {"action": action}
            
            # Spezielle Behandlung basierend auf dem COVER_FUNCTIONS-Dictionary
            cover_key = COVER_FUNCTIONS.get(action)
            if cover_key:
                # Für Systeme, die direkte Switch-Funktionen verwenden
                command = {
                    "id": cover_key,
                    "action": "PUSH",
                    "duration": 0,
                    "value": 0
                }
                endpoint = "/set_switch"
            
            # Sende das Kommando über die Device-API
            result = await self.device.async_send_command(endpoint, command)
            
            # Speichere die Antwort
            self._last_response = result
            
            # Prüfe das Ergebnis
            if isinstance(result, dict):
                success = result.get("success", False)
                if success:
                    self._logger.info("Cover-Befehl %s erfolgreich gesendet", action)
                else:
                    self._logger.warning(
                        "Cover-Befehl %s könnte nicht erfolgreich sein: %s",
                        action,
                        result
                    )
            
            # Aktualisiere die Daten vom Gerät
            await self.coordinator.async_request_refresh()
            
        except Exception as err:
            self._logger.error("Fehler bei Cover-Befehl %s: %s", action, err)
            
            # Kein Befehl aktiv
            self._last_action = None


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Violet Cover from a config entry.
    
    Args:
        hass: Home Assistant Instanz
        config_entry: Die Config Entry
        async_add_entities: Callback zum Hinzufügen der Entities
    """
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Hole aktive Features
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, 
        config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    
    # Cover-Typ bestimmen: Direkt über Status oder über OPEN/CLOSE Switches
    has_cover = any(key in coordinator.data for key in ["COVER_STATE", "COVER_OPEN", "COVER_CLOSE"])
    
    # Überprüfe, ob die erforderlichen Daten für das Cover vorhanden sind und Feature aktiv ist
    if has_cover and "cover_control" in active_features:
        async_add_entities([VioletCover(coordinator, config_entry)])
        _LOGGER.info("Pool-Abdeckungssteuerung hinzugefügt")
    else:
        _LOGGER.info(
            "Kein Cover-Feature aktiv oder keine Cover-Daten gefunden, "
            "Cover wird nicht hinzugefügt"
        )
