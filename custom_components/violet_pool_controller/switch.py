"""Switch Integration für den Violet Pool Controller - CHANGE-ONLY LOGGING & THREAD-SAFE."""
import logging
import asyncio
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SWITCHES, CONF_ACTIVE_FEATURES, ACTION_ON, ACTION_OFF, STATE_MAP
from .api import VioletPoolAPIError
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# State Constants
STATE_OFF = 0
STATE_AUTO_ON = 1
STATE_MANUAL_ON = 4
STATE_AUTO_OFF = 5
STATE_MANUAL_OFF = 6

ON_STATES = {1, 2, 3, 4}
OFF_STATES = {0, 5, 6}

REFRESH_DELAY = 0.3


class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Switch mit Change-Only Logging & Thread-Safe - LOGGING OPTIMIZED & THREAD-SAFE."""
    entity_description: SwitchEntityDescription

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry,
        description: SwitchEntityDescription
    ) -> None:
        """Initialisiere den Switch mit Logging-Optimierung & Thread-Safety."""
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
        """Gibt True zurück, wenn der Switch eingeschaltet ist."""
        if self.coordinator.data is None:
            return False
        
        return self._get_switch_state()

    def _get_switch_state(self) -> bool:
        """
        State-Abfrage mit Change-Only Logging & optimistischem Cache.
        
        ✅ LOGGING OPTIMIZATION:
        - Nur bei State-Änderungen loggen
        - Keine Debug-Logs bei jedem Property-Zugriff
        
        ✅ FIXED: Prüft zuerst optimistischen Cache
        """
        # ✅ FIXED: Prüfe zuerst optimistischen Cache
        if self._optimistic_state is not None:
            return self._optimistic_state
        
        if self.coordinator.data is None:
            return False
        
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        
        if raw_state is None or raw_state == "":
            return False
        
        # State interpretieren
        state_int = self._convert_to_int(raw_state)
        
        if state_int is not None:
            result = self._interpret_int_state(state_int, key)
        else:
            result = self._interpret_string_state(raw_state, key)
        
        # ✅ LOGGING OPTIMIZATION: Nur bei Änderung loggen
        if result != self._last_logged_state or raw_state != self._last_logged_raw:
            _LOGGER.info(
                "Switch %s: %s → %s (raw: %s)",
                key,
                "ON" if self._last_logged_state else "OFF" if self._last_logged_state is not None else "INIT",
                "ON" if result else "OFF",
                raw_state
            )
            self._last_logged_state = result
            self._last_logged_raw = raw_state
        
        return result

    def _convert_to_int(self, value: Any) -> int | None:
        """Konvertiere Wert zu Integer, wenn möglich."""
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str) and value.isdigit():
                return int(value)
        except (ValueError, TypeError):
            pass
        return None

    def _interpret_int_state(self, state_int: int, key: str) -> bool:
        """
        Interpretiere Integer State - LOGGING OPTIMIZED.
        
        ✅ LOGGING OPTIMIZATION: Keine Debug-Logs, nur Warnungen bei Problemen.
        """
        if state_int in STATE_MAP:
            return STATE_MAP[state_int]
        
        if state_int in ON_STATES:
            return True
        
        if state_int in OFF_STATES:
            return False
        
        # ✅ Nur unbekannte States warnen (einmalig durch Change-Detection)
        _LOGGER.warning(
            "Unbekannter State %d für %s - bitte im GitHub melden! "
            "Integration verwendet Fallback: OFF",
            state_int, key
        )
        return False

    def _interpret_string_state(self, raw_state: Any, key: str) -> bool:
        """
        Interpretiere String State - LOGGING OPTIMIZED.
        
        ✅ LOGGING OPTIMIZATION: Keine Debug-Logs.
        """
        state_str = str(raw_state).upper().strip()
        
        if state_str in STATE_MAP:
            return STATE_MAP[state_str]
        
        boolean_on_states = {"TRUE", "ON", "1", "ACTIVE", "RUNNING", "MANUAL", "MAN"}
        boolean_off_states = {"FALSE", "OFF", "0", "INACTIVE", "STOPPED"}
        
        if state_str in boolean_on_states:
            return True
        
        if state_str in boolean_off_states:
            return False
        
        # ✅ Nur unbekannte Strings warnen
        _LOGGER.warning(
            "Unbekannter State-String '%s' für %s - bitte im GitHub melden! "
            "Integration verwendet Fallback: OFF",
            state_str, key
        )
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes - MINIMAL LOGGING."""
        if self.coordinator.data is None:
            return {
                "state_type": "unavailable",
                "interpreted_as": "UNKNOWN",
                "note": "Coordinator data not available"
            }
        
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        current_result = self._get_switch_state()
        
        attributes = {
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
            attributes.update({
                "pump_runtime": self.get_str_value("PUMP_RUNTIME", "00h 00m 00s"),
                "pump_last_on": self.get_value("PUMP_LAST_ON", 0),
                "pump_last_off": self.get_value("PUMP_LAST_OFF", 0),
                "pump_rpm_2": self.get_value("PUMP_RPM_2", 0),
            })
        
        # Runtime-Informationen
        runtime_key = f"{key}_RUNTIME"
        if runtime_key in self.coordinator.data:
            attributes["runtime"] = self.get_str_value(runtime_key, "00h 00m 00s")
        
        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Schalte den Switch ein."""
        await self._set_switch_state(ACTION_ON, **kwargs)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Schalte den Switch aus."""
        await self._set_switch_state(ACTION_OFF, **kwargs)

    async def _set_switch_state(self, action: str, **kwargs: Any) -> None:
        """
        Setze den Switch-Zustand - LOGGING OPTIMIZED & THREAD-SAFE.
        
        ✅ LOGGING OPTIMIZATION:
        - INFO für User-Aktionen (wichtig)
        - DEBUG nur für interne Details
        - Konsolidierte Error-Messages
        
        ✅ FIXED: Keine coordinator.data Mutation mehr!
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
                    key=key,
                    action=action,
                    duration=duration,
                    last_value=speed
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
            
            if result.get("success", True):
                # ✅ Erfolg nur bei Debug loggen (API loggt bereits)
                _LOGGER.debug("Switch %s erfolgreich auf %s gesetzt", key, action)
                
                # ✅ FIXED: NUR lokale Variable setzen, KEINE coordinator.data Mutation!
                self._optimistic_state = (action == ACTION_ON)
                self.async_write_ha_state()
                
                _LOGGER.debug(
                    "Optimistisches Update: %s = %s (lokaler Cache, kein coordinator.data mutiert)",
                    key,
                    "ON" if self._optimistic_state else "OFF"
                )
                
                # Asynchroner Refresh holt echte Daten und resettet Cache
                task = asyncio.create_task(self._delayed_refresh(key))
                task.add_done_callback(lambda t: self._handle_refresh_error(t, key))
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                # ✅ Fehler = WARNING (User-relevant)
                _LOGGER.warning("Switch %s Aktion %s fehlgeschlagen: %s", key, action, error_msg)
                task = asyncio.create_task(self._delayed_refresh(key))
                task.add_done_callback(lambda t: self._handle_refresh_error(t, key))
            
        except VioletPoolAPIError as err:
            # ✅ API-Fehler = ERROR (kritisch)
            _LOGGER.error("API-Fehler beim Setzen von Switch %s auf %s: %s", key, action, err)
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
        Verzögerter Refresh - MINIMAL LOGGING & THREAD-SAFE.
        
        ✅ FIXED: Resettet optimistischen Cache nach erfolgreichem Refresh.
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
                        "ON" if old_optimistic else "OFF"
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
        """Handle errors in refresh task - MINIMAL LOGGING."""
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
        """Validiere Speed-Parameter - MINIMAL LOGGING."""
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
        """Validiere Duration-Parameter - MINIMAL LOGGING."""
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
        """Validiere den PV-Überschuss RPM Parameter."""

        if rpm is None:
            return 2
        try:
            rpm_int = int(rpm)
        except (TypeError, ValueError):
            _LOGGER.debug("Ungültiger PV Surplus RPM %s, verwende Default 2", rpm)
            return 2

        if 1 <= rpm_int <= 3:
            return rpm_int

        _LOGGER.debug("PV Surplus RPM %s außerhalb des gültigen Bereichs, verwende Default 2", rpm)
        return 2


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Switches ein - LOGGING OPTIMIZED."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, 
        config_entry.data.get(CONF_ACTIVE_FEATURES, [])
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
                    state_int = int(value) if isinstance(value, (int, float)) or str(value).isdigit() else None
                    expected = "ON" if state_int in ON_STATES else "OFF" if state_int in OFF_STATES else "UNKNOWN"
                    _LOGGER.debug("%s: raw=%s → %s", key, value, expected)
                except Exception:
                    pass  # Fehler in Diagnose ignorieren
    else:
        _LOGGER.warning("Coordinator data is None bei Switch Setup")

    # Create switches
    for switch_config in SWITCHES:
        description = SwitchEntityDescription(
            key=switch_config["key"],
            name=switch_config["name"],
            icon=switch_config.get("icon"),
        )
        
        feature_id = switch_config.get("feature_id")
        
        if feature_id and feature_id not in active_features:
            # ✅ DEBUG: Unwichtige Info
            _LOGGER.debug("Überspringe Switch %s: Feature %s nicht aktiv", 
                         description.key, feature_id)
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
                        should_be_on = entity._get_switch_state()
                        _LOGGER.debug("Final check %s: raw=%s → display=%s", 
                                    key, raw_state, "ON" if should_be_on else "OFF")
                    except Exception:
                        pass
    else:
        # ✅ WARNING: Potenzielles Problem
        _LOGGER.warning("⚠ Keine Switches eingerichtet")

