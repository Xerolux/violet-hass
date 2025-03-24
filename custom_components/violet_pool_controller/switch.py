import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.cover import CoverEntity, CoverDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_DEVICE_NAME,
)

_LOGGER = logging.getLogger(__name__)

STATE_MAP = {
    0: False,  # AUTO (not on)
    1: True,   # AUTO (on)
    2: False,  # OFF by control rule
    3: True,   # ON by emergency rule
    4: True,   # MANUAL ON
    5: False,  # OFF by emergency rule
    6: False,  # MANUAL OFF
}

SWITCHES = [
    {"name": "Pumpe", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Absorber", "key": "SOLAR", "icon": "mdi:solar-power"},
    {"name": "Heizung", "key": "HEATER", "icon": "mdi:radiator"},
    {"name": "Licht", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Dosierung Chlor", "key": "DOS_1_CL", "icon": "mdi:flask"},
    {"name": "Dosierung pH-", "key": "DOS_4_PHM", "icon": "mdi:flask"},
    {"name": "Eco-Modus", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "Rückspülung", "key": "BACKWASH", "icon": "mdi:valve"},
    {"name": "Nachspülung", "key": "BACKWASHRINSE", "icon": "mdi:water-sync"},
    {"name": "Dosierung pH+", "key": "DOS_5_PHP", "icon": "mdi:flask"},
    {"name": "Flockmittel", "key": "DOS_6_FLOC", "icon": "mdi:flask"},
]

class VioletSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, key, name, icon, config_entry):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self._attr_name = f"{device_name} {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{key.lower()}"
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "configuration_url": f"http://{self.ip_address}",
        }

    def _get_switch_state(self):
        return self.coordinator.data.get(self._key)

    @property
    def is_on(self):
        raw_state = self._get_switch_state()
        return STATE_MAP.get(raw_state, False)

    async def async_turn_on(self, **kwargs):
        await self._send_command("ON")

    async def async_turn_off(self, **kwargs):
        await self._send_command("OFF")

    async def async_turn_auto(self, auto_delay=0):
        await self._send_command("AUTO")

    async def _send_command(self, action):
        try:
            await self.coordinator.api.set_switch_state(key=self._key, action=action)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler bei Send_Command %s für %s: %s", action, self._key, err)

class VioletCoverSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._attr_name = f"{config_entry.data.get(CONF_DEVICE_NAME, 'Violet Pool Controller')} Cover"
        self._attr_unique_id = f"{config_entry.entry_id}_cover_state"
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{config_entry.data.get(CONF_DEVICE_NAME)} ({self.ip_address})",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "configuration_url": f"http://{self.ip_address}",
        }

    @property
    def is_on(self):
        return self.coordinator.data.get("COVER_STATE") == "OPEN"

    @property
    def icon(self):
        return "mdi:window-shutter-open" if self.is_on else "mdi:window-shutter"

class VioletCover(CoordinatorEntity, CoverEntity):
    _attr_device_class = CoverDeviceClass.SHUTTER

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._config_entry = config_entry
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self._attr_name = f"{device_name} Cover"
        self._attr_unique_id = f"{config_entry.entry_id}_cover"
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "configuration_url": f"http://{self.ip_address}",
        }

    @property
    def is_closed(self):
        state = self.coordinator.data.get("COVER_STATE")
        return state == "CLOSED"

    async def async_open_cover(self, **kwargs):
        await self._send_cover_command("OPEN")

    async def async_close_cover(self, **kwargs):
        await self._send_cover_command("CLOSE")

    async def async_stop_cover(self, **kwargs):
        await self._send_cover_command("STOP")

    async def _send_cover_command(self, action):
        try:
            await self.coordinator.api.set_cover_state(action=action)
            await self.coordinator.async_request_refresh()
            _LOGGER.debug("Cover-Befehl gesendet: %s", action)
        except Exception as err:
            _LOGGER.error("Fehler bei Cover-Befehl %s: %s", action, err)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    available_switches = [sw for sw in SWITCHES if sw["key"] in coordinator.data]

    switches = [VioletSwitch(coordinator, sw["key"], sw["name"], sw["icon"], config_entry) for sw in available_switches]

    async_add_entities(switches)

    if "COVER_STATE" in coordinator.data:
        async_add_entities([
            VioletCoverSensor(coordinator, config_entry),
            VioletCover(coordinator, config_entry)
        ])

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "turn_auto",
        {vol.Optional("auto_delay", default=0): vol.Coerce(int)},
        "async_turn_auto",
    )
