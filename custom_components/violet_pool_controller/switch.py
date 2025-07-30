"""Switch-Integration für den Violet Pool Controller."""
import logging
from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SWITCHES, STATE_MAP, CONF_ACTIVE_FEATURES
from .api import ACTION_ON, ACTION_OFF, ACTION_AUTO, VioletPoolAPIError
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass
class VioletSwitchEntityDescription:
    """Beschreibt Switch-Entitäten."""
    key: str
    name: str
    icon: str | None = None
    feature_id: str | None = None
    entity_category: EntityCategory | None = None

class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Repräsentation eines Switches."""
    entity_description: VioletSwitchEntityDescription

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry, description: VioletSwitchEntityDescription) -> None:
        """Initialisiert den Switch."""
        super().__init__(coordinator, config_entry, description)
        self._attr_icon = description.icon

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn der Switch eingeschaltet ist."""
        state = self.get_str_value(self.entity_description.key, "").upper()
        if not state:
            _LOGGER.debug_once("Switch %s hat leeren Status. Standard: OFF", self.entity_description.key)
            return False
        return STATE_MAP.get(state, False)

    async def async_turn_on(self, **kwargs) -> None:
        """Schaltet den Switch ein."""
        await self._send_command(ACTION_ON)

    async def async_turn_off(self, **kwargs) -> None:
        """Schaltet den Switch aus."""
        await self._send_command(ACTION_OFF)

    async def async_turn_auto(self, auto_delay: int = 0) -> None:
        """Setzt AUTO-Modus."""
        await self._send_command(ACTION_AUTO, auto_delay)

    async def _send_command(self, api_action: str, duration: int = 0) -> None:
        """Sendet Befehl an Gerät."""
        key = self.entity_description.key
        try:
            result = await self.device.api.set_switch_state(key, api_action, duration)
            if result.get("success", True):
                _LOGGER.debug("Befehl %s für %s gesendet", api_action, key)
            else:
                _LOGGER.warning("Befehl %s für %s möglicherweise fehlgeschlagen: %s", api_action, key, result.get("response", result))
            await self.coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler bei %s für %s: %s", api_action, key, err)
            raise HomeAssistantError(f"Aktion {api_action} für {key} fehlgeschlagen: {err}") from err

class VioletPVSurplusSwitch(VioletSwitch):
    """Spezial-Switch für PV-Überschuss."""

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry) -> None:
        """Initialisiert PV-Überschuss-Switch."""
        description = VioletSwitchEntityDescription(
            key="PVSURPLUS", name="PV-Überschuss", icon="mdi:solar-power",
            feature_id="pv_surplus", device_class=SwitchDeviceClass.SWITCH
        )
        super().__init__(coordinator, config_entry, description)

    def _get_switch_state(self) -> bool:
        """Ruft PV-Überschuss-Status ab."""
        return self.get_int_value(self.entity_description.key, 0) in (1, 2)

    async def async_turn_on(self, **kwargs) -> None:
        """Aktiviert PV-Überschuss."""
        try:
            await self.device.api.set_pv_surplus(active=True, pump_speed=kwargs.get("pump_speed", 2))
            await self.coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Einschalten von PV-Überschuss: %s", err)
            raise HomeAssistantError(f"PV-Überschuss einschalten fehlgeschlagen: {err}") from err

    async def async_turn_off(self, **kwargs) -> None:
        """Deaktiviert PV-Überschuss."""
        try:
            await self.device.api.set_pv_surplus(active=False)
            await self.coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Ausschalten von PV-Überschuss: %s", err)
            raise HomeAssistantError(f"PV-Überschuss ausschalten fehlgeschlagen: {err}") from err

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Richtet Switches ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    switches = []

    for sw in SWITCHES:
        if sw["key"] not in coordinator.data or (sw.get("feature_id") and sw["feature_id"] not in active_features):
            continue
        switches.append(VioletSwitch(coordinator, config_entry, VioletSwitchEntityDescription(
            key=sw["key"], name=sw["name"], icon=sw["icon"],
            feature_id=sw.get("feature_id"), entity_category=EntityCategory.CONFIG if sw["key"].startswith("DOS_") else None
        )))

    if "pv_surplus" in active_features and "PVSURPLUS" in coordinator.data:
        switches.append(VioletPVSurplusSwitch(coordinator, config_entry))

    if switches:
        async_add_entities(switches)
        _LOGGER.info("%d Switches hinzugefügt", len(switches))
    else:
        _LOGGER.info("Keine Switches hinzugefügt")
