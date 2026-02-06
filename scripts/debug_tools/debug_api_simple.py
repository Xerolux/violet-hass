#!/usr/bin/env python3
"""Simple debug script using only standard library."""

import json
import urllib.request
import urllib.error
import base64


def fetch_api_data():
    """Fetch and analyze API data from the controller."""
    url = "http://192.168.178.55/getReadings?ALL"
    username = "Basti"
    password = "sebi2634"

    # Create basic auth header
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded}"}

    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode())

            print("=" * 80)
            print("FIRMWARE VERSION DETECTION")
            print("=" * 80)

            firmware_fields = [
                "FW", "fw", "SW_VERSION", "sw_version", "VERSION",
                "version", "SW_VERSION_CARRIER", "FIRMWARE_VERSION",
                "firmware_version", "FIRMWARE", "firmware"
            ]

            for field in firmware_fields:
                if field in data:
                    print(f"[OK] {field} = {data[field]}")

            print("\n" + "=" * 80)
            print("PUMP STATUS DETECTION")
            print("=" * 80)

            pump_fields = [
                "PUMP", "PUMP_STATE", "PUMPSTATE", "pump", "pump_state",
                "PUMP_STATUS", "FILTERPUMP", "FILTERPUMP_STATE"
            ]

            for field in pump_fields:
                if field in data:
                    print(f"[OK] {field} = {data[field]}")

            print("\n" + "=" * 80)
            print("FROST/FREEZE FIELDS")
            print("=" * 80)

            frost_count = 0
            for key in sorted(data.keys()):
                if "frost" in key.lower() or "freeze" in key.lower():
                    print(f"  {key} = {data[key]}")
                    frost_count += 1

            if frost_count == 0:
                print("  (No frost/freeze fields found)")

            # Save to file
            with open("api_data_full.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print("\n[OK] Full data saved to api_data_full.json")
            print(f"[OK] Total fields: {len(data)}")

            return data

    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP Error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        print(f"[ERROR] Connection error: {e.reason}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing error: {e}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

    return None


if __name__ == "__main__":
    print("\nViolet Pool Controller API Debug")
    print("=" * 80 + "\n")
    fetch_api_data()
