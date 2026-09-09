"""Tests for VioletControlClient, the facade over the public API.

The client used to build ``FUNCTION,ACTION`` payloads itself and post them
through the API client's private ``_request``, which skipped the API's
duration validation, its dosing routing, the cover safety gate and the auth
guard - and got the cover grammar wrong.  These tests assert the opposite:
every method reaches the controller through a *public* API method.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from violet_poolcontroller_api.api import VioletPoolAPIError

from custom_components.violet_pool_controller.http_control import VioletControlClient

OK = {"success": True, "response": "OK"}
NOT_OK = {"success": False, "response": "ERROR"}


@pytest.fixture
def api():
    """Return a mock API exposing only the public methods the client may use."""
    api = MagicMock()
    api.set_switch_state = AsyncMock(return_value=OK)
    api.set_cover_command = AsyncMock(return_value=OK)
    api.set_config = AsyncMock(return_value=OK)
    return api


@pytest.fixture
def client(api):
    """Return a client wrapping the mock API."""
    return VioletControlClient(api)


class TestPumpControl:
    """Pump commands go through set_switch_state, never through _request."""

    async def test_set_pump_speed_valid(self, client, api):
        for speed in (1, 2, 3):
            api.set_switch_state.reset_mock()
            assert await client.set_pump_speed(speed) is True
            api.set_switch_state.assert_awaited_once_with("PUMP", "ON", last_value=speed)

    async def test_set_pump_speed_zero_is_rejected(self, client):
        """Speed 0 would be sent as "manual ON at speed 0", which is not off."""
        with pytest.raises(ValueError, match="1-3"):
            await client.set_pump_speed(0)

    async def test_set_pump_speed_too_high(self, client):
        with pytest.raises(ValueError, match="1-3"):
            await client.set_pump_speed(4)

    async def test_set_pump_off(self, client, api):
        assert await client.set_pump_off() is True
        api.set_switch_state.assert_awaited_once_with("PUMP", "OFF")

    async def test_unsuccessful_command_returns_false(self, client, api):
        api.set_switch_state.return_value = NOT_OK
        assert await client.set_pump_off() is False

    async def test_api_error_propagates(self, client, api):
        api.set_switch_state.side_effect = VioletPoolAPIError("API down")
        with pytest.raises(VioletPoolAPIError, match="API down"):
            await client.set_pump_off()


class TestHeaterSolarControl:
    """Heater and solar commands."""

    async def test_set_heater_on(self, client, api):
        assert await client.set_heater_on() is True
        api.set_switch_state.assert_awaited_once_with("HEATER", "ON")

    async def test_set_heater_off(self, client, api):
        await client.set_heater_off()
        api.set_switch_state.assert_awaited_once_with("HEATER", "OFF")

    async def test_set_solar_on(self, client, api):
        await client.set_solar_on()
        api.set_switch_state.assert_awaited_once_with("SOLAR", "ON")

    async def test_set_solar_off(self, client, api):
        await client.set_solar_off()
        api.set_switch_state.assert_awaited_once_with("SOLAR", "OFF")


class TestCoverControl:
    """Cover commands use the API's guarded cover entry point."""

    @pytest.mark.parametrize("method,action", [("open", "OPEN"), ("close", "CLOSE"), ("stop", "STOP")])
    async def test_cover_commands(self, client, api, method, action):
        assert await getattr(client, f"set_cover_{method}")() is True
        api.set_cover_command.assert_awaited_once_with(action, acknowledge_unsafe=True)

    async def test_cover_never_uses_set_switch_state_directly(self, client, api):
        """The wrong grammar ("COVER,OPEN") must not come back."""
        await client.set_cover_open()
        api.set_switch_state.assert_not_awaited()


class TestBackwashControl:
    """Backwash commands."""

    async def test_set_backwash_run(self, client, api):
        assert await client.set_backwash_run(120) is True
        api.set_switch_state.assert_awaited_once_with("BACKWASH", "ON", duration=120)

    async def test_set_backwash_abort(self, client, api):
        await client.set_backwash_abort()
        api.set_switch_state.assert_awaited_once_with("BACKWASH", "OFF")


