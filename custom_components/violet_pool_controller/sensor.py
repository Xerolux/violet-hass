"""Sensor Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime, timezone

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN,
    TEMP_SENSORS,
    WATER_CHEM_SENSORS,
    ANALOG_SENSORS,
    CONF_ACTIVE_FEATURES,
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

UNIT_MAP = {
    "IMP1_value": "cm/s",
    "IMP2_value": "cm/s",
    "pump_rs485_pwr": "W",
    "SYSTEM_cpu_temperature": "°C",
    "SYSTEM_carrier_cpu_temperature": "°C",
    "SYSTEM_dosagemodule_cpu_temperature": "°C",
    "SYSTEM_memoryusage": "MB",
    "pH_value": "pH",
    "orp_value": "mV",
    "pot_value": "mg/l",
    "PUMP_RPM_0": "RPM",
    "PUMP_RPM_1": "RPM",
    "PUMP_RPM_2": "RPM",
    "PUMP_RPM_3": "RPM",
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "mL",
    "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": "mL",
    "ADC1_value": "bar",
    "ADC2_value": "cm",
    "ADC3_value": "m³",
    "ADC4_value": "V",
    "ADC5_value": "V",
    "ADC6_value": "V",
    "WATER_TEMPERATURE": "°C",
    "AIR_TEMPERATURE": "°C",
    "HUMIDITY": "%",
    "FILTER_PRESSURE": "bar",
    "HEATER_TEMPERATURE": "°C",
    "COVER_POSITION": "%",
    "UV_INTENSITY": "W/m²",
    "TDS": "ppm",
    "CHLORINE_LEVEL": "ppm",
    "BROMINE_LEVEL": "ppm",
    "TURBIDITY": "NTU",
    "CPU_TEMP": "°C",
    "CPU_TEMP_CARRIER": "°C",
    "LOAD_AVG": "",
    "MEMORY_USED": "%",
    "SW_VERSION": "",
    "SW_VERSION_CARRIER": "",
    "HW_VERSION_CARRIER": "",
    "HW_SERIAL_CARRIER": "",
    # Zusätzliche Einheiten für bestehende Sensoren
    "onewire1_value": "°C",
    "onewire2_value": "°C", 
    "onewire3_value": "°C",
    "onewire4_value": "°C",
    "onewire5_value": "°C",
    "onewire6_value": "°C",
    "water_temp": "°C",
    "air_temp": "°C",
}

NO_UNIT_SENSORS = {
    "CPU_UPTIME", "CPU_GOV", "SW_VERSION", "SW_VERSION_CARRIER", "HW_VERSION_CARRIER",
    "BACKWASH_OMNI_MOVING", "BACKWASH_DELAY_RUNNING", "HW_SERIAL_CARRIER", "SERIAL_NUMBER",
    "MAC_ADDRESS", "IP_ADDRESS", "FW", "VERSION", "VERSION_INFO", "HARDWARE_VERSION"
}

# Keys that represent Unix timestamps
_BASE_TIMESTAMP_KEYS = {
    "CURRENT_TIME_UNIX",
}
_TIMESTAMP_SUFFIXES = (
    "_LAST_ON", "_LAST_OFF", "_LAST_AUTO_RUN", "_LAST_MANUAL_RUN",
    "_LAST_CAN_RESET", "_TIMESTAMP"
)

def is_timestamp_key(key: str) -> bool:
    """Check if a key is likely a timestamp based on name."""
    key_upper = key.upper()
    if key_upper in _BASE_TIMESTAMP_KEYS:
        return True
    for suffix in _TIMESTAMP_SUFFIXES:
        if key_upper.endswith(suffix):
            return True
    return False

TEXT_VALUE_SENSORS = {
    "DOS_1_CL_STATE", "DOS_4_PHM_STATE", "DOS_5_PHP_STATE",
    "HEATERSTATE", "SOLARSTATE", "PUMPSTATE", "BACKWASHSTATE",
    "OMNI_STATE", "BACKWASH_OMNI_STATE", "SOLAR_STATE",
    "HEATER_STATE", "PUMP_STATE", "FILTER_STATE",
    "OMNI_MODE", "FILTER_MODE", "SOLAR_MODE",
    "HEATER_MODE", "DISPLAY_MODE", "OPERATING_MODE", "MAINTENANCE_MODE",
    "ERROR_CODE", "LAST_ERROR", "VERSION_CODE", "CHECKSUM",
    "RULE_RESULT", "LAST_MOVING_DIRECTION", "COVER_DIRECTION",
    "SW_VERSION", "SW_VERSION_CARRIER", "HW_VERSION_CARRIER",
    "FW", "VERSION", "VERSION_INFO", "HARDWARE_VERSION",
    "CPU_GOV", "HW_SERIAL_CARRIER", "SERIAL_NUMBER", "MAC_ADDRESS",
    "IP_ADDRESS", "DOS_1_CL_REMAINING_RANGE", "DOS_4_PHM_REMAINING_RANGE",
    "DOS_5_PHP_REMAINING_RANGE", "DOS_6_FLOC_REMAINING_RANGE",
    "BACKWASH_OMNI_MOVING", "BACKWASH_DELAY_RUNNING", "BACKWASH_STATE",
    "REFILL_STATE", "BATHING_AI_SURVEILLANCE_STATE", "BATHING_AI_PUMP_STATE",
    "OVERFLOW_REFILL_STATE", "OVERFLOW_DRYRUN_STATE", "OVERFLOW_OVERFILL_STATE",
    "time", "TIME", "CURRENT_TIME"  # Zeit-Sensoren als Text
}

# Runtime sensors - these should be treated as text, not numeric
RUNTIME_SENSORS = {
    "ECO_RUNTIME", "LIGHT_RUNTIME", "PUMP_RUNTIME",
    "BACKWASH_RUNTIME", "SOLAR_RUNTIME", "HEATER_RUNTIME",
    "EXT1_1_RUNTIME", "EXT1_2_RUNTIME", "EXT1_3_RUNTIME",
    "EXT1_4_RUNTIME", "EXT1_5_RUNTIME", "EXT1_6_RUNTIME",
    "EXT1_7_RUNTIME", "EXT1_8_RUNTIME", "EXT2_1_RUNTIME",
    "EXT2_2_RUNTIME", "EXT2_3_RUNTIME", "EXT2_4_RUNTIME",
    "EXT2_5_RUNTIME", "EXT2_6_RUNTIME", "EXT2_7_RUNTIME",
    "EXT2_8_RUNTIME", "DOS_1_CL_RUNTIME", "DOS_4_PHM_RUNTIME",
    "DOS_5_PHP_RUNTIME", "DOS_6_FLOC_RUNTIME", "OMNI_DC1_RUNTIME",
    "OMNI_DC2_RUNTIME", "OMNI_DC3_RUNTIME", "OMNI_DC4_RUNTIME",
    "OMNI_DC5_RUNTIME", "HEATER_POSTRUN_TIME", "SOLAR_POSTRUN_TIME",
    "REFILL_TIMEOUT", "CPU_UPTIME", "DEVICE_UPTIME", "RUNTIME", "POSTRUN_TIME",
    # Add the problematic PUMP_RPM_X_RUNTIME sensors
    "PUMP_RPM_0_RUNTIME", "PUMP_RPM_1_RUNTIME", "PUMP_RPM_2_RUNTIME", "PUMP_RPM_3_RUNTIME"
}

# Add runtime sensors to text sensors
TEXT_VALUE_SENSORS.update(RUNTIME_SENSORS)

# Remove timestamp keys from TEXT_VALUE_SENSORS
_keys_to_remove_from_text_sensors = set()
for text_key in list(TEXT_VALUE_SENSORS):
    if is_timestamp_key(text_key):
        _keys_to_remove_from_text_sensors.add(text_key)
for k_to_remove in _keys_to_remove_from_text_sensors:
    TEXT_VALUE_SENSORS.discard(k_to_remove)
    NO_UNIT_SENSORS.discard(k_to_remove)

NON_TEMPERATURE_SENSORS = {
    "onewire1_rcode", "onewire2_rcode", "onewire3_rcode", "onewire4_rcode",
    "onewire5_rcode", "onewire6_rcode", "onewire1romcode", "onewire2romcode",
    "onewire3romcode", "onewire4romcode", "onewire5romcode", "onewire6romcode",
    "onewire1_state", "onewire2_state", "onewire3_state", "onewire4_state",
    "onewire5_state", "onewire6_state", "onewire7_rcode", "onewire8_rcode",
    "onewire9_rcode", "onewire10_rcode", "onewire11_rcode", "onewire12_rcode",
    "onewire7_state", "onewire8_state", "onewire9_state", "onewire10_state",
    "onewire11_state", "onewire12_state"
}

SENSOR_FEATURE_MAP = {
    "onewire1_value": "heating", 
    "onewire2_value": "heating", 
    "onewire3_value": "solar",
    "onewire4_value": "heating", 
    "onewire5_value": "heating", 
    "pH_value": "ph_control",
    "orp_value": "chlorine_control", 
    "pot_value": "chlorine_control",
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "chlorine_control",
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "chlorine_control",
    "ADC2_value": "water_level", 
    "FILTER_PRESSURE": "filter_control",
    "PUMP_RPM_0": "filter_control", 
    "PUMP_RPM_1": "filter_control",
    "PUMP_RPM_2": "filter_control", 
    "PUMP_RPM_3": "filter_control",
    "water_temp": "heating",
    "air_temp": "heating",
}

@dataclass
class VioletSensorEntityDescription(SensorEntityDescription):
    """Beschreibt Violet Pool Controller Sensor-Entitäten."""
    feature_id: Optional[str] = None

class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Repräsentation eines Violet Pool Controller Sensors."""
    entity_description: VioletSensorEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: VioletSensorEntityDescription,
    ) -> None:
        """Initialisiere den Sensor."""
        super().__init__(coordinator, config_entry, description)
        self._logger = logging.getLogger(f"{DOMAIN}.{self._attr_unique_id}")

    @property
    def native_value(self) -> Union[str, int, float, datetime, None]:
        """Gib den nativen Wert des Sensors zurück."""
        key = self.entity_description.key
        raw_value = self._get_value(key)
        
        if raw_value is None:
            return None
            
        # Handle empty lists/arrays as None
        if isinstance(raw_value, str) and raw_value.strip() in ['[]', '{}', '']:
            return None
            
        # Handle timestamp values - return as datetime object
        if is_timestamp_key(key):
            return self._parse_timestamp(raw_value)
            
        # Handle text values
        if key in TEXT_VALUE_SENSORS:
            return str(raw_value)
            
        # Handle numeric values
        try:
            if isinstance(raw_value, (int, float)):
                return raw_value
            elif isinstance(raw_value, str):
                # Try to parse as number
                clean_value = raw_value.strip()
                if clean_value.replace(".", "").replace("-", "").isdigit():
                    return float(clean_value) if "." in clean_value else int(clean_value)
                else:
                    # Return as string for non-numeric values
                    return clean_value
            else:
                return str(raw_value)
        except (ValueError, TypeError):
            return str(raw_value)

    def _parse_timestamp(self, timestamp_value: Any) -> Optional[datetime]:
        """Parse einen Zeitstempel-Wert zu einem datetime Objekt."""
        try:
            if isinstance(timestamp_value, (int, float)) and timestamp_value > 0:
                return datetime.fromtimestamp(timestamp_value, tz=timezone.utc)
            elif isinstance(timestamp_value, str) and timestamp_value.isdigit():
                return datetime.fromtimestamp(int(timestamp_value), tz=timezone.utc)
        except (ValueError, OSError):
            pass
        return None

