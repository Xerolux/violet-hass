"""Climate Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, List, Optional, Set

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_DEVICE_NAME,
    MANUFACTURER,
    INTEGRATION_VERSION,
)

_LOGGER = logging.getLogger(__name__)


class VioletClimateEntity(CoordinatorEntity, ClimateEntity):
    """Repräsentiert die Heizungs- oder Absorbersteuerung des Violet Pool Controllers."""

    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_min_temp = 20.0
    _attr_max_temp = 35.0
    _attr_target_temperature_step = 0.5

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        climate_type: str,  # "HEATER" oder "SOLAR"
    ):
        """Initialisiere die Climate-Entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self.climate_type = climate_type
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        
        # Name und Unique ID basierend auf dem Typ
        if climate_type == "HEATER":
            self._attr_name = f"{device_name} Heizung"
            self._attr_unique_id = f"{config_entry.entry_id}_heater"
            self._attr_icon = "mdi:radiator"
        else:  # SOLAR
            self._attr_name = f"{device_name} Solarabsorber"
            self._attr_unique_id = f"{config_entry.entry_id}_solar"
            self._attr_icon = "mdi:solar-power"
        
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": MANUFACTURER,
            "model": f"Violet Model X (v{INTEGRATION_VERSION})",
            "sw_version": coordinator.data.get("fw", INTEGRATION_VERSION),
            "configuration_url": f"http://{self.ip_address}",
        }
        
        # Initial targets
        self._attr_target_temperature = self._get_target_temperature()
        self._attr_hvac_mode = self._get_hvac_mode()

    def _get_target_temperature(self) -> float:
        """Hole die Zieltemperatur aus den Coordinator-Daten."""
        # Diese Logik muss an die tatsächliche API angepasst werden
        if self.climate_type == "HEATER":
            # Beispiel: Heizungs-Solltemperatur aus API-Daten
            return float(self.coordinator.data.get("HEATER_TARGET_TEMP", 28.0))
        else:  # SOLAR
            # Beispiel: Solar-Solltemperatur aus API-Daten
            return float(self.coordinator.data.get("SOLAR_TARGET_TEMP", 28.0))

    def _get_hvac_mode(self) -> str:
        """Ermittle den aktuellen HVAC-Modus."""
        # Diese Logik muss an die tatsächliche API angepasst werden
        
        state_key = "HEATER" if self.climate_type == "HEATER" else "SOLAR"
        state = self.coordinator.data.get(state_key)
        
        if state is None:
            return HVACMode.OFF
            
        # Prüfe, ob Manual-Modus aktiv ist (4 = MANUAL ON, 6 = MANUAL OFF)
        if state == 4:  # MANUAL ON
            return HVACMode.HEAT
        elif state == 6:  # MANUAL OFF
            return HVACMode.OFF
        elif state in [0, 1, 2, 3, 5]:  # AUTO-Modus (verschiedene AUTO-Zustände)
            return HVACMode.AUTO
        else:
            # Fallback
            return HVACMode.OFF

    @property
    def hvac_action(self) -> Optional[str]:
        """Gib die aktuelle HVAC-Aktion zurück."""
        # Diese Logik muss an die tatsächliche API angepasst werden
        
        state_key = "HEATER" if self.climate_type == "HEATER" else "SOLAR"
        state = self.coordinator.data.get(state_key)
        
        # Status-Werte laut API-Dokumentation:
        # 0: AUTO (not on)
        # 1: AUTO (on)
        # 2: OFF by control rule
        # 3: ON by emergency rule
        # 4: MANUAL ON
        # 5: OFF by emergency rule
        # 6: MANUAL OFF
        
        if state in [1, 3, 4]:  # Eingeschaltet (AUTO oder MANUAL)
            return HVACAction.HEATING
        else:
            return HVACAction.IDLE

    @property
    def current_temperature(self) -> Optional[float]:
        """Gib die aktuelle Wassertemperatur zurück."""
        # API gibt die Beckentemperatur als onewire1_value zurück
        return float(self.coordinator.data.get("onewire1_value", 0))

    async def async_set_temperature(self, **kwargs):
        """Setze die Zieltemperatur."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
            
        # Temperatur validieren
        if temperature < self.min_temp or temperature > self.max_temp:
            _LOGGER.warning(
                "Angeforderte Temperatur %.1f liegt außerhalb des zulässigen Bereichs (%.1f-%.1f)",
                temperature, self.min_temp, self.max_temp
            )
            return
            
        try:
            # API-Call zum Setzen der Temperatur
            # Diese Logik muss an die tatsächliche API angepasst werden
            _LOGGER.info(
                "Setze %s Zieltemperatur auf %.1f°C",
                "Heizung" if self.climate_type == "HEATER" else "Solar",
                temperature
            )
            
            # Da die API für die Temperatureinstellung nicht direkt dokumentiert ist,
            # ist dies ein vereinfachter Platzhalter
            # In der realen Implementierung würde man einen entsprechenden API-Call machen
            
            # Beispiel: Über eine noch zu implementierende API-Methode
            # key = "HEATER_TARGET_TEMP" if self.climate_type == "HEATER" else "SOLAR_TARGET_TEMP"
            # await self.coordinator.api.set_temperature(key, temperature)
            
            # Lokal aktualisieren ohne auf API-Refresh zu warten
            self._attr_target_temperature = temperature
            self.async_write_ha_state()
            
            # Daten vom Gerät neu laden
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen der Temperatur: %s", err)

    async def async_set_hvac_mode(self, hvac_mode):
        """Setze den HVAC-Modus (OFF, HEAT, AUTO)."""
        try:
            # API-Call zum Setzen des Modus
            # Diese Logik muss an die tatsächliche API angepasst werden
            
            api_key = "HEATER" if self.climate_type == "HEATER" else "SOLAR"
            action = None
            
            if hvac_mode == HVACMode.HEAT:
                action = "ON"  # MANUAL ON
            elif hvac_mode == HVACMode.OFF:
                action = "OFF"  # MANUAL OFF
            elif hvac_mode == HVACMode.AUTO:
                action = "AUTO"  # AUTO mode
            else:
                _LOGGER.warning("Nicht unterstützter HVAC-Modus: %s", hvac_mode)
                return
                
            _LOGGER.info(
                "Setze %s-Modus auf %s",
                "Heizung" if self.climate_type == "HEATER" else "Solar",
                action
            )
            
            # API-Aufruf
            await self.coordinator.api.set_switch_state(
                key=api_key,
                action=action,
                duration=0  # permanent
            )
            
            # Lokal aktualisieren ohne auf API-Refresh zu warten
            self._attr_hvac_mode = hvac_mode
            self.async_write_ha_state()
            
            # Daten vom Gerät neu laden
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen des HVAC-Modus: %s", err)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
):
    """Richte Climate-Entities basierend auf dem Config-Entry ein."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    # Prüfe, ob Heizung vorhanden ist
    if "HEATER" in coordinator.data:
        entities.append(VioletClimateEntity(coordinator, config_entry, "HEATER"))
    
    # Prüfe, ob Solarabsorber vorhanden ist
    if "SOLAR" in coordinator.data:
        entities.append(VioletClimateEntity(coordinator, config_entry, "SOLAR"))
    
    if entities:
        async_add_entities(entities)
    else:
        _LOGGER.info("Keine Heizung oder Solarabsorber in den API-Daten gefunden, Climate-Entities werden nicht hinzugefügt")
