#!/bin/bash
# Check Home Assistant logs for errors related to Violet Pool Controller

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HA_CONFIG_DIR="$PROJECT_ROOT/.ha-test-instance"
LOG_FILE="$HA_CONFIG_DIR/home-assistant.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ ! -f "$LOG_FILE" ]; then
    echo -e "${RED}No log file found. Start HA first with:${NC}"
    echo -e "  ${YELLOW}./scripts/start-ha-test.sh${NC}"
    exit 1
fi

echo -e "${GREEN}=== Violet Pool Controller Logs ===${NC}\n"

# Filter for integration-related logs
echo -e "${YELLOW}Recent integration activity:${NC}"
grep -i "violet_pool_controller" "$LOG_FILE" | tail -50

echo -e "\n${RED}=== Errors ===${NC}"
grep -E "ERROR|Exception|Traceback" "$LOG_FILE" | grep -i "violet" | tail -20

echo -e "\n${YELLOW}=== Warnings ===${NC}"
grep "WARNING" "$LOG_FILE" | grep -i "violet" | tail -10

echo -e "\n${GREEN}=== Config Flow Activity ===${NC}"
grep -E "config_flow|Config flow" "$LOG_FILE" | grep -i "violet" | tail -15

echo -e "\n${YELLOW}Full log: $LOG_FILE${NC}"
echo -e "${YELLOW}Live follow: tail -f $LOG_FILE${NC}"
