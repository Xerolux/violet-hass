#!/usr/bin/env python3
"""Full API smoke test against the Violet Pool Controller mock server.

Starts the mock server automatically, runs every public API method,
and prints a summary with pass/fail/skip counts and detailed error info.

Usage:
    python tests/test_api_smoke.py
    python tests/test_api_smoke.py --host localhost --port 8480
    python tests/test_api_smoke.py --user admin --password secret
"""

from __future__ import annotations

import asyncio
import dataclasses
import subprocess
import sys
import time
import traceback
from collections.abc import Callable, Coroutine
from typing import Any

import aiohttp

from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError


@dataclasses.dataclass
class SmokeResult:
    name: str
    status: str  # "PASS" | "FAIL" | "SKIP"
    detail: str = ""
    duration_ms: float = 0.0


_results: list[SmokeResult] = []


async def _run(
    name: str,
    coro: Coroutine[Any, Any, Any],
    *,
    check: Callable[[Any], str | None] | None = None,
) -> Any:
    start = time.monotonic()
    try:
        result = await coro
        elapsed = (time.monotonic() - start) * 1000

        error_msg: str | None = None
        if check is not None:
            error_msg = check(result)

        if error_msg:
            _results.append(SmokeResult(name, "FAIL", error_msg, elapsed))
        else:
            detail = ""
            if isinstance(result, dict):
                if "success" in result:
                    detail = f"success={result['success']}"
                elif len(result) <= 8:
                    detail = ", ".join(f"{k}={v}" for k, v in result.items())
                else:
                    detail = f"{len(result)} keys"
            elif isinstance(result, list):
                detail = f"{len(result)} entries"
            elif isinstance(result, bool):
                detail = str(result)
            _results.append(SmokeResult(name, "PASS", detail, elapsed))
        return result
    except VioletPoolAPIError as exc:
        elapsed = (time.monotonic() - start) * 1000
        _results.append(SmokeResult(name, "FAIL", f"VioletPoolAPIError: {exc}", elapsed))
        return None
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        tb = traceback.format_exc()
        _results.append(SmokeResult(name, "FAIL", f"{type(exc).__name__}: {exc}\n{tb}", elapsed))
        return None


async def _expect_error(
    name: str,
    coro: Coroutine[Any, Any, Any],
    *,
    error_contains: str | None = None,
) -> None:
    start = time.monotonic()
    try:
        result = await coro
        elapsed = (time.monotonic() - start) * 1000
        _results.append(SmokeResult(name, "FAIL", f"Expected error but got success: {result}", elapsed))
    except VioletPoolAPIError as exc:
        elapsed = (time.monotonic() - start) * 1000
        msg = str(exc)
        if error_contains and error_contains not in msg:
            _results.append(SmokeResult(name, "FAIL", f"Error message mismatch: '{msg}' does not contain '{error_contains}'", elapsed))
        else:
            _results.append(SmokeResult(name, "PASS", f"Correctly raised: {msg}", elapsed))
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        _results.append(SmokeResult(name, "FAIL", f"Unexpected {type(exc).__name__}: {exc}", elapsed))


def _skip(name: str, reason: str) -> None:
    _results.append(SmokeResult(name, "SKIP", reason))


