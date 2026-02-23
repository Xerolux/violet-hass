from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime, UnitOfVolume
from homeassistant.helpers.entity import EntityCategory

from ..const import DOSING_STATE_SENSORS
from ..device import VioletPoolDataUpdateCoordinator
from ..entity import VioletPoolControllerEntity
from ..error_codes import get_error_info
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
            entity_category=EntityCategory.DIAGNOSTIC,
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


class VioletDosingStateSensor(VioletPoolControllerEntity, SensorEntity):
    """Sensor for dosing system state arrays (DOS_*_STATE) and composite states."""

    # German translations for common state detail codes
    _DETAIL_DE: dict[str, str] = {
        "PUMP_ANTI_FREEZE": "Frostschutz",
        "BLOCKED_BY_OUTSIDE_TEMP": "Blockiert (Außentemp.)",
        "BLOCKED_BY_TRESHOLDS": "Blockiert (Grenzwerte)",
        "TRESHOLDS_REACHED": "Grenzwerte erreicht",
        "BLOCKED_BY_PUMP": "Blockiert (Pumpe aus)",
        "BLOCKED_BY_FLOW": "Blockiert (Durchfluss)",
        "BLOCKED_BY_SOLAR": "Blockiert (Solar)",
        "BLOCKED_BY_HEATER": "Blockiert (Heizung)",
        "WAITING_FOR_PUMP": "Wartet auf Pumpe",
        "WAITING_FOR_FLOW": "Wartet auf Durchfluss",
        "DOSING": "Dosiert",
        "DOSING_PAUSED": "Dosierung pausiert",
        "MANUAL_DOSING": "Manuelle Dosierung",
    }

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the dosing state sensor."""
        description = SensorEntityDescription(
            key=key,
            name=name,
            icon=icon,
            entity_category=EntityCategory.DIAGNOSTIC,
        )
        super().__init__(coordinator, config_entry, description)

    def _translate_detail(self, code: str) -> str:
        """Translate a detail code to German, fallback to title-cased string."""
        return self._DETAIL_DE.get(code, code.replace("_", " ").title())

    @property
    def native_value(self) -> str | None:
        """Return the dosing state as comma-separated German string."""
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
