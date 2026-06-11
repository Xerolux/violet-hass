"""Safe live write test: DOSSTOP on an idle dosing channel.

Sends OFF and AUTO to DOS_1_CL while no manual dosing is running -
nothing is dispensed; validates POST /triggerManualDosing mechanics,
auth and the AUTO->DOSSTOP safety mapping (v0.0.27).
"""

import asyncio
import os
import sys

import aiohttp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "violet_poolcontroller_api"))

from violet_poolcontroller_api.api import VioletPoolAPI  # noqa: E402


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host=os.environ["VIOLET_HOST"],
            session=session,
            username=os.environ["VIOLET_USER"],
            password=os.environ["VIOLET_PASS"],
        )

        print("=== Test A: set_switch_state(DOS_1_CL, OFF) -> DOSSTOP (idle, harmless) ===")
        result = await api.set_switch_state("DOS_1_CL", "OFF")
        print(f"  result: {result}")

        print()
        print("=== Test B: set_switch_state(DOS_1_CL, AUTO) -> must also map to DOSSTOP ===")
        result = await api.set_switch_state("DOS_1_CL", "AUTO")
        print(f"  result: {result}")

        print()
        print("=== State after tests ===")
        readings = await api.get_readings()
        print(f"  DOS_1_CL = {readings.get('DOS_1_CL')} STATE={readings.get('DOS_1_CL_STATE')}")


asyncio.run(main())
