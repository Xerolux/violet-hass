"""Binary Sensor Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, List, Optional, cast

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN, 
    BINARY_SENSORS, 
    STATE_MAP,
    CONF_ACTIVE_FEATURES,
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Mapping von Binary Sensor Keys zu Feature-IDs
BINARY_SENSOR_FEATURE_MAP = {
    "PUMP": "filter_control",
    "HEATER": "heating",
    "SOLAR": "solar",
    "LIGHT": "led_lighting",
    "BACKWASH": "backwash",
    "BACKWASHRINSE": "backwash",
    "DOS_1_CL": "chlorine_control",
    "DOS_4_PHM": "ph_control",
    "DOS_5_PHP": "ph_control",
    "DOS_6_FLOC": "chlorine_control",
    "COVER_OPEN": "cover_control",
    "COVER_CLOSE": "cover_control",
    "COVER_IS_CLOSED": "cover_control",
    "COVER_STATE": "cover_control",
    "REFILL": "water_refill",
    "PVSURPLUS": "pv_surplus",
}


class VioletBinarySensor(VioletPoolControllerEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    def __init__(
        self, 
        coordinator: VioletPoolDataUpdateCoordinator, 
        config_entry: ConfigEntry,
        description: BinarySensorEntityDescription,
        feature_id: Optional[str] = None,
        transform_fn: Optional[callable] = None,
    ) -> None:
        """Initialize the binary sensor.
        
        Args:
            coordinator: Der Daten-Koordinator
            config_entry: Die Config Entry des Geräts
            description: Die Beschreibung der Entität
            feature_id: Optional feature ID to check availability
            transform_fn: Optionale Funktion zur Transformation des Zustands
        """
        # Füge feature_id zur EntityDescription hinzu wenn vorhanden
        if feature_id:
            setattr(description, "feature_id", feature_id)
            
        # Initialisiere die Basisklasse
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_description=description,
        )
        
        # Icon-Basis für Zustandsänderungen
        self._icon_base = description.icon
        
        # Funktion zur Transformation des Zustands
        self._transform_fn = transform_fn
        
        # Tracking für Logging
        self._has_logged_none_state = False

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        return self._get_sensor_state()

    @property
    def icon(self) -> str:
        """Return the icon for the binary sensor, changing based on state."""
        return self._icon_base if self.is_on else f"{self._icon_base}-off"

    def _get_sensor_state(self) -> bool:
        """Hilfsmethode zum Abrufen und Mappen des aktuellen Sensorzustands von der API."""
        key = self.entity_description.key
        
        # Wenn eine Transformationsfunktion definiert ist, verwende diese
        if self._transform_fn:
            return self._transform_fn(self.coordinator.data)
            
        # Standardverhalten: Verwende die get_bool_value-Methode aus der Basis-Entity
        raw_state = self.get_str_value(key, "")
        
        if not raw_state:
            if not self._has_logged_none_state:
                self._logger.warning(
                    "Binary Sensor '%s' returned None/empty as its state. Defaulting to 'OFF'.",
                    key
                )
                self._has_logged_none_state = True
            return False
            
        # Konvertiere den Wert mit der STATE_MAP
        if raw_state.upper() in STATE_MAP:
            return STATE_MAP[raw_state.upper()]
            
        # Versuche direkte Boolsche Konvertierung als Fallback
        return self.get_bool_value(key, False)


# Spezielle Transformationsfunktionen für bestimmte Sensoren
def cover_is_closed(data: Dict[str, Any]) -> bool:
    """Bestimmt, ob die Abdeckung geschlossen ist.
    
    Args:
        data: Die API-Daten
        
    Returns:
        bool: True, wenn die Abdeckung geschlossen ist
    """
    # Es gibt verschiedene Möglichkeiten, wie der Abdeckungsstatus repräsentiert werden kann
    cover_state = data.get("COVER_STATE")
    if cover_state in ["CLOSED", "2", 2]:
        return True
        
    # Alternativer Pfad: COVER_OPEN / COVER_CLOSE Status
    if data.get("COVER_OPEN") in ["OFF", "0", 0, False] and data.get("COVER_CLOSE") in ["ON", "1", 1, True]:
        return True
        
    return False


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Violet Device binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Hole aktive Features
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, 
        config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )

    # Verfügbare Daten aus der API
    available_data_keys = set(coordinator.data.keys())
    
    # Liste für alle zu erstellenden Binary Sensors
    binary_sensors: List[VioletBinarySensor] = []
    
    # Erzeugen regulärer Binary Sensors basierend auf der Definition
    for sensor in BINARY_SENSORS:
        key = sensor["key"]
        
        # Prüfe, ob der Sensor in den API-Daten vorhanden ist
        if key not in available_data_keys:
            continue
            
        # Prüfe, ob das zugehörige Feature aktiv ist
        feature_id = BINARY_SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Binary Sensor %s wird übersprungen, da Feature %s nicht aktiv ist",
                key,
                feature_id
            )
            continue
            
        # Bestimme die richtige device_class basierend auf dem Sensor-Typ
        device_class = None
        if key in ["PUMP", "SOLAR", "HEATER"]:
            device_class = BinarySensorDeviceClass.RUNNING
        elif key == "LIGHT":
            device_class = BinarySensorDeviceClass.LIGHT
        elif key in ["COVER_OPEN", "COVER_CLOSE"]:
            device_class = BinarySensorDeviceClass.OPENING
        elif key in ["REFILL"]:
            device_class = BinarySensorDeviceClass.MOISTURE
        
        # Bestimme die Entity Category basierend auf dem Sensor-Typ
        entity_category = None
        if key.startswith("DOS_"):
            entity_category = EntityCategory.DIAGNOSTIC
            
        # Erstelle EntityDescription
        description = BinarySensorEntityDescription(
            key=key,
            name=sensor["name"],
            icon=sensor["icon"],
            device_class=device_class,
            entity_category=EntityCategory(entity_category) if entity_category else None,
        )
        
        # Sensor erstellen
        binary_sensors.append(
            VioletBinarySensor(
                coordinator=coordinator, 
                config_entry=config_entry,
                description=description,
                feature_id=feature_id,
            )
        )
    
    # Zusätzlich: Spezifische Sensoren basierend auf API-Daten hinzufügen
    
    # Cover Status (Kombination aus mehreren Zuständen)
    cover_keys = ["COVER_STATE", "COVER_OPEN", "COVER_CLOSE"]
    if any(key in available_data_keys for key in cover_keys) and "cover_control" in active_features:
        description = BinarySensorEntityDescription(
            key="COVER_IS_CLOSED",  # Dies ist ein spezieller Key für die Logik
            name="Cover Geschlossen",
            icon="mdi:window-shutter",
            device_class=BinarySensorDeviceClass.DOOR,
        )
        
        binary_sensors.append(
            VioletBinarySensor(
                coordinator=coordinator, 
                config_entry=config_entry,
                description=description,
                feature_id="cover_control",
                transform_fn=cover_is_closed,
            )
        )
    
    # PV Überschuss Status
    if "PVSURPLUS" in available_data_keys and "pv_surplus" in active_features:
        description = BinarySensorEntityDescription(
            key="PVSURPLUS",
            name="PV Überschuss Aktiv",
            icon="mdi:solar-power",
        )
        
        binary_sensors.append(
            VioletBinarySensor(
                coordinator=coordinator, 
                config_entry=config_entry,
                description=description,
                feature_id="pv_surplus",
            )
        )
    
    # Zur Meldung der Anzahl an hinzugefügten Sensoren    
    if binary_sensors:
        _LOGGER.info(f"{len(binary_sensors)} Binary Sensoren gefunden und hinzugefügt.")
        async_add_entities(binary_sensors)
    else:
        _LOGGER.warning("Keine passenden Binary Sensoren in den API-Daten gefunden.")
