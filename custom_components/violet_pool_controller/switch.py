"""Switch-Integration für den Violet Pool Controller."""
import logging
import asyncio
from datetime import timedelta
from typing import Any, Dict, Optional, Callable

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_DEVICE_NAME,
    INTEGRATION_VERSION,
    MANUFACTURER,
    SWITCHES,
    STATE_MAP,
)

_LOGGER = logging.getLogger(__name__)


class VioletSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Violet Pool Controller Switch."""

    def __init__(
        self, 
        coordinator, 
        key: str, 
        name: str, 
        icon: str, 
        config_entry: ConfigEntry,
        device_class: Optional[str] = None
    ):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self._attr_name = f"{device_name} {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{key.lower()}"
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")
        
        if device_class:
            self._attr_device_class = device_class

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": MANUFACTURER,
            "model": f"Violet Model X (v{INTEGRATION_VERSION})",
            "configuration_url": f"http://{self.ip_address}",
            "sw_version": coordinator.data.get("fw", INTEGRATION_VERSION),
        }

    def _get_switch_state(self) -> bool:
        """Get the current state of the switch from the coordinator data."""
        raw_state = self.coordinator.data.get(self._key)
        if raw_state is None:
            if not hasattr(self, "_has_logged_none_state") or not self._has_logged_none_state:
                _LOGGER.warning("Switch %s returned None as its state. Defaulting to 'OFF'.", self._key)
                self._has_logged_none_state = True
            return False
        return STATE_MAP.get(raw_state, False)

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self._get_switch_state()

    @property
    def icon(self) -> str:
        """Return the icon for the switch, changing based on state."""
        return self._icon if self.is_on else f"{self._icon}-off"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._send_command("ON")

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._send_command("OFF")

    async def async_turn_auto(self, auto_delay: int = 0):
        """Set the switch to AUTO mode."""
        await self._send_command("AUTO", auto_delay)

    async def _send_command(self, action: str, value: int = 0):
        """Send command to the device."""
        try:
            response = await self.coordinator.api.set_switch_state(
                key=self._key, 
                action=action, 
                duration=value
            )
            _LOGGER.debug("Command sent to %s: %s, Response: %s", self._key, action, response)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler bei Send_Command %s für %s: %s", action, self._key, err)


class VioletPVSurplusSwitch(VioletSwitch):
    """Special switch for PV Surplus functionality."""
    
    def __init__(self, coordinator, config_entry: ConfigEntry):
        """Initialize the PV Surplus switch."""
        super().__init__(
            coordinator=coordinator,
            key="PVSURPLUS",
            name="PV-Überschuss",
            icon="mdi:solar-power",
            config_entry=config_entry,
            device_class=SwitchDeviceClass.SWITCH
        )
        
    def _get_switch_state(self) -> bool:
        """Get the current state of the PV surplus switch."""
        state = self.coordinator.data.get(self._key)
        # PV Surplus wird im API als 0, 1 oder 2 zurückgegeben
        return state in (1, 2)
        
    async def async_turn_on(self, **kwargs):
        """Turn on PV surplus mode."""
        try:
            # Drehzahlstufe aus den Attributen holen oder Standard verwenden
            pump_speed = kwargs.get("pump_speed", 2)
            await self.coordinator.api.set_pv_surplus(True, pump_speed)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Aktivieren des PV-Überschussmodus: %s", err)

    async def async_turn_off(self, **kwargs):
        """Turn off PV surplus mode."""
        try:
            await self.coordinator.api.set_pv_surplus(False)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Deaktivieren des PV-Überschussmodus: %s", err)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
):
    """Set up Violet Pool Controller switches from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Verfügbare Switches aus der API filtern
    available_data_keys = set(coordinator.data.keys())
    available_switches = [sw for sw in SWITCHES if sw["key"] in available_data_keys]

    # Standard-Switches erstellen
    switches = [
        VioletSwitch(
            coordinator=coordinator, 
            key=sw["key"], 
            name=sw["name"], 
            icon=sw["icon"], 
            config_entry=config_entry
        ) 
        for sw in available_switches
    ]
    
    # Speziellen PV Surplus Switch hinzufügen, wenn in den Daten vorhanden
    if "PVSURPLUS" in available_data_keys:
        switches.append(VioletPVSurplusSwitch(coordinator, config_entry))

    async_add_entities(switches)

    # Services registrieren
    platform = entity_platform.async_get_current_platform()

    # Service zum Umschalten in den AUTO-Modus
    platform.async_register_entity_service(
        "turn_auto",
        {vol.Optional("auto_delay", default=0): vol.Coerce(int)},
        "async_turn_auto",
    )
    
    # Service für PV Surplus mit Pumpen-Drehzahl
    platform.async_register_entity_service(
        "set_pv_surplus",
        {vol.Optional("pump_speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3))},
        "_send_with_pump_speed",
    )
    
    # Service für manuelle Dosierung
    platform.async_register_entity_service(
        "manual_dosing",
        {vol.Required("duration_seconds"): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600))},
        "_manual_dosing",
    )
