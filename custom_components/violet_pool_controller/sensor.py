import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VioletDeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Violet Device Sensor."""

    def __init__(self, coordinator, key, icon, config_entry):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"
        self._config_entry = config_entry

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._key)

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

    @property
    def device_info(self):
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, "violet_pool_controller")},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get('fw', 'Unknown'),
            "configuration_url": f"http://{self._config_entry.data.get('host', 'Unknown IP')}",
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        units = {
            # Add the unit mappings for sensors as per your original code
        }
        return units.get(self._key, None)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        VioletDeviceSensor(coordinator, sensor["key"], sensor["icon"], config_entry)
        for sensor in SENSORS
    ]
    async_add_entities(sensors)

SENSORS = [
    {"name": "Messwasserüberwachung", "key": "IMP1_value", "icon": "mdi:flash"},
    {"name": "IMP2 Value", "key": "IMP2_value", "icon": "mdi:flash"},

    # Power and Temperature
    {"name": "Pump Power", "key": "pump_rs485_pwr", "icon": "mdi:power"},
    {"name": "System CPU Temperature", "key": "SYSTEM_cpu_temperature", "icon": "mdi:thermometer"},
    {"name": "Carrier CPU Temperature", "key": "SYSTEM_carrier_cpu_temperature", "icon": "mdi:thermometer"},
    {"name": "System Dosage Module CPU Temperature", "key": "SYSTEM_dosagemodule_cpu_temperature", "icon": "mdi:thermometer"},
    {"name": "System Memory Usage", "key": "SYSTEM_memoryusage", "icon": "mdi:memory"},
    {"name": "CPU Temperature", "key": "CPU_TEMP", "icon": "mdi:thermometer"},  # CPU temperature
    {"name": "CPU Temperature CARRIER", "key": "CPU_TEMP_CARRIER", "icon": "mdi:thermometer"},  # CPU temperature CARRIER
    {"name": "System Memory", "key": "SYSTEM_MEMORY", "icon": "mdi:memory"},  # System memory usage
    {"name": "Load Average", "key": "LOAD_AVG", "icon": "mdi:chart-line"},  # Load average percentage
    
    # Software Version
    {"name": "Software Violet Application", "key": "SW_VERSEION", "icon": "mdi:update"},  # Software-Version VIOLET application
    {"name": "Firmware Violet Carrier", "key": "SW_VERSION_CARRIER", "icon": "mdi:update"},  # Firmware-Version VIOLET carrier

    # OneWire Sensors (Temperature, Min/Max Values)
    {"name": "OneWire 1 Temperature", "key": "onewire1_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 1 Min Value", "key": "onewire1_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 1 Max Value", "key": "onewire1_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 2 Temperature", "key": "onewire2_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 2 Min Value", "key": "onewire2_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 2 Max Value", "key": "onewire2_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 3 Temperature", "key": "onewire3_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 3 Min Value", "key": "onewire3_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 3 Max Value", "key": "onewire3_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 4 Temperature", "key": "onewire4_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 4 Min Value", "key": "onewire4_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 4 Max Value", "key": "onewire4_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 5 Temperature", "key": "onewire5_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 5 Min Value", "key": "onewire5_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 5 Max Value", "key": "onewire5_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 6 Temperature", "key": "onewire6_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 6 Min Value", "key": "onewire6_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 6 Max Value", "key": "onewire6_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 7 Temperature", "key": "onewire7_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 7 Min Value", "key": "onewire7_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 7 Max Value", "key": "onewire7_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 8 Temperature", "key": "onewire8_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 8 Min Value", "key": "onewire8_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 8 Max Value", "key": "onewire8_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 9 Temperature", "key": "onewire9_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 9 Min Value", "key": "onewire9_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 9 Max Value", "key": "onewire9_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 10 Temperature", "key": "onewire10_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 10 Min Value", "key": "onewire10_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 10 Max Value", "key": "onewire10_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 11 Temperature", "key": "onewire11_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 11 Min Value", "key": "onewire11_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 11 Max Value", "key": "onewire11_value_max", "icon": "mdi:thermometer-plus"},

    {"name": "OneWire 12 Temperature", "key": "onewire12_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 12 Min Value", "key": "onewire12_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "OneWire 12 Max Value", "key": "onewire12_value_max", "icon": "mdi:thermometer-plus"},

    # Analog Sensors (ADC)
    {"name": "Filterdruck", "key": "ADC1_value", "icon": "mdi:waveform"},  # Pressure sensor
    {"name": "Schwallwasser", "key": "ADC2_value", "icon": "mdi:waveform"},  # Water level sensor
    {"name": "Durchfluss", "key": "ADC3_value", "icon": "mdi:waveform"},  # Flow sensor
    {"name": "ADC4", "key": "ADC4_value", "icon": "mdi:waveform"},  # Generic sensor
    {"name": "ADC5", "key": "ADC5_value", "icon": "mdi:waveform"},  # Generic sensor
    {"name": "ADC6", "key": "ADC6_value", "icon": "mdi:waveform"},  # Generic sensor

    # pH and ORP Sensors
    {"name": "pH Value", "key": "pH_value", "icon": "mdi:flask"},  # pH sensor
    {"name": "pH Min Value", "key": "pH_value_min", "icon": "mdi:water-minus"},  # Minimum pH value
    {"name": "pH Max Value", "key": "pH_value_max", "icon": "mdi:water-plus"},  # Maximum pH value

    {"name": "ORP Value", "key": "orp_value", "icon": "mdi:chemical-weapon"},  # ORP (Oxidation Reduction Potential) sensor
    {"name": "ORP Min Value", "key": "orp_value_min", "icon": "mdi:flash-minus"},  # Minimum ORP value
    {"name": "ORP Max Value", "key": "orp_value_max", "icon": "mdi:flash-plus"},  # Maximum ORP value

    {"name": "Potentiometer Value", "key": "pot_value", "icon": "mdi:gauge"},  # Potentiometer value
    {"name": "Potentiometer Min Value", "key": "pot_value_min", "icon": "mdi:gauge-minus"},  # Minimum potentiometer value
    {"name": "Potentiometer Max Value", "key": "pot_value_max", "icon": "mdi:gauge-plus"},  # Maximum potentiometer value

    # Dosing amounts (daily and total)
    {"name": "Chlorine Daily Dosing Amount", "key": "DOS_1_CL_DAILY_DOSING_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "Chlorine Total Can Amount", "key": "DOS_1_CL_TOTAL_CAN_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "ELO Daily Dosing Amount", "key": "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "ELO Total Can Amount", "key": "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "pH-minus Daily Dosing Amount", "key": "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "pH-minus Total Can Amount", "key": "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML", "icon": "mdi:flask"},

    # Pump RPM sensors
    {"name": "Pump RPM 0", "key": "PUMP_RPM_0", "icon": "mdi:fan"},  # Pump RPM sensor
    {"name": "Pump RPM 1", "key": "PUMP_RPM_1", "icon": "mdi:fan"},  # Pump RPM sensor
    {"name": "Pump RPM 2", "key": "PUMP_RPM_2", "icon": "mdi:fan"},  # Pump RPM sensor
    {"name": "Pump RPM 3", "key": "PUMP_RPM_3", "icon": "mdi:fan"},  # Pump RPM sensor

    # Runtime values (duration format hh:mm:ss)
    {"name": "Pump Runtime", "key": "PUMP_RUNTIME", "icon": "mdi:timer"},
    {"name": "Solar Runtime", "key": "SOLAR_RUNTIME", "icon": "mdi:timer"},
    {"name": "Heater Runtime", "key": "HEATER_RUNTIME", "icon": "mdi:timer"},
    {"name": "Backwash Runtime", "key": "BACKWASH_RUNTIME", "icon": "mdi:timer"},
    {"name": "Omni DC0 Runtime", "key": "OMNI_DC0_RUNTIME", "icon": "mdi:timer"},
    {"name": "Omni DC1 Runtime", "key": "OMNI_DC1_RUNTIME", "icon": "mdi:timer"},

    # System states and other
    {"name": "System Carrier Alive Count", "key": "SYSTEM_carrier_alive_count", "icon": "mdi:alert-circle"},  # System carrier alive count
    {"name": "System EXT1 Module Alive Count", "key": "SYSTEM_ext1module_alive_count", "icon": "mdi:alert-circle"},  # External module count
    {"name": "System Dosage Module Alive Count", "key": "SYSTEM_dosagemodule_alive_count", "icon": "mdi:alert-circle"},  # Dosage module alive count

    # Solar and heater timers
    {"name": "Solar Last On", "key": "SOLAR_LAST_ON", "icon": "mdi:timer"},  # Solar system last on time
    {"name": "Solar Last Off", "key": "SOLAR_LAST_OFF", "icon": "mdi:timer-off"},  # Solar system last off time
    {"name": "Heater Last On", "key": "HEATER_LAST_ON", "icon": "mdi:timer"},  # Heater last on time
    {"name": "Heater Last Off", "key": "HEATER_LAST_OFF", "icon": "mdi:timer-off"},  # Heater last off time
    {"name": "Backwash Last On", "key": "BACKWASH_LAST_ON", "icon": "mdi:timer"},  # Backwash last on time
    {"name": "Backwash Last Off", "key": "BACKWASH_LAST_OFF", "icon": "mdi:timer-off"},  # Backwash last off time
]
