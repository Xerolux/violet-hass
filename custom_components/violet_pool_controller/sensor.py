import logging
import asyncio
from typing import Any, Dict
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Bestimmte Sensoren, die keine Einheit haben sollen
NO_UNIT_SENSORS = {
    "SOLAR_LAST_OFF", "HEATER_LAST_ON", "HEATER_LAST_OFF",
    "BACKWASH_LAST_ON", "BACKWASH_LAST_OFF", "PUMP_LAST_ON", "PUMP_LAST_OFF"
}

# Mapping einiger Keys zu Einheiten
UNIT_MAP = {
    "IMP1_value": "cm/s",
    "IMP2_value": "cm/s",
    "pump_rs485_pwr": "W",
    "SYSTEM_cpu_temperature": "°C",
    "SYSTEM_carrier_cpu_temperature": "°C",
    "SYSTEM_dosagemodule_cpu_temperature": "°C",
    "SYSTEM_memoryusage": "MB",
    "pH_value": "pH",
    "orp_value": "mV",
    "pot_value": "mg/l",
    "PUMP_RPM_0": "RPM",
    "PUMP_RPM_1": "RPM",
    "PUMP_RPM_2": "RPM",
    "PUMP_RPM_3": "RPM",
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "mL",
    "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": "mL",
    "ADC1_value": "bar",
    "ADC2_value": "cm",
    "ADC3_value": "m³",
    "ADC4_value": "V",
    "ADC5_value": "V",
    "ADC6_value": "V",
    "WATER_TEMPERATURE": "°C",
    "AIR_TEMPERATURE": "°C",
    "HUMIDITY": "%",
    "FILTER_PRESSURE": "bar",
    "HEATER_TEMPERATURE": "°C",
    "COVER_POSITION": "%",
    "UV_INTENSITY": "W/m²",
    "TDS": "ppm",
    "CHLORINE_LEVEL": "ppm",
    "BROMINE_LEVEL": "ppm",
    "TURBIDITY": "NTU",
}

def guess_name_from_key(key: str) -> str:
    """
    Erzeuge einen halbwegs lesbaren Namen aus dem Key.
    Beispiel: "SYSTEM_cpu_temperature" -> "System Cpu Temperature"
    """
    # Sonderfall: Versuche, underscores durch Leerzeichen zu ersetzen
    # und die Einzelteile zu kapitalisieren.
    # Man kann das beliebig anpassen (z.B. "CPU" groß lassen, etc.).
    return " ".join(part.capitalize() for part in key.split("_"))

def guess_icon_from_key(key: str) -> str:
    """
    Ordne basierend auf dem Key einen MDI-Icon zu.
    Das hier ist nur eine einfache Heuristik. 
    Du kannst nach Belieben weiter verfeinern.
    """
    klower = key.lower()

    # Ein paar Beispiel-Regeln:
    if "temp" in klower or "therm" in klower:
        return "mdi:thermometer"
    if "pump" in klower:
        return "mdi:water-pump"
    if "orp" in klower:
        return "mdi:flash"
    if "ph" in klower:
        return "mdi:flask"
    if "pressure" in klower or "adc" in klower:
        return "mdi:gauge"
    if "memory" in klower:
        return "mdi:memory"
    if "rpm" in klower:
        return "mdi:fan"
    if "version" in klower or "fw" in klower:
        return "mdi:update"
    if "last_on" in klower:
        return "mdi:timer"
    if "last_off" in klower:
        return "mdi:timer-off"
    if "onewire" in klower:
        return "mdi:thermometer"

    # Falls nichts passt, nimm ein generisches Icon.
    return "mdi:information"

class VioletDeviceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Violet Device Sensor."""

    def __init__(
        self,
        coordinator,
        key: str,
        config_entry: ConfigEntry,
        name: str | None = None,
        icon: str | None = None
    ):
        """
        :param coordinator: Dein DataUpdateCoordinator
        :param key: Der Key, wie er in coordinator.data auftaucht
        :param config_entry: Die ConfigEntry
        :param name: Anzeige-Name; wenn None, bauen wir einen aus dem key
        :param icon: MDI-Icon; wenn None, wird eines automatisch ermittelt
        """
        super().__init__(coordinator)
        self._key = key
        self._config_entry = config_entry

        # Namen und Icon automatisch generieren oder übernehmen
        if name:
            self._attr_name = name
        else:
            self._attr_name = f"Violet {guess_name_from_key(key)}"

        if icon:
            self._icon = icon
        else:
            self._icon = guess_icon_from_key(key)

        # Unique ID für HA
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{key}"

        # Ggf. Einheit
        self._unit = UNIT_MAP.get(key)

        # Vermeide mehrfaches Loggen bei None-States
        self._has_logged_none_state = False

    @property
    def native_value(self) -> Any:
        """Return the current value of this sensor."""
        value = self.coordinator.data.get(self._key)
        if value is None:
            if not self._has_logged_none_state:
                _LOGGER.warning("Sensor '%s' returned None as its state.", self._key)
                self._has_logged_none_state = True
        return value

    @property
    def icon(self) -> str:
        """Return the dynamic icon (falls du es anpassen willst)."""
        # Du könntest hier noch zusätzliche Logik machen, je nach self.native_value
        return self._icon

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return the device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get("fw", self.coordinator.data.get("SW_VERSION", "Unknown")),
            "configuration_url": f"http://{self._config_entry.data.get('host', 'Unknown IP')}/getReadings?ALL",
        }

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        if self._key in NO_UNIT_SENSORS:
            return None
        return self._unit


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Violet Device sensors from a config entry."""
    coordinator = hass.data.get(DOMAIN, {}).get(config_entry.entry_id)
    if not coordinator:
        _LOGGER.error("Unable to retrieve coordinator for Violet Pool Controller (entry_id: %s).", config_entry.entry_id)
        return

    # Wir lesen jetzt ALLE Keys aus, die in coordinator.data liegen.
    # Daraus bauen wir dynamisch Entities.
    data_keys = list(coordinator.data.keys())

    sensor_entities = []
    for key in data_keys:
        # Du könntest hier filtern, wenn gewisse Keys keinen Sensor ergeben sollen
        # if not is_relevant_sensor(key):
        #    continue

        sensor_entities.append(
            VioletDeviceSensor(
                coordinator=coordinator,
                key=key,
                config_entry=config_entry
            )
        )

    _LOGGER.debug("Erzeuge %d Sensor-Entitäten für Keys: %s", len(sensor_entities), data_keys)

    async_add_entities(sensor_entities)
