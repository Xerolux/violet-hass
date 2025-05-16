"""Switch-Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, List
from dataclasses import dataclass

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN,
    SWITCHES,
    STATE_MAP,
    DOSING_FUNCTIONS,
    CONF_ACTIVE_FEATURES,
    API_SET_FUNCTION_MANUALLY,
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass
class VioletSwitchEntityDescription(SwitchEntityDescription):
    """Beschreibt die Violet Pool Switch-Entitäten."""
    feature_id: Optional[str] = None

class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Repräsentation eines Violet Pool Controller Switches."""
    entity_description: VioletSwitchEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: VioletSwitchEntityDescription,
    ):
        """Initialisiert den Switch."""
        super().__init__(coordinator, config_entry, description)
        self._icon_base = description.icon
        self._has_logged_none_state = False

    @property
    def icon(self) -> str:
        """Gibt das Icon basierend auf dem Status zurück."""
        return f"{self._icon_base}-off" if not self.is_on else self._icon_base

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn der Switch eingeschaltet ist."""
        return self._get_switch_state()

    def _get_switch_state(self) -> bool:
        """Ruft den aktuellen Status des Switches ab."""
        raw_state = self.get_str_value(self.entity_description.key, "")
        if not raw_state:
            if not self._has_logged_none_state:
                _LOGGER.warning(f"Switch {self.entity_description.key} hat leeren Status. Standard: OFF.")
                self._has_logged_none_state = True
            return False
        return STATE_MAP.get(raw_state.upper(), False)

    async def async_turn_on(self, **kwargs) -> None:
        """Schaltet den Switch ein."""
        await self._send_command("ON")

    async def async_turn_off(self, **kwargs) -> None:
        """Schaltet den Switch aus."""
        await self._send_command("OFF")

    async def async_turn_auto(self, auto_delay: int = 0) -> None:
        """Setzt den Switch in den AUTO-Modus."""
        await self._send_command("AUTO", auto_delay)

    async def _send_command(self, action: str, value: int = 0) -> None:
        """Sendet einen Befehl an das Gerät im ursprünglichen Format."""
        try:
            key = self.entity_description.key
            command_str = f"{key},{action},{value},0"
            result = await self.device.async_send_command(
                endpoint=API_SET_FUNCTION_MANUALLY,
                command=command_str
            )
            _LOGGER.debug(f"Befehl an {key} gesendet: {command_str}, Antwort: {result}")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Fehler beim Senden von {action} für {key}: {err}")

class VioletPVSurplusSwitch(VioletSwitch):
    """Spezial-Switch für PV-Überschuss-Funktionalität."""

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry):
        description = VioletSwitchEntityDescription(
            key="PVSURPLUS",
            name="PV-Überschuss",
            icon="mdi:solar-power",
            device_class=SwitchDeviceClass.SWITCH,
            feature_id="pv_surplus",
        )
        super().__init__(coordinator, config_entry, description)

    def _get_switch_state(self) -> bool:
        """Ruft den aktuellen Status des PV-Überschuss-Switches ab."""
        state = self.get_int_value(self.entity_description.key, 0)
        return state in (1, 2)

    async def async_turn_on(self, **kwargs) -> None:
        """Aktiviert den PV-Überschussmodus."""
        pump_speed = kwargs.get("pump_speed", 2)
        await self._send_command("ON", pump_speed)

    async def async_turn_off(self, **kwargs) -> None:
        """Deaktiviert den PV-Überschussmodus."""
        await self._send_command("OFF")

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richtet die Switches basierend auf der Config-Entry ein."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    available_data_keys = set(coordinator.data.keys())
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    switches: List[VioletSwitch] = []

    for sw in SWITCHES:
        key = sw["key"]
        if key not in available_data_keys:
            continue
        feature_id = sw.get("feature_id")
        if feature_id and feature_id not in active_features:
            continue
        entity_category = EntityCategory.CONFIG if key.startswith("DOS_") else None
        description = VioletSwitchEntityDescription(
            key=key,
            name=sw["name"],
            icon=sw["icon"],
            feature_id=feature_id,
            entity_category=entity_category,
        )
        switches.append(VioletSwitch(coordinator, config_entry, description))

    if "pv_surplus" in active_features and "PVSURPLUS" in available_data_keys:
        switches.append(VioletPVSurplusSwitch(coordinator, config_entry))

    if switches:
        async_add_entities(switches)
    else:
        _LOGGER.info("Keine Switches gefunden oder keine aktiven Switch-Features konfiguriert.")