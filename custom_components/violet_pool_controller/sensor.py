"""Sensor Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass

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

# Einheiten für verschiedene Sensortypen
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

# Sensortypen ohne Einheiten
NO_UNIT_SENSORS = {
    "SOLAR_LAST_OFF", "HEATER_LAST_ON", "HEATER_LAST_OFF",
    "BACKWASH_LAST_ON", "BACKWASH_LAST_OFF", "PUMP_LAST_ON", "PUMP_LAST_OFF",
    "CPU_UPTIME", "CPU_GOV", "SW_VERSION", "SW_VERSION_CARRIER", "HW_VERSION_CARRIER",
    "BACKWASH_OMNI_MOVING", "BACKWASH_DELAY_RUNNING"
}

# Sensoren mit Textwerten (nicht numerisch)
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

# Nicht-Temperatur-Sensoren mit "temp" oder "onewire" im Namen
NON_TEMPERATURE_SENSORS = {
    "onewire1_rcode", "onewire2_rcode", "onewire3_rcode", "onewire4_rcode",
    "onewire5_rcode", "onewire6_rcode", "onewire1romcode", "onewire2romcode",
    "onewire3romcode", "onewire4romcode", "onewire5romcode", "onewire6romcode",
    "onewire1_state", "onewire2_state", "onewire3_state", "onewire4_state",
    "onewire5_state", "onewire6_state"
}

# Mapping von Sensor-Keys zu Feature-IDs
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
    "HEATER_TEMPERATURE": "heating",
    "COVER_POSITION": "cover_control",
}

@dataclass
class VioletSensorEntityDescription(SensorEntityDescription):
    """Beschreibung von Violet Pool Sensorentitäten."""
    feature_id: Optional[str] = None
    is_numeric: bool = True

class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Repräsentation eines Violet Pool Controller Sensors."""
    entity_description: VioletSensorEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: VioletSensorEntityDescription,
    ):
        """Initialisiert den Sensor."""
        super().__init__(coordinator, config_entry, description)
        self._has_logged_none_state = False

    @property
    def native_value(self) -> Union[float, int, str, None]:
        """Gibt den aktuellen Wert des Sensors zurück."""
        key = self.entity_description.key
        key_upper = key.upper()

        # Prüfe, ob es sich um einen Text-Sensor handelt
        is_text_sensor = (
            key_upper in TEXT_VALUE_SENSORS or
            any(pattern in key_upper for pattern in ["RUNTIME", "STATE", "MODE", "VERSION", "TIME", "DIRECTION", "FW", "MOVING", "RUNNING"]) or
            not self.entity_description.is_numeric
        )

        # Text-Sensoren direkt als String zurückgeben
        if is_text_sensor:
            return self.get_str_value(key)

        # Zeitstempel-Sensoren (z. B. "last_on", "last_off")
        if key.lower().endswith(("_last_on", "_last_off")):
            return self.get_str_value(key)

        # Rohwert aus Coordinator-Daten holen
        raw_value = self.coordinator.data.get(key) if self.coordinator.data else None

        # Listenwerte für Status-Sensoren
        if isinstance(raw_value, list):
            if not raw_value:
                return None
            elif len(raw_value) == 1:
                raw_value = raw_value[0]
            else:
                return ", ".join(str(item) for item in raw_value)

        # None-Werte behandeln
        if raw_value is None:
            if not self._has_logged_none_state:
                _LOGGER.warning(f"Sensor '{key}' hat None als Zustand zurückgegeben.")
                self._has_logged_none_state = True
            return None

        # Spezielle String-Muster prüfen (z. B. "53d", "00h 00m 00s")
        if isinstance(raw_value, str):
            if any(c.isalpha() for c in raw_value) or any(unit in raw_value for unit in ["h ", "m ", "s", "d "]):
                return raw_value
            if raw_value.count('.') >= 1 and any(c.isalpha() for c in raw_value):
                return raw_value
            if raw_value.count('.') == 3 and all(part.isdigit() for part in raw_value.split('.')):
                return raw_value

        # Wert basierend auf Device Class abrufen
        device_class = self.entity_description.device_class
        if device_class in (SensorDeviceClass.TEMPERATURE, SensorDeviceClass.PRESSURE,
                           SensorDeviceClass.PH, SensorDeviceClass.POWER,
                           SensorDeviceClass.VOLTAGE):
            return self.get_float_value(key)

        # Standard: Float-Interpretation mit Fallback auf String
        try:
            if isinstance(raw_value, (int, float)):
                return raw_value
            elif isinstance(raw_value, str) and raw_value.replace(".", "", 1).isdigit():
                return float(raw_value)
            return raw_value
        except Exception as err:
            _LOGGER.error(f"Fehler beim Abrufen des Werts für {key}: {err}")
            return None

    def _update_from_coordinator(self) -> None:
        """Aktualisiert den Sensorzustand aus den Coordinator-Daten."""
        pass  # Keine zusätzlichen Updates nötig

