# Changelog - Violet Pool Controller

All notable changes to this project will be documented in this file.

## [0.1.0-9]

### Changed
- **Code Cleanup**: Removed 221 lines of deprecated service handlers from `__init__.py`
- **Documentation**: Enhanced inline code documentation and comments
- **Imports**: Optimized import structure for better performance
- **Maintainability**: Reduced `__init__.py` from 451 to 230 lines (49% reduction)

### Fixed
- **Type Hints**: Improved type annotations throughout codebase
- **Logging**: More consistent debug/info logging levels

### Technical
- All services now exclusively in `services.py` (no duplicates)
- Cleaner separation of concerns between modules
- Better code organization for future maintenance

---

## [0.1.0-8]

### Added
- **Enhanced State Debugging**: New `extra_state_attributes` with detailed state interpretation
- **State Logic Explanation**: Added `_explain_state_logic()` method for troubleshooting
- **Extended Switch Attributes**: Runtime, last_on, last_off tracking for PUMP

### Changed
- **Switch State Interpretation**: Unified state handling across integer and string values
- **Binary Sensor Logic**: Improved boolean detection with extended value sets
- **Logging**: More verbose state change logging for debugging

### Fixed
- **State Consistency**: Fixed edge cases in state interpretation
- **None Handling**: Better None-value handling in state checks
- **Type Safety**: Improved type conversion error handling

---

## [0.1.0-7]

### Added
- **Flow Rate Sensor**: New `VioletFlowRateSensor` with ADC3/IMP2 prioritization
- **Sensor Transparency**: Added `extra_state_attributes` showing data source priority
- **Enhanced Debugging**: Source tracking for multi-sensor values (ADC3 > IMP2)

### Changed
- **pH Sensor Unit**: Removed unit from pH sensor (complies with HA specification)
  - pH Sensor: No unit (raw measurement)
  - pH Number: "pH" unit (for setpoints)
- **CPU Temperature**: Ensured °C unit for all CPU temperature sensors
- **Boolean Sensors**: Improved detection and handling of boolean value sensors

### Fixed
- **Unit Consistency**: Fixed unit assignment for temperature and flow sensors
- **Device Class**: Corrected device class assignment based on value types
- **State Class**: Proper state class handling for different sensor types

### Technical
- `apply_adc3_imp2_mapping()` now only logs (no data mutation)
- Flow rate prioritization handled in sensor's `native_value` property
- Better separation of concerns for sensor data handling

---

## [0.1.0-6]

### Added
- **State 4 Support**: Added missing State 4 (Manual Forced ON) to `STATE_MAP`
- **PVSURPLUS Function**: Added PVSURPLUS to `SWITCH_FUNCTIONS` dict
- **Extended State Documentation**: Comprehensive state mapping documentation

### Fixed
- **Critical State Bug**: State 4 now correctly interpreted as ON
- **PVSURPLUS Control**: PVSURPLUS now recognized as valid switch function
- **Cover State Handling**: Improved string state handling for COVER_STATE

### Changed
- **STATE_MAP**: Now includes all states 0-6 for both int and string
- **State Priority**: Updated priority values for better UI sorting
- **Documentation**: Enhanced state constant documentation

---

## [0.1.0-5]

### Added
- **Services Module**: New dedicated `services.py` for all service definitions
- **Service Manager**: Centralized `VioletServiceManager` class
- **Service Handlers**: Professional `VioletServiceHandlers` class structure
- **Safety Locks**: Dosing safety interval management system

### Changed
- **Service Organization**: All services moved from `__init__.py` to `services.py`
- **Service Registration**: Unified `async_register_services()` function
- **Code Structure**: Better separation of concerns (550+ lines reorganized)

### Improved
- **Maintainability**: Services now in dedicated module
- **Testability**: Isolated service logic easier to test
- **Scalability**: New services easier to add

### Technical
- Service schemas now in centralized `get_service_schemas()` function
- Handler methods grouped by functionality
- Consistent error handling across all services

---

## [0.1.0.4]

### Critical Bugfixes
- **Auth-Handling**: Fixed authentication when no username provided (device.py)
- **Password Handling**: Simplified password None-handling in API (api.py)
- **Boolean Detection**: Improved boolean value detection for sensors (sensor.py)
- **ADC3/IMP2 Mapping**: Made flow rate mapping more transparent, keeps original values
- **Switch Logging**: Reduced excessive INFO logging to DEBUG level

### UI/UX Improvements
- **Disclaimer**: Moderated safety notice, less intimidating for users
- Improved error messages and user guidance

### Documentation
- Added comprehensive CHANGELOG
- Improved code comments and documentation

### Validation
- All 9 critical issues from code analysis resolved
- No breaking changes for existing installations

---

## [0.1.0.3] - 2024-12-19

### Added
- Initial comprehensive