def determine_device_class(key: str, unit: Optional[str]) -> Optional[SensorDeviceClass]:
    """Bestimme die Device-Klasse basierend auf Key und Unit."""
    key_lower = key.lower()
    
    # WICHTIG: Runtime-Sensoren haben KEINE Device-Klasse
    if key in RUNTIME_SENSORS:
        return None
    
    if unit == "°C" or "temp" in key_lower or key in {"SYSTEM_cpu_temperature", "SYSTEM_carrier_cpu_temperature"}:
        return SensorDeviceClass.TEMPERATURE
    elif unit == "%" and ("humidity" in key_lower or "memory" in key_lower):
        return SensorDeviceClass.HUMIDITY if "humidity" in key_lower else None
    elif unit == "bar" or "pressure" in key_lower:
        return SensorDeviceClass.PRESSURE
    elif unit in {"mV", "V"} or "voltage" in key_lower:
        return SensorDeviceClass.VOLTAGE
    elif unit == "W" or "power" in key_lower:
        return SensorDeviceClass.POWER
    elif unit in {"mg/l", "ppm"} or key in {"pH_value", "orp_value", "pot_value"}:
        return None  # No specific device class for chemical values
    elif unit in {"m³", "mL", "l"} or "volume" in key_lower:
        return None  # No specific device class for volume
    elif unit == "RPM" or "rpm" in key_lower:
        return SensorDeviceClass.FREQUENCY
    elif is_timestamp_key(key):
        return SensorDeviceClass.TIMESTAMP
    
    return None