# Hilfsfunktionen
def guess_device_class(key: str) -> Optional[str]:
    """Bestimmt die Device Class basierend auf dem Sensor-Key."""
    key_upper = key.upper()
    if key_upper in TEXT_VALUE_SENSORS or any(pattern in key_upper for pattern in ["RUNTIME", "STATE", "MODE", "VERSION", "TIME", "DIRECTION", "FW", "MOVING", "RUNNING"]):
        return None
    if key.lower() in NON_TEMPERATURE_SENSORS:
        return None
    klower = key.lower()
    if "temp" in klower and not klower.endswith("_state") or "onewire" in klower and klower.endswith("_value") or "cpu_temp" in klower:
        return SensorDeviceClass.TEMPERATURE
    if "humidity" in klower:
        return SensorDeviceClass.HUMIDITY
    if "pressure" in klower or "adc1" in klower:
        return SensorDeviceClass.PRESSURE
    if "energy" in klower or "power" in klower:
        return SensorDeviceClass.POWER
    if "ph_value" in klower:
        return SensorDeviceClass.PH
    if "voltage" in klower:
        return SensorDeviceClass.VOLTAGE
    return None

def guess_state_class(key: str) -> Optional[str]:
    """Bestimmt die State Class basierend auf dem Sensor-Key."""
    key_upper = key.upper()
    if key_upper in TEXT_VALUE_SENSORS or any(pattern in key_upper for pattern in ["RUNTIME", "STATE", "MODE", "VERSION", "TIME", "DIRECTION", "FW", "MOVING", "RUNNING"]):
        return None
    if "_REMAINING_RANGE" in key_upper:
        return None
    klower = key.lower()
    if "daily" in klower or "_daily_" in klower:
        return SensorStateClass.TOTAL
    if "last_on" in klower or "last_off" in klower:
        return None
    if any(x in klower for x in ["runtime", "state", "_status", "rcode", "romcode", "mode", "version", "time", "direction", "fw", "moving", "running"]):
        return None
    return SensorStateClass.MEASUREMENT

def guess_icon(key: str) -> str:
    """Bestimmt ein Icon basierend auf dem Sensor-Key."""
    klower = key.lower()
    if "temp" in klower or "therm" in klower or "cpu_temp" in klower:
        return "mdi:thermometer"
    if "pump" in klower:
        return "mdi:water-pump"
    if "orp" in klower:
        return "mdi:flash"
    if "ph" in klower:
        return "mdi:flask"
    if "pressure" in klower or "adc" in klower:
        return "mdi:gauge"
    if "memory" in klower:
        return "mdi:memory"
    if "cpu" in klower or "load" in klower:
        return "mdi:cpu-64-bit"
    if "uptime" in klower:
        return "mdi:clock-outline"
    if "rpm" in klower:
        return "mdi:fan"
    if "version" in klower or "fw" in klower:
        return "mdi:update"
    if "serial" in klower:
        return "mdi:barcode"
    if "runtime" in klower:
        return "mdi:clock-time-four-outline"
    if "state" in klower:
        return "mdi:state-machine"
    if "direction" in klower:
        return "mdi:arrow-decision"
    if "time" in klower:
        return "mdi:timer-outline"
    if "mode" in klower:
        return "mdi:tune"
    if "last_on" in klower:
        return "mdi:timer"
    if "last_off" in klower:
        return "mdi:timer-off"
    if "status" in klower:
        return "mdi:information-outline"
    if "rcode" in klower or "romcode" in klower:
        return "mdi:identifier"
    if "_remaining_range" in klower:
        return "mdi:calendar-clock"
    if "moving" in klower:
        return "mdi:motion"
    if "running" in klower:
        return "mdi:run"
    return "mdi:information"

