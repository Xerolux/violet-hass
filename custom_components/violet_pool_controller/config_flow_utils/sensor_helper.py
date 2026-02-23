"""Config Flow Sensor Helper."""

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from ..api import VioletPoolAPI
from ..const import (
    CONF_API_URL,
    CONF_PASSWORD,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
)
from .validators import validate_credentials_strength

_LOGGER = logging.getLogger(__name__)


async def get_grouped_sensors(
    hass: HomeAssistant,
    config_data: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Fetch sensors and group them.

    Args:
        hass: The Home Assistant instance.
        config_data: The configuration data.

    Returns:
        A dictionary mapping groups to lists of sensor keys.
    """
    try:
        # Validate credentials strength before using them
        username = config_data.get(CONF_USERNAME)
        password = config_data.get(CONF_PASSWORD)

        validate_credentials_strength(username, password)

        api = VioletPoolAPI(
            host=config_data[CONF_API_URL],
            session=aiohttp_client.async_get_clientsession(hass),
            username=username,
            password=password,
            use_ssl=config_data.get(CONF_USE_SSL, False),
            verify_ssl=True,
            timeout=config_data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION),
            max_retries=config_data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS),
        )

        data = await api.get_readings()

        grouped: dict[str, list[str]] = {}
        for key in sorted(data.keys()):
            # Einfache Gruppierung nach Präfix
            group = key.split("_")[0]
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(key)
        return grouped

    except Exception:
        return {}
