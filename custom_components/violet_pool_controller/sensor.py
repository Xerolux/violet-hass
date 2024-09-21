import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, CONF_API_URL, CONF_POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Violet Device sensors, binary sensors, and switches from a config entry."""
    api_url = config_entry.data.get(CONF_API_URL)
    polling_interval = config_entry.data.get(CONF_POLLING_INTERVAL)

    # Get the shared aiohttp session
    session = aiohttp_client.async_get_clientsession(hass)

    # Create a coordinator to manage polling and updating entities
    coordinator = VioletDataUpdateCoordinator(
        hass, api_url, polling_interval, session
    )

    # Fetch initial data to create entities dynamically based on the keys
    await coordinator.async_config_entry_first_refresh()

    # Create sensors, binary sensors, and switches for each key in the API data
    sensors = [
        VioletDeviceSensor(coordinator, sensor["key"], sensor["icon"], config_entry)
        for sensor in SENSORS
    ]

    binary_sensors = [
        VioletBinarySensor(coordinator, sensor["key"], sensor["icon"])
        for sensor in BINARY_SENSORS
    ]

    switches = [
        VioletSwitch(coordinator, switch["key"], switch["icon"])
        for switch in SWITCHES
    ]

    async_add_entities(sensors + binary_sensors + switches)


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Device data."""

    def __init__(self, hass, api_url, polling_interval, session):
        """Initialize the coordinator."""
        self.api_url = api_url
        self.session = session
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=polling_interval),
        )

    async def _async_update_data(self):
        """Fetch data from the Violet API."""
        try:
            async with self.session.get(self.api_url, ssl=False, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


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
            "sw_version": self.coordinator.data.get('fw', 'Unknown'),  # Firmware version from JSON
            "configuration_url": f"http://{self._config_entry.data.get('host', 'Unknown IP')}",  # IP from config entry
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
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
            "SYSTEM_dosagemodule_cpu_temperature": "°C",
            "SYSTEM_carrier_alive_count": None,  # Count, unitless
            "SYSTEM_ext1module_alive_count": None,  # Count, unitless
            "SYSTEM_dosagemodule_alive_count": None,  # Count, unitless
            "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "mL",
            "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": "ml",
            "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": "mL",
            "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": "ml",
            "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "mL",
            "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": "ml",
            "PUMP_RUNTIME": None,  # Time duration format (hh:mm:ss)
            "SOLAR_RUNTIME": None,  # Time duration format (hh:mm:ss)
            "HEATER_RUNTIME": None,  # Time duration format (hh:mm:ss)
            "BACKWASH_RUNTIME": None,  # Time duration format (hh:mm:ss)
            "OMNI_DC0_RUNTIME": None,  # Time duration format (hh:mm:ss)
            "OMNI_DC1_RUNTIME": None,  # Time duration format (hh:mm:ss)
            "CPU_TEMP": "°C",
            "SYSTEM_MEMORY": "MB",
            "LOAD_AVG": "%",
        }
        return units.get(self._key, None)


class VioletBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    def __init__(self, coordinator, key, icon):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get(self._key) == 1

    @property
    def icon(self):
        """Return the icon."""
        return self._icon


class VioletSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Violet Device Switch."""

    def __init__(self, coordinator, key, icon):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = f"Violet {self._key}"
        self._attr_unique_id = f"{DOMAIN}_{self._key}"

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.coordinator.data.get(self._key) == 1

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        # Add the API call to turn the switch on
        pass

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        # Add the API call to turn the switch off
        pass

    @property
    def icon(self):
        """Return the icon."""
        return self._icon


# Define your sensors, binary sensors, and switches with appropriate MDI icons
SENSORS = [
    {"name": "Messwasserüberwachung", "key": "IMP1_value", "icon": "mdi:flash"},
    {"name": "IMP2 Value", "key": "IMP2_value", "icon": "mdi:flash"},
    {"name": "Pump Power", "key": "pump_rs485_pwr", "icon": "mdi:power"},
    {"name": "System CPU Temperature", "key": "SYSTEM_cpu_temperature", "icon": "mdi:thermometer"},
    {"name": "System Dosage Temperature", "key": "SYSTEM_dosagemodule_cpu_temperature", "icon": "mdi:thermometer"},
    {"name": "System Memory Usage", "key": "SYSTEM_memoryusage", "icon": "mdi:memory"},
    {"name": "Carrier CPU Temperature", "key": "SYSTEM_carrier_cpu_temperature", "icon": "mdi:thermometer"},
    {"name": "pH Value", "key": "pH_value", "icon": "mdi:flask"},
    {"name": "pHM Daily", "key": "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML", "icon": "mdi:flask"},
    {"name": "ORP Value", "key": "orp_value", "icon": "mdi:chemical-weapon"},
    {"name": "ORP Daily", "key": "DOS_1_CL_DAILY_DOSING_AMOUNT_ML", "icon": "mdi:chemical-weapon"},
    {"name": "Potentiometer Value", "key": "pot_value", "icon": "mdi:gauge"},
    {"name": "OneWire 1 Temperature", "key": "onewire1_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 2 Temperature", "key": "onewire2_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 3 Temperature", "key": "onewire3_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 4 Temperature", "key": "onewire4_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 5 Temperature", "key": "onewire5_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 6 Temperature", "key": "onewire6_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 7 Temperature", "key": "onewire7_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 8 Temperature", "key": "onewire8_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 9 Temperature", "key": "onewire9_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 10 Temperature", "key": "onewire10_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 11 Temperature", "key": "onewire11_value", "icon": "mdi:thermometer"},
    {"name": "OneWire 12 Temperature", "key": "onewire12_value", "icon": "mdi:thermometer"},
    {"name": "Onewire Sensor 1 ROM Code", "key": "onewire1romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 2 ROM Code", "key": "onewire2romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 3 ROM Code", "key": "onewire3romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 4 ROM Code", "key": "onewire4romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 5 ROM Code", "key": "onewire5romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 6 ROM Code", "key": "onewire6romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 7 ROM Code", "key": "onewire7romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 8 ROM Code", "key": "onewire8romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 9 ROM Code", "key": "onewire9romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 10 ROM Code", "key": "onewire10romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 11 ROM Code", "key": "onewire11romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 12 ROM Code", "key": "onewire12romcode", "icon": "mdi:barcode"},
    {"name": "Onewire Sensor 1 Fault Count", "key": "onewire1_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 2 Fault Count", "key": "onewire2_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 3 Fault Count", "key": "onewire3_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 4 Fault Count", "key": "onewire4_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 5 Fault Count", "key": "onewire5_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 6 Fault Count", "key": "onewire6_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 7 Fault Count", "key": "onewire7_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 8 Fault Count", "key": "onewire8_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 9 Fault Count", "key": "onewire9_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 10 Fault Count", "key": "onewire10_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 11 Fault Count", "key": "onewire11_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 12 Fault Count", "key": "onewire12_faultcount", "icon": "mdi:alert-circle"},
    {"name": "Onewire Sensor 1 Freeze Count", "key": "onewire1_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 2 Freeze Count", "key": "onewire2_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 3 Freeze Count", "key": "onewire3_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 4 Freeze Count", "key": "onewire4_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 5 Freeze Count", "key": "onewire5_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 6 Freeze Count", "key": "onewire6_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 7 Freeze Count", "key": "onewire7_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 8 Freeze Count", "key": "onewire8_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 9 Freeze Count", "key": "onewire9_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 10 Freeze Count", "key": "onewire10_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 11 Freeze Count", "key": "onewire11_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 12 Freeze Count", "key": "onewire12_freezecount", "icon": "mdi:snowflake"},
    {"name": "Onewire Sensor 1 State", "key": "onewire1_state", "icon": "mdi:check"},
    {"name": "Onewire Sensor 2 State", "key": "onewire2_state", "icon": "mdi:check"},
    {"name": "Onewire Sensor 3 State", "key": "onewire3_state", "icon": "mdi:check"},
    {"name": "Onewire Sensor 4 State", "key": "onewire4_state", "icon": "mdi:check"},
    {"name": "Onewire Sensor 5 State", "key": "onewire5_state", "icon": "mdi:alert"},
    {"name": "Onewire Sensor 6 State", "key": "onewire6_state", "icon": "mdi:alert"},
    {"name": "Onewire Sensor 7 State", "key": "onewire7_state", "icon": "mdi:check"},
    {"name": "Onewire Sensor 8 State", "key": "onewire8_state", "icon": "mdi:check"},
    {"name": "Onewire Sensor 9 State", "key": "onewire9_state", "icon": "mdi:alert"},
    {"name": "Onewire Sensor 10 State", "key": "onewire10_state", "icon": "mdi:check"},
    {"name": "Onewire Sensor 11 State", "key": "onewire11_state", "icon": "mdi:alert"},
    {"name": "Onewire Sensor 12 State", "key": "onewire12_state", "icon": "mdi:alert"},
    {"name": "Onewire Sensor 1 Min Value", "key": "onewire1_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 1 Max Value", "key": "onewire1_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 2 Min Value", "key": "onewire2_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 2 Max Value", "key": "onewire2_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 3 Min Value", "key": "onewire3_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 3 Max Value", "key": "onewire3_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 4 Min Value", "key": "onewire4_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 4 Max Value", "key": "onewire4_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 5 Min Value", "key": "onewire5_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 5 Max Value", "key": "onewire5_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 6 Min Value", "key": "onewire6_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 6 Max Value", "key": "onewire6_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 7 Min Value", "key": "onewire7_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 7 Max Value", "key": "onewire7_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 8 Min Value", "key": "onewire8_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 8 Max Value", "key": "onewire8_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 9 Min Value", "key": "onewire9_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 9 Max Value", "key": "onewire9_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 10 Min Value", "key": "onewire10_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 10 Max Value", "key": "onewire10_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 11 Min Value", "key": "onewire11_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 11 Max Value", "key": "onewire11_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "Onewire Sensor 12 Min Value", "key": "onewire12_value_min", "icon": "mdi:thermometer-minus"},
    {"name": "Onewire Sensor 12 Max Value", "key": "onewire12_value_max", "icon": "mdi:thermometer-plus"},
    {"name": "pH Min Value", "key": "pH_value_min", "icon": "mdi:water-minus"},
    {"name": "pH Max Value", "key": "pH_value_max", "icon": "mdi:water-plus"},
    {"name": "ORP Min Value", "key": "orp_value_min", "icon": "mdi:flash-minus"},
    {"name": "ORP Max Value", "key": "orp_value_max", "icon": "mdi:flash-plus"},
    {"name": "Potentiometer Min Value", "key": "pot_value_min", "icon": "mdi:gauge-minus"},
    {"name": "Potentiometer Max Value", "key": "pot_value_max", "icon": "mdi:gauge-plus"},
    {"name": "Filterdruck", "key": "ADC1_value", "icon": "mdi:waveform"},
    {"name": "Schwallwasser", "key": "ADC2_value", "icon": "mdi:waveform"},
    {"name": "Durchfluss", "key": "ADC3_value", "icon": "mdi:waveform"},
    {"name": "ADC4", "key": "ADC4_value", "icon": "mdi:waveform"},
    {"name": "ADC5", "key": "ADC5_value", "icon": "mdi:waveform"},
    {"name": "ADC6", "key": "ADC6_value", "icon": "mdi:waveform"},
    {"name": "Pump RPM 0", "key": "PUMP_RPM_0", "icon": "mdi:fan"},
    {"name": "Pump RPM 1", "key": "PUMP_RPM_1", "icon": "mdi:fan"},
    {"name": "Pump RPM 2", "key": "PUMP_RPM_2", "icon": "mdi:fan"},
    {"name": "Pump RPM 3", "key": "PUMP_RPM_3", "icon": "mdi:fan"},
    {"name": "Backwash State", "key": "BACKWASH", "icon": "mdi:water-pump"},
    {"name": "Backwash Rinse State", "key": "BACKWASHRINSE", "icon": "mdi:water-pump"},
    {"name": "Omni DC0 State", "key": "OMNI_DC0", "icon": "mdi:power-plug"},
    {"name": "Omni DC1 State", "key": "OMNI_DC1", "icon": "mdi:power-plug"},
    {"name": "Omni DC2 State", "key": "OMNI_DC2", "icon": "mdi:power-plug"},
    {"name": "Omni DC3 State", "key": "OMNI_DC3", "icon": "mdi:power-plug"},
    {"name": "Eco Mode State", "key": "ECO", "icon": "mdi:leaf"}
    {"name": "Solar Last On", "key": "SOLAR_LAST_ON", "icon": "mdi:timer"},
    {"name": "Solar Last Off", "key": "SOLAR_LAST_OFF", "icon": "mdi:timer-off"},
    {"name": "Heater Last On", "key": "HEATER_LAST_ON", "icon": "mdi:timer"},
    {"name": "Heater Last Off", "key": "HEATER_LAST_OFF", "icon": "mdi:timer-off"},
    {"name": "Backwash Last On", "key": "BACKWASH_LAST_ON", "icon": "mdi:timer"},
    {"name": "Backwash Last Off", "key": "BACKWASH_LAST_OFF", "icon": "mdi:timer-off"},
]

BINARY_SENSORS = [
    {"name": "Pump State", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Solar State", "key": "SOLAR", "icon": "mdi:solar-power"},
    {"name": "Heater State", "key": "HEATER", "icon": "mdi:radiator"},
    {"name": "Cover State", "key": "COVER_STATE", "icon": "mdi:garage"},
    {"name": "Refill State", "key": "REFILL_STATE", "icon": "mdi:water-boiler"},
    {"name": "Light State", "key": "LIGHT", "icon": "mdi:lightbulb"},
]

SWITCHES = [
    {"name": "Pump Switch", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Light Switch", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Eco Mode", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "DOS CL Switch", "key": "DOS_1_CL", "icon": "mdi:chemical-weapon"},
    {"name": "DOS PHM Switch", "key": "DOS_4_PHM", "icon": "mdi:chemical-weapon"},
]
