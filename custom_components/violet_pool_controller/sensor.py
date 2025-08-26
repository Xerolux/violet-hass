"""Sensor Integration für den Violet Pool Controller."""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN, TEMP_SENSORS, WATER_CHEM_SENSORS, ANALOG_SENSORS, CONF_ACTIVE_FEATURES, 
    UNIT_MAP, NO_UNIT_SENSORS, SENSOR_FEATURE_MAP
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Timestamp detection
_TIMESTAMP_SUFFIXES = ("_LAST_ON", "_LAST_OFF", "_LAST_AUTO_RUN", "_LAST_MANUAL_RUN", "_LAST_CAN_RESET", "_TIMESTAMP")
_TIMESTAMP_KEYS = {"CURRENT_TIME_UNIX"} | {key for key in UNIT_MAP if any(key.upper().endswith(suffix) for suffix in _TIMESTAMP_SUFFIXES)}

# Text value sensors that should remain as strings
TEXT_VALUE_SENSORS = {
    "DOS_1_CL_STATE", "DOS_4_PHM_STATE", "DOS_5_PHP_STATE", "HEATERSTATE", "SOLARSTATE", "PUMPSTATE",
    "BACKWASHSTATE", "OMNI_STATE", "BACKWASH_OMNI_STATE", "SOLAR_STATE", "HEATER_STATE", "PUMP_STATE",
    "FILTER_STATE", "OMNI_MODE", "FILTER_MODE", "SOLAR_MODE", "HEATER_MODE", "DISPLAY_MODE",
    "OPERATING_MODE", "MAINTENANCE_MODE", "ERROR_CODE", "LAST_ERROR", "VERSION_CODE", "CHECKSUM",
    "RULE_RESULT", "LAST_MOVING_DIRECTION", "COVER_DIRECTION", "SW_VERSION", "SW_VERSION_CARRIER",
    "HW_VERSION_CARRIER", "FW", "VERSION", "VERSION_INFO", "HARDWARE_VERSION", "CPU_GOV",
    "HW_SERIAL_CARRIER", "SERIAL_NUMBER", "MAC_ADDRESS", "IP_ADDRESS", 
    "DOS_1_CL_REMAINING_RANGE", "DOS_4_PHM_REMAINING_RANGE", "DOS_5_PHP_REMAINING_RANGE", 
    "DOS_6_FLOC_REMAINING_RANGE", "BACKWASH_OMNI_MOVING", "BACKWASH_DELAY_RUNNING", 
    "BACKWASH_STATE", "REFILL_STATE", "BATHING_AI_SURVEILLANCE_STATE", "BATHING_AI_PUMP_STATE", 
    "OVERFLOW_REFILL_STATE", "OVERFLOW_DRYRUN_STATE", "OVERFLOW_OVERFILL_STATE",
    "time", "TIME", "CURRENT_TIME"
}

# Runtime sensors - usually formatted time strings
RUNTIME_SENSORS = {
    "ECO_RUNTIME", "LIGHT_RUNTIME", "PUMP_RUNTIME", "BACKWASH_RUNTIME", "SOLAR_RUNTIME", "HEATER_RUNTIME",
    *{f"EXT{i}_{j}_RUNTIME" for i in (1, 2) for j in range(1, 9)},
    "DOS_1_CL_RUNTIME", "DOS_4_PHM_RUNTIME", "DOS_5_PHP_RUNTIME", "DOS_6_FLOC_RUNTIME",
    *{f"OMNI_DC{i}_RUNTIME" for i in range(1, 6)}, "HEATER_POSTRUN_TIME", "SOLAR_POSTRUN_TIME",
    "REFILL_TIMEOUT", "CPU_UPTIME", "DEVICE_UPTIME", "RUNTIME", "POSTRUN_TIME",
    *{f"PUMP_RPM_{i}_RUNTIME" for i in range(4)}
}

# Non-temperature onewire sensors (status info)
NON_TEMPERATURE_SENSORS = {
    *{f"onewire{i}_{suffix}" for i in range(1, 13) for suffix in ("rcode", "romcode", "state")},
}

# Combine text sensors
TEXT_VALUE_SENSORS.update(RUNTIME_SENSORS)

@dataclass
class VioletSensorEntityDescription:
    """Beschreibt Sensor-Entitäten."""
    key: str
    name: str
    icon: str | None = None
    native_unit_of_measurement: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    feature_id: str | None = None
    entity_category: EntityCategory | None = None

class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Repräsentation eines Sensors."""
    entity_description: VioletSensorEntityDescription

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry, description: VioletSensorEntityDescription) -> None:
        """Initialisiere Sensor."""
        super().__init__(coordinator, config_entry, description)
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_entity_category = description.entity_category
        self._logger = logging.getLogger(f"{DOMAIN}.{self._attr_unique_id}")

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Gib nativen Wert zurück."""
        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)
        
        if raw_value is None:
            return None
            
        # Handle timestamp values
        if key in _TIMESTAMP_KEYS:
            try:
                return datetime.fromtimestamp(float(raw_value), tz=timezone.utc) if raw_value else None
            except (ValueError, TypeError):
                return None
                
        # Handle text values
        if key in TEXT_VALUE_SENSORS:
            return str(raw_value)
            
        # Try to convert to numeric value
        try:
            f = float(raw_value)
            # Round based on sensor type
            if key == "pH_value":
                return round(f, 2)
            elif key in {"onewire1_value", "onewire2_value", "onewire3_value", "onewire4_value", "onewire5_value", "onewire6_value"}:
                return round(f, 1)
            elif "temp" in key.lower():
                return round(f, 1)
            # Return integer if it's a whole number
            return int(f) if f.is_integer() else f
        except (ValueError, TypeError):
            return str(raw_value)

