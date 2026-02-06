#!/usr/bin/env python3
"""Test if device setup correctly extracts firmware version."""

import json


def extract_firmware(data):
    """Simulate firmware extraction logic from device.py."""
    firmware_version = (
        data.get("FW")
        or data.get("fw")
        or data.get("SW_VERSION")
        or data.get("sw_version")
        or data.get("VERSION")
        or data.get("version")
        or data.get("SW_VERSION_CARRIER")
        or data.get("FIRMWARE_VERSION")
        or data.get("firmware_version")
        or None
    )
    return firmware_version


if __name__ == "__main__":
    # Load API data
    with open("api_data_full.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 80)
    print("FIRMWARE EXTRACTION TEST")
    print("=" * 80)

    # Test the extraction
    fw = extract_firmware(data)
    print(f"\nExtracted firmware: '{fw}'")
    print(f"Type: {type(fw)}")
    print(f"Is None: {fw is None}")
    print(f"Bool value: {bool(fw)}")
    print(f"Will display as: {fw or 'Unbekannt'}")

    # Check individual fields
    print("\n" + "=" * 80)
    print("INDIVIDUAL FIELD CHECK")
    print("=" * 80)

    fields = ["FW", "fw", "SW_VERSION", "sw_version"]
    for field in fields:
        value = data.get(field)
        print(f"{field:20s} = {value!r:20s} (type: {type(value).__name__})")

    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)
    if fw and fw != "Unbekannt":
        print(f"✓ SUCCESS: Firmware '{fw}' should be displayed")
    else:
        print("✗ FAIL: Firmware extraction failed")
