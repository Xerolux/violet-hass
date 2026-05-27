# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024-2026  Xerolux
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

"""Tests for the VioletPoolAPI client."""

# ruff: noqa: S101

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Never

import aiohttp
import pytest
import pytest_asyncio
from aioresponses import aioresponses

from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError
from violet_poolcontroller_api.circuit_breaker import CircuitBreakerOpenError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


@pytest.fixture
def mock_aioresponse() -> Generator[aioresponses, None, None]:
    """Provide a mocked aioresponses context for HTTP mocking."""
    with aioresponses() as m:
        yield m

@pytest_asyncio.fixture
async def api_client() -> AsyncGenerator[VioletPoolAPI, None]:
    """Provide a VioletPoolAPI instance with low retries for fast error tests."""
    async with aiohttp.ClientSession() as session:
        # Pass low retry counts to make error tests faster
        api = VioletPoolAPI(
            host="192.168.1.100",
            session=session,
            username="admin",
            password="password",  # noqa: S106
            max_retries=1,
        )
        yield api


@pytest_asyncio.fixture
async def standalone_api_client() -> AsyncGenerator[VioletPoolAPI, None]:
    """Provide a VioletPoolAPI instance configured for dosing-standalone mode."""
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host="192.168.1.100",
            session=session,
            username="admin",
            password="password",  # noqa: S106
            max_retries=1,
            dosing_standalone=True,
        )
        yield api

@pytest.mark.asyncio
async def test_get_readings_success(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test get_readings returns the correct parsed JSON dictionary."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_data = {"PUMPSTATE": "2", "PH": 7.2}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_readings()

    assert isinstance(result, dict)
    assert result == mock_data

@pytest.mark.asyncio
async def test_set_pump_speed_success(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_pump_speed formats the request correctly and returns success."""
    url = "http://192.168.1.100/setFunctionManually?PUMP,ON,0,2"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_pump_speed(speed=2, duration=0)

    assert result["success"] is True
    assert result["response"] == "OK"

@pytest.mark.asyncio
async def test_request_server_error(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test that a 500 error raises VioletPoolAPIError after retrying."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_aioresponse.get(url, status=500)
    # the second time it retries
    mock_aioresponse.get(url, status=500)

    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.get_readings()

    assert "Error communicating with Violet controller" in str(exc_info.value)

@pytest.mark.asyncio
async def test_init_with_port() -> None:
    """Test initializing API with a port in the hostname."""
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host="192.168.1.100:8080",
            session=session,
            username="admin",
            password="password",  # noqa: S106
        )
        assert api._base_url == "http://192.168.1.100:8080"  # noqa: SLF001


@pytest.mark.asyncio
async def test_circuit_breaker_open_is_wrapped(
    api_client: VioletPoolAPI, monkeypatch: pytest.Monkeypatch,
) -> None:
    """Test circuit breaker open errors are exposed as VioletPoolAPIError."""

    async def raise_open(_func: Any, *_args: Any, **_kwargs: Any) -> Never:  # noqa: ANN401
        msg = "Circuit breaker is OPEN"
        raise CircuitBreakerOpenError(msg)

    monkeypatch.setattr(api_client._circuit_breaker, "call", raise_open)  # noqa: SLF001

    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.get_readings()

    assert "Circuit breaker is open" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_specific_readings_requires_valid_categories(
    api_client: VioletPoolAPI,
) -> None:
    """Test that empty category lists are rejected consistently."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.get_specific_readings(["", "   "])

    assert "No valid categories provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_config_rejects_path_traversal_parameter(
    api_client: VioletPoolAPI,
) -> None:
    """Test config payload validation rejects dangerous parameter names."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.set_config({"../../evil": "1"})

    assert "Invalid configuration parameter" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_config_requires_non_empty_keys(api_client: VioletPoolAPI) -> None:
    """Test whitespace-only config key lists are rejected."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.get_config(["  ", ""])

    assert "No valid configuration keys provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_history_normalizes_hours_and_sensor(
    api_client: VioletPoolAPI, monkeypatch: pytest.Monkeypatch,
) -> None:
    """Test get_history enforces minimum hour value and ALL sensor fallback."""
    captured: dict[str, object] = {}

    async def fake_request(endpoint: str, **kwargs: Any) -> dict[str, bool]:  # noqa: ANN401
        captured["endpoint"] = endpoint
        captured["params"] = kwargs.get("params")
        return {"ok": True}

    monkeypatch.setattr(api_client, "_request", fake_request)

    result = await api_client.get_history(hours=0, sensor="")

    assert result == {"ok": True}
    assert captured["params"] == {"hours": 1, "sensor": "ALL"}


