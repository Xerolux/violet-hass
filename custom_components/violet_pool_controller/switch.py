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
            return "mdi:chemical-weapon" if self.is_on else "mdi:chemical-weapon-off"
        elif self._key == "DOS_4_PHM":
            return "mdi:chemical-weapon" if self.is_on else "mdi:chemical-weapon-off"
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
    """Set up Violet Device switches from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["icon"])
        for switch in SWITCHES
    ]
    async_add_entities(switches)


SWITCHES = [
    {"name": "Pump Switch", "key": "PUMP", "icon": "mdi:water-pump"},  # Switch for controlling the pump
    {"name": "Light Switch", "key": "LIGHT", "icon": "mdi:lightbulb"},  # Switch for controlling the pool light
    {"name": "Eco Mode", "key": "ECO", "icon": "mdi:leaf"},  # Switch for Eco mode
    {"name": "Chlorine Dosing Switch", "key": "DOS_1_CL", "icon": "mdi:chemical-weapon"},  # Chlorine dosing switch
    {"name": "pH-minus Dosing Switch", "key": "DOS_4_PHM", "icon": "mdi:chemical-weapon"},  # pH-minus dosing switch
]
