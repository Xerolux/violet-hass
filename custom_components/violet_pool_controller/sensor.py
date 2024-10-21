import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# List of sensors that should not have a unit of measurement
NO_UNIT_SENSORS = [
    "SOLAR_LAST_OFF",
    "HEATER_LAST_ON",
    "HEATER_LAST_OFF",
    "BACKWASH_LAST_ON",
    "BACKWASH_LAST_OFF",
    "PUMP_LAST_ON",
    "PUMP_LAST_OFF",
]

class VioletDeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Violet Device Sensor."""

    def __init__(self, coordinator, key, icon, config_entry):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"
        self._state = None  # Cache the sensor state
        self._has_logged_none_state = False  # Avoid logging multiple warnings for None states

    @property
    def state(self):
        """Return the state of the sensor."""
        self._state = self._get_sensor_state()
        if self._state is None and not self._has_logged_none_state:
            _LOGGER.warning(f"Sensor {self._key} returned None as its state.")
            self._has_logged_none_state = True
        return self._state

    @property
    def icon(self):
        """Return the dynamic icon depending on the sensor state, if applicable."""
        if self._key == "pump_rs485_pwr":
            return "mdi:power" if self.state else "mdi:power-off"
        if self._key.startswith("onewire"):
            return "mdi:thermometer" if self.state else "mdi:thermometer-off"
        return self._icon  # Default icon if no special handling is needed

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, "violet_pool_controller")},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get('fw') or self.coordinator.data.get('SW_VERSION', 'Unknown'),
            "configuration_url": f"http://{self._config_entry.data.get('host', 'Unknown IP')}/getReadings?ALL",
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._key in NO_UNIT_SENSORS:
            return None  # These sensors should not have a unit of measurement
        return self._get_unit_for_key(self._key)

    def _get_sensor_state(self):
        """Helper method to retrieve the current sensor state from the coordinator."""
        return self.coordinator.data.get(self._key)

    def _get_unit_for_key(self, key):
        """Helper method to retrieve the unit of measurement based on the sensor key."""
        units = {
            "IMP1_value": "cm/s",
            "IMP2_value": "cm/s",
            "pump_rs485_pwr": "W",
            "SYSTEM_cpu_temperature": "°C",
            "SYSTEM_carrier_cpu_temperature": "°C",
            "SYSTEM_dosagemodule_cpu_temperature": "°C",
            "SYSTEM_memoryusage": "MB",
            "onewire1_value": "°C",
            "onewire2_value": "°C",
            "onewire3_value": "°C",
            "onewire4_value": "°C",
            "onewire5_value": "°C",
            "onewire6_value": "°C",
            "onewire7_value": "°C",
            "onewire8_value": "°C",
            "onewire9_value": "°C",
            "onewire10_value": "°C",
            "onewire11_value": "°C",
            "onewire12_value": "°C",
            "ADC1_value": "bar",
            "ADC2_value": "cm",
            "ADC3_value": "m³",
            "ADC4_value": "V",
            "ADC5_value": "V",
            "ADC6_value": "V",
            "pH_value": "pH",
            "orp_value": "mV",
            "pot_value": "mg/l",
            "PUMP_RPM_0": "RPM",
            "PUMP_RPM_1": "RPM",
            "PUMP_RPM_2": "RPM",
            "PUMP_RPM_3": "RPM",
            "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "mL",
            "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": "mL",
            "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": "mL",
            "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": "mL",
            "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "mL",
            "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": "mL",
            "CPU_TEMP": "°C",
            "SYSTEM_MEMORY": "MB",
            "LOAD_AVG": "%",
            "WATER_TEMPERATURE": "°C",
            "AIR_TEMPERATURE": "°C",
            "HUMIDITY": "%",
            "SOLAR_PANEL_TEMPERATURE": "°C",
            "FILTER_PRESSURE": "bar",
            "HEATER_TEMPERATURE": "°C",
            "COVER_POSITION": "%",
            "UV_INTENSITY": "W/m²",
            "TDS": "ppm",
            "CALCIUM_HARDNESS": "ppm",
            "ALKALINITY": "ppm",
            "SALINITY": "ppm",
            "TURBIDITY": "NTU",
            "CHLORINE_LEVEL": "ppm",
            "BROMINE_LEVEL": "ppm",
        }
        return units.get(key, None)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device sensors from a config entry."""
    try:
        coordinator = hass.data[DOMAIN][config_entry.entry_id]
    except KeyError:
        _LOGGER.error("Unable to retrieve coordinator for Violet Pool Controller.")
        return

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
    {"name": "CPU Temperature", "key": "CPU_TEMP", "icon": "mdi:thermometer"},
    {"name": "CPU Temperature CARRIER", "key": "CPU_TEMP_CARRIER", "icon": "mdi:thermometer"},
    {"name": "System Memory", "key": "SYSTEM_MEMORY", "icon": "mdi:memory"},
    {"name": "Load Average", "key": "LOAD_AVG", "icon": "mdi:chart-line"},
    
    # Software Version
    {"name": "Software Violet Application", "key": "SW_VERSION", "icon": "mdi:update"},
    {"name": "Firmware Violet Carrier", "key": "SW_VERSION_CARRIER", "icon": "mdi:update"},

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
    {"name": "Filterdruck", "key": "ADC1_value", "icon": "mdi:waveform"},
    {"name": "Schwallwasser", "key": "ADC2_value", "icon": "mdi:waveform"},
    {"name": "Durchfluss", "key": "ADC3_value", "icon": "mdi:waveform"},
    {"name": "ADC4", "key": "ADC4_value", "icon": "mdi:waveform"},
    {"name": "ADC5", "key": "ADC5_value", "icon": "mdi:waveform"},
    {"name": "ADC6", "key": "ADC6_value", "icon": "mdi:waveform"},

    # pH and ORP Sensors
    {"name": "pH Value", "key": "pH_value", "icon": "mdi:flask"},
    {"name": "pH Min Value", "key": "pH_value_min", "icon": "mdi:water-minus"},
    {"name": "pH Max Value", "key": "pH_value_max", "icon": "mdi:water-plus"},

    {"name": "ORP Value", "key": "orp_value", "icon": "mdi:chemical-weapon"},
    {"name": "ORP Min Value", "key": "orp_value_min", "icon": "mdi:flash-minus"},
    {"name": "ORP Max Value", "key": "orp_value_max", "icon": "mdi:flash-plus"},

    {"name": "Potentiometer Value", "key": "pot_value", "icon": "mdi:gauge"},
    {"name": "Potentiometer Min Value", "key": "pot_value_min", "icon": "mdi:gauge-minus"},
    {"name": "Potentiometer Max Value", "key": "pot_value_max", "icon": "mdi:gauge-plus"},

    # Dosing amounts (daily and total)
    {"name": "Chlorine Daily Dosing Amount", "key": "DOS_1_CL_DAILY_DOSING_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "Chlorine Total Can Amount", "key": "DOS_1_CL_TOTAL_CAN_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "ELO Daily Dosing Amount", "key": "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "ELO Total Can Amount", "key": "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "pH-minus Daily Dosing Amount", "key": "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "pH-minus Total Can Amount", "key": "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML", "icon": "mdi:flask"},

    # Pump RPM sensors
    {"name": "Pump RPM 0", "key": "PUMP_RPM_0", "icon": "mdi:fan"},
    {"name": "Pump RPM 1", "key": "PUMP_RPM_1", "icon": "mdi:fan"},
    {"name": "Pump RPM 2", "key": "PUMP_RPM_2", "icon": "mdi:fan"},
    {"name": "Pump RPM 3", "key": "PUMP_RPM_3", "icon": "mdi:fan"},

    # Runtime values (duration format hh:mm:ss)
    {"name": "Pump Runtime", "key": "PUMP_RUNTIME", "icon": "mdi:timer"},
    {"name": "Solar Runtime", "key": "SOLAR_RUNTIME", "icon": "mdi:timer"},
    {"name": "Heater Runtime", "key": "HEATER_RUNTIME", "icon": "mdi:timer"},
    {"name": "Backwash Runtime", "key": "BACKWASH_RUNTIME", "icon": "mdi:timer"},
    {"name": "Omni DC0 Runtime", "key": "OMNI_DC0_RUNTIME", "icon": "mdi:timer"},
    {"name": "Omni DC1 Runtime", "key": "OMNI_DC1_RUNTIME", "icon": "mdi:timer"},

    # System states and other
    {"name": "System Carrier Alive Count", "key": "SYSTEM_carrier_alive_count", "icon": "mdi:alert-circle"},
    {"name": "System EXT1 Module Alive Count", "key": "SYSTEM_ext1module_alive_count", "icon": "mdi:alert-circle"},
    {"name": "System Dosage Module Alive Count", "key": "SYSTEM_dosagemodule_alive_count", "icon": "mdi:alert-circle"},

    # Solar and heater timers
    {"name": "Solar Last On", "key": "SOLAR_LAST_ON", "icon": "mdi:timer"},
    {"name": "Solar Last Off", "key": "SOLAR_LAST_OFF", "icon": "mdi:timer-off"},
    {"name": "Heater Last On", "key": "HEATER_LAST_ON", "icon": "mdi:timer"},
    {"name": "Heater Last Off", "key": "HEATER_LAST_OFF", "icon": "mdi:timer-off"},
    {"name": "Backwash Last On", "key": "BACKWASH_LAST_ON", "icon": "mdi:timer"},
    {"name": "Backwash Last Off", "key": "BACKWASH_LAST_OFF", "icon": "mdi:timer-off"},
]