# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from dataclasses import replace
from typing import Any, cast

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.helpers.restore_state import RestoreEntity

try:
    from homeassistant.components.number import NumberMode
except ImportError:
    NumberMode = None  # type: ignore[assignment,misc]

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from violet_poolcontroller_api.api import VioletPoolAPIError
from violet_poolcontroller_api.utils_sanitizer import InputSanitizer

from .const import (
    CONF_ACTIVE_FEATURES,
    CSI_INPUT_DEFINITIONS,
    DOMAIN,
    LSI_INPUT_DEFINITIONS,
    SETPOINT_DEFINITIONS,
)
from .device import VioletPoolDataUpdateCoordinator
from .dosing_channel import (
    CHANNEL_CHLORINE,
    CHANNEL_ELECTROLYSIS,
    active_dosing_channel,
    active_dosing_channels,
)
from .entity import VioletPoolControllerEntity
from .entity_cleanup import track_provided_entities
from .runtime_data import get_runtime_data

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platforms; HA should not throttle entity state writes
PARALLEL_UPDATES = 0

PUMP_SPEED_LEVELS = range(1, 5)


class VioletNumber(VioletPoolControllerEntity, NumberEntity):
    """Representation of a Violet Pool number entity (setpoint)."""

    entity_description: NumberEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: NumberEntityDescription,
        setpoint_config: dict,
    ) -> None:
        """
        Initialize the number entity.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            description: The entity description.
            setpoint_config: The setpoint configuration.
        """
        super().__init__(coordinator, config_entry, description)

        self._attr_native_min_value = setpoint_config["min_value"]
        self._attr_native_max_value = setpoint_config["max_value"]
        self._attr_native_step = setpoint_config["step"]

        self._setpoint_fields = setpoint_config["setpoint_fields"]
        self._indicator_fields = setpoint_config["indicator_fields"]
        self._default_value = setpoint_config["default_value"]
        self._api_key = setpoint_config["api_key"]
        # Config key holding this setpoint when the pool doses via electrolysis
        # instead of a chlorine pump (see dosing_channel.py).
        self._electrolysis_key: str | None = setpoint_config.get("electrolysis_key")
        # Set on the second entity a dual-dosing pool gets: it always reads and
        # writes the electrolysis channel, whatever the enable flags say.
        self._pinned_to_electrolysis: bool = bool(setpoint_config.get("pinned_to_electrolysis"))

        # Local cache variable for thread-safe optimistic updates
        self._optimistic_value: float | None = None

        _LOGGER.info(
            "Number entity initialized: %s (range: %.1f-%.1f, step: %.1f, parameter key: %s)",
            description.name,
            self._attr_native_min_value,
            self._attr_native_max_value,
            self._attr_native_step,
            self._api_key,
        )

    @property
    def _active_electrolysis_key(self) -> str | None:
        """Return the electrolysis config key when that channel is in charge.

        Returns:
            The ``DOSAGE_electrolysis_*`` key for this setpoint, or ``None``
            when the entity has none or the chlorine channel is active. The
            second entity of a dual-dosing pool is pinned to the electrolysis
            channel and always returns its key.
        """
        if not self._electrolysis_key:
            return None
        if self._pinned_to_electrolysis:
            return self._electrolysis_key
        if active_dosing_channel(self.coordinator.data) != CHANNEL_ELECTROLYSIS:
            return None
        return self._electrolysis_key

    @property
    def native_value(self) -> float | None:
        """
        Return the current setpoint value.

        Tries to read the value from various possible fields.
        If no value is found, returns the default value.

        Returns:
            The current setpoint or default value.
        """
        if self._optimistic_value is not None:
            return self._optimistic_value

        # Special case: pump speed — determine active level from PUMP_RPM_{i}
        # PUMP_RPM_{i} returns status codes (0-6); 1, 3 and 4 mean output ON
        # (2 = rule-blocked OFF). PUMP_RPM_0 is the PUMP_STOP output and lies
        # below this entity's min value of 1, so start at level 1.
        if self._api_key == "PUMP_SPEED":
            for level in PUMP_SPEED_LEVELS:
                rpm_val = self.get_value(f"PUMP_RPM_{level}")
                if rpm_val is not None:
                    try:
                        if int(rpm_val) in (1, 3, 4):  # status code = ON
                            _LOGGER.debug(
                                "Pump speed active: level %d (PUMP_RPM_%d=%s)",
                                level,
                                level,
                                rpm_val,
                            )
                            return float(level)
                    except (ValueError, TypeError):
                        pass

        # An electrolysis pool stores the setpoint in its own channel; the
        # chlorine keys still exist but hold a value nobody maintains.
        if (electrolysis_key := self._active_electrolysis_key) is not None:
            value = self.get_float_value(electrolysis_key)
            if value is not None:
                _LOGGER.debug(
                    "Setpoint for %s from electrolysis field '%s': %.2f",
                    self.entity_description.name,
                    electrolysis_key,
                    value,
                )
                return value

        if self._setpoint_fields:
            for field in self._setpoint_fields:
                value = self.get_float_value(field)
                if value is not None:
                    _LOGGER.debug(
                        "Setpoint for %s from field '%s': %.2f",
                        self.entity_description.name,
                        field,
                        value,
                    )
                    return value

        # Fallback to default value
        _LOGGER.debug(
            "No setpoint found for %s, using default: %.2f",
            self.entity_description.name,
            self._default_value,
        )
        try:
            return float(self._default_value)
        except (ValueError, TypeError):
            _LOGGER.debug(
                "Invalid default value for %s: %s, falling back to 0.0",
                self.entity_description.name,
                self._default_value,
            )
            return 0.0

    @property
    def available(self) -> bool:
        """
        Check if the entity is available.

        Entity is available if at least one indicator field
        is present in the coordinator data.

        Returns:
            True if available, False otherwise.
        """
        if self.coordinator.data is None:
            return False

        if self._indicator_fields:
            for field in self._indicator_fields:
                if field in self.coordinator.data:
                    _LOGGER.debug(
                        "Entity %s available (indicator '%s' found)",
                        self.entity_description.name,
                        field,
                    )
                    return super().available

            _LOGGER.debug(
                "Entity %s not available (no indicator fields found)",
                self.entity_description.name,
            )

        return super().available

    async def _delayed_refresh(self) -> None:
        """Request a coordinator refresh and clear optimistic value after
        data arrives."""
        try:
            await self._request_coordinator_refresh(
                delay=0.5,
                log_context=cast(str | None, self.entity_description.name),
            )
        finally:
            self._optimistic_value = None
            _LOGGER.debug(
                "Optimistic cache for '%s' cleared",
                self.entity_description.name,
            )
            self.async_write_ha_state()

    def _handle_refresh_error(self, task: asyncio.Task) -> None:
        """Handle errors in the refresh task."""
        try:
            if not task.cancelled():
                exc = task.exception()
                if exc is not None:
                    _LOGGER.debug(
                        "Refresh task failed for %s: %s",
                        self.entity_description.name,
                        exc,
                    )
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            pass  # Normal during HA reload

    async def async_set_native_value(self, value: float) -> None:
        """
        Set a new setpoint value.

        Uses the corresponding API method based on the setpoint type.

        Args:
            value: The new setpoint value.

        Raises:
            HomeAssistantError: If the API call fails.
        """
        if not self._api_key:
            _LOGGER.error(
                "No parameter key defined for %s - cannot set value",
                self.entity_description.name,
            )
            raise HomeAssistantError(
                translation_key="no_api_key",
                translation_domain=DOMAIN,
                translation_placeholders={"entity": str(self.entity_description.name)},
            )

        try:
            if self._api_key == "pH":
                sanitized_value = InputSanitizer.validate_ph_value(value)
            elif self._api_key == "ORP":
                sanitized_value = float(InputSanitizer.validate_orp_value(value))
            elif self._api_key == "MinChlorine":
                sanitized_value = InputSanitizer.validate_chlorine_level(value)
            else:
                # Generic float validation with range
                sanitized_value = InputSanitizer.sanitize_float(
                    value,
                    min_value=self._attr_native_min_value,
                    max_value=self._attr_native_max_value,
                    precision=1 if self._attr_native_step >= 0.1 else 2,
                )
        except (ValueError, TypeError) as err:
            _LOGGER.error(
                "Input sanitization failed for %s (value: %s): %s",
                self.entity_description.name,
                value,
                err,
            )
            raise HomeAssistantError(
                translation_key="invalid_value",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err

        if (
            sanitized_value < self._attr_native_min_value
            or sanitized_value > self._attr_native_max_value
        ):
            _LOGGER.error(
                "Value %.2f outside valid range (%.1f-%.1f) for %s",
                sanitized_value,
                self._attr_native_min_value,
                self._attr_native_max_value,
                self.entity_description.name,
            )
            raise HomeAssistantError(
                translation_key="value_out_of_range",
                translation_domain=DOMAIN,
                translation_placeholders={
                    "value": str(sanitized_value),
                    "min": str(self._attr_native_min_value),
                    "max": str(self._attr_native_max_value),
                },
            )

        try:
            unit = self.entity_description.native_unit_of_measurement or ""
            _LOGGER.info(
                "Setting %s to %.2f%s (was: %.2f%s) [sanitized: %.2f]",
                self.entity_description.name,
                value,
                unit,
                self.native_value or 0,
                unit,
                sanitized_value,
            )

            api_key = self._api_key
            electrolysis_key = self._active_electrolysis_key

            if electrolysis_key is not None:
                _LOGGER.debug(
                    "Using set_target_value for electrolysis key %s (sanitized: %.2f)",
                    electrolysis_key,
                    sanitized_value,
                )
                result = await self.device.api.set_target_value(
                    electrolysis_key,
                    int(sanitized_value) if api_key == "ORP" else sanitized_value,
                )
            elif api_key == "pH":
                _LOGGER.debug("Using set_ph_target (sanitized: %.2f)", sanitized_value)
                result = await self.device.api.set_ph_target(sanitized_value)
            elif api_key == "ORP":
                _LOGGER.debug("Using set_orp_target (sanitized: %.1f)", sanitized_value)
                result = await self.device.api.set_orp_target(sanitized_value)
            elif api_key == "MinChlorine":
                _LOGGER.debug("Using set_min_chlorine_level (sanitized: %.2f)", sanitized_value)
                result = await self.device.api.set_min_chlorine_level(sanitized_value)
            elif api_key == "PUMP_SPEED":
                _LOGGER.debug("Using set_pump_speed (sanitized: %d)", int(sanitized_value))
                result = await self.device.api.set_pump_speed(int(sanitized_value))
            elif api_key in ("HEATER_TARGET_TEMP", "SOLAR_TARGET_TEMP"):
                _LOGGER.debug(
                    "Using set_device_temperature for %s (sanitized: %.1f)",
                    api_key.replace("_TARGET_TEMP", ""),
                    sanitized_value,
                )
                climate_key = api_key.replace("_TARGET_TEMP", "")
                result = await self.device.api.set_device_temperature(climate_key, sanitized_value)
            elif api_key.endswith("_TOTAL_CAN_AMOUNT_ML"):
                _LOGGER.debug(
                    "Using set_dosing_parameters for %s (sanitized: %.0f ml)",
                    api_key,
                    sanitized_value,
                )
                result = await self.device.api.set_dosing_parameters(
                    {api_key: int(sanitized_value)}
                )
            else:
                _LOGGER.debug(
                    "Using set_target_value for %s (sanitized: %.2f)",
                    api_key,
                    sanitized_value,
                )
                result = await self.device.api.set_target_value(api_key, sanitized_value)

            if result.get("success") is True:
                _LOGGER.info(
                    "%s set to %.2f%s successfully",
                    self.entity_description.name,
                    value,
                    unit,
                )

                self._optimistic_value = sanitized_value
                _LOGGER.debug(
                    "Optimistic cache for '%s' set to %.2f",
                    self.entity_description.name,
                    value,
                )

                self.async_write_ha_state()

                task = asyncio.create_task(self._delayed_refresh())
                task.add_done_callback(self._handle_refresh_error)

            else:
                error_msg = result.get("response", result)
                _LOGGER.warning(
                    "Setting %s may have failed: %s",
                    self.entity_description.name,
                    error_msg,
                )
                raise HomeAssistantError(
                    translation_key="failed_to_set_value",
                    translation_domain=DOMAIN,
                    translation_placeholders={"detail": str(error_msg)},
                )

        except VioletPoolAPIError as err:
            _LOGGER.error(
                "API error setting %s to %.2f: %s",
                self.entity_description.name,
                value,
                err,
            )
            raise HomeAssistantError(
                translation_key="api_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err

        except HomeAssistantError:
            raise

        except Exception as err:
            _LOGGER.exception(
                "Unexpected error setting %s to %.2f: %s",
                self.entity_description.name,
                value,
                err,
            )
            raise HomeAssistantError(
                translation_key="unexpected_error",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err


class VioletSaturationIndexInputNumber(VioletPoolControllerEntity, NumberEntity, RestoreEntity):
    """Local number entity used as an input for saturation index calculators."""

    entity_description: NumberEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: NumberEntityDescription,
        input_config: dict,
    ) -> None:
        """Initialize the local saturation index input number."""
        super().__init__(coordinator, config_entry, description)
        self._input_key = str(input_config["key"])
        self._store_key = str(input_config.get("store_key", "lsi_inputs"))
        default_value = input_config.get("default_value")
        self._default_value = float(default_value) if default_value is not None else None
        self._attr_native_min_value = input_config["min_value"]
        self._attr_native_max_value = input_config["max_value"]
        self._attr_native_step = input_config["step"]
        self._attr_entity_category = input_config.get("entity_category")
        self._value: float | None = None

    async def async_added_to_hass(self) -> None:
        """Restore the last input value and publish it to the calculator value store."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in {"unknown", "unavailable"}:
            try:
                self._value = float(last_state.state)
            except (ValueError, TypeError):
                self._value = None
        if self._value is None:
            self._value = self._default_value
        self._update_saturation_index_store(self._value)

    @property
    def native_value(self) -> float | None:
        """Return the current local input value."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Set the local input value without writing to the controller API."""
        try:
            new_value = float(value)
        except (ValueError, TypeError) as err:
            raise HomeAssistantError(
                translation_key="invalid_value",
                translation_domain=DOMAIN,
                translation_placeholders={"detail": str(err)},
            ) from err

        if new_value < self._attr_native_min_value or new_value > self._attr_native_max_value:
            raise HomeAssistantError(
                translation_key="value_out_of_range",
                translation_domain=DOMAIN,
                translation_placeholders={
                    "value": str(new_value),
                    "min": str(self._attr_native_min_value),
                    "max": str(self._attr_native_max_value),
                },
            )

        self._value = new_value
        self._update_saturation_index_store(new_value)
        self.async_write_ha_state()

    def _update_saturation_index_store(self, value: float | None) -> None:
        """Store the input value for the matching result sensor."""
        runtime_data = get_runtime_data(self.config_entry)
        if runtime_data is None:
            return

        entry_store = runtime_data.calculator_inputs.setdefault(self._store_key, {})
        entry_store[self._input_key] = value
        if hasattr(self, "hass"):
            async_dispatcher_send(
                self.hass,
                f"{DOMAIN}_{self.config_entry.entry_id}_{self._store_key}_updated",
            )


def electrolysis_twin(
    setpoint_config: dict,
    data: Mapping[str, Any] | None,
) -> dict | None:
    """Return the second setpoint config a dual-dosing pool needs.

    A pool can run an electrolysis cell and a chlorine pump at the same time.
    The controller then keeps one setpoint per channel, and a single entity
    would leave the electrolysis one unreachable - nothing in Home Assistant
    would read or write it.

    Args:
        setpoint_config: The setpoint definition the primary entity was built
            from.
        data: The merged coordinator data.

    Returns:
        A copy of the setpoint config pinned to the electrolysis channel, or
        ``None`` when this setpoint has no electrolysis counterpart or only one
        channel is enabled.
    """
    electrolysis_key = setpoint_config.get("electrolysis_key")
    if not electrolysis_key:
        return None
    if set(active_dosing_channels(data)) != {CHANNEL_CHLORINE, CHANNEL_ELECTROLYSIS}:
        return None
    return {
        **setpoint_config,
        "key": f"{setpoint_config['key']}_electrolysis",
        "name": f"{setpoint_config['name']} (Electrolysis)",
        "translation_key": f"{setpoint_config['translation_key']}_electrolysis",
        "pinned_to_electrolysis": True,
    }


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up number entities for the config entry.

    Creates number entities for all configured setpoints that are
    included in the active features and whose indicator fields are available.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry.
        async_add_entities: Callback to add entities.
    """
    coordinator = config_entry.runtime_data.coordinator

    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )

    _LOGGER.debug(
        "Setting up number entities for '%s' with active features: %s",
        config_entry.title,
        ", ".join(active_features),
    )

    if coordinator.data is None:
        _LOGGER.warning(
            "Coordinator data is None for '%s'. Number entities will not be created.",
            config_entry.title,
        )
        track_provided_entities(hass, config_entry, Platform.NUMBER, [])
        return

    entities: list[NumberEntity] = []

    if "ph_control" in active_features:
        for store_key, input_definitions in (
            ("lsi_inputs", LSI_INPUT_DEFINITIONS),
            ("csi_inputs", CSI_INPUT_DEFINITIONS),
        ):
            input_store = config_entry.runtime_data.calculator_inputs.setdefault(store_key, {})
            for input_config in input_definitions:
                input_config = {**input_config, "store_key": store_key}
                input_store.setdefault(str(input_config["key"]), input_config.get("default_value"))
                description = NumberEntityDescription(
                    key=str(input_config["key"]),
                    name=str(input_config["name"]),
                    icon=input_config.get("icon"),  # type: ignore[arg-type]
                    native_unit_of_measurement=input_config.get(  # type: ignore[arg-type]
                        "unit_of_measurement"
                    ),
                    device_class=input_config.get("device_class"),  # type: ignore[arg-type]
                    entity_category=input_config.get("entity_category"),  # type: ignore[arg-type]
                    translation_key=cast(str | None, input_config.get("translation_key")),
                    mode=cast(
                        "NumberMode | None",
                        NumberMode.BOX if NumberMode is not None else "box",
                    ),
                )
                entities.append(
                    VioletSaturationIndexInputNumber(
                        coordinator, config_entry, description, input_config
                    )
                )

    for setpoint_config in SETPOINT_DEFINITIONS:
        setpoint_name = str(setpoint_config["name"])
        setpoint_key = str(setpoint_config["key"])
        feature_id = setpoint_config["feature_id"]

        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Skipping number '%s': feature '%s' not active",
                setpoint_name,
                feature_id,
            )
            continue

        indicator_fields = setpoint_config.get("indicator_fields", [])
        if isinstance(indicator_fields, list):
            has_indicators = any(field in coordinator.data for field in indicator_fields)

            if not has_indicators:
                _LOGGER.debug(
                    "Skipping number '%s': no indicator fields available (%s)",
                    setpoint_name,
                    ", ".join(str(f) for f in indicator_fields),
                )
                continue

        description = NumberEntityDescription(
            key=setpoint_key,
            name=setpoint_name,
            icon=setpoint_config.get("icon"),  # type: ignore[arg-type]
            native_unit_of_measurement=setpoint_config.get("unit_of_measurement"),  # type: ignore[arg-type]
            device_class=setpoint_config.get("device_class"),  # type: ignore[arg-type]
            entity_category=setpoint_config.get("entity_category"),  # type: ignore[arg-type]
            entity_registry_enabled_default=cast(
                bool, setpoint_config.get("entity_registry_enabled_default", True)
            ),
            translation_key=cast(str | None, setpoint_config.get("translation_key")),
            mode=cast(
                "NumberMode | None",
                NumberMode.BOX if NumberMode is not None else "box",
            ),
        )

        _LOGGER.debug("Creating number entity for '%s' (key: %s)", setpoint_name, setpoint_key)

        entities.append(VioletNumber(coordinator, config_entry, description, setpoint_config))

        twin = electrolysis_twin(setpoint_config, coordinator.data)
        if twin is not None:
            entities.append(
                VioletNumber(
                    coordinator,
                    config_entry,
                    replace(
                        description,
                        key=str(twin["key"]),
                        name=str(twin["name"]),
                        translation_key=str(twin["translation_key"]),
                    ),
                    twin,
                )
            )
            _LOGGER.debug(
                "Both dosing channels active - added '%s' for %s",
                twin["name"],
                twin["electrolysis_key"],
            )

    track_provided_entities(hass, config_entry, Platform.NUMBER, entities)

    if entities:
        async_add_entities(entities)
        entity_names = [str(e.entity_description.name) for e in entities]
        _LOGGER.info(
            "%d number entities added for '%s': %s",
            len(entities),
            config_entry.title,
            ", ".join(entity_names),
        )
    else:
        _LOGGER.info("No number entities set up for '%s'", config_entry.title)
