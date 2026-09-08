"""Control service handlers for the Violet Pool Controller integration."""

from __future__ import annotations

import logging
from typing import Any

from .service_mixins import (
    ClimateServiceHandlersMixin,
    CoverServiceHandlersMixin,
    DosingServiceHandlersMixin,
    ExtensionServiceHandlersMixin,
    PumpServiceHandlersMixin,
    RulesServiceHandlersMixin,
    SystemServiceHandlersMixin,
)

_LOGGER = logging.getLogger(__name__)


class VioletControlServiceHandlers(
    ClimateServiceHandlersMixin,
    CoverServiceHandlersMixin,
    DosingServiceHandlersMixin,
    ExtensionServiceHandlersMixin,
    PumpServiceHandlersMixin,
    RulesServiceHandlersMixin,
    SystemServiceHandlersMixin,
):
    """Handlers for control and action-oriented services."""

    manager: Any
    hass: Any
