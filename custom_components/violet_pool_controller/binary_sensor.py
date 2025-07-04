"""Binary Sensor Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BINARY_SENSORS, STATE_MAP, CONF_ACTIVE_FEATURES
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_FEATURE_MAP = {
    "PUMP": "filter_control",
    "HEATER": "heating",
    "SOLAR": "solar",
    "LIGHT": "led_lighting",
    "BACKWASH": "backwash",
    "BACKWASHRINSE": "backwash",
    "DOS_1_CL": "chlorine_control",
    "DOS_4_PHM": "ph_control",
    "DOS_5_PHP": "ph_control",
    "DOS_6_FLOC": "chlorine_control",
    "COVER_OPEN": "cover_control",
    "COVER_CLOSE": "cover_control",
    "COVER_STATE": "cover_control",
    "REFILL": "water_refill",
    "PVSURPLUS": "pv_surplus",
}

@dataclass
class VioletBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Beschreibung der Violet Pool Binary Sensor-Entities."""
    feature_id: Optional[str] = None

class VioletBinarySensor(VioletPoolControllerEntity, BinarySensorEntity):
    """Repräsentation eines Violet Pool Binary Sensors."""
    entity_description: VioletBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: VioletBinarySensorEntityDescription,
    ) -> None:
        """Initialisiere den Binary Sensor.

        Args:
            coordinator: Daten-Koordinator.
            config_entry: Config Entry.
            description: Sensor-Beschreibung.
        """
        super().__init__(coordinator, config_entry, description)
        self._icon_base = description.icon
        self._has_logged_none_state = False
        _LOGGER.debug(
            "Initialisiere Binary Sensor: %s (unique_id=%s, feature_id=%s)",
            self.entity_id,
            self._attr_unique_id,
            getattr(self.entity_description, "feature_id", None)
        )

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn der Sensor eingeschaltet ist."""
        result = self._get_sensor_state()
        _LOGGER.debug("Binary Sensor %s is_on=%s", self.entity_id, result)
        return result

    @property
    def icon(self) -> str:
        """Gibt das Icon basierend auf dem Zustand zurück."""
        return f"{self._icon_base}-off" if not self.is_on else self._icon_base

    def _get_sensor_state(self) -> bool:
        """Rufe den aktuellen Sensorzustand ab."""
        key = self.entity_description.key
        raw_state = self.get_str_value(key, "")
        _LOGGER.debug("Binary Sensor %s raw_state=%s", self.entity_id, raw_state)

        if not raw_state:
            if not self._has_logged_none_state:
                self._logger.debug("Binary Sensor '%s' hat None/leeren Zustand. Standard: OFF.", key)
                self._has_logged_none_state = True
            return False

        if raw_state.upper() in STATE_MAP:
            mapped_state = STATE_MAP[raw_state.upper()]
            _LOGGER.debug("Binary Sensor %s mapped_state=%s", self.entity_id, mapped_state)
            return mapped_state

        bool_state = self.get_bool_value(key, False)
        _LOGGER.debug("Binary Sensor %s bool_state=%s", self.entity_id, bool_state)
        return bool_state

class CoverIsClosedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor für den Cover-Geschlossen-Status."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialisiere den Cover-Geschlossen-Sensor.

        Args:
            coordinator: Daten-Koordinator.
            config_entry: Config Entry.
        """
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_name = "Cover Geschlossen"
        self._attr_unique_id = f"{config_entry.entry_id}_cover_is_closed"
        self._attr_device_class = BinarySensorDeviceClass.DOOR
        self._attr_icon = "mdi:window-shutter"
        self._attr_device_info = coordinator.device.device_info
        self._logger = logging.getLogger(f"{DOMAIN}.{self._attr_unique_id}")
        self._logger.info("Initialisiere Cover-Geschlossen Sensor: %s", self._attr_unique_id)

    @property
    def available(self) -> bool:
        """Gibt an, ob die Entität verfügbar ist."""
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn die Abdeckung geschlossen ist."""
        if not self.coordinator.data:
            _LOGGER.debug("Cover-Geschlossen Sensor: Keine Daten verfügbar")
            return False

        data = self.coordinator.data
        debug_data = {
            "COVER_STATE": data.get("COVER_STATE"),
            "COVER_OPEN": data.get("COVER_OPEN"),
            "COVER_CLOSE": data.get("COVER_CLOSE"),
            "LAST_MOVING_DIRECTION": data.get("LAST_MOVING_DIRECTION")
        }
        _LOGGER.debug("Cover-Geschlossen Sensor Debug-Daten: %s", debug_data)

        cover_state = data.get("COVER_STATE")
        if cover_state in ["CLOSED", "2", 2]:
            _LOGGER.debug("Cover-Geschlossen Sensor: Status CLOSED erkannt")
            return True

        if "