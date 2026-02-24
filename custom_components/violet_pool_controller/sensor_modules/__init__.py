
"""Sensor Submodules for Violet Pool Controller."""
from __future__ import annotations

from .base import (
    _BOOLEAN_VALUE_KEYS,
    _RUNTIME_KEYS,
    _TIMESTAMP_KEYS,
    _TIMESTAMP_SUFFIXES,
    _build_sensor_description,
    should_skip_sensor,
)
from .generic import (
    VioletSensor,
    VioletStatusSensor,
)
from .monitoring import (
    VioletAPIRequestRateSensor,
    VioletAverageLatencySensor,
    VioletConnectionLatencySensor,
    VioletLastEventAgeSensor,
    VioletSystemHealthSensor,
)
from .specialized import (
    VioletDosingStateSensor,
    VioletErrorCodeSensor,
    VioletFlowRateSensor,
)

__all__ = [
    # Base
    "_BOOLEAN_VALUE_KEYS",
    "_RUNTIME_KEYS",
    "_TIMESTAMP_KEYS",
    "_TIMESTAMP_SUFFIXES",
    "_build_sensor_description",
    "should_skip_sensor",
    # Generic
    "VioletSensor",
    "VioletStatusSensor",
    # Monitoring
    "VioletAPIRequestRateSensor",
    "VioletAverageLatencySensor",
    "VioletConnectionLatencySensor",
    "VioletLastEventAgeSensor",
    "VioletSystemHealthSensor",
    # Specialized
    "VioletDosingStateSensor",
    "VioletErrorCodeSensor",
    "VioletFlowRateSensor",
]
