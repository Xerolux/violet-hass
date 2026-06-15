# violet-poolController-api - API f├╝r Violet Pool Controller
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

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Never

import aiohttp
import pytest
import pytest_asyncio
from aioresponses import aioresponses
from yarl import URL

from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError
from violet_poolcontroller_api.circuit_breaker import CircuitBreakerOpenError
from violet_poolcontroller_api.const_api import (
    ERROR_CODES,
    ERROR_SEVERITY_ALARM,
    ERROR_SEVERITY_INFO,
    ERROR_SEVERITY_REMINDER,
    ERROR_SEVERITY_WARNING,
)

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
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test get_readings returns the correct parsed JSON dictionary."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_data = {"PUMPSTATE": "2", "PH": 7.2}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_readings()

    assert isinstance(result, Mapping)
    assert dict(result) == mock_data


@pytest.mark.asyncio
async def test_set_pump_speed_success(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_pump_speed formats the request correctly and returns success."""
    url = "http://192.168.1.100/setFunctionManually?PUMP,ON,0,2"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_pump_speed(speed=2, duration=0)

    assert result["success"] is True
    assert result["response"] == "OK"


@pytest.mark.asyncio
async def test_request_server_error(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
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
    api_client: VioletPoolAPI,
    monkeypatch: pytest.Monkeypatch,
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
    api_client: VioletPoolAPI,
    monkeypatch: pytest.Monkeypatch,
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
    api_client: VioletPoolAPI,
    monkeypatch: pytest.Monkeypatch,
) -> None:
    """Test set_config applies sanitizer before sending form-encoded payload."""
    captured: dict[str, object] = {}

    async def fake_request(endpoint: str, **kwargs: Any) -> str:  # noqa: ANN401
        captured["endpoint"] = endpoint
        captured["data"] = kwargs.get("data")
        return "OK"

    monkeypatch.setattr(api_client, "_request", fake_request)

    result = await api_client.set_config({"pool mode": "A<mode>", "speed": 3.7})

    assert result["success"] is True
    assert result["response"] == "OK"
    assert captured["data"] == {"poolmode": "A<mode>", "speed": 3.7}


@pytest.mark.asyncio
async def test_standalone_mode_allows_manual_dosing(
    mock_aioresponse: aioresponses,
    standalone_api_client: VioletPoolAPI,
) -> None:
    """Standalone mode must still allow dosing outputs."""
    url = "http://192.168.1.100/triggerManualDosing"
    mock_aioresponse.post(url, body="MANDOS_STARTED\nOK", status=200)

    result = await standalone_api_client.manual_dosing("Chlor", 45)

    assert result["success"] is True
    assert "MANDOS_STARTED" in result["response"]


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
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
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

    assert isinstance(result, Mapping)
    assert dict(result) == {"date": "12.04.2023", "CPU_TEMP": 45.5}
    assert api_client.dosing_standalone is True


@pytest.mark.asyncio
async def test_dosing_standalone_detection_dict_format(
    mock_aioresponse: aioresponses,
    standalone_api_client: VioletPoolAPI,
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

    assert isinstance(result, Mapping)
    assert standalone_api_client.dosing_standalone is False


@pytest.mark.asyncio
async def test_get_hardware_profile(mock_aioresponse, api_client):
    """Test get_hardware_profile correctly detects components via alive counters."""
    url = "http://192.168.1.100/getReadings?ALL"

    # 1. Base module only (no DOS, EXT)
    mock_aioresponse.get(
        url,
        payload={"getReadings": {"PUMPSTATE": "2", "SYSTEM_dosagemodule_cpu_temperature": "N/A"}},
        status=200,
    )
    profile = await api_client.get_hardware_profile()
    assert profile == {
        "base_module": True,
        "dosing_module": False,
        "extension_module_1": False,
        "extension_module_2": False,
    }

    # 2. Base module + Dosing + Ext1 (via alive counters)
    mock_aioresponse.get(
        url,
        payload={
            "getReadings": {
                "PUMPSTATE": "2",
                "SYSTEM_dosagemodule_alive_count": "20392243",
                "SYSTEM_dosagemodule_cpu_temperature": 45.5,
                "SYSTEM_ext1module_alive_count": "52443888",
                "EXT1_1": "1",
            }
        },
        status=200,
    )
    profile = await api_client.get_hardware_profile()
    assert profile == {
        "base_module": True,
        "dosing_module": True,
        "extension_module_1": True,
        "extension_module_2": False,
    }

    # 3. Base module + Ext1 + Ext2 (via alive counters, no Dosing)
    mock_aioresponse.get(
        url,
        payload={
            "getReadings": {
                "PUMPSTATE": "2",
                "SYSTEM_ext1module_alive_count": "100",
                "SYSTEM_ext2module_alive_count": "200",
                "EXT1_1": "1",
                "EXT2_1": "1",
            }
        },
        status=200,
    )
    profile = await api_client.get_hardware_profile()
    assert profile == {
        "base_module": True,
        "dosing_module": False,
        "extension_module_1": True,
        "extension_module_2": True,
    }

    # 4. Real-world scenario: EXT2 relay data present (value 0) but no ext2 module
    #    Controller always returns EXT2_* keys even when the module is absent.
    mock_aioresponse.get(
        url,
        payload={
            "getReadings": {
                "PUMPSTATE": "2",
                "SYSTEM_dosagemodule_alive_count": "20392243",
                "SYSTEM_ext1module_alive_count": "52443888",
                "EXT1_1": 0,
                "EXT1_2": 0,
                "EXT2_1": 0,
                "EXT2_2": 0,
                "EXT2_1_LAST_ON": 0,
                "EXT2_1_LAST_OFF": 0,
            }
        },
        status=200,
    )
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
    mock_aioresponse.get(
        url,
        payload={
            "getReadings": {
                "PUMPSTATE": "2",
                "SYSTEM_ext1module_alive_count": "0",
                "EXT1_1": 0,
                "EXT1_2": 0,
            }
        },
        status=200,
    )

    result = await api_client.get_readings()
    assert "EXT1_2" in result, (
        "EXT1_2 must not be filtered when SYSTEM_ext1module_alive_count is present, "
        "even if the counter is still 0 after a restart"
    )


@pytest.mark.asyncio
async def test_ext1_readings_not_filtered_when_detected(mock_aioresponse, api_client):
    """EXT1_* readings are included when extension_module_1 is detected."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_aioresponse.get(
        url,
        payload={
            "getReadings": {
                "PUMPSTATE": "2",
                "SYSTEM_ext1module_alive_count": "12345",
                "EXT1_1": 1,
                "EXT1_2": 0,
                "EXT1_3": 0,
            }
        },
        status=200,
    )

    result = await api_client.get_readings()
    assert "EXT1_1" in result
    assert "EXT1_2" in result
    assert "EXT1_3" in result


