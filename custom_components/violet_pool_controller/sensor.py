"""Sensor Integration für den Violet Pool Controller - COMPLETE AI3 FIX VERSION."""
import logging
from datetime import datetime, timezone

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass, SensorEntityDescription
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
    *{f"PUMP_RPM_{i}_RUNTIME" for i in range(4)},
    # Add PUMP_RPM_X_LAST_ON/OFF as text sensors
    *{f"PUMP_RPM_{i}_LAST_ON" for i in range(4)},
    *{f"PUMP_RPM_{i}_LAST_OFF" for i in range(4)},
}

# Non-temperature onewire sensors (status info)
NON_TEMPERATURE_SENSORS = {
    *{f"onewire{i}_{suffix}" for i in range(1, 13) for suffix in ("rcode", "romcode", "state")},
}

# Combine text sensors
TEXT_VALUE_SENSORS.update(RUNTIME_SENSORS)

# Time-formatted sensors that should be treated as text
TIME_FORMAT_SENSORS = {
    *{f"PUMP_RPM_{i}_LAST_ON" for i in range(4)},
    *{f"PUMP_RPM_{i}_LAST_OFF" for i in range(4)},
    "HEATER_POSTRUN_TIME", "SOLAR_POSTRUN_TIME", "CPU_UPTIME", "DEVICE_UPTIME",
}

class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Repräsentation eines Sensors."""
    entity_description: SensorEntityDescription

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry, description: SensorEntityDescription) -> None:
        """Initialisiere Sensor."""
        super().__init__(coordinator, config_entry, description)
        self._logger = logging.getLogger(f"{DOMAIN}.{self._attr_unique_id}")

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Gib nativen Wert zurück."""
        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)
        
        if raw_value is None:
            return None
            
        # Handle timestamp values (UNIX timestamps)
        if key in _TIMESTAMP_KEYS and key not in TIME_FORMAT_SENSORS:
            try:
                return datetime.fromtimestamp(float(raw_value), tz=timezone.utc) if raw_value else None
            except (ValueError, TypeError):
                return None
                
        # Handle text values and time-formatted strings
        if key in TEXT_VALUE_SENSORS or key in TIME_FORMAT_SENSORS:
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

