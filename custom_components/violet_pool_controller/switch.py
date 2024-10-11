import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
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
        self.session = coordinator.session
        self.timeout = coordinator.timeout if hasattr(coordinator, 'timeout') else 10  # Customizable timeout
        self.auto_reset_time = None  # Zeitpunkt des automatischen Zurücksetzens

        if not all([self.ip_address, self.username, self.password]):
            _LOGGER.error(f"Fehlende Zugangsdaten oder IP-Adresse für den Schalter {self._key}")
        else:
            _LOGGER.info(f"VioletSwitch für {self._key} mit IP {self.ip_address} initialisiert")

    def _get_switch_state(self):
        return self.coordinator.data.get(self._key)

    @property
    def is_on(self):
        return self._get_switch_state() in (1, 4)

    @property
    def is_auto(self):
        return self._get_switch_state() == 0  # Hier prüfst du, ob der Zustand "AUTO" ist

    async def _send_command(self, action, duration=0, last_value=0):
        url = f"http://{self.ip_address}{API_SET_FUNCTION_MANUALLY}?{self._key},{action},{duration},{last_value}"
        auth = aiohttp.BasicAuth(self.username, self.password)

        retry_attempts = 3  # Retry mechanism
        for attempt in range(retry_attempts):
            try:
                async with async_timeout.timeout(self.timeout):
                    async with self.session.get(url, auth=auth) as response:
                        response.raise_for_status()
                        response_text = await response.text()
                        lines = response_text.strip().split('\n')
                        if len(lines) >= 3 and lines[0] == "OK" and lines[1] == self._key and ("SWITCHED_TO" in lines[2] or "ON" in lines[2] or "OFF" in lines[2]):
                            _LOGGER.debug(f"Erfolgreich {action} Befehl an {self._key} gesendet mit Dauer {duration} und letztem Wert {last_value}")
                            await self.coordinator.async_request_refresh()
                            return
                        elif len(lines) >= 3 and lines[0] == "OK" and lines[1] == self._key and ("SWITCHED_TO" in lines[2] or "ON" in lines[2] or "OFF" in lines[2]) and "PERMANENTLY" in lines[2]:
                            _LOGGER.debug(f"Erfolgreich {action} Befehl an {self._key} gesendet (dauerhaft) mit Dauer {duration} und letztem Wert {last_value}")
                            await self.coordinator.async_request_refresh()
                            return
                        else:
                            _LOGGER.error(f"Unerwartete Antwort vom Server beim Senden des {action} Befehls an {self._key}: {response_text}")
            except aiohttp.ClientResponseError as resp_err:
                _LOGGER.error(f"Antwortfehler beim Senden des {action} Befehls an {self._key}: {resp_err.status} {resp_err.message}")
            except aiohttp.ClientError as err:
                _LOGGER.error(f"Client-Fehler beim Senden des {action} Befehls an {self._key}: {err}")
            except asyncio.TimeoutError:
                _LOGGER.error(f"Timeout beim Senden des {action} Befehls an {self._key}, Versuch {attempt + 1} von {retry_attempts}")
            except Exception as err:
                _LOGGER.error(f"Unerwarteter Fehler beim Senden des {action} Befehls an {self._key}: {err}")

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug(f"async_turn_on aufgerufen für {self._key} mit Argumenten: {kwargs}")
        duration = kwargs.get("duration", 0)
        last_value = kwargs.get("last_value", 0)  # Standardwert 0
        await self._send_command("ON", duration, last_value)
        # Automatisches Zurücksetzen zu AUTO nach Ablauf der Dauer
        auto_delay = kwargs.get("auto_delay", 0)
        if auto_delay > 0:
            self.auto_reset_time = datetime.now() + timedelta(seconds=auto_delay)
            _LOGGER.debug(f"Automatisches Zurücksetzen zu AUTO nach {auto_delay} Sekunden für {self._key}")
            await asyncio.sleep(auto_delay)
            await self.async_turn_auto()

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug(f"async_turn_off aufgerufen für {self._key} mit Argumenten: {kwargs}")
        last_value = kwargs.get("last_value", 0)  # Standardwert 0
        await self._send_command("OFF", 0, last_value)

    async def async_turn_auto(self, **kwargs):
        _LOGGER.debug(f"async_turn_auto aufgerufen für {self._key} mit Argumenten: {kwargs}")
        auto_delay = kwargs.get("auto_delay", 0)  # Zeit in Sekunden bis zum AUTO-Rücksetzen
        last_value = kwargs.get("last_value", 0)  # Standardwert 0
        await self._send_command("AUTO", auto_delay, last_value)
        self.auto_reset_time = None  # Reset der automatischen Rücksetzungszeit

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
        elif "EXT" in self._key:
            return "mdi:power-socket" if self.is_on else "mdi:power-socket-off"
        return self._icon

    @property
    def extra_state_attributes(self):
        attributes = super().extra_state_attributes or {}
        # Zusätzliche visuelle Hinweise hinzufügen
        attributes['status_detail'] = "AUTO" if self.is_auto else "MANUAL"
        attributes['duration_remaining'] = self._get_switch_state() if not self.is_auto else "N/A"
        if self.auto_reset_time:
            remaining_time = (self.auto_reset_time - datetime.now()).total_seconds()
            attributes['auto_reset_in'] = max(0, remaining_time)
        else:
            attributes['auto_reset_in'] = "N/A"
        return attributes

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "violet_pool_controller")},
            "name": "Violet Pool Controller",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",
            "sw_version": self.coordinator.data.get('fw') or self.coordinator.data.get('SW_VERSION', 'Unbekannt'),
        }

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    available_switches = [switch for switch in SWITCHES if switch["key"] in coordinator.data]
    switches = [
        VioletSwitch(coordinator, switch["key"], switch["name"], switch["icon"])
        for switch in available_switches
    ]
    async_add_entities(switches)

SWITCHES = [
    {"name": "Pump Switch", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Light Switch", "key": "LIGHT", "icon": "mdi:lightbulb"},
]