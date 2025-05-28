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
}

NO_UNIT_SENSORS = {
    "CPU_UPTIME", "CPU_GOV", "SW_VERSION", "SW_VERSION_CARRIER", "HW_VERSION_CARRIER",
    "BACKWASH_OMNI_MOVING", "BACKWASH_DELAY_RUNNING"
    # Timestamp keys will also have no unit, handled by device_class check
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
    "ECO_RUNTIME", "LIGHT_RUNTIME", "PUMP_RUNTIME",
    "BACKWASH_RUNTIME", "SOLAR_RUNTIME", "HEATER_RUNTIME",
    "EXT1_1_RUNTIME", "EXT1_2_RUNTIME", "EXT1_3_RUNTIME",
    "EXT1_4_RUNTIME", "EXT1_5_RUNTIME", "EXT1_6_RUNTIME",
    "EXT1_7_RUNTIME", "EXT1_8_RUNTIME", "EXT2_1_RUNTIME",
    "EXT2_2_RUNTIME", "EXT2_3_RUNTIME", "EXT2_4_RUNTIME",
    "EXT2_5_RUNTIME", "EXT2_6_RUNTIME", "EXT2_7_RUNTIME",
    "EXT2_8_RUNTIME", "DOS_1_CL_RUNTIME", "DOS_4_PHM_RUNTIME",
    "DOS_5_PHP_RUNTIME", "DOS_6_FLOC_RUNTIME", "OMNI_DC1_RUNTIME",
    "OMNI_DC2_RUNTIME", "OMNI_MODE", "FILTER_MODE", "SOLAR_MODE",
    "HEATER_MODE", "DISPLAY_MODE", "OPERATING_MODE", "MAINTENANCE_MODE",
    "ERROR_CODE", "LAST_ERROR", "VERSION_CODE", "CHECKSUM",
    "RULE_RESULT", "LAST_MOVING_DIRECTION", "COVER_DIRECTION",
    "SW_VERSION", "SW_VERSION_CARRIER", "HW_VERSION_CARRIER",
    "FW", "VERSION", "VERSION_INFO", "HARDWARE_VERSION",
    "HEATER_POSTRUN_TIME", "SOLAR_POSTRUN_TIME", "REFILL_TIMEOUT",
    "CPU_UPTIME", "DEVICE_UPTIME", "RUNTIME", "POSTRUN_TIME",
    "CPU_GOV", "HW_SERIAL_CARRIER", "SERIAL_NUMBER", "MAC_ADDRESS",
    "IP_ADDRESS", "DOS_1_CL_REMAINING_RANGE", "DOS_4_PHM_REMAINING_RANGE",
    "DOS_5_PHP_REMAINING_RANGE", "DOS_6_FLOC_REMAINING_RANGE",
    "BACKWASH_OMNI_MOVING", "BACKWASH_DELAY_RUNNING", "BACKWASH_STATE",
    "REFILL_STATE", "BATHING_AI_SURVEILLANCE_STATE", "BATHING_AI_PUMP_STATE",
    "OVERFLOW_REFILL_STATE", "OVERFLOW_DRYRUN_STATE", "OVERFLOW_OVERFILL_STATE",
}
# Remove timestamp keys from TEXT_VALUE_SENSORS
_keys_to_remove_from_text_sensors = set()
for text_key in list(TEXT_VALUE_SENSORS): # Iterate over a copy for safe removal
    if is_timestamp_key(text_key):
        _keys_to_remove_from_text_sensors.add(text_key)
for k_to_remove in _keys_to_remove_from_text_sensors:
    TEXT_VALUE_SENSORS.discard(k_to_remove)
    NO_UNIT_SENSORS.discard(k_to_remove) # Also ensure they don't get units from NO_UNIT_SENSORS if listed there