@pytest.mark.asyncio
async def test_set_config_sanitizes_payload_before_request(
    api_client: VioletPoolAPI, monkeypatch: pytest.Monkeypatch,
) -> None:
    """Test set_config applies sanitizer before sending JSON payload."""
    captured: dict[str, object] = {}

    async def fake_request(endpoint: str, **kwargs: Any) -> str:  # noqa: ANN401
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
    mock_aioresponse: aioresponses, standalone_api_client: VioletPoolAPI,
) -> None:
    """Standalone mode must still allow dosing outputs."""
    url = "http://192.168.1.100/setFunctionManually?DOS_1_CL,ON,45,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await standalone_api_client.manual_dosing("Chlor", 45)

    assert result["success"] is True
    assert result["response"] == "OK"


@pytest.mark.asyncio
async def test_standalone_mode_blocks_base_module_functions(
    standalone_api_client: VioletPoolAPI,
) -> None:
    """Standalone mode must reject functions that require the base module."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await standalone_api_client.set_pump_speed(speed=2, duration=0)

    assert "requires the Violet base module" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_readings_standalone_list_format(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test get_readings parses the standalone list format correctly."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_data = {
        "getReadings": [
            {
                "VALUE NAME": '   "date"',
                "DESCRIPTION": "System-date",
                "FORMAT": "STRING",
                "DETAILS": "deliverd as TT.MM.YYYY",
                "VALUE": "12.04.2023",
            },
            {
                "VALUE NAME": '   "CPU_TEMP"',
                "DESCRIPTION": "CPU-Temperature",
                "FORMAT": "FLOAT",
                "DETAILS": None,
                "VALUE": 45.5,
            },
        ],
    }
    mock_aioresponse.get(url, payload=mock_data, status=200)

    assert api_client.dosing_standalone is False

    result = await api_client.get_readings()

    assert isinstance(result, dict)
    assert result == {"date": "12.04.2023", "CPU_TEMP": 45.5}
    assert api_client.dosing_standalone is True


@pytest.mark.asyncio
async def test_dosing_standalone_detection_dict_format(
    mock_aioresponse: aioresponses, standalone_api_client: VioletPoolAPI,
) -> None:
    """Test dosing_standalone is set to False when dict format is received."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_data = {
        "getReadings": {
            "PUMPSTATE": "2",
            "PH": 7.2,
        },
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


@pytest.mark.asyncio
async def test_timeout_property(api_client: VioletPoolAPI) -> None:
    """Test that timeout property returns the configured value."""
    assert api_client.timeout == 10.0


@pytest.mark.asyncio
async def test_max_retries_property(api_client: VioletPoolAPI) -> None:
    """Test that max_retries property returns the configured value."""
    assert api_client.max_retries == 1


@pytest.mark.asyncio
async def test_dosing_standalone_property_false(api_client: VioletPoolAPI) -> None:
    """Test dosing_standalone returns False for standard client."""
    assert api_client.dosing_standalone is False


@pytest.mark.asyncio
async def test_dosing_standalone_property_true(
    standalone_api_client: VioletPoolAPI,
) -> None:
    """Test dosing_standalone returns True for standalone client."""
    assert standalone_api_client.dosing_standalone is True


