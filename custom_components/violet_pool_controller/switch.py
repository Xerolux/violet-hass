"""Switch-Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Callable, List, cast
from dataclasses import dataclass

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN,
    INTEGRATION_VERSION,
    MANUFACTURER,
    SWITCHES,
    STATE_MAP,
    DOSING_FUNCTIONS,
    CONF_ACTIVE_FEATURES,
    API_SET_FUNCTION_MANUALLY,
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class VioletSwitchEntityDescription(SwitchEntityDescription):
    """Class describing Violet Pool switch entities."""

    feature_id: Optional[str] = None


class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Representation of a Violet Pool Controller Switch."""

    entity_description: VioletSwitchEntityDescription

    def __init__(
        self, 
        coordinator: VioletPoolDataUpdateCoordinator, 
        config_entry: ConfigEntry,
        description: VioletSwitchEntityDescription,
    ):
        """Initialize the switch.
        
        Args:
            coordinator: The data update coordinator
            config_entry: The config entry
            description: The entity description
        """
        # Initialisiere die Basisklasse
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_description=description,
        )
        
        # Icon-Eigenschaften
        self._icon_base = description.icon
        
        # Tracking für Logging
        self._has_logged_none_state = False

    @property
    def icon(self) -> str:
        """Return the icon for the switch, changing based on state."""
        return self._icon_base if self.is_on else f"{self._icon_base}-off"

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self._get_switch_state()

    def _get_switch_state(self) -> bool:
        """Get the current state of the switch from the coordinator data."""
        # Nutze die sicheren Abrufmethoden aus der Basis-Entity
        raw_state = self.get_str_value(self.entity_description.key, "")
        
        if not raw_state:
            if not self._has_logged_none_state:
                self._logger.warning(
                    "Switch %s returned empty state. Defaulting to 'OFF'.", 
                    self.entity_description.key
                )
                self._has_logged_none_state = True
            return False
            
        # Konvertiere den Wert mit der STATE_MAP
        if raw_state.upper() in STATE_MAP:
            return STATE_MAP[raw_state.upper()]
            
        # Versuche direkte Boolsche Konvertierung als Fallback
        return self.get_bool_value(self.entity_description.key, False)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self._send_command("ON")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self._send_command("OFF")

    async def async_turn_auto(self, auto_delay: int = 0) -> None:
        """Set the switch to AUTO mode."""
        await self._send_command("AUTO", auto_delay)

    async def _send_command(self, action: str, value: int = 0) -> None:
        """Send command to the device.
        
        Args:
            action: The action to perform (ON, OFF, AUTO)
            value: Optional value for the command (e.g., delay)
        """
        try:
            # Der korrekte Endpunkt ist "/setFunctionManually" aus der API-Doku
            endpoint = API_SET_FUNCTION_MANUALLY
            
            # Erstelle das Kommando als Rohformat, wie in der API erwartet
            key = self.entity_description.key
            raw_query = f"{key},{action},{value},0"
            
            self._logger.debug("Sende Raw-Command: %s", raw_query)
            
            # Nutze die zentrale Befehlsmethode des Geräts
            result = await self.device.api.api_request(
                endpoint=endpoint,
                raw_query=raw_query
            )
            
            self._logger.debug(
                "Command sent to %s: %s (value: %s), Response: %s",
                key,
                action,
                value,
                result
            )
            
            # Aktualisiere die Daten
            await self.coordinator.async_request_refresh()
            
        except Exception as err:
            self._logger.error(
                "Fehler bei Send_Command %s für %s: %s",
                action,
                self.entity_description.key,
                err
            )
            
    async def _manual_dosing(self, duration_seconds: int) -> None:
        """Führt eine manuelle Dosierung für die angegebene Dauer aus.
        
        Args:
            duration_seconds: Dauer der Dosierung in Sekunden
        """
        try:
            # Überprüfe, ob es sich um einen Dosierungs-Switch handelt
            dosing_type = None
            for key, value in DOSING_FUNCTIONS.items():
                if value == self.entity_description.key:
                    dosing_type = key
                    break

            if not dosing_type:
                self._logger.error(
                    "Der Switch %s ist kein Dosierungs-Switch",
                    self.entity_description.key
                )
                return

            # Führe die manuelle Dosierung aus als Raw Query
            endpoint = API_SET_FUNCTION_MANUALLY
            raw_query = f"{self.entity_description.key},MAN,{duration_seconds},0"
            
            result = await self.device.api.api_request(
                endpoint=endpoint,
                raw_query=raw_query
            )
            
            self._logger.info(
                "Manuelle Dosierung für %s für %d Sekunden gestartet: %s",
                dosing_type,
                duration_seconds,
                result
            )
            
            # Aktualisiere die Daten vom Gerät
            await self.coordinator.async_request_refresh()
            
        except Exception as err:
            self._logger.error("Fehler bei der manuellen Dosierung: %s", err)

    async def _send_with_pump_speed(self, pump_speed: int) -> None:
        """Aktiviert den PV-Überschussmodus mit einer bestimmten Pumpendrehzahl.
        
        Args:
            pump_speed: Die Pumpendrehzahl (1-3)
        """
        try:
            # Sicherstellen, dass wir einen PV-Surplus-Switch haben
            if self.entity_description.key != "PVSURPLUS":
                self._logger.error(
                    "Der Switch %s ist kein PV-Überschuss-Switch",
                    self.entity_description.key
                )
                return
            
            # Setze den PV-Überschussmodus als Raw Query
            endpoint = API_SET_FUNCTION_MANUALLY
            raw_query = f"PVSURPLUS,ON,{pump_speed},0"
            
            result = await self.device.api.api_request(
                endpoint=endpoint,
                raw_query=raw_query
            )
            
            self._logger.info(
                "PV-Überschussmodus aktiviert mit Pumpenstufe %d: %s",
                pump_speed,
                result
            )
            
            # Aktualisiere die Daten vom Gerät
            await self.coordinator.async_request_refresh()
            
        except Exception as err:
            self._logger.error("Fehler beim Aktivieren des PV-Überschussmodus: %s", err)


