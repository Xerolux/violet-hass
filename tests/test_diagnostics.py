"""Tests for the diagnostics dump.

``async_get_config_entry_diagnostics`` had no test at all, and it used to dump
every controller key verbatim - including the identifiers Home Assistant
expects an integration to redact before the file is attached to a bug report.
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from homeassistant.components.diagnostics import REDACTED
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_PASSWORD,
    CONF_USE_SSL,
    CONF_USERNAME,
    DOMAIN,
)
from custom_components.violet_pool_controller.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.violet_pool_controller.error_handler import EnhancedErrorHandler

CURRENT_DATA = {
    "PUMP": 1,
    "onewire1_value": 24.5,
    "IP_ADDRESS": "192.168.178.55",
    "MAC_ADDRESS": "00:11:22:33:44:55",
    "SERIAL_NUMBER": "VPC-0001",
    "HW_SERIAL_CARRIER": "CARRIER-0001",
}


@pytest.fixture
def entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a config entry with a fully stubbed coordinator attached."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={
            CONF_API_URL: "192.168.178.55",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Test Pool Controller",
            CONF_CONTROLLER_NAME: "Test Pool",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "s3cret",
        },
        options={CONF_PASSWORD: "s3cret-in-options"},
    )
    config_entry.add_to_hass(hass)

    device = MagicMock()
    device.device_name = "Test Pool Controller"
    device.controller_name = "Test Pool"
    device._firmware_version = "1.2.3"
    device.device_id = 1
    device.api_url = "192.168.178.55"
    device.use_ssl = False
    device.available = True
    device._consecutive_failures = 0
    device.last_error = None
    device.system_health = 100.0
    device.connection_latency = 12.5
    device.average_latency = 11.0
    device._api_request_count = 7
    device.api_request_rate = 6.0
    device.last_event_age = 1.0
    device._poll_history = [(datetime(2026, 1, 1, tzinfo=UTC), 400, 12.5, ())]
    device.error_handler = EnhancedErrorHandler()

    config_entry.runtime_data = SimpleNamespace(
        coordinator=SimpleNamespace(
            device=device,
            data=dict(CURRENT_DATA),
            last_update_success=True,
        )
    )
    return config_entry


class TestDiagnostics:
    """The dump must be complete but free of credentials and identifiers."""

    async def test_credentials_are_redacted(self, hass: HomeAssistant, entry):
        """Username and password never appear, in data or in options."""
        result = await async_get_config_entry_diagnostics(hass, entry)

        assert result["config_entry"]["data"][CONF_PASSWORD] == REDACTED
        assert result["config_entry"]["data"][CONF_USERNAME] == REDACTED
        assert result["config_entry"]["options"][CONF_PASSWORD] == REDACTED

    async def test_controller_identifiers_are_redacted(self, hass: HomeAssistant, entry):
        """IP, MAC and the serial numbers are redacted inside current_data."""
        result = await async_get_config_entry_diagnostics(hass, entry)
        current = result["current_data"]

        for key in ("IP_ADDRESS", "MAC_ADDRESS", "SERIAL_NUMBER", "HW_SERIAL_CARRIER"):
            assert current[key] == REDACTED, f"{key} must be redacted"

    async def test_readings_are_still_included(self, hass: HomeAssistant, entry):
        """Redaction must not swallow the readings the dump exists for."""
        result = await async_get_config_entry_diagnostics(hass, entry)

        assert result["current_data"]["PUMP"] == 1
        assert result["current_data"]["onewire1_value"] == 24.5
        assert result["poll_statistics"]["total_polls"] == 1
        assert result["connection"]["last_update_success"] is True
        assert result["device"]["name"] == "Test Pool Controller"

    async def test_error_statistics_come_from_the_device_handler(
        self, hass: HomeAssistant, entry
    ):
        """The statistics are this controller's, not a process-wide singleton's."""
        handler = entry.runtime_data.coordinator.device.error_handler
        handler.record_error(handler.classify_error(TimeoutError("boom")))

        result = await async_get_config_entry_diagnostics(hass, entry)

        assert result["error_statistics"]["total_errors"] == 1
        assert len(result["recent_errors"]) == 1
        assert result["recent_errors"][0]["type"] == "timeout_error"
