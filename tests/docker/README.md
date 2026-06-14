# Docker Test Environment

This directory contains everything needed to test the violet-hass addon in a Docker container with a live pool controller.

## 📁 Files

### Documentation
- **DOCKER_TEST_GUIDE.md** - Complete guide for Docker testing
- **TEST_RESULTS_2026-02-23.md** - Results from the latest test run
- **README.md** - This file

### Configuration
- **test_credentials.example.txt** - Template for credentials (safe to commit)
- **test_credentials.txt** - Optional local credentials file (gitignored)
- **docker-compose.yml** - Docker Compose configuration (in project root)

### Scripts
- **run_docker_test.sh** - Automated test script

## 🚀 Quick Start

### 1. Setup Credentials

```bash
# Copy the example file to a local-only file outside the repository
cp test_credentials.example.txt %USERPROFILE%\\violet-test-credentials.local.txt

# Edit with your real credentials
nano %USERPROFILE%\\violet-test-credentials.local.txt
```

If you prefer to keep a local file in this folder for convenience, use
`test_credentials.txt` or `*.local.txt`. Both are gitignored and should never
contain credentials you are not willing to rotate.

### 2. Run Tests

```bash
# Option A: Run all tests
./run_docker_test.sh all

# Option B: Run smoke tests only
./run_docker_test.sh smoke

# Option C: Run API tests only
./run_docker_test.sh api

# Option D: Test pump control specifically
./run_docker_test.sh pump

# Option E: Show logs
./run_docker_test.sh logs

# Option F: Show status
./run_docker_test.sh status
```

## 📊 Test Results

Latest test: **2026-02-23**

Status: ✅ **ALL TESTS PASSED**

Key metrics:
- HA Boot time: 2.76s
- API fetch time: 0.255s
- All entities created
- Pump control working
- State sync working

See **TEST_RESULTS_2026-02-23.md** for detailed results.

## 🔒 Security & .gitignore

The following files are **NOT** in git (see .gitignore):

```
tests/docker/test_credentials.txt      # Contains real passwords
tests/docker/test_results/             # Test run results
tests/docker/screenshots/              # Screenshots from tests
tests/docker/logs/                     # Detailed logs
config/.storage/                       # HA config with credentials
config/home-assistant.log*             # HA logs
```

**⚠️ IMPORTANT:** Prefer storing live credentials outside the repository. If you
use `test_credentials.txt`, keep it local-only and rotate credentials if it was
ever exposed.

## 📝 Test Checklist

Before running tests:
- [ ] Docker is running
- [ ] Controller is powered on and reachable
- [ ] Local credentials exist outside the repo or in a gitignored local file
- [ ] No firewall blocking port 8123

After running tests:
- [ ] All tests passed
- [ ] Pump is turned off (if testing pump control)
- [ ] Results documented in TEST_RESULTS_YYYY-MM-DD.md
- [ ] Any issues logged

## 🐛 Troubleshooting

### Container won't start

```bash
# Clean up and restart
docker compose down
docker rm -f homeassistant-dev
docker compose up -d
```

### Can't connect to controller

```bash
# Test connection manually
curl -u "user:pass" "http://192.168.178.55/getReadings?ALL"

# Check network
ping 192.168.178.55
```

### Integration not loading

1. Check config entry in `config/.storage/core.config_entries`
2. Make sure key is `host` not `api_url`
3. Restart container: `docker compose restart`

## 📖 Further Reading

- **DOCKER_TEST_GUIDE.md** - Comprehensive testing guide
- **../README.md** - Project root README
- **../../docs/** - Additional documentation

## 🔄 Test Workflow

1. **Setup:** Create/update `test_credentials.txt`
2. **Start:** Run `./run_docker_test.sh start` or `docker compose up -d`
3. **Test:** Run `./run_docker_test.sh all`
4. **Verify:** Check results and logs
5. **Document:** Update TEST_RESULTS_YYYY-MM-DD.md
6. **Cleanup:** Turn off pump, stop container if needed

---

*Last updated: 2026-02-23*
*Status: Production Ready ✅*
