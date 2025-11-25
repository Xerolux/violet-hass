"""Sensor Integration für den Violet Pool Controller."""
import logging
from datetime import datetime, timezone
from typing import Any

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
    STATUS_SENSORS,
    CONF_ACTIVE_FEATURES,
    CONF_SELECTED_SENSORS,  # WICHTIG: Neuer Import für die Sensor-Auswahl
    UNIT_MAP,
    NO_UNIT_SENSORS,
    SENSOR_FEATURE_MAP,
    VioletState
)
from .error_codes import get_error_info
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
    "HW_VERSION_CARRIER", "FW", "fw", "VERSION", "VERSION_INFO",
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
    "time", "TIME", "CURRENT_TIME",
    # ✅ Neue System-Status-Sensoren
    "LOAD_AVG", "pump_rs485_pwr",
    "SYSTEM_carrier_alive_count", "SYSTEM_carrier_alive_faultcount",
    "SYSTEM_dosagemodule_alive_count", "SYSTEM_dosagemodule_alive_faultcount",
    "SYSTEM_ext1module_alive_count", "SYSTEM_ext1module_alive_faultcount",
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
    """Representation of a Violet Pool sensor."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SensorEntityDescription
    ) -> None:
        """
        Initialize the sensor.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            description: The sensor entity description.
        """
        super().__init__(coordinator, config_entry, description)
        self._logger = logging.getLogger(f"{DOMAIN}.sensor.{description.key}")

        _LOGGER.debug(
            "Sensor initialized: %s (Key: %s, Class: %s)",
            description.name,
            description.key,
            description.device_class
        )

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """
        Return the native value of the sensor.

        Converts values based on sensor type:
        - Timestamps -> datetime objects
        - Text/Runtime -> Strings
        - Numeric -> float/int

        Returns:
            The native value or None.
        """
        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)

        if raw_value is None:
            self._logger.debug("Kein Wert verfügbar für %s", key)
            return None

        if key in _TIMESTAMP_KEYS and key not in TIME_FORMAT_SENSORS:
            try:
                timestamp = float(raw_value)
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                return dt
            except (ValueError, TypeError) as err:
                self._logger.warning("Timestamp-Konvertierung fehlgeschlagen für %s: %s (%s)", key, raw_value, err)
                return None

        if (key in TEXT_VALUE_SENSORS or key in TIME_FORMAT_SENSORS or key in BOOLEAN_VALUE_SENSORS):
            return str(raw_value)

        try:
            f = float(raw_value)
            if key == "pH_value":
                return round(f, 2)
            if "temp" in key.lower() or "onewire" in key.lower():
                return round(f, 1)
            if f.is_integer():
                return int(f)
            return f
        except (ValueError, TypeError):
            return str(raw_value)


class VioletStatusSensor(VioletSensor):
    """Sensor for status values using VioletState (e.g. Pump Auto/Manual)."""

    @property
    def native_value(self) -> str | None:
        """
        Return the native value for the status sensor.

        Returns:
            The display string for the status.
        """
        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)
        if raw_value is None:
            return None

        # Use VioletState to get display string (e.g. "Auto (Active)")
        state = VioletState(raw_value, key)
        return state.display_mode

    @property
    def icon(self) -> str:
        """
        Return the icon for the status sensor.

        Returns:
            The icon string.
        """
        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)
        if raw_value is None:
            return super().icon
        state = VioletState(raw_value, key)
        return state.icon


class VioletErrorCodeSensor(VioletSensor):
    """Specialized sensor that resolves error codes to descriptive text."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        value_key: str,
    ) -> None:
        """
        Initialize the error code sensor.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            value_key: The key containing the error code.
        """
        description = SensorEntityDescription(
            key=value_key,
            name="Last Error Code",
            icon="mdi:alert-circle",
            entity_category=EntityCategory.DIAGNOSTIC,
        )
        super().__init__(coordinator, config_entry, description)
        self._value_key = value_key

    def _get_error_code(self) -> str | None:
        """Get the raw error code."""
        value = self.get_value(self._value_key)
        if value is None:
            return None
        code = str(value).strip()
        return code or None

    @property
    def native_value(self) -> str | None:
        """
        Return the error code description.

        Returns:
            The error code subject or None.
        """
        code = self._get_error_code()
        if code is None:
            return None
        return get_error_info(code)["subject"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """
        Return additional attributes for the error code.

        Returns:
            A dictionary of attributes.
        """
        code = self._get_error_code()
        if code is None:
            return {}
        info = get_error_info(code)
        return {
            "code": code,
            "type": info.get("type"),
            "severity": info.get("severity"),
            "description": info.get("description"),
        }


class VioletFlowRateSensor(VioletPoolControllerEntity, SensorEntity):
    """Special flow rate sensor prioritizing ADC3 over IMP2."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry
    ) -> None:
        """
        Initialize the flow rate sensor.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
        """
        description = SensorEntityDescription(
            key="flow_rate_adc3_priority",
            name="Flow Rate",
            icon="mdi:pump",
            native_unit_of_measurement="m³/h",
            device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
            state_class=SensorStateClass.MEASUREMENT,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        """
        Return the flow rate value.

        Prioritizes ADC3_value over IMP2_value.

        Returns:
            The flow rate value or None.
        """
        adc3_value = self.coordinator.data.get("ADC3_value")
        if adc3_value is not None:
            try:
                return round(float(adc3_value), 2)
            except (ValueError, TypeError):
                pass

        imp2_value = self.coordinator.data.get("IMP2_value")
        if imp2_value is not None:
            try:
                return round(float(imp2_value), 2)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """
        Return additional attributes for debugging.

        Returns:
            A dictionary of debug attributes.
        """
        adc3 = self.coordinator.data.get("ADC3_value")
        imp2 = self.coordinator.data.get("IMP2_value")
        source = "ADC3" if adc3 is not None else "IMP2" if imp2 is not None else "None"
        return {
            "adc3_raw_value": str(adc3) if adc3 is not None else "N/A",
            "imp2_raw_value": str(imp2) if imp2 is not None else "N/A",
            "data_source": source,
        }

    @property
    def available(self) -> bool:
        """
        Check if the sensor is available.

        Available if a source is available.

        Returns:
            True if available, False otherwise.
        """
        return super().available and (
            self.coordinator.data.get("ADC3_value") is not None or
            self.coordinator.data.get("IMP2_value") is not None
        )


def _is_boolean_value(value: Any) -> bool:
    """Check if value represents a boolean."""
    if not isinstance(value, (str, bool)):
        return False
    return str(value).lower().strip() in ('true', 'false', '1', '0', 'on', 'off', 'yes', 'no')


def determine_device_class(key: str, unit: str | None, raw_value=None) -> SensorDeviceClass | None:
    """
    Determine the device class for a sensor.

    Args:
        key: The sensor key.
        unit: The unit of measurement.
        raw_value: The raw value.

    Returns:
        The device class or None.
    """
    if key in BOOLEAN_VALUE_SENSORS or (raw_value is not None and _is_boolean_value(raw_value)):
        return None
    if key == "pH_value":
        return SensorDeviceClass.PH
    if unit == "°C":
        return SensorDeviceClass.TEMPERATURE
    # Temperature device class requires a valid temperature unit. Keep diagnostic
    # sensors without units (e.g. SYSTEM_*_cpu_temperature) unitless for
    # backwards-compatible statistics while avoiding Home Assistant warnings.
    if unit is None:
        return None
    if "temp" in key.lower():
        return SensorDeviceClass.TEMPERATURE
    if unit == "%":
        return SensorDeviceClass.HUMIDITY
    if unit == "bar":
        return SensorDeviceClass.PRESSURE
    if unit in {"mV", "V"}:
        return SensorDeviceClass.VOLTAGE
    if unit == "W":
        return SensorDeviceClass.POWER
    if key in _TIMESTAMP_KEYS and key not in TIME_FORMAT_SENSORS:
        return SensorDeviceClass.TIMESTAMP
    return None


def determine_state_class(key: str, unit: str | None, raw_value=None) -> SensorStateClass | None:
    """
    Determine the state class for a sensor.

    Args:
        key: The sensor key.
        unit: The unit of measurement.
        raw_value: The raw value.

    Returns:
        The state class or None.
    """
    if key in BOOLEAN_VALUE_SENSORS or (raw_value is not None and _is_boolean_value(raw_value)):
        return None
    if any(k in key for k in TEXT_VALUE_SENSORS | _TIMESTAMP_KEYS | NO_UNIT_SENSORS | RUNTIME_SENSORS):
        return None
    if "total" in key.lower() or "daily" in key.lower():
        return SensorStateClass.TOTAL_INCREASING
    if unit is not None:
        return SensorStateClass.MEASUREMENT
    return None


def get_icon(unit: str | None, key: str, raw_value=None) -> str:
    """
    Determine the icon for a sensor.

    Args:
        unit: The unit of measurement.
        key: The sensor key.
        raw_value: The raw value.

    Returns:
        The icon string.
    """
    is_bool = raw_value is not None and _is_boolean_value(raw_value)
    if key in BOOLEAN_VALUE_SENSORS or is_bool:
        return "mdi:toggle-switch"
    if key == "pH_value":
        return "mdi:flask"
    if "flow" in key.lower():
        return "mdi:pump"
    if unit == "°C":
        return "mdi:thermometer"
    if unit == "bar":
        return "mdi:gauge"
    if unit in {"mV", "V"}:
        return "mdi:flash"
    if key in _TIMESTAMP_KEYS:
        return "mdi:clock"
    return "mdi:information"


def should_skip_sensor(key: str, raw_value) -> bool:
    """
    Check if a sensor should be skipped.

    Args:
        key: The sensor key.
        raw_value: The raw value.

    Returns:
        True if the sensor should be skipped, False otherwise.
    """
    if raw_value is None:
        return True
    raw_str = str(raw_value).strip()
    if raw_str in ("[]", "{}", ""):
        return True
    if key in NON_TEMPERATURE_SENSORS:
        return True
    if key.startswith("_"):
        return True
    return False

# ==========================================================================================
# ======================== NEUE SETUP FUNKTION STARTET HIER ================================
# ==========================================================================================

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """
    Set up sensors based on configuration.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry.
        async_add_entities: Callback to add entities.
    """
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Hole Konfiguration aus Options (primär) oder Data (Fallback)
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    selected_sensors_raw = config_entry.options.get(
        CONF_SELECTED_SENSORS,
        config_entry.data.get(CONF_SELECTED_SENSORS),
    )
    selected_sensors = list(selected_sensors_raw or [])
    selected_sensor_set = set(selected_sensors)

    # WICHTIG: Wenn selected_sensors None ist (alte Konfig), erstellen wir alle Sensoren.
    # Ein leeres Array [] bedeutet, der User hat explizit keine Sensoren ausgewählt.
    create_all_sensors = selected_sensors_raw is None

    if create_all_sensors:
        _LOGGER.info("Keine Sensor-Auswahl gefunden. Erstelle ALLE verfügbaren Sensoren (Abwärtskompatibilität).")
    else:
        _LOGGER.info("Erstelle %d ausgewählte Sensoren.", len(selected_sensors))

    sensors = []
    data_keys = set(coordinator.data.keys())
    all_predefined_sensors = {**TEMP_SENSORS, **WATER_CHEM_SENSORS, **ANALOG_SENSORS, **STATUS_SENSORS}

    handled_special_keys: set[str] = set()

    for error_key in ("LAST_ERROR_CODE", "ERROR_CODE", "LAST_ERROR"):
        if error_key not in data_keys:
            continue
        if not create_all_sensors and error_key not in selected_sensor_set:
            continue
        sensors.append(VioletErrorCodeSensor(coordinator, config_entry, error_key))
        handled_special_keys.add(error_key)
        _LOGGER.info("Fehlercode-Sensor für %s hinzugefügt", error_key)

    # Erstelle nur den speziellen Flow-Sensor, wenn er ausgewählt wurde (oder alle erstellt werden)
    # und die benötigten Daten vorhanden sind.
    flow_sensor_keys_present = any(key in data_keys for key in FLOW_RATE_SENSORS)
    flow_sensor_selected = create_all_sensors or "flow_rate_adc3_priority" in selected_sensor_set

    if flow_sensor_keys_present and flow_sensor_selected:
        sensors.append(VioletFlowRateSensor(coordinator, config_entry))
        _LOGGER.info("Förderleistungs-Sensor mit ADC3-Priorität hinzugefügt.")

    # Alle anderen Sensoren durchlaufen
    for key in sorted(list(data_keys)): # Sortiert für konsistente Reihenfolge
        raw_value = coordinator.data.get(key)

        if key in handled_special_keys:
            _LOGGER.debug("Überspringe Standard-Sensor für %s (spezielle Behandlung)", key)
            continue

        # Logik zum Überspringen von irrelevanten Sensoren
        if should_skip_sensor(key, raw_value):
            continue

        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug("Überspringe Sensor %s (Feature '%s' nicht aktiv)", key, feature_id)
            continue

        # ===============================================================
        # NEUE FILTERLOGIK: Prüfe, ob der Sensor ausgewählt wurde
        # ===============================================================
        if not create_all_sensors and key not in selected_sensor_set:
            # Ausnahme: Wenn der Flow-Sensor ausgewählt wurde, müssen seine
            # Quell-Sensoren (ADC3, IMP2) nicht extra ausgewählt werden.
            if key in FLOW_RATE_SENSORS and flow_sensor_selected:
                _LOGGER.debug(
                    "Ignoriere Quell-Sensor %s, da der priorisierte Flow-Sensor aktiv ist.",
                    key,
                )
                continue

            _LOGGER.debug("Überspringe Sensor %s (nicht ausgewählt)", key)
            continue
        # ===============================================================

        # Sensor-Erstellung
        predefined_info = all_predefined_sensors.get(key)
        if predefined_info:
            name = predefined_info["name"]
            icon = predefined_info.get("icon")
        else:
            name = key.replace("_", " ").title()
            icon = None

        unit = UNIT_MAP.get(key) if key not in NO_UNIT_SENSORS else None
        if _is_boolean_value(raw_value):
            unit = None  # Booleans haben keine Einheit

        # ✅ FIX: Automatische Einheiten-Zuweisung für Temperatur-Sensoren und abhängige Werte
        if unit is None and key not in NO_UNIT_SENSORS and not _is_boolean_value(raw_value):
            # 1. Prüfe auf Suffixe und erbe Einheit vom Basis-Key
            for suffix in ["_min", "_max", "_setpoint", "_target", "_faultcount", "_freezecount"]:
                if key.endswith(suffix):
                    base_key = key[:-len(suffix)]
                    unit = UNIT_MAP.get(base_key)
                    if unit:
                        _LOGGER.debug("Unit %s for %s inherited from %s", unit, key, base_key)
                    break

            # 2. Wenn immer noch keine Unit, prüfe auf "temp" oder "onewire"
            if unit is None and ("temp" in key.lower() or "onewire" in key.lower()):
                 unit = "°C"
                 _LOGGER.debug("Auto-assigned °C unit to sensor: %s", key)

        description = SensorEntityDescription(
            key=key,
            name=name,
            icon=icon or get_icon(unit, key, raw_value),
            native_unit_of_measurement=unit,
            device_class=determine_device_class(key, unit, raw_value),
            state_class=determine_state_class(key, unit, raw_value),
            entity_category=EntityCategory.DIAGNOSTIC if key.startswith("SYSTEM_") else None,
        )

        # Verwende VioletStatusSensor für Status-Sensoren (aber nicht für Firmware)
        if key in STATUS_SENSORS and key not in ["fw", "FW"]:
             sensors.append(VioletStatusSensor(coordinator, config_entry, description))
        else:
             sensors.append(VioletSensor(coordinator, config_entry, description))

    if sensors:
        async_add_entities(sensors)
        _LOGGER.info("%d Sensoren für '%s' hinzugefügt.", len(sensors), config_entry.title)
    else:
        _LOGGER.warning(
            "Keine Sensoren für '%s' hinzugefügt. "
            "Überprüfe die Auswahl im Konfigurationsmenü.",
            config_entry.title
        )
