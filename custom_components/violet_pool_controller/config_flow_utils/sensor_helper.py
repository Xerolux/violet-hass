# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Config Flow Sensor Helper."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from violet_poolcontroller_api import (
    VioletAuthError,
    VioletPoolAPI,
    VioletPoolAPIError,
)

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

        from ..const import CONF_DOSING_STANDALONE, DEFAULT_DOSING_STANDALONE

        api = VioletPoolAPI(
            host=config_data[CONF_API_URL],
            session=aiohttp_client.async_get_clientsession(hass),
            username=username,
            password=password,
            use_ssl=config_data.get(CONF_USE_SSL, False),
            verify_ssl=True,
            timeout=config_data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION),
            max_retries=config_data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS),
            dosing_standalone=config_data.get(
                CONF_DOSING_STANDALONE, DEFAULT_DOSING_STANDALONE
            ),
        )

        data = await api.get_readings()
        config_data[CONF_DOSING_STANDALONE] = api.dosing_standalone

        grouped: dict[str, list[str]] = {}
        for key in sorted(data.keys()):
            # Simple grouping by prefix
            group = key.split("_")[0]
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(key)
        return grouped

    except VioletAuthError as err:
        _LOGGER.warning("Failed to get grouped sensors: authentication error: %s", err)
        return {}
    except VioletPoolAPIError as err:
        _LOGGER.warning("Failed to get grouped sensors: API error: %s", err)
        return {}
    except TimeoutError as err:
        _LOGGER.warning("Failed to get grouped sensors: timeout: %s", err)
        return {}
    except Exception as err:
        _LOGGER.error("Failed to get grouped sensors: unexpected error: %s", err)
        return {}
