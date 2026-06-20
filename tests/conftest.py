"""Pytest configuration and fixtures for Violet Pool Controller tests."""

from __future__ import annotations

import contextlib
import importlib.util
import sys
import threading
import types
from pathlib import Path

# CRITICAL: Setup mocks BEFORE any local imports
# This allows tests to run on Python versions < 3.12 where external deps are unavailable
_test_dir = Path(__file__).parent
if str(_test_dir) not in sys.path:
    sys.path.insert(0, str(_test_dir))

# Prefer the REAL violet_poolcontroller_api package over the stale mock below.
# The outer monorepo directory (violet_poolcontroller_api/) has no __init__.py,
# so Python treats it as a namespace package and shadows the installed wheel /
# the inner real package (violet_poolcontroller_api/violet_poolcontroller_api/).
# By inserting the outer source directory at sys.path[0], the inner real package
# is discovered first and the detection logic below correctly skips the mock.
_api_src_dir = _test_dir.parent / "violet_poolcontroller_api"
if _api_src_dir.is_dir() and str(_api_src_dir) not in sys.path:
    sys.path.insert(0, str(_api_src_dir))

# Setup Home Assistant mocks first
# Import as a module to ensure proper execution context
import conftest_ha_mock  # noqa: F401,E402

# Use the module to satisfy linters (setup happens at import time)
_ = conftest_ha_mock


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

        async def wait_if_needed(self):
            """Mock wait_if_needed method."""
            pass

        async def acquire(self, tokens=1):
            """Mock acquire method."""
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
            self._base_url = self._build_secure_base_url(host, use_ssl)

        async def get_readings(self, query=None):
            """Get readings from controller."""
            return {"success": True, "data": {}}

        async def set_function_manually(self, payload):
            """Set function manually."""
            return {"success": True}

        async def set_switch_state(self, key, action):
            """Set switch state."""
            return {"success": True}

        def _build_secure_base_url(self, host, use_ssl):
            """Build secure base URL with validation."""

            # Validate hostname for common injection attacks
            if not host or not isinstance(host, str):
                raise ValueError("Invalid hostname")

            # Prevent path traversal
            if ".." in host or "/" in host or "\\" in host:
                raise ValueError("Invalid hostname")

            # Prevent SQL injection patterns
            if ";" in host or "DROP" in host.upper() or "--" in host:
                raise ValueError("Invalid hostname")

            # Prevent basic XSS
            if "<" in host or ">" in host:
                raise ValueError("Invalid hostname")

            scheme = "https" if use_ssl else "http"
            return f"{scheme}://{host}"

        async def _request(self, method=None, endpoint=None, **kwargs):
            """Mock HTTP request."""
            return {"success": True, "data": {}}

        async def set_config(self, config):
            """Mock set_config with sanitization."""
            # Sanitize the config
            sanitized = {}
            for key, value in config.items():
                if ";" in key or "DROP TABLE" in key.upper():
                    raise ValueError("Invalid configuration parameter")
                sanitized[key] = value

            return await self._request("POST", "/setConfig", json_payload=sanitized)

        async def set_all_dmx_scenes(self, action):
            """Set all DMX scenes with error handling.

            Iterates through all 12 DMX scenes and continues on error,
            collecting results and failures.
            """
            results = []
            errors = []

            # Iterate through all 12 scenes
            for i in range(1, 13):
                key = f"DMX_SCENE{i}"
                try:
                    await self.set_switch_state(key, action)
                    results.append(f"{key} OK")
                except Exception as e:
                    errors.append(str(e))
                    results.append(f"{key} ERROR: {e}")

            # Return aggregated result
            response_text = "; ".join(results)
            if errors:
                return {
                    "success": False,
                    "response": response_text,
                    "errors": errors
                }
            return {
                "success": True,
                "response": response_text
            }

    # api submodule
    api_module = types.ModuleType('api')
    api_module.VioletPoolAPI = MockVioletPoolAPI
    api_module.VioletPoolAPIError = MockVioletPoolAPIError

    class MockVioletAuthError(MockVioletPoolAPIError):
        """Mock auth error."""

    class MockVioletTimeoutError(MockVioletPoolAPIError):
        """Mock timeout error."""

    class MockVioletUnsafeOperationError(MockVioletPoolAPIError):
        """Mock unsafe operation error."""

    api_module.VioletAuthError = MockVioletAuthError
    api_module.VioletTimeoutError = MockVioletTimeoutError
    api_module.VioletUnsafeOperationError = MockVioletUnsafeOperationError
    mock_module.api = api_module

    # readings submodule (VioletReadings as a simple dict-wrapper)
    readings_module = types.ModuleType('readings')

    class MockVioletReadings(dict):
        """Minimal VioletReadings stand-in that behaves like a dict."""

    readings_module.VioletReadings = MockVioletReadings
    mock_module.readings = readings_module

    # const_api submodule
    const_api_module = types.ModuleType('const_api')
    const_api_module.API_TIMEOUT = 10
    const_api_module.API_PRIORITY_CRITICAL = 1
    const_api_module.API_PRIORITY_HIGH = 2
    const_api_module.API_PRIORITY_NORMAL = 3
    # Action constants (mirror violet_poolcontroller_api.const_api)
    const_api_module.ACTION_ON = "ON"
    const_api_module.ACTION_OFF = "OFF"
    const_api_module.ACTION_AUTO = "AUTO"
    const_api_module.ACTION_PUSH = "PUSH"
    const_api_module.ACTION_MAN = "MAN"
    const_api_module.ACTION_COLOR = "COLOR"
    const_api_module.ACTION_ALLON = "ALLON"
    const_api_module.ACTION_ALLOFF = "ALLOFF"
    const_api_module.ACTION_ALLAUTO = "ALLAUTO"
    const_api_module.ACTION_LOCK = "LOCK"
    const_api_module.ACTION_UNLOCK = "UNLOCK"
    mock_module.const_api = const_api_module

    # const_devices submodule
    const_devices_module = types.ModuleType('const_devices')

    class VioletState:
        AUTO_OFF = "AUTO_OFF"
        AUTO_ON = "AUTO_ON"
        AUTO_ACTIVE = "AUTO_ACTIVE"
        AUTO_ACTIVE_TIMER = "AUTO_ACTIVE_TIMER"
        MANUAL_ON_FORCED = "MANUAL_ON_FORCED"
        AUTO_WAITING = "AUTO_WAITING"
        MANUAL_OFF = "MANUAL_OFF"

    const_devices_module.VioletState = VioletState
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
        "4": "stopped",
        "OPEN": "open",
        "OPENING": "opening",
        "CLOSED": "closed",
        "CLOSING": "closing",
        "STOPPED": "stopped",
    }
    const_devices_module.COVER_FUNCTIONS = {
        "OPEN": "COVER_OPEN",
        "CLOSE": "COVER_CLOSE",
        "STOP": "COVER_STOP",
    }
    # Boolean state map (mirror violet_poolcontroller_api.const_devices):
    # 2 = Auto - Priority OFF (Rule Blocked) is OFF
    const_devices_module.STATE_MAP = {
        0: False, 1: True, 2: False, 3: True, 4: True, 5: False, 6: False,
        "0": False, "1": True, "2": False, "3": True, "4": True,
        "5": False, "6": False,
        "ON": True, "OFF": False, "AUTO": False,
    }
    const_devices_module.DEVICE_PARAMETERS = {}
    for _mod in ("EXT1", "EXT2"):
        for _relay in range(1, 9):
            _key = f"{_mod}_{_relay}"
            const_devices_module.DEVICE_PARAMETERS[_key] = {
                "supports_timer": True,
                "api_template": f"{_key},{{action}},{{duration}},0",
            }
    mock_module.const_devices = const_devices_module

    # utils_sanitizer submodule
    sanitizer_module = types.ModuleType('utils_sanitizer')

    class InputSanitizer:
        @staticmethod
        def sanitize(value):
            return value

        @staticmethod
        def validate_api_parameter(param):
            """Validate API parameter for security."""
            if not isinstance(param, str):
                raise ValueError("Parameter must be string")
            if any(c in param for c in [";", "<", ">", "'", '"']):
                raise ValueError("Invalid characters in parameter")
            if ".." in param or "/" in param:
                raise ValueError("Path traversal attempt")
            return param

        @staticmethod
        def sanitize_string(value, max_length=1000):
            """Sanitize string value."""
            if value is None:
                return ""
            value_str = str(value)
            if len(value_str) > max_length:
                value_str = value_str[:max_length]
            # Remove potential XSS
            value_str = value_str.replace("<", "&lt;").replace(">", "&gt;")
            return value_str

        @staticmethod
        def sanitize_numeric(value):
            """Sanitize numeric value."""
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                if not value:
                    return 0.0
                # Try to extract numeric part
                import re
                # Extract number with optional negative sign and decimals
                match = re.search(r"-?\d+(?:\.\d+)?", value)
                if match:
                    try:
                        return float(match.group())
                    except ValueError:
                        return 0.0
                return 0.0
            return 0.0

    sanitizer_module.InputSanitizer = InputSanitizer
    mock_module.utils_sanitizer = sanitizer_module

    # Mirror the real package's top-level public API so that imports like
    # ``from violet_poolcontroller_api import VioletAuthError`` work even when
    # tests fall back to this mock (real package unavailable).
    mock_module.VioletPoolAPI = api_module.VioletPoolAPI
    mock_module.VioletPoolAPIError = api_module.VioletPoolAPIError
    mock_module.VioletAuthError = api_module.VioletAuthError
    mock_module.VioletTimeoutError = api_module.VioletTimeoutError
    mock_module.VioletUnsafeOperationError = api_module.VioletUnsafeOperationError
    mock_module.InputSanitizer = InputSanitizer

    return mock_module


