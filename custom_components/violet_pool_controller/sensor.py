"""Sensor Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Union

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_DEVICE_NAME,
    MANUFACTURER,
    INTEGRATION_VERSION,
    TEMP_SENSORS,
    WATER_CHEM_SENSORS,
    ANALOG_SENSORS,
)

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
}

# Sensortypen ohne Einheiten
NO_UNIT_SENSORS = {
    "SOLAR_LAST_OFF", "HEATER_LAST_ON", "HEATER_LAST_OFF",
    "BACKWASH_LAST_ON", "BACKWASH_LAST_OFF", "PUMP_LAST_ON", "PUMP_LAST_OFF"
}


class VioletSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Violet Pool Controller Sensor."""

    def __init__(
        self,
        coordinator,
        key: str,
        name: str,
        config_entry: ConfigEntry,
        device_class: Optional[str] = None,
        state_class: Optional[str] = None,
        unit: Optional[str] = None,
        icon: Optional[str] = None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._config_entry = config_entry
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self._attr_name = f"{device_name} {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{key.lower()}"
        
        if device_class:
            self._attr_device_class = device_class
            
        if state_class:
            self._attr_state_class = state_class
            
        if unit:
            self._attr_native_unit_of_measurement = unit
            
        if icon:
            self._attr_icon = icon
            
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": MANUFACTURER,
            "model": f"Violet Model X (v{INTEGRATION_VERSION})",
            "sw_version": coordinator.data.get("fw", INTEGRATION_VERSION),
            "configuration_url": f"http://{self.ip_address}",
        }
        
        self._has_logged_none_state = False  # Verhindert wiederholte Logs bei None-Zustand

    @property
    def native_value(self) -> Union[float, int, str, None]:
        """Return the current value of this sensor."""
        value = self.coordinator.data.get(self._key)
        if value is None:
            if not self._has_logged_none_state:
                _LOGGER.warning("Sensor '%s' returned None as its state.", self._key)
                self._has_logged_none_state = True
        return value

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


def guess_device_class(key: str) -> Optional[str]:
    """Bestimme die Device Class basierend auf dem Key."""
    klower = key.lower()
    
    if "temp" in klower or "therm" in klower or "onewire" in klower:
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
        return SensorStateClass.TIMESTAMP
        
    # Standard für Messwerte
    return SensorStateClass.MEASUREMENT


def guess_icon(key: str) -> str:
    """Bestimme ein Icon basierend auf dem Key."""
    klower = key.lower()

    # Temperatur-Icons
    if "temp" in klower or "therm" in klower:
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
    if "rpm" in klower:
        return "mdi:fan"
    if "version" in klower or "fw" in klower:
        return "mdi:update"
        
    # Zeit-Icons
    if "last_on" in klower:
        return "mdi:timer"
    if "last_off" in klower:
        return "mdi:timer-off"
        
    # Fallback
    return "mdi:information"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Violet Device sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Verfügbare Daten aus der API
    available_data_keys = set(coordinator.data.keys())
    
    # Liste für alle zu erstellenden Sensors
    sensors = []
    
    # 1. Temperatursensoren hinzufügen
    for key, sensor_info in TEMP_SENSORS.items():
        if key in available_data_keys:
            sensors.append(
                VioletSensor(
                    coordinator=coordinator,
                    key=key,
                    name=sensor_info["name"],
                    config_entry=config_entry,
                    device_class=SensorDeviceClass.TEMPERATURE,
                    state_class=SensorStateClass.MEASUREMENT,
                    unit="°C",
                    icon=sensor_info["icon"]
                )
            )
    
    # 2. Wasserchemie-Sensoren hinzufügen
    for key, sensor_info in WATER_CHEM_SENSORS.items():
        if key in available_data_keys:
            sensors.append(
                VioletSensor(
                    coordinator=coordinator,
                    key=key,
                    name=sensor_info["name"],
                    config_entry=config_entry,
                    device_class=guess_device_class(key),
                    state_class=SensorStateClass.MEASUREMENT,
                    unit=sensor_info["unit"],
                    icon=sensor_info["icon"]
                )
            )
    
    # 3. Analog-Sensoren hinzufügen
    for key, sensor_info in ANALOG_SENSORS.items():
        if key in available_data_keys:
            sensors.append(
                VioletSensor(
                    coordinator=coordinator,
                    key=key,
                    name=sensor_info["name"],
                    config_entry=config_entry,
                    device_class=guess_device_class(key),
                    state_class=SensorStateClass.MEASUREMENT,
                    unit=sensor_info["unit"],
                    icon=sensor_info["icon"]
                )
            )
    
    # 4. Alle anderen Sensoren hinzufügen (dynamisch)
    # Wir wollen mit einigen Keys vorsichtig sein, die keine echten Sensordaten enthalten
    excluded_keys = {
        "fw", "date", "time", "CURRENT_TIME_UNIX",  # Systeminformationen
        # Binäre Zustände, die bereits als binary_sensor erfasst werden
        "PUMP", "SOLAR", "HEATER", "LIGHT", "ECO", "BACKWASH", "BACKWASHRINSE",
        "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC",
        "REFILL", "PVSURPLUS"
    }
    
    for key in available_data_keys:
        # Überspringe bereits definierte Sensoren und ausgeschlossene Keys
        if (key in TEMP_SENSORS or key in WATER_CHEM_SENSORS or 
            key in ANALOG_SENSORS or key in excluded_keys):
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
        
        # Erstelle den Sensor
        sensors.append(
            VioletSensor(
                coordinator=coordinator,
                key=key,
                name=name,
                config_entry=config_entry,
                device_class=device_class,
                state_class=state_class,
                unit=unit,
                icon=icon
            )
        )
    
    # 5. Spezielle Dosierungs-Sensoren hinzufügen
    dosing_keys = {
        "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "Chlor Tagesdosierung",
        "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "pH- Tagesdosierung",
        "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "pH+ Tagesdosierung",
        "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "Flockmittel Tagesdosierung",
    }
    
    for key, name in dosing_keys.items():
        if key in available_data_keys:
            sensors.append(
                VioletSensor(
                    coordinator=coordinator,
                    key=key,
                    name=name,
                    config_entry=config_entry,
                    state_class=SensorStateClass.TOTAL,
                    unit="mL",
                    icon="mdi:water"
                )
            )
    
    # Entitäten hinzufügen
    if sensors:
        _LOGGER.info(f"{len(sensors)} Sensoren gefunden und hinzugefügt.")
        async_add_entities(sensors)
    else:
        _LOGGER.warning("Keine passenden Sensoren in den API-Daten gefunden.")
