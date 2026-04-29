# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024–2026  Xerolux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import aiohttp
import pytest
import pytest_asyncio
from aioresponses import aioresponses
from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError
from violet_poolcontroller_api.circuit_breaker import CircuitBreakerOpenError

@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m

@pytest_asyncio.fixture
async def api_client():
    async with aiohttp.ClientSession() as session:
        # Pass low retry counts to make error tests faster
        api = VioletPoolAPI(
            host="192.168.1.100",
            session=session,
            username="admin",
            password="password",
            max_retries=1
        )
        yield api


@pytest_asyncio.fixture
async def standalone_api_client():
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host="192.168.1.100",
            session=session,
            username="admin",
            password="password",
            max_retries=1,
            dosing_standalone=True,
        )
        yield api

@pytest.mark.asyncio
async def test_get_readings_success(mock_aioresponse, api_client):
    """Test get_readings returns the correct parsed JSON dictionary."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_data = {"PUMPSTATE": "2", "PH": 7.2}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_readings()

    assert isinstance(result, dict)
    assert result == mock_data

@pytest.mark.asyncio
async def test_set_pump_speed_success(mock_aioresponse, api_client):
    """Test set_pump_speed formats the request correctly and returns success."""
    url = "http://192.168.1.100/setFunctionManually?PUMP,ON,0,2"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_pump_speed(speed=2, duration=0)

    assert result["success"] is True
    assert result["response"] == "OK"

@pytest.mark.asyncio
async def test_request_server_error(mock_aioresponse, api_client):
    """Test that a 500 error raises VioletPoolAPIError after retrying."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_aioresponse.get(url, status=500)
    # the second time it retries
    mock_aioresponse.get(url, status=500)

    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.get_readings()

    assert "Error communicating with Violet controller" in str(exc_info.value)

@pytest.mark.asyncio
async def test_init_with_port():
    """Test initializing API with a port in the hostname."""
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host="192.168.1.100:8080",
            session=session,
            username="admin",
            password="password"
        )
        assert api._base_url == "http://192.168.1.100:8080"


@pytest.mark.asyncio
async def test_circuit_breaker_open_is_wrapped(api_client, monkeypatch):
    """Test circuit breaker open errors are exposed as VioletPoolAPIError."""

    async def raise_open(_func, *args, **kwargs):
        raise CircuitBreakerOpenError("Circuit breaker is OPEN")

    monkeypatch.setattr(api_client._circuit_breaker, "call", raise_open)

    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.get_readings()

    assert "Circuit breaker is open" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_specific_readings_requires_valid_categories(api_client):
    """Test that empty category lists are rejected consistently."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.get_specific_readings(["", "   "])

    assert "No valid categories provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_config_rejects_path_traversal_parameter(api_client):
    """Test config payload validation rejects dangerous parameter names."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.set_config({"../../evil": "1"})

    assert "Invalid configuration parameter" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_config_requires_non_empty_keys(api_client):
    """Test whitespace-only config key lists are rejected."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.get_config(["  ", ""])

    assert "No valid configuration keys provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_history_normalizes_hours_and_sensor(api_client, monkeypatch):
    """Test get_history enforces minimum hour value and ALL sensor fallback."""
    captured: dict[str, object] = {}

    async def fake_request(endpoint, **kwargs):
        captured["endpoint"] = endpoint
        captured["params"] = kwargs.get("params")
        return {"ok": True}

    monkeypatch.setattr(api_client, "_request", fake_request)

    result = await api_client.get_history(hours=0, sensor="")

    assert result == {"ok": True}
    assert captured["params"] == {"hours": 1, "sensor": "ALL"}


@pytest.mark.asyncio
async def test_set_config_sanitizes_payload_before_request(api_client, monkeypatch):
    """Test set_config applies sanitizer before sending JSON payload."""
    captured: dict[str, object] = {}

    async def fake_request(endpoint, **kwargs):
        captured["endpoint"] = endpoint
        captured["json_payload"] = kwargs.get("json_payload")
        return "OK"

    monkeypatch.setattr(api_client, "_request", fake_request)

    result = await api_client.set_config({"pool mode": "A<mode>", "speed": 3.7})

    assert result["success"] is True
    assert result["response"] == "OK"
    assert captured["json_payload"] == {"poolmode": "A<mode>", "speed": 3.7}


@pytest.mark.asyncio
async def test_standalone_mode_allows_manual_dosing(
    mock_aioresponse, standalone_api_client
):
    """Standalone mode must still allow dosing outputs."""
    url = "http://192.168.1.100/setFunctionManually?DOS_1_CL,ON,45,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await standalone_api_client.manual_dosing("Chlor", 45)

    assert result["success"] is True
    assert result["response"] == "OK"


@pytest.mark.asyncio
async def test_standalone_mode_blocks_base_module_functions(standalone_api_client):
    """Standalone mode must reject functions that require the base module."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await standalone_api_client.set_pump_speed(speed=2, duration=0)

    assert "requires the Violet base module" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_readings_standalone_list_format(mock_aioresponse, api_client):
    """Test get_readings parses the standalone list format correctly."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_data = {
        "getReadings": [
            {
                "VALUE NAME": "   \"date\"",
                "DESCRIPTION": "System-date",
                "FORMAT": "STRING",
                "DETAILS": "deliverd as TT.MM.YYYY",
                "VALUE": "12.04.2023"
            },
            {
                "VALUE NAME": "   \"CPU_TEMP\"",
                "DESCRIPTION": "CPU-Temperature",
                "FORMAT": "FLOAT",
                "DETAILS": None,
                "VALUE": 45.5
            }
        ]
    }
    mock_aioresponse.get(url, payload=mock_data, status=200)

    assert api_client.dosing_standalone is False

    result = await api_client.get_readings()

    assert isinstance(result, dict)
    assert result == {"date": "12.04.2023", "CPU_TEMP": 45.5}
    assert api_client.dosing_standalone is True


@pytest.mark.asyncio
async def test_dosing_standalone_detection_dict_format(mock_aioresponse, standalone_api_client):
    """Test dosing_standalone is set to False when dict format is received."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_data = {
        "getReadings": {
            "PUMPSTATE": "2",
            "PH": 7.2
        }
    }
    mock_aioresponse.get(url, payload=mock_data, status=200)

    assert standalone_api_client.dosing_standalone is True

    result = await standalone_api_client.get_readings()

    assert isinstance(result, dict)
    assert standalone_api_client.dosing_standalone is False