async def run_all_tests(api: VioletPoolAPI) -> None:
    print()
    print("=" * 70)
    print("  VIOLET POOL API - FULL SMOKE TEST")
    print("=" * 70)
    print()

    # ── Properties ──────────────────────────────────────────────────────
    print("[Properties]")

    await _run("timeout", _run_prop(api, "timeout"), check=lambda v: None if v > 0 else f"timeout={v}")
    await _run("max_retries", _run_prop(api, "max_retries"), check=lambda v: None if v >= 1 else f"max_retries={v}")
    await _run("dosing_standalone", _run_prop(api, "dosing_standalone"), check=lambda v: None if isinstance(v, bool) else f"type={type(v)}")

    # ── GET endpoints ───────────────────────────────────────────────────
    print("[GET Data]")

    await _run(
        "get_readings",
        api.get_readings(),
        check=lambda r: "PUMP missing" if "PUMP" not in r else ("pH_value missing" if "pH_value" not in r else None),
    )

    await _run(
        "get_hardware_profile",
        api.get_hardware_profile(),
        check=lambda r: "missing base_module" if "base_module" not in r else None,
    )

    await _run(
        "get_specific_readings(DOSAGE)",
        api.get_specific_readings(["DOSAGE"]),
        check=lambda r: "empty" if not r else None,
    )

    await _run(
        "get_history",
        api.get_history(hours=1, sensor="ALL"),
        check=lambda r: "no data" if not r else None,
    )

    await _run(
        "get_weather_data",
        api.get_weather_data(),
        check=lambda r: "missing temp" if "temp" not in r else None,
    )

    await _run(
        "get_overall_dosing",
        api.get_overall_dosing(),
        check=lambda r: "empty" if not r else None,
    )

    await _run(
        "get_output_states",
        api.get_output_states(),
        check=lambda r: "PUMP missing" if "PUMP" not in r else None,
    )

    await _run(
        "get_config",
        api.get_config(["DOSAGE_phminus_setpoint", "DOSAGE_chlorine_setpoint_orp"]),
        check=lambda r: "missing keys" if len(r) < 2 else None,
    )

    await _run(
        "get_calibration_raw_values",
        api.get_calibration_raw_values(),
        check=lambda r: "missing pH_raw" if "pH_raw" not in r else None,
    )

    await _run(
        "get_calibration_history(pH)",
        api.get_calibration_history("pH"),
        check=lambda r: "empty" if not r else None,
    )

    # ── POST endpoints (config / commands) ──────────────────────────────
    print("[Config & Commands]")

    await _run(
        "set_config(DOSAGE_phminus_setpoint=7.4)",
        api.set_config({"DOSAGE_phminus_setpoint": 7.4}),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_ph_target(7.2)",
        api.set_ph_target(7.2),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_orp_target(700)",
        api.set_orp_target(700),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_min_chlorine_level(0.5)",
        api.set_min_chlorine_level(0.5),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_target_value(CUSTOM, 42.0)",
        api.set_target_value("CUSTOM", 42.0),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_dosing_parameters",
        api.set_dosing_parameters({"DOSAGE_chlorine_use": 1}),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_dosage_enabled(pH-, True)",
        api.set_dosage_enabled("pH-", True),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_device_temperature(HEATER, 28.0)",
        api.set_device_temperature("HEATER", 28.0),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_device_temperature(SOLAR, 30.0)",
        api.set_device_temperature("SOLAR", 30.0),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "restore_calibration(pH, 2024-01-01)",
        api.restore_calibration("pH", "2024-01-01"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    # ── Switch controls ─────────────────────────────────────────────────
    print("[Switch Controls]")

    await _run(
        "set_pump_speed(2)",
        api.set_pump_speed(speed=2),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "get_readings (verify PUMP=4 after ON)",
        api.get_readings(),
        check=lambda r: f"PUMP={r.get('PUMP')}, expected 4" if r.get("PUMP") != 4 else None,
    )

    await _run(
        "control_pump(OFF)",
        api.control_pump("OFF"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "get_readings (verify PUMP=6 after OFF)",
        api.get_readings(),
        check=lambda r: f"PUMP={r.get('PUMP')}, expected 6" if r.get("PUMP") != 6 else None,
    )

    await _run(
        "control_pump(AUTO)",
        api.control_pump("AUTO"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "control_pump(ON, speed=3, duration=600)",
        api.control_pump("ON", speed=3, duration=600),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    # ── Dosing ──────────────────────────────────────────────────────────
    print("[Dosing]")

    for dosing_type in ["Chlor", "pH-", "pH+", "Elektrolyse", "Flockmittel"]:
        await _run(
            f"manual_dosing({dosing_type}, 30)",
            api.manual_dosing(dosing_type, 30),
            check=lambda r: "not success" if not r.get("success") else None,
        )

    await _run(
        "set_switch_state(DOS_1_CL, OFF) - stop dosing",
        api.set_switch_state("DOS_1_CL", "OFF"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    # ── Extension relays ────────────────────────────────────────────────
    print("[Extension Relays]")

    await _run(
        "set_switch_state(EXT1_2, ON)",
        api.set_switch_state("EXT1_2", "ON"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_switch_state(EXT2_5, ON, duration=3600)",
        api.set_switch_state("EXT2_5", "ON", duration=3600),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    # ── DMX / Light ────────────────────────────────────────────────────
    print("[DMX & Light]")

    await _run(
        "set_all_dmx_scenes(ALLOFF)",
        api.set_all_dmx_scenes("ALLOFF"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_all_dmx_scenes(ALLON)",
        api.set_all_dmx_scenes("ALLON"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_all_dmx_scenes(ALLAUTO)",
        api.set_all_dmx_scenes("ALLAUTO"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_light_color_pulse",
        api.set_light_color_pulse(),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    # ── Digital input rules ─────────────────────────────────────────────
    print("[Digital Input Rules]")

    await _run(
        "trigger_digital_input_rule(DIRULE_1)",
        api.trigger_digital_input_rule("DIRULE_1"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_digital_input_rule_lock(DIRULE_1, locked=True)",
        api.set_digital_input_rule_lock("DIRULE_1", locked=True),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_digital_input_rule_lock(DIRULE_1, locked=False)",
        api.set_digital_input_rule_lock("DIRULE_1", locked=False),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    # ── PV Surplus ──────────────────────────────────────────────────────
    print("[PV Surplus]")

    await _run(
        "set_pv_surplus(active=True, pump_speed=3)",
        api.set_pv_surplus(active=True, pump_speed=3),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_pv_surplus(active=False)",
        api.set_pv_surplus(active=False),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    # ── Output test mode ────────────────────────────────────────────────
    print("[Output Test Mode]")

    await _run(
        "set_output_test_mode(EXT1_1)",
        api.set_output_test_mode(output="EXT1_1"),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    await _run(
        "set_output_test_mode(LIGHT, PULSE, 60)",
        api.set_output_test_mode(output="LIGHT", mode="PULSE", duration=60),
        check=lambda r: "not success" if not r.get("success") else None,
    )

    # ── Error parsing (static, no server needed) ────────────────────────
    print("[Error Parsing]")

    await _run(
        "parse_error_notification(0020)",
        _async_static(VioletPoolAPI.parse_error_notification, "0020"),
        check=lambda r: "missing is_alarm" if not r.get("is_alarm") else None,
    )

    await _run(
        "parse_error_notification(9999, subject=Custom)",
        _async_static(VioletPoolAPI.parse_error_notification, "9999", subject="Custom"),
        check=lambda r: "wrong message" if r.get("message") != "Custom" else None,
    )

    await _run(
        "parse_error_notification(20) - zero pad",
        _async_static(VioletPoolAPI.parse_error_notification, "20"),
        check=lambda r: f"code={r.get('code')}, expected 0020" if r.get("code") != "0020" else None,
    )

    await _run(
        "parse_multiple_errors(0020,0120)",
        _async_static(VioletPoolAPI.parse_multiple_errors, {"ERRORCODE": "0020,0120", "SUBJECT": "Test"}),
        check=lambda r: f"expected 2, got {len(r)}" if len(r) != 2 else None,
    )

    await _run(
        "parse_multiple_errors(empty)",
        _async_static(VioletPoolAPI.parse_multiple_errors, {"ERRORCODE": "0"}),
        check=lambda r: f"expected 0, got {len(r)}" if len(r) != 0 else None,
    )

    # ── Validation errors (expect VioletPoolAPIError) ───────────────────
    print("[Validation (expected errors)]")

    await _expect_error(
        "manual_dosing(Unknown) - should fail",
        api.manual_dosing("Unknown", 30),
        error_contains="Unknown dosing type",
    )

    await _expect_error(
        "set_all_dmx_scenes(INVALID) - should fail",
        api.set_all_dmx_scenes("INVALID"),
        error_contains="Unsupported DMX action",
    )

    await _expect_error(
        "get_specific_readings([]) - should fail",
        api.get_specific_readings(["", "   "]),
        error_contains="No valid categories provided",
    )

    await _expect_error(
        "get_config([]) - should fail",
        api.get_config(["  ", ""]),
        error_contains="No valid configuration keys provided",
    )

    await _expect_error(
        "set_config({}) - should fail",
        api.set_config({}),
        error_contains="must not be empty",
    )

    await _expect_error(
        "restore_calibration(empty) - should fail",
        api.restore_calibration("", ""),
        error_contains="Sensor and timestamp are required",
    )

    await _expect_error(
        "set_output_test_mode(empty) - should fail",
        api.set_output_test_mode(output=""),
        error_contains="Output identifier is required",
    )

    await _expect_error(
        "get_calibration_history(empty) - should fail",
        api.get_calibration_history(""),
        error_contains="Sensor name required",
    )

    await _expect_error(
        "set_switch_state(DOS_UNKNOWN, ON) - should fail",
        api.set_switch_state("DOS_UNKNOWN", "ON"),
        error_contains="Unknown dosing output key",
    )

    await _expect_error(
        "set_dosage_enabled(Unknown) - should fail",
        api.set_dosage_enabled("Unknown", True),
        error_contains="Unknown dosing type",
    )

    # ── Skipped methods (use _api_request, not available in source) ─────
    print("[Skipped - requires _api_request]")

    _skip("get_log(actions)", "uses _api_request (not in source, only in installed package)")
    _skip("get_notifications", "uses _api_request (not in source, only in installed package)")
    _skip("is_dosage_enabled(pH-)", "uses _request_json_dict without payload_name param mismatch")


async def _run_prop(api: VioletPoolAPI, prop: str) -> Any:
    return getattr(api, prop)


async def _async_static(func: Any, *args: Any, **kwargs: Any) -> Any:
    return func(*args, **kwargs)


def print_report() -> None:
    print()
    print("=" * 70)
    print("  TEST REPORT")
    print("=" * 70)

    passed = [r for r in _results if r.status == "PASS"]
    failed = [r for r in _results if r.status == "FAIL"]
    skipped = [r for r in _results if r.status == "SKIP"]

    total_time = sum(r.duration_ms for r in _results)

    print()
    print(f"  TOTAL: {len(_results)}  |  PASS: {len(passed)}  |  FAIL: {len(failed)}  |  SKIP: {len(skipped)}  |  Time: {total_time:.0f}ms")
    print()

    if passed:
        print("-" * 70)
        print(f"  PASSED ({len(passed)})")
        print("-" * 70)
        for r in passed:
            detail = f"  {r.detail}" if r.detail else ""
            print(f"  [PASS] {r.name} ({r.duration_ms:.0f}ms){detail}")

    if skipped:
        print()
        print("-" * 70)
        print(f"  SKIPPED ({len(skipped)})")
        print("-" * 70)
        for r in skipped:
            print(f"  [SKIP] {r.name}")
            print(f"         Reason: {r.detail}")

    if failed:
        print()
        print("-" * 70)
        print(f"  FAILED ({len(failed)})")
        print("-" * 70)
        for r in failed:
            print(f"  [FAIL] {r.name} ({r.duration_ms:.0f}ms)")
            for line in r.detail.splitlines():
                print(f"         {line}")
            print()

    print("=" * 70)
    if not failed:
        print("  ALL TESTS PASSED!")
    else:
        print(f"  {len(failed)} TEST(S) FAILED!")
    print("=" * 70)
    print()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Violet Pool API Smoke Test")
    parser.add_argument("--host", default="localhost", help="Mock server host")
    parser.add_argument("--port", type=int, default=8480, help="Mock server port")
    parser.add_argument("--user", default=None, help="Username for Basic Auth")
    parser.add_argument("--password", default=None, help="Password for Basic Auth")
    parser.add_argument("--no-start", action="store_true", help="Don't auto-start mock server (use running one)")
    args = parser.parse_args()

    proc = None

    if not args.no_start:
        cmd = [sys.executable, "tests/mock_server.py", "--port", str(args.port)]
        if args.user:
            cmd += ["--user", args.user, "--password", args.password or ""]
        print(f"Starting mock server on port {args.port}...")
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

    try:
        asyncio.run(_run_tests(args))
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
            print(f"Mock server stopped (pid={proc.pid})")


async def _run_tests(args: Any) -> None:
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host=f"{args.host}:{args.port}",
            session=session,
            username=args.user,
            password=args.password,
            max_retries=1,
        )
        await run_all_tests(api)
    print_report()


if __name__ == "__main__":
    main()
