"""Sensor Integration für den Violet Pool Controller."""
import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity, SensorDeviceClass, SensorStateClass, SensorEntityDescription
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN, TEMP_SENSORS, WATER_CHEM_SENSORS, ANALOG_SENSORS,
    CONF_ACTIVE_FEATURES, CONF_SELECTED_SENSORS, # Neuer Import
    UNIT_MAP, NO_UNIT_SENSORS, SENSOR_FEATURE_MAP
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# --- Definitionen für Sensor-Typen (gekürzt, da unverändert) ---
_TIMESTAMP_SUFFIXES = ("_LAST_ON", "_LAST_OFF", "_TIMESTAMP")
_TIMESTAMP_KEYS = {"CURRENT_TIME_UNIX"} | {k for k in UNIT_MAP if any(k.upper().endswith(s) for s in _TIMESTAMP_SUFFIXES)}
TEXT_VALUE_SENSORS = {"DOS_1_CL_STATE", "HEATERSTATE", "PUMPSTATE", "VERSION"} # Stark gekürzt
RUNTIME_SENSORS = {"ECO_RUNTIME", "PUMP_RUNTIME"} # Stark gekürzt
BOOLEAN_VALUE_SENSORS = {"OVERFLOW_REFILL_STATE"} # Stark gekürzt
TEXT_VALUE_SENSORS.update(RUNTIME_SENSORS)
TEXT_VALUE_SENSORS.update(BOOLEAN_VALUE_SENSORS)
TIME_FORMAT_SENSORS = {"CPU_UPTIME"} # Stark gekürzt
FLOW_RATE_SENSORS = {"ADC3_value", "IMP2_value"}


def _is_boolean_value(value: Any) -> bool:
    if not isinstance(value, (str, bool)): return False
    return str(value).lower().strip() in ('true', 'false', '1', '0', 'on', 'off')

# --- Klassen VioletSensor und VioletFlowRateSensor (unverändert) ---
class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Repräsentation eines Sensors."""
    entity_description: SensorEntityDescription

    def __init__(self, coordinator, config_entry, description):
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self):
        key = self.entity_description.key
        raw_value = self.coordinator.data.get(key)
        if raw_value is None: return None
        
        if key in _TIMESTAMP_KEYS and key not in TIME_FORMAT_SENSORS:
            try: return datetime.fromtimestamp(float(raw_value), tz=timezone.utc)
            except (ValueError, TypeError): return None
        
        if key in TEXT_VALUE_SENSORS or key in TIME_FORMAT_SENSORS:
            return str(raw_value)
            
        try:
            f = float(raw_value)
            return int(f) if f.is_integer() else round(f, 2)
        except (ValueError, TypeError):
            return str(raw_value)


class VioletFlowRateSensor(VioletPoolControllerEntity, SensorEntity):
    """Spezieller Förderleistungs-Sensor."""
    def __init__(self, coordinator, config_entry):
        description = SensorEntityDescription(
            key="flow_rate_adc3_priority", name="Förderleistung", icon="mdi:pump",
            native_unit_of_measurement="m³/h", device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
            state_class=SensorStateClass.MEASUREMENT,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        adc3 = self.coordinator.data.get("ADC3_value")
        if adc3 is not None:
            try: return round(float(adc3), 2)
            except (ValueError, TypeError): pass
        
        imp2 = self.coordinator.data.get("IMP2_value")
        if imp2 is not None:
            try: return round(float(imp2), 2)
            except (ValueError, TypeError): pass
        return None

    @property
    def available(self) -> bool:
        return super().available and (
            self.coordinator.data.get("ADC3_value") is not None or 
            self.coordinator.data.get("IMP2_value") is not None
        )

# --- Helper-Funktionen (determine_device_class, etc. - unverändert) ---
def determine_device_class(key, unit, raw_value=None): return None # Gekürzt
def determine_state_class(key, unit, raw_value=None): return None # Gekürzt
def get_icon(unit, key, raw_value=None): return "mdi:information" # Gekürzt
def should_skip_sensor(key: str, raw_value) -> bool:
    if raw_value is None: return True
    raw_str = str(raw_value).strip()
    return raw_str in ("[]", "{}", "") or key.startswith("_")


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Richtet Sensoren basierend auf der Konfiguration ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Hole Konfiguration aus Options (primär) oder Data (Fallback)
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    selected_sensors = config_entry.options.get(CONF_SELECTED_SENSORS, config_entry.data.get(CONF_SELECTED_SENSORS))

    # WICHTIG: Wenn selected_sensors None ist (alte Konfig), erstellen wir alle Sensoren
    # Ein leeres Array [] bedeutet, der User hat explizit keine Sensoren ausgewählt.
    create_all_sensors = selected_sensors is None
    
    if create_all_sensors:
        _LOGGER.warning("Keine Sensor-Auswahl gefunden. Erstelle ALLE verfügbaren Sensoren (Abwärtskompatibilität).")
    else:
        _LOGGER.info("Erstelle %d ausgewählte Sensoren.", len(selected_sensors))

    sensors = []
    data_keys = set(coordinator.data.keys())
    all_predefined_sensors = {**TEMP_SENSORS, **WATER_CHEM_SENSORS, **ANALOG_SENSORS}
    
    # Erstelle nur den speziellen Flow-Sensor, wenn er ausgewählt wurde (oder alle erstellt werden)
    if (create_all_sensors or "flow_rate_adc3_priority" in selected_sensors) and any(k in data_keys for k in FLOW_RATE_SENSORS):
        sensors.append(VioletFlowRateSensor(coordinator, config_entry))

    # Dynamische und vordefinierte Sensoren durchlaufen
    for key in data_keys:
        raw_value = coordinator.data.get(key)
        
        # Logik zum Überspringen von Sensoren
        if should_skip_sensor(key, raw_value): continue
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if feature_id and feature_id not in active_features: continue
        
        # ===============================================================
        # NEUE LOGIK: Prüfe, ob der Sensor ausgewählt wurde
        # ===============================================================
        if not create_all_sensors and key not in selected_sensors:
            _LOGGER.debug("Überspringe Sensor %s (nicht ausgewählt)", key)
            continue
        # ===============================================================

        # Sensor-Erstellung (wie bisher, aber jetzt gefiltert)
        predefined_info = all_predefined_sensors.get(key)
        if predefined_info:
            name = predefined_info["name"]
            icon = predefined_info.get("icon")
        else:
            name = key.replace("_", " ").title()
            icon = None
            
        unit = UNIT_MAP.get(key) if key not in NO_UNIT_SENSORS else None
        if _is_boolean_value(raw_value): unit = None # Booleans haben keine Einheit
        
        description = SensorEntityDescription(
            key=key,
            name=name,
            icon=icon or get_icon(unit, key, raw_value),
            native_unit_of_measurement=unit,
            device_class=determine_device_class(key, unit, raw_value),
            state_class=determine_state_class(key, unit, raw_value),
            entity_category=EntityCategory.DIAGNOSTIC if key.startswith("SYSTEM_") else None,
        )
        sensors.append(VioletSensor(coordinator, config_entry, description))

    if sensors:
        async_add_entities(sensors)
        _LOGGER.info("%d Sensoren für '%s' hinzugefügt.", len(sensors), config_entry.title)
    else:
        _LOGGER.warning("Keine Sensoren für '%s' hinzugefügt.", config_entry.title)
