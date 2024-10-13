import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, CONF_API_URL

_LOGGER = logging.getLogger(__name__)

class VioletBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    def __init__(self, coordinator, key, icon, config_entry):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry  # Store config_entry here
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"
        self._attr_is_on = self._get_sensor_state() == 1
        self._attr_icon = self._icon if self._attr_is_on else f"{self._icon}-off"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "violet_pool_controller")},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get('fw') or self.coordinator.data.get('SW_VERSION', 'Unbekannt'),
            "configuration_url": f"http://{self._config_entry.data.get(CONF_API_URL, 'Unknown IP')}",
        }

    def _get_sensor_state(self):
        """Helper method to retrieve the current sensor state from the coordinator."""
        return self.coordinator.data.get(self._key)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement, if applicable."""
        return self._get_unit_for_key(self._key)

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
    """Set up Violet Device binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    binary_sensors = [
        VioletBinarySensor(coordinator, sensor["key"], sensor["icon"], config_entry)
        for sensor in BINARY_SENSORS
    ]
    async_add_entities(binary_sensors)

BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP_STATE", "icon": "mdi:water-pump"},
    {"name": "Solar State", "key": "SOLAR_STATE", "icon": "mdi:solar-power"},
    {"name": "Heater State", "key": "HEATER_STATE", "icon": "mdi:radiator"},
    {"name": "Cover State", "key": "COVER_STATE", "icon": "mdi:garage"},
    {"name": "Refill State", "key": "REFILL_STATE", "icon": "mdi:water-boiler"},
    {"name": "Light State", "key": "LIGHT_STATE", "icon": "mdi:lightbulb"},
]
