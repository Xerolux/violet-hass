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