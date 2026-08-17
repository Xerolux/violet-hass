"""Tests for numeric config clamping in _extract_config.

The config/options flow accepts polling intervals up to 3600s and timeouts down
to 1s, while ``_validate_config`` used to insist on 5-300s and 5-60s. A value
the UI itself offered therefore made the next setup fail with "Invalid
configuration". Values are now clamped into the supported range instead.
"""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller import _extract_config, _validate_config
from custom_components.violet_pool_controller.config_flow_utils.constants import (
    MAX_POLLING_INTERVAL,
    MAX_RETRIES,
    MAX_TIMEOUT,
    MIN_RETRIES,
    MIN_TIMEOUT,
)
from custom_components.violet_pool_controller.const import (
    CONF_ADAPTIVE_POLLING,
    CONF_API_URL,
    CONF_DEVICE_NAME,
    CONF_POLLING_INTERVAL,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    DEFAULT_ADAPTIVE_POLLING,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
    MIN_SUPPORTED_POLLING_INTERVAL,
)


def _entry(options: dict | None = None, data: dict | None = None) -> MockConfigEntry:
    """Create a minimal config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={
            CONF_API_URL: "192.168.178.55",
            CONF_DEVICE_NAME: "Test Pool Controller",
            **(data or {}),
        },
        options=options or {},
    )


class TestNumericClamping:
    """Out-of-range values must not break the setup."""

    @pytest.mark.parametrize(
        ("option", "value", "expected"),
        [
            (CONF_POLLING_INTERVAL, 600, 600),
            (CONF_POLLING_INTERVAL, 99_999, MAX_POLLING_INTERVAL),
            (CONF_POLLING_INTERVAL, 1, MIN_SUPPORTED_POLLING_INTERVAL),
            (CONF_TIMEOUT_DURATION, 3, 3),
            (CONF_TIMEOUT_DURATION, 900, MAX_TIMEOUT),
            (CONF_TIMEOUT_DURATION, 0, MIN_TIMEOUT),
            (CONF_RETRY_ATTEMPTS, 50, MAX_RETRIES),
            (CONF_RETRY_ATTEMPTS, 0, MIN_RETRIES),
        ],
    )
    def test_values_are_clamped_and_accepted(self, option, value, expected) -> None:
        """A value from the options flow is clamped, and validation passes."""
        config = _extract_config(_entry(options={option: value}))

        key = {
            CONF_POLLING_INTERVAL: "polling_interval",
            CONF_TIMEOUT_DURATION: "timeout_duration",
            CONF_RETRY_ATTEMPTS: "retry_attempts",
        }[option]

        assert config[key] == expected
        assert _validate_config(config) is True

    def test_legacy_five_second_interval_is_kept(self) -> None:
        """Entries from older versions using a 5s interval keep working."""
        config = _extract_config(_entry(data={CONF_POLLING_INTERVAL: 5}))

        assert config["polling_interval"] == 5
        assert _validate_config(config) is True

    def test_float_values_are_accepted(self) -> None:
        """Number selectors hand back floats; they must not fall back."""
        config = _extract_config(_entry(options={CONF_POLLING_INTERVAL: 30.0}))

        assert config["polling_interval"] == 30

    def test_non_numeric_value_falls_back_to_default(self) -> None:
        """A corrupt value falls back to the default instead of raising."""
        config = _extract_config(_entry(options={CONF_POLLING_INTERVAL: "not-a-number"}))

        assert config["polling_interval"] == DEFAULT_POLLING_INTERVAL
        assert _validate_config(config) is True


class TestAdaptivePollingConfig:
    """The adaptive polling option is part of the extracted config."""

    def test_defaults_to_enabled(self) -> None:
        """Without an explicit setting the back-off is on."""
        assert _extract_config(_entry())["adaptive_polling"] is DEFAULT_ADAPTIVE_POLLING

    def test_option_overrides_default(self) -> None:
        """The options flow can turn the back-off off."""
        config = _extract_config(_entry(options={CONF_ADAPTIVE_POLLING: False}))

        assert config["adaptive_polling"] is False
