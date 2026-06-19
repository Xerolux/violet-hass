"""Tests for VioletControlClient HTTP control layer."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from violet_poolcontroller_api.api import VioletPoolAPIError

from custom_components.violet_pool_controller.http_control import VioletControlClient


class TestSetFunctionManually:
    """Test the core set_function_manually method."""

    @pytest.fixture
    def client(self):
        """Create a VioletControlClient with a mock API."""
        api = MagicMock()
        api._request = AsyncMock()
        return VioletControlClient(api)

    async def test_success_with_response(self, client):
        """Non-empty response returns True."""
        client.api._request.return_value = "OK\nPUMP\nON"
        result = await client.set_function_manually("PUMP", "ON")
        assert result is True
        client.api._request.assert_awaited_once()
        call_args = client.api._request.call_args
        assert "/setFunctionManually?PUMP,ON" in call_args[0][0]

    async def test_success_with_param(self, client):
        """Command includes param when provided."""
        client.api._request.return_value = "OK"
        result = await client.set_function_manually("PUMP", "ON", 3)
        assert result is True
        call_args = client.api._request.call_args
        assert "/setFunctionManually?PUMP,ON,3" in call_args[0][0]

    async def test_failure_empty_response(self, client):
        """Empty/falsy response returns False."""
        client.api._request.return_value = ""
        result = await client.set_function_manually("PUMP", "OFF")
        assert result is False

    async def test_failure_none_response(self, client):
        """None response returns False."""
        client.api._request.return_value = None
        result = await client.set_function_manually("HEATER", "ON")
        assert result is False

    async def test_violet_api_error_propagates(self, client):
        """VioletPoolAPIError is re-raised."""
        client.api._request.side_effect = VioletPoolAPIError("API down")
        with pytest.raises(VioletPoolAPIError, match="API down"):
            await client.set_function_manually("PUMP", "ON")

    async def test_timeout_error_wrapped(self, client):
        """TimeoutError is wrapped into VioletPoolAPIError."""
        client.api._request.side_effect = TimeoutError()
        with pytest.raises(VioletPoolAPIError, match="Timeout"):
            await client.set_function_manually("PUMP", "ON")

    async def test_generic_exception_wrapped(self, client):
        """Generic exceptions are wrapped into VioletPoolAPIError."""
        client.api._request.side_effect = RuntimeError("unexpected")
        with pytest.raises(VioletPoolAPIError, match="Error executing"):
            await client.set_function_manually("PUMP", "ON")

    async def test_uses_get_method(self, client):
        """Request uses GET method."""
        client.api._request.return_value = "OK"
        await client.set_function_manually("SOLAR", "ON")
        assert client.api._request.call_args[1]["method"] == "GET"


class TestPumpControl:
    """Test pump control helpers."""

    @pytest.fixture
    def client(self):
        """Create a VioletControlClient with a mock API."""
        api = MagicMock()
        api._request = AsyncMock(return_value="OK")
        return VioletControlClient(api)

    async def test_set_pump_speed_valid(self, client):
        """Valid speed levels 0-3 are accepted."""
        for speed in range(4):
            client.api._request.reset_mock()
            result = await client.set_pump_speed(speed)
            assert result is True
            call_url = client.api._request.call_args[0][0]
            assert f"PUMP,ON,{speed}" in call_url

    async def test_set_pump_speed_too_high(self, client):
        """Speed > 3 raises ValueError."""
        with pytest.raises(ValueError, match="0-3"):
            await client.set_pump_speed(4)

    async def test_set_pump_speed_negative(self, client):
        """Speed < 0 raises ValueError."""
        with pytest.raises(ValueError, match="0-3"):
            await client.set_pump_speed(-1)

    async def test_set_pump_off(self, client):
        """set_pump_off sends PUMP OFF command."""
        result = await client.set_pump_off()
        assert result is True
        call_url = client.api._request.call_args[0][0]
        assert "PUMP,OFF" in call_url


class TestHeaterSolarControl:
    """Test heater and solar control helpers."""

    @pytest.fixture
    def client(self):
        """Create a VioletControlClient with a mock API."""
        api = MagicMock()
        api._request = AsyncMock(return_value="OK")
        return VioletControlClient(api)

    async def test_set_heater_on(self, client):
        result = await client.set_heater_on()
        assert result is True
        assert "HEATER,ON" in client.api._request.call_args[0][0]

    async def test_set_heater_off(self, client):
        result = await client.set_heater_off()
        assert result is True
        assert "HEATER,OFF" in client.api._request.call_args[0][0]

    async def test_set_solar_on(self, client):
        result = await client.set_solar_on()
        assert result is True
        assert "SOLAR,ON" in client.api._request.call_args[0][0]

    async def test_set_solar_off(self, client):
        result = await client.set_solar_off()
        assert result is True
        assert "SOLAR,OFF" in client.api._request.call_args[0][0]


class TestCoverControl:
    """Test cover control helpers."""

    @pytest.fixture
    def client(self):
        """Create a VioletControlClient with a mock API."""
        api = MagicMock()
        api._request = AsyncMock(return_value="OK")
        return VioletControlClient(api)

    async def test_set_cover_open(self, client):
        result = await client.set_cover_open()
        assert result is True
        assert "COVER,OPEN" in client.api._request.call_args[0][0]

    async def test_set_cover_close(self, client):
        result = await client.set_cover_close()
        assert result is True
        assert "COVER,CLOSE" in client.api._request.call_args[0][0]

    async def test_set_cover_stop(self, client):
        result = await client.set_cover_stop()
        assert result is True
        assert "COVER,STOP" in client.api._request.call_args[0][0]


class TestBackwashControl:
    """Test backwash control helpers."""

    @pytest.fixture
    def client(self):
        """Create a VioletControlClient with a mock API."""
        api = MagicMock()
        api._request = AsyncMock(return_value="OK")
        return VioletControlClient(api)

    async def test_set_backwash_run(self, client):
        result = await client.set_backwash_run()
        assert result is True
        assert "BACKWASH,RUN" in client.api._request.call_args[0][0]

    async def test_set_backwash_abort(self, client):
        result = await client.set_backwash_abort()
        assert result is True
        assert "BACKWASH,ABORT" in client.api._request.call_args[0][0]


class TestTriggerManualDosing:
    """Test manual dosing trigger."""

    @pytest.fixture
    def client(self):
        """Create a VioletControlClient with a mock API."""
        api = MagicMock()
        api._request = AsyncMock()
        return VioletControlClient(api)

    async def test_dosstart_success(self, client):
        """DOSSTART with MANDOS_STARTED response returns True."""
        client.api._request.return_value = "MANDOS_STARTED\nOK"
        result = await client.trigger_manual_dosing(0, 30)
        assert result is True
        assert client.api._request.call_args[1]["method"] == "POST"
        form = client.api._request.call_args[1]["data"]
        assert form["action"] == "DOSSTART"
        assert form["output"] == "0"
        assert form["runtime"] == "30"

    async def test_dosstart_ok_response(self, client):
        """\\nOK response also indicates success."""
        client.api._request.return_value = "something\nOK"
        result = await client.trigger_manual_dosing(1, 15)
        assert result is True

    async def test_dosstop_success(self, client):
        """DOSSTOP with MANDOS_STOPPED response returns True."""
        client.api._request.return_value = "MANDOS_STOPPED"
        result = await client.trigger_manual_dosing(0, 0, action="DOSSTOP")
        assert result is True
        form = client.api._request.call_args[1]["data"]
        assert form["action"] == "DOSSTOP"

    async def test_pump_off_error(self, client):
        """PUMP_OFF_ERROR response returns False."""
        client.api._request.return_value = "PUMP_OFF_ERROR"
        result = await client.trigger_manual_dosing(0, 30)
        assert result is False

    async def test_backwash_error(self, client):
        """BACKWASH_ERROR response returns False."""
        client.api._request.return_value = "BACKWASH_ERROR"
        result = await client.trigger_manual_dosing(0, 30)
        assert result is False

    async def test_unexpected_response(self, client):
        """Unexpected response returns False."""
        client.api._request.return_value = "SOMETHING_ELSE"
        result = await client.trigger_manual_dosing(0, 30)
        assert result is False

    async def test_invalid_action(self, client):
        """Unknown action raises ValueError."""
        with pytest.raises(ValueError, match="DOSSTART.*DOSSTOP"):
            await client.trigger_manual_dosing(0, 30, action="INVALID")

    async def test_invalid_index_high(self, client):
        """Index > 5 raises ValueError."""
        with pytest.raises(ValueError, match="0-5"):
            await client.trigger_manual_dosing(6, 30)

    async def test_invalid_index_negative(self, client):
        """Index < 0 raises ValueError."""
        with pytest.raises(ValueError, match="0-5"):
            await client.trigger_manual_dosing(-1, 30)

    async def test_dosstart_zero_runtime(self, client):
        """DOSSTART with 0 runtime raises ValueError."""
        with pytest.raises(ValueError, match="Runtime must be > 0"):
            await client.trigger_manual_dosing(0, 0)

    async def test_runtime_formatted(self, client):
        """Runtime is formatted as MM:SS."""
        client.api._request.return_value = "MANDOS_STARTED"
        await client.trigger_manual_dosing(0, 125)
        form = client.api._request.call_args[1]["data"]
        assert form["runtime_formatted"] == "02:05"

    async def test_from_param(self, client):
        """from_param is passed through to form data."""
        client.api._request.return_value = "MANDOS_STARTED"
        await client.trigger_manual_dosing(0, 30, from_param=3)
        form = client.api._request.call_args[1]["data"]
        assert form["from"] == "3"

    async def test_timeout_wrapped(self, client):
        """TimeoutError is wrapped into VioletPoolAPIError."""
        client.api._request.side_effect = TimeoutError()
        with pytest.raises(VioletPoolAPIError, match="Timeout"):
            await client.trigger_manual_dosing(0, 30)

    async def test_api_error_propagates(self, client):
        """VioletPoolAPIError propagates unchanged."""
        client.api._request.side_effect = VioletPoolAPIError("fail")
        with pytest.raises(VioletPoolAPIError, match="fail"):
            await client.trigger_manual_dosing(0, 30)


class TestSetConfig:
    """Test set_config with value normalization."""

    @pytest.fixture
    def client(self):
        """Create a VioletControlClient with a mock API."""
        api = MagicMock()
        api.set_config = AsyncMock()
        return VioletControlClient(api)

    async def test_success(self, client):
        """Successful config update returns True."""
        client.api.set_config.return_value = True
        result = await client.set_config({"POOL_SETPOINT": 28.0})
        assert result is True

    async def test_failure(self, client):
        """Failed config update returns False."""
        client.api.set_config.return_value = False
        result = await client.set_config({"POOL_SETPOINT": 28.0})
        assert result is False

    async def test_bool_normalization(self, client):
        """Boolean values are converted to int (True->1, False->0)."""
        client.api.set_config.return_value = True
        await client.set_config({"EXT1_1_use": True, "EXT1_2_use": False})
        sent = client.api.set_config.call_args[0][0]
        assert sent["EXT1_1_use"] == 1
        assert sent["EXT1_2_use"] == 0
        assert isinstance(sent["EXT1_1_use"], int)

    async def test_use_key_float_normalization(self, client):
        """Float values for *_use keys are normalized to int."""
        client.api.set_config.return_value = True
        await client.set_config({"EXT1_1_use": 1.0, "EXT1_2_use": 0.0})
        sent = client.api.set_config.call_args[0][0]
        assert sent["EXT1_1_use"] == 1
        assert sent["EXT1_2_use"] == 0

    async def test_enabled_key_normalization(self, client):
        """Float values for *_enabled keys are normalized to int."""
        client.api.set_config.return_value = True
        await client.set_config({"HEATER_enabled": 1.0})
        sent = client.api.set_config.call_args[0][0]
        assert sent["HEATER_enabled"] == 1

    async def test_non_special_keys_pass_through(self, client):
        """Non-use/enabled keys are passed unchanged."""
        client.api.set_config.return_value = True
        await client.set_config({"POOL_SETPOINT": 28.5, "PH_target": 7.2})
        sent = client.api.set_config.call_args[0][0]
        assert sent["POOL_SETPOINT"] == 28.5
        assert sent["PH_target"] == 7.2

    async def test_api_error_propagates(self, client):
        """VioletPoolAPIError propagates."""
        client.api.set_config.side_effect = VioletPoolAPIError("fail")
        with pytest.raises(VioletPoolAPIError, match="fail"):
            await client.set_config({"KEY": "value"})