class TestTriggerManualDosing:
    """Manual dosing is routed by the API, not re-implemented here."""

    async def test_dosstart_maps_index_to_key(self, client, api):
        assert await client.trigger_manual_dosing(0, 30) is True
        api.set_switch_state.assert_awaited_once_with("DOS_1_CL", "ON", duration=30)

    async def test_dosstart_other_channels(self, client, api):
        for index, key in ((1, "DOS_2_ELO"), (3, "DOS_4_PHM"), (4, "DOS_5_PHP"), (5, "DOS_6_FLOC")):
            api.set_switch_state.reset_mock()
            await client.trigger_manual_dosing(index, 15)
            api.set_switch_state.assert_awaited_once_with(key, "ON", duration=15)

    async def test_dosstop(self, client, api):
        assert await client.trigger_manual_dosing(0, 0, action="DOSSTOP") is True
        api.set_switch_state.assert_awaited_once_with("DOS_1_CL", "OFF")

    async def test_invalid_action(self, client):
        with pytest.raises(ValueError, match="DOSSTART.*DOSSTOP"):
            await client.trigger_manual_dosing(0, 30, action="INVALID")

    async def test_unknown_index(self, client):
        with pytest.raises(ValueError, match="Dosing index"):
            await client.trigger_manual_dosing(2, 30)

    async def test_unsupported_source_is_rejected(self, client, api):
        """from=3 (H2O2) has no public API path and must not dose chlorine."""
        with pytest.raises(ValueError, match="not supported"):
            await client.trigger_manual_dosing(0, 30, from_param=3)
        api.set_switch_state.assert_not_awaited()

    async def test_failed_command_returns_false(self, client, api):
        api.set_switch_state.return_value = NOT_OK
        assert await client.trigger_manual_dosing(0, 30) is False

    async def test_api_error_propagates(self, client, api):
        api.set_switch_state.side_effect = VioletPoolAPIError("fail")
        with pytest.raises(VioletPoolAPIError, match="fail"):
            await client.trigger_manual_dosing(0, 30)


class TestSetConfig:
    """set_config normalises flag values before handing them to the API."""

    async def test_success(self, client, api):
        assert await client.set_config({"POOL_SETPOINT": 28.0}) is True

    async def test_failure(self, client, api):
        api.set_config.return_value = NOT_OK
        assert await client.set_config({"POOL_SETPOINT": 28.0}) is False

    async def test_bool_normalization(self, client, api):
        await client.set_config({"EXT1_1_use": True, "EXT1_2_use": False})
        sent = api.set_config.call_args[0][0]
        assert sent == {"EXT1_1_use": 1, "EXT1_2_use": 0}
        assert isinstance(sent["EXT1_1_use"], int)

    async def test_use_key_float_normalization(self, client, api):
        await client.set_config({"EXT1_1_use": 1.0, "EXT1_2_use": 0.0})
        sent = api.set_config.call_args[0][0]
        assert sent == {"EXT1_1_use": 1, "EXT1_2_use": 0}

    async def test_enabled_key_normalization(self, client, api):
        await client.set_config({"HEATER_enabled": 1.0})
        assert api.set_config.call_args[0][0]["HEATER_enabled"] == 1

    async def test_non_special_keys_pass_through(self, client, api):
        await client.set_config({"POOL_SETPOINT": 28.5, "PH_target": 7.2})
        sent = api.set_config.call_args[0][0]
        assert sent == {"POOL_SETPOINT": 28.5, "PH_target": 7.2}

    async def test_api_error_propagates(self, client, api):
        api.set_config.side_effect = VioletPoolAPIError("fail")
        with pytest.raises(VioletPoolAPIError, match="fail"):
            await client.set_config({"KEY": "value"})


class TestNoPrivateApiUse:
    """The facade must never reach into the API client's private surface."""

    async def test_request_is_never_called(self, api):
        api._request = AsyncMock()
        client = VioletControlClient(api)
        await client.set_pump_speed(2)
        await client.set_heater_on()
        await client.set_cover_open()
        await client.trigger_manual_dosing(0, 30)
        await client.set_config({"KEY": 1})
        api._request.assert_not_awaited()
