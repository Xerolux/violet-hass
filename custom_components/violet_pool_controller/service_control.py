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

DOSING_INDEX_MAP = {
    "chlorine": 0,  # DOS_1_CL
    "electrolysis": 1,  # DOS_2_ELO
    "ph_minus": 3,  # DOS_4_PHM (index 2 is unused in firmware)
    "ph_plus": 4,  # DOS_5_PHP
    "flocculant": 5,  # DOS_6_FLOC
    "h2o2": 0,  # shares DOS_1_CL physical output, from_param=3 distinguishes it
}

DOSING_FROM_PARAM_MAP = {
    "h2o2": 3,  # H2O2 uses from=3; all others default to from=1
}

DOSING_SYSTEMS = {
    "chlorine": "DOSAGE_chlorine",
    "electrolysis": "DOSAGE_electrolysis",
    "ph_minus": "DOSAGE_phminus",
    "ph_plus": "DOSAGE_phplus",
    "flocculant": "DOSAGE_floc",
    "h2o2": "DOSAGE_h2o2",
}

DOSING_SYSTEM_TO_KEY = {
    "chlorine": "DOS_1_CL",
    "electrolysis": "DOS_2_ELO",
    "ph_minus": "DOS_4_PHM",
    "ph_plus": "DOS_5_PHP",
    "flocculant": "DOS_6_FLOC",
    "h2o2": "DOS_1_CL",
}


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
