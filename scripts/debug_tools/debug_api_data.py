#!/usr/bin/env python3
"""Debug script to analyze Violet Pool Controller API data.

This script fetches data from your controller and helps identify:
1. Which field contains the firmware version
2. What state value the pump sends when in frost protection mode
"""

import asyncio
import aiohttp
import json


async def fetch_api_data():
    """Fetch and analyze API data from the controller."""
    url = "http://192.168.178.55/getReadings?ALL"
    auth = aiohttp.BasicAuth("Basti", "sebi2634")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, auth=auth, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()

                    print("=" * 80)
                    print("FIRMWARE VERSION DETECTION")
                    print("=" * 80)

                    # Check all possible firmware fields
                    firmware_fields = [
                        "FW", "fw", "SW_VERSION", "sw_version", "VERSION",
                        "version", "SW_VERSION_CARRIER", "FIRMWARE_VERSION",
                        "firmware_version", "FIRMWARE", "firmware"
                    ]

                    for field in firmware_fields:
                        if field in data:
                            print(f"✓ Found: {field} = {data[field]}")

                    print("\n" + "=" * 80)
                    print("PUMP STATUS DETECTION")
                    print("=" * 80)

                    # Check all possible pump fields
                    pump_fields = [
                        "PUMP", "PUMP_STATE", "PUMPSTATE", "pump", "pump_state",
                        "PUMP_STATUS", "FILTERPUMP", "FILTERPUMP_STATE"
                    ]

                    for field in pump_fields:
                        if field in data:
                            print(f"✓ Found: {field} = {data[field]}")

                    print("\n" + "=" * 80)
                    print("FROST PROTECTION DETECTION")
                    print("=" * 80)

                    # Check for frost protection fields
                    frost_fields = [
                        "FROST", "FROST_PROTECTION", "FREEZE", "FREEZE_PROTECTION",
                        "FROSTSCHUTZ", "frost", "frost_protection"
                    ]

                    for field in frost_fields:
                        if field in data:
                            print(f"✓ Found: {field} = {data[field]}")

                    # Search for any field containing "frost" or "freeze"
                    print("\nSearching for fields containing 'frost' or 'freeze':")
                    for key in data.keys():
                        if "frost" in key.lower() or "freeze" in key.lower():
                            print(f"  - {key} = {data[key]}")

                    print("\n" + "=" * 80)
                    print("ALL AVAILABLE KEYS")
                    print("=" * 80)
                    print("\nTotal fields:", len(data))
                    print("\nAll keys:")
                    for i, key in enumerate(sorted(data.keys()), 1):
                        print(f"  {i:3d}. {key}")

                    # Save full data to file
                    output_file = "api_data_full.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"\n✓ Full API data saved to: {output_file}")

                else:
                    print(f"❌ Error: HTTP {response.status}")
                    print(await response.text())

        except asyncio.TimeoutError:
            print("❌ Timeout connecting to controller")
        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("\nViolet Pool Controller API Debug Tool")
    print("=" * 80)
    print("Connecting to: http://192.168.178.55/getReadings?ALL")
    print("=" * 80 + "\n")

    asyncio.run(fetch_api_data())

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("""
1. Check the output above for firmware fields
2. Check what value PUMP/PUMP_STATE shows when frost protection is active
3. Check api_data_full.json for complete data
4. Share the findings so I can update the code accordingly
    """)
