"""Switch-Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, List

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceError
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN,
    INTEGRATION_VERSION,
    MANUFACTURER,
    SWITCHES,
    STATE_MAP,
    DOSING_FUNCTIONS,
    CONF_ACTIVE_FEATURES,
    API_SET_FUNCTION_MANUALLY,
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class VioletSwitchEntityDescription(SwitchEntityDescription):
    """Class describing Violet Pool switch entities."""
    feature_id: Optional[str] = None

class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Representation of a Violet Pool Controller Switch."""

    entity_description: VioletSwitchEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: VioletSwitchEntityDescription,
    ):
        """Initialize the switch."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_description=description,
        )
        self._icon_base = description.icon
        self._has_logged_none_state = False

    @property
    def icon(self) -> str:
        """Return the icon for the switch, changing based on state."""
        return f"{self._icon_base}-off" if not self.is_on else self._icon_base

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self._get_switch_state()

    def _get_switch_state(self) -> bool:
        """Get the current state of the switch from coordinator data."""
        raw_state = self.get_str_value(self.entity_description.key, "").upper()
        if not raw_state:
            if not self._has_logged_none_state:
                self._logger.warning(
                    "Switch %s returned empty state. Defaulting to OFF.",
                    self.entity_description.key,
                )
                self._has_logged_none_state = True
            return False
        return STATE_MAP.get(raw_state, self.get_bool_value(self.entity_description.key, False))

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self._send_command("ON")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self._send_command("OFF")

    async def async_turn_auto(self, auto_delay: int = 0) -> None:
        """Set the switch to AUTO mode."""
        await self._send_command("AUTO", auto_delay)

    async def _send_command(self, action: str, duration: int = 0) -> None:
        """Send a command to the device."""
        try:
            key = self.entity_description.key
            self._logger.debug("Sending command to %s: %s (duration: %d)", key, action, duration)
            result = await self.coordinator.api.set_switch_state(
                key=key,
                action=action,
                duration=duration,
            )
            self._logger.debug("Command sent to %s: %s, response: %s", key, action, result)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            self._logger.error("Failed to send command %s to %s: %s", action, self.entity_description.key, err)
            raise ServiceError(f"Failed to send command {action} to {self.entity_description.key}: {err}") from err

    async def _manual_dosing(self, duration_seconds: int) -> None:
        """Perform manual dosing for the specified duration."""
        dosing_type = next((k for k, v in DOSING_FUNCTIONS.items() if v == self.entity_description.key), None)
        if not dosing_type:
            self._logger.error("Switch %s is not a dosing switch", self.entity_description.key)
            raise ServiceError(f"Switch {self.entity_description.key} is not a dosing switch")

        try:
            self._logger.debug("Starting manual dosing for %s: %d seconds", dosing_type, duration_seconds)
            result = await self.coordinator.api.manual_dosing(dosing_type, duration_seconds)
            self._logger.info("Manual dosing for %s started for %d seconds: %s", dosing_type, duration_seconds, result)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            self._logger.error("Failed to perform manual dosing for %s: %s", dosing_type, err)
            raise ServiceError(f"Failed to perform manual dosing for {dosing_type}: {err}") from err

    async def _send_with_pump_speed(self, pump_speed: int) -> None:
        """Activate PV surplus mode with a specific pump speed."""
        if self.entity_description.key != "PVSURPLUS":
            self._logger.error("Switch %s is not a PV surplus switch", self.entity_description.key)
            raise ServiceError(f"Switch {self.entity_description.key} is not a PV surplus switch")

        try:
            self._logger.debug("Activating PV surplus with pump speed %d", pump_speed)
            result = await self.coordinator.api.set_pv_surplus(active=True, pump_speed=pump_speed)
            self._logger.info("PV surplus activated with pump speed %d: %s", pump_speed, result)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            self._logger.error("Failed to activate PV surplus with pump speed %d: %s", pump_speed, err)
            raise ServiceError(f"Failed to activate PV surplus: {err}") from err

class VioletPVSurplusSwitch(VioletSwitch):
    """Special switch for PV Surplus functionality."""

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry):
        """Initialize the PV Surplus switch."""
        description = VioletSwitchEntityDescription(
            key="PVSURPLUS",
            name="PV-Überschuss",
            icon="mdi:solar-power",
            device_class=SwitchDeviceClass.SWITCH,
            feature_id="pv_surplus",
        )
        super().__init__(coordinator, config_entry, description)

    def _get_switch_state(self) -> bool:
        """Get the current state of the PV surplus switch."""
        state = self.get_int_value(self.entity_description.key, 0)
        return state in (1, 2)  # 1 or 2 indicates ON (pump speed)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on PV surplus mode with default pump speed."""
        pump_speed = kwargs.get("pump_speed", 2)  # Default to medium speed
        await self._send_with_pump_speed(pump_speed)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off PV surplus mode."""
        try:
            self._logger.debug("Deactivating PV surplus")
            result = await self.coordinator.api.set_pv_surplus(active=False)
            self._logger.info("PV surplus deactivated: %s", result)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            self._logger.error("Failed to deactivate PV surplus: %s", err)
            raise ServiceError(f"Failed to deactivate PV surplus: {err}") from err

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Violet Pool Controller switches from a config entry."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    available_data_keys = set(coordinator.data.keys())
    switches: List[VioletSwitch] = []

    # Mapping von Switch-Keys zu Feature-IDs
    feature_map = {
        "FILTER": "filter_control",
        "HEATER": "heating",
        "SOLAR": "solar",
        "BACKWASH": "backwash",
        "PVSURPLUS": "pv_surplus",
        "LIGHT": "led_lighting",
        "COVER_OPEN": "cover_control",
        "COVER_CLOSE": "cover_control",
        "REFILL": "water_refill",
        "DOS_1_CL": "chlorine_control",
        "DOS_4_PHM": "ph_control",
        "DOS_5_PHP": "ph_control",
    }

    # Standard-Switches erstellen
    for sw in SWITCHES:
        key = sw["key"]
        if key not in available_data_keys:
            continue

        feature_id = feature_map.get(key)
        # Optional: Feature-Filterung aktivieren, aktuell deaktiviert
        # if feature_id and feature_id not in active_features:
        #     _LOGGER.debug("Skipping switch %s (feature %s not active)", key, feature_id)
        #     continue

        entity_category = EntityCategory.CONFIG if key.startswith("DOS_") else None
        description = VioletSwitchEntityDescription(
            key=key,
            name=sw["name"],
            icon=sw["icon"],
            feature_id=feature_id,
            entity_category=entity_category,
        )
        switches.append(VioletSwitch(coordinator, config_entry, description))

    # PV Surplus Switch hinzufügen, falls nicht bereits vorhanden
    if "PVSURPLUS" in available_data_keys and not any(s.entity_description.key == "PVSURPLUS" for s in switches):
        switches.append(VioletPVSurplusSwitch(coordinator, config_entry))

    if switches:
        async_add_entities(switches)
        platform = entity_platform.async_get_current_platform()

        # Allgemeine Dienste
        platform.async_register_entity_service(
            "turn_auto",
            {vol.Optional("auto_delay", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=3600))},
            "async_turn_auto",
        )

        # Dienste nur für spezifische Switches
        dosing_switches = [s for s in switches if s.entity_description.key in DOSING_FUNCTIONS.values()]
        if dosing_switches:
            platform.async_register_entity_service(
                "manual_dosing",
                {vol.Required("duration_seconds"): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600))},
                "_manual_dosing",
                entity_filter=lambda e: e.entity_description.key in DOSING_FUNCTIONS.values(),
            )

        pv_switches = [s for s in switches if s.entity_description.key == "PVSURPLUS"]
        if pv_switches:
            platform.async_register_entity_service(
                "set_pv_surplus",
                {vol.Optional("pump_speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3))},
                "_send_with_pump_speed",
                entity_filter=lambda e: e.entity_description.key == "PVSURPLUS",
            )
    else:
        _LOGGER.info("No switches found or no active switch features configured")
