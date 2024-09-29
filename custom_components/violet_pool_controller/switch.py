import logging
import aiohttp
import asyncio
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import async_timeout

from .const import (
    DOMAIN, 
    API_SET_FUNCTION_MANUALLY
)

_LOGGER = logging.getLogger(__name__)

class VioletSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, key, name, icon):
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{self._key}"
        self.ip_address = coordinator.ip_address
        self.username = coordinator.username
        self.password = coordinator.password
        self.use_ssl = coordinator.use_ssl
        self.session = coordinator.session

        if not all([self.ip_address, self.username, self.password]):
            _LOGGER.error("Fehlende Zugangsdaten oder IP-Adresse für den VioletSwitch")
        else:
            _LOGGER.info(f"VioletSwitch für {self._key} mit IP {self.ip_address} initialisiert")

    def _get_switch_state(self):
        return self.coordinator.data.get(self._key)

    @property
    def is_on(self):
        return self._get_switch_state() == 1

    async def _send_command(self, action, duration=0):
        url = f"http://{self.username}:{self.password}@{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},{action},{duration},0"
        
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    lines = response_text.strip().split('\n')
                    if len(lines) >= 3 and lines[0] == "OK" and lines[1] == self._key and lines[2] == f"SWITCHED_TO_{action}":
                        _LOGGER.debug(f"Erfolgreich {action} Befehl an {self._key} gesendet mit Dauer {duration}")
                        await self.coordinator.async_request_refresh()
                    else:
                        _LOGGER.error(f"Unerwartete Antwort vom Server beim Senden des {action} Befehls an {self._key}: {response_text}")
        except aiohttp.ClientResponseError as resp_err:
            _LOGGER.error(f"Antwortfehler beim Senden des {action} Befehls an {self._key}: {resp_err.status} {resp_err.message}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Client-Fehler beim Senden des {action} Befehls an {self._key}: {err}")
        except asyncio.TimeoutError:
            _LOGGER.error(f"Timeout beim Senden des {action} Befehls an {self._key}")
        except Exception as err:
            _LOGGER.error(f"Unerwarteter Fehler beim Senden des {action} Befehls an {self._key}: {err}")


    async def async_turn_on(self, **kwargs):
        """Schaltet den Schalter ein."""
        await self._send_command("ON")

    async def async_turn_off(self, **kwargs):
        """Schaltet den Schalter aus."""
        await self._send_command("OFF")

    @property
    def icon(self):
        if self._key == "PUMP":
            return "mdi:water-pump" if self.is_on else "mdi:water-pump-off"
        elif self._key == "LIGHT":
            return "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb"
        elif self._key == "ECO":
            return "mdi:leaf" if self.is_on else "mdi:leaf-off"
        elif self._key in ["DOS_1_CL", "DOS_4_PHM"]:
            return "mdi:flask" if self.is_on else "mdi:flask-outline"
        return self._icon

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "violet_pool_controller")},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get('fw', 'Unbekannt'),
        }

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    verfügbare_schalter = [switch for switch in SWITCHES if switch["key"] in coordinator.data]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["name"], switch["icon"])
        for switch in verfügbare_schalter
    ]
    async_add_entities(switches)

SWITCHES = [
    {"name": "Pump Switch", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Light Switch", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Eco Mode", "key": "ECO", "icon": "mdi:leaf"},
    ##{"name": "Chlorine Dosing Switch", "key": "DOS_1_CL", "icon": "mdi:flask"},
    ##{"name": "pH-minus Dosing Switch", "key": "DOS_4_PHM", "icon": "mdi:flask"},
    {"name": "External Switch 1", "key": "EXT_1", "icon": "mdi:power-socket-eu"},
    {"name": "External Switch 2", "key": "EXT_2", "icon": "mdi:power-socket-eu"},
    {"name": "External Switch 3", "key": "EXT_3", "icon": "mdi:power-socket-eu"},
    {"name": "External Switch 4", "key": "EXT_4", "icon": "mdi:power-socket-eu"},
    {"name": "External Switch 5", "key": "EXT_5", "icon": "mdi:power-socket-eu"},
    {"name": "External Switch 6", "key": "EXT_6", "icon": "mdi:power-socket-eu"},
    {"name": "External Switch 7", "key": "EXT_7", "icon": "mdi:power-socket-eu"},
    {"name": "External Switch 8", "key": "EXT_8", "icon": "mdi:power-socket-eu"},
    {"name": "DIRULE 1", "key": "DIRULE_1", "icon": "mdi:lock-open"},
    {"name": "DIRULE 2", "key": "DIRULE_2", "icon": "mdi:lock-open"},
    {"name": "DIRULE 3", "key": "DIRULE_3", "icon": "mdi:lock-open"},
    {"name": "DIRULE 4", "key": "DIRULE_4", "icon": "mdi:lock-open"},
    {"name": "DIRULE 5", "key": "DIRULE_5", "icon": "mdi:lock-open"},
    {"name": "DIRULE 6", "key": "DIRULE_6", "icon": "mdi:lock-open"},
    {"name": "DIRULE 7", "key": "DIRULE_7", "icon": "mdi:lock-open"},
    {"name": "DMX Scene 1", "key": "DMX_SCENE1", "icon": "mdi:theater"},
    {"name": "DMX Scene 2", "key": "DMX_SCENE2", "icon": "mdi:theater"},
    {"name": "DMX Scene 3", "key": "DMX_SCENE3", "icon": "mdi:theater"},
    {"name": "DMX Scene 4", "key": "DMX_SCENE4", "icon": "mdi:theater"},
    {"name": "DMX Scene 5", "key": "DMX_SCENE5", "icon": "mdi:theater"},
    {"name": "DMX Scene 6", "key": "DMX_SCENE6", "icon": "mdi:theater"},
    {"name": "DMX Scene 7", "key": "DMX_SCENE7", "icon": "mdi:theater"},
    {"name": "DMX Scene 8", "key": "DMX_SCENE8", "icon": "mdi:theater"},
    {"name": "DMX Scene 9", "key": "DMX_SCENE9", "icon": "mdi:theater"},
    {"name": "DMX Scene 10", "key": "DMX_SCENE10", "icon": "mdi:theater"},
    {"name": "DMX Scene 11", "key": "DMX_SCENE11", "icon": "mdi:theater"},
    {"name": "DMX Scene 12", "key": "DMX_SCENE12", "icon": "mdi:theater"},
]

