"""Read-only live check against a real Violet controller.

Usage:
    set VIOLET_HOST / VIOLET_USER / VIOLET_PASS, then:
    python tests/live_readonly_check.py

Performs ONLY GET requests (getReadings, getConfig, getLog) - no writes.
"""

import asyncio
import os
import sys

import aiohttp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "violet_poolcontroller_api"))

from violet_poolcontroller_api.api import VioletPoolAPI  # noqa: E402

HOST = os.environ["VIOLET_HOST"]
USER = os.environ["VIOLET_USER"]
PASS = os.environ["VIOLET_PASS"]

DOS_KEYS = ["DOS_1_CL", "DOS_2_ELO", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC"]
USE_KEYS = [
    "DOSAGE_chlorine_use",
    "DOSAGE_electrolysis_use",
    "DOSAGE_phminus_use",
    "DOSAGE_phplus_use",
    "DOSAGE_floc_use",
]


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(host=HOST, session=session, username=USER, password=PASS)

        print("=== 1. getReadings?ALL (auth + data check) ===")
        readings = await api.get_readings()
        print(f"OK - {len(readings)} keys received")
        for k in ("FW", "SW_VERSION", "HW_VERSION", "time", "date", "CPU_TEMP"):
            if k in readings:
                print(f"  {k} = {readings[k]}")

        print("\n=== 2. Dosing channel states ===")
        for key in DOS_KEYS:
            state = readings.get(key, "<missing>")
            detail = readings.get(f"{key}_STATE", "<missing>")
            runtime = readings.get(f"{key}_RUNTIME", "<missing>")
            daily = readings.get(f"{key}_DAILY_DOSING_AMOUNT_ML", "<missing>")
            print(f"  {key}: state={state} detail={detail} runtime={runtime} daily_ml={daily}")

        print("\n=== 3. DOSAGE_*_use config flags (getConfig) ===")
        cfg = await api.get_config(USE_KEYS)
        for k in USE_KEYS:
            print(f"  {k} = {cfg.get(k, '<missing>')}")

        print("\n=== 4. Key sensor values + plausibility ===")
        checks = [
            ("PH_value", "pH", 6.0, 8.5),
            ("ORP_value", "mV", 300, 1000),
            ("POT_value", "mg/l", 0, 5),
            ("onewire1_value", "degC pool", 0, 45),
            ("onewire2_value", "degC", -20, 90),
            ("ADC1_value", "bar?", -1, 10),
            ("IMP1_value", "imp", 0, 100000),
            ("IMP2_value", "imp", 0, 100000),
        ]
        for key, unit, lo, hi in checks:
            val = readings.get(key)
            if val is None:
                print(f"  {key}: <not present>")
                continue
            try:
                f = float(val)
                flag = "OK" if lo <= f <= hi else "OUT OF RANGE?"
                print(f"  {key} = {val} {unit}  [{flag}]")
            except (TypeError, ValueError):
                print(f"  {key} = {val!r} (non-numeric)")

        print("\n=== 5. Output states overview ===")
        for key in ("PUMP", "HEATER", "SOLAR", "LIGHT", "BACKWASH", "PVSURPLUS"):
            print(f"  {key}: {readings.get(key, '<missing>')}")

        print("\n=== 6. Last action log entries ===")
        try:
            log = await api.get_log("actions", page=0)
            for line in log["lines"][:10]:
                print(f"  {line}")
        except Exception as err:  # noqa: BLE001
            print(f"  getLog failed: {err}")

        print("\nDONE - all read-only checks completed")


asyncio.run(main())
