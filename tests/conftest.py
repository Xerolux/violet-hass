"""Pytest configuration and fixtures for Violet Pool Controller tests.

The suite runs against the real Home Assistant test harness
(``pytest-homeassistant-custom-component``) and the real
``violet-poolController-api`` package. Both are installed by
``requirements-dev.txt``; if either is missing, the run stops instead of
silently falling back to stubs. A stubbed run would report green while
testing nothing but the stubs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add the project root to sys.path so ``custom_components.violet_pool_controller``
# imports resolve from a plain checkout.
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def _require(module: str, hint: str) -> None:
    """Stop the run with an actionable message when a hard dependency is missing."""
    try:
        __import__(module)
    except ImportError as err:  # pragma: no cover - environment guard
        pytest.exit(
            f"{hint} is required to run this test suite but could not be imported "
            f"({module}: {err}). Install the development environment first:\n"
            f"    pip install -r requirements-dev.txt",
            returncode=4,
        )


_require("homeassistant", "Home Assistant")
_require("pytest_homeassistant_custom_component", "pytest-homeassistant-custom-component")
_require("violet_poolcontroller_api", "The violet-poolController-api package")


def pytest_runtest_teardown(item: pytest.Item) -> None:
    """Undo the harness's per-test socket guard.

    pytest-homeassistant-custom-component calls
    ``pytest_socket.disable_socket(allow_unix_socket=True)`` from its own
    ``pytest_runtest_setup`` hook. ``disable_socket`` installs a guard by
    subclassing whatever ``socket.socket`` currently is - so every call adds
    one level to the MRO, and ``GuardedSocket.__new__``'s ``super().__new__``
    chain grows one frame per test.

    pytest-socket normally unwinds that in its own teardown, but ``pytest.ini``
    disables the plugin (``-p no:socket``) because Home Assistant needs to
    manage socket blocking itself. Nothing was left to call ``enable_socket``,
    so the chain grew until it hit Python's recursion limit: from roughly the
    950th test onwards, every remaining test errored at setup with
    ``RecursionError: maximum recursion depth exceeded`` - 475 of them in a
    full run. Splitting the suite in half hid it, which is why it survived so
    long.

    Restoring the real socket after each test is exactly what the plugin would
    do, and keeps the blocking the harness sets up for the next test intact
    (it re-applies it in its own setup hook).
    """
    try:
        import pytest_socket

        pytest_socket.enable_socket()
    except Exception:  # pragma: no cover - pytest-socket always present via the harness
        pass


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom settings."""
    # Windows only: pytest-homeassistant-custom-component calls
    # ``pytest_socket.disable_socket(allow_unix_socket=True)`` from its
    # ``pytest_runtest_setup`` hook. AF_UNIX does not exist on Windows, so
    # asyncio's ProactorEventLoop cannot create its self-pipe and every test
    # errors out during setup. Neutralise disable_socket there so the loop can
    # be created. Linux and macOS keep the harness's socket blocking.
    if sys.platform == "win32":
        try:
            import pytest_socket

            def _no_op_disable_socket(*_args: object, **_kwargs: object) -> None:
                pass

            pytest_socket.disable_socket = _no_op_disable_socket
            pytest_socket.enable_socket()
        except Exception:  # pragma: no cover - Windows-only path
            pass

    config.addinivalue_line("markers", "thread_safe: mark test as thread-safe")


@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(fixturedef: pytest.FixtureDef, request: pytest.FixtureRequest) -> None:
    """Re-enable sockets before every fixture setup (Windows-only workaround).

    See ``pytest_configure``: on Windows the event loop itself needs
    ``socket.socketpair()``, and newer pytest-asyncio releases provision the
    loop from varying fixtures, so the guard cannot be tied to a single one.
    """
    if sys.platform != "win32":
        return
    try:  # pragma: no cover - Windows-only path
        import pytest_socket

        pytest_socket.enable_socket()
    except Exception:
        pass


# NOTE: The hass / device_registry / entity_registry fixtures are provided by
# pytest-homeassistant-custom-component. Do not redefine them here - a local
# override shadows the real fixtures and breaks every test that depends on a
# functioning HomeAssistant instance.
