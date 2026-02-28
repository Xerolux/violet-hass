"""Tests for Violet Pool Controller reconfiguration flow (Gold Level)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.data_flow_flow import FlowResultType
import voluptuous as vol


class TestReconfigureFlow:
    """Test the reconfiguration flow."""

    @pytest.fixture
    def mock_config_entry(self):
        """Create a mock config entry."""
        entry = MagicMock(spec=ConfigEntry)
        entry.entry_id = "test_entry_id"
        entry.data = {
            "api_url": "192.168.178.55",
            "use_ssl": True,
            "device_name": "Test Pool Controller",
            "controller_name": "Violet",
            "username": "admin",
            "password": "password",
            "device_id": 1,
            "polling_interval": 10,
            "timeout_duration": 30,
            "retry_attempts": 3,
        }
        return entry

    @pytest.fixture
    def config_flow(self, hass: HomeAssistant):
        """Create a ConfigFlow instance for testing."""
        from custom_components.violet_pool_controller.config_flow import ConfigFlow

        flow = ConfigFlow()
        flow.hass = hass
        return flow

    @pytest.mark.asyncio
    async def test_async_step_reconfigure_show_form(
        self, hass: HomeAssistant, config_flow, mock_config_entry
    ):
        """Test that reconfigure step shows the form with current values."""
        # Mock the config entries to return our mock entry
        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)

        # Set context for reconfigure
        config_flow.context = {"entry_id": mock_config_entry.entry_id}

        # Call reconfigure step
        result = await config_flow.async_step_reconfigure(user_input=None)

        # Verify form is shown
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reconfigure"

        # Verify form has current values
        data_schema = result["data_schema"]
        assert data_schema is not None

    @pytest.mark.asyncio
    async def test_async_step_reconfigure_with_valid_input(
        self, hass: HomeAssistant, config_flow, mock_config_entry
    ):
        """Test reconfigure with valid input updates the entry."""
        # Mock dependencies
        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
        hass.config_entries.async_update_entry = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        # Mock API test to succeed
        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_readings = AsyncMock(return_value={"status": "ok"})
            mock_api_class.return_value = mock_api

            # Set context
            config_flow.context = {"entry_id": mock_config_entry.entry_id}

            # New configuration values
            user_input = {
                "api_url": "192.168.178.100",  # Changed IP
                "username": "newuser",
                "password": "newpassword",
                "use_ssl": False,  # Changed to False
                "polling_interval": 20,  # Changed from 10
                "timeout_duration": 60,  # Changed from 30
                "retry_attempts": 5,  # Changed from 3
            }

            # Call reconfigure with input
            result = await config_flow.async_step_reconfigure(user_input=user_input)

            # Verify entry was updated
            hass.config_entries.async_update_entry.assert_called_once()
            call_args = hass.config_entries.async_update_entry.call_args
            updated_entry = call_args[0][0]
            updated_data = call_args[1]["data"]

            # Verify new values
            assert updated_data["api_url"] == "192.168.178.100"
            assert updated_data["use_ssl"] is False
            assert updated_data["polling_interval"] == 20
            assert updated_data["timeout_duration"] == 60
            assert updated_data["retry_attempts"] == 5

            # Verify reload was triggered
            hass.config_entries.async_reload.assert_called_once_with(
                mock_config_entry.entry_id
            )

            # Verify flow is aborted with success
            assert result["type"] == FlowResultType.ABORT
            assert result["reason"] == "reconfigure_successful"

    @pytest.mark.asyncio
    async def test_async_step_reconfigure_invalid_ip(
        self, hass: HomeAssistant, config_flow, mock_config_entry
    ):
        """Test reconfigure with invalid IP address shows error."""
        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
        config_flow.context = {"entry_id": mock_config_entry.entry_id}

        # Invalid IP
        user_input = {
            "api_url": "invalid-ip-address",
            "use_ssl": True,
            "polling_interval": 10,
            "timeout_duration": 30,
            "retry_attempts": 3,
        }

        result = await config_flow.async_step_reconfigure(user_input=user_input)

        # Verify form is shown with errors
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reconfigure"
        assert "errors" in result
        assert "api_url" in result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_reconfigure_connection_fails(
        self, hass: HomeAssistant, config_flow, mock_config_entry
    ):
        """Test reconfigure when connection test fails."""
        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
        config_flow.context = {"entry_id": mock_config_entry.entry_id}

        # Mock API test to fail
        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_readings = AsyncMock(side_effect=Exception("Connection failed"))
            mock_api_class.return_value = mock_api

            # New values that won't connect
            user_input = {
                "api_url": "192.168.178.999",  # Non-existent IP
                "use_ssl": True,
                "polling_interval": 10,
                "timeout_duration": 30,
                "retry_attempts": 3,
            }

            result = await config_flow.async_step_reconfigure(user_input=user_input)

            # Verify form is shown with connection error
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "reconfigure"
            assert "errors" in result
            assert "base" in result["errors"]
            assert result["errors"]["base"] == "cannot_connect"

    @pytest.mark.asyncio
    async def test_async_step_reconfigure_partial_update(
        self, hass: HomeAssistant, config_flow, mock_config_entry
    ):
        """Test reconfigure with only some fields changed."""
        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
        hass.config_entries.async_update_entry = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        # Mock API test to succeed
        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_readings = AsyncMock(return_value={"status": "ok"})
            mock_api_class.return_value = mock_api

            config_flow.context = {"entry_id": mock_config_entry.entry_id}

            # Only change polling interval
            user_input = {
                "api_url": "192.168.178.55",  # Same as before
                "use_ssl": True,  # Same as before
                "polling_interval": 30,  # Changed
                "timeout_duration": 30,  # Same
                "retry_attempts": 3,  # Same
            }

            result = await config_flow.async_step_reconfigure(user_input=user_input)

            # Verify entry was updated
            hass.config_entries.async_update_entry.assert_called_once()
            call_args = hass.config_entries.async_update_entry.call_args
            updated_data = call_args[1]["data"]

            # Verify only polling interval changed
            assert updated_data["api_url"] == "192.168.178.55"
            assert updated_data["polling_interval"] == 30
            assert updated_data["timeout_duration"] == 30
            assert updated_data["retry_attempts"] == 3

            assert result["type"] == FlowResultType.ABORT
            assert result["reason"] == "reconfigure_successful"

    @pytest.mark.asyncio
    async def test_async_step_reconfigure_missing_entry(
        self, hass: HomeAssistant, config_flow
    ):
        """Test reconfigure when entry doesn't exist."""
        # Mock that entry doesn't exist
        hass.config_entries.async_get_entry = MagicMock(return_value=None)

        config_flow.context = {"entry_id": "non_existent_entry"}

        result = await config_flow.async_step_reconfigure(user_input=None)

        # Should abort with error
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "reconfigure_failed"

    @pytest.mark.asyncio
    async def test_async_step_reconfigure_preserves_credentials(
        self, hass: HomeAssistant, config_flow, mock_config_entry
    ):
        """Test that reconfigure can update credentials."""
        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
        hass.config_entries.async_update_entry = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        # Mock API test to succeed
        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_readings = AsyncMock(return_value={"status": "ok"})
            mock_api_class.return_value = mock_api

            config_flow.context = {"entry_id": mock_config_entry.entry_id}

            # Update only credentials
            user_input = {
                "api_url": "192.168.178.55",
                "username": "newusername",  # Changed
                "password": "newpassword",  # Changed
                "use_ssl": True,
                "polling_interval": 10,
                "timeout_duration": 30,
                "retry_attempts": 3,
            }

            result = await config_flow.async_step_reconfigure(user_input=user_input)

            # Verify credentials were updated
            call_args = hass.config_entries.async_update_entry.call_args
            updated_data = call_args[1]["data"]

            assert updated_data["username"] == "newusername"
            assert updated_data["password"] == "newpassword"

            assert result["type"] == FlowResultType.ABORT
            assert result["reason"] == "reconfigure_successful"

    @pytest.mark.asyncio
    async def test_async_step_reconfigure_ssl_toggle(
        self, hass: HomeAssistant, config_flow, mock_config_entry
    ):
        """Test reconfigure SSL toggle between HTTP and HTTPS."""
        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
        hass.config_entries.async_update_entry = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        # Mock API test to succeed for both HTTP and HTTPS
        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_readings = AsyncMock(return_value={"status": "ok"})
            mock_api_class.return_value = mock_api

            config_flow.context = {"entry_id": mock_config_entry.entry_id}

            # Test 1: SSL True to False
            user_input_http = {
                "api_url": "192.168.178.55",
                "use_ssl": False,
                "polling_interval": 10,
                "timeout_duration": 30,
                "retry_attempts": 3,
            }

            result_http = await config_flow.async_step_reconfigure(
                user_input=user_input_http
            )

            call_args = hass.config_entries.async_update_entry.call_args
            updated_data = call_args[1]["data"]
            assert updated_data["use_ssl"] is False

            # Test 2: SSL False to True
            hass.config_entries.async_update_entry.reset_mock()

            user_input_https = {
                "api_url": "192.168.178.55",
                "use_ssl": True,
                "polling_interval": 10,
                "timeout_duration": 30,
                "retry_attempts": 3,
            }

            result_https = await config_flow.async_step_reconfigure(
                user_input=user_input_https
            )

            call_args = hass.config_entries.async_update_entry.call_args
            updated_data = call_args[1]["data"]
            assert updated_data["use_ssl"] is True


