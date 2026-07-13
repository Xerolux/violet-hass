#!/usr/bin/env python3
"""Quick integration import test - checks if all modules load correctly."""
# ruff: noqa: T201

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("=" * 60)
print("Violet Pool Controller - Quick Import Test")
print("=" * 60)
print()

errors = []
warnings = []

# Test 1: Import const module
print("📦 Testing const.py imports...")
try:
    from custom_components.violet_pool_controller import const
    print("  ✅ const.py imported successfully")
    print(f"  ℹ️  Version: {const.INTEGRATION_VERSION}")
    print(f"  ℹ️  Domain: {const.DOMAIN}")
except Exception as e:
    errors.append(f"const.py: {e}")
    print(f"  ❌ Failed: {e}")

# Test 2: Import const_api
print("\n📦 Testing const_api.py imports...")
try:
    from custom_components.violet_pool_controller import const_api
    print("  ✅ const_api.py imported successfully")
    print(f"  ℹ️  API Endpoints defined: {len([x for x in dir(const_api) if x.startswith('API_')])}")
except Exception as e:
    errors.append(f"const_api.py: {e}")
    print(f"  ❌ Failed: {e}")

# Test 3: Import const_sensors
print("\n📦 Testing const_sensors.py imports...")
try:
    print("  ✅ const_sensors.py imported successfully")
except Exception as e:
    errors.append(f"const_sensors.py: {e}")
    print(f"  ❌ Failed: {e}")

# Test 4: Import const_features
print("\n📦 Testing const_features.py imports...")
try:
    print("  ✅ const_features.py imported successfully")
except Exception as e:
    errors.append(f"const_features.py: {e}")
    print(f"  ❌ Failed: {e}")

# Test 5: Import const_devices
print("\n📦 Testing const_devices.py imports...")
try:
    print("  ✅ const_devices.py imported successfully")
except Exception as e:
    errors.append(f"const_devices.py: {e}")
    print(f"  ❌ Failed: {e}")

# Test 6: Check for ProCon.IP references
print("\n🔍 Checking for ProCon.IP references...")
try:
    # Check if any ProCon.IP constants exist
    proconip_refs = []
    for module in [const, const_api]:
        for attr in dir(module):
            if 'PROCON' in attr.upper():
                proconip_refs.append(f"{module.__name__}.{attr}")

    if proconip_refs:
        warnings.append(f"Found ProCon.IP references: {', '.join(proconip_refs)}")
        print(f"  ⚠️  Found references: {', '.join(proconip_refs)}")
    else:
        print("  ✅ No ProCon.IP references found")
except Exception as e:
    warnings.append(f"ProCon.IP check failed: {e}")

# Test 7: Check config flow schema validity
print("\n📋 Testing config_flow.py structure...")
try:
    # Read config_flow.py to check for issues
    config_flow_path = os.path.join(
        project_root,
        "custom_components/violet_pool_controller/config_flow.py"
    )
    with open(config_flow_path) as f:
        content = f.read()

    # Check for ProCon.IP references
    if 'proconip' in content.lower():
        warnings.append("config_flow.py still contains 'proconip' references")
        print("  ⚠️  Contains 'proconip' references")
    else:
        print("  ✅ No ProCon.IP references in config_flow.py")

    # Check for essential methods
    required_methods = [
        'async_step_user',
        'async_step_disclaimer',
        'async_step_connection',
        'async_step_pool_setup',
        'async_step_feature_selection'
    ]

    missing_methods = []
    for method in required_methods:
        if f'def {method}' not in content:
            missing_methods.append(method)

    if missing_methods:
        errors.append(f"Missing methods: {', '.join(missing_methods)}")
        print(f"  ❌ Missing: {', '.join(missing_methods)}")
    else:
        print("  ✅ All essential methods present")

except Exception as e:
    errors.append(f"config_flow.py check: {e}")
    print(f"  ❌ Failed: {e}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if errors:
    print(f"\n❌ ERRORS ({len(errors)}):")
    for error in errors:
        print(f"  • {error}")

if warnings:
    print(f"\n⚠️  WARNINGS ({len(warnings)}):")
    for warning in warnings:
        print(f"  • {warning}")

if not errors and not warnings:
    print("\n✅ All tests passed! Integration looks good.")
elif not errors:
    print("\n✅ No critical errors, but see warnings above.")
else:
    print("\n❌ Critical errors found. Please fix before testing with HA.")
    sys.exit(1)

print()