@pytest.mark.asyncio
async def test_get_hardware_profile(mock_aioresponse, api_client):
    """Test get_hardware_profile correctly detects components via alive counters."""
    url = "http://192.168.1.100/getReadings?ALL"

    # 1. Base module only (no DOS, EXT)
    mock_aioresponse.get(url, payload={"getReadings": {"PUMPSTATE": "2", "SYSTEM_dosagemodule_cpu_temperature": "N/A"}}, status=200)
    profile = await api_client.get_hardware_profile()
    assert profile == {
        "base_module": True,
        "dosing_module": False,
        "extension_module_1": False,
        "extension_module_2": False,
    }

    # 2. Base module + Dosing + Ext1 (via alive counters)
    mock_aioresponse.get(url, payload={"getReadings": {
        "PUMPSTATE": "2",
        "SYSTEM_dosagemodule_alive_count": "20392243",
        "SYSTEM_dosagemodule_cpu_temperature": 45.5,
        "SYSTEM_ext1module_alive_count": "52443888",
        "EXT1_1": "1",
    }}, status=200)
    profile = await api_client.get_hardware_profile()
    assert profile == {
        "base_module": True,
        "dosing_module": True,
        "extension_module_1": True,
        "extension_module_2": False,
    }

    # 3. Base module + Ext1 + Ext2 (via alive counters, no Dosing)
    mock_aioresponse.get(url, payload={"getReadings": {
        "PUMPSTATE": "2",
        "SYSTEM_ext1module_alive_count": "100",
        "SYSTEM_ext2module_alive_count": "200",
        "EXT1_1": "1",
        "EXT2_1": "1",
    }}, status=200)
    profile = await api_client.get_hardware_profile()
    assert profile == {
        "base_module": True,
        "dosing_module": False,
        "extension_module_1": True,
        "extension_module_2": True,
    }

    # 4. Real-world scenario: EXT2 relay data present (value 0) but no ext2 module
    #    Controller always returns EXT2_* keys even when the module is absent.
    mock_aioresponse.get(url, payload={"getReadings": {
        "PUMPSTATE": "2",
        "SYSTEM_dosagemodule_alive_count": "20392243",
        "SYSTEM_ext1module_alive_count": "52443888",
        "EXT1_1": 0, "EXT1_2": 0,
        "EXT2_1": 0, "EXT2_2": 0,
        "EXT2_1_LAST_ON": 0, "EXT2_1_LAST_OFF": 0,
    }}, status=200)
    profile = await api_client.get_hardware_profile()
    assert profile["extension_module_1"] is True
    assert profile["extension_module_2"] is False

