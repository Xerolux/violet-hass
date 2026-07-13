"""Services module for Violet Pool Controller."""

from .climate import ClimateServiceHandlersMixin
from .cover import CoverServiceHandlersMixin
from .dosing import DosingServiceHandlersMixin
from .extension import ExtensionServiceHandlersMixin
from .pump import PumpServiceHandlersMixin
from .rules import RulesServiceHandlersMixin
from .system import SystemServiceHandlersMixin

__all__ = [
    "ClimateServiceHandlersMixin",
    "CoverServiceHandlersMixin",
    "DosingServiceHandlersMixin",
    "ExtensionServiceHandlersMixin",
    "PumpServiceHandlersMixin",
    "RulesServiceHandlersMixin",
    "SystemServiceHandlersMixin",
]