NON_TEMPERATURE_SENSORS = {
    "onewire1_rcode", "onewire2_rcode", "onewire3_rcode", "onewire4_rcode",
    "onewire5_rcode", "onewire6_rcode", "onewire1romcode", "onewire2romcode",
    "onewire3romcode", "onewire4romcode", "onewire5romcode", "onewire6romcode",
    "onewire1_state", "onewire2_state", "onewire3_state", "onewire4_state",
    "onewire5_state", "onewire6_state"
}

SENSOR_FEATURE_MAP = {
    "onewire1_value": "heating", "onewire2_value": "heating", "onewire3_value": "solar",
    "onewire4_value": "heating", "onewire5_value": "heating", "pH_value": "ph_control",
    "orp_value": "chlorine_control", "pot_value": "chlorine_control",
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "chlorine_control",
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "chlorine_control",
    "ADC2_value": "water_level", "FILTER_PRESSURE": "filter_control",
    "PUMP_RPM_0": "filter_control", "PUMP_RPM_1": "filter_control",
    "PUMP_RPM_2": "filter_control", "PUMP_RPM_3": "filter_control",
    "HEATER_TEMPERATURE": "heating", "COVER_POSITION": "cover_control",
}

@dataclass
class VioletSensorEntityDescription(SensorEntityDescription):
    """Beschreibung von Violet Pool Sensorentitäten."""
    feature_id: Optional[str] = None
    is_numeric: bool = True # Default to True, override for text/timestamp sensors

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
        self._has_logged_none_state = False

    @property
    def native_value(self) -> Union[datetime, float, int, str, None]:
        """Gib den aktuellen Sensorwert zurück."""
        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)

        if raw_value is None:
            if not self._has_logged_none_state:
                _LOGGER.debug(f"Sensor '{key}' received None state.")
                self._has_logged_none_state = True
            return None
        self._has_logged_none_state = False

        if isinstance(raw_value, list):
            return ", ".join(str(item) for item in raw_value) if raw_value else None

        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            if isinstance(raw_value, (int, float)):
                try:
                    return datetime.fromtimestamp(raw_value, tz=timezone.utc)
                except (OSError, TypeError, ValueError) as e:
                    _LOGGER.warning(f"Sensor '{key}' (Timestamp) invalid numeric value '{raw_value}': {e}")
                    return None
            elif isinstance(raw_value, str) and raw_value.isdigit():
                try:
                    return datetime.fromtimestamp(int(raw_value), tz=timezone.utc)
                except (OSError, TypeError, ValueError) as e:
                    _LOGGER.warning(f"Sensor '{key}' (Timestamp) invalid string value '{raw_value}': {e}")
                    return None
            _LOGGER.warning(
                f"Sensor '{key}' (Timestamp) value '{raw_value}' (type: {type(raw_value)}) is not a valid Unix timestamp."
            )
            return None

        if self.entity_description.is_numeric: # is_numeric is False for timestamps
            if isinstance(raw_value, (int, float)):
                return raw_value
            _LOGGER.warning(
                f"Sensor '{key}' is_numeric=True, but value '{raw_value}' (type: {type(raw_value)}) from coordinator is not int/float. "
                "This might indicate an issue with _process_api_data or an unexpected string value."
            )
            # Attempt to return string if not numeric, or None if it's some other type
            return str(raw_value) if isinstance(raw_value, str) else None

        return str(raw_value)


