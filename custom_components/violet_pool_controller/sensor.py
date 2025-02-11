import logging
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
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

# Define SENSORS *before* async_setup_entry
SENSORS = [
    SensorEntityDescription(key="IMP1_value", name="Messwasserüberwachung", icon="mdi:flash"),
    SensorEntityDescription(key="IMP2_value", name="IMP2 Value", icon="mdi:flash"),

    # Power and Temperature
    SensorEntityDescription(key="pump_rs485_pwr", name="Pump Power", icon="mdi:power"),
    SensorEntityDescription(key="SYSTEM_cpu_temperature", name="System CPU Temperature", icon="mdi:thermometer"),
    SensorEntityDescription(key="SYSTEM_carrier_cpu_temperature", name="Carrier CPU Temperature", icon="mdi:thermometer"),
    SensorEntityDescription(key="SYSTEM_dosagemodule_cpu_temperature", name="System Dosage Module CPU Temperature", icon="mdi:thermometer"),
    SensorEntityDescription(key="SYSTEM_memoryusage", name="System Memory Usage", icon="mdi:memory"),
    SensorEntityDescription(key="CPU_TEMP", name="CPU Temperature", icon="mdi:thermometer"),
    SensorEntityDescription(key="CPU_TEMP_CARRIER", name="CPU Temperature CARRIER", icon="mdi:thermometer"),
    SensorEntityDescription(key="SYSTEM_MEMORY", name="System Memory", icon="mdi:memory"),
    SensorEntityDescription(key="LOAD_AVG", name="Load Average", icon="mdi:chart-line"),

    # Software Version
    SensorEntityDescription(key="SW_VERSION", name="Software Violet Application", icon="mdi:update"),
    SensorEntityDescription(key="SW_VERSION_CARRIER", name="Firmware Violet Carrier", icon="mdi:update"),

    # OneWire Sensors (Temperature, Min/Max Values)
     SensorEntityDescription(key="onewire1_value", name="OneWire 1 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire1_value_min", name="OneWire 1 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire1_value_max", name="OneWire 1 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire2_value", name="OneWire 2 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire2_value_min", name="OneWire 2 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire2_value_max", name="OneWire 2 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire3_value", name="OneWire 3 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire3_value_min", name="OneWire 3 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire3_value_max", name="OneWire 3 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire4_value", name="OneWire 4 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire4_value_min", name="OneWire 4 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire4_value_max", name="OneWire 4 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire5_value", name="OneWire 5 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire5_value_min", name="OneWire 5 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire5_value_max", name="OneWire 5 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire6_value", name="OneWire 6 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire6_value_min", name="OneWire 6 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire6_value_max", name="OneWire 6 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire7_value", name="OneWire 7 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire7_value_min", name="OneWire 7 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire7_value_max", name="OneWire 7 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire8_value", name="OneWire 8 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire8_value_min", name="OneWire 8 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire8_value_max", name="OneWire 8 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire9_value", name="OneWire 9 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire9_value_min", name="OneWire 9 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire9_value_max", name="OneWire 9 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire10_value", name="OneWire 10 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire10_value_min", name="OneWire 10 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire10_value_max", name="OneWire 10 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire11_value", name="OneWire 11 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire11_value_min", name="OneWire 11 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire11_value_max", name="OneWire 11 Max Value", icon="mdi:thermometer-plus"),

     SensorEntityDescription(key="onewire12_value", name="OneWire 12 Temperature", icon="mdi:thermometer"),
     SensorEntityDescription(key="onewire12_value_min", name="OneWire 12 Min Value", icon="mdi:thermometer-minus"),
     SensorEntityDescription(key="onewire12_value_max", name="OneWire 12 Max Value", icon="mdi:thermometer-plus"),

    # Analog Sensors (ADC)
     SensorEntityDescription(key="ADC1_value", name="Filterdruck", icon="mdi:waveform"),
     SensorEntityDescription(key="ADC2_value", name="Schwallwasser", icon="mdi:waveform"),
     SensorEntityDescription(key="ADC3_value", name="Durchfluss", icon="mdi:waveform"),
     SensorEntityDescription(key="ADC4_value", name="ADC4", icon="mdi:waveform"),
     SensorEntityDescription(key="ADC5_value", name="ADC5", icon="mdi:waveform"),
     SensorEntityDescription(key="ADC6_value", name="ADC6", icon="mdi:waveform"),

    # pH and ORP Sensors
     SensorEntityDescription(key="pH_value", name="pH Value", icon="mdi:flask"),
     SensorEntityDescription(key="pH_value_min", name="pH Min Value", icon="mdi:water-minus"),
     SensorEntityDescription(key="pH_value_max", name="pH Max Value", icon="mdi:water-plus"),

     SensorEntityDescription(key="orp_value", name="ORP Value", icon="mdi:chemical-weapon"),
     SensorEntityDescription(key="orp_value_min", name="ORP Min Value", icon="mdi:flash-minus"),
     SensorEntityDescription(key="orp_value_max", name="ORP Max Value", icon="mdi:flash-plus"),
     SensorEntityDescription(key="pot_value", name="Potentiometer Value", icon="mdi:gauge"),
     SensorEntityDescription(key="pot_value_min", name="Potentiometer Min Value", icon="mdi:gauge-low"),
     SensorEntityDescription(key="pot_value_max", name="Potentiometer Max Value", icon="mdi:gauge-high"),

    # Dosing amounts (daily and total)
    SensorEntityDescription(key="DOS_1_CL_DAILY_DOSING_AMOUNT_ML", name="Chlorine Daily Dosing Amount", icon="mdi:flask"),
    SensorEntityDescription(key="DOS_1_CL_TOTAL_CAN_AMOUNT_ML", name="Chlorine Total Can Amount", icon="mdi:flask"),
    SensorEntityDescription(key="DOS_2_ELO_DAILY_DOSING_AMOUNT_ML", name="ELO Daily Dosing Amount", icon="mdi:flask"),
    SensorEntityDescription(key="DOS_2_ELO_TOTAL_CAN_AMOUNT_ML", name="ELO Total Can Amount", icon="mdi:flask"),
    SensorEntityDescription(key="DOS_4_PHM_DAILY_DOSING_AMOUNT_ML", name="pH-minus Daily Dosing Amount", icon="mdi:flask"),
    SensorEntityDescription(key="DOS_4_PHM_TOTAL_CAN_AMOUNT_ML", name="pH-minus Total Can Amount", icon="mdi:flask"),

    # Pump RPM sensors
     SensorEntityDescription(key="PUMP_RPM_0", name="Pump RPM 0", icon="mdi:fan"),
     SensorEntityDescription(key="PUMP_RPM_1", name="Pump RPM 1", icon="mdi:fan"),
     SensorEntityDescription(key="PUMP_RPM_2", name="Pump RPM 2", icon="mdi:fan"),
     SensorEntityDescription(key="PUMP_RPM_3", name="Pump RPM 3", icon="mdi:fan"),

    # Runtime values (duration format hh:mm:ss)
    SensorEntityDescription(key="PUMP_RUNTIME", name="Pump Runtime", icon="mdi:timer"),
    SensorEntityDescription(key="SOLAR_RUNTIME", name="Solar Runtime", icon="mdi:timer"),
    SensorEntityDescription(key="HEATER_RUNTIME", name="Heater Runtime", icon="mdi:timer"),
    SensorEntityDescription(key="BACKWASH_RUNTIME", name="Backwash Runtime", icon="mdi:timer"),
    SensorEntityDescription(key="OMNI_DC0_RUNTIME", name="Omni DC0 Runtime", icon="mdi:timer"),
    SensorEntityDescription(key="OMNI_DC1_RUNTIME", name="Omni DC1 Runtime", icon="mdi:timer"),

    # System states and other
     SensorEntityDescription(key="SYSTEM_carrier_alive_count", name="System Carrier Alive Count", icon="mdi:alert-circle"),
     SensorEntityDescription(key="SYSTEM_ext1module_alive_count", name="System EXT1 Module Alive Count", icon="mdi:alert-circle"),
     SensorEntityDescription(key="SYSTEM_dosagemodule_alive_count", name="System Dosage Module Alive Count", icon="mdi:alert-circle"),
    # Solar and heater timers
     SensorEntityDescription(key="SOLAR_LAST_ON", name="Solar Last On", icon="mdi:timer"),
     SensorEntityDescription(key="SOLAR_LAST_OFF", name="Solar Last Off", icon="mdi:timer-off"),
     SensorEntityDescription(key="HEATER_LAST_ON", name="Heater Last On", icon="mdi:timer"),
     SensorEntityDescription(key="HEATER_LAST_OFF", name="Heater Last Off", icon="mdi:timer-off"),
     SensorEntityDescription(key="BACKWASH_LAST_ON", name="Backwash Last On", icon="mdi:timer"),
     SensorEntityDescription(key="BACKWASH_LAST_OFF", name="Backwash Last Off", icon="mdi:timer-off"),
]

class VioletDeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Violet Device Sensor."""

    def __init__(self, coordinator, entity_description, config_entry):
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._config_entry = config_entry
        self._attr_name = f"Violet {entity_description.name}"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{entity_description.key}"  # Unique ID
        self._has_logged_none_state = False

    @property
    def state(self):
        """Return the state of the sensor."""
        state = self._get_sensor_state()
        if state is None and not self._has_logged_none_state:
            _LOGGER.warning(f"Sensor {self.entity_description.key} returned None as its state.")
            self._has_logged_none_state = True
        return state

    @property
    def icon(self):
        """Return the dynamic icon."""
        if self.entity_description.key == "pump_rs485_pwr":
            return "mdi:power" if self.state else "mdi:power-off"
        if "onewire" in self.entity_description.key:
            return "mdi:thermometer"
        return self.entity_description.icon

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
        """
