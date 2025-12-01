"""Pytest configuration and fixtures for Violet Pool Controller tests."""

from __future__ import annotations

import threading
from typing import Any
from unittest.mock import patch

import pytest


def pytest_configure(config):
    """Configure pytest with custom settings."""
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
