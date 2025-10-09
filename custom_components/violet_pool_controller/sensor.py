"""Sensor Integration für den Violet Pool Controller."""
import logging
from datetime import datetime, timezone

from homeassistant.components.sensor import (
    SensorEntity, 
    SensorDeviceClass, 
    SensorStateClass, 
    SensorEntityDescription
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
    UNIT_MAP, 
    NO_UNIT_SENSORS, 
    SENSOR_FEATURE_MAP
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Timestamp detection
_TIMESTAMP_SUFFIXES = (
    "_LAST_ON", "_LAST_OFF", "_LAST_AUTO_RUN", "_LAST_MANUAL_RUN", 
    "_LAST_CAN_RESET", "_TIMESTAMP"
)
_TIMESTAMP_KEYS = {
    "CURRENT_TIME_UNIX"
} | {
    key for key in UNIT_MAP 
    if any(key.upper().endswith(suffix) for suffix in _TIMESTAMP_SUFFIXES)
}

# Text value sensors that should remain as strings
TEXT_VALUE_SENSORS = {
    "DOS_1_CL_STATE", "DOS_4_PHM_STATE", "DOS_5_PHP_STATE", 
    "HEATERSTATE", "SOLARSTATE", "PUMPSTATE",
    "BACKWASHSTATE", "OMNI_STATE", "BACKWASH_OMNI_STATE", 
    "SOLAR_STATE", "HEATER_STATE", "PUMP_STATE",
    "FILTER_STATE", "OMNI_MODE", "FILTER_MODE", "SOLAR_MODE", 
    "HEATER_MODE", "DISPLAY_MODE",
    "OPERATING_MODE", "MAINTENANCE_MODE", "ERROR_CODE", 
    "LAST_ERROR", "VERSION_CODE", "CHECKSUM",
    "RULE_RESULT", "LAST_MOVING_DIRECTION", "COVER_DIRECTION", 
    "SW_VERSION", "SW_VERSION_CARRIER",
    "HW_VERSION_CARRIER", "FW", "VERSION", "VERSION_INFO", 
    "HARDWARE_VERSION", "CPU_GOV",
    "HW_SERIAL_CARRIER", "SERIAL_NUMBER", "MAC_ADDRESS", "IP_ADDRESS", 
    "DOS_1_CL_REMAINING_RANGE", "DOS_4_PHM_REMAINING_RANGE", 
    "DOS_5_PHP_REMAINING_RANGE", 
    "DOS_6_FLOC_REMAINING_RANGE", "BACKWASH_OMNI_MOVING", 
    "BACKWASH_DELAY_RUNNING", 
    "BACKWASH_STATE", "REFILL_STATE", "BATHING_AI_SURVEILLANCE_STATE", 
    "BATHING_AI_PUMP_STATE", 
    "OVERFLOW_REFILL_STATE", "OVERFLOW_DRYRUN_STATE", 
    "OVERFLOW_OVERFILL_STATE",
    "time", "TIME", "CURRENT_TIME"
}

# Runtime sensors - usually formatted time strings
RUNTIME_SENSORS = {
    "ECO_RUNTIME", "LIGHT_RUNTIME", "PUMP_RUNTIME", "BACKWASH_RUNTIME", 
    "SOLAR_RUNTIME", "HEATER_RUNTIME",
    "DOS_1_CL_RUNTIME", "DOS_4_PHM_RUNTIME", "DOS_5_PHP_RUNTIME", 
    "DOS_6_FLOC_RUNTIME",
    "HEATER_POSTRUN_TIME", "SOLAR_POSTRUN_TIME",
    "REFILL_TIMEOUT", "CPU_UPTIME", "DEVICE_UPTIME", "RUNTIME", 
    "POSTRUN_TIME",
}

# Add extension and OMNI runtime sensors
RUNTIME_SENSORS.update({
    f"EXT{i}_{j}_RUNTIME" for i in (1, 2) for j in range(1, 9)
})
RUNTIME_SENSORS.update({
    f"OMNI_DC{i}_RUNTIME" for i in range(1, 6)
})
RUNTIME_SENSORS.update({
    f"PUMP_RPM_{i}_RUNTIME" for i in range(4)
})
RUNTIME_SENSORS.update({
    f"PUMP_RPM_{i}_LAST_ON" for i in range(4)
})
RUNTIME_SENSORS.update({
    f"PUMP_RPM_{i}_LAST_OFF" for i in range(4)
})

# Non-temperature onewire sensors (status info)
NON_TEMPERATURE_SENSORS = {
    f"onewire{i}_{suffix}" 
    for i in range(1, 13) 
    for suffix in ("rcode", "romcode", "state")
}

# Boolean sensors that contain True/False values
BOOLEAN_VALUE_SENSORS = {
    "OVERFLOW_REFILL_STATE", "OVERFLOW_DRYRUN_STATE", "OVERFLOW_OVERFILL_STATE",
    "BACKWASH_OMNI_MOVING", "BACKWASH_DELAY_RUNNING", 
    "BATHING_AI_SURVEILLANCE_STATE",
    "BATHING_AI_PUMP_STATE",
}
BOOLEAN_VALUE_SENSORS.update({
    f"onewire{i}_state" for i in range(1, 13)
})

# Combine text sensors
TEXT_VALUE_SENSORS.update(RUNTIME_SENSORS)
TEXT_VALUE_SENSORS.update(BOOLEAN_VALUE_SENSORS)

# Time-formatted sensors that should be treated as text
TIME_FORMAT_SENSORS = {
    "HEATER_POSTRUN_TIME", "SOLAR_POSTRUN_TIME", "CPU_UPTIME", "DEVICE_UPTIME",
}
TIME_FORMAT_SENSORS.update({
    f"PUMP_RPM_{i}_LAST_ON" for i in range(4)
})
TIME_FORMAT_SENSORS.update({
    f"PUMP_RPM_{i}_LAST_OFF" for i in range(4)
})

# Flow rate sensors - these should have numeric values
FLOW_RATE_SENSORS = {
    "ADC3_value", "IMP2_value", "flow_rate_adc3_priority"
}


class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Repräsentation eines Sensors."""
    
    entity_description: SensorEntityDescription

    def __init__(
        self, 
        coordinator: VioletPoolDataUpdateCoordinator, 
        config_entry: ConfigEntry, 
        description: SensorEntityDescription
    ) -> None:
        """Initialisiere Sensor."""
        super().__init__(coordinator, config_entry, description)
        self._logger = logging.getLogger(f"{DOMAIN}.sensor.{description.key}")
        
        _LOGGER.debug(
            "Sensor initialisiert: %s (Key: %s, Klasse: %s)",
            description.name,
            description.key,
            description.device_class
        )

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """
        Gibt nativen Wert zurück.
        
        Wandelt Werte je nach Sensor-Typ um:
        - Timestamps → datetime Objekte
        - Text/Runtime → Strings
        - Numeric → float/int
        
        Returns:
            Konvertierter Sensor-Wert
        """
        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)
        
        if raw_value is None:
            self._logger.debug("Kein Wert verfügbar für %s", key)
            return None
        
        # Handle timestamp values (UNIX timestamps)
        if key in _TIMESTAMP_KEYS and key not in TIME_FORMAT_SENSORS:
            try:
                timestamp = float(raw_value)
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                self._logger.debug(
                    "Timestamp für %s: %.0f → %s",
                    key, timestamp, dt.isoformat()
                )
                return dt
            except (ValueError, TypeError) as err:
                self._logger.warning(
                    "Timestamp-Konvertierung fehlgeschlagen für %s: %s (%s)",
                    key, raw_value, err
                )
                return None
        
        # Handle text values, time-formatted strings, and boolean values
        if (key in TEXT_VALUE_SENSORS or 
            key in TIME_FORMAT_SENSORS or 
            key in BOOLEAN_VALUE_SENSORS):
            return str(raw_value)
        
        # Try to convert to numeric value
        try:
            f = float(raw_value)
            
            # Round based on sensor type
            if key == "pH_value":
                return round(f, 2)
            elif key in {
                "onewire1_value", "onewire2_value", "onewire3_value",
                "onewire4_value", "onewire5_value", "onewire6_value"
            }:
                return round(f, 1)
            elif "temp" in key.lower():
                return round(f, 1)
            
            # Return integer if it's a whole number
            if f.is_integer():
                return int(f)
            
            return f
            
        except (ValueError, TypeError):
            # If conversion fails, return as string
            return str(raw_value)


class VioletFlowRateSensor(VioletPoolControllerEntity, SensorEntity):
    """
    Spezieller Förderleistungs-Sensor mit ADC3/IMP2 Priorität.
    
    Priorisiert ADC3_value über IMP2_value für genauere Messungen.
    """

    def __init__(
        self, 
        coordinator: VioletPoolDataUpdateCoordinator, 
        config_entry: ConfigEntry
    ) -> None:
        """Initialisiere Förderleistungs-Sensor."""
        description = SensorEntityDescription(
            key="flow_rate_adc3_priority",
            name="Förderleistung",
            icon="mdi:pump",
            native_unit_of_measurement="m³/h",
            device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
            state_class=SensorStateClass.MEASUREMENT,
        )
        super().__init__(coordinator, config_entry, description)
        
        _LOGGER.info(
            "Förderleistungs-Sensor initialisiert (Priorität: ADC3 > IMP2)"
        )

    @property
    def native_value(self) -> float | None:
        """
        Priorisiert ADC3_value über IMP2_value für Förderleistung.
        
        Returns:
            Förderleistung in m³/h oder None
        """
        # Prüfe ADC3_value zuerst (höchste Priorität)
        adc3_value = self.coordinator.data.get("ADC3_value")
        if adc3_value is not None:
            try:
                value = round(float(adc3_value), 2)
                _LOGGER.debug("Förderleistung von ADC3: %.2f m³/h", value)
                return value
            except (ValueError, TypeError) as err:
                _LOGGER.warning(
                    "ADC3_value kann nicht zu Float konvertiert werden: %s (%s)",
                    adc3_value, err
                )

        # Fallback auf IMP2_value
        imp2_value = self.coordinator.data.get("IMP2_value")
        if imp2_value is not None:
            try:
                value = round(float(imp2_value), 2)
                _LOGGER.debug("Förderleistung von IMP2 (Fallback): %.2f m³/h", value)
                return value
            except (ValueError, TypeError) as err:
                _LOGGER.warning(
                    "IMP2_value kann nicht zu Float konvertiert werden: %s (%s)",
                    imp2_value, err
                )

        _LOGGER.debug("Keine Förderleistungsdaten verfügbar (ADC3/IMP2)")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """
        Zusätzliche Attribute für Debugging und Transparenz.
        
        Returns:
            Dictionary mit Debug-Informationen
        """
        adc3_value = self.coordinator.data.get("ADC3_value")
        imp2_value = self.coordinator.data.get("IMP2_value")
        
        source = "None"
        if adc3_value is not None:
            source = "ADC3"
        elif imp2_value is not None:
            source = "IMP2"

        return {
            "adc3_raw_value": str(adc3_value) if adc3_value is not None else "Nicht verfügbar",
            "imp2_raw_value": str(imp2_value) if imp2_value is not None else "Nicht verfügbar", 
            "data_source": source,
            "sensor_priority": "ADC3 > IMP2",
            "unit": "m³/h",
            "description": "Förderleistung der Filterpumpe"
        }

    @property
    def available(self) -> bool:
        """
        Sensor ist verfügbar wenn mindestens eine Quelle verfügbar ist.
        
        Returns:
            True wenn ADC3 oder IMP2 verfügbar
        """
        adc3_available = self.coordinator.data.get("ADC3_value") is not None
        imp2_available = self.coordinator.data.get("IMP2_value") is not None
        is_available = super().available and (adc3_available or imp2_available)
        
        if not is_available:
            _LOGGER.debug("Förderleistungs-Sensor nicht verfügbar")
        
        return is_available

    def is_boolean_value(value) -> bool:
    if not isinstance(value, (str, bool)):
        return False
    
    str_value = str(value).lower().strip()
    return str_value in ('true', 'false', '1', '0', 'on', 'off', 'yes', 'no')


def determine_device_class(
    key: str, 
    unit: str | None, 
    raw_value=None
) -> SensorDeviceClass | None:
    """
    Bestimmt Device-Klasse mit korrekter Unit-Validierung.
    
    Args:
        key: Sensor-Key
        unit: Einheit
        raw_value: Rohdaten-Wert
        
    Returns:
        Passende SensorDeviceClass oder None
    """
    # Boolean sensors sollten keine device class haben
    if key in BOOLEAN_VALUE_SENSORS or (raw_value is not None and is_boolean_value(raw_value)):
        return None
    
    # pH sensor bekommt pH device class
    if key == "pH_value":
        return SensorDeviceClass.PH
    
    # CPU temperature sensors sollten °C haben
    if key in {
        "SYSTEM_cpu_temperature", 
        "SYSTEM_carrier_cpu_temperature", 
        "SYSTEM_DosageModule_cpu_temperature"
    }:
        return SensorDeviceClass.TEMPERATURE
    
    # Flow rate sensors - nur wenn nicht boolean
    if key in FLOW_RATE_SENSORS and not (raw_value is not None and is_boolean_value(raw_value)):
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


def determine_state_class(
    key: str, 
    unit: str | None, 
    raw_value=None
) -> SensorStateClass | None:
    """
    Bestimmt State-Klasse.
    
    Args:
        key: Sensor-Key
        unit: Einheit
        raw_value: Rohdaten-Wert
        
    Returns:
        Passende SensorStateClass oder None
    """
    # Boolean value sensors sollten keine state class haben
    if key in BOOLEAN_VALUE_SENSORS or (raw_value is not None and is_boolean_value(raw_value)):
        return None
    
    # Text/Timestamp/Runtime sensors haben keine state class
    if (key in TEXT_VALUE_SENSORS or 
        key in _TIMESTAMP_KEYS or 
        key in NO_UNIT_SENSORS or 
        key in RUNTIME_SENSORS or 
        key in TIME_FORMAT_SENSORS):
        return None
    
    # Measurement für diese Units
    if unit in {"°C", "bar", "mV", "V", "W", "mg/l", "ppm", "%", "RPM", "m³/h", "cm/s"}:
        return SensorStateClass.MEASUREMENT
    
    # pH hat keine Unit mehr, aber ist trotzdem measurement
    if key == "pH_value":
        return SensorStateClass.MEASUREMENT
    
    # Total für kumulative Werte
    key_lower = key.lower()
    if "total" in key_lower or "daily" in key_lower:
        return SensorStateClass.TOTAL_INCREASING
    
    return None


def get_icon(unit: str | None, key: str, raw_value=None) -> str:
    """
    Bestimmt Icon basierend auf Unit und Key.
    
    Args:
        unit: Einheit
        key: Sensor-Key
        raw_value: Rohdaten-Wert
        
    Returns:
        MDI Icon-String
    """
    # Boolean value sensors bekommen toggle icon
    if key in BOOLEAN_VALUE_SENSORS or (raw_value is not None and is_boolean_value(raw_value)):
        return "mdi:toggle-switch"
    
    # Spezielle Icons für bekannte Keys
    if key == "pH_value":
        return "mdi:flask"
    elif key in FLOW_RATE_SENSORS or "flow" in key.lower():
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
    """
    Prüft, ob Sensor übersprungen werden soll.
    
    Args:
        key: Sensor-Key
        raw_value: Rohdaten-Wert
        
    Returns:
        True wenn Sensor übersprungen werden soll
    """
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


def apply_adc3_imp2_mapping(coordinator_data: dict) -> None:
    """
    Wendet ADC3/IMP2 Mapping für Förderleistung an.
    
    Priorisiert ADC3_value über IMP2_value für bessere Genauigkeit.
    
    Args:
        coordinator_data: Dictionary mit Controller-Daten
    """
    if not coordinator_data:
        return
    
    adc3_value = coordinator_data.get("ADC3_value")
    imp2_value = coordinator_data.get("IMP2_value")
    
    _LOGGER.debug("ADC3/IMP2 Förderleistung Mapping:")
    _LOGGER.debug("  ADC3_value: %s", adc3_value)
    _LOGGER.debug("  IMP2_value: %s", imp2_value)
    
    # Priorisiere ADC3_value über IMP2_value
    if adc3_value is not None:
        # Sichere originalen IMP2 Wert falls vorhanden
        if imp2_value is not None:
            coordinator_data["IMP2_value_original"] = imp2_value
        
        # Ersetze IMP2_value durch ADC3_value für Kompatibilität
        coordinator_data["IMP2_value"] = adc3_value
        _LOGGER.info(
            "ADC3_value (%s) mapped zu IMP2_value für Kompatibilität",
            adc3_value
        )
        
        # Behalte ADC3_value als Referenz
        coordinator_data["ADC3_value_reference"] = adc3_value
        _LOGGER.debug("ADC3_value als Referenz beibehalten")
        
    elif imp2_value is not None:
        _LOGGER.info("Verwende originalen IMP2_value (%s)", imp2_value)
    else:
        _LOGGER.warning("Weder ADC3_value noch IMP2_value verfügbar")


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """
    Richtet Sensoren ein mit ADC3/IMP2 Fix und korrekten Units.
    
    Args:
        hass: Home Assistant Instanz
        config_entry: Config Entry
        async_add_entities: Callback zum Hinzufügen von Entities
    """
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Aktive Features aus Options oder Data holen
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, 
        config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    
    _LOGGER.debug(
        "Setup Sensoren für '%s' mit Features: %s",
        config_entry.title,
        ", ".join(active_features)
    )
    
    sensors = []
    
    # ADC3/IMP2 Förderleistung Mapping anwenden
    apply_adc3_imp2_mapping(coordinator.data)
    
    data_keys = set(coordinator.data.keys())
    _LOGGER.debug("Verfügbare Daten-Keys: %d", len(data_keys))
    
    # Unit Fixes für bekannte Probleme
    unit_fixes = {
        # pH sensor sollte keine unit haben (per Home Assistant Spec)
        "pH_value": None,
        
        # CPU temperature sensors müssen °C haben
        "SYSTEM_cpu_temperature": "°C",
        "SYSTEM_carrier_cpu_temperature": "°C", 
        "SYSTEM_DosageModule_cpu_temperature": "°C",
        "CPU_TEMP": "°C",
        "CPU_TEMP_CARRIER": "°C",
        
        # Flow rate sensors einheitlich
        "ADC3_value": "m³/h",
        "IMP2_value": "m³/h",
        "ADC3_value_reference": "m³/h",
        
        # Boolean sensors sollten keine units haben
        **{key: None for key in BOOLEAN_VALUE_SENSORS},
    }
    
    # Apply unit fixes to UNIT_MAP
    for key, unit in unit_fixes.items():
        if key in data_keys:
            if unit is None and key in UNIT_MAP:
                # Remove unit für pH und boolean sensors
                del UNIT_MAP[key]
            else:
                UNIT_MAP[key] = unit

    # Combine all predefined sensors
    all_predefined_sensors = {
        **TEMP_SENSORS, 
        **WATER_CHEM_SENSORS, 
        **ANALOG_SENSORS
    }

    # Add predefined sensors
    predefined_count = 0
    for key, info in all_predefined_sensors.items():
        if key not in data_keys:
            continue
        
        if should_skip_sensor(key, coordinator.data.get(key)):
            _LOGGER.debug("Überspringe Sensor %s (Keine Daten)", key)
            continue
        
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Überspringe Sensor %s (Feature %s nicht aktiv)",
                key, feature_id
            )
            continue
        
        raw_value = coordinator.data.get(key)
        
        # Apply unit fixes
        unit = info.get("unit")
        if key in unit_fixes:
            unit = unit_fixes[key]
        
        # Use proper SensorEntityDescription
        sensors.append(VioletSensor(
            coordinator, 
            config_entry, 
            SensorEntityDescription(
                key=key,
                name=info["name"],
                icon=info.get("icon") or get_icon(unit, key, raw_value),
                native_unit_of_measurement=unit,
                device_class=determine_device_class(key, unit, raw_value),
                state_class=determine_state_class(key, unit, raw_value),
                entity_category=EntityCategory.DIAGNOSTIC if key.startswith(("SYSTEM_", "CPU_")) else None,
            )
        ))
        predefined_count += 1

    _LOGGER.debug("%d vordefinierte Sensoren hinzugefügt", predefined_count)

    # Spezieller Förderleistungs-Sensor mit ADC3-Priorität
    if any(key in coordinator.data for key in ["ADC3_value", "IMP2_value"]):
        adc3_val = coordinator.data.get("ADC3_value")
        imp2_val = coordinator.data.get("IMP2_value")
        
        # Nur hinzufügen wenn Werte nicht boolean sind
        if not (is_boolean_value(adc3_val) or is_boolean_value(imp2_val)):
            sensors.append(VioletFlowRateSensor(coordinator, config_entry))
            _LOGGER.info("Förderleistungs-Sensor mit ADC3-Priorität hinzugefügt")

    # Add dynamic sensors from coordinator data
    dynamic_count = 0
    for key in data_keys - set(all_predefined_sensors):
        raw_value = coordinator.data.get(key)
        
        if should_skip_sensor(key, raw_value):
            continue
        
        # Skip already handled special sensors
        if key in {"ADC3_value_reference", "IMP2_value_original"}:
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
        
        # Boolean sensors sollten keine units haben
        if is_boolean_value(raw_value):
            unit = None
        
        # Create nice name from key
        name = key.replace("_", " ").title()
        
        # Use proper SensorEntityDescription
        sensors.append(VioletSensor(
            coordinator, 
            config_entry, 
            SensorEntityDescription(
                key=key,
                name=name,
                icon=get_icon(unit, key, raw_value),
                native_unit_of_measurement=unit,
                device_class=determine_device_class(key, unit, raw_value),
                state_class=determine_state_class(key, unit, raw_value),
                entity_category=EntityCategory.DIAGNOSTIC if key.startswith(("SYSTEM_", "CPU_")) or key in TEXT_VALUE_SENSORS else None,
            )
        ))
        dynamic_count += 1

    _LOGGER.debug("%d dynamische Sensoren hinzugefügt", dynamic_count)

    # Entities hinzufügen
    if sensors:
        async_add_entities(sensors)
        _LOGGER.info(
            "%d Sensoren für '%s' hinzugefügt (%d vordefiniert, %d dynamisch)",
            len(sensors),
            config_entry.title,
            predefined_count,
            dynamic_count
        )
        
        # Final debug info
        if any(key in coordinator.data for key in ["ADC3_value", "IMP2_value"]):
            adc3 = coordinator.data.get("ADC3_value")
            imp2 = coordinator.data.get("IMP2_value")
            _LOGGER.info("Förderleistung Status:")
            _LOGGER.info("  ADC3_value: %s", adc3)
            _LOGGER.info("  IMP2_value: %s", imp2)
    else:
        _LOGGER.warning("Keine Sensoren für '%s' hinzugefügt", config_entry.title)