def guess_device_class(key: str, is_ts_key: bool) -> Optional[SensorDeviceClass]:
    """Bestimme die Device Class."""
    if is_ts_key:
        return SensorDeviceClass.TIMESTAMP

    key_upper = key.upper()
    if key_upper in TEXT_VALUE_SENSORS: return None
    if any(pattern in key_upper for pattern in ["RUNTIME", "STATE", "MODE", "VERSION", "DIRECTION", "FW", "MOVING", "RUNNING", "_INFO", "_STATUS", "_MESSAGE", "_TEXT", "_RCODE", "_ROMCODE", "_GOV", "_SERIAL", "_ADDRESS"]):
        return None
    if key.lower() in NON_TEMPERATURE_SENSORS: return None

    klower = key.lower()
    if "temp" in klower and not klower.endswith(("_state", "_mode", "_status")):
        return SensorDeviceClass.TEMPERATURE
    if "onewire" in klower and klower.endswith("_value"):
        if klower not in NON_TEMPERATURE_SENSORS:
            return SensorDeviceClass.TEMPERATURE
    if "humidity" in klower: return SensorDeviceClass.HUMIDITY
    if "pressure" in klower or "adc1_value" == klower: return SensorDeviceClass.PRESSURE
    if "energy" in klower or "power" in klower or key_upper == "PUMP_RS485_PWR": return SensorDeviceClass.POWER
    if "ph_value" == klower: return SensorDeviceClass.PH
    if "voltage" in klower or (klower.startswith("adc") and klower.endswith("_value") and "adc1_value" not in klower):
        return SensorDeviceClass.VOLTAGE
    if "orp_value" == klower or "pot_value" == klower: return None
    return None


def guess_state_class(key: str, device_class: Optional[SensorDeviceClass]) -> Optional[SensorStateClass]:
    """Bestimme die State Class."""
    if device_class == SensorDeviceClass.TIMESTAMP: return None

    key_upper = key.upper()
    if key_upper in TEXT_VALUE_SENSORS or \
       any(pattern in key_upper for pattern in ["RUNTIME", "STATE", "MODE", "VERSION", "DIRECTION", "FW", "MOVING", "RUNNING", "_INFO", "_STATUS", "_MESSAGE", "_TEXT", "_RCODE", "_ROMCODE", "_GOV", "_SERIAL", "_ADDRESS", "_REMAINING_RANGE"]):
        return None

    klower = key.lower()
    if "daily" in klower or "_daily_" in klower or key_upper.endswith("_TOTAL_CAN_AMOUNT_ML"):
        return SensorStateClass.TOTAL

    if device_class is not None and device_class != SensorDeviceClass.ENUM :
        return SensorStateClass.MEASUREMENT
    return None

def guess_icon(key: str) -> str:
    """Bestimme ein Icon."""
    klower = key.lower()
    if is_timestamp_key(key): return "mdi:clock-time-four-outline" # Specific icon for timestamps
    if "temp" in klower or "therm" in klower or "cpu_temp" in klower: return "mdi:thermometer"
    if "pump" in klower: return "mdi:water-pump"
    if "orp" in klower: return "mdi:flash"
    if "ph" in klower: return "mdi:flask"
    if "pressure" in klower or "adc" in klower: return "mdi:gauge"
    if "memory" in klower: return "mdi:memory"
    if "cpu" in klower or "load" in klower: return "mdi:cpu-64-bit"
    if "uptime" in klower: return "mdi:clock-outline" # Could be text or numeric (seconds)
    if "rpm" in klower: return "mdi:fan"
    if "version" in klower or "fw" in klower: return "mdi:update"
    if "serial" in klower: return "mdi:barcode"
    if "runtime" in klower: return "mdi:clock-time-four-outline"
    if "state" in klower: return "mdi:state-machine"
    if "direction" in klower: return "mdi:arrow-decision"
    # "time" was too generic, now handled by is_timestamp_key for icon
    if "mode" in klower: return "mdi:tune"
    if "status" in klower: return "mdi:information-outline"
    if "rcode" in klower or "romcode" in klower: return "mdi:identifier"
    if "_remaining_range" in klower: return "mdi:calendar-clock"
    if "moving" in klower: return "mdi:motion"
    if "running" in klower: return "mdi:run"
    return "mdi:information"

