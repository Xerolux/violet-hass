"""Climate Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, List, Optional, Set, Final, ClassVar, cast
from dataclasses import dataclass

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
    ClimateEntityDescription,
)
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN,
    CONF_ACTIVE_FEATURES,
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# HVAC-Modus-Mapping für verschiedene API-Zustände
HEATER_HVAC_MODES: Final[Dict[int, str]] = {
    0: HVACMode.AUTO,  # AUTO (nicht an)
    1: HVACMode.AUTO,  # AUTO (an)
    2: HVACMode.AUTO,  # AUS durch Regelregel
    3: HVACMode.AUTO,  # EIN durch Notfallregel
    4: HVACMode.HEAT,  # MANUAL ON
    5: HVACMode.AUTO,  # AUS durch Notfallregel
    6: HVACMode.OFF,   # MANUAL OFF
}

# HVAC-Aktion-Mapping für verschiedene API-Zustände
HEATER_HVAC_ACTIONS: Final[Dict[int, str]] = {
    0: HVACAction.IDLE,     # AUTO (nicht an)
    1: HVACAction.HEATING,  # AUTO (an)
    2: HVACAction.IDLE,     # AUS durch Regelregel
    3: HVACAction.HEATING,  # EIN durch Notfallregel
    4: HVACAction.HEATING,  # MANUAL ON
    5: HVACAction.IDLE,     # AUS durch Notfallregel
    6: HVACAction.OFF,      # MANUAL OFF
}

# Feature-IDs für die verschiedenen Climate-Typen
CLIMATE_FEATURE_MAP: Final[Dict[str, str]] = {
    "HEATER": "heating",
    "SOLAR": "solar",
}

# Sensorkeys für die Wassertemperatur
WATER_TEMP_SENSORS: Final[List[str]] = [
    "onewire1_value",    # Standardsensor
    "water_temp",        # Alternative
    "WATER_TEMPERATURE", # Alternative
    "temp_value",        # Alternative
]


@dataclass
class VioletClimateEntityDescription(ClimateEntityDescription):
    """Class describing Violet Pool climate entities."""

    feature_id: Optional[str] = None


class VioletClimateEntity(VioletPoolControllerEntity, ClimateEntity):
    """Repräsentiert die Heizungs- oder Absorbersteuerung des Violet Pool Controllers."""

    # Klassen-Attribute für Climate-Features
    _attr_temperature_unit: ClassVar[str] = UnitOfTemperature.CELSIUS
    _attr_supported_features: ClassVar[int] = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes: ClassVar[List[str]] = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_min_temp: ClassVar[float] = 20.0
    _attr_max_temp: ClassVar[float] = 35.0
    _attr_target_temperature_step: ClassVar[float] = 0.5

    entity_description: VioletClimateEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        climate_type: str,  # "HEATER" oder "SOLAR"
    ):
        """Initialisiere die Climate-Entity.
        
        Args:
            coordinator: Der Daten-Koordinator
            config_entry: Die Config Entry des Geräts
            climate_type: Art der Heizung ("HEATER" oder "SOLAR")
        """
        # Wichtig: climate_type vor dem super().__init__ setzen
        self.climate_type = climate_type
        
        # Name und Icon bestimmen
        if climate_type == "HEATER":
            name = "Heizung"
            icon = "mdi:radiator"
        else:  # SOLAR
            name = "Solarabsorber"
            icon = "mdi:solar-power"
        
        # Feature-ID bestimmen
        feature_id = CLIMATE_FEATURE_MAP.get(climate_type)
        
        # EntityDescription erstellen
        entity_description = VioletClimateEntityDescription(
            key=climate_type,
            name=name,
            icon=icon,
            feature_id=feature_id,
        )
        
        # Initialisiere die Basisklasse
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_description=entity_description,
        )
        
        # Initialer Zustand
        self._attr_target_temperature = self._get_target_temperature()
        self._attr_hvac_mode = self._get_hvac_mode()
        
        self._logger.debug(
            "Climate-Entität für %s initialisiert mit Target: %.1f°C, Modus: %s",
            self.climate_type,
            self._attr_target_temperature,
            self._attr_hvac_mode
        )

    def _get_target_temperature(self) -> float:
        """Hole die Zieltemperatur aus den Coordinator-Daten.
        
        Returns:
            float: Die Zieltemperatur in °C
        """
        if self.climate_type == "HEATER":
            # Heizungs-Solltemperatur aus API-Daten
            return self.get_float_value("HEATER_TARGET_TEMP", 28.0)
        else:  # SOLAR
            # Solar-Solltemperatur aus API-Daten
            return self.get_float_value("SOLAR_TARGET_TEMP", 28.0)

    def _get_hvac_mode(self) -> str:
        """Ermittle den aktuellen HVAC-Modus.
        
        Returns:
            str: Der aktuelle HVAC-Modus (HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO)
        """
        # Hole den Status aus den API-Daten
        state = self.get_int_value(self.climate_type, 0)
        
        # Konvertiere Status in HVAC-Modus
        return HEATER_HVAC_MODES.get(state, HVACMode.OFF)

    def _update_from_coordinator(self) -> None:
        """Aktualisiere den Zustand der Climate-Entity anhand der Coordinator-Daten."""
        # Aktualisiere Zieltemperatur und HVAC-Modus
        self._attr_target_temperature = self._get_target_temperature()
        self._attr_hvac_mode = self._get_hvac_mode()
    
    @property
    def hvac_action(self) -> Optional[str]:
        """Gib die aktuelle HVAC-Aktion zurück.
        
        Returns:
            Optional[str]: Die aktuelle HVAC-Aktion
        """
        # Hole den Status aus den API-Daten
        state = self.get_int_value(self.climate_type, 0)
        
        # Konvertiere Status in HVAC-Aktion
        return HEATER_HVAC_ACTIONS.get(state, HVACAction.IDLE)

    @property
    def current_temperature(self) -> Optional[float]:
        """Gib die aktuelle Wassertemperatur zurück.
        
        Returns:
            Optional[float]: Die aktuelle Wassertemperatur in °C
        """
        # Versuche, die Wassertemperatur aus verschiedenen möglichen Sensorkeys zu lesen
        for sensor_key in WATER_TEMP_SENSORS:
            value = self.get_float_value(sensor_key, None)
            if value is not None:
                return value
                
        # Falls keine Temperatur gefunden wurde
        return None

    async def async_set_temperature(self, **kwargs) -> None:
        """Setze die Zieltemperatur.
        
        Args:
            **kwargs: Keyword-Argumente, insbesondere ATTR_TEMPERATURE
        """
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
            
        # Temperatur validieren
        if temperature < self.min_temp or temperature > self.max_temp:
            self._logger.warning(
                "Angeforderte Temperatur %.1f liegt außerhalb des zulässigen Bereichs (%.1f-%.1f)",
                temperature, self.min_temp, self.max_temp
            )
            return
            
        try:
            # Temperatur auf eine Dezimalstelle runden
            temperature = round(temperature, 1)
            
            self._logger.info(
                "Setze %s Zieltemperatur auf %.1f°C",
                "Heizung" if self.climate_type == "HEATER" else "Solar",
                temperature
            )
            
            # Bestimme den API-Endpunkt
            endpoint = "/set_temperature"
            
            # Bereite die Kommandodaten vor
            command = {
                "type": self.climate_type,
                "temperature": temperature
            }
            
            # Sende das Kommando über die Device-API
            result = await self.device.async_send_command(endpoint, command)
            
            # Prüfe das Ergebnis
            if isinstance(result, dict) and result.get("success", False):
                # Lokal aktualisieren ohne auf API-Refresh zu warten
                self._attr_target_temperature = temperature
                self.async_write_ha_state()
                
                # Daten vom Gerät neu laden
                await self.coordinator.async_request_refresh()
            else:
                self._logger.error(
                    "Fehler beim Setzen der Temperatur: Ungültige Antwort: %s",
                    result
                )
                
        except Exception as err:
            self._logger.error("Fehler beim Setzen der Temperatur: %s", err)

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Setze den HVAC-Modus (OFF, HEAT, AUTO).
        
        Args:
            hvac_mode: Der zu setzende HVAC-Modus
        """
        try:
            # API-Key und Aktion bestimmen
            api_key = self.climate_type
            action = None
            
            if hvac_mode == HVACMode.HEAT:
                action = "ON"  # MANUAL ON
            elif hvac_mode == HVACMode.OFF:
                action = "OFF"  # MANUAL OFF
            elif hvac_mode == HVACMode.AUTO:
                action = "AUTO"  # AUTO mode
            else:
                self._logger.warning("Nicht unterstützter HVAC-Modus: %s", hvac_mode)
                return
                
            self._logger.info(
                "Setze %s-Modus auf %s",
                "Heizung" if self.climate_type == "HEATER" else "Solar",
                action
            )
            
            # Bereite das Kommando vor
            command = {
                "id": api_key,
                "action": action,
                "duration": 0  # permanent
            }
            
            # Sende das Kommando über die Device-API
            result = await self.device.async_send_command("/set_switch", command)
            
            # Prüfe das Ergebnis
            if isinstance(result, dict) and result.get("success", False):
                # Lokal aktualisieren ohne auf API-Refresh zu warten
                self._attr_hvac_mode = hvac_mode
                self.async_write_ha_state()
                
                # Daten vom Gerät neu laden
                await self.coordinator.async_request_refresh()
            else:
                self._logger.error(
                    "Fehler beim Setzen des HVAC-Modus: Ungültige Antwort: %s",
                    result
                )
                
        except Exception as err:
            self._logger.error("Fehler beim Setzen des HVAC-Modus: %s", err)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Climate-Entities basierend auf dem Config-Entry ein.
    
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
    
    entities = []
    
    # Prüfe, ob Heizung vorhanden ist (Feature-Check deaktiviert)
    if "HEATER" in coordinator.data:
        entities.append(VioletClimateEntity(coordinator, config_entry, "HEATER"))
    
    # Prüfe, ob Solarabsorber vorhanden ist (Feature-Check deaktiviert)
    if "SOLAR" in coordinator.data:
        entities.append(VioletClimateEntity(coordinator, config_entry, "SOLAR"))
    
    if entities:
        async_add_entities(entities)
        _LOGGER.info("%d Climate-Entities hinzugefügt", len(entities))
    else:
        _LOGGER.info(
            "Keine Heizungs- oder Solarabsorber-Daten gefunden, " 
            "Climate-Entities werden nicht hinzugefügt"
        )
