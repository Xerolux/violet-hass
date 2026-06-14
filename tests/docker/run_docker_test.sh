#!/bin/bash

# Docker Test Automation Script for violet-hass
# Usage: ./run_docker_test.sh [test_name]
#
# Examples:
#   ./run_docker_test.sh              # Run all tests
#   ./run_docker_test.sh pump         # Run pump tests only
#   ./run_docker_test.sh smoke        # Run smoke tests only

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CREDENTIALS_FILE="$SCRIPT_DIR/test_credentials.txt"

# Load credentials
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo -e "${RED}ERROR: Credentials file not found: $CREDENTIALS_FILE${NC}"
    echo "Please create test_credentials.txt from test_credentials.example.txt"
    exit 1
fi

source "$CREDENTIALS_FILE"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

# Change to project directory
cd "$PROJECT_ROOT"

# ============================================================================
# Test Functions
# ============================================================================

test_docker_running() {
    print_header "TEST 1: Check Docker"

    if ! docker ps > /dev/null 2>&1; then
        log_error "Docker is not running"
        return 1
    fi

    log_success "Docker is running"
}

test_container_exists() {
    print_header "TEST 2: Check Container"

    if docker ps -a | grep -q "homeassistant-dev"; then
        log_info "Container exists"

        # Check if running
        if docker ps | grep -q "homeassistant-dev"; then
            log_success "Container is running"
            return 0
        else
            log_warning "Container exists but is not running"
            return 1
        fi
    else
        log_warning "Container does not exist"
        return 1
    fi
}

start_container() {
    print_header "ACTION: Start Container"

    log_info "Starting Docker Compose..."
    docker compose up -d

    log_info "Waiting for Home Assistant to boot (30s)..."
    sleep 30

    if docker ps | grep -q "homeassistant-dev"; then
        log_success "Container started successfully"
        return 0
    else
        log_error "Container failed to start"
        return 1
    fi
}

test_ha_boot() {
    print_header "TEST 3: Check Home Assistant Boot"

    log_info "Checking logs for boot message..."

    if docker compose logs | grep -q "Home Assistant initialized"; then
        log_success "Home Assistant booted successfully"

        # Show boot time
        BOOT_TIME=$(docker compose logs | grep "Home Assistant initialized" | tail -1 | grep -oP "initialized in \K[0-9.]+")
        log_info "Boot time: ${BOOT_TIME}s"

        return 0
    else
        log_error "Home Assistant boot not detected"
        return 1
    fi
}

test_integration_loaded() {
    print_header "TEST 4: Check Integration Loaded"

    log_info "Checking for violet_pool_controller in logs..."

    if docker compose logs | grep -q "Setting up violet_pool_controller"; then
        log_success "Integration loaded successfully"
        return 0
    else
        log_error "Integration not found in logs"
        return 1
    fi
}

test_api_connection() {
    print_header "TEST 5: Test API Connection"

    log_info "Testing connection to controller..."

    RESPONSE=$(curl -s -w "\n%{http_code}" -u "${CONTROLLER_USER}:${CONTROLLER_PASS}" \
        "http://${CONTROLLER_IP}/getReadings?ALL" 2>/dev/null)

    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    if [ "$HTTP_CODE" = "200" ]; then
        log_success "API connection successful (HTTP 200)"

        # Check if we got valid JSON
        if echo "$BODY" | jq empty 2>/dev/null; then
            DATA_POINTS=$(echo "$BODY" | jq 'length')
            log_info "Received $DATA_POINTS data points"
        fi

        return 0
    else
        log_error "API connection failed (HTTP $HTTP_CODE)"
        return 1
    fi
}

test_pump_control() {
    print_header "TEST 6: Test Pump Control"

    log_info "Setting pump to speed 2 (Normal)..."

    RESPONSE=$(curl -s -u "${CONTROLLER_USER}:${CONTROLLER_PASS}" \
        "http://${CONTROLLER_IP}/setFunctionManually?PUMP,ON,0,2" 2>/dev/null)

    if echo "$RESPONSE" | grep -q "OK"; then
        log_success "Pump command accepted"

        log_info "Waiting 2 seconds for state change..."
        sleep 2

        log_info "Verifying pump state..."
        STATE=$(curl -s -u "${CONTROLLER_USER}:${CONTROLLER_PASS}" \
            "http://${CONTROLLER_IP}/getReadings?PUMP,PUMP_RPM_2" | jq -r '.PUMP_RPM_2')

        if [ "$STATE" = "4" ]; then
            log_success "Pump speed 2 confirmed (PUMP_RPM_2=4)"
            return 0
        else
            log_warning "Pump state verification unclear (PUMP_RPM_2=$STATE)"
            return 1
        fi
    else
        log_error "Pump command failed"
        return 1
    fi
}

test_pump_off() {
    print_header "ACTION: Turn Pump Off"

    log_info "Turning off pump..."

    RESPONSE=$(curl -s -u "${CONTROLLER_USER}:${CONTROLLER_PASS}" \
        "http://${CONTROLLER_IP}/setFunctionManually?PUMP,OFF" 2>/dev/null)

    if echo "$RESPONSE" | grep -q "OK"; then
        log_success "Pump turned off successfully"
        return 0
    else
        log_error "Failed to turn off pump"
        return 1
    fi
}

check_logs_for_errors() {
    print_header "TEST 7: Check Logs for Errors"

    log_info "Searching for errors in Docker logs..."

    ERRORS=$(docker compose logs 2>&1 | grep -i "error" | grep -v "which has not been tested" | tail -10)

    if [ -z "$ERRORS" ]; then
        log_success "No critical errors found"
        return 0
    else
        log_warning "Found potential errors:"
        echo "$ERRORS"
        return 1
    fi
}

show_logs() {
    print_header "DOCKER LOGS (Last 50 lines)"
    docker compose logs --tail=50
}

show_status() {
    print_header "CONTAINER STATUS"
    docker compose ps

    echo ""
    print_header "ENTITY REGISTRY"
    docker compose logs 2>&1 | grep "Registered new.*violet" | tail -10
}

# ============================================================================
# Test Suites
# ============================================================================

run_smoke_tests() {
    print_header "SMOKE TESTS"

    test_docker_running || return 1
    test_container_exists || return 1
    test_ha_boot || return 1
    test_integration_loaded || return 1
    check_logs_for_errors || return 1

    log_success "All smoke tests passed!"
}

run_api_tests() {
    print_header "API TESTS"

    test_api_connection || return 1
    test_pump_control || return 1
    test_pump_off || return 1

    log_success "All API tests passed!"
}

run_all_tests() {
    print_header "RUNNING ALL TESTS"

    run_smoke_tests || return 1
    run_api_tests || return 1

    log_success "ALL TESTS PASSED! ✅"
}

# ============================================================================
# Main Script
# ============================================================================

main() {
    local TEST_NAME="${1:-all}"

    case "$TEST_NAME" in
        "smoke")
            run_smoke_tests
            ;;
        "api")
            run_api_tests
            ;;
        "pump")
            test_api_connection
            test_pump_control
            test_pump_off
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "start")
            start_container
            ;;
        "all"|*)
            # Check if container needs to be started
            if ! test_container_exists; then
                start_container || exit 1
            fi

            run_all_tests
            show_status
            ;;
    esac
}

# Run main function with all arguments
main "$@"