def guess_entity_category(key: str) -> Optional[str]:
    """Bestimmt die Entity-Kategorie basierend auf dem Sensor-Key."""
    klower = key.lower()
    if any(x in klower for x in ["system", "cpu", "memory", "fw", "version", "load", "uptime", "serial", "rcode", "romcode", "runtime", "time", "hw_"]):
        return EntityCategory.DIAGNOSTIC
    if "setpoint" in klower or "target" in klower:
        return EntityCategory.CONFIG
    return None

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Richtet Violet Pool Sensoren aus einer Config Entry ein."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    available_data_keys = set(coordinator.data.keys())
    sensors: List[VioletSensor] = []

    # 1. Temperatur-Sensoren
    for key, sensor_info in TEMP_SENSORS.items():
        if key not in available_data_keys:
            continue
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(f"Sensor {key} übersprungen, da Feature {feature_id} inaktiv.")
            continue
        description = VioletSensorEntityDescription(
            key=key,
            name=sensor_info["name"],
            icon=sensor_info["icon"],
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement="°C",
            feature_id=feature_id,
            is_numeric=True,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    # 2. Wasserchemie-Sensoren
    for key, sensor_info in WATER_CHEM_SENSORS.items():
        if key not in available_data_keys:
            continue
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(f"Sensor {key} übersprungen, da Feature {feature_id} inaktiv.")
            continue
        device_class = guess_device_class(key)
        unit = None if device_class == SensorDeviceClass.PH else sensor_info["unit"]
        key_upper = key.upper()
        is_numeric = key_upper not in TEXT_VALUE_SENSORS and not any(pattern in key_upper for pattern in ["RUNTIME", "STATE", "MODE", "VERSION", "TIME", "DIRECTION", "FW", "MOVING", "RUNNING"]) and "_REMAINING_RANGE" not in key_upper
        description = VioletSensorEntityDescription(
            key=key,
            name=sensor_info["name"],
            icon=sensor_info["icon"],
            device_class=device_class,
            state_class=guess_state_class(key) if is_numeric else None,
            native_unit_of_measurement=unit,
            feature_id=feature_id,
            is_numeric=is_numeric,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    # 3. Analog-Sensoren
    for key, sensor_info in ANALOG_SENSORS.items():
        if key not in available_data_keys:
            continue
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(f"Sensor {key} übersprungen, da Feature {feature_id} inaktiv.")
            continue
        key_upper = key.upper()
        is_numeric = key_upper not in TEXT_VALUE_SENSORS and not any(pattern in key_upper for pattern in ["RUNTIME", "STATE", "MODE", "VERSION", "TIME", "DIRECTION", "FW", "MOVING", "RUNNING"]) and "_REMAINING_RANGE" not in keyframes_upper
        description = VioletSensorEntityDescription(
            key=key,
            name=sensor_info["name"],
            icon=sensor_info["icon"],
            device_class=guess_device_class(key),
            state_class=guess_state_class(key) if is_numeric else None,
            native_unit_of_measurement=sensor_info["unit"],
            feature_id=feature_id,
            is_numeric=is_numeric,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    # 4. Dynamische Sensoren
    excluded_keys = {"date", "time", "CURRENT_TIME_UNIX"}
    for key in available_data_keys:
        if key in TEMP_SENSORS or key in WATER_CHEM_SENSORS or key in ANALOG_SENSORS or key in excluded_keys:
            continue
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(f"Sensor {key} übersprungen, da Feature {feature_id} inaktiv.")
            continue
        name = key.replace('_', ' ').title()
        key_upper = key.upper()
        is_text_sensor = key_upper in TEXT_VALUE_SENSORS or any(pattern in key_upper for pattern in ["RUNTIME", "STATE", "MODE", "VERSION", "TIME", "DIRECTION", "FW", "MOVING", "RUNNING", "_OMNI_", "DELAY_"]) or "_REMAINING_RANGE" in key_upper
        unit = None if (is_text_sensor or key in NO_UNIT_SENSORS) else UNIT_MAP.get(key)
        if guess_device_class(key) == SensorDeviceClass.TEMPERATURE and not unit:
            unit = "°C"
        description = VioletSensorEntityDescription(
            key=key,
            name=name,
            icon=guess_icon(key),
            device_class=guess_device_class(key),
            state_class=guess_state_class(key) if not is_text_sensor else None,
            native_unit_of_measurement=unit,
            entity_category=EntityCategory(guess_entity_category(key)) if guess_entity_category(key) else None,
            feature_id=feature_id,
            is_numeric=not is_text_sensor,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    # 5. Dosierungs-Sensoren
    dosing_keys = {
        "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "Chlor Tagesdosierung",
        "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "pH- Tagesdosierung",
        "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "pH+ Tagesdosierung",
        "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "Flockmittel Tagesdosierung",
    }
    created_sensor_keys = {sensor.entity_description.key for sensor in sensors}
    for key, name in dosing_keys.items():
        if key in created_sensor_keys or key not in available_data_keys:
            continue
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(f"Sensor {key} übersprungen, da Feature {feature_id} inaktiv.")
            continue
        key_upper = key.upper()
        is_numeric = key_upper not in TEXT_VALUE_SENSORS and not any(pattern in key_upper for pattern in ["RUNTIME", "STATE", "MODE", "VERSION", "TIME", "DIRECTION", "FW", "MOVING", "RUNNING"]) and "_REMAINING_RANGE" not in key_upper
        description = VioletSensorEntityDescription(
            key=key,
            name=name,
            icon="mdi:water",
            state_class=SensorStateClass.TOTAL if is_numeric else None,
            native_unit_of_measurement="mL",
            feature_id=feature_id,
            is_numeric=is_numeric,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    # 6. System-Sensoren
    system_sensors = {
        "CPU_TEMP": {"name": "CPU Temperatur", "icon": "mdi:cpu-64-bit", "device_class": SensorDeviceClass.TEMPERATURE, "unit": "°C"},
        "CPU_TEMP_CARRIER": {"name": "Carrier CPU Temperatur", "icon": "mdi:cpu-64-bit", "device_class": SensorDeviceClass.TEMPERATURE, "unit": "°C"},
        "LOAD_AVG": {"name": "System Auslastung", "icon": "mdi:chart-line", "unit": ""},
        "CPU_UPTIME": {"name": "System Laufzeit", "icon": "mdi:clock-outline", "unit": None},
        "CPU_GOV": {"name": "CPU Governor", "icon": "mdi:cpu-64-bit", "unit": None},
        "MEMORY_USED": {"name": "Speichernutzung", "icon": "mdi:memory", "unit": "%"},
        "SW_VERSION": {"name": "Software Version", "icon": "mdi:update", "unit": None},
        "SW_VERSION_CARRIER": {"name": "Carrier SW Version", "icon": "mdi:update", "unit": None},
        "HW_VERSION_CARRIER": {"name": "Carrier HW Version", "icon": "mdi:chip", "unit": None},
        "BACKWASH_OMNI_MOVING": {"name": "Backwash Moving", "icon": "mdi:motion", "unit": None},
        "BACKWASH_DELAY_RUNNING": {"name": "Backwash Delay Running", "icon": "mdi:timer-sand", "unit": None},
    }
    for key, info in system_sensors.items():
        if key not in available_data_keys or key in created_sensor_keys:
            continue
        key_upper = key.upper()
        is_text_sensor = key_upper in TEXT_VALUE_SENSORS or any(pattern in key_upper for pattern in ["VERSION", "TIME", "UPTIME", "GOV", "MOVING", "RUNNING", "DELAY", "OMNI"]) or "_REMAINING_RANGE" in key_upper
        description = VioletSensorEntityDescription(
            key=key,
            name=info["name"],
            icon=info["icon"],
            device_class=info.get("device_class"),
            state_class=None,
            native_unit_of_measurement=info["unit"],
            entity_category=EntityCategory.DIAGNOSTIC,
            is_numeric=not is_text_sensor,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    if sensors:
        _LOGGER.info(f"{len(sensors)} Sensoren hinzugefügt.")
        async_add_entities(sensors)
    else:
        _LOGGER.warning("Keine passenden Sensoren gefunden.")