def guess_entity_category(key: str) -> Optional[str]:
    """Bestimme die Entity-Kategorie."""
    klower = key.lower()
    if any(x in klower for x in ["system", "cpu", "memory", "fw", "version", "load", "uptime", "serial", "rcode", "romcode", "hw_"]) or is_timestamp_key(key): # Added is_timestamp_key for CURRENT_TIME_UNIX
        # Runtime keys are often diagnostic
        if "runtime" in klower : return EntityCategory.DIAGNOSTIC
        # Explicitly check if it's not a timestamp for other runtime/time like keys that are not purely diagnostic
        if not is_timestamp_key(key) and ("runtime" in klower or "time" in klower):
             pass # Let them be None if not fitting other specific categories
        else:
            return EntityCategory.DIAGNOSTIC

    if "setpoint" in klower or "target" in klower:
        return EntityCategory.CONFIG
    return None

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Sensoren ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    available_data_keys = set(coordinator.data.keys())
    sensors: List[VioletSensor] = []

    # Predefined sensors (TEMP_SENSORS, WATER_CHEM_SENSORS, ANALOG_SENSORS)
    for predefined_group in [TEMP_SENSORS, WATER_CHEM_SENSORS, ANALOG_SENSORS]:
        for key, sensor_info in predefined_group.items():
            if key not in available_data_keys:
                continue
            feature_id = SENSOR_FEATURE_MAP.get(key)
            if feature_id and feature_id not in active_features:
                _LOGGER.debug(f"Sensor {key} (predefined) übersprungen, da Feature {feature_id} inaktiv.")
                continue

            is_ts = is_timestamp_key(key) # Should be False for these typically
            current_device_class = sensor_info.get("device_class") or guess_device_class(key, is_ts)
            current_state_class = sensor_info.get("state_class") or guess_state_class(key, current_device_class)
            unit = sensor_info.get("unit")
            
            # is_numeric should be True if not text and not timestamp
            is_numeric_for_description = not is_ts and not (key.upper() in TEXT_VALUE_SENSORS)
            if current_device_class == SensorDeviceClass.PH: # pH is numeric but unitless for HA
                 unit = None
            elif current_device_class == SensorDeviceClass.TEMPERATURE and not unit:
                 unit = "°C"


            description = VioletSensorEntityDescription(
                key=key,
                name=sensor_info["name"],
                icon=sensor_info["icon"],
                device_class=current_device_class,
                state_class=current_state_class,
                native_unit_of_measurement=unit,
                feature_id=feature_id,
                is_numeric=is_numeric_for_description,
            )
            sensors.append(VioletSensor(coordinator, config_entry, description))
            available_data_keys.discard(key) # Remove key to avoid re-processing

    # Dynamically created sensors
    excluded_keys = {"date", "time"} # CURRENT_TIME_UNIX handled by is_timestamp_key
    for key in list(available_data_keys): # Iterate over copy as we might modify original set
        if key in excluded_keys:
            available_data_keys.discard(key)
            continue

        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(f"Sensor {key} (dynamic) übersprungen, da Feature {feature_id} inaktiv.")
            available_data_keys.discard(key)
            continue

        name = key.replace('_', ' ').title()
        is_ts = is_timestamp_key(key)
        current_device_class = guess_device_class(key, is_ts)
        current_state_class = guess_state_class(key, current_device_class)
        
        is_numeric_for_description = not is_ts and not (key.upper() in TEXT_VALUE_SENSORS)
        val_from_coord = coordinator.data.get(key)
        if current_device_class is None and not is_ts and not (key.upper() in TEXT_VALUE_SENSORS):
            if isinstance(val_from_coord, str) and not val_from_coord.replace(".", "", 1).isdigit():
                 is_numeric_for_description = False
        
        unit = None
        if current_device_class != SensorDeviceClass.TIMESTAMP:
            if not (key.upper() in TEXT_VALUE_SENSORS and UNIT_MAP.get(key) is None):
                 if key not in NO_UNIT_SENSORS :
                    unit = UNIT_MAP.get(key)
            if current_device_class == SensorDeviceClass.TEMPERATURE and not unit:
                unit = "°C"
        
        description = VioletSensorEntityDescription(
            key=key, name=name, icon=guess_icon(key),
            device_class=current_device_class, state_class=current_state_class,
            native_unit_of_measurement=unit,
            entity_category=guess_entity_category(key), # Removed EntityCategory() wrapping
            feature_id=feature_id, is_numeric=is_numeric_for_description,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))
        available_data_keys.discard(key)


    # Dosing keys (ensure they are not processed above if already in available_data_keys)
    dosing_keys_desc = {
        "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "Chlor Tagesdosierung",
        "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "pH- Tagesdosierung",
        "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "pH+ Tagesdosierung",
        "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "Flockmittel Tagesdosierung",
    }
    for key, name in dosing_keys_desc.items():
        if key not in coordinator.data: continue # Ensure key is in coordinator data
        if any(s.entity_description.key == key for s in sensors): continue # Skip if already created

        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(f"Sensor {key} (dosing) übersprungen, da Feature {feature_id} inaktiv.")
            continue
        
        is_numeric_for_description = not (key.upper() in TEXT_VALUE_SENSORS) # Timestamps not expected here
        current_state_class = SensorStateClass.TOTAL if is_numeric_for_description else None

        description = VioletSensorEntityDescription(
            key=key, name=name, icon="mdi:water",
            state_class=current_state_class, native_unit_of_measurement="mL",
            feature_id=feature_id, is_numeric=is_numeric_for_description,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    # System sensors (ensure they are not processed above)
    system_sensors_desc = {
        "CPU_TEMP": {"name": "CPU Temperatur", "icon": "mdi:cpu-64-bit", "device_class": SensorDeviceClass.TEMPERATURE, "unit": "°C"},
        "CPU_TEMP_CARRIER": {"name": "Carrier CPU Temperatur", "icon": "mdi:cpu-64-bit", "device_class": SensorDeviceClass.TEMPERATURE, "unit": "°C"},
        "LOAD_AVG": {"name": "System Auslastung", "icon": "mdi:chart-line", "unit": ""},
        "CPU_UPTIME": {"name": "System Laufzeit", "icon": "mdi:clock-outline", "unit": None}, # Could be text or timestamp if numeric
        "CPU_GOV": {"name": "CPU Governor", "icon": "mdi:cpu-64-bit", "unit": None},
        "MEMORY_USED": {"name": "Speichernutzung", "icon": "mdi:memory", "unit": "%"},
        "SW_VERSION": {"name": "Software Version", "icon": "mdi:update", "unit": None},
        "SW_VERSION_CARRIER": {"name": "Carrier SW Version", "icon": "mdi:update", "unit": None},
        "HW_VERSION_CARRIER": {"name": "Carrier HW Version", "icon": "mdi:chip", "unit": None},
        "BACKWASH_OMNI_MOVING": {"name": "Backwash Moving", "icon": "mdi:motion", "unit": None},
        "BACKWASH_DELAY_RUNNING": {"name": "Backwash Delay Running", "icon": "mdi:timer-sand", "unit": None},
    }
    for key, info in system_sensors_desc.items():
        if key not in coordinator.data: continue
        if any(s.entity_description.key == key for s in sensors): continue

        is_ts = is_timestamp_key(key) # e.g. if CPU_UPTIME is a numeric timestamp
        current_device_class = info.get("device_class") or guess_device_class(key, is_ts)
        current_state_class = guess_state_class(key, current_device_class) if not (key.upper() in TEXT_VALUE_SENSORS) else None
        is_numeric_for_description = not is_ts and not (key.upper() in TEXT_VALUE_SENSORS)
        if is_ts : is_numeric_for_description = False # Timestamps are not numeric for HA state

        description = VioletSensorEntityDescription(
            key=key, name=info["name"], icon=info["icon"],
            device_class=current_device_class,
            state_class=current_state_class,
            native_unit_of_measurement=info["unit"],
            entity_category=EntityCategory.DIAGNOSTIC,
            is_numeric=is_numeric_for_description,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    if sensors:
        _LOGGER.info(f"{len(sensors)} Sensoren hinzugefügt.")
        async_add_entities(sensors)
    else:
        _LOGGER.warning("Keine passenden Sensoren gefunden.")