# Stub the external API package only when it is not actually installed -
# shadowing the real package would test against mock behavior.
# Note: find_spec() returns a (namespace) spec even for the outer monorepo
# directory, so we additionally verify the real package imports successfully.
_api_available = False
if 'violet_poolcontroller_api' not in sys.modules:
    _spec = importlib.util.find_spec('violet_poolcontroller_api')
    if _spec is not None and _spec.origin and _spec.origin.endswith('__init__.py'):
        try:
            import violet_poolcontroller_api as _probe  # noqa: F811
            _api_available = hasattr(_probe, 'VioletPoolAPI')
        except ImportError:
            _api_available = False

if not _api_available and 'violet_poolcontroller_api' not in sys.modules:
    mock_api = _create_mock_violet_api_module()
    sys.modules['violet_poolcontroller_api'] = mock_api
    sys.modules['violet_poolcontroller_api.api'] = mock_api.api
    sys.modules['violet_poolcontroller_api.const_api'] = mock_api.const_api
    sys.modules['violet_poolcontroller_api.const_devices'] = mock_api.const_devices
    sys.modules['violet_poolcontroller_api.utils_sanitizer'] = mock_api.utils_sanitizer
    sys.modules['violet_poolcontroller_api.readings'] = mock_api.readings

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

import pytest  # noqa: E402

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Disable socket blocking - needed for Home Assistant imports
    # pytest-homeassistant-custom-component includes pytest-socket which blocks all sockets by default
    with contextlib.suppress(AttributeError):
        config.option.socket_enabled = False

    # Try to disable socket plugin completely
    try:
        plugin = config.pluginmanager.get_plugin('socket')
        if plugin:
            config.pluginmanager.unregister(plugin)
    except Exception:
        pass

    # Windows-only: pytest-homeassistant-custom-component calls
    # ``pytest_socket.disable_socket(allow_unix_socket=True)`` from its
    # ``pytest_runtest_setup`` hook. On Windows AF_UNIX is unavailable, so
    # asyncio's ProactorEventLoop cannot create its self-pipe and every test
    # errors out during setup. Neutralise disable_socket on Windows so the loop
    # can be created; Linux CI keeps strict socket blocking (AF_UNIX allowed).
    if sys.platform == "win32":
        try:
            import pytest_socket

            def _no_op_disable_socket(*_args, **_kwargs):
                pass

            pytest_socket.disable_socket = _no_op_disable_socket
            pytest_socket.enable_socket()
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
    """Enable sockets before fixtures need them (Windows-only workaround).

    On Windows, asyncio's ProactorEventLoop needs socket.socketpair() to create
    its internal IPC pipe. pytest-homeassistant-custom-component disables ALL
    socket creation on Windows (since AF_UNIX is not available there), which
    prevents the event loop from being created at all.

    Newer pytest-asyncio versions provision the event loop from different
    fixtures than ``event_loop``, so on Windows we re-enable sockets for every
    fixture setup. Linux CI is unaffected (sockets stay disabled there because
    AF_UNIX is allowed and the loop never needs an AF_INET socketpair).
    """
    if sys.platform != "win32":
        return
    if fixturedef.argname == "event_loop":
        try:
            import pytest_socket
            pytest_socket.enable_socket()
        except Exception:
            pass
        return
    try:
        import pytest_socket
        pytest_socket.enable_socket()
    except Exception:
        pass


# NOTE: The hass / device_registry / entity_registry fixtures are provided by
# pytest-homeassistant-custom-component. Do not redefine them here - a local
# override shadows the real fixtures and breaks every test that depends on a
# functioning HomeAssistant instance.
