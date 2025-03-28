"""Number Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Final, List, cast
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
    NumberDeviceClass,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
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

# Sollwerte-Definitionen
SETPOINT_DEFINITIONS: Final = [
    {
        "key": "ph_setpoint",
        "name": "pH Sollwert",
        "min_value": 6.8,
        "max_value": 7.8,
        "step": 0.1,
        "icon": "mdi:flask",
        "api_key": "pH",  # Für API-Aufrufe
        "feature_id": "ph_control",  # Feature-ID für Aktivierung
        "parameter": "pH Sollwert",  # Parameter-Name in der API
        "unit_of_measurement": "pH",
        "api_endpoint": "/set_target_value",  # Endpunkt für die API
        "device_class": NumberDeviceClass.PH,
        "entity_category": EntityCategory.CONFIG,
    },
    {
        "key": "chlorine_setpoint",
        "name": "Redox Sollwert",
        "min_value": 600,
        "max_value": 850,
        "step": 10,
        "icon": "mdi:flash",
        "api_key": "ORP",  # Für API-Aufrufe
        "feature_id": "chlorine_control",  # Feature-ID für Aktivierung
        "parameter": "Redox Sollwert",  # Parameter-Name in der API
        "unit_of_measurement": "mV",
        "api_endpoint": "/set_target_value",  # Endpunkt für die API
        "entity_category": EntityCategory.CONFIG,
    },
    {
        "key": "min_chlorine_level",
        "name": "Min. Chlorgehalt",
        "min_value": 0.1,
        "max_value": 0.5,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "MinChlorine",  # Für API-Aufrufe
        "feature_id": "chlorine_control",  # Feature-ID für Aktivierung
        "parameter": "Min. Chlorgehalt",  # Parameter-Name in der API
        "unit_of_measurement": "mg/l",
        "api_endpoint": "/set_target_value",  # Endpunkt für die API
        "entity_category": EntityCategory.CONFIG,
    },
    {
        "key": "max_chlorine_level_day",
        "name": "Max. Chlorgehalt Tag",
        "min_value": 0.3,
        "max_value": 0.8,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "MaxChlorineDay",  # Für API-Aufrufe
        "feature_id": "chlorine_control",  # Feature-ID für Aktivierung
        "parameter": "Max. Chlorgehalt Tag",  # Parameter-Name in der API
        "unit_of_measurement": "mg/l",
        "api_endpoint": "/set_target_value",  # Endpunkt für die API
        "entity_category": EntityCategory.CONFIG,
    },
    {
        "key": "max_chlorine_level_night",
        "name": "Max. Chlorgehalt Nacht",
        "min_value": 0.5,
        "max_value": 1.2,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "MaxChlorineNight",  # Für API-Aufrufe
        "feature_id": "chlorine_control",  # Feature-ID für Aktivierung
        "parameter": "Max. Chlorgehalt Nacht",  # Parameter-Name in der API
        "unit_of_measurement": "mg/l",
        "api_endpoint": "/set_target_value",  # Endpunkt für die API
        "entity_category": EntityCategory.CONFIG,
    },
]

# Mapping der Keys zu den tatsächlichen API-Datenfeldern
KEY_TO_DATA_FIELD: Final[Dict[str, str]] = {
    "ph_setpoint": "pH_SETPOINT",
    "chlorine_setpoint": "REDOX_SETPOINT",
    "min_chlorine_level": "MIN_CHLORINE_LEVEL",
    "max_chlorine_level_day": "MAX_CHLORINE_LEVEL_DAY",
    "max_chlorine_level_night": "MAX_CHLORINE_LEVEL_NIGHT",
}

# Default-Werte für den Fall, dass die Daten nicht verfügbar sind
DEFAULT_VALUES: Final[Dict[str, float]] = {
    "ph_setpoint": 7.2,
    "chlorine_setpoint": 750.0,
    "min_chlorine_level": 0.2,
    "max_chlorine_level_day": 0.5,
    "max_chlorine_level_night": 0.8,
}


@dataclass
class VioletNumberEntityDescription(NumberEntityDescription):
    """Class describing Violet Pool number entities."""

    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    parameter: Optional[str] = None
    feature_id: Optional[str] = None


class VioletNumberEntity(VioletPoolControllerEntity, NumberEntity):
    """Repräsentiert einen Sollwert im Violet Pool Controller."""

    entity_description: VioletNumberEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        definition: Dict[str, Any],
    ):
        """Initialisiere die Number-Entity.
        
        Args:
            coordinator: Der Daten-Koordinator
            config_entry: Die Config Entry des Geräts
            definition: Die Definition des Sollwerts
        """
        # Erstelle eine angepasste EntityDescription mit allen benötigten Feldern
        description = VioletNumberEntityDescription(
            key=definition["key"],
            name=definition["name"],
            icon=definition.get("icon"),
            device_class=definition.get("device_class"),
            native_unit_of_measurement=definition.get("unit_of_measurement"),
            entity_category=definition.get("entity_category"),
            api_key=definition.get("api_key"),
            api_endpoint=definition.get("api_endpoint"),
            parameter=definition.get("parameter"),
            feature_id=definition.get("feature_id"),
        )
        
        # Initialisiere die Basisklasse
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_description=description,
        )
        
        # Number-spezifische Attribute
        self._definition = definition
        self._attr_native_min_value = definition.get("min_value")
        self._attr_native_max_value = definition.get("max_value")
        self._attr_native_step = definition.get("step")
        self._attr_mode = NumberMode.AUTO
        
        # Initialen Wert setzen
        self._attr_native_value = self._get_current_value()
        
        self._logger.debug(
            "Number-Entity für %s initialisiert mit Wert: %s %s", 
            definition["name"],
            self._attr_native_value,
            self._attr_native_unit_of_measurement or ""
        )

    def _update_from_coordinator(self) -> None:
        """Aktualisiert den Zustand der Number-Entity anhand der Coordinator-Daten."""
        self._attr_native_value = self._get_current_value()

    def _get_current_value(self) -> Optional[float]:
        """Ermittle den aktuellen Wert aus den Coordinator-Daten.
        
        Returns:
            Optional[float]: Der aktuelle Wert oder None, wenn nicht verfügbar
        """
        key = self._definition["key"]
        
        # Datenfeld aus dem Mapping holen
        data_field = KEY_TO_DATA_FIELD.get(key)
        
        # Versuche den Wert aus den Coordinator-Daten zu bekommen
        if data_field:
            value = self.get_float_value(data_field, None)
            if value is not None:
                return value
                
        # Spezielle Behandlung für bestimmte Sollwerte
        if key == "ph_setpoint":
            # Versuche alternative Feldnamen für pH-Sollwert
            alternatives = ["pH_TARGET", "TARGET_PH"]
            for alt_field in alternatives:
                value = self.get_float_value(alt_field, None)
                if value is not None:
                    return value
                    
        if key == "chlorine_setpoint":
            # Versuche alternative Feldnamen für Redox-Sollwert
            alternatives = ["ORP_TARGET", "TARGET_ORP", "REDOX_TARGET"]
            for alt_field in alternatives:
                value = self.get_float_value(alt_field, None)
                if value is not None:
                    return value
        
        # Fallback zu Default-Wert
        default_value = DEFAULT_VALUES.get(key, self._attr_native_min_value)
        self._logger.debug(
            "Verwende Standard-Wert für %s: %s", 
            key, 
            default_value
        )
        return default_value

    async def async_set_native_value(self, value: float) -> None:
        """Setze den neuen Wert im Gerät.
        
        Args:
            value: Der neue Wert
        """
        try:
            api_key = self.entity_description.api_key
            api_endpoint = self.entity_description.api_endpoint
            
            if not api_key or not api_endpoint:
                self._logger.error(
                    "Fehler: API-Key oder Endpunkt nicht definiert für %s", 
                    self.entity_id
                )
                return
                
            # Runde Werte entsprechend der Schrittgröße
            if self._attr_native_step:
                value = round(value / self._attr_native_step) * self._attr_native_step
                # Für Werte mit Dezimalstellen: auf 2 Dezimalstellen runden
                if self._attr_native_step < 1:
                    value = round(value, 2)
                    
            self._logger.info(
                "Setze Sollwert für %s: %s = %s %s",
                self.name,
                api_key,
                value,
                self._attr_native_unit_of_measurement or ""
            )
            
            # Bereite das Kommando vor
            command = {
                "target_type": api_key,
                "value": value
            }
            
            # Sende den Befehl über die Device-API
            result = await self.device.async_send_command(api_endpoint, command)
            
            # Prüfe das Ergebnis
            if isinstance(result, dict) and result.get("success", False):
                self._logger.debug(
                    "Sollwert erfolgreich gesetzt: %s = %s", 
                    api_key, 
                    value
                )
            else:
                self._logger.warning(
                    "Sollwert möglicherweise nicht erfolgreich gesetzt: %s", 
                    result
                )
            
            # Aktualisiere den lokalen Wert ohne auf den Coordinator zu warten
            self._attr_native_value = value
            self.async_write_ha_state()
            
            # Aktualisiere die Daten vom Gerät
            await self.coordinator.async_request_refresh()
            
        except Exception as err:
            self._logger.error("Fehler beim Setzen des Sollwerts: %s", err)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Number-Entities basierend auf dem Config-Entry ein.
    
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
    
    # Erstelle Number-Entities für alle passenden Definitionen
    entities: List[VioletNumberEntity] = []
    
    for definition in SETPOINT_DEFINITIONS:
        # Prüfe, ob das Feature aktiv ist
        feature_id = definition.get("feature_id")
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Number-Entity für %s wird übersprungen, da Feature %s nicht aktiv ist",
                definition["name"],
                feature_id
            )
            continue
        
        # Prüfe, ob relevante Daten in der API vorhanden sind
        key = definition["key"]
        data_field = KEY_TO_DATA_FIELD.get(key)
        
        # Zusätzliche Indikatoren für spezifische Sollwerte
        key_specific_indicators = {
            "ph_setpoint": ["pH_value", "pH_TARGET", "DOS_4_PHM", "DOS_5_PHP"],
            "chlorine_setpoint": ["orp_value", "ORP_TARGET", "DOS_1_CL", "pot_value"],
            "min_chlorine_level": ["CHLORINE_LEVEL", "pot_value", "DOS_1_CL"],
            "max_chlorine_level_day": ["CHLORINE_LEVEL", "pot_value", "DOS_1_CL"],
            "max_chlorine_level_night": ["CHLORINE_LEVEL", "pot_value", "DOS_1_CL"],
        }
        
        # Prüfe, ob irgendein relevanter Indikator in den Daten existiert
        should_add = False
        
        # Zuerst prüfen, ob das direkte Datenfeld existiert
        if data_field and data_field in coordinator.data:
            should_add = True
        else:
            # Dann prüfen, ob alternative Indikatoren existieren
            for indicator in key_specific_indicators.get(key, []):
                if indicator in coordinator.data:
                    should_add = True
                    break
        
        if should_add:
            entities.append(VioletNumberEntity(coordinator, config_entry, definition))
            _LOGGER.debug("Number-Entity für %s hinzugefügt", definition["name"])
        else:
            _LOGGER.debug(
                "Number-Entity für %s wird übersprungen (keine relevanten Daten)",
                definition["name"]
            )
    
    if entities:
        _LOGGER.info("%d Number-Entities für Sollwerte hinzugefügt", len(entities))
        async_add_entities(entities)
    else:
        _LOGGER.info(
            "Keine passenden Sollwert-Entities in den API-Daten gefunden oder keine aktiven Features"
        )