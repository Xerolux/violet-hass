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
)
from .api import (
    ACTION_ON, ACTION_OFF, ACTION_AUTO,
    VioletPoolAPIError, VioletPoolConnectionError, VioletPoolCommandError
)
from homeassistant.exceptions import HomeAssistantError
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
        await self._send_command(ACTION_ON)

    async def async_turn_off(self, **kwargs) -> None:
        """Schaltet den Switch aus."""
        await self._send_command(ACTION_OFF)

    async def async_turn_auto(self, auto_delay: int = 0) -> None:
        """Setzt den Switch in den AUTO-Modus."""
        # This method provides 'AUTO' functionality. For HA UI interaction, a custom service may need to be defined.
        await self._send_command(ACTION_AUTO, auto_delay)

    async def _send_command(self, api_action: str, value: int = 0) -> None:
        """Sendet einen Befehl an das Gerät über die VioletPoolAPI."""
        try:
            key = self.entity_description.key
            # action_map = {
            #     "ON": ACTION_ON,
            #     "OFF": ACTION_OFF,
            #     "AUTO": ACTION_AUTO,
            # }
            # api_action = action_map.get(action_str.upper())
            # if api_action is None:
            #     _LOGGER.error(f"Unbekannte Aktion '{action_str}' für Switch {key}")
            #     return

            # The 'value' parameter from _send_command is used as 'duration' in set_switch_state
            # last_value defaults to 0 as per original command_str format
            result = await self.device.api.set_switch_state(
                key=key,
                action=api_action,
                duration=value,
                last_value=0
            )
            _LOGGER.debug(f"Befehl an {key} gesendet: action={api_action}, duration={value}, Antwort: {result}")
            await self.coordinator.async_request_refresh()
        except (VioletPoolConnectionError, VioletPoolCommandError) as err:
            _LOGGER.error(f"API-Fehler beim Senden von {api_action} für {key}: {err}")
            raise HomeAssistantError(f"Aktion '{api_action}' für Switch {key} fehlgeschlagen: {err}") from err
        except Exception as err: # Catch any other unexpected errors
            _LOGGER.exception(f"Unerwarteter Fehler beim Senden von {api_action} für {key}: {err}")
            raise HomeAssistantError(f"Unerwarteter Fehler bei Aktion '{api_action}' für Switch {key}: {err}") from err

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
        return state in (1, 2) # 1=ON, 2=ON (variable speed), 0=OFF

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Aktiviert den PV-Überschussmodus."""
        pump_speed = kwargs.get("pump_speed", 2) # Default to speed 2 if not provided
        try:
            await self.device.api.set_pv_surplus(active=True, pump_speed=pump_speed)
            await self.coordinator.async_request_refresh()
        except (VioletPoolConnectionError, VioletPoolCommandError) as err:
            _LOGGER.error(f"API-Fehler beim Einschalten des PV-Überschuss: {err}")
            raise HomeAssistantError(f"PV-Überschuss einschalten fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.exception(f"Unerwarteter Fehler beim Einschalten des PV-Überschuss: {err}")
            raise HomeAssistantError(f"Unerwarteter Fehler beim Einschalten des PV-Überschuss: {err}") from err

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Deaktiviert den PV-Überschussmodus."""
        try:
            await self.device.api.set_pv_surplus(active=False)
            await self.coordinator.async_request_refresh()
        except (VioletPoolConnectionError, VioletPoolCommandError) as err:
            _LOGGER.error(f"API-Fehler beim Ausschalten des PV-Überschuss: {err}")
            raise HomeAssistantError(f"PV-Überschuss ausschalten fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.exception(f"Unerwarteter Fehler beim Ausschalten des PV-Überschuss: {err}")
            raise HomeAssistantError(f"Unerwarteter Fehler beim Ausschalten des PV-Überschuss: {err}") from err

    # _send_command is inherited from VioletSwitch but not used by VioletPVSurplusSwitch directly
    # if overrides are removed. If it's not needed at all, it can be removed or VioletPVSurplusSwitch
    # might not need to inherit _send_command if all its actions are custom.
    # For now, we assume it's okay to have it inherited. The direct calls to self.device.api are preferred.

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