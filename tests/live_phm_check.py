"""Live test: 5-second manual pH-minus dosing run (verifies output index 3)."""

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

        print("=== DOSSTART DOS_4_PHM (pH-), runtime=5s ===")
        result = await api.set_switch_state("DOS_4_PHM", "ON", duration=5)
        print(f"  result: {result}")

        await asyncio.sleep(1.5)
        readings = await api.get_readings()
        print(f"  during run: DOS_4_PHM = {readings.get('DOS_4_PHM')} "
              f"STATE={readings.get('DOS_4_PHM_STATE')}")

        await asyncio.sleep(8)
        readings = await api.get_readings()
        print(f"  after run:  DOS_4_PHM = {readings.get('DOS_4_PHM')} "
              f"STATE={readings.get('DOS_4_PHM_STATE')}")

        result = await api.set_switch_state("DOS_4_PHM", "OFF")
        print(f"  cleanup DOSSTOP: {result}")

        log = await api.get_log("actions", page=0)
        for line in log["lines"][:3]:
            print(f"  {line}")


asyncio.run(main())
