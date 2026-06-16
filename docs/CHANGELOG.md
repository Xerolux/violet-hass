# Changelog

All notable changes to the Violet Pool Controller Home Assistant integration are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.0.0] – 2026-06-16

### ✨ New Features

- **Security-First Architecture**: Passive-first, read-only security model with no state assumption on startup
- **Advanced Error Management**: Reset blocking errors button for direct error code management
- **Multi-State Switch Support**: Full support for device states 0-6 with operational mode indicators
- **Firmware Update Detection**: Real-time firmware version checking and update notifications
- **Enhanced Diagnostics Services**: New diagnostic services for connection testing and error analysis
- **DMX Scene Control**: 12 DMX scene selection and control
- **Pool Light Color Control**: Advanced light color pulse management
- **Digital Rule Management**: Configure automation rules based on digital input signals
- **Service Framework**: Comprehensive service system with validation schemas
- **Entity ID Migration**: Automatic migration of legacy entity IDs with proper restoration

### 🚀 Improvements

- **Connection Recovery**: Exponential backoff recovery (10s-300s) with 10 max attempts
- **Rate Limiting**: Token bucket algorithm prevents API flooding
- **Thread Safety**: Documented lock ordering prevents deadlocks
- **Input Sanitization**: XSS, injection, and path-traversal protection
- **SSL/TLS Security**: Certificate verification enabled by default
- **Error Codes**: Comprehensive error code mappings with severity classification
- **Sensor Modularization**: Refactored sensor implementations (generic, monitoring, specialized)
- **Config Flow UX**: Enhanced validation, sensor discovery, and duplicate detection
- **Type Hints**: Full type annotation support with mypy validation
- **Translations**: Support for 10 languages (English, German, Spanish, French, Italian, Dutch, Polish, Portuguese, Russian, Chinese)

### 🔧 Bug Fixes

- Fixed duplicate entity ID prefix generation
- Resolved aiohttp dependency conflicts
- Corrected firmware protocol violations
- Fixed SSL default settings
- Corrected system sensor key name handling
- Fixed dosing response error handling
- Normalized boolean config values to integers (0/1)
- Resolved CodeQL warnings in security test suite

### 🔒 Security Enhancements

- Strict passive-first security model
- All inputs validated through InputSanitizer
- Rate-limited API access
- No state restoration on startup
- Only explicit user commands trigger state changes
- See SECURITY.md for full architecture documentation

### 📚 Documentation

- Added comprehensive SECURITY.md documentation
- Enhanced ARCHITECTURE.md with full component details
- Added CONTRIBUTING.md guidelines
- Improved developer documentation in CLAUDE.md
- Added security principles test suite

### 🧪 Testing

- Full test suite with 21+ test modules
- Thread-safety and async/await testing
- Security principles validation
- Offline scenario testing
- ZeroConf discovery testing
- Config flow and reconfiguration testing

---

## [2.0.0-beta.9] – 2026-06-09

### ✨ New Features

- H2O2 sensor support (hydrogen peroxide monitoring)
- Runtime statistics sensors
- RS485 power status monitoring
- Stopwatch functionality for pool operations
- Dosing statistics tracking

### 🔧 Bug Fixes

- Fixed firmware version detection for both old and new key names
- Corrected firmware update entity visibility
- Fixed firmware protocol API calls synchronization
- Resolved service translation synchronization
- Fixed duplicate device-prefix generation

---

## [2.0.0-beta.8] – 2026-05-28

### ✨ New Features

- 15 firmware-discovery improvements
- Enhanced controller initialization
- Improved error recovery mechanisms

### 🚀 Improvements

- Better mock server with real controller keys
- Enhanced version detection logic
- Improved mock server responses

---

## [2.0.0-beta.7] – 2026-05-20

### ✨ New Features

- Entity prefix migration for duplicate handling
- Firmware update entity detection
- New sensor types and categories

### 🔧 Bug Fixes

- Fixed entity ID migration system
- Resolved duplicate device-prefix issues
- Corrected system sensor initialization

---

## [2.0.0-beta.6] – 2026-05-15

### 🚀 Improvements

- Code quality improvements
- Enhanced error handling
- Better sensor organization

---

## [2.0.0-beta.5] – 2026-05-10

### 🚀 Improvements

- API package integration improvements
- Better sensor implementation structure
- Documentation updates

---

## [2.0.0-beta.1 through beta.4] – 2026-05-01 to 2026-05-08

### ✨ New Features

- Initial 2.0.0 beta release cycle
- Modular sensor system
- Enhanced config flow

### 🚀 Improvements

- Service system refactoring
- Error handler improvements
- Connection recovery enhancements

---

## [1.2.4] – 2026-04-15

### ✨ New Features

- Basic pool controller integration
- Sensor platform support
- Binary sensor support
- Switch platform support
- Climate platform support
- Cover platform support
- Service system foundation

### 🚀 Improvements

- Initial rate limiting implementation
- Basic error handling
- Configuration flow foundation
- ZeroConf discovery support

### 🔧 Bug Fixes

- Initial stability improvements

---

## [1.2.3] and Earlier

Earlier versions prior to 1.2.3 are not documented in this changelog.
For detailed history, see git commit log.

---

<!-- Link References for direct GitHub navigation -->
[2.0.0]: https://github.com/Xerolux/violet-hass/compare/v2.0.0-beta.9...v2.0.0
[2.0.0-beta.9]: https://github.com/Xerolux/violet-hass/compare/v2.0.0-beta.8...v2.0.0-beta.9
[2.0.0-beta.8]: https://github.com/Xerolux/violet-hass/compare/v2.0.0-beta.7...v2.0.0-beta.8
[2.0.0-beta.7]: https://github.com/Xerolux/violet-hass/compare/v2.0.0-beta.6...v2.0.0-beta.7
[2.0.0-beta.6]: https://github.com/Xerolux/violet-hass/compare/v2.0.0-beta.5...v2.0.0-beta.6
[2.0.0-beta.5]: https://github.com/Xerolux/violet-hass/compare/v2.0.0-beta.1...v2.0.0-beta.5
[2.0.0-beta.1 through beta.4]: https://github.com/Xerolux/violet-hass/compare/v1.2.4...v2.0.0-beta.1
[1.2.4]: https://github.com/Xerolux/violet-hass/compare/v1.2.3...v1.2.4
