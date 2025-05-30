"""Number Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Final, List
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
    NumberDeviceClass,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.exceptions import HomeAssistantError # Import HomeAssistantError

from .const import DOMAIN, CONF_ACTIVE_FEATURES, API_SET_TARGET_VALUES, API_SET_DOSING_PARAMETERS # Import API endpoint constants
from .api import VioletPoolAPIError, VioletPoolConnectionError, VioletPoolCommandError # Import API errors
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SETPOINT_DEFINITIONS: Final = [
    {
        "key": "ph_setpoint",
        "name": "pH Sollwert",
        "min_value": 6.8,
        "max_value": 7.8,
        "step": 0.1,
        "icon": "mdi:flask",
        "api_key": "pH",
        "feature_id": "ph_control",
        "parameter": "pH Sollwert",
        "unit_of_measurement": "pH",
        "api_endpoint": "/set_target_value",
        "device_class": NumberDeviceClass.PH,
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["pH_SETPOINT", "pH_TARGET", "TARGET_PH"],
        "indicator_fields": ["pH_value", "DOS_4_PHM", "DOS_5_PHP"],
        "default_value": 7.2,
    },
    # Weitere Definitionen unverändert ...
]

@dataclass
class VioletNumberEntityDescription(NumberEntityDescription):
    """Beschreibung der Violet Pool Number-Entities."""
    api_key: Optional[str] = None # This is the target_type or parameter_name for the API
    api_endpoint: Optional[str] = None # e.g. API_SET_TARGET_VALUES or API_SET_DOSING_PARAMETERS
    parameter: Optional[str] = None # Original field, seems redundant if api_key is used as API parameter name
    feature_id: Optional[str] = None
    dosing_type: Optional[str] = None # For API_SET_DOSING_PARAMETERS

class VioletNumberEntity(VioletPoolControllerEntity, NumberEntity):
    """Repräsentiert einen Sollwert im Violet Pool Controller."""
    entity_description: VioletNumberEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        definition: Dict[str, Any],
    ):
        """Initialisiere die Number-Entity."""
        self._definition = definition
        description = VioletNumberEntityDescription(
            key=definition["key"],
            name=definition["name"],
            icon=definition.get("icon"),
            device_class=definition.get("device_class"),
            native_unit_of_measurement=definition.get("unit_of_measurement"),
            entity_category=definition.get("entity_category"),
            api_key=definition.get("api_key"), # This will be the target_type or parameter_name
            api_endpoint=definition.get("api_endpoint"),
            parameter=definition.get("parameter"), # Potentially for display name or context, if different from api_key
            feature_id=definition.get("feature_id"),
            dosing_type=definition.get("dosing_type"), # Get dosing_type
        )
        super().__init__(coordinator, config_entry, description)
        self._attr_native_min_value = definition["min_value"]
        self._attr_native_max_value = definition["max_value"]
        self._attr_native_step = definition["step"]
        self._attr_mode = NumberMode.AUTO
        self._attr_native_value = self._get_current_value()
        unit = self.entity_description.native_unit_of_measurement or ""
        _LOGGER.debug(
            "Number-Entity für %s initialisiert mit Wert: %s %s",
            definition["name"],
            self._attr_native_value,
            unit
        )

    def _update_from_coordinator(self) -> None:
        """Aktualisiert den Zustand basierend auf Coordinator-Daten."""
        old_value = self._attr_native_value
        self._attr_native_value = self._get_current_value()
        if old_value != self._attr_native_value:
            _LOGGER.debug(
                "Wert für %s aktualisiert: %s -> %s",
                self.name,
                old_value,
                self._attr_native_value
            )

    # Removed _update_from_coordinator method

    def _get_current_value(self) -> Optional[float]:
        """Ermittle den aktuellen Wert aus den Coordinator-Daten."""
        setpoint_fields = self._definition.get("setpoint_fields", [])
        for field in setpoint_fields:
            value = self.get_float_value(field, None)
            if value is not None:
                return value
        default = self._definition.get("default_value", self._attr_native_min_value)
        _LOGGER.debug("Verwende Standardwert für %s: %s", self.name, default)
        return default

    async def async_set_native_value(self, value: float) -> None:
        """Setze den neuen Wert im Gerät."""
        try:
            api_key_for_call = self.entity_description.api_key or self.entity_description.key # Fallback to key if api_key is not set
            current_api_endpoint = self.entity_description.api_endpoint

            if not api_key_for_call:
                _LOGGER.error("API-Key (target_type/parameter_name) fehlt für Number-Entity %s", self.entity_id)
                return
            if not current_api_endpoint:
                _LOGGER.error("API-Endpunkt fehlt für Number-Entity %s", self.entity_id)
                return

            # Round value according to step
            if self._attr_native_step and self._attr_native_step > 0:
                value = round(value / self._attr_native_step) * self._attr_native_step
                # Ensure precision for float steps (e.g. 0.1)
                if isinstance(self._attr_native_step, float):
                    num_decimals = str(self._attr_native_step)[::-1].find('.')
                    if num_decimals > 0 : # Check if decimal part exists
                         value = round(value, num_decimals)


            _LOGGER.info(
                "Setze Wert für %s (API Key: %s) auf %s%s via Endpoint %s",
                self.name, api_key_for_call, value,
                self.entity_description.native_unit_of_measurement or "",
                current_api_endpoint
            )

            result: Optional[Dict[str, Any]] = None
            if current_api_endpoint == API_SET_TARGET_VALUES:
                result = await self.device.api.set_target_value(
                    target_type=api_key_for_call, # api_key from description is used as target_type
                    value=value
                )
            elif current_api_endpoint == API_SET_DOSING_PARAMETERS:
                dosing_type = self.entity_description.dosing_type
                if not dosing_type:
                    _LOGGER.error(
                        "Dosing_type fehlt in der Entity-Beschreibung für %s bei Verwendung von API_SET_DOSING_PARAMETERS.",
                        self.entity_id
                    )
                    return
                result = await self.device.api.set_dosing_parameters(
                    dosing_type=dosing_type,
                    parameter_name=api_key_for_call, # api_key from description is used as parameter_name
                    value=value
                )
            else:
                _LOGGER.error(
                    "Nicht unterstützter API-Endpunkt '%s' für Number-Entity %s",
                    current_api_endpoint, self.entity_id
                )
                return

            if result and result.get("success", True): # Assume success if not explicitly false
                _LOGGER.debug("Wert erfolgreich gesetzt für %s: %s = %s", self.name, api_key_for_call, value)
            else:
                _LOGGER.warning("Wert setzen für %s (%s) möglicherweise fehlgeschlagen: %s", self.name, api_key_for_call, result.get("response", result) if result else "Keine Antwort")
            
            self._attr_native_value = value # Optimistic update
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
        except (VioletPoolConnectionError, VioletPoolCommandError) as err:
            _LOGGER.error(f"API-Fehler beim Setzen des Werts für {self.name} ({api_key_for_call}): {err}")
            raise HomeAssistantError(f"Setzen des Werts für {self.name} fehlgeschlagen: {err}") from err
        except Exception as err: # Catch any other unexpected errors
            _LOGGER.exception(f"Unerwarteter Fehler beim Setzen des Werts für {self.name} ({api_key_for_call}): {err}")
            raise HomeAssistantError(f"Unerwarteter Fehler beim Setzen des Werts für {self.name}: {err}") from err

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Number-Entities basierend auf dem Config-Entry ein."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities: List[VioletNumberEntity] = []
    for definition in SETPOINT_DEFINITIONS:
        feature_id = definition.get("feature_id")
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Überspringe %s: Feature %s nicht aktiv",
                definition["name"],
                feature_id
            )
            continue
        indicator_fields = definition.get("indicator_fields", [])
        if not any(field in coordinator.data for field in indicator_fields):
            _LOGGER.debug(
                "Überspringe %s: Keine Indikator-Daten",
                definition["name"]
            )
            continue
        entities.append(VioletNumberEntity(coordinator, config_entry, definition))
        _LOGGER.debug("Number-Entity für %s hinzugefügt", definition["name"])
    if entities:
        _LOGGER.info("%d Number-Entities hinzugefügt", len(entities))
        async_add_entities(entities)
    else:
        _LOGGER.info("Keine passenden Entities gefunden")
