# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024-2026  Xerolux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Mock server simulating the Violet Pool Controller HTTP API.

Usage:
    python tests/mock_server.py                                    # no auth
    python tests/mock_server.py --user admin --password secret     # Basic Auth
    python tests/mock_server.py --port 9000                        # custom port
    python tests/mock_server.py --standalone                       # dosing-standalone mode
    python tests/mock_server.py --delay 0.3                        # simulate 300ms latency

Auth model (matches real controller):
    /getReadings         → no auth required
    all other endpoints  → Basic Auth (when --user is set)

Control endpoints (not on real controller):
    GET /mock/state                                  → current internal state as JSON
    GET /mock/error?code=500                         → force next N requests to return this error
    GET /mock/reset                                  → reset all state to defaults
    GET /mock/firmware?available=1.2.0               → simulate a firmware update being available
    GET /mock/firmware?available=                    → clear firmware update (up to date)
    GET /mock/firmware?installed=1.2.0               → change installed firmware version

The server prints all incoming requests so you can verify what the client sends.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import logging
import random
import time
from datetime import UTC, datetime
from typing import Any

from aiohttp import web

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
_LOGGER = logging.getLogger("mock_server")

_SIMULATED_DELAY: float = 0.0
_STANDALONE_MODE = False
_AUTH_CREDENTIALS: tuple[str, str] | None = None

_STATE_NUMERIC_MAP: dict[str, int] = {
    "ON": 4,
    "OFF": 6,
    "AUTO": 0,
    "MAN": 4,
    "COLOR": 4,
    "PUSH": 4,
    "LOCK": 4,
    "UNLOCK": 6,
    "ALLON": 4,
    "ALLOFF": 6,
    "ALLAUTO": 0,
}

_SWITCH_KEYS: set[str] = {
    "PUMP", "SOLAR", "HEATER", "LIGHT", "ECO",
    "BACKWASH", "BACKWASHRINSE", "REFILL", "PVSURPLUS",
}
for _eb in [1, 2]:
    for _rn in range(1, 9):
        _SWITCH_KEYS.add(f"EXT{_eb}_{_rn}")
for _sn in range(1, 13):
    _SWITCH_KEYS.add(f"DMX_SCENE{_sn}")
for _dn in range(1, 9):
    _SWITCH_KEYS.add(f"DIRULE_{_dn}")
for _on in range(6):
    _SWITCH_KEYS.add(f"OMNI_DC{_on}")


