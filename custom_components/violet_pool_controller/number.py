"""Sensor Integration für den Violet Pool Controller."""
import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import UnitOfTemperature, UnitOfPressure, UnitOfLength, UnitOfVolumeFlowRate

from .const import (
    DOMAIN, TEMP_SENSORS, WATER_CHEM_SENSORS, ANALOG_SENSORS, CONF_ACTIVE_FEATURES
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Feature mapping for sensors
SENSOR_FEATURE_MAP = {
    # Temperature sensors
    "onewire1_value": None,  # Always show water temperature
    "onewire2_value": None,  # Always show air temperature
    "onewire3_value": "solar",
    "onewire4_value": "solar",
    "onewire5_value": "heating",
    "onewire6_value": "heating",
    # Water chemistry
    "pH_value": "ph_control",
    "orp_value": "chlorine_control",
    "pot_value": "chlorine_control",
    # Analog sensors
    "ADC1_value": "filter_control",
    "ADC2_value": "water_level",
    "IMP1_value": "filter_control",
    "IMP2_value": "filter_control",
}

@dataclass
class VioletSensorEntityDescription:
    """Beschreibung der Violet Pool Sensor-Entities."""
    key: str
    name: str
    icon: str | None = None
    unit_of_measurement: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    entity_category: EntityCategory | None = None
    feature_id: str | None = None
    suggested_display_precision: int | None = None

class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Repräsentation eines Violet Pool Sensors."""
    entity_description: VioletSensorEntityDescription

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry,
        description: VioletSensorEntityDescription
    ) -> None:
        """Initialisiere den Sensor."""
        super().__init__(coordinator, config_entry, description)
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_entity_category = description.entity_category
        self._attr_suggested_display_precision = description.suggested_display_precision
        _LOGGER.debug("Initialisiere Sensor: %s (unique_id=%s)", self.entity_id, self._attr_unique_id)

    @property
    def native_value(self) -> float | int | str | None:
        """Gibt den nativen Wert des Sensors zurück."""
        key = self.entity_description.key
        value = self.get_value(key)
        
        if value is None:
            return None
            
        # For numeric sensors, try to convert to appropriate type
        if self.entity_description.unit_of_measurement:
            try:
                # Convert to float for numeric values
                numeric_value = float(value)
                
                # Round based on precision requirements
                if self.entity_description.suggested_display_precision is not None:
                    return round(numeric_value, self.entity_description.suggested_display_precision)
                elif self.entity_description.key == "pH_value":
                    return round(numeric_value, 2)
                elif "temp" in key.lower() or "onewire" in key.lower():
                    return round(numeric_value, 1)
                else:
                    return numeric_value
                    
            except (ValueError, TypeError):
                return str(value)
        
        return value

def _create_sensor_descriptions() -> list[VioletSensorEntityDescription]:
    """Create sensor entity descriptions from sensor constants."""
    descriptions = []
    
    # Temperature sensors
    for key, config in TEMP_SENSORS.items():
        descriptions.append(VioletSensorEntityDescription(
            key=key,
            name=config["name"],
            icon=config["icon"],
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            feature_id=SENSOR_FEATURE_MAP.get(key),
            suggested_display_precision=1
        ))
    
    # Water chemistry sensors
    for key, config in WATER_CHEM_SENSORS.items():
        device_class = None
        if key == "pH_value":
            device_class = SensorDeviceClass.PH
        
        descriptions.append(VioletSensorEntityDescription(
            key=key,
            name=config["name"],
            icon=config["icon"],
            unit_of_measurement=config["unit"],
            device_class=device_class,
            state_class=SensorStateClass.MEASUREMENT,
            feature_id=SENSOR_FEATURE_MAP.get(key),
            suggested_display_precision=2 if key == "pH_value" else 0
        ))
    
    # Analog sensors
    for key, config in ANALOG_SENSORS.items():
        device_class = None
        state_class = SensorStateClass.MEASUREMENT
        
        if "druck" in config["name"].lower() or config["unit"] == "bar":
            device_class = SensorDeviceClass.PRESSURE
        elif "füllstand" in config["name"].lower() or config["unit"] == "cm":
            device_class = SensorDeviceClass.DISTANCE
        elif "durchfluss" in config["name"].lower() or "förderleistung" in config["name"].lower():
            device_class = SensorDeviceClass.VOLUME_FLOW_RATE
            
        descriptions.append(VioletSensorEntityDescription(
            key=key,
            name=config["name"],
            icon=config["icon"],
            unit_of_measurement=config["unit"],
            device_class=device_class,
            state_class=state_class,
            feature_id=SENSOR_FEATURE_MAP.get(key),
            suggested_display_precision=1
        ))
    
    # Additional diagnostic sensors
    descriptions.extend([
        VioletSensorEntityDescription(
            key="fw",
            name="Firmware Version",
            icon="mdi:information",
            entity_category=EntityCategory.DIAGNOSTIC
        ),
        VioletSensorEntityDescription(
            key="uptime",
            name="Uptime",
            icon="mdi:clock",
            unit_of_measurement="s",
            device_class=SensorDeviceClass.DURATION,
            entity_category=EntityCategory.DIAGNOSTIC
        ),
    ])
    
    return descriptions

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Sensors für die Config Entry ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    entities: list[SensorEntity] = []

    # Create sensor descriptions
    sensor_descriptions = _create_sensor_descriptions()

    for description in sensor_descriptions:
        # Check if feature is active (if feature_id is specified)
        if description.feature_id and description.feature_id not in active_features:
            _LOGGER.debug("Überspringe Sensor %s: Feature %s nicht aktiv", description.key, description.feature_id)
            continue
            
        # Check if data is available for this sensor
        if description.key not in coordinator.data:
            _LOGGER.debug("Überspringe Sensor %s: Keine Daten verfügbar", description.key)
            continue
            
        # Skip sensors with None/empty values (except diagnostic sensors)
        value = coordinator.data.get(description.key)
        if value is None or value == "" and description.entity_category != EntityCategory.DIAGNOSTIC:
            _LOGGER.debug("Überspringe Sensor %s: Leerer Wert", description.key)
            continue
            
        entities.append(VioletSensor(coordinator, config_entry, description))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("Sensors eingerichtet: %s", [e.entity_id for e in entities])
    else:
        _LOGGER.info("Keine Sensors eingerichtet")
