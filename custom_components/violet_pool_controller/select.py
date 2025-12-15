"""Select Integration für den Violet Pool Controller - ON/OFF/AUTO Steuerung."""

import asyncio
import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import VioletPoolAPIError
from .const import (
    ACTION_AUTO,
    ACTION_OFF,
    ACTION_ON,
    CONF_ACTIVE_FEATURES,
    DOMAIN,
    SELECT_CONTROLS,
)
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity

_LOGGER = logging.getLogger(__name__)

# Mode Constants
MODE_OFF = "off"
MODE_ON = "on"
MODE_AUTO = "auto"

# State to Mode Mapping
# Der Controller liefert numerische States 0-6
# 0 = AUTO (Standby/Off)
# 1 = MANUAL ON oder AUTO ON
# 2 = AUTO (Active)
# 3 = AUTO (Active with Timer)
# 4 = MANUAL ON (Forced)
# 5 = AUTO (Waiting/Off)
# 6 = MANUAL OFF
STATE_TO_MODE = {
    0: MODE_AUTO,  # Auto Standby
    1: MODE_ON,  # Manual ON oder Auto ON (behandeln als ON)
    2: MODE_AUTO,  # Auto Active
    3: MODE_AUTO,  # Auto Active with Timer
    4: MODE_ON,  # Manual ON (Forced)
    5: MODE_AUTO,  # Auto Waiting
    6: MODE_OFF,  # Manual OFF
}

# Mode to Action Mapping
MODE_TO_ACTION = {
    MODE_OFF: ACTION_OFF,
    MODE_ON: ACTION_ON,
    MODE_AUTO: ACTION_AUTO,
}

REFRESH_DELAY = 0.5


