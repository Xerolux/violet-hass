"""Binary Sensor Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, 
    BINARY_SENSORS, 
    STATE_MAP,
    CONF_API_URL,
    CONF_DEVICE_NAME,
    MANUFACTURER,
    INTEGRATION_VERSION,
)

_LOGGER = logging.getLogger(__name__)


class VioletBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Violet Device Binary Sensor."""

    def __init__(
        self, 
        coordinator, 
        key: str, 
        name: str, 
        icon: str, 
        config_entry: ConfigEntry,
        device_class: Optional[str] = None
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self._attr_name = f"{device_name} {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{key}"
        
        if device_class:
            self._attr_device_class = device_class
        
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": MANUFACTURER,
            "model": f"Violet Model X (v{INTEGRATION_VERSION})",
            "sw_version": coordinator.data.get("fw", INTEGRATION_VERSION),
            "configuration_url": f"http://{self.ip_address}",
        }
        
        self._has_logged_none_state = False  # Verhindert wiederholte Logs bei None-Zustand

    def _get_sensor_state(self) -> bool:
        """Hilfsmethode zum Abrufen und Mappen des aktuellen Sensorzustands von der API."""
        state = self.coordinator.data.get(self._key, None)

        if state is None:
            if not self._has_logged_none_state:
                _LOGGER.warning(f"Sensor {self._key} returned None as its state. Defaulting to 'OFF'.")
                self._has_logged_none_state = True  # Nur einmal loggen
            return False  # Standardmäßig OFF, wenn state None ist

        # Numerischen Zustand mit STATE_MAP mappen; bei unbekannten Werten default zu False.
        return STATE_MAP.get(state, False)

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        return self._get_sensor_state()

    @property
    def icon(self) -> str:
        """Return the icon for the binary sensor, changing based on state."""
        return self._icon if self.is_on else f"{self._icon}-off"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success
        

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Violet Device binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Verfügbare Daten aus der API
    available_data_keys = set(coordinator.data.keys())

    # Erzeuge Binary Sensor Entities basierend auf der BINARY_SENSORS Liste,
    # aber nur für die tatsächlich vorhandenen Daten in der API.
    binary_sensors = []
    
    for sensor in BINARY_SENSORS:
        if sensor["key"] in available_data_keys:
            # Bestimme die richtige device_class basierend auf dem Sensor-Typ
            device_class = None
            if sensor["key"] in ["PUMP", "SOLAR", "HEATER"]:
                device_class = BinarySensorDeviceClass.RUNNING
            elif sensor["key"] == "LIGHT":
                device_class = BinarySensorDeviceClass.LIGHT
            
            binary_sensors.append(
                VioletBinarySensor(
                    coordinator=coordinator, 
                    key=sensor["key"], 
                    name=sensor["name"], 
                    icon=sensor["icon"], 
                    config_entry=config_entry,
                    device_class=device_class
                )
            )
    
    # Zusätzlich: Spezifische Sensoren basierend auf API-Daten hinzufügen
    
    # Cover Status
    if "COVER_STATE" in available_data_keys:
        binary_sensors.append(
            VioletBinarySensor(
                coordinator=coordinator, 
                key="COVER_IS_CLOSED",  # Dies ist ein spezieller Key für die Logik
                name="Cover Geschlossen", 
                icon="mdi:window-shutter", 
                config_entry=config_entry,
                device_class=BinarySensorDeviceClass.DOOR
            )
        )
    
    # PV Überschuss Status
    if "PVSURPLUS" in available_data_keys:
        binary_sensors.append(
            VioletBinarySensor(
                coordinator=coordinator, 
                key="PVSURPLUS",
                name="PV Überschuss Aktiv", 
                icon="mdi:solar-power", 
                config_entry=config_entry
            )
        )
    
    # Zur Meldung der Anzahl an hinzugefügten Sensoren    
    if binary_sensors:
        _LOGGER.info(f"{len(binary_sensors)} Binary Sensoren gefunden und hinzugefügt.")
        async_add_entities(binary_sensors)
    else:
        _LOGGER.warning("Keine passenden Binary Sensoren in den API-Daten gefunden.")
