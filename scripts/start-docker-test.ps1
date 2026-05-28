#!/usr/bin/env pwsh
#requires -Version 7
<#
.SYNOPSIS
    One-command Docker test environment for Violet Pool Controller
.DESCRIPTION
    Sets up a complete Home Assistant test instance with the integration
    pre-configured. Edit config/test_secrets.ps1 with your controller details.
.EXAMPLE
    ./scripts/start-docker-test.ps1
    ./scripts/start-docker-test.ps1 -SkipSetup   # Just start existing container
    ./scripts/start-docker-test.ps1 -Clean        # Full reset
#>

param(
    [switch]$Clean,
    [switch]$SkipSetup,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

$ConfigDir = Join-Path $ProjectRoot "config"
$SecretsFile = Join-Path $ConfigDir "test_secrets.ps1"

# --- Color helpers ---
function Write-Step($msg) { Write-Host "`n[STEP] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "  [ERR] $msg" -ForegroundColor Red }

# --- Load secrets ---
$DefaultSecrets = @{
    ControllerHost = "192.168.178.55"
    ControllerPort = 80
    ControllerUser = "Basti"
    ControllerPass = "sebi2634"
    UseSSL = $false
    DeviceId = 1
    PollingInterval = 10
    DeviceName = "Violet Pool Controller"
}

if (Test-Path $SecretsFile) {
    . $SecretsFile
    Write-Ok "Loaded secrets from config/test_secrets.ps1"
} else {
    Write-Warn "No test_secrets.ps1 found, using defaults"
    Write-Warn "Create config/test_secrets.ps1 to customize (see config/test_secrets.example.ps1)"
    $ControllerHost = $DefaultSecrets.ControllerHost
    $ControllerPort = $DefaultSecrets.ControllerPort
    $ControllerUser = $DefaultSecrets.ControllerUser
    $ControllerPass = $DefaultSecrets.ControllerPass
    $UseSSL = $DefaultSecrets.UseSSL
    $DeviceId = $DefaultSecrets.DeviceId
    $PollingInterval = $DefaultSecrets.PollingInterval
    $DeviceName = $DefaultSecrets.DeviceName
}

# --- Step 1: Clean if requested ---
if ($Clean) {
    Write-Step "Cleaning existing container and config..."
    docker rm -f homeassistant-dev 2>$null
    if (Test-Path $ConfigDir) {
        Remove-Item -Recurse -Force (Join-Path $ConfigDir ".storage") -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force (Join-Path $ConfigDir "deps") -ErrorAction SilentlyContinue
        Remove-Item -Force (Join-Path $ConfigDir "home-assistant.log*") -ErrorAction SilentlyContinue
        Remove-Item -Force (Join-Path $ConfigDir ".HA_VERSION") -ErrorAction SilentlyContinue
        Remove-Item -Force (Join-Path $ConfigDir ".uuid") -ErrorAction SilentlyContinue
        Remove-Item -Force (Join-Path $ConfigDir "*.db*") -ErrorAction SilentlyContinue
    }
    Write-Ok "Cleaned"
}

# --- Step 2: Ensure config directory structure ---
Write-Step "Setting up config directory..."
$dirs = @(
    $ConfigDir
    (Join-Path $ConfigDir "custom_components")
    (Join-Path $ConfigDir "blueprints")
    (Join-Path $ConfigDir "blueprints\automation")
    (Join-Path $ConfigDir "tts")
    (Join-Path $ConfigDir ".storage")
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Symlink integration if not already linked
$integrationSrc = Join-Path $ProjectRoot "custom_components\violet_pool_controller"
$integrationDst = Join-Path $ConfigDir "custom_components\violet_pool_controller"
if (-not (Test-Path $integrationDst)) {
    # On Windows, create a junction (directory symlink)
    cmd /c mklink /J "$integrationDst" "$integrationSrc" | Out-Null
    Write-Ok "Linked integration to config/custom_components/"
} else {
    Write-Ok "Integration already linked"
}

# --- Step 3: Write configuration.yaml ---
$ConfigYaml = @"
homeassistant:
  name: Home
  latitude: 52.520008
  longitude: 13.404954
  elevation: 34
  unit_system: metric
  time_zone: Europe/Berlin
  country: DE
  language: de

logger:
  default: info
  logs:
    custom_components.violet_pool_controller: debug
    homeassistant.components.config_flow: debug

config:
http:
  server_port: 8123
  cors_allowed_origins:
    - http://localhost:8123
frontend:
mobile_app:
person:
sun:
automation:
script:
"@

Set-Content -Path (Join-Path $ConfigDir "configuration.yaml") -Value $ConfigYaml -Encoding UTF8
Write-Ok "Written configuration.yaml"

# --- Step 4: Bootstrap - only create onboarding marker for fresh install ---
$onboardingFile = Join-Path $ConfigDir ".storage\onboarding"
$storageDir = Join-Path $ConfigDir ".storage"

if (-not (Test-Path $storageDir)) {
    New-Item -ItemType Directory -Path $storageDir -Force | Out-Null
}

# We DON'T pre-create auth - HA creates its own on first boot.
# Instead we use the onboarding API after HA starts.
if (Test-Path (Join-Path $ConfigDir ".HA_VERSION")) {
    Write-Ok "HA instance already initialized"
} else {
    Write-Ok "Fresh install - will complete onboarding via API after HA starts"
}

# --- Step 5: Pull latest image and start container ---
Write-Step "Starting Home Assistant container..."
docker compose up -d 2>&1 | ForEach-Object { Write-Host "  $_" }

# --- Step 6: Wait for HA to be ready ---
Write-Step "Waiting for Home Assistant to start (max 90s)..."
$ready = $false
for ($i = 0; $i -lt 18; $i++) {
    Start-Sleep -Seconds 5
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8123/api/" -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200 -or $r.StatusCode -eq 401) {
            $ready = $true
            break
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            $ready = $true
            break
        }
    }
    Write-Host "  Waiting... ($($i*5)s)"
}

if (-not $ready) {
    Write-Err "Home Assistant did not start within 90s. Check: docker logs homeassistant-dev"
    exit 1
}
Write-Ok "Home Assistant is running"

# --- Step 7: Install dependencies ---
Write-Step "Installing integration dependencies..."
$apiPkg = "violet-poolController-api"
$manifestFile = Join-Path $ProjectRoot "custom_components\violet_pool_controller\manifest.json"
$manifest = Get-Content $manifestFile -Raw | ConvertFrom-Json
$apiVersion = ($manifest.requirements | Where-Object { $_ -match $apiPkg }) -replace ".*==", ""

docker exec homeassistant-dev pip install -q "$apiPkg==$apiVersion" 2>&1 | Select-Object -Last 2
Write-Ok "Installed $apiPkg==$apiVersion"

# Restart to pick up new packages
docker restart homeassistant-dev | Out-Null
Start-Sleep -Seconds 15
Write-Ok "Container restarted"

# --- Step 8: Complete onboarding and get auth token ---
Write-Step "Setting up authentication..."

$token = $null

# Check if HA needs onboarding
try {
    $checkResp = Invoke-WebRequest -Uri "http://localhost:8123/api/onboarding" -UseBasicParsing -ErrorAction Stop
    $needsOnboarding = ($checkResp.Content | ConvertFrom-Json).done -eq $false
} catch {
    $needsOnboarding = $false
}

if ($needsOnboarding) {
    Write-Ok "Completing HA onboarding..."
    $client_id = "http://localhost:8123"

    # Step 1: Create user
    $body = @{
        client_id = $client_id
        username = "test"
        password = "testtest"
        name = "Test User"
        language = "en"
    } | ConvertTo-Json
    $r = Invoke-RestMethod -Uri "http://localhost:8123/api/onboarding/users" -Method Post -Body $body -ContentType "application/json"
    $authCode = $r.auth_code
    Write-Ok "User created"

    # Step 2: Exchange auth code for token
    $body = "grant_type=authorization_code&code=$authCode&client_id=$client_id"
    $r = Invoke-RestMethod -Uri "http://localhost:8123/auth/token" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
    $token = $r.access_token
    Write-Ok "Got access token"
} else {
    Write-Ok "HA already onboarded, logging in..."
}

# If we still need a token, try login
if (-not $token) {
    # Try JWT from storage
    $jwtScript = @'
import json, hashlib, hmac, time, base64
try:
    with open("/config/.storage/auth") as f:
        d = json.load(f)
    tokens = d["data"]["refresh_tokens"]
    for t in tokens:
        if t["token_type"] == "normal":
            jwt_key = t["jwt_key"]
            header = base64.urlsafe_b64encode(json.dumps({"alg":"HS256","typ":"JWT"}).encode()).decode().rstrip("=")
            payload_data = {"iss":t["id"],"iat":int(time.time()),"exp":int(time.time())+86400*30}
            payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
            sig = hmac.new(jwt_key.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
            sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
            print(f"{header}.{payload}.{sig_b64}")
except Exception:
    pass
'@
    $token = docker exec homeassistant-dev python3 -c $jwtScript 2>$null
}

if (-not $token) {
    Write-Err "Failed to generate token."
    Write-Warn "Open http://localhost:8123 in browser (user=test, pass=testtest), then re-run with -SkipSetup"
    exit 1
}
Write-Ok "Authenticated"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# --- Step 9: Add Violet Pool Controller config entry ---
if ($SkipSetup) {
    Write-Step "Skipping integration setup (--SkipSetup)"
} else {
    Write-Step "Setting up Violet Pool Controller integration..."

    # Check if already configured
    try {
        $existing = Invoke-RestMethod -Uri "http://localhost:8123/api/config/config_entries/entry" -Headers $headers
        $violetEntry = $existing | Where-Object { $_.domain -eq "violet_pool_controller" }
        if ($violetEntry) {
            Write-Ok "Integration already configured (entry_id=$($violetEntry.entry_id))"
        } else {
            # Flow step 1: Initiate
            $body = @{ client_id = "docker-test"; handler = "violet_pool_controller"; show_advanced_options = $false } | ConvertTo-Json
            $r = Invoke-RestMethod -Uri "http://localhost:8123/api/config/config_entries/flow" -Headers $headers -Method Post -Body $body
            $flowId = $r.flow_id
            Write-Ok "Flow initiated: $flowId"

            # Flow step 2: Start setup
            $body = @{ action = "start_setup" } | ConvertTo-Json
            $r = Invoke-RestMethod -Uri "http://localhost:8123/api/config/config_entries/flow/$flowId" -Headers $headers -Method Post -Body $body
            Write-Ok "Setup started"

            # Flow step 3: Accept disclaimer
            $body = @{ agreement = $true } | ConvertTo-Json
            $r = Invoke-RestMethod -Uri "http://localhost:8123/api/config/config_entries/flow/$flowId" -Headers $headers -Method Post -Body $body
            Write-Ok "Disclaimer accepted"

            # Flow step 4: Connection settings
            $body = @{
                host = $ControllerHost
                port = $ControllerPort
                username = $ControllerUser
                password = $ControllerPass
                use_ssl = $UseSSL
                verify_ssl = $true
                device_id = $DeviceId
                polling_interval = $PollingInterval
                timeout_duration = 10
                retry_attempts = 3
                device_name = $DeviceName
                controller_name = $DeviceName
            } | ConvertTo-Json
            $r = Invoke-RestMethod -Uri "http://localhost:8123/api/config/config_entries/flow/$flowId" -Headers $headers -Method Post -Body $body
            Write-Ok "Connection configured (host=$ControllerHost)"

            # Flow step 5: Pool setup (defaults)
            $body = @{ pool_size = 50; pool_type = "outdoor"; disinfection_method = "chlorine" } | ConvertTo-Json
            $r = Invoke-RestMethod -Uri "http://localhost:8123/api/config/config_entries/flow/$flowId" -Headers $headers -Method Post -Body $body
            Write-Ok "Pool configured"

            # Flow step 6: Feature selection (all major features)
            $body = @{
                enable_heating = $true
                enable_solar = $true
                enable_ph_control = $true
                enable_chlorine_control = $true
                enable_flocculation = $true
                enable_cover_control = $true
                enable_backwash = $true
                enable_pv_surplus = $true
                enable_filter_control = $true
                enable_led_lighting = $true
            } | ConvertTo-Json
            $r = Invoke-RestMethod -Uri "http://localhost:8123/api/config/config_entries/flow/$flowId" -Headers $headers -Method Post -Body $body
            Write-Ok "Features selected"

            # Flow step 7: Sensor selection (accept defaults = empty body)
            $body = "{}"
            $r = Invoke-RestMethod -Uri "http://localhost:8123/api/config/config_entries/flow/$flowId" -Headers $headers -Method Post -Body $body

            if ($r.type -eq "create_entry") {
                Write-Ok "Integration configured! entry_id=$($r.result.entry_id)"
            } else {
                Write-Warn "Unexpected flow state: $($r.type) step=$($r.step_id)"
            }
        }
    } catch {
        Write-Err "Failed to configure integration: $_"
        Write-Warn "You may need to set it up manually via http://localhost:8123"
    }
}

# --- Step 10: Check for errors ---
Write-Step "Checking for errors in logs..."
Start-Sleep -Seconds 5
$errors = docker logs homeassistant-dev --tail 200 2>&1 | Select-String -Pattern "ERROR|Traceback|TypeError|AttributeError" -CaseSensitive:$false
if ($errors) {
    Write-Warn "Found errors:"
    $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
} else {
    Write-Ok "No errors found in logs"
}

# --- Done ---
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  Docker Test Environment Ready!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "  HA URL:     http://localhost:8123" -ForegroundColor White
Write-Host "  Token:      $token" -ForegroundColor Gray
Write-Host ""
Write-Host "  Useful commands:" -ForegroundColor White
Write-Host "    docker logs homeassistant-dev --tail 50 -f     # Follow logs"
Write-Host "    docker logs homeassistant-dev 2>&1 | Select-String 'violet|ERROR'"
Write-Host "    docker compose down                            # Stop"
Write-Host "    ./scripts/start-docker-test.ps1 -Clean         # Full reset"
Write-Host ""

# Save token for other scripts
$token | Set-Content (Join-Path $ConfigDir ".test_token") -Force