def determine_device_class(key: str, unit: str | None) -> SensorDeviceClass | None:
    """Bestimme Device-Klasse."""
    if key in RUNTIME_SENSORS or key in TEXT_VALUE_SENSORS:
        return None
        
    key_lower = key.lower()
    
    if unit == "°C" or "temp" in key_lower or key in {"SYSTEM_cpu_temperature", "SYSTEM_carrier_cpu_temperature"}:
        return SensorDeviceClass.TEMPERATURE
    elif key == "pH_value":
        return SensorDeviceClass.PH
    elif unit == "%" and "humidity" in key_lower:
        return SensorDeviceClass.HUMIDITY
    elif unit == "bar" or "pressure" in key_lower:
        return SensorDeviceClass.PRESSURE
    elif unit in {"mV", "V"} or "voltage" in key_lower:
        return SensorDeviceClass.VOLTAGE
    elif unit == "W" or "power" in key_lower:
        return SensorDeviceClass.POWER
    elif unit == "RPM" or "rpm" in key_lower:
        return SensorDeviceClass.FREQUENCY
    elif key in _TIMESTAMP_KEYS:
        return SensorDeviceClass.TIMESTAMP
        
    return None

def determine_state_class(key: str, unit: str | None) -> SensorStateClass | None:
    """Bestimme State-Klasse."""
    if key in TEXT_VALUE_SENSORS or key in _TIMESTAMP_KEYS or key in NO_UNIT_SENSORS or key in RUNTIME_SENSORS:
        return None
        
    if unit in {"°C", "bar", "mV", "V", "W", "mg/l", "ppm", "%", "RPM", "pH"}:
        return SensorStateClass.MEASUREMENT
        
    key_lower = key.lower()
    if "total" in key_lower or "daily" in key_lower:
        return SensorStateClass.TOTAL_INCREASING
        
    return None

def get_icon(unit: str | None, key: str) -> str:
    """Bestimme Icon basierend auf Unit und Key."""
    if unit == "°C":
        return "mdi:thermometer"
    elif unit in {"bar", "Pa"}:
        return "mdi:gauge"
    elif unit in {"mV", "V"}:
        return "mdi:flash"
    elif unit == "W":
        return "mdi:lightning-bolt"
    elif unit in {"mg/l", "ppm"}:
        return "mdi:test-tube"
    elif unit == "pH":
        return "mdi:flask"
    elif unit == "RPM":
        return "mdi:speedometer"
    elif key in _TIMESTAMP_KEYS:
        return "mdi:clock"
    elif key in TEXT_VALUE_SENSORS:
        return "mdi:text"
    elif key in RUNTIME_SENSORS:
        return "mdi:timer"
    return "mdi:information"

def should_skip_sensor(key: str, raw_value) -> bool:
    """Prüfe, ob Sensor übersprungen werden soll."""
    if raw_value is None:
        return True
        
    raw_str = str(raw_value).strip()
    if raw_str in ("[]", "{}", ""):
        return True
        
    # Skip runtime sensors with time formatting
    if key in RUNTIME_SENSORS:
        if ":" in raw_str or any(s in raw_str.lower() for s in ("h", "m", "s")) and not raw_str.replace(".", "").isdigit():
            return True
            
    # Skip non-temperature onewire sensors
    if key in NON_TEMPERATURE_SENSORS:
        return True
        
    # Skip private keys
    if key.startswith("_"):
        return True
        
    return False

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Richte Sensoren ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    sensors = []
    data_keys = set(coordinator.data.keys())
    
    # Combine all predefined sensors
    all_predefined_sensors = {**TEMP_SENSORS, **WATER_CHEM_SENSORS, **ANALOG_SENSORS}

    # Add predefined sensors
    for key, info in all_predefined_sensors.items():
        if key not in data_keys:
            continue
        if should_skip_sensor(key, coordinator.data.get(key)):
            continue
            
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            continue
            
        sensors.append(VioletSensor(coordinator, config_entry, VioletSensorEntityDescription(
            key=key,
            name=info["name"],
            icon=info.get("icon"),
            native_unit_of_measurement=info.get("unit"),
            device_class=determine_device_class(key, info.get("unit")),
            state_class=determine_state_class(key, info.get("unit")),
            feature_id=feature_id
        )))

    # Add dynamic sensors from coordinator data
    for key in data_keys - set(all_predefined_sensors):
        raw_value = coordinator.data.get(key)
        if should_skip_sensor(key, raw_value):
            continue
            
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            continue
            
        # Determine unit from mapping or none
        unit = None if key in NO_UNIT_SENSORS else UNIT_MAP.get(key)
        
        # Create nice name from key
        name = key.replace("_", " ").title()
        
        sensors.append(VioletSensor(coordinator, config_entry, VioletSensorEntityDescription(
            key=key,
            name=name,
            icon=get_icon(unit, key),
            native_unit_of_measurement=unit,
            device_class=determine_device_class(key, unit),
            state_class=determine_state_class(key, unit),
            feature_id=feature_id,
            entity_category=EntityCategory.DIAGNOSTIC if key.startswith(("SYSTEM_", "CPU_")) or key in TEXT_VALUE_SENSORS else None
        )))

    if sensors:
        async_add_entities(sensors)
        _LOGGER.info("%d Sensoren hinzugefügt", len(sensors))
    else:
        _LOGGER.warning("Keine Sensoren hinzugefügt")