def determine_state_class(key: str, unit: Optional[str]) -> Optional[SensorStateClass]:
    """Bestimme die State-Klasse basierend auf Key und Unit."""
    # WICHTIG: Runtime-Sensoren, Text-Sensoren und Timestamps haben KEINE State-Klasse
    if key in TEXT_VALUE_SENSORS or is_timestamp_key(key) or key in NO_UNIT_SENSORS or key in RUNTIME_SENSORS:
        return None
        
    if unit in {"°C", "bar", "mV", "V", "W", "mg/l", "ppm", "%", "RPM"}:
        return SensorStateClass.MEASUREMENT
    elif "total" in key.lower() or "daily" in key.lower():
        return SensorStateClass.TOTAL_INCREASING
        
    return None  # Default to None for safety

def should_skip_sensor(key: str, raw_value: Any) -> bool:
    """Bestimme ob ein Sensor übersprungen werden sollte."""
    # Skip sensors with problematic values
    if isinstance(raw_value, str):
        if raw_value.strip() in ['[]', '{}', '']:
            return True
        # Skip runtime sensors with time format that can't be converted to numeric
        if key in RUNTIME_SENSORS and (':' in raw_value or 'h' in raw_value or 'm' in raw_value or 's' in raw_value):
            return True
    
    # Skip irrelevant keys
    if key in NON_TEMPERATURE_SENSORS or key.startswith("_"):
        return True
        
    return False

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richte Sensoren basierend auf dem Config-Entry ein."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    
    sensors: List[VioletSensor] = []
    available_data_keys = set(coordinator.data.keys())

    # Erstelle vordefinierte Sensoren aus const.py
    all_predefined_sensors = {**TEMP_SENSORS, **WATER_CHEM_SENSORS, **ANALOG_SENSORS}
    
    for key, info in all_predefined_sensors.items():
        if key not in available_data_keys:
            continue
            
        raw_value = coordinator.data.get(key)
        if should_skip_sensor(key, raw_value):
            continue
            
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            continue
            
        unit = info.get("unit", "")
        device_class = determine_device_class(key, unit)
        state_class = determine_state_class(key, unit)
        
        description = VioletSensorEntityDescription(
            key=key,
            name=info["name"],
            icon=info.get("icon"),
            native_unit_of_measurement=unit,
            device_class=device_class,
            state_class=state_class,
            feature_id=feature_id,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    # Erstelle dynamische Sensoren für alle anderen verfügbaren Keys
    for key in available_data_keys:
        if key in all_predefined_sensors:
            continue  # Bereits verarbeitet
            
        raw_value = coordinator.data.get(key)
        if should_skip_sensor(key, raw_value):
            continue
            
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            continue
            
        unit = UNIT_MAP.get(key)
        if key in NO_UNIT_SENSORS:
            unit = None
            
        device_class = determine_device_class(key, unit)
        state_class = determine_state_class(key, unit)
        
        # Spezielle Behandlung für RUNTIME Sensoren - immer als Text
        if key in RUNTIME_SENSORS:
            device_class = None
            state_class = None
        
        # Generiere einen lesbaren Namen
        name = key.replace("_", " ").title()
        
        # Bestimme Icon basierend auf Typ
        icon = "mdi:information"
        if unit == "°C":
            icon = "mdi:thermometer"
        elif unit in {"bar", "Pa"}:
            icon = "mdi:gauge"
        elif unit in {"mV", "V"}:
            icon = "mdi:flash"
        elif unit == "W":
            icon = "mdi:lightning-bolt"
        elif unit in {"mg/l", "ppm"}:
            icon = "mdi:test-tube"
        elif unit == "RPM":
            icon = "mdi:speedometer"
        elif is_timestamp_key(key):
            icon = "mdi:clock"
        elif key in TEXT_VALUE_SENSORS:
            icon = "mdi:text"
            
        description = VioletSensorEntityDescription(
            key=key,
            name=name,
            icon=icon,
            native_unit_of_measurement=unit,
            device_class=device_class,
            state_class=state_class,
            feature_id=feature_id,
            entity_category=EntityCategory.DIAGNOSTIC if key.startswith(("SYSTEM_", "CPU_")) else None,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    if sensors:
        async_add_entities(sensors)
        _LOGGER.info("%d Sensoren hinzugefügt", len(sensors))
    else:
        _LOGGER.warning("Keine Sensoren gefunden")