"""DataUpdateCoordinator für den Violet Pool Controller.

⚠️ DEPRECATED: This module is deprecated and kept only for backward compatibility.
All coordinator functionality has been moved to device.py.

Please import from device.py instead:
    from .device import VioletPoolDataUpdateCoordinator

This file will be removed in a future version.
"""
import logging
import warnings

# Re-export from device.py for backward compatibility
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Show deprecation warning on import
warnings.warn(
    "Importing VioletPoolDataUpdateCoordinator from coordinator.py is deprecated. "
    "Please import from device.py instead. This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

_LOGGER.warning(
    "coordinator.py is deprecated. Please import VioletPoolDataUpdateCoordinator from device.py instead."
)

__all__ = ["VioletPoolDataUpdateCoordinator"]