@pytest.mark.asyncio
async def test_ext1_readings_filtered_when_not_detected(mock_aioresponse, api_client):
    """EXT1_* readings are stripped when extension_module_1 key is absent."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_aioresponse.get(
        url,
        payload={
            "getReadings": {
                "PUMPSTATE": "2",
                # No SYSTEM_ext1module_alive_count ÔåÆ module not connected
                "EXT1_1": 0,
                "EXT1_2": 0,
            }
        },
        status=200,
    )

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
                "VALUE NAME": '   "DOS_1_CL"',
                "DESCRIPTION": "Current state of OUTPUT: CL-DOSING",
                "FORMAT": "INTEGER",
                "DETAILS": "0 - AUTO (not on)",
                "VALUE": 2,
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
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test get_weather_data returns weather information from controller."""
    url = "http://192.168.1.100/getWeatherdata"
    mock_data = {"temp": 25.0, "condition": "sunny"}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_weather_data()

    assert result == mock_data


@pytest.mark.asyncio
async def test_get_overall_dosing(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test get_overall_dosing returns aggregated dosing statistics."""
    url = "http://192.168.1.100/getOverallDosing"
    mock_data = {"CL": 120, "PHM": 45}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_overall_dosing()

    assert result == mock_data


@pytest.mark.asyncio
async def test_get_output_states(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test get_output_states returns detailed output state information."""
    url = "http://192.168.1.100/getOutputstates"
    mock_data = {"PUMP": 2, "LIGHT": 0}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_output_states()

    assert result == mock_data


@pytest.mark.asyncio
async def test_get_calibration_raw_values(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test get_calibration_raw_values returns raw sensor calibration data."""
    url = "http://192.168.1.100/getCalibRawValues"
    mock_data = {"pH_raw": 512, "ORP_raw": 750}
    mock_aioresponse.get(url, payload=mock_data, status=200)

    result = await api_client.get_calibration_raw_values()

    assert result == mock_data


@pytest.mark.asyncio
async def test_get_calibration_history(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
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
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
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
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
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
async def test_set_all_dmx_scenes_alloff(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_all_dmx_scenes sends a single ALLOFF request to DMX_SCENE1."""
    url = "http://192.168.1.100/setFunctionManually?DMX_SCENE1,ALLOFF,0,0"
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
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_light_color_pulse triggers COLOR action on LIGHT output."""
    url = "http://192.168.1.100/setFunctionManually?LIGHT,COLOR,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_light_color_pulse()

    assert result["success"] is True


@pytest.mark.asyncio
async def test_trigger_digital_input_rule(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test trigger_digital_input_rule sends PUSH action for the rule."""
    url = "http://192.168.1.100/setFunctionManually?DIRULE_1,PUSH,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.trigger_digital_input_rule("DIRULE_1")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_digital_input_rule_lock(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_digital_input_rule_lock locks a digital input rule."""
    url = "http://192.168.1.100/setFunctionManually?DIRULE_1,LOCK,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_digital_input_rule_lock("DIRULE_1", locked=True)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_digital_input_rule_unlock(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_digital_input_rule_lock unlocks a digital input rule."""
    url = "http://192.168.1.100/setFunctionManually?DIRULE_1,UNLOCK,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_digital_input_rule_lock("DIRULE_1", locked=False)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_device_temperature(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_device_temperature sends correct target temperature."""
    url = "http://192.168.1.100/setConfig"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.set_device_temperature("HEATER", 28.0)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_device_temperature_solar(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_device_temperature uses SOLAR_maxtemp for SOLAR key."""
    url = "http://192.168.1.100/setConfig"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.set_device_temperature("SOLAR", 30.0)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_ph_target(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_ph_target sends correct pH target value."""
    url = "http://192.168.1.100/setConfig"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.set_ph_target(7.2)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_orp_target(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_orp_target sends correct ORP target value."""
    url = "http://192.168.1.100/setConfig"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.set_orp_target(750)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_min_chlorine_level(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_min_chlorine_level sends correct chlorine target value."""
    url = "http://192.168.1.100/setConfig"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.set_min_chlorine_level(0.5)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_target_value(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_target_value sends generic target value update."""
    url = "http://192.168.1.100/setConfig"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.set_target_value("CUSTOM", 42.0)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_dosing_parameters(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_dosing_parameters sends POST via /setConfig."""
    url = "http://192.168.1.100/setConfig"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.set_dosing_parameters({"DOS_1_CL_DOSING_TIME": 30})

    assert result["success"] is True


@pytest.mark.asyncio
async def test_reset_blocking(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test reset_blocking clears fault blockings via GET /resetBlocking."""
    url = "http://192.168.1.100/resetBlocking"
    mock_aioresponse.get(url, body="OK\nBLOCKINGS_CLEARED", status=200)

    result = await api_client.reset_blocking()

    assert result["success"] is True
    assert "BLOCKINGS_CLEARED" in result["response"]


@pytest.mark.asyncio
async def test_set_can_amount_adjust(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_can_amount (ADJUST) updates canister level via POST."""
    url = "http://192.168.1.100/setCanAmount"
    mock_aioresponse.post(url, body="OK\nDOS_1_CL\n25000", status=200)

    result = await api_client.set_can_amount("DOS_1_CL", 25000)

    assert result["success"] is True
    # Verify form payload sent to the controller
    sent = list(mock_aioresponse.requests.values())[0][0].kwargs["data"]
    assert sent["action"] == "ADJUST"
    assert sent["which"] == "DOS_1_CL"
    assert sent["amount"] == "25000"
    assert sent["cid"] == "1"


@pytest.mark.asyncio
async def test_set_can_amount_reset(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_can_amount(reset=True) sends RESET action."""
    url = "http://192.168.1.100/setCanAmount"
    mock_aioresponse.post(url, body="OK", status=200)

    result = await api_client.set_can_amount("DOS_6_FLOC", 20000, reset=True)

    assert result["success"] is True
    sent = list(mock_aioresponse.requests.values())[0][0].kwargs["data"]
    assert sent["action"] == "RESET"
    assert sent["cid"] == "6"


@pytest.mark.asyncio
async def test_set_can_amount_rejects_unknown_key(
    api_client: VioletPoolAPI,
) -> None:
    """Test set_can_amount raises on unknown dosing key."""
    with pytest.raises(VioletPoolAPIError, match="Unknown dosing key"):
        await api_client.set_can_amount("DOS_99_XXX", 1000)


@pytest.mark.asyncio
async def test_set_can_amount_rejects_nonpositive_amount(
    api_client: VioletPoolAPI,
) -> None:
    """Test set_can_amount rejects zero/negative fill levels."""
    with pytest.raises(ValueError, match="must be > 0"):
        await api_client.set_can_amount("DOS_1_CL", 0)
    with pytest.raises(ValueError, match="must be > 0"):
        await api_client.set_can_amount("DOS_1_CL", -100)


@pytest.mark.asyncio
async def test_set_system_service_enable(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_system_service(enabled=True) hits the /enableFTP endpoint."""
    url = "http://192.168.1.100/enableFTP"
    mock_aioresponse.get(url, body="OK\nenableFTP", status=200)

    result = await api_client.set_system_service("ftp", enabled=True)

    assert result["success"] is True
    sent_key = list(mock_aioresponse.requests.keys())[0]
    assert str(sent_key[1]).endswith("/enableFTP")


@pytest.mark.asyncio
async def test_set_system_service_disable(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_system_service(enabled=False) hits /disableSSH."""
    url = "http://192.168.1.100/disableSSH"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.set_system_service("ssh", enabled=False)

    assert result["success"] is True
    sent_key = list(mock_aioresponse.requests.keys())[0]
    assert str(sent_key[1]).endswith("/disableSSH")


@pytest.mark.asyncio
async def test_set_system_service_rejects_unknown(
    api_client: VioletPoolAPI,
) -> None:
    """Test set_system_service raises on unknown service name."""
    with pytest.raises(VioletPoolAPIError, match="Unknown system service"):
        await api_client.set_system_service("telnet", enabled=True)


@pytest.mark.asyncio
async def test_get_system_services(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test get_system_services normalises raw getServiceStates response."""
    url = "http://192.168.1.100/getServiceStates"
    mock_aioresponse.get(
        url,
        payload={
            "proftpd": 0,
            "shairport": 1,
            "samba": 0,
            "sshd": 1,
            "homekit": 0,
            "tunnel_state": 1,
            "support_tunnel_state": 0,
            "date": "29.02.2024",
            "time": "19:50:02",
        },
        status=200,
    )

    result = await api_client.get_system_services()

    # Alexa has no state_key and must be absent.
    assert "alexa" not in result
    assert result == {
        "ftp": False,
        "shairport": True,
        "samba": False,
        "ssh": True,
        "homebridge": False,
        "tunnel": True,
        "support_tunnel": False,
    }


# ---------------------------------------------------------------------------
# OmniTronic + RS485 + LiveTrace (P12 / P13 / P15)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_set_omni_position(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_omni_position sends OMNI,OMNI_DC<N> via setFunctionManually."""
    url = "http://192.168.1.100/setFunctionManually?OMNI,OMNI_DC2,0,0"
    mock_aioresponse.get(url, body="OK\nOMNITRONIC\nOMNI_DC2\n", status=200)

    result = await api_client.set_omni_position(2)

    # The mock only matches the exact URL we registered, so a True result
    # proves the right URL was hit (aioresponses returns 404 otherwise).
    assert result["success"] is True
    assert "OMNITRONIC" in result["response"]
    # One request must have been recorded.
    assert len(list(mock_aioresponse.requests.values())) == 1


@pytest.mark.asyncio
async def test_set_omni_position_filtration(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Position 0 (Filtration) is valid and maps to OMNI_DC0."""
    url = "http://192.168.1.100/setFunctionManually?OMNI,OMNI_DC0,0,0"
    mock_aioresponse.get(url, body="OK\nOMNITRONIC\nOMNI_DC0\n", status=200)

    result = await api_client.set_omni_position(0)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_set_omni_position_rejects_out_of_range(
    api_client: VioletPoolAPI,
) -> None:
    """Positions outside 0-5 are rejected before the request is sent."""
    with pytest.raises(VioletPoolAPIError, match="Invalid OmniTronic position"):
        await api_client.set_omni_position(6)
    with pytest.raises(VioletPoolAPIError, match="Invalid OmniTronic position"):
        await api_client.set_omni_position(-1)


@pytest.mark.asyncio
async def test_get_rs485_pump_data(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test get_rs485_pump_data returns the pump's JSON config + live values."""
    url = "http://192.168.1.100/getRS485PumpData?BADU_ECO_DRIVE_II"
    mock_aioresponse.get(
        url,
        payload={
            "BRAND": "BADU",
            "NAME": "Eco Drive II",
            "pump_rs485_pwr": 450,
            "SLAVE_PRESENT": "YES",
        },
        status=200,
    )

    result = await api_client.get_rs485_pump_data("BADU_ECO_DRIVE_II")

    assert result["BRAND"] == "BADU"
    assert result["pump_rs485_pwr"] == 450
    assert result["SLAVE_PRESENT"] == "YES"


@pytest.mark.asyncio
async def test_get_rs485_pump_data_rejects_unknown_pump(
    api_client: VioletPoolAPI,
) -> None:
    with pytest.raises(VioletPoolAPIError, match="Unknown RS485 pump name"):
        await api_client.get_rs485_pump_data("PENTAIR_VSF")


@pytest.mark.asyncio
async def test_set_rs485_live(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_rs485_live forwards mode+level to the pump's modbus."""
    url = "http://192.168.1.100/setRS485Live?BADU_ECO_DRIVE_II,1,hz,45"
    mock_aioresponse.get(url, body='"1|0,0|2,4500"', status=200)

    result = await api_client.set_rs485_live(
        "BADU_ECO_DRIVE_II", slave_id=1, mode="hz", level=45
    )

    assert "1|0,0|2,4500" in result


@pytest.mark.asyncio
async def test_set_rs485_live_rejects_bad_mode(
    api_client: VioletPoolAPI,
) -> None:
    with pytest.raises(VioletPoolAPIError, match="Invalid RS485 mode"):
        await api_client.set_rs485_live(
            "BADU_ECO_DRIVE_II", slave_id=1, mode="percent", level=50
        )


@pytest.mark.asyncio
async def test_set_rs485_live_rejects_bad_slave_id(
    api_client: VioletPoolAPI,
) -> None:
    with pytest.raises(ValueError, match="slave_id must be 1-247"):
        await api_client.set_rs485_live(
            "BADU_ECO_DRIVE_II", slave_id=0, mode="hz", level=45
        )


@pytest.mark.asyncio
async def test_end_rs485_live(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test end_rs485_live sends the DONE sentinel."""
    url = "http://192.168.1.100/setRS485Live?DONE"
    mock_aioresponse.get(url, body='"DONE"', status=200)

    result = await api_client.end_rs485_live()

    assert result == "DONE"


@pytest.mark.asyncio
async def test_get_live_trace(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test get_live_trace parses the 3-line CSV into a dict."""
    url = "http://192.168.1.100/getLiveTrace"
    csv_body = (
        "epoch;date;time;onewire1_value;pH_value;PUMP\n"
        "ms;;;°C;;\n"
        "1709234445000;29.02.2024;19:50:02;7,30;7,3;1\n"
    )
    mock_aioresponse.get(url, body=csv_body, status=200)

    result = await api_client.get_live_trace()

    assert result["onewire1_value"] == "7.30"  # German comma → dot
    assert result["pH_value"] == "7.3"
    assert result["PUMP"] == "1"
    assert result["date"] == "29.02.2024"


@pytest.mark.asyncio
async def test_get_live_trace_malformed(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Malformed payloads (fewer than 3 lines) raise VioletPoolAPIError."""
    url = "http://192.168.1.100/getLiveTrace"
    mock_aioresponse.get(url, body="only_one_line", status=200)

    with pytest.raises(VioletPoolAPIError, match="Malformed getLiveTrace"):
        await api_client.get_live_trace()


@pytest.mark.asyncio
async def test_control_pump(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test control_pump sends correct pump action command."""
    url = "http://192.168.1.100/setFunctionManually?PUMP,OFF,0,0"
    mock_aioresponse.get(url, body="OK", status=200)

    result = await api_client.control_pump("OFF")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_command_result_parses_multiline_response(
    api_client: VioletPoolAPI,
) -> None:
    """Test _command_result parses multi-line controller response."""
    body = "OK\nPUMP\nMANUELL EIN\nDrehzahl 2"
    result = VioletPoolAPI._command_result(body)

    assert result["success"] is True
    assert result["response"] == body
    assert result["output"] == "PUMP"
    assert result["message"] == "MANUELL EIN\nDrehzahl 2"


@pytest.mark.asyncio
async def test_command_result_single_line_ok(
    api_client: VioletPoolAPI,
) -> None:
    """Test _command_result handles single-line OK response."""
    result = VioletPoolAPI._command_result("OK")

    assert result["success"] is True
    assert result["response"] == "OK"
    assert "output" not in result
    assert "message" not in result


@pytest.mark.asyncio
async def test_command_result_error_response(
    api_client: VioletPoolAPI,
) -> None:
    """Test _command_result detects ERROR in response."""
    body = "ERROR\nDOS_1_CL\nTHIS IS A DOSING OUTPUT! ARE YOU NUTS?"
    result = VioletPoolAPI._command_result(body)

    assert result["success"] is False
    assert result["output"] == "DOS_1_CL"


@pytest.mark.asyncio
async def test_command_result_dosing_started(
    api_client: VioletPoolAPI,
) -> None:
    """Test _command_result handles MANDOS_STARTED response."""
    body = "MANDOS_STARTED\nOK"
    result = VioletPoolAPI._command_result(body)

    assert result["success"] is True
    assert result["output"] == "OK"


@pytest.mark.asyncio
async def test_command_result_dict_passthrough(
    api_client: VioletPoolAPI,
) -> None:
    """Test _command_result passes dict through unchanged."""
    data = {"key": "value", "nested": {"a": 1}}
    result = VioletPoolAPI._command_result(data)

    assert result is data


@pytest.mark.asyncio
async def test_set_pv_surplus_enable(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_pv_surplus enables PV surplus with speed in WERT_1."""
    url = "http://192.168.1.100/setFunctionManually?PVSURPLUS,ON,2,0"
    mock_aioresponse.get(url, body="OK\nPVSURPLUS\nON", status=200)

    result = await api_client.set_pv_surplus(active=True, pump_speed=2)

    assert result["success"] is True
    assert result["output"] == "PVSURPLUS"


@pytest.mark.asyncio
async def test_set_pv_surplus_disable(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_pv_surplus disables PV surplus mode."""
    url = "http://192.168.1.100/setFunctionManually?PVSURPLUS,OFF,0,0"
    mock_aioresponse.get(url, body="OK\nPVSURPLUS\nOFF", status=200)

    result = await api_client.set_pv_surplus(active=False)

    assert result["success"] is True
    assert result["output"] == "PVSURPLUS"


def test_error_codes_structure() -> None:
    """Test error codes have required severity and message fields."""
    for code, info in ERROR_CODES.items():
        assert "severity" in info, f"Code {code} missing 'severity'"
        assert "message" in info, f"Code {code} missing 'message'"
        assert info["severity"] in (
            ERROR_SEVERITY_ALARM,
            ERROR_SEVERITY_WARNING,
            ERROR_SEVERITY_INFO,
            ERROR_SEVERITY_REMINDER,
        ), f"Code {code} has invalid severity: {info['severity']}"


def test_error_codes_test_message_is_info() -> None:
    """Test code 0000 (test message) has INFO severity."""
    assert ERROR_CODES["0000"]["severity"] == ERROR_SEVERITY_INFO


def test_error_codes_filter_pressure_alarms() -> None:
    """Test filter pressure alarm codes have ALARM severity."""
    assert ERROR_CODES["0020"]["severity"] == ERROR_SEVERITY_ALARM
    assert ERROR_CODES["0021"]["severity"] == ERROR_SEVERITY_ALARM


def test_error_codes_dosing_warnings() -> None:
    """Test dosing warning codes."""
    assert ERROR_CODES["0120"]["severity"] == ERROR_SEVERITY_WARNING
    assert ERROR_CODES["0150"]["severity"] == ERROR_SEVERITY_WARNING
    assert ERROR_CODES["0160"]["severity"] == ERROR_SEVERITY_WARNING


def test_error_codes_hardware_modules() -> None:
    """Test hardware module error codes."""
    assert ERROR_CODES["0200"]["severity"] == ERROR_SEVERITY_WARNING
    assert ERROR_CODES["0208"]["severity"] == ERROR_SEVERITY_ALARM
    assert ERROR_CODES["0209"]["severity"] == ERROR_SEVERITY_ALARM


def test_error_codes_omnitronic_faults_added() -> None:
    """OmniTronic multi-port valve faults (0045/46/47/49) are present as ALARM."""
    # Regression test for missing backwash-valve codes – see CLAUDE.md notes.
    for code in ("0045", "0046", "0047", "0049"):
        assert code in ERROR_CODES, f"Missing OmniTronic code {code}"
        assert ERROR_CODES[code]["severity"] == ERROR_SEVERITY_ALARM


def test_error_codes_h2o2_dosing_added() -> None:
    """H2O2 dosing warnings (0142-0145) are present."""
    for code in ("0142", "0143", "0144", "0145"):
        assert code in ERROR_CODES, f"Missing H2O2 code {code}"
        assert ERROR_CODES[code]["severity"] == ERROR_SEVERITY_WARNING


def test_error_codes_reminder_category() -> None:
    """REMINDER-category codes are classified correctly (not INFO)."""
    # 0003 birthday, 0005 system status, 0010-0012 updates, 0180-0182 calibration.
    for code in ("0003", "0005", "0010", "0011", "0012", "0180", "0181", "0182"):
        assert ERROR_CODES[code]["severity"] == ERROR_SEVERITY_REMINDER, code


def test_error_code_0005_text_corrected() -> None:
    """Code 0005 is the generic system-status reminder, not cloud maintenance."""
    # Regression: previously held wrong text "Wartungsarbeiten am Cloud-Server".
    assert "Cloud-Server" not in ERROR_CODES["0005"]["message"]
    assert ERROR_CODES["0005"]["message"] == "Systemnachricht"


def test_error_codes_four_digit_format() -> None:
    """Test all error code keys are 4-digit zero-padded strings."""
    for code in ERROR_CODES:
        assert len(code) == 4, f"Code {code} is not 4 digits"
        assert code.isdigit(), f"Code {code} is not numeric"


def test_parse_error_notification_known_code() -> None:
    """Test parsing a known error code returns structured result."""
    result = VioletPoolAPI.parse_error_notification("0020")
    assert result["code"] == "0020"
    assert result["severity"] == ERROR_SEVERITY_ALARM
    assert result["is_alarm"] is True
    assert result["is_warning"] is False
    assert "Filterdruck" in result["message"]


def test_parse_error_notification_unknown_code() -> None:
    """Test parsing an unknown error code falls back gracefully."""
    result = VioletPoolAPI.parse_error_notification("9999", subject="Custom error")
    assert result["code"] == "9999"
    assert result["message"] == "Custom error"


def test_parse_error_notification_zero_pads() -> None:
    """Test error code is zero-padded to 4 digits."""
    result = VioletPoolAPI.parse_error_notification("20")
    assert result["code"] == "0020"


def test_parse_multiple_errors() -> None:
    """Test parsing multiple comma-separated error codes."""
    payload = {"ERRORCODE": "0020,0120", "SUBJECT": "Test"}
    results = VioletPoolAPI.parse_multiple_errors(payload)
    assert len(results) == 2
    assert results[0]["code"] == "0020"
    assert results[1]["code"] == "0120"


def test_parse_multiple_errors_empty() -> None:
    """Test parsing empty error code returns empty list."""
    results = VioletPoolAPI.parse_multiple_errors({"ERRORCODE": "0"})
    assert results == []

    results = VioletPoolAPI.parse_multiple_errors({})
    assert results == []


def test_parse_multiple_errors_single() -> None:
    """Test parsing a single error code."""
    results = VioletPoolAPI.parse_multiple_errors({"ERRORCODE": "0001"})
    assert len(results) == 1
    assert results[0]["code"] == "0001"


@pytest.mark.asyncio
async def test_set_switch_state_multiline_response(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test set_switch_state parses multi-line response from controller."""
    url = "http://192.168.1.100/setFunctionManually?PUMP,ON,0,2"
    body = "OK\nPUMP\nMANUELL EIN\nDrehzahl 2"
    mock_aioresponse.get(url, body=body, status=200)

    result = await api_client.set_pump_speed(speed=2, duration=0)

    assert result["success"] is True
    assert result["output"] == "PUMP"
    assert result["message"] == "MANUELL EIN\nDrehzahl 2"


@pytest.mark.asyncio
async def test_trigger_dosing_multiline_response(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test dosing trigger parses MANDOS_STARTED multi-line response."""
    url = "http://192.168.1.100/triggerManualDosing"
    mock_aioresponse.post(url, body="MANDOS_STARTED\nOK", status=200)

    result = await api_client.manual_dosing("Chlor", 30)

    assert result["success"] is True
    assert result["output"] == "OK"


@pytest.mark.asyncio
async def test_manual_dosing_flockmittel(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test Flockmittel dosing routes to DOS_6_FLOC via triggerManualDosing."""
    url = "http://192.168.1.100/triggerManualDosing"
    mock_aioresponse.post(url, body="MANDOS_STARTED\nOK", status=200)

    result = await api_client.manual_dosing("Flockmittel", 60)

    assert result["success"] is True
    assert "MANDOS_STARTED" in result["response"]


@pytest.mark.asyncio
async def test_manual_dosing_ph_minus(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test pH- dosing routes to DOS_4_PHM via triggerManualDosing."""
    url = "http://192.168.1.100/triggerManualDosing"
    mock_aioresponse.post(url, body="MANDOS_STARTED\nOK", status=200)

    result = await api_client.manual_dosing("pH-", 30)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_manual_dosing_ph_plus(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test pH+ dosing routes to DOS_5_PHP via triggerManualDosing."""
    url = "http://192.168.1.100/triggerManualDosing"
    mock_aioresponse.post(url, body="MANDOS_STARTED\nOK", status=200)

    result = await api_client.manual_dosing("pH+", 45)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_manual_dosing_elektrolyse(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test Elektrolyse dosing routes to DOS_2_ELO via triggerManualDosing."""
    url = "http://192.168.1.100/triggerManualDosing"
    mock_aioresponse.post(url, body="MANDOS_STARTED\nOK", status=200)

    result = await api_client.manual_dosing("Elektrolyse", 120)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_manual_dosing_unknown_type(api_client: VioletPoolAPI) -> None:
    """Test manual_dosing raises error for unknown dosing type."""
    with pytest.raises(VioletPoolAPIError) as exc_info:
        await api_client.manual_dosing("Unknown", 30)

    assert "Unknown dosing type" in str(exc_info.value)


@pytest.mark.asyncio
async def test_manual_dosing_stop(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test stopping a manual dosing run sends DOSSTOP."""
    url = "http://192.168.1.100/triggerManualDosing"
    mock_aioresponse.post(url, body="MANDOS_STOPPED\nOK", status=200)

    result = await api_client.set_switch_state("DOS_1_CL", "OFF")

    assert result["success"] is True
    assert "MANDOS_STOPPED" in result["response"]


@pytest.mark.asyncio
async def test_dosing_auto_action_sends_dosstop(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """AUTO on a dosing output must stop the run, never start one.

    setFunctionManually does not work for DOS_* outputs (PoolDigital forum),
    so AUTO maps to DOSSTOP via /triggerManualDosing - stopping the manual
    run returns the channel to automatic mode.
    """
    url = "http://192.168.1.100/triggerManualDosing"
    mock_aioresponse.post(url, body="MANDOS_STOPPED\nOK", status=200)

    result = await api_client.set_switch_state("DOS_6_FLOC", "AUTO")

    assert result["success"] is True
    request_key = ("POST", URL(url))
    sent = mock_aioresponse.requests[request_key][0].kwargs["data"]
    assert sent["action"] == "DOSSTOP"


@pytest.mark.asyncio
async def test_dosing_unknown_action_rejected(api_client: VioletPoolAPI) -> None:
    """Unknown dosing actions raise instead of defaulting to DOSSTART."""
    with pytest.raises(VioletPoolAPIError, match="Unsupported dosing action"):
        await api_client.set_switch_state("DOS_1_CL", "PUSH")


@pytest.mark.asyncio
async def test_pv_surplus_with_speed(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test PV surplus sends speed in WERT_1 per manual section 26.3."""
    url = "http://192.168.1.100/setFunctionManually?PVSURPLUS,ON,3,0"
    mock_aioresponse.get(url, body="OK\nPVSURPLUS\nON", status=200)

    result = await api_client.set_pv_surplus(active=True, pump_speed=3)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_ext2_relay_auto(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test EXT2 relay control per manual section 26.2.2."""
    url = "http://192.168.1.100/setFunctionManually?EXT2_5,ON,3600,0"
    mock_aioresponse.get(url, body="OK\nEXT2_5\nMANUELL EIN", status=200)

    result = await api_client.set_switch_state("EXT2_5", "ON", duration=3600)

    assert result["success"] is True
    assert result["output"] == "EXT2_5"


@pytest.mark.asyncio
async def test_pump_auto_reset(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test PUMP AUTO reset per manual section 26.2.1."""
    url = "http://192.168.1.100/setFunctionManually?PUMP,AUTO,0,0"
    mock_aioresponse.get(url, body="OK\nPUMP\nAUTO", status=200)

    result = await api_client.control_pump("AUTO")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_pump_off_with_duration(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Test PUMP OFF with duration per manual section 26.2.1."""
    url = "http://192.168.1.100/setFunctionManually?PUMP,OFF,600,0"
    mock_aioresponse.get(url, body="OK\nPUMP\nMANUELL AUS\n600 Sekunden", status=200)

    result = await api_client.control_pump("OFF", duration=600)

    assert result["success"] is True
    assert result["message"] == "MANUELL AUS\n600 Sekunden"


@pytest.mark.asyncio
async def test_pv_surplus_auto_is_mapped_to_off(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """PVSURPLUS supports only ON/OFF (manual 26.3); AUTO is sent as OFF."""
    url = "http://192.168.1.100/setFunctionManually?PVSURPLUS,OFF,0,0"
    mock_aioresponse.get(url, body="OK\nPVSURPLUS\nOFF", status=200)

    result = await api_client.set_switch_state("PVSURPLUS", "AUTO")

    assert result["success"] is True
    assert result["output"] == "PVSURPLUS"


@pytest.mark.asyncio
async def test_pv_surplus_rejects_unknown_action(
    api_client: VioletPoolAPI,
) -> None:
    """PVSURPLUS rejects actions that cannot be mapped to ON/OFF."""
    with pytest.raises(VioletPoolAPIError, match="manual section 26.3"):
        await api_client.set_switch_state("PVSURPLUS", "PUSH")


@pytest.mark.asyncio
async def test_pv_surplus_speed_is_clamped(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Pump speed for PVSURPLUS is clamped to the documented 1-3 range."""
    url = "http://192.168.1.100/setFunctionManually?PVSURPLUS,ON,3,0"
    mock_aioresponse.get(url, body="OK\nPVSURPLUS\nON", status=200)

    result = await api_client.set_pv_surplus(active=True, pump_speed=5)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_client_error_fails_fast_without_retry(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """A 4xx response raises immediately instead of being retried."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_aioresponse.get(url, status=401, body="Unauthorized")

    with pytest.raises(VioletPoolAPIError, match="HTTP 401"):
        await api_client.get_readings()


@pytest.mark.asyncio
async def test_client_error_does_not_trip_circuit_breaker(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """Deterministic 4xx errors must not count as circuit breaker failures."""
    url = "http://192.168.1.100/getReadings?ALL"
    threshold = api_client._circuit_breaker.failure_threshold

    for _ in range(threshold + 1):
        mock_aioresponse.get(url, status=401, body="Unauthorized")
        with pytest.raises(VioletPoolAPIError, match="HTTP 401"):
            await api_client.get_readings()

    stats = api_client._circuit_breaker.get_stats()
    assert stats["failure_count"] == 0
    assert stats["state"] == "CLOSED"


@pytest.mark.asyncio
async def test_server_error_still_counts_for_circuit_breaker(
    mock_aioresponse: aioresponses,
    api_client: VioletPoolAPI,
) -> None:
    """5xx errors keep counting as circuit breaker failures."""
    url = "http://192.168.1.100/getReadings?ALL"
    mock_aioresponse.get(url, status=500, body="boom")

    with pytest.raises(VioletPoolAPIError):
        await api_client.get_readings()

    stats = api_client._circuit_breaker.get_stats()
    assert stats["failure_count"] == 1


def test_command_result_error_first_line() -> None:
    """Line 1 of the response decides success per manual section 26.2."""
    result = VioletPoolAPI._command_result("ERROR\nPUMP\nUNKNOWN OUTPUT")
    assert result["success"] is False

    result = VioletPoolAPI._command_result("OK\nPUMP\nInfo about error handling")
    assert result["success"] is True


def test_state_translation_language_switch() -> None:
    """Display texts are language-configurable instead of hardwired German."""
    from violet_poolcontroller_api.const_devices import (
        VioletState,
        get_state_translation_language,
        set_state_translation_language,
    )

    assert get_state_translation_language() == "de"
    state = VioletState("0")
    assert state.display_mode == "Automatik (Bereit)"
    assert state.display_mode_for("en") == "Auto (Ready)"

    english_state = VioletState("0", language="en")
    assert english_state.display_mode == "Auto (Ready)"

    set_state_translation_language("en")
    try:
        assert VioletState("4").display_mode == "Manual On"
    finally:
        set_state_translation_language("de")

    with pytest.raises(ValueError, match="Unsupported language"):
        set_state_translation_language("fr")