class TestReconfigureIntegrationScenarios:
    """Test real-world reconfiguration scenarios."""

    @pytest.fixture
    def mock_config_entry(self):
        """Create a mock config entry."""
        entry = MagicMock(spec=ConfigEntry)
        entry.entry_id = "test_entry_id"
        entry.data = {
            "api_url": "192.168.178.55",
            "use_ssl": True,
            "device_name": "Test Pool",
            "controller_name": "Violet",
            "device_id": 1,
        }
        return entry

    @pytest.mark.asyncio
    async def test_reconfigure_after_network_change(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test reconfiguring after router assigns new IP."""
        from custom_components.violet_pool_controller.config_flow import ConfigFlow

        flow = ConfigFlow()
        flow.hass = hass

        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
        hass.config_entries.async_update_entry = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        # Mock successful connection with new IP
        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_readings = AsyncMock(return_value={"status": "ok"})
            mock_api_class.return_value = mock_api

            flow.context = {"entry_id": mock_config_entry.entry_id}

            # User's controller got new IP from router
            user_input = {
                "api_url": "192.168.178.60",  # New IP
                "use_ssl": True,
                "polling_interval": 10,
                "timeout_duration": 30,
                "retry_attempts": 3,
            }

            result = await flow.async_step_reconfigure(user_input=user_input)

            # Should succeed
            assert result["reason"] == "reconfigure_successful"

            # New IP should be saved
            updated_data = hass.config_entries.async_update_entry.call_args[1]["data"]
            assert updated_data["api_url"] == "192.168.178.60"

    @pytest.mark.asyncio
    async def test_reconfigure_timeout_for_slow_network(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test increasing timeout for slow/unreliable network."""
        from custom_components.violet_pool_controller.config_flow import ConfigFlow

        flow = ConfigFlow()
        flow.hass = hass

        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
        hass.config_entries.async_update_entry = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        # Mock API with delay (slow network)
        async def slow_api_call():
            import asyncio

            await asyncio.sleep(0.1)  # Simulate slow network
            return {"status": "ok"}

        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_readings = slow_api_call
            mock_api_class.return_value = mock_api

            flow.context = {"entry_id": mock_config_entry.entry_id}

            # Increase timeout for slow network
            user_input = {
                "api_url": "192.168.178.55",
                "use_ssl": True,
                "polling_interval": 10,
                "timeout_duration": 60,  # Increased from 30 to 60
                "retry_attempts": 5,  # More retries for unreliable network
            }

            result = await flow.async_step_reconfigure(user_input=user_input)

            assert result["reason"] == "reconfigure_successful"

            updated_data = hass.config_entries.async_update_entry.call_args[1]["data"]
            assert updated_data["timeout_duration"] == 60
            assert updated_data["retry_attempts"] == 5

    @pytest.mark.asyncio
    async def test_reconfigure_faster_polling(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test decreasing polling interval for faster updates."""
        from custom_components.violet_pool_controller.config_flow import ConfigFlow

        flow = ConfigFlow()
        flow.hass = hass

        hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
        hass.config_entries.async_update_entry = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.get_readings = AsyncMock(return_value={"status": "ok"})
            mock_api_class.return_value = mock_api

            flow.context = {"entry_id": mock_config_entry.entry_id}

            # Decrease polling for faster updates
            user_input = {
                "api_url": "192.168.178.55",
                "use_ssl": True,
                "polling_interval": 5,  # Faster polling (minimum)
                "timeout_duration": 30,
                "retry_attempts": 3,
            }

            result = await flow.async_step_reconfigure(user_input=user_input)

            assert result["reason"] == "reconfigure_successful"

            updated_data = hass.config_entries.async_update_entry.call_args[1]["data"]
            assert updated_data["polling_interval"] == 5
