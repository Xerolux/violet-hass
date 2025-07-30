"""Number Integration für den Violet Pool Controller."""
import logging
from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberMode, NumberDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_ACTIVE_FEATURES, SETPOINT_DEFINITIONS
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
    api_key: str | None = None
    api_endpoint: str | None = None
    parameter: str | None = None
    feature_id: str | None = None
    dosing_type: str | None = None
    unit_of_measurement: str | None = None
    device_class: NumberDeviceClass | None = None
    entity_category: EntityCategory | None = None
    setpoint_fields: list[str] = None
    indicator_fields: list[str] = None
    default_value: float = 0.0

class VioletNumberEntity(VioletPoolControllerEntity, NumberEntity):
    """Repräsentiert einen Sollwert."""
    entity_description: VioletNumberEntityDescription

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry, definition: dict) -> None:
        """Initialisiere Number-Entity."""
        description = VioletNumberEntityDescription(**definition)
        super().__init__(coordinator, config_entry, description)
        self._definition = definition
        self._attr_native_min_value = definition["min_value"]
        self._attr_native_max_value = definition["max_value"]
        self._attr_native_step = definition["step"]
        self._attr_mode = NumberMode.AUTO
        self._attr_native_value = self._get_current_value()
        _LOGGER.debug("Number-Entity %s initialisiert: %s %s", definition["name"], self._attr_native_value, description.unit_of_measurement or "")

    def _get_current_value(self) -> float:
        """Ermittle aktuellen Wert."""
        for field in self._definition.get("setpoint_fields", []):
            if value := self.get_float_value(field, None):
                return value
        default = self._definition.get("default_value", self._attr_native_min_value)
        _LOGGER.debug("Standardwert für %s: %s", self.name, default)
        return default

    async def async_set_native_value(self, value: float) -> None:
        """Setze neuen Wert."""
        api_key = self.entity_description.api_key or self.entity_description.key
        endpoint = self.entity_description.api_endpoint
        if not api_key or not endpoint:
            _LOGGER.error("API-Key oder Endpunkt fehlt für %s", self.entity_id)
            return

        # Round value to step precision
        if self._attr_native_step > 0:
            value = round(value / self._attr_native_step) * self._attr_native_step
            if isinstance(self._attr_native_step, float):
                value = round(value, len(str(self._attr_native_step).split(".")[1]))

        _LOGGER.info("Setze %s (%s) auf %s %s", self.name, api_key, value, self.entity_description.unit_of_measurement or "")
        try:
            if endpoint == "/set_target_value":
                result = await self.device.api.set_target_value(api_key, value)
            elif endpoint == "/set_dosing_parameters":
                if not self.entity_description.dosing_type:
                    _LOGGER.error("Dosing_type fehlt für %s", self.entity_id)
                    return
                result = await self.device.api.set_dosing_parameters(self.entity_description.dosing_type, api_key, value)
            else:
                _LOGGER.error("Ungültiger Endpunkt %s für %s", endpoint, self.entity_id)
                return

            if result.get("success", True):
                self._attr_native_value = value
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                raise HomeAssistantError(f"Wert setzen fehlgeschlagen: {result.get('response', result)}")
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen von %s: %s", self.name, err)
            raise HomeAssistantError(f"Wert setzen fehlgeschlagen: {err}") from err

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Richte Number-Entities ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    entities = []

    for definition in SETPOINT_DEFINITIONS:
        if definition.get("feature_id") not in active_features:
            _LOGGER.debug("Überspringe %s: Feature %s inaktiv", definition["name"], definition.get("feature_id"))
            continue
        if not any(field in coordinator.data for field in definition.get("indicator_fields", [])):
            _LOGGER.debug("Überspringe %s: Keine Indikator-Daten", definition["name"])
            continue
        entities.append(VioletNumberEntity(coordinator, config_entry, definition))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("%d Number-Entities hinzugefügt", len(entities))
    else:
        _LOGGER.info("Keine Number-Entities hinzugefügt")