class VioletPVSurplusSwitch(VioletSwitch):
    """Special switch for PV Surplus functionality."""
    
    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry):
        """Initialize the PV Surplus switch."""
        description = VioletSwitchEntityDescription(
            key="PVSURPLUS",
            name="PV-Überschuss",
            icon="mdi:solar-power",
            device_class=SwitchDeviceClass.SWITCH,
            feature_id="pv_surplus",
        )
        
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            description=description,
        )
        
    def _get_switch_state(self) -> bool:
        """Get the current state of the PV surplus switch."""
        # Nutze die sicheren Abrufmethoden aus der Basis-Entity
        state = self.get_int_value(self.entity_description.key, 0)
        # PV Surplus wird im API als 0, 1 oder 2 zurückgegeben
        return state in (1, 2)
        
    async def async_turn_on(self, **kwargs) -> None:
        """Turn on PV surplus mode."""
        try:
            # Standard-Pumpendrehzahl verwenden
            pump_speed = 2
            
            # Direkt das Raw-Query Format verwenden
            endpoint = API_SET_FUNCTION_MANUALLY
            raw_query = f"PVSURPLUS,ON,{pump_speed},0"
            
            result = await self.device.api.api_request(
                endpoint=endpoint,
                raw_query=raw_query
            )
            
            self._logger.info(
                "PV-Überschussmodus aktiviert mit Stufe %d: %s",
                pump_speed,
                result
            )
            
            await self.coordinator.async_request_refresh()
            
        except Exception as err:
            self._logger.error("Fehler beim Aktivieren des PV-Überschussmodus: %s", err)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off PV surplus mode."""
        try:
            # Direkt das Raw-Query Format verwenden
            endpoint = API_SET_FUNCTION_MANUALLY
            raw_query = "PVSURPLUS,OFF,0,0"
            
            result = await self.device.api.api_request(
                endpoint=endpoint,
                raw_query=raw_query
            )
            
            self._logger.info(
                "PV-Überschussmodus deaktiviert: %s",
                result
            )
            
            await self.coordinator.async_request_refresh()
            
        except Exception as err:
            self._logger.error("Fehler beim Deaktivieren des PV-Überschussmodus: %s", err)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Violet Pool Controller switches from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Hole aktive Features
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, 
        config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )

    # Verfügbare Switches aus der API filtern
    available_data_keys = set(coordinator.data.keys())
    switches: List[VioletSwitch] = []
    
    # Mapping von Switch-Keys zu Feature-IDs erstellen
    feature_map = {
        "FILTER": "filter_control",
        "HEATER": "heating",
        "SOLAR": "solar",
        "BACKWASH": "backwash",
        "PVSURPLUS": "pv_surplus",
        "LIGHT": "led_lighting",
        "COVER_OPEN": "cover_control",
        "COVER_CLOSE": "cover_control",
        "REFILL": "water_refill",
        "DOS_1_CL": "chlorine_control",
        "DOS_4_PHM": "ph_control",
        "DOS_5_PHP": "ph_control",
    }

    # Standard-Switches erstellen
    for sw in SWITCHES:
        key = sw["key"]
        
        # Prüfe, ob der Switch in den API-Daten vorhanden ist
        if key not in available_data_keys:
            continue
            
        # Prüfe, ob das zugehörige Feature aktiv ist
        feature_id = feature_map.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Switch %s wird übersprungen, da Feature %s nicht aktiv ist",
                key,
                feature_id
            )
            continue
            
        # Bestimme EntityCategory basierend auf dem Switch-Typ
        entity_category = None
        if key.startswith("DOS_"):
            entity_category = EntityCategory.CONFIG
        
        # Erstelle die Entity-Beschreibung
        description = VioletSwitchEntityDescription(
            key=key,
            name=sw["name"],
            icon=sw["icon"],
            feature_id=feature_id,
            entity_category=entity_category if entity_category else None,
        )
        
        # Erstelle den Switch
        switches.append(
            VioletSwitch(
                coordinator=coordinator, 
                config_entry=config_entry,
                description=description,
            )
        )
    
    # Prüfen, ob bereits ein PV-Surplus-Switch existiert
    pv_switch_exists = any(switch.entity_description.key == "PVSURPLUS" for switch in switches)

    # Speziellen PV Surplus Switch hinzufügen, wenn in den Daten vorhanden und Feature aktiv
    if "PVSURPLUS" in available_data_keys and "pv_surplus" in active_features and not pv_switch_exists:
        switches.append(VioletPVSurplusSwitch(coordinator, config_entry))

    # Füge alle Switches hinzu
    if switches:
        async_add_entities(switches)
        
        # Registriere Dienste
        platform = entity_platform.async_get_current_platform()

        # Service zum Umschalten in den AUTO-Modus
        platform.async_register_entity_service(
            "turn_auto",
            {vol.Optional("auto_delay", default=0): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=3600)
            )},
            "async_turn_auto",
        )
        
        # Service für PV Surplus mit Pumpen-Drehzahl
        platform.async_register_entity_service(
            "set_pv_surplus",
            {vol.Optional("pump_speed", default=2): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3)
            )},
            "_send_with_pump_speed",
        )
        
        # Service für manuelle Dosierung
        platform.async_register_entity_service(
            "manual_dosing",
            {vol.Required("duration_seconds"): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3600)
            )},
            "_manual_dosing",
        )
    else:
        _LOGGER.info(
            "Keine Switches gefunden oder keine aktiven Switch-Features konfiguriert"
        )