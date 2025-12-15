"""Switch Integration für den Violet Pool Controller - CHANGE-ONLY LOGGING & THREAD-SAFE."""

import asyncio
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import VioletPoolAPIError
from .const import ACTION_OFF, ACTION_ON, CONF_ACTIVE_FEATURES, DOMAIN, SWITCHES
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity, interpret_state_as_bool

_LOGGER = logging.getLogger(__name__)

# State Constants
# Der Violet Pool Controller verwendet verschiedene Zustände für Geräte:
# - 0: AUTO_OFF - Automatik-Modus, Gerät ist aus
# - 1: AUTO_ON - Automatik-Modus, Gerät ist an (z.B. nach Zeitplan)
# - 2-3: Weitere AUTO-Zustände (z.B. Aufwärmen, Vorbereiten)
# - 4: MANUAL_ON - Manueller Modus, Gerät ist eingeschaltet
# - 5: AUTO_OFF - Alternative AUTO-OFF Darstellung
# - 6: MANUAL_OFF - Manueller Modus, Gerät ist ausgeschaltet
#
# WICHTIG: State "4" wird als ON behandelt, nicht als ERROR/UNDEFINED.
# Dies ist ein normaler Zustand für manuell eingeschaltete Geräte.
STATE_OFF = 0
STATE_AUTO_ON = 1
STATE_MANUAL_ON = 4
STATE_AUTO_OFF = 5
STATE_MANUAL_OFF = 6

# ON_STATES: Alle Zustände, bei denen das Gerät aktiv ist (1-4)
ON_STATES = {1, 2, 3, 4}
# OFF_STATES: Alle Zustände, bei denen das Gerät inaktiv ist (0, 5, 6)
OFF_STATES = {0, 5, 6}

REFRESH_DELAY = 0.3


