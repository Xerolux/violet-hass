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

from ..config_entry_helpers import extract_api_host, with_non_default_port
from ..const import (
    CONF_ACTIVE_FEATURES,
    CONF_DOSING_STANDALONE,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_DOSING_STANDALONE,
    DEFAULT_PORT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_USE_SSL,
    DEFAULT_VERIFY_SSL,
)
from ..feature_keys import is_key_feature_active
from ..sensor_modules.base import romcode_key_rank, romcode_sensor_index

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
    offered = _drop_duplicate_romcode_spellings(keys)

    grouped: dict[str, list[str]] = {}
    for key in sorted(offered):
        if features is not None and not is_key_feature_active(key, features):
            continue
        # Simple grouping by prefix
        group = key.split("_")[0]
        grouped.setdefault(group, []).append(key)
    return grouped


def _drop_duplicate_romcode_spellings(keys: Iterable[str]) -> list[str]:
    """Return the keys with only one ROM-code spelling per OneWire probe.

    A controller may report the same ROM code as ``onewire1_rcode`` and
    ``onewire1romcode``; offering both would ask the user to pick between two
    entries for one value (the sensor platform publishes only one of them).

    Args:
        keys: The raw controller keys.

    Returns:
        The keys to offer, in no particular order.
    """
    best: dict[int, str] = {}
    others: list[str] = []
    for key in keys:
        index = romcode_sensor_index(key)
        if index is None:
            others.append(key)
            continue
        current = best.get(index)
        if current is None or romcode_key_rank(key, "") > romcode_key_rank(current, ""):
            best[index] = key
    return others + list(best.values())


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
        # NOTE: no credential-strength check here. The connection test in the
        # config flow does not apply one either, so a short controller password
        # ("1234") passed the test and then made this call raise - the
        # exception was swallowed below and the entry was created without a
        # single entity.
        username = config_data.get(CONF_USERNAME)
        password = config_data.get(CONF_PASSWORD)

        # Same host+port construction as the connection test. Without the port
        # a controller on e.g. :8080 was contacted on the default port, and
        # discovery silently returned nothing.
        host = with_non_default_port(
            extract_api_host(config_data),
            config_data.get(CONF_PORT, DEFAULT_PORT),
        )

        api = VioletPoolAPI(
            host=host,
            session=aiohttp_client.async_get_clientsession(hass),
            username=username,
            password=password,
            use_ssl=config_data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
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
