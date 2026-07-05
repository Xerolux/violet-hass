"""Integration test: API client against mock server with Basic Auth.

Starts the mock server, runs the API client with correct and wrong
credentials, and verifies that authentication is enforced properly.
"""

from __future__ import annotations

import asyncio
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import aiohttp
import pytest

from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError

HOST = "127.0.0.1"
PORT = 8499
USER = "admin"
PASS = "secret"

_MOCK_SERVER_PATH = Path(__file__).parent / "mock_server.py"


def _start_mock_server() -> subprocess.Popen[bytes]:
    """Start the mock server subprocess and wait until it accepts connections."""
    proc = subprocess.Popen(
        [
            sys.executable,
            str(_MOCK_SERVER_PATH),
            "--port",
            str(PORT),
            "--user",
            USER,
            "--password",
            PASS,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            msg = f"Mock server exited early with code {proc.returncode}"
            raise RuntimeError(msg)
        try:
            with socket.create_connection((HOST, PORT), timeout=0.5):
                return proc
        except OSError:
            time.sleep(0.1)
    proc.terminate()
    msg = f"Mock server did not start listening on port {PORT} within 10s"
    raise RuntimeError(msg)


@pytest.fixture(scope="module", autouse=True)
def mock_server() -> Iterator[subprocess.Popen[bytes]]:
    """Run the mock server for all tests in this module."""
    proc = _start_mock_server()
    try:
        yield proc
    finally:
        proc.terminate()
        proc.wait(timeout=5)


async def _request(url: str, auth: aiohttp.BasicAuth | None = None) -> tuple[int, str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=auth) as r:
            return r.status, await r.text()


async def test_raw_auth() -> None:
    print("=" * 60)
    print("TEST 1: Raw HTTP - /getReadings without credentials -> 200")
    print("=" * 60)
    status, body = await _request(f"http://{HOST}:{PORT}/getReadings?ALL")
    assert status == 200, f"Expected 200, got {status}"
    print(f"  OK: status={status} body_len={len(body)}")

    print()
    print("=" * 60)
    print("TEST 2: Raw HTTP - /getConfig without credentials -> 401")
    print("=" * 60)
    status, body = await _request(f"http://{HOST}:{PORT}/getConfig")
    assert status == 401, f"Expected 401, got {status}"
    print(f"  OK: status={status} body={body!r}")

    print()
    print("=" * 60)
    print("TEST 3: Raw HTTP - /getConfig with wrong password -> 401")
    print("=" * 60)
    status, body = await _request(
        f"http://{HOST}:{PORT}/getConfig",
        auth=aiohttp.BasicAuth("admin", "wrongpassword"),
    )
    assert status == 401, f"Expected 401, got {status}"
    print(f"  OK: status={status} body={body!r}")

    print()
    print("=" * 60)
    print("TEST 4: Raw HTTP - /getConfig with correct credentials -> 200")
    print("=" * 60)
    status, body = await _request(
        f"http://{HOST}:{PORT}/getConfig",
        auth=aiohttp.BasicAuth(USER, PASS),
    )
    assert status == 200, f"Expected 200, got {status}"
    print(f"  OK: status={status} body_len={len(body)}")

    print()
    print("=" * 60)
    print("TEST 5: /mock/* endpoints bypass auth")
    print("=" * 60)
    status, body = await _request(f"http://{HOST}:{PORT}/mock/state")
    assert status == 200, f"Expected 200, got {status}"
    print(f"  OK: /mock/state status={status} (no auth required)")


async def test_api_client() -> None:
    print()
    print("=" * 60)
    print("TEST 6: VioletPoolAPI - wrong credentials -> error on /getConfig")
    print("=" * 60)
    async with aiohttp.ClientSession() as session:
        api_bad = VioletPoolAPI(
            host=f"{HOST}:{PORT}",
            session=session,
            username="admin",
            password="wrongpassword",
            max_retries=1,
        )
        try:
            await api_bad.get_config(["DOSAGE_phminus_setpoint"])
            assert False, "Should have raised VioletPoolAPIError"
        except VioletPoolAPIError as exc:
            print(f"  OK: VioletPoolAPIError raised: {exc}")

    print()
    print("=" * 60)
    print("TEST 7: VioletPoolAPI - correct credentials -> full workflow")
    print("=" * 60)
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host=f"{HOST}:{PORT}",
            session=session,
            username=USER,
            password=PASS,
            max_retries=1,
        )

        readings = await api.get_readings()
        print(f"  get_readings: {len(readings)} keys, pH={readings.get('pH_value')}, PUMP={readings.get('PUMP')}")
        assert "PUMP" in readings
        assert "pH_value" in readings

        result = await api.set_pump_speed(speed=2, duration=0)
        print(f"  set_pump_speed: {result}")
        assert result["success"] is True

        readings2 = await api.get_readings()
        print(f"  get_readings after PUMP ON: PUMP={readings2.get('PUMP')} (expect 4)")
        assert readings2["PUMP"] == 4

        result = await api.manual_dosing("Chlor", 45)
        print(f"  manual_dosing(Chlor): {result}")
        assert result["success"] is True

        result = await api.set_ph_target(7.4)
        print(f"  set_ph_target(7.4): {result}")
        assert result["success"] is True

        config = await api.get_config(["DOSAGE_phminus_setpoint"])
        print(f"  get_config: {config}")
        assert "DOSAGE_phminus_setpoint" in config

        weather = await api.get_weather_data()
        print(f"  get_weather_data: temp={weather.get('temp')}")
        assert "temp" in weather

        states = await api.get_output_states()
        print(f"  get_output_states: {list(states.keys())}")
        assert "PUMP" in states

        profile = await api.get_hardware_profile()
        print(f"  get_hardware_profile: {profile}")
        assert profile["base_module"] is True
        assert profile["dosing_module"] is True

        result = await api.control_pump("AUTO")
        print(f"  control_pump(AUTO): {result}")
        assert result["success"] is True

        readings3 = await api.get_readings()
        print(f"  get_readings after PUMP AUTO: PUMP={readings3.get('PUMP')} (expect 0)")

        result = await api.set_switch_state("DOS_1_CL", "OFF")
        print(f"  stop dosing: {result}")
        assert result["success"] is True

        result = await api.set_pv_surplus(active=True, pump_speed=3)
        print(f"  set_pv_surplus: {result}")
        assert result["success"] is True

        result = await api.set_light_color_pulse()
        print(f"  set_light_color_pulse: {result}")
        assert result["success"] is True

        result = await api.set_all_dmx_scenes("ALLOFF")
        print(f"  set_all_dmx_scenes(ALLOFF): {result}")
        assert result["success"] is True

        result = await api.trigger_digital_input_rule("DIRULE_1")
        print(f"  trigger_digital_input_rule: {result}")
        assert result["success"] is True

        calib = await api.get_calibration_raw_values()
        print(f"  get_calibration_raw_values: {list(calib.keys())}")

        calib_hist = await api.get_calibration_history("pH")
        print(f"  get_calibration_history: {len(calib_hist)} entries")

        calib_hist = await api.get_calibration_history("pH")
        print(f"  get_calibration_history: {len(calib_hist)} entries")

        result = await api.set_dosing_parameters({"DOSAGE_chlorine_use": 0})
        print(f"  set_dosing_parameters: {result}")
        assert result["success"] is True

        result = await api.set_device_temperature("HEATER", 30.0)
        print(f"  set_device_temperature(HEATER, 30): {result}")

    print()
    print("=" * 60)
    print("TEST 8: Error simulation with auth")
    print("=" * 60)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{HOST}:{PORT}/mock/error?code=500&count=1") as r:
            print(f"  activate error mode: {await r.json()}")

        api = VioletPoolAPI(
            host=f"{HOST}:{PORT}",
            session=session,
            username=USER,
            password=PASS,
            max_retries=1,
        )
        try:
            await api.get_readings()
            assert False, "Should have raised"
        except VioletPoolAPIError:
            print("  OK: got VioletPoolAPIError on 500")

        readings = await api.get_readings()
        print(f"  recovered: {len(readings)} keys")

    print()
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


def main() -> None:
    print(f"Starting mock server on port {PORT} with auth ({USER}:{PASS})...")
    proc = _start_mock_server()

    try:
        asyncio.run(test_raw_auth())
        asyncio.run(test_api_client())
    finally:
        proc.terminate()
        proc.wait(timeout=5)
        print(f"\nMock server stopped (pid={proc.pid})")


if __name__ == "__main__":
    main()
