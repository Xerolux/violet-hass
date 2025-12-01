#!/bin/bash
# Run Tests for Violet Pool Controller
# This script runs all tests in the proper environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if virtual environment exists
VENV_DIR=".venv-ha-test"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Error: Test environment not found${NC}"
    echo -e "Run ${YELLOW}./scripts/setup-test-env.sh${NC} first"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Parse command line arguments
TEST_PATH="${1:-tests/}"
PYTEST_ARGS="${@:2}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running Tests${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}Environment:${NC}"
echo -e "  Python: $(python --version)"
echo -e "  pytest: $(pytest --version | head -1)"
echo -e "  Test path: $TEST_PATH"
echo -e "  Extra args: $PYTEST_ARGS"
echo -e ""

# Run pytest with proper settings
pytest "$TEST_PATH" -v $PYTEST_ARGS

# Capture exit code
EXIT_CODE=$?

echo -e ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Tests failed with code $EXIT_CODE${NC}"
    echo -e "${RED}========================================${NC}"
fi

exit $EXIT_CODE
