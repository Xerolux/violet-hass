"""Number Integration für den Violet Pool Controller."""
import logging
from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SETPOINT_DEFINITIONS, CONF_ACTIVE_FEATURES
from .api import VioletPoolAPIError
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass
class VioletNumberEntityDescription:
    """Beschreibung der Violet Pool Number-Entities."""
    key: str
    name: str
    min_value: float
    max_value: float
    step: float
    icon: str | None = None
    unit_of_measurement: str | None = None
    device_class: NumberDeviceClass | None = None
    entity_category: EntityCategory | None = None
    feature_id: str | None = None
    api_key: str | None = None
    setpoint_fields: list[str] | None = None
    indicator_fields: list[str] | None = None
    default_value: float | None = None

class VioletNumber(VioletPoolControllerEntity, NumberEntity):
    """Repräsentation einer Violet Pool Number-Entity (Sollwert)."""
    entity_description: VioletNumberEntityDescription

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry,
        description: VioletNumberEntityDescription
    ) -> None:
        """Initialisiere die Number-Entity."""
        super().__init__(coordinator, config_entry, description)
        self._attr_icon = description.icon
        self._attr_native_min_value = description.min_value
        self._attr_native_max_value = description.max_value
        self._attr_native_step = description.step
        self._attr_native_unit_of_measurement = description.unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_entity_category = description.entity_category
        _LOGGER.debug("Initialisiere Number: %s (unique_id=%s)", self.entity_id, self._attr_unique_id)

    @property
    def native_value(self) -> float | None:
        """Gibt den aktuellen Sollwert zurück."""
        # Try to find the setpoint value in the coordinator data
        if self.entity_description.setpoint_fields:
            for field in self.entity_description.setpoint_fields:
                value = self.get_float_value(field)
                if value is not None:
                    return value
        
        # Fallback to default value if no setpoint found
        return self.entity_description.default_value

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Check if any of the indicator fields are available
        if self.entity_description.indicator_fields:
            for field in self.entity_description.indicator_fields:
                if field in self.coordinator.data:
                    return super().available
        
        return super().available

    async def async_set_native_value(self, value: float) -> None:
        """Setze einen neuen Sollwert."""
        if not self.entity_description.api_key:
            _LOGGER.error("Kein API-Key für %s definiert", self.entity_description.name)
            return

        try:
            _LOGGER.info("Setze %s auf %.2f %s", 
                        self.entity_description.name, value, 
                        self.entity_description.unit_of_measurement or "")
            
            # Use the appropriate API method based on the setpoint type
            api_key = self.entity_description.api_key
            
            if api_key == "pH":
                result = await self.device.api.set_ph_target(value)
            elif api_key == "ORP":
                result = await self.device.api.set_orp_target(int(value))
            elif api_key == "MinChlorine":
                result = await self.device.api.set_min_chlorine_level(value)
            else:
                result = await self.device.api.set_target_value(api_key, value)
            
            if result.get("success", True):
                _LOGGER.info("%s erfolgreich auf %.2f gesetzt", self.entity_description.name, value)
                
                # Optimistically update the value in coordinator data
                if self.entity_description.setpoint_fields:
                    for field in self.entity_description.setpoint_fields:
                        self.coordinator.data[field] = value
                
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.warning("%s setzen möglicherweise fehlgeschlagen: %s", 
                              self.entity_description.name, result.get("response", result))
                raise HomeAssistantError(f"Sollwert setzen fehlgeschlagen: {result.get('response', result)}")
                
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen von %s: %s", self.entity_description.name, err)
            raise HomeAssistantError(f"Sollwert setzen fehlgeschlagen: {err}") from err

def _create_number_descriptions() -> list[VioletNumberEntityDescription]:
    """Create number entity descriptions from SETPOINT_DEFINITIONS constant."""
    descriptions = []
    
    for setpoint_config in SETPOINT_DEFINITIONS:
        descriptions.append(VioletNumberEntityDescription(
            key=setpoint_config["key"],
            name=setpoint_config["name"],
            min_value=setpoint_config["min_value"],
            max_value=setpoint_config["max_value"],
            step=setpoint_config["step"],
            icon=setpoint_config["icon"],
            api_key=setpoint_config["api_key"],
            feature_id=setpoint_config["feature_id"],
            unit_of_measurement=setpoint_config["unit_of_measurement"],
            device_class=setpoint_config["device_class"],
            entity_category=setpoint_config["entity_category"],
            setpoint_fields=setpoint_config["setpoint_fields"],
            indicator_fields=setpoint_config["indicator_fields"],
            default_value=setpoint_config["default_value"]
        ))
    
    return descriptions

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Number-Entities für die Config Entry ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    entities: list[NumberEntity] = []

    # Create number descriptions
    number_descriptions = _create_number_descriptions()

    for description in number_descriptions:
        # Check if feature is active
        if description.feature_id and description.feature_id not in active_features:
            _LOGGER.debug("Überspringe Number %s: Feature %s nicht aktiv", description.key, description.feature_id)
            continue
            
        # Check if any indicator fields are available (shows that this setpoint is relevant)
        if description.indicator_fields:
            has_indicators = any(field in coordinator.data for field in description.indicator_fields)
            if not has_indicators:
                _LOGGER.debug("Überspringe Number %s: Keine Indikator-Felder verfügbar", description.key)
                continue
            
        entities.append(VioletNumber(coordinator, config_entry, description))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("Number-Entities eingerichtet: %s", [e.entity_id for e in entities])
    else:
        _LOGGER.info("Keine Number-Entities eingerichtet")
