"""Tests for Violet Pool Controller API with Rate Limiting."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.violet_pool_controller.api import VioletPoolAPI, VioletPoolAPIError
from custom_components.violet_pool_controller.const import (
    API_PRIORITY_CRITICAL,
    API_PRIORITY_HIGH,
    API_PRIORITY_NORMAL,
)


class TestVioletPoolAPI:
    """Test VioletPoolAPI with Rate Limiting."""

    @pytest.fixture
    def mock_session(self):
        """Create mock aiohttp session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        return session

    @pytest.fixture
    def api(self, mock_session):
        """Create API instance with mocked session."""
        return VioletPoolAPI(
            host="192.168.178.55",
            session=mock_session,
            username="test",
            password="test",
            use_ssl=False,
            timeout=10,
            max_retries=3,
        )

    async def test_rate_limiter_initialized(self, api):
        """Test dass Rate Limiter korrekt initialisiert wird."""
        assert api._rate_limiter is not None, "Rate Limiter sollte initialisiert sein"

    async def test_rate_limiting_active(self, api, mock_session):
        """Test dass Rate Limiting bei Requests aktiv ist."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"success": true}')
        mock_response.json = AsyncMock(return_value={"success": True})

        # Setup context manager
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # session.request is NOT async, it returns an async context manager
        mock_session.request = MagicMock(return_value=mock_response)

        # Mock Rate Limiter
        with patch.object(api._rate_limiter, 'wait_if_needed', new_callable=AsyncMock) as mock_wait:
            # Führe Request aus
            result = await api._request("/test", expect_json=True)

            # Prüfe dass wait_if_needed aufgerufen wurde
            mock_wait.assert_called_once()
            assert result == {"success": True}

    async def test_rate_limiting_with_priorities(self, api, mock_session):
        """Test dass verschiedene Prioritäten korrekt weitergegeben werden."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")

        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request = MagicMock(return_value=mock_response)

        with patch.object(api._rate_limiter, 'wait_if_needed', new_callable=AsyncMock) as mock_wait:
            # Test Critical Priority
            await api._request("/critical", priority=API_PRIORITY_CRITICAL)
            mock_wait.assert_called_with(priority=API_PRIORITY_CRITICAL, timeout=10.0)

            # Test High Priority
            await api._request("/high", priority=API_PRIORITY_HIGH)
            mock_wait.assert_called_with(priority=API_PRIORITY_HIGH, timeout=10.0)

            # Test Normal Priority (Default)
            await api._request("/normal")
            mock_wait.assert_called_with(priority=API_PRIORITY_NORMAL, timeout=10.0)

    async def test_rate_limiter_timeout_handling(self, api, mock_session):
        """Test dass Timeout im Rate Limiter korrekt behandelt wird."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")

        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request = MagicMock(return_value=mock_response)

        # Simuliere Rate Limiter Timeout
        with patch.object(
            api._rate_limiter,
            'wait_if_needed',
            side_effect=asyncio.TimeoutError("Rate limiter timeout")
        ):
            # Request sollte trotzdem durchgehen (nur Warning)
            result = await api._request("/test")
            assert result == "OK", "Request sollte trotz Rate Limiter Timeout durchgehen"

    async def test_api_error_handling(self, api, mock_session):
        """Test dass API-Fehler korrekt behandelt werden."""
        # Mock error response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request = MagicMock(return_value=mock_response)

        with patch.object(api._rate_limiter, 'wait_if_needed', new_callable=AsyncMock):
            # Sollte VioletPoolAPIError werfen
            with pytest.raises(VioletPoolAPIError, match="HTTP 500"):
                await api._request("/error")

    async def test_json_parsing_error_handling(self, api, mock_session):
        """Test dass JSON-Parsing-Fehler korrekt behandelt werden."""
        # Mock invalid JSON response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="Invalid JSON")
        mock_response.json = AsyncMock(side_effect=aiohttp.ContentTypeError(
            MagicMock(), MagicMock()
        ))

        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request = MagicMock(return_value=mock_response)

        with patch.object(api._rate_limiter, 'wait_if_needed', new_callable=AsyncMock):
            # Sollte VioletPoolAPIError werfen
            with pytest.raises(VioletPoolAPIError, match="Invalid JSON"):
                await api._request("/test", expect_json=True)
