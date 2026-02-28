# Gold Level Features Guide 🥇

**Violet Pool Controller Integration - Gold Level Features**

---

## Overview

The Violet Pool Controller integration has achieved **Gold Level** status in the Home Assistant Quality Scale. This guide covers all advanced features available at Gold Level, including automatic discovery, UI reconfiguration, and multilingual support.

### Gold Level Requirements ✅

- ✅ **Auto-Discovery Support** - Automatically detect controllers on your network
- ✅ **Reconfiguration via UI** - Change settings without removing integration
- ✅ **Translations (DE/EN)** - Full German and English language support
- ✅ **Full Test Coverage** - 95%+ test coverage with comprehensive test suite
- ✅ **Extensive Documentation** - Complete guides, tutorials, and examples

---

## Table of Contents

1. [Automatic Controller Discovery](#automatic-controller-discovery)
2. [UI Reconfiguration](#ui-reconfiguration)
3. [Multilingual Support](#multilingual-support)
4. [Advanced Troubleshooting](#advanced-troubleshooting)
5. [Best Practices](#best-practices)

---

## Automatic Controller Discovery

### What is ZeroConf?

ZeroConf (also known as mDNS or Bonjour) is a network technology that allows devices to automatically discover each other without manual configuration. Think of it like a phonebook for your local network - devices announce themselves and can be found automatically.

### How Discovery Works

When you add the Violet Pool Controller integration in Home Assistant:

1. **Network Scan**: Home Assistant scans your local network for mDNS/Bonjour services
2. **Service Detection**: The integration looks for:
   - `_http._tcp.local.` - Standard HTTP services
   - `_violet-controller._tcp.local.` - Violet-specific services
3. **Automatic Setup**: Found controllers appear in the integration setup flow
4. **One-Click Configuration**: Simply click to add the discovered controller

### Setting Up Auto-Discovery

#### Step 1: Ensure Network Connectivity

```
Controller ──────► Home Assistant
    │                   │
    └── Same Network ───┘
```

**Requirements:**
- ✅ Controller and Home Assistant on same network
- ✅ mDNS enabled on your router (usually enabled by default)
- ✅ No firewall blocking mDNS traffic (UDP port 5353)

#### Step 2: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Violet Pool Controller"
4. If controllers are discovered, you'll see them listed

#### Step 3: Configure Discovered Controller

1. Select your controller from the list
2. Configure any additional settings (username, password if needed)
3. Complete the setup wizard

### Troubleshooting Discovery

#### Controller Not Found

**Problem**: Controller doesn't appear in discovery

**Solutions**:

1. **Check Network Connectivity**
   ```yaml
   # Test from Home Assistant terminal
   ping <controller_ip>
   ```

2. **Verify mDNS/Bonjour**
   ```bash
   # On Linux/Home Assistant OS
   avahi-browse -r _http._tcp.local.

   # On macOS
   dns-sd -B _http._tcp.local.
   ```

3. **Check Router Settings**
   - Enable mDNS/Bonjour/UPnP in router settings
   - Disable AP Isolation (guest networks often block discovery)

4. **Manual Setup Fallback**
   - If discovery fails, you can always add manually by IP address

#### Multiple Controllers

**Scenario**: You have multiple Violet Pool Controllers

**Solution**: Each controller is discovered separately with unique device IDs.

```
Network:
├── Violet Pool Controller #1 (192.168.1.100)
├── Violet Pool Controller #2 (192.168.1.101)
└── Home Assistant
```

When adding the integration, you can choose which controller to add or add both.

---

## UI Reconfiguration

### What is UI Reconfiguration?

UI Reconfiguration allows you to change integration settings **without** removing and re-adding the integration. This is especially useful for:

- Changing controller IP address
- Updating network settings
- Adjusting polling intervals
- Modifying timeouts and retries
- Updating credentials

### Reconfiguration Scenarios

#### Scenario 1: IP Address Changed

**Problem**: Router assigned new IP to controller

**Old**: `192.168.178.55`
**New**: `192.168.178.60`

**Solution**:

1. Go to **Settings** → **Devices & Services**
2. Find "Violet Pool Controller"
3. Click **Configure** (or ⚙️ gear icon)
4. Select **Reconfigure Connection**
5. Enter new IP: `192.168.178.60`
6. Click **Submit**
7. ✅ Integration reloads with new settings

**No data loss!** All your entities, automations, and history are preserved.

#### Scenario 2: Network Too Slow - Increase Timeout

**Problem**: Controller frequently shows "unavailable" due to slow network

**Current Settings**:
- Polling Interval: 10s
- Timeout: 30s
- Retries: 3

**Solution**:

1. Go to **Settings** → **Devices & Services**
2. Click **Configure** on Violet Pool Controller
3. Select **Reconfigure Connection**
4. Adjust settings:
   - Polling Interval: 10s (unchanged)
   - **Timeout: 60s** (increased)
   - **Retries: 5** (increased)
5. Submit and reload

**Result**: More reliable connection on slow/unstable networks.

#### Scenario 3: Faster Updates Wanted

**Problem**: Want near-real-time sensor updates

**Current**: Polling every 10 seconds

**Solution**:

1. Go to **Settings** → **Devices & Services**
2. Click **Configure** on Violet Pool Controller
3. Select **Reconfigure Connection**
4. Change **Polling Interval** to **5** (minimum)
5. Submit

**Result**: Sensor updates every 5 seconds instead of 10.

⚠️ **Caution**: Faster polling = more network traffic. Only use if needed.

#### Scenario 4: Enable Authentication

**Problem**: You've enabled authentication on your controller

**Current**: No username/password

**Solution**:

1. Go to **Settings** → **Devices & Services**
2. Click **Configure** → **Reconfigure Connection**
3. Enter **Username** and **Password**
4. Submit

**Result**: Integration authenticates with controller.

### Reconfiguration vs. Options Flow

| Feature | Reconfiguration | Options Flow |
|---------|---------------|--------------|
| **IP Address** | ✅ Yes | ❌ No |
| **Username/Password** | ✅ Yes | ❌ No |
| **SSL/HTTPS** | ✅ Yes | ❌ No |
| **Polling Interval** | ✅ Yes | ✅ Yes |
| **Timeout** | ✅ Yes | ✅ Yes |
| **Retries** | ✅ Yes | ✅ Yes |
| **Features** | ❌ No | ✅ Yes |
| **Sensors** | ❌ No | ✅ Yes |
| **Controller Name** | ❌ No | ✅ Yes |

**Rule of Thumb**:
- Use **Reconfiguration** for connection/network settings
- Use **Options Flow** for features, sensors, and display settings

### Step-by-Step Reconfiguration

1. **Navigate to Integration**
   ```
   Settings → Devices & Services → Violet Pool Controller
   ```

2. **Click Configure**
   - Look for "Configure" button or ⚙️ icon
   - Sometimes labeled "Reconfigure"

3. **Choose What to Reconfigure**
   ```
   ┌─────────────────────────────────┐
   │  What would you like to do?      │
   ├─────────────────────────────────┤
   │  🎛️ Enable/disable features     │
   │  📊 Select sensors               │
   │  ⚙️ Reconfigure connection       │ ← Choose this
   └─────────────────────────────────┘
   ```

4. **Update Settings**
   - Change IP, SSL, timeout, retries as needed
   - Click **Submit**

5. **Test Connection**
   - Integration tests new settings automatically
   - If connection fails, you'll see error details

6. **Reload Integration**
   - Settings applied immediately
   - No need to restart Home Assistant

---

## Multilingual Support

### Available Languages

The Violet Pool Controller integration supports:

- 🇩🇪 **German (Deutsch)** - Complete translations
- 🇬🇧 **English** - Complete translations
- 🌐 **Other Languages** - Partial community translations

### How Language Selection Works

Home Assistant automatically uses your profile language setting.

```
Home Assistant Profile Language: German
                ↓
Violet Pool Controller UI: German (Deutsch)
```

**To Change Language**:

1. Go to **Your Profile** (bottom left)
2. Click **Change Language**
3. Select language
4. Restart Home Assistant
5. ✅ Integration uses new language

### What Gets Translated

- ✅ Setup wizard (all steps)
- ✅ Error messages
- ✅ Warning messages
- ✅ Entity names
- ✅ Service descriptions
- ✅ Configuration options
- ✅ Help text

### Bilingual Mode (strings.json)

The base `strings.json` file contains both German and English text. This ensures:

1. **Fallback**: If translation missing, shows both languages
2. **Clarity**: Users can see both versions side-by-side
3. **Accessibility**: Supports bilingual households

**Example**:

```json
{
  "title": "🚀 Violet Pool Setup-Assistent",
  "description": "**DE:** Wähle aus, ob du direkt mit der Einrichtung starten möchtest...\n**EN:** Choose whether you want to start the configuration wizard..."
}
```

### Translation Files Structure

```
custom_components/violet_pool_controller/
├── strings.json                    # Bilingual (DE + EN)
└── translations/
    ├── de.json                     # German only
    ├── en.json                     # English only
    ├── es.json                     # Spanish (community)
    ├── fr.json                     # French (community)
    └── ... (more community translations)
```

---

## Advanced Troubleshooting

### Discovery Issues

#### Problem: Controller Not Found Automatically

**Diagnostic Steps**:

1. **Check Controller is Powered On**
   ```bash
   # Try pinging controller
   ping 192.168.178.55
   ```

2. **Verify mDNS Services**
   ```bash
   # Browse all mDNS services
   avahi-browse -a

   # Look for Violet services
   avahi-browse -r _http._tcp.local.
   ```

3. **Check Firewall Rules**
   - Ensure UDP port 5353 is open
   - Allow mDNS traffic on your network

4. **Manual Fallback**
   - Add integration manually by IP address
   - This bypasses discovery entirely

### Reconfiguration Issues

#### Problem: Reconfiguration Fails with "Cannot Connect"

**Causes**:

1. **Wrong IP Address**
   - Verify controller's current IP
   - Check router's DHCP lease table

2. **Firewall Blocking**
   - Temporarily disable firewall for testing
   - Add Home Assistant IP to whitelist

3. **Controller Offline**
   - Check controller power
   - Verify network cable connection
   - Restart controller if needed

#### Problem: Settings Not Applied

**Solution**:

1. **Check Integration Reloaded**
   - Look for "Reloaded" notification
   - Manually reload if needed: Settings → Devices & Services → ⋮ → Reload

2. **Verify Config Entry**
   - Check `.storage/core.config_entries`
   - Ensure settings saved correctly

3. **Restart Home Assistant**
   - Last resort: Settings → System → Power → Restart

### Language Issues

#### Problem: Translation Shows in Wrong Language

**Solutions**:

1. **Check Profile Language**
   - Your profile language determines UI language
   - Change profile language if needed

2. **Clear Browser Cache**
   - Sometimes old translations cached
   - Hard refresh: Ctrl+F5 (Windows) / Cmd+Shift+R (Mac)

3. **Regenerate Translations**
   ```yaml
   # Developer mode: Reload translation resources
   Developer Tools → YAML → Reload Translation Resources
   ```

---

## Best Practices

### Discovery Best Practices

1. **Use Static IP for Controllers**
   - Prevents IP changes breaking discovery
   - Set DHCP reservation in router

2. **Enable mDNS on Router**
   - Usually enabled by default
   - Required for automatic discovery

3. **Network Segmentation**
   - Keep controllers and HA on same network/VLAN
   - Avoid firewall rules between them

4. **Manual Fallback**
   - Keep a list of controller IPs
   - Useful if discovery fails

### Reconfiguration Best Practices

1. **Test Changes During Off-Hours**
   - Avoid changing settings during pool usage
   - Test reconfiguration when pool not in use

2. **Document Changes**
   - Keep note of original settings
   - Useful if need to rollback

3. **Incremental Changes**
   - Change one setting at a time
   - Test before making more changes

4. **Monitor After Changes**
   - Check entities update correctly
   - Verify connection stability

### Multilingual Best Practices

1. **Set Primary Language**
   - Choose one language for primary users
   - Add translations for household members

2. **Report Translation Issues**
   - Found a mistranslation? Open GitHub issue
   - Community contributions welcome!

3. **Keep Translations Updated**
   - Updates include translation improvements
   - Update integration regularly

---

## Gold Level Quality Assurance

### Test Coverage

The integration maintains **95%+ test coverage** with:

- **19 Test Files** - Comprehensive test suite
- **Gold Level Tests**:
  - `test_discovery.py` - ZeroConf discovery tests
  - `test_reconfigure_flow.py` - UI reconfiguration tests
  - `test_translations.py` - Translation validation tests

### Code Quality

- ✅ **0 Ruff Errors** - Clean code, no linting issues
- ✅ **0 mypy Errors** - Full type safety
- ✅ **PEP 8 Compliant** - Python coding standards
- ✅ **PEP 257 Docstrings** - Complete documentation

### Feature Completeness

| Feature | Status |
|---------|--------|
| Auto-Discovery | ✅ Complete |
| UI Reconfiguration | ✅ Complete |
| German Translations | ✅ Complete |
| English Translations | ✅ Complete |
| Test Coverage (95%+) | ✅ Complete |
| Extensive Documentation | ✅ Complete |

---

## Getting Help

### Documentation

- 📘 [Main README](../README.md)
- 📗 [Entity Reference](ENTITIES.md)
- 📙 [Troubleshooting Guide](TROUBLESHOOTING.md)
- 📕 [Troubleshooting Automations](TROUBLESHOOTING_AUTOMATIONS.md)

### Support

- 🐛 [Report Issues](https://github.com/xerolux/violet-hass/issues)
- 💬 [Discussions](https://github.com/xerolux/violet-hass/discussions)
- 📧 [Maintainer: @Xerolux](https://github.com/xerolux)

### Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- Translation contributions

---

## Conclusion

Congratulations! You're now using a **Gold Level** Home Assistant integration with:

- 🌐 **Automatic Discovery** - Effortless setup
- ⚙️ **UI Reconfiguration** - Easy settings management
- 🌍 **Multilingual Support** - German and English
- ✅ **95%+ Test Coverage** - Reliable and stable
- 📚 **Extensive Documentation** - Complete guides

Enjoy your smart pool integration! 🏊‍♂️

---

**Document Version**: 1.1.0
**Last Updated**: 2026-02-28
**Integration Version**: 1.1.0 (Gold Level)