@pytest.mark.asyncio
async def test_get_weather_data(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test get_weather_data returns weather information from controller."""
    url = "http://192.168.1.100/getWeatherdata"
    mock_data = {"temp": 25.0, "condition": "sunny"}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_weather_data()

    assert result == mock_data


@pytest.mark.asyncio
async def test_get_overall_dosing(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test get_overall_dosing returns aggregated dosing statistics."""
    url = "http://192.168.1.100/getOverallDosing"
    mock_data = {"CL": 120, "PHM": 45}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_overall_dosing()

    assert result == mock_data


@pytest.mark.asyncio
async def test_get_output_states(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test get_output_states returns detailed output state information."""
    url = "http://192.168.1.100/getOutputstates"
    mock_data = {"PUMP": 2, "LIGHT": 0}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_output_states()

    assert result == mock_data


@pytest.mark.asyncio
async def test_get_calibration_raw_values(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test get_calibration_raw_values returns raw sensor calibration data."""
    url = "http://192.168.1.100/getCalibRawValues"
    mock_data = {"pH_raw": 512, "ORP_raw": 750}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_calibration_raw_values()

    assert result == mock_data


@pytest.mark.asyncio
async def test_get_calibration_history(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test get_calibration_history parses pipe-separated text response."""
    url = "http://192.168.1.100/getCalibHistory?pH"
    body = "2024-01-01 | 7.2 | pH_CALIB\n2024-01-02 | 750 | ORP_CALIB"
    mock_aioresponse.get(url, body=body, status=200)

    result = await api_client.get_calibration_history("pH")

    assert len(result) == 2
    assert result[0] == {"timestamp": "2024-01-01", "value": "7.2", "type": "pH_CALIB"}
    assert result[1] == {"timestamp": "2024-01-02", "value": "750", "type": "ORP_CALIB"}


@pytest.mark.asyncio
async def test_restore_calibration(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test restore_calibration sends correct payload and returns success."""
    url = "http://192.168.1.100/restoreOldCalib"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.restore_calibration("pH", "2024-01-01")

    assert result["success"] is True
    assert result["response"] == "OK"


@pytest.mark.asyncio
async def test_restore_calibration_missing_sensor(
    api_client: VioletPoolAPI,
) -> None:
    """Test restore_calibration raises error when sensor is missing."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.restore_calibration("", "2024-01-01")

    assert "Sensor and timestamp are required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_restore_calibration_missing_timestamp(
    api_client: VioletPoolAPI,
) -> None:
    """Test restore_calibration raises error when timestamp is missing."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.restore_calibration("pH", "")

    assert "Sensor and timestamp are required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_output_test_mode(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_output_test_mode sends correct command with default values."""
    url = "http://192.168.1.100/setOutputTestmode?EXT1_1,SWITCH,120000"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_output_test_mode(output="EXT1_1")

    assert result["success"] is True
    assert result["response"] == "OK"


@pytest.mark.asyncio
async def test_set_output_test_mode_missing_output(
    api_client: VioletPoolAPI,
) -> None:
    """Test set_output_test_mode raises error when output is missing."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.set_output_test_mode(output="")

    assert "Output identifier is required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_pv_surplus_enable(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_pv_surplus enables PV surplus mode."""
    url = "http://192.168.1.100/setFunctionManually?PVSURPLUS,ON,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_pv_surplus(active=True)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_pv_surplus_disable(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_pv_surplus disables PV surplus mode."""
    url = "http://192.168.1.100/setFunctionManually?PVSURPLUS,OFF,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_pv_surplus(active=False)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_all_dmx_scenes_alloff(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_all_dmx_scenes sends ALLOFF to all 12 DMX scenes."""
    for i in range(1, 13):
        url = f"http://192.168.1.100/setFunctionManually?DMX_SCENE{i},ALLOFF,0,0"
        mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_all_dmx_scenes("ALLOFF")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_all_dmx_scenes_invalid_action(
    api_client: VioletPoolAPI,
) -> None:
    """Test set_all_dmx_scenes raises error for unsupported action."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.set_all_dmx_scenes("INVALID")

    assert "Unsupported DMX action" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_light_color_pulse(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_light_color_pulse triggers COLOR action on LIGHT output."""
    url = "http://192.168.1.100/setFunctionManually?LIGHT,COLOR,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_light_color_pulse()

    assert result["success"] is True


@pytest.mark.asyncio
async def test_trigger_digital_input_rule(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test trigger_digital_input_rule sends PUSH action for the rule."""
    url = "http://192.168.1.100/setFunctionManually?DIRULE_1,PUSH,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.trigger_digital_input_rule("DIRULE_1")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_digital_input_rule_lock(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_digital_input_rule_lock locks a digital input rule."""
    url = "http://192.168.1.100/setFunctionManually?DIRULE_1,LOCK,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_digital_input_rule_lock("DIRULE_1", locked=True)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_digital_input_rule_unlock(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_digital_input_rule_lock unlocks a digital input rule."""
    url = "http://192.168.1.100/setFunctionManually?DIRULE_1,UNLOCK,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_digital_input_rule_lock("DIRULE_1", locked=False)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_device_temperature(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_device_temperature sends correct target temperature."""
    url = "http://192.168.1.100/setTargetValues?target=HEATER_TARGET_TEMP&value=28.0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_device_temperature("HEATER", 28.0)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_ph_target(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_ph_target sends correct pH target value."""
    url = "http://192.168.1.100/setTargetValues?target=pH&value=7.2"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_ph_target(7.2)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_orp_target(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_orp_target sends correct ORP target value."""
    url = "http://192.168.1.100/setTargetValues?target=ORP&value=750"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_orp_target(750)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_min_chlorine_level(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_min_chlorine_level sends correct chlorine target value."""
    url = "http://192.168.1.100/setTargetValues?target=MinChlorine&value=0.5"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_min_chlorine_level(0.5)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_target_value(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_target_value sends generic target value update."""
    url = "http://192.168.1.100/setTargetValues?target=CUSTOM&value=42.0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_target_value("CUSTOM", 42.0)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_dosing_parameters(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test set_dosing_parameters sends POST with dosing configuration."""
    url = "http://192.168.1.100/setDosingParameters"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.set_dosing_parameters({"DOS_1_CL_DOSING_TIME": 30})

    assert result["success"] is True


@pytest.mark.asyncio
async def test_control_pump(
    mock_aioresponse: aioresponses, api_client: VioletPoolAPI,
) -> None:
    """Test control_pump sends correct pump action command."""
    url = "http://192.168.1.100/setFunctionManually?PUMP,OFF,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.control_pump("OFF")

    assert result["success"] is True
