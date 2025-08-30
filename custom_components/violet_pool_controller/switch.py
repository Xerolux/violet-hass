"""Switch Integration für den Violet Pool Controller - COMPLETE FIX with corrected state parsing."""
import logging
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

class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Repräsentation eines Violet Pool Switches - MIT KORRIGIERTER STATE LOGIC."""
    entity_description: SwitchEntityDescription

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry,
        description: SwitchEntityDescription
    ) -> None:
        """Initialisiere den Switch."""
        super().__init__(coordinator, config_entry, description)
        _LOGGER.debug("Initialisiere Switch: %s (unique_id=%s)", self.entity_id, self._attr_unique_id)

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn der Switch eingeschaltet ist."""
        return self._get_switch_state()

    def _get_switch_state(self) -> bool:
        """Rufe den aktuellen Switch-Zustand ab - KORRIGIERTE VERSION."""
        key = self.entity_description.key
        raw_state = self.get_value(key, "")  # Verwende get_value() statt get_str_value()
        
        # Debug-Logging für Problemdiagnose
        _LOGGER.debug("Switch '%s': raw_state = '%s' (type: %s)", key, raw_state, type(raw_state))
        
        # Spezielles Debug-Logging für PUMP
        if key == "PUMP":
            _LOGGER.info("🔍 PUMP STATE DEBUG: raw_value = %s (type: %s)", raw_state, type(raw_state))
        
        if raw_state is None:
            _LOGGER.debug("Switch '%s' hat None-Zustand. Standard: OFF.", key)
            return False
        
        # Konvertiere zu String für einheitliche Behandlung
        state_str = str(raw_state).upper().strip()
        
        if not state_str:
            _LOGGER.debug("Switch '%s' hat leeren Zustand. Standard: OFF.", key)
            return False

        # STATE_MAP aus const.py verwenden - KRITISCHE KORREKTUR
        # Prüfe zuerst String-basierte States
        if state_str in STATE_MAP:
            result = STATE_MAP[state_str]
            _LOGGER.debug("Switch '%s': '%s' → %s (via STATE_MAP)", key, state_str, result)
            if key == "PUMP":
                _LOGGER.info("🎯 PUMP RESULT via STATE_MAP: %s → %s", state_str, result)
            return result
        
        # Fallback: Direkter numerischer Vergleich für PUMP States
        # Basierend auf API-Dokumentation Kapitel 26.2.1:
        # 0 = AUTO-Standby (OFF), 1 = Manuell EIN, 2 = AUTO-Aktiv (ON), 
        # 3 = AUTO-Zeitsteuerung (ON), 4 = Manuell forciert (ON), 
        # 5 = AUTO-Wartend (OFF), 6 = Manuell AUS
        if state_str.isdigit():
            numeric_state = int(state_str)
            result = numeric_state in [1, 2, 3, 4]  # Diese States bedeuten "EIN"
            _LOGGER.debug("Switch '%s': numeric %d → %s (numeric logic)", key, numeric_state, result)
            if key == "PUMP":
                _LOGGER.info("🎯 PUMP RESULT via numeric: %d → %s", numeric_state, result)
            return result
        
        # Letzter Fallback: Boolean conversion für String-States
        boolean_true_states = ["TRUE", "ON", "1", "ACTIVE", "RUNNING", "OPEN", "OPENING"]
        result = state_str in boolean_true_states
        _LOGGER.debug("Switch '%s': '%s' → %s (string fallback)", key, state_str, result)
        
        if key == "PUMP":
            _LOGGER.info("🎯 PUMP RESULT via fallback: '%s' → %s", state_str, result)
        
        return result

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        
        attributes = {
            "raw_state": str(raw_state),
            "state_type": type(raw_state).__name__,
        }
        
        # Zusätzliche Attribute für PUMP
        if key == "PUMP":
            attributes.update({
                "pump_runtime": self.get_str_value("PUMP_RUNTIME", "00h 00m 00s"),
                "pump_last_on": self.get_value("PUMP_LAST_ON", 0),
                "pump_last_off": self.get_value("PUMP_LAST_OFF", 0),
                "pump_rpm_1": self.get_value("PUMP_RPM_1", 0),
                "pump_state_raw": self.get_value("PUMPSTATE", ""),
            })
        
        # Runtime-Informationen wenn verfügbar
        runtime_key = f"{key}_RUNTIME"
        if runtime_key in (self.coordinator.data or {}):
            attributes["runtime"] = self.get_str_value(runtime_key, "00h 00m 00s")
        
        # Last ON/OFF times wenn verfügbar
        last_on_key = f"{key}_LAST_ON"
        last_off_key = f"{key}_LAST_OFF"
        if last_on_key in (self.coordinator.data or {}):
            attributes["last_turned_on"] = self.get_value(last_on_key, 0)
        if last_off_key in (self.coordinator.data or {}):
            attributes["last_turned_off"] = self.get_value(last_off_key, 0)
        
        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Schalte den Switch ein."""
        await self._set_switch_state(ACTION_ON, **kwargs)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Schalte den Switch aus."""
        await self._set_switch_state(ACTION_OFF, **kwargs)

    async def _set_switch_state(self, action: str, **kwargs: Any) -> None:
        """Setze den Switch-Zustand mit verbesserter Fehlerbehandlung."""
        key = self.entity_description.key
        
        try:
            _LOGGER.info("Setze Switch %s auf %s", key, action)
            
            # Für PUMP: Unterstütze erweiterte Parameter
            if key == "PUMP" and action == ACTION_ON:
                # Prüfe auf speed-Parameter aus kwargs oder aus Helper-Inputs
                speed = kwargs.get("speed", 2)  # Standard: Normal-Geschwindigkeit
                duration = kwargs.get("duration", 0)  # Standard: Permanent
                
                _LOGGER.info("PUMP wird eingeschaltet: speed=%s, duration=%s", speed, duration)
                result = await self.device.api.set_switch_state(
                    key=key, 
                    action=action, 
                    duration=duration,
                    last_value=speed
                )
            else:
                # Standard Switch-Aktion
                result = await self.device.api.set_switch_state(key=key, action=action)
            
            if result.get("success", True):
                _LOGGER.info("Switch %s erfolgreich auf %s gesetzt", key, action)
                
                # Optimistische State-Aktualisierung
                if action == ACTION_ON:
                    self.coordinator.data[key] = 1  # Numerisch für korrekte State-Erkennung
                else:
                    self.coordinator.data[key] = 0
                
                self.async_write_ha_state()
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                _LOGGER.warning("Switch %s Aktion %s möglicherweise fehlgeschlagen: %s", 
                              key, action, error_msg)
                
                # Bei kritischen Fehlern Exception werfen
                if "error" in error_msg.lower() or "failed" in error_msg.lower():
                    raise HomeAssistantError(f"Switch-Aktion fehlgeschlagen: {error_msg}")
            
            # Request refresh to get actual state - mit kurzer Verzögerung
            await asyncio.sleep(0.5)  # Kurz warten damit Controller Status aktualisiert
            await self.coordinator.async_request_refresh()
            
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen von Switch %s auf %s: %s", key, action, err)
            raise HomeAssistantError(f"Switch-Aktion fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler beim Setzen von Switch %s: %s", key, err)
            raise HomeAssistantError(f"Switch-Fehler: {err}") from err

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Switches für die Config Entry ein - MIT VERBESSERTER DIAGNOSTIK."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    entities: list[SwitchEntity] = []

    # Debug-Logging für Setup-Diagnose
    _LOGGER.info("🔍 SWITCH SETUP DEBUG:")
    _LOGGER.info("  Active features: %s", active_features)
    _LOGGER.info("  Coordinator data keys: %s", list(coordinator.data.keys()) if coordinator.data else 'NO DATA')
    
    if coordinator.data:
        _LOGGER.info("  PUMP in data: %s", 'PUMP' in coordinator.data)
        if 'PUMP' in coordinator.data:
            _LOGGER.info("  PUMP value: %s (type: %s)", coordinator.data['PUMP'], type(coordinator.data['PUMP']))

    # Create switch descriptions from SWITCHES constant
    for switch_config in SWITCHES:
        # Use proper SwitchEntityDescription
        description = SwitchEntityDescription(
            key=switch_config["key"],
            name=switch_config["name"],
            icon=switch_config.get("icon"),
        )
        
        # Get feature_id from the original SWITCHES config
        feature_id = switch_config.get("feature_id")
        
        # Check if feature is active (if feature_id is specified)
        if feature_id and feature_id not in active_features:
            _LOGGER.debug("Überspringe Switch %s: Feature %s nicht aktiv", description.key, feature_id)
            continue
            
        # Spezielle Behandlung für PUMP Switch - immer erstellen wenn filter_control aktiv
        if description.key == "PUMP" and "filter_control" in active_features:
            _LOGGER.info("✅ Erstelle PUMP Switch (filter_control aktiv)")
            entities.append(VioletSwitch(coordinator, config_entry, description))
            continue
        
        # Standard Switch-Erstellung
        # Wir erstellen den Switch auch wenn keine Daten da sind, da er steuerbar sein könnte
        _LOGGER.debug("Erstelle Switch: %s (feature: %s)", description.name, feature_id or "none")
        entities.append(VioletSwitch(coordinator, config_entry, description))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("✅ %d Switches eingerichtet: %s", len(entities), [e.entity_description.name for e in entities])
        
        # Spezielles Logging für PUMP Switch
        pump_switches = [e for e in entities if e.entity_description.key == "PUMP"]
        if pump_switches:
            pump_switch = pump_switches[0]
            _LOGGER.info("🎯 PUMP SWITCH Details:")
            _LOGGER.info("  Entity ID: %s", pump_switch.entity_id)
            _LOGGER.info("  Unique ID: %s", pump_switch._attr_unique_id)
            _LOGGER.info("  Name: %s", pump_switch._attr_name)
            if coordinator.data and 'PUMP' in coordinator.data:
                _LOGGER.info("  Current raw state: %s", coordinator.data['PUMP'])
                _LOGGER.info("  Should show as: %s", "ON" if coordinator.data['PUMP'] in [1, 2, 3, 4] else "OFF")
    else:
        _LOGGER.warning("❌ Keine Switches eingerichtet - prüfe active_features und Konfiguration")
        _LOGGER.info("  Available switch configs: %s", [s["name"] for s in SWITCHES])
        _LOGGER.info("  Required for PUMP: 'filter_control' in active_features")