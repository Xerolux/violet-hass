import logging
from typing import Any, Optional
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, CONF_DEVICE_NAME, CONF_API_URL
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

# Fehlende Konstante ersetzen
CONCENTRATION_MILLIGRAMS_PER_LITER = "mg/L"

_LOGGER = logging.getLogger(__name__)

# Liste der Sensoren, die keine Einheit benötigen
NO_UNIT_SENSORS = [
    "SOLAR_LAST_OFF",
    "HEATER_LAST_ON",
    "HEATER_LAST_OFF",
    "BACKWASH_LAST_ON",
    "BACKWASH_LAST_OFF",
    "PUMP_LAST_ON",
    "PUMP_LAST_OFF",
    "SW_VERSION",  # Software-Versionen benötigen keine Einheit
    "SW_VERSION_CARRIER",
    "SYSTEM_carrier_alive_count",
    "SYSTEM_ext1module_alive_count",
    "SYSTEM_dosagemodule_alive_count",
]


class VioletDeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Violet Device Sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        key: str,
        icon: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key: str = key
        self._icon: str = icon
        self._config_entry: ConfigEntry = config_entry
        self._attr_name: str = f"Violet {key}"  # Mehr beschreibender Name
        self._attr_unique_id: str = f"{config_entry.entry_id}_{key}"  # Eindeutige ID mit entry_id
        self._state: Any = None  # Cache für den Sensorzustand
        self._has_logged_none_state: bool = False  # Verhindert mehrfaches Loggen, wenn state None ist

        # Geräteinformationen setzen – entry_id als eindeutiger Bezeichner
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": (
                f"{config_entry.data.get(CONF_DEVICE_NAME, 'Violet Pool Controller')} "
                f"({config_entry.data.get(CONF_API_URL, 'Unknown IP')})"
            ),
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",  # Falls möglich dynamisch abrufbar machen
            "sw_version": self.coordinator.data.get("fw", "Unknown"),
            "configuration_url": f"http://{config_entry.data.get(CONF_API_URL, 'Unknown IP')}",
        }

    @property
    def state(self) -> Any:
        """Return the state of the sensor."""
        self._state = self._get_sensor_state()
        if self._state is None and not self._has_logged_none_state:
            _LOGGER.warning("Sensor %s returned None as its state.", self._key)
            self._has_logged_none_state = True
        return self._state

    @property
    def icon(self) -> str:
        """Return the dynamic icon depending on the sensor state, if applicable."""
        if self._key == "pump_rs485_pwr":
            return "mdi:power" if self.state else "mdi:power-off"
        if self._key.startswith("onewire"):
            return "mdi:thermometer" if self.state is not None else "mdi:thermometer-off"
        return self._icon

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self._key in self.coordinator.data

    @property
    def unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement."""
        if self._key in NO_UNIT_SENSORS:
            return None
        return self._get_unit_for_key(self._key)

    @property
    def state_class(self) -> Optional[str]:
        """Return the state class of the sensor."""
        return self._get_state_class_for_key(self._key)

    @property
    def device_class(self) -> Optional[str]:
        """Return the device class of the sensor."""
        return self._get_device_class_for_key(self._key)

    def _get_sensor_state(self) -> Any:
        """Helper method to retrieve the current sensor state from the coordinator."""
        return self.coordinator.data.get(self._key)

    def _get_unit_for_key(self, key: str) -> Optional[str]:
        """Helper method to retrieve the unit of measurement based on the sensor key."""
        units = {
            "IMP1_value": "cm/s",
            "IMP2_value": "cm/s",
            "pump_rs485_pwr": UnitOfPower.WATT,
            "SYSTEM_cpu_temperature": UnitOfTemperature.CELSIUS,
            "SYSTEM_carrier_cpu_temperature": UnitOfTemperature.CELSIUS,
            "SYSTEM_dosagemodule_cpu_temperature": UnitOfTemperature.CELSIUS,
            "SYSTEM_memoryusage": "MB",  # Nicht standard, aber gültig
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
            "ADC2_value": "cm",  # Nicht standard
            "ADC3_value": "m³",  # Nicht standard; alternativ UnitOfVolume.CUBIC_METERS
            "ADC4_value": "V",   # Nicht standard
            "ADC5_value": "V",   # Nicht standard
            "ADC6_value": "V",   # Nicht standard
            "pH_value": "pH",    # Nicht standard
            "orp_value": "mV",   # Nicht standard, Millivolt
            "pot_value": CONCENTRATION_MILLIGRAMS_PER_LITER,
            "PUMP_RPM_0": "RPM",  # Nicht standard
            "PUMP_RPM_1": "RPM",  # Nicht standard
            "PUMP_RPM_2": "RPM",  # Nicht standard
            "PUMP_RPM_3": "RPM",  # Nicht standard
            "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": UnitOfVolume.MILLILITERS,
            "CPU_TEMP": UnitOfTemperature.CELSIUS,
            "CPU_TEMP_CARRIER": UnitOfTemperature.CELSIUS,
            "SYSTEM_MEMORY": "MB",  # Nicht standard
            "LOAD_AVG": PERCENTAGE,
            "WATER_TEMPERATURE": UnitOfTemperature.CELSIUS,
            "AIR_TEMPERATURE": UnitOfTemperature.CELSIUS,
            "HUMIDITY": PERCENTAGE,
            "SOLAR_PANEL_TEMPERATURE": UnitOfTemperature.CELSIUS,
            "FILTER_PRESSURE": UnitOfPressure.BAR,
            "HEATER_TEMPERATURE": UnitOfTemperature.CELSIUS,
            "COVER_POSITION": PERCENTAGE,
            "UV_INTENSITY": "W/m²",  # Nicht standard, aber gültig
            "TDS": CONCENTRATION_PARTS_PER_MILLION,
            "CALCIUM_HARDNESS": CONCENTRATION_PARTS_PER_MILLION,
            "ALKALINITY": CONCENTRATION_PARTS_PER_MILLION,
            "SALINITY": CONCENTRATION_PARTS_PER_MILLION,
            "TURBIDITY": "NTU",  # Nicht standard
            "CHLORINE_LEVEL": CONCENTRATION_PARTS_PER_MILLION,
            "BROMINE_LEVEL": CONCENTRATION_PARTS_PER_MILLION,
            "PUMP_RUNTIME": UnitOfTime.SECONDS,
            "SOLAR_RUNTIME": UnitOfTime.SECONDS,
            "HEATER_RUNTIME": UnitOfTime.SECONDS,
            "BACKWASH_RUNTIME": UnitOfTime.SECONDS,
            "OMNI_DC0_RUNTIME": UnitOfTime.SECONDS,
            "OMNI_DC1_RUNTIME": UnitOfTime.SECONDS,
        }
        return units.get(key)

    def _get_state_class_for_key(self, key: str) -> Optional[str]:
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
            "SYSTEM_carrier_alive_count": SensorStateClass.TOTAL_INCREASING,
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
        return state_classes.get(key)

    def _get_device_class_for_key(self, key: str) -> Optional[str]:
        """Helper method to retrieve the device class based on the sensor key."""
        device_classes = {
            "SYSTEM_cpu_temperature": SensorDeviceClass.TEMPERATURE,
            "SYSTEM_carrier_cpu_temperature": SensorDeviceClass.TEMPERATURE,
            "SYSTEM_dosagemodule_cpu_temperature": SensorDeviceClass.TEMPERATURE,
            "onewire1_value": SensorDeviceClass.TEMPERATURE,
            "onewire2_value": SensorDeviceClass.TEMPERATURE,
            "onewire3_value": SensorDeviceClass.TEMPERATURE,
            "onewire4_value": SensorDeviceClass.TEMPERATURE,
            "onewire5_value": SensorDeviceClass.TEMPERATURE,
            "onewire6_value": SensorDeviceClass.TEMPERATURE,
            "onewire7_value": SensorDeviceClass.TEMPERATURE,
            "onewire8_value": SensorDeviceClass.TEMPERATURE,
            "onewire9_value": SensorDeviceClass.TEMPERATURE,
            "onewire10_value": SensorDeviceClass.TEMPERATURE,
            "onewire11_value": SensorDeviceClass.TEMPERATURE,
            "onewire12_value": SensorDeviceClass.TEMPERATURE,
            "CPU_TEMP": SensorDeviceClass.TEMPERATURE,
            "CPU_TEMP_CARRIER": SensorDeviceClass.TEMPERATURE,
            "WATER_TEMPERATURE": SensorDeviceClass.TEMPERATURE,
            "AIR_TEMPERATURE": SensorDeviceClass.TEMPERATURE,
            "SOLAR_PANEL_TEMPERATURE": SensorDeviceClass.TEMPERATURE,
            "HEATER_TEMPERATURE": SensorDeviceClass.TEMPERATURE,
            "HUMIDITY": SensorDeviceClass.HUMIDITY,
            "FILTER_PRESSURE": SensorDeviceClass.PRESSURE,
            "UV_INTENSITY": SensorDeviceClass.ILLUMINANCE,
            "TDS": SensorDeviceClass.CONCENTRATION,
            "CALCIUM_HARDNESS": SensorDeviceClass.CONCENTRATION,
            "ALKALINITY": SensorDeviceClass.CONCENTRATION,
            "SALINITY": SensorDeviceClass.CONCENTRATION,
            "TURBIDITY": SensorDeviceClass.ILLUMINANCE,
            "CHLORINE_LEVEL": SensorDeviceClass.CONCENTRATION,
            "BROMINE_LEVEL": SensorDeviceClass.CONCENTRATION,
        }
        return device_classes.get(key)
