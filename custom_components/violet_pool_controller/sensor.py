"""Sensor Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Union, List, cast
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

# Einheiten für verschiedene Sensortypen (nicht in const.py, da spezifisch für sensor.py)
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
    "CPU_UPTIME": "d",
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
    "BACKWASH_LAST_ON", "BACKWASH_LAST_OFF", "PUMP_LAST_ON", "PUMP_LAST_OFF"
}

# Mapping von Sensor-Keys zu Feature-IDs
SENSOR_FEATURE_MAP = {
    # Temperatur-Sensoren
    "onewire1_value": "heating",
    "onewire2_value": "heating",
    "onewire3_value": "solar",
    "onewire4_value": "heating",
    "onewire5_value": "heating",
    
    # Wasserchemie-Sensoren
    "pH_value": "ph_control",
    "orp_value": "chlorine_control",
    "pot_value": "chlorine_control",
    
    # Dosierung
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "chlorine_control",
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "chlorine_control",
    
    # Wasserstand
    "ADC2_value": "water_level",
    
    # Filter/Pumpe
    "FILTER_PRESSURE": "filter_control",
    "PUMP_RPM_0": "filter_control",
    "PUMP_RPM_1": "filter_control",
    "PUMP_RPM_2": "filter_control",
    "PUMP_RPM_3": "filter_control",
    
    # Heizung
    "HEATER_TEMPERATURE": "heating",
    
    # Abdeckung
    "COVER_POSITION": "cover_control",
}


@dataclass
class VioletSensorEntityDescription(SensorEntityDescription):
    """Class describing Violet Pool sensor entities."""

    feature_id: Optional[str] = None


class VioletSensor(VioletPoolControllerEntity, SensorEntity):
    """Representation of a Violet Pool Controller Sensor."""

    entity_description: VioletSensorEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: VioletSensorEntityDescription,
    ):
        """Initialize the sensor.
        
        Args:
            coordinator: Der Daten-Koordinator
            config_entry: Die Config Entry des Geräts
            description: Die Beschreibung der Entität
        """
        # Initialisiere die Basisklasse
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_description=description,
        )
        
        # Tracking für Logging
        self._has_logged_none_state = False
        
    @property
    def native_value(self) -> Union[float, int, str, None]:
        """Return the current value of this sensor."""
        key = self.entity_description.key
        
        # Prüfe auf Zeitstempel-Sensoren anhand des Namens statt der nicht mehr vorhandenen Klasse
        if key.lower().endswith("_last_on") or key.lower().endswith("_last_off"):
            return self.get_str_value(key)
            
        # Sensorwerte basierend auf Typ und DeviceClass abrufen
        if self.entity_description.device_class == SensorDeviceClass.TEMPERATURE:
            return self.get_float_value(key)
                
        if self.entity_description.device_class == SensorDeviceClass.PRESSURE:
            return self.get_float_value(key)
                
        if self.entity_description.device_class == SensorDeviceClass.PH:
            return self.get_float_value(key)
                
        if self.entity_description.device_class == SensorDeviceClass.POWER:
            return self.get_float_value(key)
                
        if self.entity_description.device_class == SensorDeviceClass.VOLTAGE:
            return self.get_float_value(key)
        
        # Standardverhalten: Versuche, den Wert als Float zu interpretieren, mit Fallback auf String
        try:
            value = self.coordinator.data.get(key)
            if value is None:
                if not self._has_logged_none_state:
                    self._logger.warning("Sensor '%s' returned None as its state.", key)
                    self._has_logged_none_state = True
                return None
                
            # Versuche Konvertierung zu Float, falls möglich
            if isinstance(value, (int, float)):
                return value
            elif isinstance(value, str) and value.replace(".", "", 1).isdigit():
                return float(value)
            return value
        except Exception as err:
            self._logger.error(f"Error retrieving value for {key}: {err}")
            return None

    def _update_from_coordinator(self) -> None:
        """Aktualisiert den Zustand des Sensors anhand der Coordinator-Daten."""
        # Die native_value-Property wird aufgerufen, wenn Home Assistant
        # den Zustand des Sensors abfragt, daher brauchen wir hier nichts
        # Besonderes zu tun. Wir überschreiben diese Methode nur, um die
        # Basisimplementierung zu überschreiben.
        pass


def guess_device_class(key: str) -> Optional[str]:
    """Bestimme die Device Class basierend auf dem Key."""
    klower = key.lower()
    
    if "temp" in klower or "therm" in klower or "onewire" in klower or "cpu_temp" in klower:
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
        
    # Weitere Device Classes können nach Bedarf hinzugefügt werden
    
    return None


def guess_state_class(key: str) -> Optional[str]:
    """Bestimme die State Class basierend auf dem Key."""
    klower = key.lower()
    
    if "daily" in klower or "_daily_" in klower:
        return SensorStateClass.TOTAL
        
    if "last_on" in klower or "last_off" in klower:
        # SensorStateClass.TIMESTAMP existiert nicht mehr in HA
        return None
        
    # Standard für Messwerte
    return SensorStateClass.MEASUREMENT


def guess_icon(key: str) -> str:
    """Bestimme ein Icon basierend auf dem Key."""
    klower = key.lower()

    # Temperatur-Icons
    if "temp" in klower or "therm" in klower or "cpu_temp" in klower:
        return "mdi:thermometer"
        
    # Pump-Icons
    if "pump" in klower:
        return "mdi:water-pump"
        
    # Chemie-Icons
    if "orp" in klower:
        return "mdi:flash"
    if "ph" in klower:
        return "mdi:flask"
        
    # Druck-Icons
    if "pressure" in klower or "adc" in klower:
        return "mdi:gauge"
        
    # System-Icons
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
        
    # Zeit-Icons
    if "last_on" in klower:
        return "mdi:timer"
    if "last_off" in klower:
        return "mdi:timer-off"
        
    # Fallback
    return "mdi:information"


def guess_entity_category(key: str) -> Optional[str]:
    """Bestimmt die EntityCategory basierend auf dem Key."""
    klower = key.lower()
    
    # Diagnostische Sensoren
    if (
        "system" in klower or 
        "cpu" in klower or 
        "memory" in klower or 
        "fw" in klower or 
        "version" in klower or
        "load" in klower or 
        "uptime" in klower or
        "serial" in klower
    ):
        return EntityCategory.DIAGNOSTIC
        
    # Konfigurationssensoren
    if "setpoint" in klower or "target" in klower:
        return EntityCategory.CONFIG
        
    # Standardmäßig keine Kategorie
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Violet Device sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Hole aktive Features
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, 
        config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    
    # Verfügbare Daten aus der API
    available_data_keys = set(coordinator.data.keys())
    
    # Liste für alle zu erstellenden Sensors
    sensors: List[VioletSensor] = []
    
    # 1. Temperatursensoren hinzufügen
    for key, sensor_info in TEMP_SENSORS.items():
        # Überprüfe, ob der Sensor verfügbar ist und das zugehörige Feature aktiv ist
        if key not in available_data_keys:
            continue
            
        # Prüfe, ob das Feature aktiv ist - DEAKTIVIERT um mehr Sensoren anzuzeigen
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if False and feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Sensor %s wird übersprungen, da Feature %s nicht aktiv ist",
                key,
                feature_id
            )
            continue
            
        # Erstelle EntityDescription
        description = VioletSensorEntityDescription(
            key=key,
            name=sensor_info["name"],
            icon=sensor_info["icon"],
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement="°C",
            feature_id=feature_id,
        )
            
        # Sensor erstellen
        sensors.append(
            VioletSensor(
                coordinator=coordinator,
                config_entry=config_entry,
                description=description,
            )
        )
    
    # 2. Wasserchemie-Sensoren hinzufügen
    for key, sensor_info in WATER_CHEM_SENSORS.items():
        if key not in available_data_keys:
            continue
            
        # Prüfe, ob das Feature aktiv ist - DEAKTIVIERT um mehr Sensoren anzuzeigen
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if False and feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Sensor %s wird übersprungen, da Feature %s nicht aktiv ist",
                key,
                feature_id
            )
            continue
            
        # Device Class bestimmen
        device_class = guess_device_class(key)
        
        # Einheit anpassen - für pH keine Einheit verwenden
        unit = None if device_class == SensorDeviceClass.PH else sensor_info["unit"]
        
        # Erstelle EntityDescription
        description = VioletSensorEntityDescription(
            key=key,
            name=sensor_info["name"],
            icon=sensor_info["icon"],
            device_class=device_class,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=unit,
            feature_id=feature_id,
        )
            
        # Sensor erstellen
        sensors.append(
            VioletSensor(
                coordinator=coordinator,
                config_entry=config_entry,
                description=description,
            )
        )
    
    # 3. Analog-Sensoren hinzufügen
    for key, sensor_info in ANALOG_SENSORS.items():
        if key not in available_data_keys:
            continue
            
        # Prüfe, ob das Feature aktiv ist - DEAKTIVIERT um mehr Sensoren anzuzeigen
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if False and feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Sensor %s wird übersprungen, da Feature %s nicht aktiv ist",
                key,
                feature_id
            )
            continue
            
        # Erstelle EntityDescription
        description = VioletSensorEntityDescription(
            key=key,
            name=sensor_info["name"],
            icon=sensor_info["icon"],
            device_class=guess_device_class(key),
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=sensor_info["unit"],
            feature_id=feature_id,
        )
            
        # Sensor erstellen
        sensors.append(
            VioletSensor(
                coordinator=coordinator,
                config_entry=config_entry,
                description=description,
            )
        )
    
    # 4. Alle anderen Sensoren hinzufügen (dynamisch)
    # Wir wollen mit einigen Keys vorsichtig sein, die keine echten Sensordaten enthalten
    excluded_keys = {
        # Nur absolut notwendige Ausschlüsse
        "date", "time", "CURRENT_TIME_UNIX",  # Systeminformationen
        
        # Diese auskommentiert, um mehr Sensoren anzuzeigen
        # "fw",
        # "PUMP", "SOLAR", "HEATER", "LIGHT", "ECO", "BACKWASH", "BACKWASHRINSE",
        # "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC",
        # "REFILL", "PVSURPLUS"
    }
    
    for key in available_data_keys:
        # Überspringe bereits definierte Sensoren und ausgeschlossene Keys
        if (key in TEMP_SENSORS or key in WATER_CHEM_SENSORS or 
            key in ANALOG_SENSORS or key in excluded_keys):
            continue
            
        # Prüfe, ob das Feature aktiv ist - DEAKTIVIERT um mehr Sensoren anzuzeigen
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if False and feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Sensor %s wird übersprungen, da Feature %s nicht aktiv ist",
                key,
                feature_id
            )
            continue
            
        # Bestimme Name, Einheit, Device Class usw. für diesen Sensor
        name = key.replace('_', ' ').title()
        unit = UNIT_MAP.get(key)
        
        # Überspringe Keys, die keinen Wert haben sollten
        if key in NO_UNIT_SENSORS:
            unit = None
            
        device_class = guess_device_class(key)
        state_class = guess_state_class(key)
        icon = guess_icon(key)
        entity_category = guess_entity_category(key)
        
        # Erstelle EntityDescription
        description = VioletSensorEntityDescription(
            key=key,
            name=name,
            icon=icon,
            device_class=device_class,
            state_class=state_class,
            native_unit_of_measurement=unit,
            entity_category=EntityCategory(entity_category) if entity_category else None,
            feature_id=feature_id,
        )
        
        # Sensor erstellen
        sensors.append(
            VioletSensor(
                coordinator=coordinator,
                config_entry=config_entry,
                description=description,
            )
        )
    
    # 5. Spezielle Dosierungs-Sensoren hinzufügen
    dosing_keys = {
        "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "Chlor Tagesdosierung",
        "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "pH- Tagesdosierung",
        "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "pH+ Tagesdosierung",
        "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "Flockmittel Tagesdosierung",
    }
    
    # Erstelle ein Set, um bereits erstellte Sensor-Keys zu verfolgen
    created_sensor_keys = {sensor.entity_description.key for sensor in sensors}
    
    for key, name in dosing_keys.items():
        # Überspringe, wenn der Sensor bereits existiert
        if key in created_sensor_keys:
            _LOGGER.debug(
                "Überspringe doppelten Dosierungs-Sensor %s, da er bereits hinzugefügt wurde",
                key
            )
            continue
            
        if key not in available_data_keys:
            continue
            
        # Prüfe, ob das Feature aktiv ist - DEAKTIVIERT um mehr Sensoren anzuzeigen
        feature_id = SENSOR_FEATURE_MAP.get(key)
        if False and feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Sensor %s wird übersprungen, da Feature %s nicht aktiv ist",
                key,
                feature_id
            )
            continue
            
        # Erstelle EntityDescription
        description = VioletSensorEntityDescription(
            key=key,
            name=name,
            icon="mdi:water",
            state_class=SensorStateClass.TOTAL,
            native_unit_of_measurement="mL",
            feature_id=feature_id,
        )
            
        # Sensor erstellen
        sensors.append(
            VioletSensor(
                coordinator=coordinator,
                config_entry=config_entry,
                description=description,
            )
        )
    
    # 6. Spezielle CPU/System-Sensoren explizit hinzufügen
    system_sensors = {
        "CPU_TEMP": {"name": "CPU Temperatur", "icon": "mdi:cpu-64-bit", "device_class": SensorDeviceClass.TEMPERATURE, "unit": "°C"},
        "CPU_TEMP_CARRIER": {"name": "Carrier CPU Temperatur", "icon": "mdi:cpu-64-bit", "device_class": SensorDeviceClass.TEMPERATURE, "unit": "°C"},
        "LOAD_AVG": {"name": "System Auslastung", "icon": "mdi:chart-line", "unit": ""},
        "CPU_UPTIME": {"name": "System Laufzeit", "icon": "mdi:clock-outline", "unit": ""},
        "MEMORY_USED": {"name": "Speichernutzung", "icon": "mdi:memory", "unit": "%"},
        "SW_VERSION": {"name": "Software Version", "icon": "mdi:update", "unit": ""},
    }
    
    for key, info in system_sensors.items():
        if key not in available_data_keys or key in created_sensor_keys:
            continue
            
        # Erstelle EntityDescription
        description = VioletSensorEntityDescription(
            key=key,
            name=info["name"],
            icon=info["icon"],
            device_class=info.get("device_class"),
            state_class=SensorStateClass.MEASUREMENT if key not in ["SW_VERSION", "CPU_UPTIME"] else None,
            native_unit_of_measurement=info["unit"],
            entity_category=EntityCategory.DIAGNOSTIC,
        )
            
        # Sensor erstellen
        sensors.append(
            VioletSensor(
                coordinator=coordinator,
                config_entry=config_entry,
                description=description,
            )
        )
    
    # Entitäten hinzufügen
    if sensors:
        _LOGGER.info(f"{len(sensors)} Sensoren gefunden und hinzugefügt.")
        async_add_entities(sensors)
    else:
        _LOGGER.warning("Keine passenden Sensoren in den API-Daten gefunden.")