class VioletSelect(VioletPoolControllerEntity, SelectEntity):
    """Select Entity für ON/OFF/AUTO Steuerung von Pool-Geräten."""

    entity_description: SelectEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SelectEntityDescription,
        device_key: str,
    ) -> None:
        """
        Initialize the select entity.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            description: The select entity description.
            device_key: The device key (e.g., PUMP, HEATER).
        """
        super().__init__(coordinator, config_entry, description)
        self._device_key = device_key
        self._attr_options = [MODE_OFF, MODE_ON, MODE_AUTO]

        # Optimistic state cache
        self._optimistic_mode: str | None = None

        _LOGGER.debug(
            "Select-Entity initialisiert: %s (Device: %s)", self.entity_id, device_key
        )

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        # Prüfe optimistischen Cache
        if self._optimistic_mode is not None:
            return self._optimistic_mode

        if self.coordinator.data is None:
            return None

        raw_state = self.get_value(self._device_key, "")

        # Konvertiere raw_state zu Mode
        try:
            if isinstance(raw_state, (int, float)):
                state_int = int(raw_state)
            elif isinstance(raw_state, str) and raw_state.isdigit():
                state_int = int(raw_state)
            else:
                # String-based states (ON, OFF, AUTO)
                state_str = str(raw_state).upper().strip()
                if state_str in ("ON", "MANUAL", "MAN"):
                    return MODE_ON
                if state_str in ("OFF", "STOPPED"):
                    return MODE_OFF
                if state_str in ("AUTO", "AUTOMATIC"):
                    return MODE_AUTO
                _LOGGER.debug(
                    "Unbekannter String-State '%s' für %s, verwende AUTO als Default",
                    raw_state,
                    self._device_key,
                )
                return MODE_AUTO

            # Verwende Mapping für numerische States
            mode = STATE_TO_MODE.get(state_int)
            if mode:
                return mode

            _LOGGER.warning(
                "Unbekannter numerischer State %s für %s, verwende AUTO als Default",
                state_int,
                self._device_key,
            )
            return MODE_AUTO

        except (ValueError, TypeError) as err:
            _LOGGER.debug(
                "Fehler beim Konvertieren von State '%s' für %s: %s",
                raw_state,
                self._device_key,
                err,
            )
            return MODE_AUTO

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}

        raw_state = self.get_value(self._device_key, "")

        attributes: dict[str, Any] = {
            "raw_state": str(raw_state) if raw_state is not None else "None",
            "device_key": self._device_key,
        }

        # Optimistic state indicator
        if self._optimistic_mode is not None:
            attributes["pending_update"] = True
            attributes["target_mode"] = self._optimistic_mode

        # Device-spezifische Attribute
        if self._device_key == "PUMP":
            attributes.update(
                {
                    "runtime": self.get_str_value("PUMP_RUNTIME", "00h 00m 00s"),
                    "speed": self.get_value("PUMP_RPM_2", 2),
                }
            )
        elif self._device_key == "HEATER":
            attributes.update(
                {
                    "runtime": self.get_str_value("HEATER_RUNTIME", "00h 00m 00s"),
                    "target_temp": self.get_value("HEATER_TARGET_TEMP", 28.0),
                }
            )
        elif self._device_key == "SOLAR":
            attributes.update(
                {
                    "runtime": self.get_str_value("SOLAR_RUNTIME", "00h 00m 00s"),
                    "target_temp": self.get_value("SOLAR_TARGET_TEMP", 30.0),
                }
            )

        return attributes

    async def async_select_option(self, option: str) -> None:
        """
        Change the selected option.

        Args:
            option: The new option (off, on, auto).

        Raises:
            HomeAssistantError: If the action fails.
        """
        if option not in self._attr_options:
            raise HomeAssistantError(f"Ungültige Option: {option}")

        action = MODE_TO_ACTION[option]

        try:
            _LOGGER.info("Setze %s auf Modus '%s' (Action: %s)", self._device_key, option, action)

            # API call
            result = await self.device.api.set_switch_state(key=self._device_key, action=action)

            if result.get("success") is True:
                _LOGGER.debug("%s erfolgreich auf Modus '%s' gesetzt", self._device_key, option)

                # Optimistic update
                self._optimistic_mode = option
                self.async_write_ha_state()

                # Delayed refresh
                task = asyncio.create_task(self._delayed_refresh())
                task.add_done_callback(lambda t: self._handle_refresh_error(t))
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                _LOGGER.warning(
                    "%s Modus-Wechsel zu '%s' fehlgeschlagen: %s",
                    self._device_key,
                    option,
                    error_msg,
                )
                task = asyncio.create_task(self._delayed_refresh())
                task.add_done_callback(lambda t: self._handle_refresh_error(t))

        except VioletPoolAPIError as err:
            _LOGGER.error(
                "API-Fehler beim Setzen von %s auf Modus '%s': %s",
                self._device_key,
                option,
                err,
            )
            self._optimistic_mode = None
            raise HomeAssistantError(f"Modus-Wechsel fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.error(
                "Unerwarteter Fehler beim Setzen von %s auf Modus '%s': %s",
                self._device_key,
                option,
                err,
            )
            self._optimistic_mode = None
            raise HomeAssistantError(f"Modus-Wechsel Fehler: {err}") from err

    async def _delayed_refresh(self) -> None:
        """Perform a delayed refresh."""
        try:
            await asyncio.sleep(REFRESH_DELAY)
            await self.coordinator.async_request_refresh()

            # Reset optimistic cache nach erfolgreichem Refresh
            if self.coordinator.last_update_success:
                old_mode = self._optimistic_mode
                self._optimistic_mode = None

                if old_mode is not None:
                    _LOGGER.debug(
                        "Optimistischer Cache nach Refresh gelöscht für %s (war: %s)",
                        self._device_key,
                        old_mode,
                    )

        except Exception as err:
            _LOGGER.debug("Fehler beim verzögerten Refresh für %s: %s", self._device_key, err)
            self._optimistic_mode = None

    def _handle_refresh_error(self, task: asyncio.Task) -> None:
        """
        Handle errors in the refresh task.

        Args:
            task: The task object.
        """
        try:
            if not task.cancelled():
                exc = task.exception()
                if exc is not None:
                    _LOGGER.debug("Refresh task failed for %s: %s", self._device_key, exc)
        except asyncio.CancelledError:
            pass
        except Exception as err:
            _LOGGER.debug("Error handling refresh task for %s: %s", self._device_key, err)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up select entities for the config entry.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry.
        async_add_entities: Callback to add entities.
    """
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities: list[SelectEntity] = []

    _LOGGER.info("Select Setup - Active features: %s", active_features)

    # Create select entities
    for select_config in SELECT_CONTROLS:
        feature_id = select_config.get("feature_id")

        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Überspringe Select %s: Feature %s nicht aktiv",
                select_config["key"],
                feature_id,
            )
            continue

        # Map entity_category string to EntityCategory enum
        entity_category = None
        if "entity_category" in select_config:
            category_str = select_config["entity_category"]
            if category_str == "config":
                entity_category = EntityCategory.CONFIG

        description = SelectEntityDescription(
            key=select_config["key"],
            name=select_config["name"],
            icon=select_config.get("icon"),
            entity_category=entity_category,
        )

        entities.append(
            VioletSelect(
                coordinator, config_entry, description, select_config["device_key"]
            )
        )

    if entities:
        async_add_entities(entities)
        _LOGGER.info("✓ %d Select-Entities erfolgreich eingerichtet", len(entities))
    else:
        _LOGGER.warning("⚠ Keine Select-Entities eingerichtet")
