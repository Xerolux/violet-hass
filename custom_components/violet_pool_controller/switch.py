import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
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
# Wichtig: Nur falls du in diesem Modul direkt API-Strings brauchst.
# Falls du hier "API_SET_FUNCTION_MANUALLY" usw. nicht nutzt, musst du es nicht importieren.

_LOGGER = logging.getLogger(__name__)

# Map the API numeric values to ON (True) or OFF (False) states
STATE_MAP = {
    0: False,  # AUTO (not on)
    1: True,   # AUTO (on)
    2: False,  # OFF by control rule
    3: True,   # ON by emergency rule
    4: True,   # MANUAL ON
    5: False,  # OFF by emergency rule
    6: False,  # MANUAL OFF
}

# Liste möglicher Switches (Beispiel)
SWITCHES = [
    {"name": "Pump", "key": "PUMP", "icon": "mdi:water-pump"},
    {"name": "Light", "key": "LIGHT", "icon": "mdi:lightbulb"},
    {"name": "Eco", "key": "ECO", "icon": "mdi:leaf"},
    {"name": "Dos 1 CL", "key": "DOS_1_CL", "icon": "mdi:flask"},
    {"name": "Dos 4 PHM", "key": "DOS_4_PHM", "icon": "mdi:flask"},
]


class VioletSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Violet Device Switch."""

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        key: str,
        name: str,
        icon: str,
        config_entry: ConfigEntry,
        auto_reset_time: float = 0
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._key = key
        self._icon = icon
        self._config_entry = config_entry
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        self._attr_name = f"{device_name} {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{key.lower()}"
        self.ip_address: str = config_entry.data.get(CONF_API_URL, "Unknown IP")
        self.auto_reset_deadline: datetime | None = None

        # Device Info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",  # wenn du später dynamisch abrufen willst, kannst du das anpassen
            "sw_version": self.coordinator.data.get("fw", "Unknown"),
            "configuration_url": f"http://{self.ip_address}",
        }

        _LOGGER.debug("VioletSwitch (%s) init: IP=%s, key=%s", device_name, self.ip_address, key)

    def _get_switch_state(self) -> int | None:
        """Fetch the current raw state of this switch from the coordinator data."""
        return self.coordinator.data.get(self._key)

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on, based on the mapped API state."""
        raw_state = self._get_switch_state()
        return STATE_MAP.get(raw_state, False)

    @property
    def is_auto(self) -> bool:
        """Check if the switch is in AUTO mode (raw_state = 0)."""
        return self._get_switch_state() == 0

    @property
    def available(self) -> bool:
        """Return True if the switch data is available."""
        return self.coordinator.last_update_success and (self._key in self.coordinator.data)

    @property
    def icon(self) -> str:
        """Return a dynamic icon based on the current state."""
        icon_map = {
            "PUMP": "mdi:water-pump" if self.is_on else "mdi:water-pump-off",
            "LIGHT": "mdi:lightbulb-on" if self.is_on else "mdi:lightbulb",
            "ECO": "mdi:leaf" if self.is_on else "mdi:leaf-off",
            "DOS_1_CL": "mdi:flask" if self.is_on else "mdi:flask-outline",
            "DOS_4_PHM": "mdi:flask" if self.is_on else "mdi:flask-outline",
        }
        return icon_map.get(self._key, self._icon)

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes for the switch."""
        attributes = super().extra_state_attributes or {}
        attributes["status_detail"] = "AUTO" if self.is_auto else "MANUAL"
        raw_state = self._get_switch_state()
        if not self.is_auto:
            attributes["duration_remaining"] = raw_state
        else:
            attributes["duration_remaining"] = "N/A"

        if self.auto_reset_deadline:
            remaining = (self.auto_reset_deadline - datetime.now()).total_seconds()
            attributes["auto_reset_in"] = max(0, remaining)
        else:
            attributes["auto_reset_in"] = "N/A"

        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        duration = kwargs.get("duration", 0)
        last_value = kwargs.get("last_value", 0)
        await self._send_command("ON", duration, last_value)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        last_value = kwargs.get("last_value", 0)
        await self._send_command("OFF", 0, last_value)

    async def async_turn_auto(self, **kwargs: Any) -> None:
        """Set the switch to AUTO mode (or auto-delay)."""
        auto_delay = kwargs.get("auto_delay", 0)
        last_value = kwargs.get("last_value", 0)
        await self._send_command("AUTO", auto_delay, last_value)

        # Optional: Wenn du mit auto_delay meinst, dass nach X Sekunden wieder auf AUTO gestellt wird,
        # könntest du das so lösen (wie in deinem Beispielcode):
        if auto_delay > 0:
            self.auto_reset_deadline = datetime.now() + timedelta(seconds=auto_delay)
            _LOGGER.debug("Auto-reset on %s in %s seconds", self._key, auto_delay)
            await asyncio.sleep(auto_delay)
            if self.auto_reset_deadline and datetime.now() >= self.auto_reset_deadline:
                # Nochmal "AUTO" schicken
                await self._send_command("AUTO", 0, last_value)
            else:
                _LOGGER.debug("Auto-reset canceled for %s", self._key)
        else:
            self.auto_reset_deadline = None

    async def _send_command(self, action: str, duration: int = 0, last_value: int = 0) -> None:
        """Send a command via the coordinator's API."""
        if not hasattr(self.coordinator, "api") or not self.coordinator.api:
            _LOGGER.error("Coordinator hat kein API-Objekt! Abbruch.")
            return

        _LOGGER.debug(
            "_send_command -> %s: key=%s, duration=%d, last_value=%d",
            action,
            self._key,
            duration,
            last_value,
        )

        try:
            response_text = await self.coordinator.api.set_switch_state(
                key=self._key,
                action=action,
                duration=duration,
                last_value=last_value
            )
            _LOGGER.debug("Antwort vom Server (%s): %s", self._key, response_text)

            # Beispiel: Prüfe, ob "OK" drinsteht oder "SWITCHED_TO"
            lines = response_text.strip().split("\n")
            if (
                len(lines) >= 2
                and lines[0] == "OK"
                and lines[1] == self._key
            ):
                _LOGGER.debug("Kommando erfolgreich: action=%s, key=%s", action, self._key)
            else:
                _LOGGER.warning("Unerwartete Antwort für %s: %s", self._key, response_text)

            # Anschließend Daten neu abfragen
            await self.coordinator.async_request_refresh()

        except Exception as err:
            _LOGGER.error("Fehler bei _send_command %s für %s: %s", action, self._key, err)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Violet switches based on config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Sammle nur die Switches, die tatsächlich in coordinator.data vorhanden sind (optional)
    available_switches = [
        sw for sw in SWITCHES if sw["key"] in coordinator.data
    ]

    switches = [
        VioletSwitch(
            coordinator,
            key=switch["key"],
            name=switch["name"],
            icon=switch["icon"],
            config_entry=config_entry
        )
        for switch in available_switches
    ]

    async_add_entities(switches)

    # Entity-spezifische Services definieren
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "turn_auto",
        {
            vol.Optional("auto_delay", default=0): vol.Coerce(int),
            vol.Optional("last_value", default=0): vol.Coerce(int),
        },
        "async_turn_auto",
    )

    platform.async_register_entity_service(
        "turn_on",
        {
            vol.Optional("duration", default=0): vol.Coerce(int),
            vol.Optional("last_value", default=0): vol.Coerce(int),
        },
        "async_turn_on",
    )

    platform.async_register_entity_service(
        "turn_off",
        {
            vol.Optional("last_value", default=0): vol.Coerce(int),
        },
        "async_turn_off",
    )
