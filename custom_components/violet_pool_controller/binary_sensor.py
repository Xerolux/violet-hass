import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VioletBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    def __init__(self, coordinator, key, icon, config_entry):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon  # Default icon
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"
        self._config_entry = config_entry

    def _get_sensor_state(self):
        """Helper method to retrieve the current sensor state from the coordinator."""
        return self.coordinator.data.get(self._key)

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._get_sensor_state() == 1

    @property
    def icon(self):
        """Return the dynamic icon depending on the sensor state."""
        if self._key == "PUMP_STATE":
            return "mdi:water-pump" if self.is_on else "mdi:water-pump-off"
        elif self._key == "SOLARSTATE":
            return "mdi:solar-power" if self.is_on else "mdi:solar-power-off"
        elif self._key == "HEATERSTATE":
            return "mdi:radiator" if self.is_on else "mdi:radiator-off"
        elif self._key == "COVER_STATE":
            return "mdi:garage-open" if self.is_on else "mdi:garage"
        elif self._key == "LIGHT_STATE":
            return "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb"
        return self._icon  # Default icon if no specific dynamic icon is set

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
        return self._get_unit_for_key(self._key)

    def _get_unit_for_key(self, key):
        """Helper method to retrieve the unit of measurement based on the sensor key."""
        units = {
            "IMP1_value": "cm/s",                      # Flow sensor 1
            "IMP2_value": "cm/s",                      # Flow sensor 2
            "pump_rs485_pwr": "W",                     # Pump power consumption
            "SYSTEM_cpu_temperature": "°C",            # System CPU temperature
            "SYSTEM_carrier_cpu_temperature": "°C",    # Carrier CPU temperature
            "SYSTEM_dosagemodule_cpu_temperature": "°C",  # Dosage module CPU temperature
            "SYSTEM_memoryusage": "MB",                # System memory usage
            "onewire1_value": "°C",                    # 1-Wire sensor 1 temperature
            "onewire2_value": "°C",                    # 1-Wire sensor 2 temperature
            "onewire3_value": "°C",                    # 1-Wire sensor 3 temperature
            "onewire4_value": "°C",                    # 1-Wire sensor 4 temperature
            "onewire5_value": "°C",                    # 1-Wire sensor 5 temperature
            "onewire6_value": "°C",                    # 1-Wire sensor 6 temperature
            "onewire7_value": "°C",                    # 1-Wire sensor 7 temperature
            "onewire8_value": "°C",                    # 1-Wire sensor 8 temperature
            "onewire9_value": "°C",                    # 1-Wire sensor 9 temperature
            "onewire10_value": "°C",                   # 1-Wire sensor 10 temperature
            "onewire11_value": "°C",                   # 1-Wire sensor 11 temperature
            "onewire12_value": "°C",                   # 1-Wire sensor 12 temperature
            "ADC1_value": "bar",                       # Analog sensor 1 (e.g., pressure)
            "ADC2_value": "cm",                        # Analog sensor 2 (e.g., water level)
            "ADC3_value": "m³",                        # Analog sensor 3 (e.g., volume flow)
            "ADC4_value": "V",                         # Analog sensor 4 (e.g., voltage)
            "ADC5_value": "V",                         # Analog sensor 5 (e.g., voltage)
            "ADC6_value": "V",                         # Analog sensor 6 (e.g., voltage)
            "pH_value": "pH",                          # pH sensor value
            "orp_value": "mV",                         # ORP (Oxidation Reduction Potential) sensor value
            "pot_value": "mg/l",                       # Potentiometer value (e.g., chlorine level)
            "PUMP_RPM_0": "RPM",                       # Pump RPM sensor 0
            "PUMP_RPM_1": "RPM",                       # Pump RPM sensor 1
            "PUMP_RPM_2": "RPM",                       # Pump RPM sensor 2
            "PUMP_RPM_3": "RPM",                       # Pump RPM sensor 3
            "SYSTEM_carrier_alive_count": None,        # Carrier alive count (unitless)
            "SYSTEM_ext1module_alive_count": None,     # External module 1 alive count (unitless)
            "SYSTEM_dosagemodule_alive_count": None,   # Dosage module alive count (unitless)
            "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "mL",   # Daily chlorine dosing (mL)
            "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": "mL",      # Total chlorine can amount (mL)
            "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": "mL",  # Daily electrolytic dosing (mL)
            "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": "mL",     # Total electrolytic can amount (mL)
            "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "mL",  # Daily pH-minus dosing (mL)
            "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": "mL",     # Total pH-minus can amount (mL)
            "PUMP_RUNTIME": None,                      # Pump runtime (hh:mm:ss)
            "SOLAR_RUNTIME": None,                     # Solar runtime (hh:mm:ss)
            "HEATER_RUNTIME": None,                    # Heater runtime (hh:mm:ss)
            "BACKWASH_RUNTIME": None,                  # Backwash runtime (hh:mm:ss)
            "OMNI_DC0_RUNTIME": None,                  # OMNI DC0 runtime (hh:mm:ss)
            "OMNI_DC1_RUNTIME": None,                  # OMNI DC1 runtime (hh:mm:ss)
            "CPU_TEMP": "°C",                          # CPU temperature
            "SYSTEM_MEMORY": "MB",                     # System memory usage
            "LOAD_AVG": "%",                           # Load average percentage

            # Erweiterte Sensorwerte:
            "WATER_TEMPERATURE": "°C",                 # Pool water temperature
            "AIR_TEMPERATURE": "°C",                   # Ambient air temperature near the pool
            "HUMIDITY": "%",                           # Humidity level around the pool
            "SOLAR_PANEL_TEMPERATURE": "°C",           # Temperature of the solar panel
            "FILTER_PRESSURE": "bar",                  # Pressure in the pool filter
            "HEATER_TEMPERATURE": "°C",                # Heater output temperature
            "COVER_POSITION": "%",                     # Position of the pool cover (0-100%)
            "UV_INTENSITY": "W/m²",                    # UV sensor value (for pool sterilization)
            "TDS": "ppm",                              # Total dissolved solids in the water
            "CALCIUM_HARDNESS": "ppm",                 # Calcium hardness in pool water
            "ALKALINITY": "ppm",                       # Alkalinity level of the water
            "SALINITY": "ppm",                         # Salinity of the pool water
            "TURBIDITY": "NTU",                        # Water turbidity (clarity)
            "CHLORINE_LEVEL": "ppm",                   # Chlorine level in the water
            "BROMINE_LEVEL": "ppm",                    # Bromine level in the water
        }
        return units.get(self._key, None)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    binary_sensors = [
        VioletBinarySensor(coordinator, sensor["key"], sensor["icon"], config_entry)
        for sensor in BINARY_SENSORS
    ]
    async_add_entities(binary_sensors)

BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP_STATE", "icon": "mdi:water-pump"},  # Binary sensor for pump state
    {"name": "Solar State", "key": "SOLARSTATE", "icon": "mdi:solar-power"},  # Binary sensor for solar state
    {"name": "Heater State", "key": "HEATERSTATE", "icon": "mdi:radiator"},  # Binary sensor for heater state
    {"name": "Cover State", "key": "COVER_STATE", "icon": "mdi:garage"},  # Binary sensor for pool cover position
    {"name": "Refill State", "key": "REFILL_STATE", "icon": "mdi:water-boiler"},  # Binary sensor for water refill
    {"name": "Light State", "key": "LIGHT_STATE", "icon": "mdi:lightbulb"},  # Binary sensor for pool light
]
