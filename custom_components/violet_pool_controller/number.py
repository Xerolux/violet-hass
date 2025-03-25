"""Number Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Final

from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, 
    CONF_API_URL, 
    CONF_DEVICE_NAME,
    MANUFACTURER,
    INTEGRATION_VERSION,
)

_LOGGER = logging.getLogger(__name__)

# Sollwerte-Definitionen
SETPOINT_DEFINITIONS: Final = [
    {
        "key": "ph_setpoint",
        "name": "pH Sollwert",
        "min_value": 6.8,
        "max_value": 7.8,
        "step": 0.1,
        "icon": "mdi:flask",
        "api_key": "pH-",  # Für API-Aufrufe
        "parameter": "pH Sollwert",  # Parameter-Name in der API
        "unit_of_measurement": "pH",
    },
    {
        "key": "chlorine_setpoint",
        "name": "Redox Sollwert",
        "min_value": 600,
        "max_value": 850,
        "step": 10,
        "icon": "mdi:flash",
        "api_key": "Chlor",  # Für API-Aufrufe
        "parameter": "Redox Sollwert",  # Parameter-Name in der API
        "unit_of_measurement": "mV",
    },
    {
        "key": "min_chlorine_level",
        "name": "Min. Chlorgehalt",
        "min_value": 0.1,
        "max_value": 0.5,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "Chlor",  # Für API-Aufrufe
        "parameter": "Min. Chlorgehalt",  # Parameter-Name in der API
        "unit_of_measurement": "mg/l",
    },
    {
        "key": "max_chlorine_level_day",
        "name": "Max. Chlorgehalt Tag",
        "min_value": 0.3,
        "max_value": 0.8,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "Chlor",  # Für API-Aufrufe
        "parameter": "Max. Chlorgehalt Tag",  # Parameter-Name in der API
        "unit_of_measurement": "mg/l",
    },
    {
        "key": "max_chlorine_level_night",
        "name": "Max. Chlorgehalt Nacht",
        "min_value": 0.5,
        "max_value": 1.2,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "Chlor",  # Für API-Aufrufe
        "parameter": "Max. Chlorgehalt Nacht",  # Parameter-Name in der API
        "unit_of_measurement": "mg/l",
    },
]


class VioletNumberEntity(CoordinatorEntity, NumberEntity):
    """Repräsentiert einen Sollwert im Violet Pool Controller."""

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        definition: Dict[str, Any],
    ):
        """Initialisiere die Number-Entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._definition = definition
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        
        self._attr_name = f"{device_name} {definition['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{definition['key']}"
        self._attr_icon = definition.get("icon")
        self._attr_native_min_value = definition.get("min_value")
        self._attr_native_max_value = definition.get("max_value")
        self._attr_native_step = definition.get("step")
        self._attr_mode = NumberMode.AUTO  # oder NumberMode.SLIDER
        
        if "unit_of_measurement" in definition:
            self._attr_native_unit_of_measurement = definition["unit_of_measurement"]
        
        # Tatsächlicher Wert kommt aus der API, hier setzen wir nur einen Standard
        self._attr_native_value = self._get_current_value()
        
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": MANUFACTURER,
            "model": f"Violet Model X (v{INTEGRATION_VERSION})",
            "sw_version": coordinator.data.get("fw", INTEGRATION_VERSION),
            "configuration_url": f"http://{self.ip_address}",
        }

    def _get_current_value(self) -> Optional[float]:
        """Ermittle den aktuellen Wert aus den Coordinator-Daten."""
        # Hier muss die Logik angepasst werden, um die richtigen API-Werte zu lesen
        # Da die API nicht direkt dokumentiert, wie man Sollwerte abruft, ist dies ein Platzhalter
        # In einer vollständigen Implementierung müsste man die API-Antwort analysieren
        
        key = self._definition["key"]
        
        # Beispiel für pH-Sollwert
        if key == "ph_setpoint":
            # Suche nach einem entsprechenden Wert in den API-Daten
            return float(self.coordinator.data.get("pH_SETPOINT", 7.2))
        
        # Beispiel für Redox-Sollwert
        elif key == "chlorine_setpoint":
            return float(self.coordinator.data.get("REDOX_SETPOINT", 750))
        
        # Weitere Werte
        elif key == "min_chlorine_level":
            return float(self.coordinator.data.get("MIN_CHLORINE_LEVEL", 0.2))
        elif key == "max_chlorine_level_day":
            return float(self.coordinator.data.get("MAX_CHLORINE_LEVEL_DAY", 0.5))
        elif key == "max_chlorine_level_night":
            return float(self.coordinator.data.get("MAX_CHLORINE_LEVEL_NIGHT", 0.8))
        
        # Fallback
        return self._attr_native_min_value

    async def async_set_native_value(self, value: float) -> None:
        """Setze den neuen Wert im Gerät
