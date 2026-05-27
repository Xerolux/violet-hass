> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Security.de)**

---

# Security & SSL – Integration Security

> Security architecture, SSL/TLS configuration, and best practices.

---

## Security Overview

The Violet Pool Controller integration was developed with multiple security layers:

```
┌─────────────────────────────────────────────┐
│           SECURITY LAYERS                   │
├─────────────────────────────────────────────┤
│  1. Input Sanitization (XSS, Injection)     │
│  2. SSL/TLS Certificate Verification        │
│  3. Token Bucket Rate Limiting              │
│  4. Thread-Safe Locking                     │
│  5. Auto-Recovery with Backoff              │
└─────────────────────────────────────────────┘
```

---

## SSL/TLS Configuration

### Default Setting: SSL Enabled

SSL certificate verification is **enabled by default** (`verify_ssl=True`).

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `use_ssl` | `False` | Use HTTPS instead of HTTP |
| `verify_ssl` | `True` | Verify certificate |

### When to Disable SSL?

Only when the controller uses a **self-signed certificate** and you are on a **trusted home network**:

```
Settings → Devices & Services → Violet Pool Controller
→ Configure → Verify SSL certificate: No
```

> **Warning:** Never disable SSL verification on public networks!

### SSL with Custom Certificate

For self-signed certificates in production environments:

1. Add the certificate to the Home Assistant CA store
2. Keep `verify_ssl: true`
3. Renew the certificate regularly

---

## Input Sanitization

All user inputs are validated through `InputSanitizer` before reaching the API.

### Protected Attack Vectors

| Attack | Protection |
|--------|------------|
| **XSS** (Cross-Site-Scripting) | HTML escaping of all inputs |
| **SQL Injection** | Pattern-based validation |
| **Command Injection** | Whitelist validation for commands |
| **Path Traversal** | Path normalization and validation |
| **Parameter Tampering** | Range checking for numeric values |

### Validated Value Ranges

| Parameter | Minimum | Maximum |
|-----------|---------|---------|
| pH value | 6.0 | 8.0 |
| ORP value | 200 mV | 900 mV |
| Temperature | 10°C | 40°C |
| Dosing duration | 5s | 300s |
| Pump speed | 0 | 3 |

---

## Rate Limiting

The token bucket algorithm protects the controller from overload:

```
Token Bucket:
├── Max tokens: configurable
├── Refill rate: constant
├── Priority queue: critical requests first
└── When bucket empty: request delayed
```

### Why Rate Limiting?

The Violet Pool Controller is an **embedded system** with limited CPU power. Too many simultaneous API requests can:
- Crash the controller
- Corrupt measurements
- Slow down control operations

### Recommended Polling Intervals

| Number of Controllers | Recommended Interval |
|-----------------------|----------------------|
| 1 | 15–20 seconds |
| 2–3 | 25–30 seconds |
| 4+ | 45–60 seconds |

---

## Thread Safety

The integration uses two documented locks with a fixed ordering:

```python
_api_lock:       Protects API calls and data updates
_recovery_lock:  Protects recovery state and attempts

Ordering: NEVER nested!
```

**Why is this important?** Home Assistant is multi-threaded. Without locks, simultaneous requests could lead to inconsistent states.

---

## Auto-Recovery & Backoff

On connection loss, the integration automatically attempts to re-establish the connection:

```
Attempt 1:  Immediately
Attempt 2:  Wait 10 seconds
Attempt 3:  Wait 20 seconds
Attempt 4:  Wait 40 seconds
...
Max wait time: 300 seconds (5 minutes)
Max attempts:  10

After 10 failed attempts: Manual intervention required
```

### Recovery After Maximum Failure

```
Settings → Devices & Services → Violet Pool Controller
→ Reload
```

Or in `configuration.yaml`:

```yaml
# Manually restart integration
homeassistant:
  customize:
    violet_pool_controller.*:
      assumed_state: false
```

---

## Network Security

### Recommended Network Configuration

```
┌─────────────────────────────────────────┐
│  Home Network (192.168.1.0/24)          │
│                                         │
│  Home Assistant  ←→  Violet Controller  │
│  (192.168.1.10)       (192.168.1.55)   │
│                                         │
│  Both in same VLAN (no internet)        │
└─────────────────────────────────────────┘
```

### Firewall Recommendations

```
# Recommended: Isolate controller from the internet
# Only Home Assistant should access the controller

iptables -A INPUT -s 192.168.1.10 -d 192.168.1.55 -j ACCEPT
iptables -A INPUT -d 192.168.1.55 -j DROP
```

### Port Requirements

| Port | Protocol | Usage |
|------|----------|-------|
| `80` | HTTP | Unencrypted API |
| `443` | HTTPS | Encrypted API (when SSL enabled) |

---

## Security Checklist

### Basic Configuration

- [ ] Controller has a static IP address
- [ ] Controller is not directly accessible from the internet
- [ ] Home Assistant is up to date
- [ ] Integration is on the latest version

### SSL/TLS

- [ ] SSL enabled when possible
- [ ] Certificate valid (not expired)
- [ ] `verify_ssl` only disabled for self-signed certificate on home network

### Credentials

- [ ] Controller password is strong and unique
- [ ] Credentials stored only in HA configuration (not in YAML files)

### Monitoring

- [ ] Automation for critical error codes
- [ ] Log level set to `warning` for production

---

## Reporting Security Vulnerabilities

If you discover a security vulnerability:

1. **Do not report publicly** (no GitHub issue)
2. **Email:** git@xerolux.de
3. **Description** of the vulnerability with proof of concept
4. **Expected behavior** vs. actual behavior

We respond within 48 hours and coordinate responsible disclosure.

---

## Logging & Privacy

The integration logs **no** sensitive data:
- No passwords in logs
- No complete API responses in debug mode
- No personal data

### Configure Log Level

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.violet_pool_controller: warning
    # For debugging:
    # custom_components.violet_pool_controller: debug
```

---

*Back: [Troubleshooting](Troubleshooting) | Next: [FAQ](FAQ)*