# violet-poolController-api - API f├╝r Violet Pool Controller
# Copyright (C) 2024-2026  Xerolux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Violet Pool Controller API client library."""

from .api import VioletPoolAPI, VioletPoolAPIError
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from .const_api import (  # noqa: F401
    ACTION_ALLAUTO,
    ACTION_ALLOFF,
    ACTION_ALLON,
    ACTION_AUTO,
    ACTION_COLOR,
    ACTION_LOCK,
    ACTION_OFF,
    ACTION_ON,
    ACTION_PUSH,
    ACTION_UNLOCK,
    ERROR_CODES,
    ERROR_SEVERITY_ALARM,
    ERROR_SEVERITY_INFO,
    ERROR_SEVERITY_WARNING,
)
from .const_devices import (  # noqa: F401
    COVER_FUNCTIONS,
    COVER_STATE_MAP,
    DEVICE_PARAMETERS,
    STATE_TRANSLATIONS,
    VioletState,
    get_state_translation_language,
    set_state_translation_language,
)
from .utils_rate_limiter import RateLimiter, get_global_rate_limiter
from .utils_sanitizer import InputSanitizer

__all__ = [
    "VioletPoolAPI",
    "VioletPoolAPIError",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "VioletState",
    "InputSanitizer",
    "RateLimiter",
    "get_global_rate_limiter",
    "get_state_translation_language",
    "set_state_translation_language",
    "STATE_TRANSLATIONS",
    "ACTION_ALLAUTO",
    "ACTION_ALLOFF",
    "ACTION_ALLON",
    "ACTION_AUTO",
    "ACTION_COLOR",
    "ACTION_LOCK",
    "ACTION_OFF",
    "ACTION_ON",
    "ACTION_PUSH",
    "ACTION_UNLOCK",
    "COVER_FUNCTIONS",
    "COVER_STATE_MAP",
    "DEVICE_PARAMETERS",
    "ERROR_CODES",
    "ERROR_SEVERITY_ALARM",
    "ERROR_SEVERITY_INFO",
    "ERROR_SEVERITY_WARNING",
]
