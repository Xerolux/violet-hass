
"""Number platform for Violet Pool Controller."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import VioletPoolAPIError
from .const import CONF_ACTIVE_FEATURES, DOMAIN, SETPOINT_DEFINITIONS
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity
from .utils_sanitizer import InputSanitizer

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platforms; HA should not throttle entity state writes
PARALLEL_UPDATES = 0


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

        # Local cache variable for thread-safe optimistic updates
        self._optimistic_value: float | None = None

        _LOGGER.info(
            "Number entity initialized: %s (range: %.1f-%.1f, step: %.1f, API key: %s)",
            description.name,
            self._attr_native_min_value,
            self._attr_native_max_value,
            self._attr_native_step,
            self._api_key,
        )

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
        # PUMP_RPM_{i} returns status codes (0-6); values 1,2,3,4 = output ON
        if self._api_key == "PUMP_SPEED":
            for level in range(1, 4):  # levels 1 (Eco), 2 (Normal), 3 (Boost)
                rpm_val = self.get_value(f"PUMP_RPM_{level}")
                if rpm_val is not None:
                    try:
                        if int(rpm_val) in (1, 2, 3, 4):  # status code = ON
                            _LOGGER.debug(
                                "Pump speed active: level %d (PUMP_RPM_%d=%s)",
                                level,
                                level,
                                rpm_val,
                            )
                            return float(level)
                    except (ValueError, TypeError):
                        pass

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
        return float(self._default_value)

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
                "No API key defined for %s - cannot set value",
                self.entity_description.name,
            )
            raise HomeAssistantError(
                f"No API key defined for {self.entity_description.name}"
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
            raise HomeAssistantError(f"Invalid value: {err}") from err

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
                f"Value {sanitized_value} outside valid range "
                f"({self._attr_native_min_value}-{self._attr_native_max_value})"
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

            if api_key == "pH":
                _LOGGER.debug("Using set_ph_target (sanitized: %.2f)", sanitized_value)
                result = await self.device.api.set_ph_target(sanitized_value)
            elif api_key == "ORP":
                _LOGGER.debug("Using set_orp_target (sanitized: %.1f)", sanitized_value)
                result = await self.device.api.set_orp_target(sanitized_value)
            elif api_key == "MinChlorine":
                _LOGGER.debug(
                    "Using set_min_chlorine_level (sanitized: %.2f)", sanitized_value
                )
                result = await self.device.api.set_min_chlorine_level(sanitized_value)
            elif api_key == "PUMP_SPEED":
                _LOGGER.debug(
                    "Using set_pump_speed (sanitized: %d)", int(sanitized_value)
                )
                result = await self.device.api.set_pump_speed(int(sanitized_value))
            elif api_key in ("HEATER_TARGET_TEMP", "SOLAR_TARGET_TEMP"):
                _LOGGER.debug(
                    "Using set_device_temperature for %s (sanitized: %.1f)",
                    api_key.replace("_TARGET_TEMP", ""),
                    sanitized_value,
                )
                climate_key = api_key.replace("_TARGET_TEMP", "")
                result = await self.device.api.set_device_temperature(
                    climate_key, sanitized_value
                )
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
                result = await self.device.api.set_target_value(
                    api_key, sanitized_value
                )

            if result.get("success") is True:
                _LOGGER.info(
                    "%s set to %.2f%s successfully",
                    self.entity_description.name,
                    value,
                    unit,
                )

                self._optimistic_value = value
                _LOGGER.debug(
                    "Optimistic cache for '%s' set to %.2f",
                    self.entity_description.name,
                    value,
                )

                self.async_write_ha_state()

                try:
                    await self.coordinator.async_request_refresh()
                finally:
                    self._optimistic_value = None
                    _LOGGER.debug(
                        "Optimistic cache for '%s' cleared",
                        self.entity_description.name,
                    )
            else:
                error_msg = result.get("response", result)
                _LOGGER.warning(
                    "Setting %s may have failed: %s",
                    self.entity_description.name,
                    error_msg,
                )
                raise HomeAssistantError(f"Failed to set value: {error_msg}")

        except VioletPoolAPIError as err:
            _LOGGER.error(
                "API error setting %s to %.2f: %s",
                self.entity_description.name,
                value,
                err,
            )
            raise HomeAssistantError(f"Failed to set value: {err}") from err

        except Exception as err:
            _LOGGER.exception(
                "Unexpected error setting %s to %.2f: %s",
                self.entity_description.name,
                value,
                err,
            )
            raise HomeAssistantError(f"Unexpected error: {err}") from err


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
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

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
            "Coordinator data is None for '%s'. "
            "Number entities will not be created.",
            config_entry.title,
        )
        return

    entities: list[NumberEntity] = []

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
            has_indicators = any(
                field in coordinator.data for field in indicator_fields
            )

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
        )

        _LOGGER.debug(
            "Creating number entity for '%s' (key: %s)", setpoint_name, setpoint_key
        )

        entities.append(
            VioletNumber(coordinator, config_entry, description, setpoint_config)
        )

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