@pytest.mark.asyncio
async def test_set_switch_state_ext1_relay(mock_aioresponse, api_client):
    """Test set_switch_state sends correct URL for EXT1_2 ON, OFF, and AUTO."""
    base = "http://192.168.1.100/setFunctionManually"

    mock_aioresponse.get(f"{base}?EXT1_2,ON,0,0", body="OK", status=200)
    result = await api_client.set_switch_state("EXT1_2", "ON")
    assert result["success"] is True

    mock_aioresponse.get(f"{base}?EXT1_2,OFF,0,0", body="OK", status=200)
    result = await api_client.set_switch_state("EXT1_2", "OFF")
    assert result["success"] is True

    mock_aioresponse.get(f"{base}?EXT1_2,AUTO,0,0", body="OK", status=200)
    result = await api_client.set_switch_state("EXT1_2", "AUTO")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_module_alive_on_zero_count(mock_aioresponse, api_client):
    """EXT1 module must be detected when alive_count key is present but value is 0.

    The alive counter starts at 0 immediately after a controller restart.  The
    old code required value > 0, which caused EXT1_* readings to be filtered
    and the relay switch to appear broken right after a restart.
    """
    url = "http://192.168.1.100/getReadings?ALL"
    mock_aioresponse.get(url, payload={"getReadings": {
        "PUMPSTATE": "2",
        "SYSTEM_ext1module_alive_count": "0",
        "EXT1_1": 0,
        "EXT1_2": 0,
    }}, status=200)

    result = await api_client.get_readings()
    assert "EXT1_2" in result, (
        "EXT1_2 must not be filtered when SYSTEM_ext1module_alive_count is present, "
        "even if the counter is still 0 after a restart"
    )


@pytest.mark.asyncio
async def test_ext1_readings_not_filtered_when_detected(mock_aioresponse, api_client):
    """EXT1_* readings are included when extension_module_1 is detected."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_aioresponse.get(url, payload={"getReadings": {
        "PUMPSTATE": "2",
        "SYSTEM_ext1module_alive_count": "12345",
        "EXT1_1": 1,
        "EXT1_2": 0,
        "EXT1_3": 0,
    }}, status=200)

    result = await api_client.get_readings()
    assert "EXT1_1" in result
    assert "EXT1_2" in result
    assert "EXT1_3" in result


@pytest.mark.asyncio
async def test_ext1_readings_filtered_when_not_detected(mock_aioresponse, api_client):
    """EXT1_* readings are stripped when extension_module_1 key is absent."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_aioresponse.get(url, payload={"getReadings": {
        "PUMPSTATE": "2",
        # No SYSTEM_ext1module_alive_count → module not connected
        "EXT1_1": 0,
        "EXT1_2": 0,
    }}, status=200)

    result = await api_client.get_readings()
    assert "EXT1_1" not in result
    assert "EXT1_2" not in result


@pytest.mark.asyncio
async def test_get_hardware_profile_standalone_dosing(mock_aioresponse, standalone_api_client):
    """Test get_hardware_profile with a standalone dosing configuration."""
    url = "http://192.168.1.100/getReadings?ALL"
    # Using the standalone list format
    mock_data = {
        "getReadings": [
            {
                "VALUE NAME": "   \"DOS_1_CL\"",
                "DESCRIPTION": "Current state of OUTPUT: CL-DOSING",
                "FORMAT": "INTEGER",
                "DETAILS": "0 - AUTO (not on)",
                "VALUE": 2
            }
        ]
    }
    mock_aioresponse.get(url, payload=mock_data, status=200)

    profile = await standalone_api_client.get_hardware_profile()
    assert profile == {
        "base_module": False,
        "dosing_module": True,
        "extension_module_1": False,
        "extension_module_2": False,
    }
