"""Pytest configuration and fixtures for Violet Pool Controller tests."""

from __future__ import annotations

import sys
from pathlib import Path
import threading
import types

# CRITICAL: Setup mocks BEFORE any local imports
# This allows tests to run on Python versions < 3.12 where external deps are unavailable
_test_dir = Path(__file__).parent
if str(_test_dir) not in sys.path:
    sys.path.insert(0, str(_test_dir))

# Setup Home Assistant mocks first
exec(open(_test_dir / 'conftest_ha_mock.py').read())


def _create_mock_violet_api_module():
    """Create a mock violet_poolcontroller_api module for testing."""
    mock_module = types.ModuleType('violet_poolcontroller_api')

    # Create API error class
    class MockVioletPoolAPIError(Exception):
        """Mock Violet Pool API Error."""
        pass

    # Create rate limiter mock
    class MockRateLimiter:
        """Mock rate limiter."""
        pass

    # Create API class
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

    # api submodule
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


if 'violet_poolcontroller_api' not in sys.modules:
    mock_api = _create_mock_violet_api_module()
    sys.modules['violet_poolcontroller_api'] = mock_api
    sys.modules['violet_poolcontroller_api.api'] = mock_api.api
    sys.modules['violet_poolcontroller_api.const_api'] = mock_api.const_api
    sys.modules['violet_poolcontroller_api.const_devices'] = mock_api.const_devices
    sys.modules['violet_poolcontroller_api.utils_sanitizer'] = mock_api.utils_sanitizer

# CRITICAL: Patch deprecated timezone BEFORE any imports
# pytest-homeassistant-custom-component uses 'US/Pacific' which is deprecated
# This must happen before pytest or homeassistant is imported
try:
    import homeassistant.util.dt as dt_util
    _original_get_time_zone = dt_util.get_time_zone
    
    def _patched_get_time_zone(time_zone_str):
        """Accept US/Pacific and map to Europe/Berlin."""
        if time_zone_str == "US/Pacific":
            time_zone_str = "Europe/Berlin"
        return _original_get_time_zone(time_zone_str)
    
    dt_util.get_time_zone = _patched_get_time_zone
except Exception:
    pass

import pytest

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Disable socket blocking - needed for Home Assistant imports
    # pytest-homeassistant-custom-component includes pytest-socket which blocks all sockets by default
    try:
        config.option.socket_enabled = False
    except AttributeError:
        pass

    # Try to disable socket plugin completely
    try:
        plugin = config.pluginmanager.get_plugin('socket')
        if plugin:
            config.pluginmanager.unregister(plugin)
    except Exception:
        pass

    # Patch the thread check in pytest-homeassistant-custom-component
    # to allow newer Home Assistant thread names
    try:
        import pytest_homeassistant_custom_component.plugins as plugins_module

        # Store original thread validation logic
        original_code = plugins_module.__dict__.get('__thread_check_original__')

        if not original_code:
            # Monkey patch by modifying the module code to accept new thread names
            # This is necessary because newer HA versions use '_run_safe_shutdown_loop'
            # instead of 'waitpid-' threads

            # We'll patch threading.enumerate to filter out HA's internal threads
            original_enumerate = threading.enumerate

            def patched_enumerate():
                """Filter out Home Assistant's safe shutdown threads from enumeration."""
                threads = original_enumerate()
                return [
                    t for t in threads
                    if not (hasattr(t, 'name') and '_run_safe_shutdown_loop' in t.name)
                ]

            # Apply the patch at module load time
            threading.enumerate = patched_enumerate
            plugins_module.__dict__['__thread_check_original__'] = True

    except (ImportError, AttributeError):
        # Plugin not installed or structure changed, skip patching
        pass

    # Add custom markers
    config.addinivalue_line(
        "markers", "thread_safe: mark test as thread-safe"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(fixturedef, request):
    """Enable sockets before event_loop fixture is set up.

    On Windows, asyncio's ProactorEventLoop needs socket.socketpair() to create
    its internal IPC pipe. pytest-homeassistant-custom-component disables ALL
    socket creation on Windows (since AF_UNIX is not available there), which
    prevents the event loop from being created at all.

    This hook intercepts event_loop fixture setup specifically and temporarily
    re-enables sockets so the loop can be created. The sockets are re-disabled
    by pytest-hacc's pytest_runtest_setup hook for the actual test body.
    """
    if fixturedef.argname == "event_loop":
        try:
            import pytest_socket
            pytest_socket.enable_socket()
        except Exception:
            pass
