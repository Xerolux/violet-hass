# Security Policy

## Supported Versions

Only the latest release receives security updates and patches.

| Version | Supported |
|---------|-----------|
| 1.x.x (latest) | ✅ Yes |
| < 1.0.0 | ❌ No |

Always upgrade to the latest release to receive security fixes.

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities via public GitHub Issues.**

If you discover a security vulnerability, please report it responsibly:

1. **Preferred:** Use [GitHub Private Security Advisories](https://github.com/Xerolux/violet-hass/security/advisories/new) — this keeps details private until a fix is released.
2. **Alternative:** Email [git@xerolux.de](mailto:git@xerolux.de) with subject `[SECURITY] violet-hass vulnerability`.

### What to include

- Description of the vulnerability and its impact
- Steps to reproduce the issue
- Affected versions
- Any suggested fix (optional)

### Response timeline

| Step | Timeframe |
|------|-----------|
| Initial acknowledgement | Within 48 hours |
| Triage & assessment | Within 7 days |
| Fix & release (if confirmed) | Within 30 days |
| Public disclosure | After fix is released |

Please allow time to fix the issue before any public disclosure to protect users.

## Security Design

This integration is designed with security in mind:

- **Local-only communication** — no cloud services or third-party APIs
- **Input sanitization** — all user inputs and API parameters are validated
- **SSL/TLS verification** — certificate verification is enabled by default
- **Rate limiting** — token bucket algorithm prevents controller overload
- **No hardcoded credentials** — all secrets are stored in Home Assistant's secure configuration store

## Scope

This security policy covers the `violet_pool_controller` Home Assistant integration. It does **not** cover the Violet Pool Controller hardware or the PoolDigital API — report those issues directly to [PoolDigital GmbH & Co. KG](https://www.pooldigital.de/).
