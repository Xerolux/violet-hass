"""Mock for violet-poolController-api for testing without external dependency."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Create mock module structure
class MockVioletPoolAPIError(Exception):
    """Mock API error."""
    pass


class MockRateLimiter:
    """Mock rate limiter."""
    pass


class MockVioletPoolAPI:
    """Mock Violet Pool Controller API."""

    def __init__(self, host, session=None, username=None, password=None,
                 use_ssl=True, timeout=10, max_retries=3):
        self.host = host
        self.session = session
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limiter = MockRateLimiter()

    async def get_readings(self, query=None):
        """Get readings from controller."""
        return {"success": True, "data": {}}

    async def set_function_manually(self, payload):
        """Set function manually."""
        return {"success": True}

    async def set_switch_state(self, key, action):
        """Set switch state."""
        return {"success": True}

    async def set_all_dmx_scenes(self, action):
        """Set all DMX scenes."""
        responses = {}
        for i in range(1, 13):
            key = f"DMX_SCENE{i}"
            responses[key] = f"{key} OK"
        return {"success": True, "response": ", ".join(responses.values())}


# Create module-level exports
def create_mock_violet_api_module():
    """Create a mock violet_poolcontroller_api module."""
    import types

    mock_module = types.ModuleType('violet_poolcontroller_api')

    # API submodule
    api_module = types.ModuleType('api')
    api_module.VioletPoolAPI = MockVioletPoolAPI
    api_module.VioletPoolAPIError = MockVioletPoolAPIError

    mock_module.api = api_module

    # const_api submodule
    const_api_module = types.ModuleType('const_api')
    const_api_module.API_TIMEOUT = 10
    const_api_module.API_PRIORITY_CRITICAL = 1
    const_api_module.API_PRIORITY_HIGH = 2
    const_api_module.API_PRIORITY_NORMAL = 3

    mock_module.const_api = const_api_module

    # const_devices submodule
    const_devices_module = types.ModuleType('const_devices')
    const_devices_module.DEVICE_STATE_MAPPING = {
        0: "AUTO_OFF",
        1: "AUTO_ON",
        2: "AUTO_ACTIVE",
        3: "AUTO_ACTIVE_TIMER",
        4: "MANUAL_ON_FORCED",
        5: "AUTO_WAITING",
        6: "MANUAL_OFF",
    }
    const_devices_module.COVER_STATE_MAP = {
        "0": "open",
        "1": "opening",
        "2": "closed",
        "3": "closing",
    }

    mock_module.const_devices = const_devices_module

    # utils_sanitizer submodule
    sanitizer_module = types.ModuleType('utils_sanitizer')
    class InputSanitizer:
        @staticmethod
        def sanitize(value):
            return value
    sanitizer_module.InputSanitizer = InputSanitizer

    mock_module.utils_sanitizer = sanitizer_module

    return mock_module


# Register mock module
if 'violet_poolcontroller_api' not in sys.modules:
    sys.modules['violet_poolcontroller_api'] = create_mock_violet_api_module()
    sys.modules['violet_poolcontroller_api.api'] = sys.modules['violet_poolcontroller_api'].api
    sys.modules['violet_poolcontroller_api.const_api'] = sys.modules['violet_poolcontroller_api'].const_api
    sys.modules['violet_poolcontroller_api.const_devices'] = sys.modules['violet_poolcontroller_api'].const_devices
    sys.modules['violet_poolcontroller_api.utils_sanitizer'] = sys.modules['violet_poolcontroller_api'].utils_sanitizer
