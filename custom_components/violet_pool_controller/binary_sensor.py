"""Binary Sensor Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, List, Optional, cast
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
    "COVER_STATE": "cover_control",
    "REFILL": "water_refill",
    "PVSURPLUS": "pv_surplus",
}

@dataclass
class VioletBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Violet Pool binary sensor entities."""

    feature_id: Optional[str] = None


class VioletBinarySensor(VioletPoolControllerEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    entity_description: VioletBinarySensorEntityDescription

    def __init__(
        self, 
        coordinator: VioletPoolDataUpdateCoordinator, 
        config_entry: ConfigEntry,
        description: VioletBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor.
        
        Args:
            coordinator: Der Daten-Koordinator
            config_entry: Die Config Entry des Geräts
            description: Die Beschreibung der Entität
        """
        # Initialisiere die Basisklasse
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_description=description,
        )
        
        # Icon-Basis für Zustandsänderungen
        self._icon_base = description.icon
        
        # Tracking für Logging
        self._has_logged_none_state = False
        
        _LOGGER.debug(
            "Initialisiere Binary Sensor: %s (unique_id=%s, feature_id=%s)",
            self.entity_id,
            self._attr_unique_id,
            getattr(self.entity_description, "feature_id", None)
        )

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        result = self._get_sensor_state()
        _LOGGER.debug("Binary Sensor %s is_on=%s", self.entity_id, result)
        return result

    @property
    def icon(self) -> str:
        """Return the icon for the binary sensor, changing based on state."""
        return self._icon_base if self.is_on else f"{self._icon_base}-off"

    def _get_sensor_state(self) -> bool:
        """Hilfsmethode zum Abrufen und Mappen des aktuellen Sensorzustands von der API."""
        key = self.entity_description.key
            
        # Standardverhalten: Verwende die get_bool_value-Methode aus der Basis-Entity
        raw_state = self.get_str_value(key, "")
        _LOGGER.debug("Binary Sensor %s raw_state=%s", self.entity_id, raw_state)
        
        if not raw_state:
            if not self._has_logged_none_state:
                self._logger.debug(
                    "Binary Sensor '%s' returned None/empty as its state. Defaulting to 'OFF'.",
                    key
                )
                self._has_logged_none_state = True
            return False
            
        # Konvertiere den Wert mit der STATE_MAP
        if raw_state.upper() in STATE_MAP:
            mapped_state = STATE_MAP[raw_state.upper()]
            _LOGGER.debug("Binary Sensor %s mapped_state=%s", self.entity_id, mapped_state)
            return mapped_state
            
        # Versuche direkte Boolsche Konvertierung als Fallback
        bool_state = self.get_bool_value(key, False)
        _LOGGER.debug("Binary Sensor %s bool_state=%s", self.entity_id, bool_state)
        return bool_state


# Eine völlig eigenständige Implementierung für den Cover-Closed Sensor
class CoverIsClosedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Spezieller eigenständiger Sensor für den Cover-Geschlossen-Status."""

    def __init__(
        self, 
        coordinator: VioletPoolDataUpdateCoordinator, 
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the cover closed sensor.
        
        Args:
            coordinator: Der Daten-Koordinator
            config_entry: Die Config Entry des Geräts
        """
        super().__init__(coordinator)
        
        # Entity-Attribute
        self._attr_has_entity_name = True
        self._attr_name = "Cover Geschlossen"
        self._attr_unique_id = f"{config_entry.entry_id}_cover_is_closed"
        self._attr_device_class = BinarySensorDeviceClass.DOOR
        self._attr_icon = "mdi:window-shutter"
        
        # Geräteinformationen vom Geräteobjekt übernehmen
        self._attr_device_info = coordinator.device.device_info
        
        # Logger
        self._logger = logging.getLogger(f"{DOMAIN}.{self._attr_unique_id}")
        self._logger.info("Initialisiere Cover-Geschlossen Sensor: %s", self._attr_unique_id)

    @property
    def available(self) -> bool:
        """Gibt an, ob die Entität verfügbar ist."""
        # Wir sind verfügbar, solange der Coordinator funktioniert und "cover_control" aktiv ist
        feature_active = self.coordinator.device.is_feature_active("cover_control")
        return self.coordinator.last_update_success and feature_active

    @property
    def is_on(self) -> bool:
        """Return True if the cover is closed."""
        if not self.coordinator.data:
            _LOGGER.debug("Cover-Geschlossen Sensor: Keine Daten verfügbar")
            return False
            
        data = self.coordinator.data
        
        # Für Debugging: Alle relevanten Daten ausgeben
        debug_data = {
            "COVER_STATE": data.get("COVER_STATE"),
            "COVER_OPEN": data.get("COVER_OPEN"),
            "COVER_CLOSE": data.get("COVER_CLOSE"),
            "LAST_MOVING_DIRECTION": data.get("LAST_MOVING_DIRECTION")
        }
        _LOGGER.debug("Cover-Geschlossen Sensor Debug-Daten: %s", debug_data)
        
        # Es gibt verschiedene Möglichkeiten, wie der Abdeckungsstatus repräsentiert werden kann
        cover_state = data.get("COVER_STATE")
        if cover_state in ["CLOSED", "2", 2]:
            _LOGGER.debug("Cover-Geschlossen Sensor: Status CLOSED erkannt")
            return True
        
        # Alternativer Pfad: COVER_OPEN / COVER_CLOSE Status - nur wenn die Daten vorhanden sind
        if "COVER_OPEN" in data and "COVER_CLOSE" in data:
            cover_open = data.get("COVER_OPEN")
            cover_close = data.get("COVER_CLOSE")
            
            if cover_open in ["OFF", "0", 0, False] and cover_close in ["ON", "1", 1, True]:
                _LOGGER.debug("Cover-Geschlossen Sensor: COVER_OPEN=OFF und COVER_CLOSE=ON erkannt")
                return True
            
        _LOGGER.debug("Cover-Geschlossen Sensor: Abdeckung ist NICHT geschlossen")
        return False

    @property 
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Gibt zusätzliche Zustandsattribute zurück."""
        attributes = {
            "feature_id": "cover_control",
            "last_updated": self.coordinator.last_update_success,
        }
        
        # Füge Rohwerte hinzu, wenn vorhanden
        if self.coordinator.data:
            data = self.coordinator.data
            if "COVER_STATE" in data:
                attributes["cover_state"] = data["COVER_STATE"]
            if "COVER_OPEN" in data:
                attributes["cover_open"] = data["COVER_OPEN"]
            if "COVER_CLOSE" in data:
                attributes["cover_close"] = data["COVER_CLOSE"]
            if "LAST_MOVING_DIRECTION" in data:
                attributes["last_moving_direction"] = data["LAST_MOVING_DIRECTION"]
                
        return attributes


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Violet Device binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Debug: Ausgabe des Coordinator-Status
    _LOGGER.debug(
        "Binary Sensor Setup: Coordinator Status - available=%s, last_update_success=%s",
        coordinator.device.available,
        coordinator.last_update_success,
    )
    
    # Hole aktive Features
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, 
        config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    _LOGGER.debug("Binary Sensor Setup: Aktive Features=%s", active_features)

    # Verfügbare Daten aus der API
    available_data_keys = set(coordinator.data.keys())
    _LOGGER.debug(
        "Binary Sensor Setup: %d verfügbare API-Daten-Keys (erste 10): %s",
        len(available_data_keys),
        list(available_data_keys)[:10]
    )
    
    # Liste für alle zu erstellenden Binary Sensors
    binary_sensors: List[BinarySensorEntity] = []
    
    # Erzeugen regulärer Binary Sensors basierend auf der Definition
    for sensor in BINARY_SENSORS:
        key = sensor["key"]
        
        # Prüfe, ob der Sensor in den API-Daten vorhanden ist
        if key not in available_data_keys:
            _LOGGER.debug("Binary Sensor %s nicht in API-Daten gefunden, wird übersprungen", key)
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
        description = VioletBinarySensorEntityDescription(
            key=key,
            name=sensor["name"],
            icon=sensor["icon"],
            device_class=device_class,
            entity_category=EntityCategory(entity_category) if entity_category else None,
            feature_id=feature_id,
        )
        
        _LOGGER.debug("Binary Sensor %s erstellen (Feature %s)", key, feature_id)
        
        # Sensor erstellen
        binary_sensors.append(
            VioletBinarySensor(
                coordinator=coordinator, 
                config_entry=config_entry,
                description=description,
            )
        )
    
    # Spezialbehandlung: Cover-geschlossen Sensor
    if "COVER_STATE" in available_data_keys and "cover_control" in active_features:
        _LOGGER.debug("Cover-Geschlossen Sensor wird erstellt (Feature cover_control)")
        # Verwende hier den komplett eigenständigen Sensor
        binary_sensors.append(
            CoverIsClosedBinarySensor(
                coordinator=coordinator, 
                config_entry=config_entry,
            )
        )
    else:
        _LOGGER.warning(
            "Cover-Geschlossen Sensor NICHT erstellt. COVER_STATE in Daten: %s, cover_control aktiv: %s",
            "COVER_STATE" in available_data_keys,
            "cover_control" in active_features
        )
    
    # PV Überschuss Status
    if "PVSURPLUS" in available_data_keys and "pv_surplus" in active_features:
        _LOGGER.debug("PV-Überschuss Sensor wird erstellt (Feature pv_surplus)")
        description = VioletBinarySensorEntityDescription(
            key="PVSURPLUS",
            name="PV Überschuss Aktiv",
            icon="mdi:solar-power",
            feature_id="pv_surplus",
        )
        
        binary_sensors.append(
            VioletBinarySensor(
                coordinator=coordinator, 
                config_entry=config_entry,
                description=description,
            )
        )
    
    # Zur Meldung der Anzahl an hinzugefügten Sensoren    
    if binary_sensors:
        _LOGGER.info(
            "%d Binary Sensoren gefunden und werden hinzugefügt: %s", 
            len(binary_sensors),
            [sensor.entity_id if hasattr(sensor, 'entity_id') else sensor._attr_name for sensor in binary_sensors]
        )
        async_add_entities(binary_sensors)
    else:
        _LOGGER.warning("Keine passenden Binary Sensoren in den API-Daten gefunden.")