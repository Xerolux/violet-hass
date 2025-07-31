"""Sensor Integration für den Violet Pool Controller."""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, TEMP_SENSORS, WATER_CHEM_SENSORS, ANALOG_SENSORS, CONF_ACTIVE_FEATURES, UNIT_MAP, NO_UNIT_SENSORS, SENSOR_FEATURE_MAP
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

_TIMESTAMP_SUFFIXES = ("_LAST_ON", "_LAST_OFF", "_LAST_AUTO_RUN", "_LAST_MANUAL_RUN", "_LAST_CAN_RESET", "_TIMESTAMP")
_TIMESTAMP_KEYS = {"CURRENT_TIME_UNIX"} | {key for key in UNIT_MAP if any(key.upper().endswith(suffix) for suffix in _TIMESTAMP_SUFFIXES)}
TEXT_VALUE_SENSORS = {
    "DOS_1_CL_STATE", "DOS_4_PHM_STATE", "DOS_5_PHP_STATE", "HEATERSTATE", "SOLARSTATE", "PUMPSTATE",
    "BACKWASHSTATE", "OMNI_STATE", "BACKWASH_OMNI_STATE", "SOLAR_STATE", "HEATER_STATE", "PUMP_STATE",
    "FILTER_STATE", "OMNI_MODE", "FILTER_MODE", "SOLAR_MODE", "HEATER_MODE", "DISPLAY_MODE",
    "OPERATING_MODE", "MAINTENANCE_MODE", "ERROR_CODE", "LAST_ERROR", "VERSION_CODE", "CHECKSUM",
    "RULE_RESULT", "LAST_MOVING_DIRECTION", "COVER_DIRECTION", "SW_VERSION", "SW_VERSION_CARRIER",
    "HW_VERSION_CARRIER", "FW", "VERSION", "VERSION_INFO", "HARDWARE_VERSION", "CPU_GOV",
    "HW_SERIAL_CARRIER", "SERIAL_NUMBER", "MAC_ADDRESS", "IP_ADDRESS", "DOS_1_CL_REMAINING_RANGE",
    "DOS_4_PHM_REMAINING_RANGE", "DOS_5_PHP_REMAINING_RANGE", "DOS_6_FLOC_REMAINING_RANGE",
    "BACKWASH_OMNI_MOVING", "BACKWASH_DELAY_RUNNING", "BACKWASH_STATE", "REFILL_STATE",
    "BATHING_AI_SURVEILLANCE_STATE", "BATHING_AI_PUMP_STATE", "OVERFLOW_REFILL_STATE",
    "OVERFLOW_DRYRUN_STATE", "OVERFLOW_OVERFILL_STATE", "time", "TIME", "CURRENT_TIME"
} - _TIMESTAMP_KEYS
RUNTIME_SENSORS = {
    "ECO_RUNTIME", "LIGHT_RUNTIME", "PUMP_RUNTIME", "BACKWASH_RUNTIME", "SOLAR_RUNTIME", "HEATER_RUNTIME",
    *{f"EXT{i}_{j}_RUNTIME" for i in (1, 2) for j in range(1, 9)},
    "DOS_1_CL_RUNTIME", "DOS_4_PHM_RUNTIME", "DOS_5_PHP_RUNTIME", "DOS_6_FLOC_RUNTIME",
    *{f"OMNI_DC{i}_RUNTIME" for i in range(1, 6)}, "HEATER_POSTRUN_TIME", "SOLAR_POSTRUN_TIME",
    "REFILL_TIMEOUT", "CPU_UPTIME", "DEVICE_UPTIME", "RUNTIME", "POSTRUN_TIME",
    *{f"PUMP_RPM_{i}_RUNTIME" for i in range(4)}
}
TEXT_VALUE_SENSORS.update(RUNTIME_SENSORS)
NON_TEMPERATURE_SENSORS = {
    *{f"onewire{i}_{suffix}" for i in range(1, 13) for suffix in ("rcode", "romcode", "state")},
}

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
        self._logger = logging.getLogger(f"{DOMAIN}.{self._attr_unique_id}")

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Gib nativen Wert zurück."""
        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)
        if raw_value is None or (isinstance(raw_value, str) and raw_value.strip() in ("[]", "{}", "")):
            return None
        if key in _TIMESTAMP_KEYS:
            try:
                return datetime.fromtimestamp(float(raw_value), tz=timezone.utc) if raw_value else None
            except (ValueError, TypeError):
                return None
        if key in TEXT_VALUE_SENSORS:
            return str(raw_value)
        try:
            if isinstance(raw_value, str):
                if "." in raw_value and raw_value.replace(".", "").replace("-", "").isdigit():
                    return float(raw_value)
                elif raw_value.isdigit():
                    return int(raw_value)
                else:
                    return str(raw_value)
            return raw_value
        except (ValueError, TypeError):
            return str(raw_value)

def determine_device_class(key: str, unit: str | None) -> SensorDeviceClass | None:
    """Bestimme Device-Klasse."""
    if key in RUNTIME_SENSORS or key in TEXT_VALUE_SENSORS or key in _TIMESTAMP_KEYS:
        return None
    key_lower = key.lower()
    if unit == "°C" or "temp" in key_lower or key in {"SYSTEM_cpu_temperature", "SYSTEM_carrier_cpu_temperature"}:
        return SensorDeviceClass.TEMPERATURE
    if unit == "%" and "humidity" in key_lower:
        return SensorDeviceClass.HUMIDITY
    if unit == "bar" or "pressure" in key_lower:
        return SensorDeviceClass.PRESSURE
    if unit in {"mV", "V"} or "voltage" in key_lower:
        return SensorDeviceClass.VOLTAGE
    if unit == "W" or "power" in key_lower:
        return SensorDeviceClass.POWER
    if unit == "RPM" or "rpm" in key_lower:
        return SensorDeviceClass.FREQUENCY
    if key in _TIMESTAMP_KEYS:
        return SensorDeviceClass.TIMESTAMP
    return None

def determine_state_class(key: str, unit: str | None) -> SensorStateClass | None:
    """Bestimme State-Klasse."""
    if key in TEXT_VALUE_SENSORS or key in _TIMESTAMP_KEYS or key in NO_UNIT_SENSORS or key in RUNTIME_SENSORS:
        return None
    if unit in {"°C", "bar", "mV", "V", "W", "mg/l", "ppm", "%", "RPM"}:
        return SensorStateClass.MEASUREMENT
    if "total" in key.lower() or "daily" in key_lower:
        return SensorStateClass.TOTAL_INCREASING
    return None

def should_skip_sensor(key: str, raw_value) -> bool:
    """Prüfe, ob Sensor übersprungen werden soll."""
    return (
        isinstance(raw_value, str) and raw_value.strip() in ("[]", "{}", "") or
        (key in RUNTIME_SENSORS and (":" in str(raw_value) or any(s in str(raw_value).lower() for s in ("h", "m", "s"))) or
        key in NON_TEMPERATURE_SENSORS or key.startswith("_")
    )

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Richte Sensoren ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    sensors = []
    data_keys = set(coordinator.data.keys())
    all_predefined_sensors = {**TEMP_SENSORS, **WATER_CHEM_SENSORS, **ANALOG_SENSORS}

    for key, info in all_predefined_sensors.items():
        if key not in data_keys or should_skip_sensor(key, coordinator.data.get(key)) or (feature_id := SENSOR_FEATURE_MAP.get(key)) and feature_id not in active_features:
            continue
        sensors.append(VioletSensor(coordinator, config_entry, VioletSensorEntityDescription(
            key=key, name=info["name"], icon=info.get("icon"),
            native_unit_of_measurement=info.get("unit"),
            device_class=determine_device_class(key, info.get("unit")),
            state_class=determine_state_class(key, info.get("unit")),
            feature_id=feature_id
        )))

    for key in data_keys - set(all_predefined_sensors):
        raw_value = coordinator.data.get(key)
        if should_skip_sensor(key, raw_value) or (feature_id := SENSOR_FEATURE_MAP.get(key)) and feature_id not in active_features:
            continue
        unit = None if key in NO_UNIT_SENSORS else UNIT_MAP.get(key)
        sensors.append(VioletSensor(coordinator, config_entry, VioletSensorEntityDescription(
            key=key, name=key.replace("_", " ").title(),
            icon=(
                "mdi:thermometer" if unit == "°C" else
                "mdi:gauge" if unit in {"bar", "Pa"} else
                "mdi:flash" if unit in {"mV", "V"} else
                "mdi:lightning-bolt" if unit == "W" else
                "mdi:test-tube" if unit in {"mg/l", "ppm"} else
                "mdi:speedometer" if unit == "RPM" else
                "mdi:clock" if key in _TIMESTAMP_KEYS else
                "mdi:text" if key in TEXT_VALUE_SENSORS else
                "mdi:information"
            ),
            native_unit_of_measurement=unit,
            device_class=determine_device_class(key, unit),
            state_class=determine_state_class(key, unit),
            feature_id=feature_id,
            entity_category=EntityCategory.DIAGNOSTIC if key.startswith(("SYSTEM_", "CPU_")) else None
        )))

    if sensors:
        async_add_entities(sensors)
        _LOGGER.info("%d Sensoren hinzugefügt", len(sensors))
    else:
        _LOGGER.warning("Keine Sensoren hinzugefügt")
