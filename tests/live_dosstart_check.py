"""Live test of a short manual dosing run (the actual Flockung-fix path).

Starts a 5-second manual chlorine dosing via POST /triggerManualDosing,
verifies the channel switches to MANUAL_DOSING, waits for it to finish,
sends a DOSSTOP as cleanup and prints the controller action log.
"""

import asyncio
import os
import sys

import aiohttp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "violet_poolcontroller_api"))

from violet_poolcontroller_api.api import VioletPoolAPI  # noqa: E402

RUNTIME_S = 5


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host=os.environ["VIOLET_HOST"],
            session=session,
            username=os.environ["VIOLET_USER"],
            password=os.environ["VIOLET_PASS"],
        )

        print(f"=== DOSSTART DOS_1_CL, runtime={RUNTIME_S}s ===")
        result = await api.set_switch_state("DOS_1_CL", "ON", duration=RUNTIME_S)
        print(f"  result: {result}")

        await asyncio.sleep(1.5)
        readings = await api.get_readings()
        print(f"  during run: DOS_1_CL = {readings.get('DOS_1_CL')} "
              f"STATE={readings.get('DOS_1_CL_STATE')}")

        print(f"  waiting {RUNTIME_S + 3}s for the run to finish...")
        await asyncio.sleep(RUNTIME_S + 3)
        readings = await api.get_readings()
        print(f"  after run: DOS_1_CL = {readings.get('DOS_1_CL')} "
              f"STATE={readings.get('DOS_1_CL_STATE')}")

        print("=== Cleanup: DOSSTOP ===")
        result = await api.set_switch_state("DOS_1_CL", "OFF")
        print(f"  result: {result}")

        print("=== Controller action log (looking for MANDOS) ===")
        log = await api.get_log("actions", page=0)
        for line in log["lines"][:6]:
            print(f"  {line}")


asyncio.run(main())
