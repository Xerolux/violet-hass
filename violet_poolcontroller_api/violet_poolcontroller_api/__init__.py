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

from .api import (
    SETPOINT_RANGES,
    VioletAuthError,
    VioletPayloadError,
    VioletPoolAPI,
    VioletPoolAPIError,
    VioletSetpointError,
    VioletTimeoutError,
    VioletUnsafeOperationError,
    validate_setpoint,
)
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
    ERROR_SEVERITY_REMINDER,
    ERROR_SEVERITY_WARNING,
)
from .const_devices import (  # noqa: F401
    COVER_FUNCTIONS,
    COVER_STATE_MAP,
    DEVICE_PARAMETERS,
    STATE_TRANSLATIONS,
    CoverState,
    DmxSceneState,
    OnewireState,
    OutputState,
    PvSurplusState,
    RuleState,
    VioletState,
    get_state_translation_language,
    set_state_translation_language,
)
from .parsers import (  # noqa: F401
    parse_epoch_milliseconds,
    parse_epoch_seconds,
    parse_hms_string,
    parse_optional_seconds,
    parse_runtime_string,
    parse_uptime_string,
)
from .readings import VioletReadings
from .utils_rate_limiter import RateLimiter, get_global_rate_limiter
from .utils_sanitizer import InputSanitizer

__all__ = [
    # Core client
    "VioletPoolAPI",
    # Exception hierarchy
    "VioletPoolAPIError",
    "VioletAuthError",
    "VioletTimeoutError",
    "VioletPayloadError",
    "VioletSetpointError",
    "VioletUnsafeOperationError",
    # Setpoint validation
    "SETPOINT_RANGES",
    "validate_setpoint",
    # Circuit breaker
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    # Enums
    "OutputState",
    "DmxSceneState",
    "RuleState",
    "CoverState",
    "OnewireState",
    "PvSurplusState",
    # State helpers
    "VioletState",
    "STATE_TRANSLATIONS",
    "get_state_translation_language",
    "set_state_translation_language",
    # Typed readings snapshot
    "VioletReadings",
    # Parsers
    "parse_runtime_string",
    "parse_hms_string",
    "parse_uptime_string",
    "parse_epoch_seconds",
    "parse_epoch_milliseconds",
    "parse_optional_seconds",
    # Utilities
    "InputSanitizer",
    "RateLimiter",
    "get_global_rate_limiter",
    # Action constants
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
    # Device constants
    "COVER_FUNCTIONS",
    "COVER_STATE_MAP",
    "DEVICE_PARAMETERS",
    # Error codes
    "ERROR_CODES",
    "ERROR_SEVERITY_ALARM",
    "ERROR_SEVERITY_INFO",
    "ERROR_SEVERITY_REMINDER",
    "ERROR_SEVERITY_WARNING",
]
