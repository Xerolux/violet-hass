import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class VioletSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Violet Device Switch."""

    def __init__(self, coordinator, key, icon):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"

    def _get_switch_state(self):
        """Helper method to retrieve the current switch state from the coordinator."""
        return self.coordinator.data.get(self._key)

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._get_switch_state() == 1

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        try:
            async with self.coordinator.session.post(f"{self.coordinator.api_url}/turn_on/{self._key}") as response:
                response.raise_for_status()
        except Exception as err:
            _LOGGER.error(f"Error turning on {self._key}: {err}")

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        try:
            async with self.coordinator.session.post(f"{self.coordinator.api_url}/turn_off/{self._key}") as response:
                response.raise_for_status()
        except Exception as err:
            _LOGGER.error(f"Error turning off {self._key}: {err}")

    @property
    def icon(self):
        """Return the icon depending on the switch state."""
        if self._key == "PUMP":
            return "mdi:water-pump" if self.is_on else "mdi:water-pump-off"
        elif self._key == "LIGHT":
            return "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb"
        elif self._key == "ECO":
            return "mdi:leaf" if self.is_on else "mdi:leaf-off"
        elif self._key == "DOS_1_CL":
            return "mdi:flask" if self.is_on else "mdi:atom"
        elif self._key == "DOS_4_PHM":
            return "mdi:flask" if self.is_on else "mdi:atom"
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
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
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
            "SYSTEM_carrier_alive_count": None,
            "SYSTEM_ext1module_alive_count": None,
            "SYSTEM_dosagemodule_alive_count": None,
            "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "mL",
            "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": "mL",
            "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": "mL",
            "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": "mL",
            "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "mL",
            "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": "mL",
            "PUMP_RUNTIME": None,
            "SOLAR_RUNTIME": None,
            "HEATER_RUNTIME": None,
            "BACKWASH_RUNTIME": None,
            "OMNI_DC0_RUNTIME": None,
            "OMNI_DC1_RUNTIME": None,
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
        return units.get(self._key, None)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device switches from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["icon"])
        for switch in SWITCHES
    ]
    async_add_entities(switches)


SWITCHES = [
    {"name": "Pump Switch", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Light Switch", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Eco Mode", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "Chlorine Dosing Switch", "key": "DOS_1_CL", "icon": "mdi:flask"},
    {"name": "pH-minus Dosing Switch", "key": "DOS_4_PHM", "icon": "mdi:flask"},
]
