"""Switch Integration für den Violet Pool Controller."""
import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SWITCHES, CONF_ACTIVE_FEATURES, ACTION_ON, ACTION_OFF, STATE_MAP
from .api import VioletPoolAPIError
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass
class VioletSwitchEntityDescription:
    """Beschreibung der Violet Pool Switch-Entities."""
    key: str
    name: str
    icon: str | None = None
    feature_id: str | None = None

class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Repräsentation eines Violet Pool Switches."""
    entity_description: VioletSwitchEntityDescription

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry,
        description: VioletSwitchEntityDescription
    ) -> None:
        """Initialisiere den Switch."""
        super().__init__(coordinator, config_entry, description)
        self._attr_icon = description.icon
        _LOGGER.debug("Initialisiere Switch: %s (unique_id=%s)", self.entity_id, self._attr_unique_id)

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn der Switch eingeschaltet ist."""
        return self._get_switch_state()

    def _get_switch_state(self) -> bool:
        """Rufe den aktuellen Switch-Zustand ab."""
        key = self.entity_description.key
        raw_state = self.get_str_value(key, "")
        
        if not raw_state:
            _LOGGER.debug("Switch '%s' hat leeren Zustand. Standard: OFF.", key)
            return False

        # Check state mapping first
        upper_state = raw_state.upper()
        if upper_state in STATE_MAP:
            return STATE_MAP[upper_state]
            
        # Fallback to boolean conversion
        return self.get_bool_value(key, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Schalte den Switch ein."""
        await self._set_switch_state(ACTION_ON)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Schalte den Switch aus."""
        await self._set_switch_state(ACTION_OFF)

    async def _set_switch_state(self, action: str) -> None:
        """Setze den Switch-Zustand."""
        try:
            key = self.entity_description.key
            _LOGGER.debug("Setze Switch %s auf %s", key, action)
            
            result = await self.device.api.set_switch_state(key=key, action=action)
            
            if result.get("success", True):
                _LOGGER.info("Switch %s auf %s gesetzt", key, action)
                # Update state optimistically
                if action == ACTION_ON:
                    self.coordinator.data[key] = True
                else:
                    self.coordinator.data[key] = False
                self.async_write_ha_state()
            else:
                _LOGGER.warning("Switch %s Aktion %s möglicherweise fehlgeschlagen: %s", 
                              key, action, result.get("response", result))
            
            # Request refresh to get actual state
            await self.coordinator.async_request_refresh()
            
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen von Switch %s: %s", self.entity_description.key, err)
            raise HomeAssistantError(f"Switch-Aktion fehlgeschlagen: {err}") from err

def _create_switch_descriptions() -> list[VioletSwitchEntityDescription]:
    """Create switch entity descriptions from SWITCHES constant."""
    descriptions = []
    
    for switch_config in SWITCHES:
        descriptions.append(VioletSwitchEntityDescription(
            key=switch_config["key"],
            name=switch_config["name"],
            icon=switch_config.get("icon"),
            feature_id=switch_config.get("feature_id")
        ))
    
    return descriptions

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Switches für die Config Entry ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    entities: list[SwitchEntity] = []

    # Create switch descriptions
    switch_descriptions = _create_switch_descriptions()

    for description in switch_descriptions:
        # Check if feature is active (if feature_id is specified)
        if description.feature_id and description.feature_id not in active_features:
            _LOGGER.debug("Überspringe Switch %s: Feature %s nicht aktiv", description.key, description.feature_id)
            continue
            
        # Check if data is available for this switch (optional, some switches might not have state feedback)
        # We'll create the switch anyway since it might be controllable even without state feedback
        entities.append(VioletSwitch(coordinator, config_entry, description))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("Switches eingerichtet: %s", [e.entity_id for e in entities])
    else:
        _LOGGER.info("Keine Switches eingerichtet")
