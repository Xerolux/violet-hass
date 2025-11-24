"""Tests for Violet Pool Controller Device with Auto-Recovery."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.device import VioletPoolControllerDevice


class TestVioletPoolControllerDevice:
    """Test VioletPoolControllerDevice with Recovery."""

    @pytest.fixture
    def mock_hass(self):
        """Create mock Home Assistant instance."""
        hass = MagicMock()
        hass.data = {}
        return hass

    @pytest.fixture
    def mock_api(self):
        """Create mock API instance."""
        api = MagicMock()
        api.get_readings = AsyncMock(return_value={"test": "data"})
        api.get_specific_readings = AsyncMock(return_value={"test": "data"})
        return api

    @pytest.fixture
    def config_entry(self):
        """Create mock config entry."""
        return MockConfigEntry(
            domain=DOMAIN,
            title="Test Pool",
            data={
                CONF_API_URL: "192.168.178.55",
                CONF_USE_SSL: False,
                CONF_DEVICE_ID: 1,
                CONF_DEVICE_NAME: "Test Pool Controller",
                CONF_CONTROLLER_NAME: "Test Pool",
            },
        )

    @pytest.fixture
    def device(self, mock_hass, config_entry, mock_api):
        """Create device instance."""
        with patch("custom_components.violet_pool_controller.device.async_get_clientsession", return_value=MagicMock()):
            device = VioletPoolControllerDevice(
                hass=mock_hass,
                config_entry=config_entry,
                api=mock_api,
            )
            return device

    async def test_recovery_lock_initialized(self, device):
        """Test dass Recovery-Lock korrekt initialisiert wird."""
        assert device._recovery_lock is not None, "Recovery-Lock sollte initialisiert sein"
        assert isinstance(device._recovery_lock, asyncio.Lock), "Sollte asyncio.Lock sein"

    async def test_recovery_race_condition_prevented(self, device):
        """Test dass Race Condition bei Recovery verhindert wird."""
        # Mock _fetch_controller_data
        device._fetch_controller_data = AsyncMock(return_value={"test": "data"})
        device._in_recovery_mode = False # Ensure false start

        # Starte zwei Recovery-Versuche parallel
        # Wir müssen sicherstellen, dass sie "gleichzeitig" den Lock erreichen
        # Aber asyncio ist single threaded.
        # Wir können prüfen, ob der zweite sofort returned.

        # Da wir im Test sind, rufen wir _attempt_recovery direkt auf.

        task1 = asyncio.create_task(device._attempt_recovery())
        task2 = asyncio.create_task(device._attempt_recovery())

        # Beide Tasks ausführen
        results = await asyncio.gather(task1, task2)

        # Nur einer sollte erfolgreich sein (True), der andere sollte False zurückgeben
        # (weil bereits im Recovery-Modus oder Lock gehalten)
        # Wait, if both succeed (because data fetch works), one might return True and other False?
        # If lock works:
        # T1 gets lock. Sets in_recovery_mode = True. Releases lock (wait, no).
        # T1 holds lock, checks in_recovery.
        # T1 sets in_recovery = True.
        # T1 releases lock? No, `async with self._recovery_lock:` scope.
        # The logic in `_attempt_recovery`:
        # async with self._recovery_lock:
        #    if self._in_recovery_mode: return False
        #    self._in_recovery_mode = True
        # ... do stuff ...
        # finally: self._in_recovery_mode = False

        # So T1 enters lock, sets flag, EXITS lock.
        # T2 enters lock, sees flag, returns False.
        # T1 continues recovery.

        # So yes, one should be True (the one that proceeded), one False.

        assert results.count(True) == 1, f"Nur ein Recovery-Versuch sollte erfolgreich sein, got {results}"
        assert results.count(False) == 1, "Ein Recovery-Versuch sollte abgelehnt werden"

    async def test_recovery_exponential_backoff(self, device):
        """Test dass Exponential Backoff korrekt berechnet wird."""
        device._fetch_controller_data = AsyncMock(return_value={"test": "data"})
        # We need to ensure we don't actually sleep for real time

        # Erster Versuch
        device._recovery_attempts = 0
        device._in_recovery_mode = False
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await device._attempt_recovery()
            # Erster Versuch: 10s * 2^0 = 10s
            mock_sleep.assert_called_once()
            # call_args[0][0] is the first positional arg
            assert mock_sleep.call_args[0][0] == 10.0

        # Zweiter Versuch
        device._in_recovery_mode = False
        device._recovery_attempts = 1
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await device._attempt_recovery()
            # Zweiter Versuch: 10s * 2^1 = 20s
            assert mock_sleep.call_args[0][0] == 20.0

        # Fünfter Versuch
        device._in_recovery_mode = False
        device._recovery_attempts = 4
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await device._attempt_recovery()
            # Fünfter Versuch: 10s * 2^4 = 160s
            assert mock_sleep.call_args[0][0] == 160.0

    async def test_recovery_max_delay_cap(self, device):
        """Test dass Recovery Delay bei 300s gekappt wird."""
        device._fetch_controller_data = AsyncMock(return_value={"test": "data"})

        # Sehr hoher Versuch (sollte 10 * 2^10 = 10240s ergeben, aber bei 300s gekappt werden)
        device._in_recovery_mode = False
        device._recovery_attempts = 10

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await device._attempt_recovery()
            # Sollte bei 300s (RECOVERY_MAX_DELAY) gekappt sein
            assert mock_sleep.call_args[0][0] == 300.0

    async def test_controller_name_in_device_info(self, device):
        """Test dass Controller-Name in device_info verwendet wird."""
        device_info = device.device_info

        assert device_info["name"] == "Test Pool", "device_info sollte Controller-Name verwenden"
        assert device_info["suggested_area"] == "Test Pool", "suggested_area sollte Controller-Name sein"

    async def test_device_info_dynamic_updates(self, device):
        """Test dass device_info bei Options-Änderung aktualisiert wird."""
        # Initial
        initial_info = device.device_info
        assert initial_info["name"] == "Test Pool"

        # Simuliere Options-Änderung
        device.controller_name = "Neuer Pool Name"

        # Device-Info sollte sofort neuen Namen zeigen (kein Caching!)
        updated_info = device.device_info
        assert updated_info["name"] == "Neuer Pool Name"
        assert updated_info["suggested_area"] == "Neuer Pool Name"

    async def test_recovery_success_resets_counters(self, device):
        """Test dass erfolgreiche Recovery Zähler zurücksetzt."""
        device._fetch_controller_data = AsyncMock(return_value={"test": "data"})
        device._consecutive_failures = 5
        device._recovery_attempts = 3
        device._in_recovery_mode = False

        # Recovery durchführen
        # We need to mock sleep to avoid waiting
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await device._attempt_recovery()

        # Sollte erfolgreich sein
        assert result is True

        # Zähler sollten zurückgesetzt sein
        assert device._consecutive_failures == 0
        assert device._recovery_attempts == 0
        assert device._available is True
