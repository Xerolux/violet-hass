# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Config Flow Sensor Helper."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from violet_poolcontroller_api import (
    VioletAuthError,
    VioletPoolAPI,
    VioletPoolAPIError,
)

from ..const import (
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_PASSWORD,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_VERIFY_SSL,
)
from ..feature_keys import is_key_feature_active
from .validators import validate_credentials_strength

_LOGGER = logging.getLogger(__name__)


def group_sensor_keys(
    keys: Iterable[str],
    active_features: Iterable[str] | None = None,
) -> dict[str, list[str]]:
    """Group controller keys by prefix, dropping keys of disabled features.

    Args:
        keys: The raw controller keys.
        active_features: The features enabled for the config entry. ``None``
            (legacy entries without a feature list) disables the filter.

    Returns:
        A dictionary mapping group names to lists of sensor keys. Groups that
        end up empty are omitted.
    """
    features = None if active_features is None else set(active_features)

    grouped: dict[str, list[str]] = {}
    for key in sorted(keys):
        if features is not None and not is_key_feature_active(key, features):
            continue
        # Simple grouping by prefix
        group = key.split("_")[0]
        grouped.setdefault(group, []).append(key)
    return grouped


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
            verify_ssl=config_data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            timeout=config_data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION),
            max_retries=config_data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS),
            dosing_standalone=config_data.get(CONF_DOSING_STANDALONE, DEFAULT_DOSING_STANDALONE),
        )

        data = await api.get_readings()
        config_data[CONF_DOSING_STANDALONE] = api.dosing_standalone

        return group_sensor_keys(data.keys(), config_data.get(CONF_ACTIVE_FEATURES))

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
