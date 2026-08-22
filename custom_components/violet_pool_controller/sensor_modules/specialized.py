# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

from __future__ import annotations

import logging
import math
import re
from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory

from ..const import (
    DIAGNOSTIC_PROBLEM_KEYS,
    DOMAIN,
    DOSING_STATE_DESCRIPTIONS,
    OMNI_FAULTY_STATES,
    SATURATION_INDEX_SOURCE_FIELDS,
)
from ..device import VioletPoolDataUpdateCoordinator
from ..entity import VioletPoolControllerEntity
from ..error_codes import get_error_info
from ..runtime_data import get_runtime_data
from .generic import VioletSensor

_LOGGER = logging.getLogger(__name__)

# Constant for flow rate sensor
_FLOW_RATE_SOURCE_KEYS = {"ADC3_value", "IMP2_value"}


class VioletErrorCodeSensor(VioletSensor):
    """A specialized sensor that resolves error codes to descriptive text."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        value_key: str,
    ) -> None:
        """Initializes the error code sensor.

        Args:
            coordinator: The data update coordinator.
            config_entry: The configuration entry.
            value_key: The key in the coordinator data that holds the error code.
        """
        description = SensorEntityDescription(
            key=value_key,
            translation_key="last_error_code",
            name="Last Error Code",
            icon="mdi:alert-circle",
            entity_category=None,
            entity_registry_enabled_default=True,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> str | None:
        """Return the descriptive subject of the error code."""
        if self.coordinator.data is None:
            return None

        code = str(self.coordinator.data.get(self.entity_description.key, "")).strip()
        return get_error_info(code)["subject"] if code else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed information about the error code as attributes."""
        if self.coordinator.data is None:
            return {}

        code = str(self.coordinator.data.get(self.entity_description.key, "")).strip()
        if not code:
            return {}
        info = get_error_info(code)
        return {
            "code": code,
            "type": info.get("type"),
            "severity": info.get("severity"),
            "description": info.get("description"),
        }


