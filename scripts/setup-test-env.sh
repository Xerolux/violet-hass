#!/bin/bash
# Setup Test Environment for Violet Pool Controller
# This script creates a Python 3.12 virtual environment with Home Assistant and test dependencies

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Violet Pool Controller - Test Setup${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if we're in the project root
if [ ! -f "custom_components/violet_pool_controller/manifest.json" ]; then
    echo -e "${RED}Error: Must be run from project root directory${NC}"
    exit 1
fi

# Check Python 3.12
echo -e "${YELLOW}Checking Python 3.12...${NC}"
if ! command -v python3.12 &> /dev/null; then
    echo -e "${RED}Python 3.12 not found. Please install it first:${NC}"
    echo "  sudo apt-get install python3.12 python3.12-venv python3.12-dev"
    exit 1
fi

PYTHON_VERSION=$(python3.12 --version)
echo -e "${GREEN}✓ Found $PYTHON_VERSION${NC}\n"

# Create virtual environment
VENV_DIR=".venv-ha-test"
echo -e "${YELLOW}Creating virtual environment in $VENV_DIR...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}  Virtual environment already exists. Removing...${NC}"
    rm -rf "$VENV_DIR"
fi

python3.12 -m venv "$VENV_DIR"
echo -e "${GREEN}✓ Virtual environment created${NC}\n"

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Activated${NC}\n"

# Upgrade pip, setuptools, wheel
echo -e "${YELLOW}Upgrading pip, setuptools, wheel...${NC}"
pip install --quiet --upgrade pip setuptools wheel
echo -e "${GREEN}✓ Upgraded${NC}\n"

# Install Home Assistant
echo -e "${YELLOW}Installing Home Assistant 2025.1.4...${NC}"
echo -e "${YELLOW}  (This may take a few minutes)${NC}"
pip install --quiet homeassistant==2025.1.4
echo -e "${GREEN}✓ Home Assistant installed${NC}\n"

# Install test dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install --quiet pytest pytest-asyncio pytest-homeassistant-custom-component
echo -e "${GREEN}✓ Test dependencies installed${NC}\n"

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
PYTEST_VERSION=$(pytest --version | head -1)
HA_VERSION=$(python -c "import homeassistant; print(homeassistant.__version__)")
echo -e "${GREEN}✓ pytest: $PYTEST_VERSION${NC}"
echo -e "${GREEN}✓ Home Assistant: $HA_VERSION${NC}\n"

# Create activation helper
echo -e "${YELLOW}Creating activation helper script...${NC}"
cat > activate-test-env.sh << 'EOF'
#!/bin/bash
# Quick activation script for test environment
source .venv-ha-test/bin/activate
export PYTHONPATH="$(pwd):$PYTHONPATH"
echo "✓ Test environment activated"
echo "  Python: $(python --version)"
echo "  pytest: $(pytest --version | head -1)"
echo ""
echo "Run tests with: pytest tests/ -v"
EOF
chmod +x activate-test-env.sh
echo -e "${GREEN}✓ Created activate-test-env.sh${NC}\n"

# Success message
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Test environment setup complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "To activate the environment, run:"
echo -e "  ${YELLOW}source activate-test-env.sh${NC}"
echo -e ""
echo -e "Then run tests with:"
echo -e "  ${YELLOW}pytest tests/ -v${NC}"
echo -e ""
echo -e "Or run specific tests:"
echo -e "  ${YELLOW}pytest tests/test_api.py -v${NC}"
echo -e ""
