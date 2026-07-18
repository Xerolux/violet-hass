# =============================================================================
# Violet Pool Controller – Service input validation helpers
# Copyright © 2026 Xerolux
# =============================================================================

"""Local validation helpers for service inputs.

These wrap the API library's ``validate_duration`` (v0.0.36+) and provide a
speed clamp. They translate ``VioletPoolAPIError`` raised by the API into
``HomeAssistantError`` so that invalid service inputs surface to the user as
a clean HA service error instead of an unhandled exception.

Background: ``InputSanitizer.validate_speed`` / ``InputSanitizer.validate_duration``
were removed from the API in v0.0.36 (they silently clamped values; the
canonical ``validate_duration`` now lives in ``_api_model`` and raises on
invalid input). The integration owns these thin wrappers to preserve the
service-call UX.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.exceptions import HomeAssistantError
from violet_poolcontroller_api import VioletPoolAPIError
from violet_poolcontroller_api._api_model import validate_duration

_LOGGER = logging.getLogger(__name__)


def _validate_speed(value: Any, *, min_speed: int, max_speed: int, default: int) -> int:
    """Clamp ``value`` into [min_speed, max_speed], falling back to ``default``.

    Mirrors the previous ``InputSanitizer.validate_speed`` contract: invalid
    types or out-of-range values are clamped/silently corrected rather than
    raising, because speed is a best-effort control parameter.
    """
    try:
        speed = int(value)
    except (TypeError, ValueError):
        _LOGGER.warning("Invalid pump speed %r, using default %d", value, default)
        return default
    if speed < min_speed:
        return min_speed
    if speed > max_speed:
        return max_speed
    return speed


def _validate_duration_seconds(
    value: Any, *, minimum: int, maximum: int
) -> int:
    """Validate an actuator duration in seconds via the API's ``validate_duration``.

    Raises ``HomeAssistantError`` (not ``VioletPoolAPIError``) on invalid input
    so HA surfaces it cleanly to the service caller.
    """
    try:
        return validate_duration(value, minimum=minimum, maximum=maximum)
    except VioletPoolAPIError as err:
        raise HomeAssistantError(
            f"Invalid duration {value!r}: must be a whole number between "
            f"{minimum} and {maximum} seconds"
        ) from err