class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Switch with change-only logging and thread safety."""

    entity_description: SwitchEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SwitchEntityDescription,
    ) -> None:
        """
        Initialize the switch.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            description: The switch entity description.
        """
        super().__init__(coordinator, config_entry, description)

        # ✅ LOGGING OPTIMIZATION: State-Change Detection
        self._last_logged_state: bool | None = None
        self._last_logged_raw: Any = None

        # ✅ FIXED: Lokale Cache-Variable für optimistisches Update
        self._optimistic_state: bool | None = None

        # ✅ Nur Setup loggen, nicht jeden Zugriff
        _LOGGER.debug("Switch initialisiert: %s", self.entity_id)

    @property
    def is_on(self) -> bool:
        """
        Return True if the switch is on.

        Returns:
            True if on, False otherwise.
        """
        if self.coordinator.data is None:
            return False

        return self._get_switch_state()

    def _get_switch_state(self) -> bool:
        """
        Get the switch state with change-only logging and optimistic cache.

        Returns:
            The boolean state of the switch.
        """
        # Prüfe zuerst optimistischen Cache
        if self._optimistic_state is not None:
            return self._optimistic_state

        if self.coordinator.data is None:
            return False

        key = self.entity_description.key
        raw_state = self.get_value(key, "")

        # Use shared utility function
        result = interpret_state_as_bool(raw_state, key)

        # Change-Only Logging
        if result != self._last_logged_state or raw_state != self._last_logged_raw:
            _LOGGER.info(
                "Switch %s: %s → %s (raw: %s)",
                key,
                "ON"
                if self._last_logged_state
                else "OFF"
                if self._last_logged_state is not None
                else "INIT",
                "ON" if result else "OFF",
                raw_state,
            )
            self._last_logged_state = result
            self._last_logged_raw = raw_state

        return result

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """
        Return additional state attributes.

        Returns:
            A dictionary of attributes.
        """
        if self.coordinator.data is None:
            return {
                "state_type": "unavailable",
                "interpreted_as": "UNKNOWN",
                "note": "Coordinator data not available",
            }

        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        current_result = self._get_switch_state()

        attributes: dict[str, Any] = {
            "raw_state": str(raw_state) if raw_state is not None else "None",
            "state_type": type(raw_state).__name__,
            "interpreted_as": "ON" if current_result else "OFF",
        }

        # ✅ FIXED: Zeige optimistischen Cache-Status
        if self._optimistic_state is not None:
            attributes["optimistic_state"] = "ON" if self._optimistic_state else "OFF"
            attributes["pending_update"] = True

        # PUMP-spezifische Attribute
        if key == "PUMP":
            attributes.update(
                {
                    "pump_runtime": self.get_str_value("PUMP_RUNTIME", "00h 00m 00s"),
                    "pump_last_on": self.get_value("PUMP_LAST_ON", 0),
                    "pump_last_off": self.get_value("PUMP_LAST_OFF", 0),
                    "pump_rpm_2": self.get_value("PUMP_RPM_2", 0),
                }
            )

        # Runtime-Informationen
        runtime_key = f"{key}_RUNTIME"
        if runtime_key in self.coordinator.data:
            attributes["runtime"] = self.get_str_value(runtime_key, "00h 00m 00s")

        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Turn the switch on.

        Args:
            **kwargs: Additional arguments.
        """
        await self._set_switch_state(ACTION_ON, **kwargs)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """
        Turn the switch off.

        Args:
            **kwargs: Additional arguments.
        """
        await self._set_switch_state(ACTION_OFF, **kwargs)

    async def _set_switch_state(self, action: str, **kwargs: Any) -> None:
        """
        Set the switch state.

        Args:
            action: The action to perform (e.g., ACTION_ON, ACTION_OFF).
            **kwargs: Additional arguments.

        Raises:
            HomeAssistantError: If the action fails.
        """
        key = self.entity_description.key

        try:
            # ✅ User-Aktion = immer loggen (INFO)
            _LOGGER.info("Setze Switch %s auf %s", key, action)

            # Für PUMP: Unterstütze erweiterte Parameter
            if key == "PUMP" and action == ACTION_ON:
                speed = self._validate_speed(kwargs.get("speed", 2))
                duration = self._validate_duration(kwargs.get("duration", 0))

                result = await self.device.api.set_switch_state(
                    key=key, action=action, duration=duration, last_value=speed
                )
            elif key == "PVSURPLUS" and action == ACTION_ON:
                rpm = self._validate_pv_rpm(kwargs.get("rpm"))

                result = await self.device.api.set_switch_state(
                    key=key,
                    action=action,
                    last_value=rpm,
                )
            else:
                result = await self.device.api.set_switch_state(key=key, action=action)

            if result.get("success") is True:
                # ✅ Erfolg nur bei Debug loggen (API loggt bereits)
                _LOGGER.debug("Switch %s erfolgreich auf %s gesetzt", key, action)

                # ✅ FIXED: NUR lokale Variable setzen, KEINE coordinator.data Mutation!
                self._optimistic_state = action == ACTION_ON
                self.async_write_ha_state()

                _LOGGER.debug(
                    "Optimistisches Update: %s = %s (lokaler Cache, kein coordinator.data mutiert)",
                    key,
                    "ON" if self._optimistic_state else "OFF",
                )

                # Asynchroner Refresh holt echte Daten und resettet Cache
                task = asyncio.create_task(self._delayed_refresh(key))
                task.add_done_callback(lambda t: self._handle_refresh_error(t, key))
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                # ✅ Fehler = WARNING (User-relevant)
                _LOGGER.warning(
                    "Switch %s Aktion %s fehlgeschlagen: %s", key, action, error_msg
                )
                task = asyncio.create_task(self._delayed_refresh(key))
                task.add_done_callback(lambda t: self._handle_refresh_error(t, key))

        except VioletPoolAPIError as err:
            # ✅ API-Fehler = ERROR (kritisch)
            _LOGGER.error(
                "API-Fehler beim Setzen von Switch %s auf %s: %s", key, action, err
            )
            # Bei Fehler Cache löschen
            self._optimistic_state = None
            raise HomeAssistantError(f"Switch-Aktion fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler beim Setzen von Switch %s: %s", key, err)
            # Bei Fehler Cache löschen
            self._optimistic_state = None
            raise HomeAssistantError(f"Switch-Fehler: {err}") from err

    async def _delayed_refresh(self, key: str) -> None:
        """
        Perform a delayed refresh.

        Args:
            key: The switch key.
        """
        try:
            await asyncio.sleep(REFRESH_DELAY)
            await self.coordinator.async_request_refresh()

            # ✅ FIXED: Reset optimistischen Cache nach Refresh
            if self.coordinator.last_update_success:
                old_optimistic = self._optimistic_state
                self._optimistic_state = None

                if old_optimistic is not None:
                    _LOGGER.debug(
                        "Optimistischer Cache nach Refresh gelöscht für %s (war: %s)",
                        key,
                        "ON" if old_optimistic else "OFF",
                    )

            # ✅ Nur bei Debug-Level loggen
            if self.coordinator.data is not None:
                new_state = self.coordinator.data.get(key, "UNKNOWN")
                _LOGGER.debug("State nach Refresh: %s = %s", key, new_state)
            else:
                _LOGGER.debug("Coordinator data is None nach Refresh für %s", key)

        except Exception as err:
            # ✅ Refresh-Fehler = DEBUG (nicht kritisch, wird wiederholt)
            _LOGGER.debug("Fehler beim verzögerten Refresh für %s: %s", key, err)
            # Bei Fehler auch Cache löschen
            self._optimistic_state = None

    def _handle_refresh_error(self, task: asyncio.Task, key: str) -> None:
        """
        Handle errors in the refresh task.

        Args:
            task: The task object.
            key: The switch key.
        """
        try:
            if not task.cancelled():
                exc = task.exception()
                if exc is not None:
                    # ✅ Nur bei echten Problemen loggen
                    _LOGGER.debug("Refresh task failed for %s: %s", key, exc)
        except asyncio.CancelledError:
            pass  # Normal, kein Log nötig
        except Exception as err:
            _LOGGER.debug("Error handling refresh task for %s: %s", key, err)

    def _validate_speed(self, speed: Any) -> int:
        """
        Validate the speed parameter.

        Args:
            speed: The speed value.

        Returns:
            The validated speed integer.
        """
        try:
            speed_int = int(speed)
            if 1 <= speed_int <= 4:
                return speed_int
            _LOGGER.warning("Ungültiger Speed-Wert %s, verwende Default 2", speed)
            return 2
        except (ValueError, TypeError):
            _LOGGER.warning("Ungültiger Speed-Typ %s, verwende Default 2", type(speed))
            return 2

    def _validate_duration(self, duration: Any) -> int:
        """
        Validate the duration parameter.

        Args:
            duration: The duration value.

        Returns:
            The validated duration integer.
        """
        try:
            duration_int = int(duration)
            if duration_int >= 0:
                return duration_int
            _LOGGER.warning("Negative Duration %s, verwende 0", duration)
            return 0
        except (ValueError, TypeError):
            _LOGGER.warning("Ungültiger Duration-Typ %s, verwende 0", type(duration))
            return 0

    def _validate_pv_rpm(self, rpm: Any | None) -> int:
        """
        Validate the PV surplus RPM parameter.

        Args:
            rpm: The RPM value.

        Returns:
            The validated RPM integer.
        """
        if rpm is None:
            return 2
        try:
            rpm_int = int(rpm)
        except (TypeError, ValueError):
            _LOGGER.debug("Ungültiger PV Surplus RPM %s, verwende Default 2", rpm)
            return 2

        if 1 <= rpm_int <= 3:
            return rpm_int

        _LOGGER.debug(
            "PV Surplus RPM %s außerhalb des gültigen Bereichs, verwende Default 2", rpm
        )
        return 2


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up switches for the config entry.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry.
        async_add_entities: Callback to add entities.
    """
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities: list[SwitchEntity] = []

    # ✅ Setup = INFO (wichtig für User)
    _LOGGER.info("Switch Setup - Active features: %s", active_features)

    # Diagnose nur bei verfügbaren Daten
    if coordinator.data is not None:
        # ✅ Diagnose = DEBUG (nur für Entwickler)
        _LOGGER.debug("Coordinator data keys: %d", len(coordinator.data.keys()))

        # State-Diagnose nur für wichtige Switches
        for key in ["PUMP", "SOLAR", "HEATER"]:
            if key in coordinator.data:
                try:
                    value = coordinator.data[key]
                    state_int = (
                        int(value)
                        if isinstance(value, (int, float)) or str(value).isdigit()
                        else None
                    )
                    expected = (
                        "ON"
                        if state_int in ON_STATES
                        else "OFF"
                        if state_int in OFF_STATES
                        else "UNKNOWN"
                    )
                    _LOGGER.debug("%s: raw=%s → %s", key, value, expected)
                except (ValueError, KeyError, TypeError) as err:
                    _LOGGER.debug("Diagnose-Fehler für %s: %s", key, err)
    else:
        _LOGGER.warning("Coordinator data is None bei Switch Setup")

    # Create switches
    for switch_config in SWITCHES:
        # Map entity_category string to EntityCategory enum
        entity_category = None
        if "entity_category" in switch_config:
            category_str = switch_config["entity_category"]
            if category_str == "diagnostic":
                entity_category = EntityCategory.DIAGNOSTIC
            elif category_str == "config":
                entity_category = EntityCategory.CONFIG

        description = SwitchEntityDescription(
            key=switch_config["key"],
            name=switch_config["name"],
            icon=switch_config.get("icon"),
            entity_category=entity_category,
        )

        feature_id = switch_config.get("feature_id")

        if feature_id and feature_id not in active_features:
            # ✅ DEBUG: Unwichtige Info
            _LOGGER.debug(
                "Überspringe Switch %s: Feature %s nicht aktiv",
                description.key,
                feature_id,
            )
            continue

        entities.append(VioletSwitch(coordinator, config_entry, description))

    if entities:
        async_add_entities(entities)
        # ✅ INFO: Erfolgreicher Setup
        _LOGGER.info("✓ %d Switches erfolgreich eingerichtet", len(entities))

        # Final check nur bei DEBUG
        if coordinator.data is not None:
            for entity in entities:
                key = entity.entity_description.key
                if key in ["PUMP", "SOLAR", "HEATER"] and key in coordinator.data:
                    try:
                        raw_state = coordinator.data[key]
                        # Type cast to access specific method
                        should_be_on = entity._get_switch_state()  # type: ignore[attr-defined]
                        _LOGGER.debug(
                            "Final check %s: raw=%s → display=%s",
                            key,
                            raw_state,
                            "ON" if should_be_on else "OFF",
                        )
                    except (ValueError, KeyError, TypeError, AttributeError) as err:
                        _LOGGER.debug("Final-Check-Fehler für %s: %s", key, err)
    else:
        # ✅ WARNING: Potenzielles Problem
        _LOGGER.warning("⚠ Keine Switches eingerichtet")