class VioletHealthSensor(VioletPoolControllerEntity, SensorEntity):
    """Aggregate pool health sensor — one-glance status of every problem source.

    Native state (filtered by translation):
        ``ok``       – no problems detected, controller reachable.
        ``warning``  – at least one non-critical problem (e.g. dry-run
                       protection triggered, OmniTronic valve blocked).
        ``error``    – hardware issue, active controller error code, or
                       any binary-sensor problem flag is on.
        ``offline``  – coordinator data missing (controller unreachable).

    The sensor aggregates every key listed in
    :data:`~custom_components.violet_pool_controller.const.DIAGNOSTIC_PROBLEM_KEYS`
    plus the OmniTronic valve state and the controller's ``last_error_id``
    field.  Active items are exposed via ``extra_state_attributes`` so users
    can see at a glance which subsystem is reporting the issue.
    """

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the health sensor."""
        description = SensorEntityDescription(
            key="pool_health",
            translation_key="pool_health",
            name="Pool Health",
            icon="mdi:heart-pulse",
            entity_category=None,  # prominent — not in the diagnostic drawer
            entity_registry_enabled_default=True,
        )
        super().__init__(coordinator, config_entry, description)

    # ------------------------------------------------------------------
    # State aggregation
    # ------------------------------------------------------------------

    def _collect_problems(self) -> tuple[list[str], list[str], list[str]]:
        """Return (errors, warnings, info) lists of human-readable labels."""
        data: Mapping[str, Any] = self.coordinator.data or {}
        errors: list[str] = []
        warnings: list[str] = []
        info: list[str] = []

        for key, spec in DIAGNOSTIC_PROBLEM_KEYS.items():
            if key not in data:
                continue
            value = data.get(key)
            label = spec["label"]
            kind = spec["type"]

            if kind == "hardware":
                # Hardware-module sensor: True = present, False = missing.
                # Treat False as an ERROR (the module is physically gone).
                if not self._is_truthy(value):
                    errors.append(f"{label} missing")
            elif kind == "problem" and self._is_truthy(value):
                # Binary PROBLEM sensor: True = problem.
                errors.append(label)

        # OmniTronic multi-port valve state (string).
        omni_state = str(data.get("BACKWASH_OMNI_STATE", "")).upper().strip()
        if omni_state and any(fault in omni_state for fault in OMNI_FAULTY_STATES):
            errors.append(f"OmniTronic valve: {omni_state}")
        elif omni_state == "BLOCKED_BY_OMNI_MOVING":
            info.append("OmniTronic valve moving")

        # OmniTronic motion flag (YES/NO).
        if str(data.get("BACKWASH_OMNI_MOVING", "")).upper() == "YES":
            info.append("OmniTronic valve moving")

        # Controller-side active errors (ERROR, ERROR_0..9, LAST_ERROR).
        checked_error_codes: list[str] = []
        for key in sorted(k for k in data if re.match(r"^ERROR(_\d+)?$", k)):
            code = str(data.get(key, "")).strip()
            if code and code not in ("0", "0000", "NONE") and code not in checked_error_codes:
                checked_error_codes.append(code)

        last_error = str(data.get("LAST_ERROR", "")).strip()
        if last_error and last_error not in ("0", "0000", "NONE") and last_error not in checked_error_codes:
            checked_error_codes.append(last_error)

        for code in checked_error_codes:
            info_err = get_error_info(code)
            severity = info_err.get("severity", "").upper()
            label = info_err.get("subject") or f"Error {code}"
            if severity in ("ALARM", "ERROR", "CRITICAL"):
                errors.append(f"Controller error {code}: {label}")
            elif severity == "WARNING":
                warnings.append(f"Controller warning {code}: {label}")
            else:
                info.append(f"Controller notice {code}: {label}")

        # Overflow refill/dryrun states (strings like "OFF" / "ON").
        overflow_state = str(data.get("OVERFLOW_REFILL_STATE", "")).upper()
        if overflow_state == "ON":
            info.append("Overflow refill active")

        return errors, warnings, info

    @staticmethod
    def _is_truthy(value: Any) -> bool:  # noqa: ANN401
        """Best-effort boolean conversion for problem/hardware flags."""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        text = str(value).strip().upper()
        return text in ("1", "YES", "ON", "TRUE", "OK", "PRESENT")

    # ------------------------------------------------------------------
    # Entity interface
    # ------------------------------------------------------------------

    @property
    def native_value(self) -> str:
        """Return the aggregate health state: ok / warning / error / offline."""
        if self.coordinator.data is None or not self.coordinator.last_update_success:
            return "offline"

        errors, warnings, _ = self._collect_problems()
        if errors:
            return "error"
        if warnings:
            return "warning"
        return "ok"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed lists of active problems and warnings."""
        if self.coordinator.data is None:
            return {"state": "offline"}

        errors, warnings, info = self._collect_problems()
        return {
            "error_count": len(errors),
            "warning_count": len(warnings),
            "info_count": len(info),
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "checked_sensors": sorted(DIAGNOSTIC_PROBLEM_KEYS.keys()),
        }


