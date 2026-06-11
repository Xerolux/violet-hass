> [🇬🇧 English](Advanced-Topics) | [🇩🇪 Deutsch](de/Advanced-Topics) &nbsp;|&nbsp; [🏠](Home)

# Advanced Topics

## PV Surplus Mode
If you have a PV system integrated, you can enable the PV surplus mode to utilize excess solar energy.
```python
# Enable PV Surplus mode and force pump speed to 3
await api.set_pv_surplus(active=True, pump_speed=3)
```

## Test Mode
Activate the controller's hardware test mode for a specific output.
```python
await api.set_output_test_mode(output="RELAY_1", mode="SWITCH", duration=120)
```

## Hardware Profile Detection
The API can dynamically detect which hardware modules are attached to your Violet Controller by interrogating `get_readings()`.

When fetching readings, the API automatically determines if it connects to a standalone dosing unit or a base module based on the payload structure. The `dosing_standalone` property is updated automatically.

```python
profile = await api.get_hardware_profile()
print(profile)
# {
#     "base_module": True,
#     "dosing_module": True,
#     "extension_module_1": True,
#     "extension_module_2": False,
# }
```
This looks for keys such as `SYSTEM_dosagemodule_cpu_temperature`, `EXT1_1`, and `EXT2_1` to definitively identify presence. By verifying the exact components (Base Module, Dosing Module, Extensions), UI/Integrations can choose to only expose what's really connected, avoiding displaying unsupported features.

## Error Handling
All API interactions can raise `VioletPoolAPIError`. It is recommended to wrap calls in a try-except block.
```python
try:
    await api.get_readings()
except VioletPoolAPIError as e:
    print(f"API Error: {e}")
```

## Rate Limiting & Circuit Breaker
The API client comes with built-in protections:
- **Rate Limiter:** Prevents overwhelming the controller by queueing requests (e.g., max 10 requests per second).
- **Circuit Breaker:** Temporarily halts requests if multiple consecutive errors occur, allowing the controller to recover.