class MockController:
    """Mutable state for the mock controller."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        now = int(time.time())
        self.outputs: dict[str, int] = {
            "PUMP": 1, "SOLAR": 0, "HEATER": 0, "LIGHT": 0,
            "ECO": 0, "BACKWASH": 0, "BACKWASHRINSE": 0,
            "REFILL": 0, "PVSURPLUS": 0,
        }
        for eb in [1, 2]:
            for rn in range(1, 9):
                self.outputs[f"EXT{eb}_{rn}"] = 0
        for sn in range(1, 13):
            self.outputs[f"DMX_SCENE{sn}"] = 0

        self.dosing_state: dict[str, str] = {
            "DOS_1_CL": "stopped", "DOS_2_ELO": "stopped",
            "DOS_4_PHM": "stopped", "DOS_5_PHP": "stopped",
            "DOS_6_FLOC": "stopped",
        }

        self.config: dict[str, Any] = {
            "DOSAGE_phminus_setpoint": 7.2,
            "DOSAGE_chlorine_setpoint_orp": 700,
            "DOSAGE_chlorine_lowerval_cl": 0.3,
            "DOSAGE_phminus_use": 1,
            "DOSAGE_phplus_use": 0,
            "DOSAGE_chlorine_use": 1,
            "DOSAGE_electrolysis_use": 0,
            "DOSAGE_floc_use": 1,
            "SOLAR_maxtemp": 28.0,
            "HEATER_set_temp": 28.0,
        }

        self.sensor_drift: dict[str, float] = {
            "pH_value": 7.18, "orp_value": 725.3, "pot_value": 0.62,
            "CPU_TEMP": 45.2,
        }
        self.last_drift_update: float = time.monotonic()

        self.error_mode: int | None = None
        self.error_count: int = 0
        self.request_count: int = 0
        self.start_time: float = time.monotonic()

        # Firmware versions — keys match the real controller's getReadings output.
        # The real controller sends ``SW_VERSION`` and lowercase ``fw``; carrier
        # board info arrives as ``SW_VERSION_CARRIER`` / ``HW_VERSION_CARRIER``.
        # The available-version key only appears when an update exists.
        self.fw_installed = "1.2.4"
        self.fw_carrier = "2.0.3"
        self.fw_available: str | None = None  # None = up to date

        self.last_on_off: dict[str, int] = {
            "PUMP_LAST_ON": now - 600, "PUMP_LAST_OFF": now - 7200,
        }

        self.log_entries: list[str] = []
        self.notifications: dict[str, dict[str, str]] = {}
        # Canister fill levels tracked for /setCanAmount (ml).  Mirrors
        # OVERALL_DOSING.<key>.TOTAL_CAN_AMOUNT_ML on the real controller.
        self.can_amounts: dict[str, int] = {
            "DOS_1_CL": 20000,
            "DOS_2_ELO": 3000,
            "DOS_4_PHM": 20000,
            "DOS_5_PHP": 20000,
            "DOS_6_FLOC": 20000,
        }
        # Records each /resetBlocking call (for test assertions).
        self.reset_blocking_calls: int = 0
        # Live state of /getServiceStates responses.  Keys mirror the real
        # controller: proftpd/shairport/samba/sshd/homekit/tunnel_state/
        # support_tunnel_state.  Alexa state is not exposed by the controller.
        self.services: dict[str, int] = {
            "proftpd": 0,
            "shairport": 0,
            "samba": 0,
            "sshd": 1,
            "homekit": 0,
            "tunnel_state": 0,
            "support_tunnel_state": 0,
        }
        # OmniTronic multi-port valve position (0-5, default 0=Filtration).
        self.omni_position: int = 0
        # RS485 live-control session state.
        self.rs485_live_active: bool = False
        self.rs485_live_mode: str = ""
        self.rs485_live_level: str = ""
        self._init_defaults()

    def _init_defaults(self) -> None:
        now_str = datetime.now(tz=UTC).strftime("%d.%m.%Y %H:%M")
        self.log_entries = [
            f"{now_str} | PUMP | ON | Auto",
            f"{now_str} | DOS_1_CL | START | Auto dosing",
            f"{now_str} | HEATER | OFF | Temperature reached",
        ]
        now = datetime.now(tz=UTC)
        self.notifications = {
            "1": {
                "DATE": now.strftime("%d.%m.%Y"),
                "TIME": now.strftime("%H:%M:%S"),
                "SENSOR_ID": "pH",
                "TYPE": "WARNING",
                "TEXT": "pH Wert außerhalb des Zielbereichs",
                "MAIL_STATE": "0",
            },
            "2": {
                "DATE": now.strftime("%d.%m.%Y"),
                "TIME": now.strftime("%H:%M:%S"),
                "SENSOR_ID": "CL",
                "TYPE": "INFO",
                "TEXT": "Chlor-Dosierung: Redox Grenzwert erreicht",
                "MAIL_STATE": "1",
            },
        }

    def update_sensor_drift(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_drift_update
        if elapsed < 2.0:
            return
        self.last_drift_update = now
        self.sensor_drift["pH_value"] = round(
            max(6.5, min(8.5, self.sensor_drift["pH_value"] + random.uniform(-0.02, 0.02))), 2,
        )
        self.sensor_drift["orp_value"] = round(
            max(400, min(900, self.sensor_drift["orp_value"] + random.uniform(-3.0, 3.0))), 1,
        )
        self.sensor_drift["pot_value"] = round(
            max(0.0, min(5.0, self.sensor_drift["pot_value"] + random.uniform(-0.03, 0.03))), 2,
        )
        self.sensor_drift["CPU_TEMP"] = round(
            max(30, min(80, self.sensor_drift["CPU_TEMP"] + random.uniform(-0.3, 0.3))), 1,
        )

    def set_switch(self, key: str, action: str) -> None:
        numeric = _STATE_NUMERIC_MAP.get(action.upper())
        if numeric is not None and key in self.outputs:
            self.outputs[key] = numeric
            now = int(time.time())
            self.last_on_off[f"{key}_LAST_ON"] = now
            self.last_on_off[f"{key}_LAST_OFF"] = now - 1

    def build_readings(self) -> dict[str, Any]:
        self.update_sensor_drift()
        now = int(time.time())
        uptime_start = time.monotonic() - self.start_time
        days = int(uptime_start // 86400)
        hours = int((uptime_start % 86400) // 3600)
        minutes = int((uptime_start % 3600) // 60)

        readings: dict[str, Any] = {
            "date": datetime.now(tz=UTC).strftime("%d.%m.%Y"),
            "time": datetime.now(tz=UTC).strftime("%H:%M:%S"),
            "CURRENT_TIME_UNIX": now,
            "CONFIGCHANGEMARKER": 0,
            # Firmware — the real controller sends BOTH ``fw`` and ``SW_VERSION``
            "fw": self.fw_installed,
            "SW_VERSION": self.fw_installed,
            "SW_VERSION_CARRIER": self.fw_carrier,
            "HW_VERSION_CARRIER": "2.1.0",
            "HW_SERIAL_CARRIER": "7",
            # Available update — only included when self.fw_available is set
            **({"SW_UPDATE_AVAILABLE": self.fw_available} if self.fw_available else {}),
            "CPU_TEMP": self.sensor_drift["CPU_TEMP"],
            "CPU_TEMP_CARRIER": round(self.sensor_drift["CPU_TEMP"] - 10.0, 1),
            "CPU_UPTIME": f"{days}d {hours}h {minutes}m",
            "LOAD_AVG": "0.42",
            "MEMORY_USED": "54.7",
            "SYSTEM_MEMORY": 162.8,
            "SYSTEM_memoryusage": 38.4,
            "SYSTEM_cpu_temperature": self.sensor_drift["CPU_TEMP"],
            "SYSTEM_carrier_cpu_temperature": self.sensor_drift["CPU_TEMP"] - 10.0,
            "SYSTEM_dosagemodule_alive_count": "18934721",
            "SYSTEM_dosagemodule_cpu_temperature": self.sensor_drift["CPU_TEMP"] - 0.4,
            "SYSTEM_ext1module_alive_count": "47291033",
            "IMP1_value": round(1.23 + random.uniform(-0.1, 0.1), 2),
            "IMP2_value": round(8.64 + random.uniform(-0.1, 0.1), 2),
            "ADC1_value": 0.31,
            "ADC2_value": 42,
            "ADC3_value": 27.3,
            "orp_value": self.sensor_drift["orp_value"],
            "orp_value_max": round(self.sensor_drift["orp_value"] + 27.0, 1),
            "orp_value_min": round(self.sensor_drift["orp_value"] - 27.0, 1),
            "pH_value": self.sensor_drift["pH_value"],
            "pH_value_max": round(self.sensor_drift["pH_value"] + 0.17, 2),
            "pH_value_min": round(self.sensor_drift["pH_value"] - 0.13, 2),
            "pot_value": self.sensor_drift["pot_value"],
            "pot_value_max": round(self.sensor_drift["pot_value"] + 0.23, 2),
            "pot_value_min": round(self.sensor_drift["pot_value"] - 0.21, 2),
            # One-wire temperature sensors (pool, solar, ambient, etc.)
            **{f"onewire{n}_value": round(25.0 + random.uniform(-5, 7), 1) for n in range(1, 11)},
            **{f"onewire{n}_value_min": round(24.0, 1) for n in range(1, 11)},
            **{f"onewire{n}_value_max": round(26.0, 1) for n in range(1, 11)},
            **{f"onewire{n}_state": "OK" for n in range(1, 11)},
            "onewire1_romcode": "28121883321901A9",
            "PUMPSTATE": str(self.outputs["PUMP"]),
            "PUMPPRIOSTATE": str(self.outputs["PUMP"]),
            "SOLARSTATE": str(self.outputs["SOLAR"]),
            "HEATERSTATE": str(self.outputs["HEATER"]),
            "LIGHTSTATE": str(self.outputs["LIGHT"]),
            "SOLAR_maxtemp": self.config.get("SOLAR_maxtemp", 28.0),
            "HEATER_set_temp": self.config.get("HEATER_set_temp", 28.0),
            "PUMP_LAST_ON": self.last_on_off.get("PUMP_LAST_ON", now - 600),
            "PUMP_LAST_OFF": self.last_on_off.get("PUMP_LAST_OFF", now - 7200),
            "PUMP_RUNTIME": "04h 33m 12s",
            "PUMP_RPM_0": 0,
            "PUMP_RPM_1": 0,
            "PUMP_RPM_2": 1,
            "PUMP_RPM_3": 0,
            # Cover and refill state
            "COVER_STATE": "OPEN",
            "REFILL_STATE": "OFF",
            "OVERFLOW_REFILL_STATE": "OFF",
            "BACKWASH_STATE": "NEXT_BW_IN 6 BW_DAY5",
            "BACKWASH_STEP": 0,
            "BACKWASH_DELAY_RUNNING": "NO",
            # Digital inputs
            **{f"INPUT{n}": 0 for n in range(1, 13)},
            "INPUTz1z2": 1,
            "INPUT_CE1": 0, "INPUT_CE2": 0, "INPUT_CE3": 0, "INPUT_CE4": 0,
            "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "12.5",
            "DOS_1_CL_LAST_CAN_RESET": "1700000000000",
            "DOS_1_CL_LAST_OFF": str(now - 300),
            "DOS_1_CL_LAST_ON": str(now - 600),
            "DOS_1_CL_RUNTIME": "00h 15m 30s",
            "DOS_1_CL_STATE": "[]",
            "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": "4750.0",
            "DOS_1_CL_TYPE": "1",
            "DOS_1_CL_USE": self.config.get("DOSAGE_chlorine_use", "1"),
            "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": "0.0",
            "DOS_2_ELO_USE": self.config.get("DOSAGE_electrolysis_use", "0"),
            "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "8.3",
            "DOS_4_PHM_USE": self.config.get("DOSAGE_phminus_use", "1"),
            "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "0.0",
            "DOS_5_PHP_USE": self.config.get("DOSAGE_phplus_use", "0"),
            "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "3.1",
            "DOS_6_FLOC_USE": self.config.get("DOSAGE_floc_use", "1"),
        }

        for key, state in self.outputs.items():
            readings[key] = state

        for dos_key, dos_st in self.dosing_state.items():
            if dos_st == "running":
                readings[dos_key] = 4

        return readings

    def build_readings_standalone(self) -> list[dict[str, Any]]:
        self.update_sensor_drift()
        entries: list[dict[str, Any]] = [
            {"VALUE NAME": '   "date"', "DESCRIPTION": "System-date", "FORMAT": "STRING",
             "VALUE": datetime.now(tz=UTC).strftime("%d.%m.%Y")},
            {"VALUE NAME": '   "time"', "DESCRIPTION": "System-time", "FORMAT": "STRING",
             "VALUE": datetime.now(tz=UTC).strftime("%H:%M:%S")},
            {"VALUE NAME": '   "CPU_TEMP"', "DESCRIPTION": "CPU-Temperature", "FORMAT": "FLOAT",
             "VALUE": self.sensor_drift["CPU_TEMP"]},
        ]
        for dos_key, dos_st in self.dosing_state.items():
            entries.append({
                "VALUE NAME": f'   "{dos_key}"',
                "DESCRIPTION": f"Current state of OUTPUT: {dos_key}",
                "FORMAT": "INTEGER",
                "VALUE": 4 if dos_st == "running" else 0,
            })
            entries.append({
                "VALUE NAME": f'   "{dos_key}_USE"',
                "DESCRIPTION": "Configured",
                "FORMAT": "STRING",
                "VALUE": "1",
            })
        return entries


_ctrl = MockController()


def _log_request(request: web.Request) -> None:
    _ctrl.request_count += 1
    _LOGGER.info(
        "[%d] %s %s (query: %s)",
        _ctrl.request_count,
        request.method,
        request.path,
        request.query_string,
    )


async def _maybe_delay() -> None:
    if _SIMULATED_DELAY > 0:
        await asyncio.sleep(_SIMULATED_DELAY)


def _check_error_mode() -> web.Response | None:
    if _ctrl.error_mode is not None and _ctrl.error_count > 0:
        _ctrl.error_count -= 1
        if _ctrl.error_count <= 0:
            _LOGGER.info("Error mode exhausted, returning to normal")
            _ctrl.error_mode = None
        _LOGGER.warning("Returning forced error: %d", _ctrl.error_mode or 500)
        return web.Response(status=_ctrl.error_mode, text=f"FORCED ERROR {_ctrl.error_mode}")
    return None


async def handle_get_readings(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    if (err := _check_error_mode()) is not None:
        return err

    query = request.query_string.upper() if request.query_string else ""

    if _STANDALONE_MODE:
        readings_data = _ctrl.build_readings_standalone()
    else:
        readings_data = _ctrl.build_readings()
        if query and query != "ALL":
            categories = [c.strip().upper() for c in query.split(",")]
            filtered: dict[str, Any] = {}
            for key, value in readings_data.items():
                if any(cat in key.upper() for cat in categories):
                    filtered[key] = value
            readings_data = filtered

    return web.json_response({"getReadings": readings_data})


async def handle_get_config(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    if (err := _check_error_mode()) is not None:
        return err

    query = request.query_string
    if query:
        keys = [k.strip() for k in query.split(",")]
        result = {k: _ctrl.config.get(k, "N/A") for k in keys}
    else:
        result = dict(_ctrl.config)
    return web.json_response(result)


async def handle_set_config(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    if (err := _check_error_mode()) is not None:
        return err

    data = await request.post()
    for key, value in data.items():
        str_key = str(key)
        _ctrl.config[str_key] = value
        _LOGGER.debug("  -> config updated: %s = %s", str_key, value)
    return web.Response(text="OK")


async def handle_set_function_manually(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    if (err := _check_error_mode()) is not None:
        return err

    query = request.query_string
    if not query:
        return web.Response(text="ERROR\nMissing query parameter")

    parts = query.split(",")
    key = parts[0]
    action = parts[1] if len(parts) > 1 else "ON"
    duration = parts[2] if len(parts) > 2 else "0"
    value = parts[3] if len(parts) > 3 else "0"

    _ctrl.set_switch(key, action)

    now_str = datetime.now(tz=UTC).strftime("%d.%m.%Y %H:%M")
    _ctrl.log_entries.insert(0, f"{now_str} | {key} | {action} | Manual")
    if len(_ctrl.log_entries) > 100:
        _ctrl.log_entries = _ctrl.log_entries[:100]

    _LOGGER.info("  -> %s action=%s duration=%s value=%s", key, action, duration, value)
    return web.Response(text=f"OK\n{key}\n{action}")


async def handle_trigger_manual_dosing(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    if (err := _check_error_mode()) is not None:
        return err

    data = await request.post()
    action = data.get("action", "DOSSTART")
    output = data.get("output", "0")
    runtime = data.get("runtime", "0")

    dos_keys = {0: "DOS_1_CL", 1: "DOS_2_ELO", 3: "DOS_4_PHM", 4: "DOS_5_PHP", 5: "DOS_6_FLOC"}
    dos_key = dos_keys.get(int(output), "DOS_UNKNOWN")

    now_str = datetime.now(tz=UTC).strftime("%d.%m.%Y %H:%M")
    if action == "DOSSTART":
        _ctrl.dosing_state[dos_key] = "running"
        _ctrl.log_entries.insert(0, f"{now_str} | {dos_key} | MANDOS_START | runtime={runtime}s")
        _LOGGER.info("  -> dosing START %s runtime=%s", dos_key, runtime)
        return web.Response(text="MANDOS_STARTED\nOK")
    else:
        _ctrl.dosing_state[dos_key] = "stopped"
        _ctrl.log_entries.insert(0, f"{now_str} | {dos_key} | MANDOS_STOP | manual")
        _LOGGER.info("  -> dosing STOP %s", dos_key)
        return web.Response(text="MANDOS_STOPPED\nOK")


async def handle_get_history(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()

    hours = request.query.get("hours", "24")
    sensor = request.query.get("sensor", "ALL")
    now = int(time.time())
    points = min(int(hours) * 4, 96)
    entries: dict[str, list[list[Any]]] = {
        "pH": [[now - i * 900, round(_ctrl.sensor_drift["pH_value"] + random.uniform(-0.3, 0.3), 2)] for i in range(points)],
        "ORP": [[now - i * 900, round(_ctrl.sensor_drift["orp_value"] + random.uniform(-50, 50), 1)] for i in range(points)],
        "CL": [[now - i * 900, round(_ctrl.sensor_drift["pot_value"] + random.uniform(-0.2, 0.2), 2)] for i in range(points)],
    }
    if sensor and sensor != "ALL" and sensor in entries:
        return web.json_response({sensor: entries[sensor]})
    return web.json_response(entries)


async def handle_get_weatherdata(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    return web.json_response({
        "temp": round(25.3 + random.uniform(-2, 2), 1),
        "condition": random.choice(["sunny", "partly_cloudy", "cloudy"]),
        "humidity": random.randint(35, 65),
        "wind_speed": round(12.5 + random.uniform(-3, 3), 1),
        "forecast": "clear",
    })


async def handle_get_overall_dosing(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    return web.json_response({
        "CL": {"daily_ml": 12.5, "total_ml": 4750.0},
        "PHM": {"daily_ml": 8.3, "total_ml": 3200.0},
        "PHP": {"daily_ml": 0.0, "total_ml": 0.0},
        "FLOC": {"daily_ml": 3.1, "total_ml": 1500.0},
    })


async def handle_get_output_runtimes(request: web.Request) -> web.Response:
    """GET /getOutputruntimes — JSON dict of runtime/timestamp stats per output."""
    _log_request(request)
    await _maybe_delay()
    now = int(time.time())
    uptime_start = time.monotonic() - _ctrl.start_time
    days = int(uptime_start // 86400)
    hours = int((uptime_start % 86400) // 3600)
    minutes = int((uptime_start % 3600) // 60)
    return web.json_response({
        "PUMP_RUNTIME": "04h 33m 12s",
        "PUMP_LAST_ON": now - 600,
        "PUMP_LAST_OFF": now - 7200,
        "SOLAR_RUNTIME": "01h 02m 03s",
        "SOLAR_LAST_ON": now - 1800,
        "SOLAR_LAST_OFF": now - 5400,
        "HEATER_RUNTIME": "00h 00m 00s",
        "HEATER_LAST_ON": 0,
        "HEATER_LAST_OFF": 0,
        "CPU_UPTIME": f"{days}d {hours}h {minutes}m",
        "LOAD_AVG": "0.42",
        "fw": _ctrl.fw_installed,
        "SW_VERSION": _ctrl.fw_installed,
    })


async def handle_get_outputstates(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    state_map = {0: ("AUTO", False), 1: ("AUTO", True), 2: ("AUTO", False), 3: ("AUTO", True), 4: ("MANUAL", True), 5: ("AUTO", False), 6: ("MANUAL", False)}
    result = {}
    for key, state_val in _ctrl.outputs.items():
        mode, active = state_map.get(state_val, ("UNKNOWN", False))
        result[key] = {"state": state_val, "mode": mode, "active": active}
    for dos_key, dos_st in _ctrl.dosing_state.items():
        is_running = dos_st == "running"
        result[dos_key] = {"state": 4 if is_running else 0, "mode": "MANUAL" if is_running else "AUTO", "active": is_running}
    return web.json_response(result)


async def handle_get_calib_raw_values(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    return web.json_response({
        "pH_raw": round(512 + random.uniform(-5, 5), 1),
        "pH_mv": round(random.uniform(-0.1, 0.1), 3),
        "ORP_raw": round(750 + random.uniform(-10, 10), 1),
        "CL_raw": round(320 + random.uniform(-8, 8), 1),
        "CL_mv": round(random.uniform(-0.1, 0.1), 3),
    })


async def handle_get_calib_history(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    sensor = request.query_string.strip() if request.query_string else "pH"
    now = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    lines = [
        f"{now} | 7.20 | {sensor}_CALIB",
        f"{now} | 750.00 | ORP_CALIB",
    ]
    return web.Response(text="\n".join(lines))


async def handle_restore_old_calib(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    data = await request.post()
    _LOGGER.info("  -> restore calibration: %s", dict(data))
    return web.Response(text="OK")


async def handle_set_output_testmode(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    query = request.query_string
    if not query:
        return web.Response(text="ERROR\nMissing query parameter")

    parts = query.split(",")
    output = parts[0]
    mode = parts[1] if len(parts) > 1 else "SWITCH"
    duration = parts[2] if len(parts) > 2 else "120000"
    _LOGGER.info("  -> testmode output=%s mode=%s duration=%s", output, mode, duration)
    return web.Response(text=f"OK\n{output}\nTESTMODE {mode}")


async def handle_get_log(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    text = "\n".join(_ctrl.log_entries)
    if len(_ctrl.log_entries) >= 20:
        text += "\nLOAD_MORE"
    return web.Response(text=text)


async def handle_get_notifications(request: web.Request) -> web.Response:
    _log_request(request)
    await _maybe_delay()
    return web.json_response(_ctrl.notifications)


async def handle_reset_blocking(request: web.Request) -> web.Response:
    """GET /resetBlocking — clear fault blockings (e.g. BLOCKED_BY_ESC)."""
    _log_request(request)
    await _maybe_delay()
    _ctrl.reset_blocking_calls += 1
    # Mirror the real controller: clear BLOCKED_BY_ESC on every dosing output.
    for key in _ctrl.dosing_state:
        _ctrl.dosing_state[key] = "stopped"
    return web.Response(text="OK\nBLOCKINGS_CLEARED")


async def handle_set_can_amount(request: web.Request) -> web.Response:
    """POST /setCanAmount — update canister fill level after refill."""
    _log_request(request)
    await _maybe_delay()
    if (err := _check_error_mode()) is not None:
        return err
    data = await request.post()
    action = str(data.get("action", "ADJUST")).upper()
    which = str(data.get("which", ""))
    cid = str(data.get("cid", ""))
    try:
        amount = int(data.get("amount", "0"))
    except ValueError:
        return web.Response(text="ERROR\nINVALID_AMOUNT", status=400)

    if which not in _ctrl.can_amounts:
        return web.Response(text=f"ERROR\nUNKNOWN_KEY:{which}", status=400)

    _ctrl.can_amounts[which] = amount
    _LOGGER.info(
        "  -> setCanAmount: action=%s which=%s cid=%s amount=%d",
        action,
        which,
        cid,
        amount,
    )
    return web.Response(text=f"OK\n{which}\n{amount}")


# Map service name -> handler state field on _ctrl.services.
_SERVICE_ENDPOINT_MAP = {
    "/enableFTP": ("ftp", True),
    "/disableFTP": ("ftp", False),
    "/enableSAMBA": ("samba", True),
    "/disableSAMBA": ("samba", False),
    "/enableSSH": ("ssh", True),
    "/disableSSH": ("ssh", False),
    "/enableSHAIRPORT": ("shairport", True),
    "/disableSHAIRPORT": ("shairport", False),
    "/enableHOMEBRIDGE": ("homekit", True),
    "/disableHOMEBRIDGE": ("homekit", False),
    "/enableALEXA": ("alexa", True),
    "/disableALEXA": ("alexa", False),
    "/enableTUNNEL": ("tunnel_state", True),
    "/disableTUNNEL": ("tunnel_state", False),
    "/enableSUPPORTTUNNEL": ("support_tunnel_state", True),
    "/disableSUPPORTTUNNEL": ("support_tunnel_state", False),
}


async def handle_toggle_service(request: web.Request) -> web.Response:
    """GET /enable* or /disable* — flip a controller system service."""
    _log_request(request)
    await _maybe_delay()
    info = _SERVICE_ENDPOINT_MAP.get(request.path)
    if info is None:
        return web.Response(text="ERROR\nUNKNOWN_ENDPOINT", status=404)
    state_key, new_value = info
    _ctrl.services[state_key] = 1 if new_value else 0
    _LOGGER.info("  -> %s: %s=%d", request.path, state_key, _ctrl.services[state_key])
    return web.Response(text="OK\n" + request.path.lstrip("/"))


async def handle_get_service_states(request: web.Request) -> web.Response:
    """GET /getServiceStates — JSON dict of system service flags."""
    _log_request(request)
    await _maybe_delay()
    now = datetime.now(tz=UTC)
    return web.json_response({
        **_ctrl.services,
        "date": now.strftime("%d.%m.%Y"),
        "time": now.strftime("%H:%M:%S"),
    })


# OmniTronic multi-port valve state — driven by /setFunctionManually?OMNI,OMNI_DC<N>.
async def handle_set_omni_position(request: web.Request) -> web.Response:
    """GET /setFunctionManually?OMNI,OMNI_DC<N> — drive the multi-port valve."""
    _log_request(request)
    await _maybe_delay()
    query = request.url.query.get("query", "") or request.url.path_qs.split("?", 1)[-1]
    # Parse "OMNI,OMNI_DC<N>,0,0"
    parts = query.split(",")
    if len(parts) < 2 or parts[0] != "OMNI":
        return web.Response(text="ERROR\nINVALID_QUERY", status=400)
    state = parts[1]
    if not state.startswith("OMNI_DC"):
        return web.Response(text=f"ERROR\nINVALID_STATE:{state}", status=400)
    try:
        pos = int(state.removeprefix("OMNI_DC"))
    except ValueError:
        return web.Response(text=f"ERROR\nINVALID_STATE:{state}", status=400)
    if not 0 <= pos <= 5:
        return web.Response(text=f"ERROR\nPOS_OUT_OF_RANGE:{pos}", status=400)
    _ctrl.omni_position = pos
    _LOGGER.info("  -> OMNI position set to %d", pos)
    return web.Response(text=f"OK\nOMNITRONIC\n{state}\n")


async def handle_get_rs485_pump_data(request: web.Request) -> web.Response:
    """GET /getRS485PumpData?<PUMP_NAME> — return pump live data + registers."""
    _log_request(request)
    await _maybe_delay()
    pump_name = request.url.query_string.split(",")[0] if request.url.query_string else ""
    # Pump configs are static; we synthesise a minimal valid response.
    if pump_name not in ("BADU_ECO_DRIVE_II", "BADU_ECO_FLEX", "BADU_PRIME_NEO_VS"):
        return web.Response(text=f'ERROR\nUNKNOWN_PUMP:{pump_name}', status=400)
    return web.json_response({
        "BRAND": "BADU",
        "NAME": pump_name.removeprefix("BADU_").replace("_", " "),
        "pump_rs485_pwr": 450,
        "pump_rs485_units": "W",
        "FLOW_value": -1,
        "PUMP_blocked": "NO",
        "BACKWASH_STEP": 0,
        "SLAVE_PRESENT": "YES",
        "MOTIONCONTROLMODE_VALIDMODES": "HZ",
        "SETTARGET_HZ_VALIDMIN": 5,
        "SETTARGET_HZ_VALIDMAX": 50,
    })


async def handle_set_rs485_live(request: web.Request) -> web.Response:
    """GET /setRS485Live?<pump>,<slave>,<mode>,<level>  OR  ?DONE."""
    _log_request(request)
    await _maybe_delay()
    qs = request.url.query_string
    if qs.upper() == "DONE":
        _ctrl.rs485_live_active = False
        return web.Response(text='"DONE"')
    parts = qs.split(",")
    if len(parts) != 4:
        return web.Response(text='"INVALID. Query too short."', status=400)
    pump_name, slave_id, mode, level = parts
    if pump_name not in ("BADU_ECO_DRIVE_II", "BADU_ECO_FLEX", "BADU_PRIME_NEO_VS"):
        return web.Response(text='"INVALID. Unknown pump."')
    _ctrl.rs485_live_active = True
    _ctrl.rs485_live_mode = mode
    _ctrl.rs485_live_level = level
    return web.Response(text=f'"{slave_id}|0,0|2,{level}"')


async def handle_get_live_trace(request: web.Request) -> web.Response:
    """GET /getLiveTrace — 3-line CSV (header; units; values)."""
    _log_request(request)
    await _maybe_delay()
    header = "epoch;date;time;onewire1_value;pH_value;orp_value;pot_value;PUMP;HEATER"
    units = "ms;;;°C; ;mV;mg/l; ; "
    values = "1709234445000;29.02.2024;19:50:02;7.30;7.3;770;0.6;1;0"
    body = "\n".join((header, units, values))
    return web.Response(text=body, content_type="text/plain")


async def handle_set_target_values(request: web.Request) -> web.Response:
    """GET /setTargetValues?target=KEY&value=VAL — set a target value."""
    _log_request(request)
    await _maybe_delay()
    if (err := _check_error_mode()) is not None:
        return err
    target = request.query.get("target", "")
    value = request.query.get("value", "")
    if target:
        _ctrl.config[target] = value
        _LOGGER.info("  -> setTargetValues: %s = %s", target, value)
    return web.json_response({"ok": True})


async def handle_set_dosing_parameters(request: web.Request) -> web.Response:
    """POST /setDosingParameters — merge JSON into dosing parameters."""
    _log_request(request)
    await _maybe_delay()
    if (err := _check_error_mode()) is not None:
        return err
    data = await request.post()
    for key, value in data.items():
        _ctrl.config[str(key)] = value
        _LOGGER.debug("  -> dosing param: %s = %s", key, value)
    return web.json_response({"ok": True})


# ---------------------------------------------------------------------------
# Mock control endpoints (NOT part of the real controller API)
# ---------------------------------------------------------------------------

async def handle_mock_state(request: web.Request) -> web.Response:
    return web.json_response({
        "standalone_mode": _STANDALONE_MODE,
        "simulated_delay": _SIMULATED_DELAY,
        "request_count": _ctrl.request_count,
        "uptime_seconds": round(time.monotonic() - _ctrl.start_time, 1),
        "outputs": _ctrl.outputs,
        "dosing_state": _ctrl.dosing_state,
        "sensor_drift": _ctrl.sensor_drift,
        "config": _ctrl.config,
        "firmware": {
            "installed": _ctrl.fw_installed,
            "available": _ctrl.fw_available,
            "carrier": _ctrl.fw_carrier,
        },
        "error_mode": _ctrl.error_mode,
        "error_count_remaining": _ctrl.error_count,
        "log_entries_count": len(_ctrl.log_entries),
    })


async def handle_mock_error(request: web.Request) -> web.Response:
    code = int(request.query.get("code", "500"))
    count = int(request.query.get("count", "1"))
    _ctrl.error_mode = code
    _ctrl.error_count = count
    _LOGGER.warning("Error mode activated: HTTP %d for next %d request(s)", code, count)
    return web.json_response({"status": "ok", "message": f"Next {count} request(s) will return HTTP {code}"})


async def handle_mock_reset(request: web.Request) -> web.Response:
    _ctrl.reset()
    _LOGGER.info("Mock controller state reset to defaults")
    return web.json_response({"status": "ok", "message": "State reset to defaults"})


async def handle_mock_firmware(request: web.Request) -> web.Response:
    """Simulate a manufacturer firmware update being available.

    GET /mock/firmware?available=1.2.0   → SW_UPDATE_AVAILABLE will be "1.2.0"
    GET /mock/firmware?available=        → no update (up to date)
    GET /mock/firmware?installed=1.2.0   → change the installed version
    GET /mock/firmware                   → just read current state
    """
    installed = request.query.get("installed")
    available = request.query.get("available")

    if installed is not None:
        _ctrl.fw_installed = installed.strip() or "0.0.0"
    if available is not None:
        stripped = available.strip()
        _ctrl.fw_available = stripped or None

    _LOGGER.info(
        "Firmware mock: installed=%s available=%s",
        _ctrl.fw_installed,
        _ctrl.fw_available or "(none)",
    )
    return web.json_response({
        "installed": _ctrl.fw_installed,
        "available": _ctrl.fw_available,
        "carrier": _ctrl.fw_carrier,
        "update_available": _ctrl.fw_available is not None,
    })


@web.middleware
async def auth_middleware(
    request: web.Request,
    handler: Any,  # noqa: ANN401
) -> web.Response:
    # The real Violet controller does not require auth for /getReadings.
    # Mock control endpoints (/mock/*) are never authenticated either.
    if request.path == "/getReadings" or request.path.startswith("/mock/"):
        return await handler(request)

    if _AUTH_CREDENTIALS is not None:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Basic "):
            _LOGGER.warning("AUTH REJECT: missing/invalid Authorization header from %s", request.remote)
            return web.Response(
                status=401,
                text="Unauthorized",
                headers={"WWW-Authenticate": 'Basic realm="Violet Pool Controller"'},
            )
        try:
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            username, password = decoded.split(":", 1)
        except (Exception):
            _LOGGER.warning("AUTH REJECT: malformed Basic auth from %s", request.remote)
            return web.Response(status=401, text="Unauthorized")

        expected_user, expected_pass = _AUTH_CREDENTIALS
        if username != expected_user or password != expected_pass:
            _LOGGER.warning(
                "AUTH REJECT: wrong credentials user=%r from %s",
                username,
                request.remote,
            )
            return web.Response(status=401, text="Unauthorized")

        _LOGGER.debug("AUTH OK: user=%r", username)

    return await handler(request)


def create_app() -> web.Application:
    app = web.Application(middlewares=[auth_middleware])

    app.router.add_get("/getReadings", handle_get_readings)
    app.router.add_get("/getConfig", handle_get_config)
    app.router.add_post("/setConfig", handle_set_config)
    app.router.add_get("/setFunctionManually", handle_set_function_manually)
    app.router.add_get("/setTargetValues", handle_set_target_values)
    app.router.add_post("/setDosingParameters", handle_set_dosing_parameters)
    app.router.add_post("/triggerManualDosing", handle_trigger_manual_dosing)
    app.router.add_get("/getHistory", handle_get_history)
    app.router.add_get("/getWeatherdata", handle_get_weatherdata)
    app.router.add_get("/getOverallDosing", handle_get_overall_dosing)
    app.router.add_get("/getOutputstates", handle_get_outputstates)
    app.router.add_get("/getOutputruntimes", handle_get_output_runtimes)
    app.router.add_get("/getCalibRawValues", handle_get_calib_raw_values)
    app.router.add_get("/getCalibHistory", handle_get_calib_history)
    app.router.add_post("/restoreOldCalib", handle_restore_old_calib)
    app.router.add_get("/setOutputTestmode", handle_set_output_testmode)
    app.router.add_get("/getLog", handle_get_log)
    app.router.add_get("/getNotifications", handle_get_notifications)
    app.router.add_get("/resetBlocking", handle_reset_blocking)
    app.router.add_post("/setCanAmount", handle_set_can_amount)
    app.router.add_get("/getServiceStates", handle_get_service_states)
    # System service toggles – one route per enable/disable endpoint.
    for endpoint in _SERVICE_ENDPOINT_MAP:
        app.router.add_get(endpoint, handle_toggle_service)
    # RS485 pump endpoints.
    app.router.add_get("/getRS485PumpData", handle_get_rs485_pump_data)
    app.router.add_get("/setRS485Live", handle_set_rs485_live)
    # Live trace (single-row snapshot of every reading).
    app.router.add_get("/getLiveTrace", handle_get_live_trace)

    app.router.add_get("/mock/state", handle_mock_state)
    app.router.add_get("/mock/error", handle_mock_error)
    app.router.add_get("/mock/reset", handle_mock_reset)
    app.router.add_get("/mock/firmware", handle_mock_firmware)

    return app


def main() -> None:
    global _STANDALONE_MODE, _SIMULATED_DELAY, _AUTH_CREDENTIALS  # noqa: PLW0603

    parser = argparse.ArgumentParser(
        description="Violet Pool Controller Mock Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Control endpoints (not on real controller):
  GET /mock/state                          -> current internal state as JSON
  GET /mock/error?code=500&count=3         -> force next 3 requests to return HTTP 500
  GET /mock/reset                          -> reset all state to defaults
  GET /mock/firmware?available=1.2.0       -> simulate firmware update available
  GET /mock/firmware?available=            -> clear firmware update (up to date)

Examples:
  python tests/mock_server.py --user admin --password secret
  python tests/mock_server.py --standalone --delay 0.2 --user admin --password test
""",
    )
    parser.add_argument("--port", type=int, default=8480, help="Port (default: 8480)")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--standalone", action="store_true", help="Dosing-standalone mode")
    parser.add_argument("--delay", type=float, default=0.0, help="Simulated latency in seconds (default: 0)")
    parser.add_argument("--user", default=None, help="Username for Basic Auth (enables auth if set)")
    parser.add_argument("--password", default=None, help="Password for Basic Auth")
    args = parser.parse_args()

    _STANDALONE_MODE = args.standalone
    _SIMULATED_DELAY = args.delay

    if args.user:
        _AUTH_CREDENTIALS = (args.user, args.password or "")
        _LOGGER.info("Basic Auth enabled: user=%r", args.user)

    if _STANDALONE_MODE:
        _LOGGER.info("Running in DOSING-STANDALONE mode (list format)")
    if _SIMULATED_DELAY > 0:
        _LOGGER.info("Simulated network delay: %.0fms", _SIMULATED_DELAY * 1000)

    _LOGGER.info("Starting Violet Pool Controller Mock Server on %s:%s", args.host, args.port)
    _LOGGER.info("Connect your API client to http://%s:%s", args.host or "localhost", args.port)

    app = create_app()
    web.run_app(app, host=args.host, port=args.port, print=_LOGGER.info)


if __name__ == "__main__":
    main()
