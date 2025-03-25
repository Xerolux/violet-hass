"""Cover Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, List

from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_API_URL, CONF_DEVICE_NAME, MANUFACTURER, INTEGRATION_VERSION

_LOGGER = logging.getLogger(__name__)


class VioletCover(CoordinatorEntity, CoverEntity):
    """Repräsentation der Pool-Abdeckung (Cover)."""

    def __init__(self, coordinator, config_entry: ConfigEntry):
        """Initialisiere die Cover-Entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        device_name = config_entry.data.get(CONF