class VioletActiveErrorsSensor(VioletPoolControllerEntity, SensorEntity):
    """Sensor that displays all active error codes as human-readable names."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the active errors sensor."""
        description = SensorEntityDescription(
            key="active_errors",
            translation_key="active_errors",
            name="Active Errors",
            icon="mdi:alert-multiple",
            entity_category=None,
            entity_registry_enabled_default=True,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> str:
        """Return all active error codes as comma-separated human-readable names."""
        if self.coordinator.data is None:
            return "No Error"

        # Collect all error codes from the data
        error_codes = []

        error_keys = [k for k in self.coordinator.data if re.match(r"^ERROR(_\d+)?$", k)]
        for key in sorted(error_keys):
            code = str(self.coordinator.data.get(key, "")).strip()
            if code and code != "0" and code != "0000":
                error_codes.append(code)

        # Also check LAST_ERROR if it's different
        last_error = str(self.coordinator.data.get("LAST_ERROR", "")).strip()
        if last_error and last_error != "0" and last_error not in error_codes:
            error_codes.append(last_error)

        if not error_codes:
            return "No Error"

        # Convert codes to names
        error_names = []
        for code in error_codes:
            info = get_error_info(code)
            error_names.append(f"{info['subject']} ({code})")

        return " | ".join(error_names)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed information about all active errors."""
        if self.coordinator.data is None:
            return {}

        # Collect all error codes
        error_codes = []
        for i in range(10):
            key = f"ERROR_{i}" if i > 0 else "ERROR"
            if key in self.coordinator.data:
                code = str(self.coordinator.data.get(key, "")).strip()
                if code and code != "0" and code != "0000":
                    error_codes.append(code)

        last_error = str(self.coordinator.data.get("LAST_ERROR", "")).strip()
        if last_error and last_error != "0" and last_error not in error_codes:
            error_codes.append(last_error)

        if not error_codes:
            return {"error_count": 0, "errors": []}

        # Build detailed error list
        errors = []
        for code in error_codes:
            info = get_error_info(code)
            errors.append(
                {
                    "code": code,
                    "name": info["subject"],
                    "type": info.get("type"),
                    "severity": info.get("severity"),
                    "description": info.get("description"),
                }
            )

        return {
            "error_count": len(errors),
            "errors": errors,
        }


class VioletDosingStateSensor(VioletPoolControllerEntity, SensorEntity):
    """Sensor for dosing system state arrays (DOS_*_STATE) and composite states."""

    # Shared label table; see const.DOSING_STATE_DESCRIPTIONS for full source.
    _DETAIL_DESCRIPTIONS: dict[str, str] = DOSING_STATE_DESCRIPTIONS

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
        *,
        translation_key: str | None = None,
    ) -> None:
        """Initialize the dosing state sensor."""
        description = SensorEntityDescription(
            key=key,
            name=name,
            icon=icon,
            entity_category=EntityCategory.DIAGNOSTIC,
            translation_key=translation_key,
            entity_registry_enabled_default=False,
        )
        super().__init__(coordinator, config_entry, description)

    def _translate_detail(self, code: str) -> str:
        """Translate a detail code to English, fallback to title-cased string."""
        return self._DETAIL_DESCRIPTIONS.get(code, code.replace("_", " ").title())

    @property
    def native_value(self) -> str | None:
        """Return the dosing state as comma-separated English string."""
        raw_value = self.get_value(self.entity_description.key)

        # Handle array values (DOS_*_STATE sensors)
        if isinstance(raw_value, list):
            if not raw_value:
                return "OK"
            return ", ".join(self._translate_detail(str(item)) for item in raw_value)

        # Handle pipe-separated strings (PUMPSTATE, HEATERSTATE, SOLARSTATE)
        if isinstance(raw_value, str) and "|" in raw_value:
            parts = raw_value.split("|", 1)
            if len(parts) == 2:
                return self._translate_detail(parts[1])
            return raw_value

        # Handle string values
        if isinstance(raw_value, str):
            return raw_value if raw_value else "OK"

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        raw_value = self.get_value(self.entity_description.key)

        attributes: dict[str, Any] = {}

        # Array-based sensors (DOS_*_STATE)
        if isinstance(raw_value, list):
            attributes["state_count"] = len(raw_value)
            attributes["states_list"] = raw_value
            attributes["has_issues"] = len(raw_value) > 0

        # Pipe-separated sensors (PUMPSTATE, HEATERSTATE, SOLARSTATE)
        elif isinstance(raw_value, str) and "|" in raw_value:
            parts = raw_value.split("|", 1)
            if len(parts) == 2:
                state_num, detail = parts
                attributes["numeric_state"] = state_num
                attributes["detail_code"] = detail
                attributes["detail_readable"] = self._translate_detail(detail)
                attributes["raw_value"] = raw_value

        return attributes


class VioletFlowRateSensor(VioletPoolControllerEntity, SensorEntity):
    """A specialized sensor for flow rate that prioritizes ADC3 over IMP2."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initializes the flow rate sensor."""
        description = SensorEntityDescription(
            key="flow_rate_adc3_priority",
            translation_key="flow_rate",
            name="Flow Rate",
            icon="mdi:pump",
            native_unit_of_measurement="m³/h",
            device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
            state_class=SensorStateClass.MEASUREMENT,
        )
        super().__init__(coordinator, config_entry, description)

    @property
    def native_value(self) -> float | None:
        """Return the flow rate, prioritizing the ADC3 value."""
        if self.coordinator.data is None:
            return None

        for key in ["ADC3_value", "IMP2_value"]:
            raw_value = self.coordinator.data.get(key)
            if raw_value is not None:
                try:
                    return round(float(raw_value), 2)
                except (ValueError, TypeError):
                    continue
        return None

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the raw source values for debugging purposes."""
        if self.coordinator.data is None:
            return {"data_source": "None"}

        adc3 = self.coordinator.data.get("ADC3_value", "N/A")
        imp2 = self.coordinator.data.get("IMP2_value", "N/A")
        source = "ADC3" if adc3 != "N/A" else "IMP2" if imp2 != "N/A" else "None"
        return {
            "adc3_raw_value": str(adc3),
            "imp2_raw_value": str(imp2),
            "data_source": source,
        }

    @property
    def available(self) -> bool:
        """The sensor is available if either of its data sources is present."""
        if self.coordinator.data is None:
            return False

        return super().available and any(
            self.coordinator.data.get(key) is not None for key in _FLOW_RATE_SOURCE_KEYS
        )


def _as_optional_float(value: object) -> float | None:
    """Convert a value to float while treating missing HA states as absent."""
    if value in (None, "", "unknown", "unavailable", "N/A"):
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None


def _interpret_saturation_index(value: float | None) -> tuple[str, str, bool]:
    """Return interpretation, warning level, and warning flag for LSI/CSI values."""
    if value is None:
        return "unknown", "unknown", False
    if value < -0.5:
        return "strongly corrosive / aggressive", "warning", True
    if value < 0:
        return "slightly corrosive", "notice", False
    if value <= 0.3:
        return "balanced", "ok", False
    if value <= 0.5:
        return "slight scaling tendency", "notice", False
    return "strong scaling tendency", "warning", True


class VioletSaturationIndexSensor(VioletPoolControllerEntity, SensorEntity):
    """Base sensor for calculating pool saturation indexes."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        *,
        key: str,
        translation_key: str,
        name: str,
        store_key: str,
        input_prefix: str,
    ) -> None:
        """Initialize the saturation index sensor."""
        self.config_entry = config_entry
        self._store_key = store_key
        self._input_prefix = input_prefix
        description = SensorEntityDescription(
            key=key,
            translation_key=translation_key,
            name=name,
            icon="mdi:water-percent",
            device_class=SensorDeviceClass.AQI,  # or None
            state_class=SensorStateClass.MEASUREMENT,
        )
        super().__init__(coordinator, config_entry, description)

    async def async_added_to_hass(self) -> None:
        """Update immediately when local saturation index input numbers change."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_{self.config_entry.entry_id}_{self._store_key}_updated",
                self.async_write_ha_state,
            )
        )

    def _get_inputs(self) -> dict[str, float | None]:
        """Return calculator inputs using controller values first, then manual values."""
        runtime_data = get_runtime_data(self.config_entry)
        inputs = runtime_data.calculator_inputs.get(self._store_key, {}) if runtime_data else {}
        prefix = self._input_prefix
        coordinator_data: Mapping[str, Any] = self.coordinator.data or {}
        manual_input_keys = {
            "ph": f"{prefix}_ph",
            "temperature_c": f"{prefix}_temperature",
            "tds_mg_l": f"{prefix}_tds",
            "calcium_hardness_mg_l_as_caco3": f"{prefix}_calcium",
            "carbonate_alkalinity_mg_l_as_caco3": f"{prefix}_alkalinity",
        }

        values: dict[str, float | None] = {}
        for input_name, source_fields in SATURATION_INDEX_SOURCE_FIELDS.items():
            controller_value = next(
                (
                    parsed_value
                    for source_field in source_fields
                    if (parsed_value := _as_optional_float(coordinator_data.get(source_field)))
                    is not None
                ),
                None,
            )
            values[input_name] = controller_value or _as_optional_float(
                inputs.get(manual_input_keys[input_name])
            )

        return values

    @staticmethod
    def _missing_inputs(values: dict[str, float | None]) -> list[str]:
        """Return names of inputs required before the result can be calculated."""
        return [key for key, value in values.items() if value is None]

    @property
    def native_value(self) -> float | None:
        """Calculate and return the saturation index value."""
        if self.coordinator.data is None:
            return None

        try:
            values = self._get_inputs()
            if self._missing_inputs(values):
                return None

            ph = values["ph"]
            temperature_c = values["temperature_c"]
            tds = values["tds_mg_l"]
            calcium_hardness = values["calcium_hardness_mg_l_as_caco3"]
            carbonate_alkalinity = values["carbonate_alkalinity_mg_l_as_caco3"]

            if (
                ph is None
                or temperature_c is None
                or tds is None
                or calcium_hardness is None
                or carbonate_alkalinity is None
                or min(tds, calcium_hardness, carbonate_alkalinity) <= 0
            ):
                return None

            # Saturation index formula (LSI/CSI without cyanuric-acid correction):
            # index = pH - pHs
            # pHs = 9.3 + A + B - C - D
            a = (math.log10(tds) - 1.0) / 10.0
            b = -13.12 * math.log10(temperature_c + 273.15) + 34.55
            c = math.log10(calcium_hardness) - 0.4
            d = math.log10(carbonate_alkalinity)

            phs = 9.3 + a + b - c - d
            saturation_index = ph - phs

            return round(saturation_index, 2)

        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, str | float | bool]:
        """Return the input values, interpretation and warning state."""
        try:
            values = self._get_inputs()
            attributes: dict[str, str | float | bool] = {
                key: value for key, value in values.items() if value is not None
            }
            missing_inputs = self._missing_inputs(values)
        except (ValueError, TypeError):
            attributes = {}
            missing_inputs = []

        value = self.native_value
        interpretation, warning_level, warning = _interpret_saturation_index(value)
        attributes.update(
            {
                "interpretation": interpretation,
                "warning_level": warning_level,
                "warning": warning,
                "missing_inputs": ", ".join(missing_inputs),
                "cyanuric_acid_correction": "not_applied",
                "alkalinity_note": (
                    "Use carbonate alkalinity / carbonate hardness for best results; "
                    "total alkalinity can be misleading with softeners."
                ),
            }
        )
        return attributes


class VioletLSISensor(VioletSaturationIndexSensor):
    """A specialized sensor for calculating the Langelier Saturation Index (LSI)."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the LSI sensor."""
        super().__init__(
            coordinator,
            config_entry,
            key="lsi_calculator",
            translation_key="lsi_index",
            name="LSI Index",
            store_key="lsi_inputs",
            input_prefix="lsi",
        )


class VioletCSISensor(VioletSaturationIndexSensor):
    """A specialized sensor for calculating the Calcite Saturation Index (CSI)."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the CSI sensor."""
        super().__init__(
            coordinator,
            config_entry,
            key="csi_calculator",
            translation_key="csi_index",
            name="CSI Index",
            store_key="csi_inputs",
            input_prefix="csi",
        )
