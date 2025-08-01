"""Binary Sensor Integration für den Violet Pool Controller."""
import logging
from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
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
class VioletBinarySensorEntityDescription:
    """Beschreibung der Violet Pool Binary Sensor-Entities."""
    key: str
    name: str
    device_class: BinarySensorDeviceClass | None = None
    icon: str | None = None
    entity_category: EntityCategory | None = None
    feature_id: str | None = None

class VioletBinarySensor(VioletPoolControllerEntity, BinarySensorEntity):
    """Repräsentation eines Violet Pool Binary Sensors."""
    entity_description: VioletBinarySensorEntityDescription

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry,
        description: VioletBinarySensorEntityDescription
    ) -> None:
        """Initialisiere den Binary Sensor."""
        super().__init__(coordinator, config_entry, description)
        self._attr_icon = description.icon
        _LOGGER.debug("Initialisiere Binary Sensor: %s (unique_id=%s)", self.entity_id, self._attr_unique_id)

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn der Sensor eingeschaltet ist."""
        state = self._get_sensor_state()
        _LOGGER.debug("Binary Sensor %s is_on=%s", self.entity_id, state)
        return state

    @property
    def icon(self) -> str | None:
        """Gibt das Icon basierend auf dem Zustand zurück."""
        return f"{self._attr_icon}-off" if not self.is_on and self._attr_icon else self._attr_icon

    def _get_sensor_state(self) -> bool:
        """Rufe den aktuellen Sensorzustand ab."""
        key = self.entity_description.key
        raw_state = self.get_str_value(key, "")
        if not raw_state:
            _LOGGER.debug_once("Binary Sensor '%s' hat leeren Zustand. Standard: OFF.", key)
            return False

        if raw_state.upper() in STATE_MAP:
            return STATE_MAP[raw_state.upper()]
        return self.get_bool_value(key, False)

class CoverIsClosedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor für den Cover-Geschlossen-Status."""

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry) -> None:
        """Initialisiere den Cover-Geschlossen-Sensor."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_name = "Cover Geschlossen"
        self._attr_unique_id = f"{config_entry.entry_id}_cover_is_closed"
        self._attr_device_class = BinarySensorDeviceClass.DOOR
        self._attr_icon = "mdi:window-shutter"
        self._attr_device_info = coordinator.device.device_info
        _LOGGER.info("Initialisiere Cover-Geschlossen Sensor: %s", self._attr_unique_id)

    @property
    def available(self) -> bool:
        """Gibt an, ob die Entität verfügbar ist."""
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn die Abdeckung geschlossen ist."""
        if not self.coordinator.data:
            _LOGGER.debug("Cover-Geschlossen Sensor: Keine Daten")
            return False

        cover_state = self.coordinator.data.get("COVER_STATE")
        _LOGGER.debug("Cover-Geschlossen Sensor: COVER_STATE=%s", cover_state)
        return cover_state in ("CLOSED", "2", 2)

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Binary Sensors für die Config Entry ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    entities: list[BinarySensorEntity] = []

    for description in BINARY_SENSORS:
        feature_id = BINARY_SENSOR_FEATURE_MAP.get(description.key)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug("Überspringe Binary Sensor %s: Feature %s nicht aktiv", description.key, feature_id)
            continue
        entities.append(VioletBinarySensor(coordinator, config_entry, description))

    if "cover_control" in active_features:
        entities.append(CoverIsClosedBinarySensor(coordinator, config_entry))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("Binary Sensors eingerichtet: %s", [e.entity_id for e in entities])
    else:
        _LOGGER.info("Keine Binary Sensors eingerichtet")
