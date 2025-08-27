"""Number Integration für den Violet Pool Controller - COMPLETE FIX."""
import logging

from homeassistant.components.number import NumberEntity, NumberDeviceClass, NumberEntityDescription
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

class VioletNumber(VioletPoolControllerEntity, NumberEntity):
    """Repräsentation einer Violet Pool Number-Entity (Sollwert)."""
    entity_description: NumberEntityDescription

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry,
        description: NumberEntityDescription, setpoint_config: dict
    ) -> None:
        """Initialisiere die Number-Entity."""
        super().__init__(coordinator, config_entry, description)
        self._attr_native_min_value = setpoint_config["min_value"]
        self._attr_native_max_value = setpoint_config["max_value"]
        self._attr_native_step = setpoint_config["step"]
        # Store additional attributes
        self._setpoint_fields = setpoint_config["setpoint_fields"]
        self._indicator_fields = setpoint_config["indicator_fields"]
        self._default_value = setpoint_config["default_value"]
        self._api_key = setpoint_config["api_key"]
        _LOGGER.debug("Initialisiere Number: %s (unique_id=%s)", self.entity_id, self._attr_unique_id)

    @property
    def native_value(self) -> float | None:
        """Gibt den aktuellen Sollwert zurück."""
        # Try to find the setpoint value in the coordinator data
        if self._setpoint_fields:
            for field in self._setpoint_fields:
                value = self.get_float_value(field)
                if value is not None:
                    return value
        
        # Fallback to default value if no setpoint found
        return self._default_value

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Check if any of the indicator fields are available
        if self._indicator_fields:
            for field in self._indicator_fields:
                if field in self.coordinator.data:
                    return super().available
        
        return super().available

    async def async_set_native_value(self, value: float) -> None:
        """Setze einen neuen Sollwert."""
        if not self._api_key:
            _LOGGER.error("Kein API-Key für %s definiert", self.entity_description.name)
            return

        try:
            _LOGGER.info("Setze %s auf %.2f %s", 
                        self.entity_description.name, value, 
                        self.entity_description.native_unit_of_measurement or "")
            
            # Use the appropriate API method based on the setpoint type
            api_key = self._api_key
            
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
                if self._setpoint_fields:
                    for field in self._setpoint_fields:
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

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Number-Entities für die Config Entry ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    entities: list[NumberEntity] = []

    for setpoint_config in SETPOINT_DEFINITIONS:
        # Check if feature is active
        if setpoint_config["feature_id"] and setpoint_config["feature_id"] not in active_features:
            _LOGGER.debug("Überspringe Number %s: Feature %s nicht aktiv", setpoint_config["key"], setpoint_config["feature_id"])
            continue
            
        # Check if any indicator fields are available (shows that this setpoint is relevant)
        if setpoint_config["indicator_fields"]:
            has_indicators = any(field in coordinator.data for field in setpoint_config["indicator_fields"])
            if not has_indicators:
                _LOGGER.debug("Überspringe Number %s: Keine Indikator-Felder verfügbar", setpoint_config["key"])
                continue
        
        # Use proper NumberEntityDescription
        description = NumberEntityDescription(
            key=setpoint_config["key"],
            name=setpoint_config["name"],
            icon=setpoint_config["icon"],
            native_unit_of_measurement=setpoint_config["unit_of_measurement"],
            device_class=setpoint_config["device_class"],
            entity_category=setpoint_config["entity_category"],
        )
            
        entities.append(VioletNumber(coordinator, config_entry, description, setpoint_config))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("Number-Entities eingerichtet: %s", [e.entity_id for e in entities])
    else:
        _LOGGER.info("Keine Number-Entities eingerichtet")