class VioletFlowRateSensor(VioletPoolControllerEntity, SensorEntity):
    """Spezieller Förderleistungs-Sensor mit AI3/IMP2 Priorität - COMPLETE FIX."""

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry) -> None:
        """Initialisiere Förderleistungs-Sensor."""
        description = SensorEntityDescription(
            key="flow_rate_ai3_priority",
            name="Förderleistung",
            icon="mdi:pump",
            native_unit_of_measurement="m³/h",
            device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
            state_class=SensorStateClass.MEASUREMENT,
        )
        super().__init__(coordinator, config_entry, description)
        _LOGGER.info("🔧 Förderleistungs-Sensor mit AI3-Priorität initialisiert")

    @property
    def native_value(self) -> float | None:
        """Priorisiere AI3_value über IMP2_value für Förderleistung."""
        # Prüfe AI3_value zuerst (höchste Priorität)
        ai3_value = self.coordinator.data.get("AI3_value")
        if ai3_value is not None:
            try:
                value = round(float(ai3_value), 2)
                _LOGGER.debug("✅ Förderleistung von AI3: %.2f m³/h", value)
                return value
            except (ValueError, TypeError):
                _LOGGER.warning("⚠️ AI3_value kann nicht zu Float konvertiert werden: %s", ai3_value)

        # Fallback auf IMP2_value
        imp2_value = self.coordinator.data.get("IMP2_value")
        if imp2_value is not None:
            try:
                value = round(float(imp2_value), 2)
                _LOGGER.debug("✅ Förderleistung von IMP2 (Fallback): %.2f m³/h", value)
                return value
            except (ValueError, TypeError):
                _LOGGER.warning("⚠️ IMP2_value kann nicht zu Float konvertiert werden: %s", imp2_value)

        _LOGGER.debug("❌ Keine Förderleistungsdaten verfügbar (AI3/IMP2)")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Zusätzliche Attribute für Debugging und Transparenz."""
        ai3_value = self.coordinator.data.get("AI3_value")
        imp2_value = self.coordinator.data.get("IMP2_value")
        
        source = "None"
        if ai3_value is not None:
            source = "AI3"
        elif imp2_value is not None:
            source = "IMP2"

        return {
            "ai3_raw_value": str(ai3_value) if ai3_value is not None else "Nicht verfügbar",
            "imp2_raw_value": str(imp2_value) if imp2_value is not None else "Nicht verfügbar", 
            "data_source": source,
            "sensor_priority": "AI3 > IMP2",
            "unit": "m³/h",
            "description": "Förderleistung der Filterpumpe"
        }

    @property
    def available(self) -> bool:
        """Sensor ist verfügbar wenn mindestens eine Quelle verfügbar ist."""
        ai3_available = self.coordinator.data.get("AI3_value") is not None
        imp2_available = self.coordinator.data.get("IMP2_value") is not None
        return super().available and (ai3_available or imp2_available)

def determine_device_class(key: str, unit: str | None) -> SensorDeviceClass | None:
    """Bestimme Device-Klasse mit korrekter Unit-Validierung."""
    # FIXME 1: pH sensor sollte keine unit haben
    if key == "pH_value":
        return SensorDeviceClass.PH
    
    # FIXME 2: CPU temperature sensors sollten °C haben
    if key in {"SYSTEM_cpu_temperature", "SYSTEM_carrier_cpu_temperature", "SYSTEM_DosageModule_cpu_temperature"}:
        return SensorDeviceClass.TEMPERATURE
    
    # Flow rate sensors
    if key in {"AI3_value", "IMP2_value", "flow_rate_ai3_priority"} or "flow" in key.lower():
        return SensorDeviceClass.VOLUME_FLOW_RATE
    
    # Text/Runtime sensors ohne device class
    if key in RUNTIME_SENSORS or key in TEXT_VALUE_SENSORS or key in TIME_FORMAT_SENSORS:
        return None
        
    key_lower = key.lower()
    
    # Normale Temperatursensoren
    if unit == "°C" or "temp" in key_lower:
        return SensorDeviceClass.TEMPERATURE
    elif unit == "%" and "humidity" in key_lower:
        return SensorDeviceClass.HUMIDITY
    elif unit == "bar" or "pressure" in key_lower:
        return SensorDeviceClass.PRESSURE
    elif unit in {"mV", "V"} or "voltage" in key_lower:
        return SensorDeviceClass.VOLTAGE
    elif unit == "W" or "power" in key_lower:
        return SensorDeviceClass.POWER
    elif key in _TIMESTAMP_KEYS and key not in TIME_FORMAT_SENSORS:
        return SensorDeviceClass.TIMESTAMP
        
    return None

def determine_state_class(key: str, unit: str | None) -> SensorStateClass | None:
    """Bestimme State-Klasse."""
    if (key in TEXT_VALUE_SENSORS or key in _TIMESTAMP_KEYS or 
        key in NO_UNIT_SENSORS or key in RUNTIME_SENSORS or 
        key in TIME_FORMAT_SENSORS):
        return None
        
    if unit in {"°C", "bar", "mV", "V", "W", "mg/l", "ppm", "%", "RPM", "m³/h", "cm/s"}:
        return SensorStateClass.MEASUREMENT
        
    # pH hat keine Unit mehr, aber ist trotzdem measurement
    if key == "pH_value":
        return SensorStateClass.MEASUREMENT
        
    key_lower = key.lower()
    if "total" in key_lower or "daily" in key_lower:
        return SensorStateClass.TOTAL_INCREASING
        
    return None

def get_icon(unit: str | None, key: str) -> str:
    """Bestimme Icon basierend auf Unit und Key."""
    if key == "pH_value":
        return "mdi:flask"
    elif key in {"AI3_value", "IMP2_value", "flow_rate_ai3_priority"} or "flow" in key.lower():
        return "mdi:pump"
    elif unit == "°C":
        return "mdi:thermometer"
    elif unit in {"bar", "Pa"}:
        return "mdi:gauge"
    elif unit in {"mV", "V"}:
        return "mdi:flash"
    elif unit == "W":
        return "mdi:lightning-bolt"
    elif unit in {"mg/l", "ppm"}:
        return "mdi:test-tube"
    elif unit == "RPM":
        return "mdi:speedometer"
    elif unit == "m³/h":
        return "mdi:pump"
    elif unit == "cm/s":
        return "mdi:water-pump"
    elif key in _TIMESTAMP_KEYS:
        return "mdi:clock"
    elif key in TEXT_VALUE_SENSORS or key in TIME_FORMAT_SENSORS:
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
        
    # Skip non-temperature onewire sensors
    if key in NON_TEMPERATURE_SENSORS:
        return True
        
    # Skip private keys
    if key.startswith("_"):
        return True
        
    return False

def apply_ai3_imp2_mapping(coordinator_data: dict) -> None:
    """Wende AI3/IMP2 Mapping für Förderleistung an - COMPLETE FIX."""
    if not coordinator_data:
        return
        
    ai3_value = coordinator_data.get("AI3_value")
    imp2_value = coordinator_data.get("IMP2_value")
    
    _LOGGER.info("🔍 AI3/IMP2 FÖRDERLEISTUNG MAPPING:")
    _LOGGER.info("  AI3_value: %s", ai3_value)
    _LOGGER.info("  IMP2_value: %s", imp2_value)
    
    # Priorisiere AI3_value über IMP2_value
    if ai3_value is not None:
        # Sichere originalen IMP2 Wert falls vorhanden
        if imp2_value is not None:
            coordinator_data["IMP2_value_original"] = imp2_value
            
        # Ersetze IMP2_value durch AI3_value für bestehende Sensoren
        coordinator_data["IMP2_value"] = ai3_value
        _LOGGER.info("  ✅ AI3_value (%s) mapped zu IMP2_value für Kompatibilität", ai3_value)
        
        # Behalte AI3_value für speziellen Sensor
        coordinator_data["AI3_value_reference"] = ai3_value
        _LOGGER.info("  ✅ AI3_value als Referenz beibehalten")
        
    elif imp2_value is not None:
        _LOGGER.info("  ✅ Verwende originalen IMP2_value (%s)", imp2_value)
    else:
        _LOGGER.warning("  ⚠️ Weder AI3_value noch IMP2_value verfügbar")

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Richte Sensoren ein mit AI3/IMP2 Fix und korrekten Units - COMPLETE VERSION."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    sensors = []
    
    # *** AI3/IMP2 FÖRDERLEISTUNG MAPPING ANWENDEN ***
    apply_ai3_imp2_mapping(coordinator.data)
    
    data_keys = set(coordinator.data.keys())
    
    # UNIT FIXES
    unit_fixes = {
        # FIXME 1: pH sensor sollte keine unit haben (per Home Assistant Spec)
        "pH_value": None,
        
        # FIXME 2: CPU temperature sensors müssen °C haben
        "SYSTEM_cpu_temperature": "°C",
        "SYSTEM_carrier_cpu_temperature": "°C", 
        "SYSTEM_DosageModule_cpu_temperature": "°C",
        "CPU_TEMP": "°C",
        "CPU_TEMP_CARRIER": "°C",
        
        # FIXME 3: Flow rate sensors einheitlich
        "AI3_value": "m³/h",
        "IMP2_value": "m³/h",
        "AI3_value_reference": "m³/h",
    }
    
    # Apply unit fixes to UNIT_MAP
    for key, unit in unit_fixes.items():
        if key in data_keys:
            if unit is None and key in UNIT_MAP:
                # Remove unit for pH
                del UNIT_MAP[key]
            else:
                UNIT_MAP[key] = unit

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
        
        # Apply unit fixes
        unit = info.get("unit")
        if key in unit_fixes:
            unit = unit_fixes[key]
            
        # Use proper SensorEntityDescription
        sensors.append(VioletSensor(coordinator, config_entry, SensorEntityDescription(
            key=key,
            name=info["name"],
            icon=info.get("icon"),
            native_unit_of_measurement=unit,
            device_class=determine_device_class(key, unit),
            state_class=determine_state_class(key, unit),
            entity_category=EntityCategory.DIAGNOSTIC if key.startswith(("SYSTEM_", "CPU_")) else None,
        )))

    # *** SPEZIELLER FÖRDERLEISTUNGS-SENSOR MIT AI3-PRIORITÄT ***
    if any(key in coordinator.data for key in ["AI3_value", "IMP2_value"]):
        sensors.append(VioletFlowRateSensor(coordinator, config_entry))
        _LOGGER.info("✅ Förderleistungs-Sensor mit AI3-Priorität hinzugefügt")

    # Add dynamic sensors from coordinator data
    for key in data_keys - set(all_predefined_sensors):
        raw_value = coordinator.data.get(key)
        if should_skip_sensor(key, raw_value):
            continue
            
        # Skip already handled special sensors
        if key in {"AI3_value_reference", "IMP2_value_original"}:
            continue
            
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            continue
        
        # Determine unit from mapping or none, with fixes applied
        unit = None
        if key not in NO_UNIT_SENSORS:
            unit = UNIT_MAP.get(key)
            if key in unit_fixes:
                unit = unit_fixes[key]
        
        # Create nice name from key
        name = key.replace("_", " ").title()
        
        # Use proper SensorEntityDescription
        sensors.append(VioletSensor(coordinator, config_entry, SensorEntityDescription(
            key=key,
            name=name,
            icon=get_icon(unit, key),
            native_unit_of_measurement=unit,
            device_class=determine_device_class(key, unit),
            state_class=determine_state_class(key, unit),
            entity_category=EntityCategory.DIAGNOSTIC if key.startswith(("SYSTEM_", "CPU_")) or key in TEXT_VALUE_SENSORS else None,
        )))

    if sensors:
        async_add_entities(sensors)
        _LOGGER.info("✅ %d Sensoren hinzugefügt (mit AI3/IMP2-Fix und Unit-Fixes)", len(sensors))
        
        # Final debug info
        if any(key in coordinator.data for key in ["AI3_value", "IMP2_value"]):
            ai3 = coordinator.data.get("AI3_value")
            imp2 = coordinator.data.get("IMP2_value")
            _LOGGER.info("🎯 FINAL FÖRDERLEISTUNG STATUS:")
            _LOGGER.info("  AI3_value: %s", ai3)
            _LOGGER.info("  IMP2_value: %s (möglicherweise von AI3 überschrieben)", imp2)
            _LOGGER.info("  Spezieller Förderleistungs-Sensor: AKTIV")
    else:
        _LOGGER.warning("❌ Keine Sensoren hinzugefügt")
