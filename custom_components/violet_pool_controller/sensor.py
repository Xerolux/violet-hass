import logging
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
    UnitOfPressure,
    UnitOfPower,
    PERCENTAGE,
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_MILLIGRAMS_PER_LITER,
)

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
    "SW_VERSION",  # Software versions don't need units
    "SW_VERSION_CARRIER", # Software versions don't need units
]

class VioletDeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Violet Device Sensor."""

    def __init__(self, coordinator, key, icon, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry
        self._attr_name = f"Violet {key}"  # More descriptive name
        self._attr_unique_id = f"{config_entry.entry_id}_{key}"  # Use entry_id for uniqueness
        self._state = None  # Cache the sensor state
        self._has_logged_none_state = False  # Avoid logging multiple warnings for None states

        # Set device info. Crucially use entry_id.
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{config_entry.data.get('device_name', 'Violet Pool Controller')} ({config_entry.data.get('host', 'Unknown IP')})",  # Include IP
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",  # Consider making this dynamic
            "sw_version": self.coordinator.data.get('fw', 'Unknown'),  # Use consistent key
            "configuration_url": f"http://{config_entry.data.get('host', 'Unknown IP')}",
        }


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
            return "mdi:power" if self.state else "mdi:power-off"  # Example dynamic icon
        if self._key.startswith("onewire"):
            return "mdi:thermometer" if self.state is not None else "mdi:thermometer-off"
        return self._icon  # Default icon

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self._key in self.coordinator.data

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._key in NO_UNIT_SENSORS:
            return None  # These sensors should not have a unit of measurement
        return self._get_unit_for_key(self._key)

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return self._get_state_class_for_key(self._key)
    
    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._get_device_class_for_key(self._key)

    def _get_sensor_state(self):
        """Helper method to retrieve the current sensor state from the coordinator."""
        return self.coordinator.data.get(self._key)

    def _get_unit_for_key(self, key):
        """Helper method to retrieve the unit of measurement based on the sensor key."""
        units = {
            "IMP1_value": "cm/s",
            "IMP2_value": "cm/s",
            "pump_rs485_pwr": UnitOfPower.WATT,
            "SYSTEM_cpu_temperature": UnitOfTemperature.CELSIUS,
            "SYSTEM_carrier_cpu_temperature": UnitOfTemperature.CELSIUS,
            "SYSTEM_dosagemodule_cpu_temperature": UnitOfTemperature.CELSIUS,
            "SYSTEM_memoryusage": "MB",  # Not a standard HA unit, but still valid
            "onewire1_value": UnitOfTemperature.CELSIUS,
            "onewire2_value": UnitOfTemperature.CELSIUS,
            "onewire3_value": UnitOfTemperature.CELSIUS,
            "onewire4_value": UnitOfTemperature.CELSIUS,
            "onewire5_value": UnitOfTemperature.CELSIUS,
            "onewire6_value": UnitOfTemperature.CELSIUS,
            "onewire7_value": UnitOfTemperature.CELSIUS,
            "onewire8_value": UnitOfTemperature.CELSIUS,
            "onewire9_value": UnitOfTemperature.CELSIUS,
            "onewire10_value": UnitOfTemperature.CELSIUS,
            "onewire11_value": UnitOfTemperature.CELSIUS,
            "onewire12_value": UnitOfTemperature.CELSIUS,
            "ADC1_value": UnitOfPressure.BAR,
            "ADC2_value": "cm", # Not a standard HA unit
            "ADC3_value": "m³",  # Not a standard HA unit, consider UnitOfVolume.CUBIC_METERS
            "ADC4_value": "V", # Not a standard HA unit
            "ADC5_value": "V", # Not a standard HA unit
            "ADC6_value": "V", # Not a standard HA unit
            "pH_value": "pH",  # Not a standard HA unit
            "orp_value": "mV",  # Not a standard HA unit, millivolts
            "pot_value": CONCENTRATION_MILLIGRAMS_PER_LITER,
            "PUMP_RPM_0": "RPM", # Not a standard HA unit
            "PUMP_RPM_1": "RPM", # Not a standard HA unit
            "PUMP_RPM_2": "RPM", # Not a standard HA unit
            "PUMP_RPM_3": "RPM", # Not a standard HA unit
            "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "CPU_TEMP": UnitOfTemperature.CELSIUS,
            "CPU_TEMP_CARRIER": UnitOfTemperature.CELSIUS,
            "SYSTEM_MEMORY": "MB",  # Not a standard HA unit
            "LOAD_AVG": PERCENTAGE,
            "WATER_TEMPERATURE": UnitOfTemperature.CELSIUS,
            "AIR_TEMPERATURE": UnitOfTemperature.CELSIUS,
            "HUMIDITY": PERCENTAGE,
            "SOLAR_PANEL_TEMPERATURE": UnitOfTemperature.CELSIUS,
            "FILTER_PRESSURE": UnitOfPressure.BAR,
            "HEATER_TEMPERATURE": UnitOfTemperature.CELSIUS,
            "COVER_POSITION": PERCENTAGE,
            "UV_INTENSITY": "W/m²",  # Not a standard HA unit, but valid.
            "TDS": CONCENTRATION_PARTS_PER_MILLION,
            "CALCIUM_HARDNESS": CONCENTRATION_PARTS_PER_MILLION,
            "ALKALINITY": CONCENTRATION_PARTS_PER_MILLION,
            "SALINITY": CONCENTRATION_PARTS_PER_MILLION,
            "TURBIDITY": "NTU",   # Not a standard HA unit
            "CHLORINE_LEVEL": CONCENTRATION_PARTS_PER_MILLION,
            "BROMINE_LEVEL": CONCENTRATION_PARTS_PER_MILLION,
            "PUMP_RUNTIME": UnitOfTime.SECONDS,
            "SOLAR_RUNTIME": UnitOfTime.SECONDS,
            "HEATER_RUNTIME": UnitOfTime.SECONDS,
            "BACKWASH_RUNTIME": UnitOfTime.SECONDS,
            "OMNI_DC0_RUNTIME": UnitOfTime.SECONDS,
            "OMNI_DC1_RUNTIME": UnitOfTime.SECONDS,
            "SYSTEM_carrier_alive_count": None,  # No unit for a count
            "SYSTEM_ext1module_alive_count": None,  # No unit for a count
            "SYSTEM_dosagemodule_alive_count": None,  # No unit for a count

        }
        return units.get(key, None)

    def _get_state_class_for_key(self, key):
        """Helper method to retrieve the state class based on the sensor key."""
        state_classes = {
            "IMP1_value": SensorStateClass.MEASUREMENT,
            "IMP2_value": SensorStateClass.MEASUREMENT,
            "pump_rs485_pwr": SensorStateClass.MEASUREMENT,
            "SYSTEM_cpu_temperature": SensorStateClass.MEASUREMENT,
            "SYSTEM_carrier_cpu_temperature": SensorStateClass.MEASUREMENT,
            "SYSTEM_dosagemodule_cpu_temperature": SensorStateClass.MEASUREMENT,
            "SYSTEM_memoryusage": SensorStateClass.MEASUREMENT,
            "onewire1_value": SensorStateClass.MEASUREMENT,
            "onewire2_value": SensorStateClass.MEASUREMENT,
            "onewire3_value": SensorStateClass.MEASUREMENT,
            "onewire4_value": SensorStateClass.MEASUREMENT,
            "onewire5_value": SensorStateClass.MEASUREMENT,
            "onewire6_value": SensorStateClass.MEASUREMENT,
            "onewire7_value": SensorStateClass.MEASUREMENT,
            "onewire8_value": SensorStateClass.MEASUREMENT,
            "onewire9_value": SensorStateClass.MEASUREMENT,
            "onewire10_value": SensorStateClass.MEASUREMENT,
            "onewire11_value": SensorStateClass.MEASUREMENT,
            "onewire12_value": SensorStateClass.MEASUREMENT,
            "ADC1_value": SensorStateClass.MEASUREMENT,
            "ADC2_value": SensorStateClass.MEASUREMENT,
            "ADC3_value": SensorStateClass.MEASUREMENT,
            "ADC4_value": SensorStateClass.MEASUREMENT,
            "ADC5_value": SensorStateClass.MEASUREMENT,
            "ADC6_value": SensorStateClass.MEASUREMENT,
            "pH_value": SensorStateClass.MEASUREMENT,
            "orp_value": SensorStateClass.MEASUREMENT,
            "pot_value": SensorStateClass.MEASUREMENT,
            "PUMP_RPM_0": SensorStateClass.MEASUREMENT,
            "PUMP_RPM_1": SensorStateClass.MEASUREMENT,
            "PUMP_RPM_2": SensorStateClass.MEASUREMENT,
            "PUMP_RPM_3": SensorStateClass.MEASUREMENT,
            "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": SensorStateClass.MEASUREMENT,
            "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": SensorStateClass.TOTAL_INCREASING,
            "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": SensorStateClass.MEASUREMENT,
            "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": SensorStateClass.TOTAL_INCREASING,
            "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": SensorStateClass.MEASUREMENT,
            "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": SensorStateClass.TOTAL_INCREASING,
            "CPU_TEMP": SensorStateClass.MEASUREMENT,
            "CPU_TEMP_CARRIER": SensorStateClass.MEASUREMENT,
            "SYSTEM_MEMORY": SensorStateClass.MEASUREMENT,
            "LOAD_AVG": SensorStateClass.MEASUREMENT,
            "WATER_TEMPERATURE": SensorStateClass.MEASUREMENT,
            "AIR_TEMPERATURE": SensorStateClass.MEASUREMENT,
            "HUMIDITY": SensorStateClass.MEASUREMENT,
            "SOLAR_PANEL_TEMPERATURE": SensorStateClass.MEASUREMENT,
            "FILTER_PRESSURE": SensorStateClass.MEASUREMENT,
            "HEATER_TEMPERATURE": SensorStateClass.MEASUREMENT,
            "COVER_POSITION": SensorStateClass.MEASUREMENT,
            "UV_INTENSITY": SensorStateClass.MEASUREMENT,
            "TDS": SensorStateClass.MEASUREMENT,
            "CALCIUM_HARDNESS": SensorStateClass.MEASUREMENT,
            "ALKALINITY": SensorStateClass.MEASUREMENT,
            "SALINITY": SensorStateClass.MEASUREMENT,
            "TURBIDITY": SensorStateClass.MEASUREMENT,
            "CHLORINE_LEVEL": SensorStateClass.MEASUREMENT,
            "BROMINE_LEVEL": SensorStateClass.MEASUREMENT,
            "PUMP_RUNTIME": SensorStateClass.TOTAL_INCREASING,
            "SOLAR_RUNTIME": SensorStateClass.TOTAL_INCREASING,
            "HEATER_RUNTIME": SensorStateClass.TOTAL_INCREASING,
            "BACKWASH_RUNTIME": SensorStateClass.TOTAL_INCREASING,
            "OMNI_DC0_RUNTIME": SensorStateClass.TOTAL_INCREASING,
            "OMNI_DC1_RUNTIME": SensorStateClass.TOTAL_INCREASING,
            "SYSTEM_carrier_alive_count":  SensorStateClass.TOTAL_INCREASING,
            "SYSTEM_ext1module_alive_count": SensorStateClass.TOTAL_INCREASING,
            "SYSTEM_dosagemodule_alive_count": SensorStateClass.TOTAL_INCREASING,
            "onewire1_value_min": SensorStateClass.MEASUREMENT,
            "onewire1_value_max": SensorStateClass.MEASUREMENT,
            "onewire2_value_min": SensorStateClass.MEASUREMENT,
            "onewire2_value_max": SensorStateClass.MEASUREMENT,
            "onewire3_value_min": SensorStateClass.MEASUREMENT,
            "onewire3_value_max": SensorStateClass.MEASUREMENT,
            "onewire4_value_min": SensorStateClass.MEASUREMENT,
            "onewire4_value_max": SensorStateClass.MEASUREMENT,
            "onewire5_value_min": SensorStateClass.MEASUREMENT,
            "onewire5_value_max": SensorStateClass.MEASUREMENT,
            "onewire6_value_min": SensorStateClass.MEASUREMENT,
            "onewire6_value_max": SensorStateClass.MEASUREMENT,
            "onewire7_value_min": SensorStateClass.MEASUREMENT,
            "onewire7_value_max": SensorStateClass.MEASUREMENT,
            "onewire8_value_min": SensorStateClass.MEASUREMENT,
            "onewire8_value_max": SensorStateClass.MEASUREMENT,
            "onewire9_value_min": SensorStateClass.MEASUREMENT,
            "onewire9_value_max": SensorStateClass.MEASUREMENT,
            "onewire10_value_min": SensorStateClass.MEASUREMENT,
            "onewire10_value_max": SensorStateClass.MEASUREMENT,
            "onewire11_value_min": SensorStateClass.MEASUREMENT,
            "onewire11_value_max": SensorStateClass.MEASUREMENT,
            "onewire12_value_min": SensorStateClass.MEASUREMENT,
            "onewire12_value_max": SensorStateClass.MEASUREMENT,
            "pH_value_min": SensorStateClass.MEASUREMENT,
            "pH_value_max": SensorStateClass.MEASUREMENT,
            "orp_value_min": SensorStateClass.MEASUREMENT,
            "orp_value_max": SensorStateClass.MEASUREMENT,
            "pot_value_min": SensorStateClass.MEASUREMENT,
            "pot_value_max": SensorStateClass.MEASUREMENT,
        }
        return state_classes.get(key
