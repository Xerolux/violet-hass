# Changelog - Violet Pool Controller

## [0.1.0.4] - 2024-12-20

### ?? Critical Bugfixes
- **Auth-Handling**: Fixed authentication when no username provided (device.py)
- **Password Handling**: Simplified password None-handling in API (api.py)
- **Boolean Detection**: Improved boolean value detection for sensors (sensor.py)
- **ADC3/IMP2 Mapping**: Made flow rate mapping more transparent, keeps original values
- **Switch Logging**: Reduced excessive INFO logging to DEBUG level

### ?? UI/UX Improvements
- **Disclaimer**: Moderated safety notice, less intimidating for users
- Improved error messages and user guidance

### ?? Documentation
- Added comprehensive CHANGELOG
- Improved code comments and documentation

### ? Validation
- All 9 critical issues from code analysis resolved
- No breaking changes for existing installations

## [0.1.0.3] - Previous Release
- Initial comprehensive implementation
- 3-State support for switches
- Extended sensor coverage (147 API parameters)
- DMX scene control (12 scenes)
