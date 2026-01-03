#!/bin/bash
# Start Home Assistant Test Instance with Violet Pool Controller
# This creates a minimal HA instance for testing the integration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Starting Home Assistant Test Instance${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Test instance directory
HA_CONFIG_DIR="$PROJECT_ROOT/.ha-test-instance"
CUSTOM_COMPONENTS_DIR="$HA_CONFIG_DIR/custom_components"

# Clean previous instance if requested
if [ "$1" == "--clean" ]; then
    echo -e "${YELLOW}Cleaning previous test instance...${NC}"
    rm -rf "$HA_CONFIG_DIR"
    echo -e "${GREEN}✓ Cleaned${NC}\n"
fi

# Create HA config directory structure
echo -e "${YELLOW}Setting up Home Assistant config directory...${NC}"
mkdir -p "$HA_CONFIG_DIR"
mkdir -p "$CUSTOM_COMPONENTS_DIR"

# Create symbolic link to integration
echo -e "${YELLOW}Linking Violet Pool Controller integration...${NC}"
rm -rf "$CUSTOM_COMPONENTS_DIR/violet_pool_controller"
ln -s "$PROJECT_ROOT/custom_components/violet_pool_controller" \
      "$CUSTOM_COMPONENTS_DIR/violet_pool_controller"
echo -e "${GREEN}✓ Integration linked${NC}\n"

# Create minimal configuration.yaml
if [ ! -f "$HA_CONFIG_DIR/configuration.yaml" ]; then
    echo -e "${YELLOW}Creating configuration.yaml...${NC}"
    cat > "$HA_CONFIG_DIR/configuration.yaml" << 'EOF'
# Home Assistant Test Configuration
# Violet Pool Controller Integration Test

default_config:

# Enable frontend
frontend:
  themes: !include_dir_merge_named themes

# Enable lovelace
lovelace:
  mode: yaml

# Logger configuration
logger:
  default: info
  logs:
    custom_components.violet_pool_controller: debug
    homeassistant.components.http: warning
    homeassistant.components.websocket_api: warning

# HTTP configuration
http:
  server_port: 8123
  cors_allowed_origins:
    - http://localhost:8123
    - http://127.0.0.1:8123

# Recorder - use SQLite for testing
recorder:
  db_url: sqlite:///:memory:
  purge_keep_days: 1
  commit_interval: 1

# History
history:

# Enable the integration (will be configured via UI)
# violet_pool_controller:
EOF
    echo -e "${GREEN}✓ Configuration created${NC}\n"
fi

# Create secrets.yaml if needed
if [ ! -f "$HA_CONFIG_DIR/secrets.yaml" ]; then
    echo -e "${YELLOW}Creating secrets.yaml...${NC}"
    cat > "$HA_CONFIG_DIR/secrets.yaml" << 'EOF'
# Test secrets file
EOF
    echo -e "${GREEN}✓ Secrets created${NC}\n"
fi

# Check if virtual environment exists
VENV_DIR="$PROJECT_ROOT/.venv-ha-test"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Virtual environment not found!${NC}"
    echo -e "Run ${YELLOW}./scripts/setup-test-env.sh${NC} first\n"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Activated${NC}\n"

# Check Home Assistant installation
if ! python -c "import homeassistant" 2>/dev/null; then
    echo -e "${RED}Home Assistant not installed in venv!${NC}"
    echo -e "Run ${YELLOW}./scripts/setup-test-env.sh${NC} first\n"
    exit 1
fi

echo -e "${GREEN}Home Assistant installed and ready${NC}\n"

# Display info
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Instance Information${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Config Directory: ${YELLOW}$HA_CONFIG_DIR${NC}"
echo -e "Integration Path: ${YELLOW}$CUSTOM_COMPONENTS_DIR/violet_pool_controller${NC}"
echo -e "Web Interface:    ${GREEN}http://localhost:8123${NC}"
echo -e ""
echo -e "${YELLOW}Press Ctrl+C to stop Home Assistant${NC}\n"

# Start Home Assistant
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Starting Home Assistant...${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Run HA with the test config directory
hass --config "$HA_CONFIG_DIR" --log-rotate-days 1 --log-file "$HA_CONFIG_DIR/home-assistant.log"
