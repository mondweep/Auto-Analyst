#!/bin/bash
# setup_attribute_filtering.sh - Script to set up attribute filtering tools

set -e  # Exit on any error

# Text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORTS_DIR="${SCRIPT_DIR}/exports"
VEHICLES_CSV="${EXPORTS_DIR}/vehicles.csv"

# Print header
echo -e "${BLUE}=== Auto-Analyst Attribute Filtering Setup ===${NC}"
echo -e "${BLUE}This script will set up the attribute filtering tools.${NC}"
echo ""

# Create directories if they don't exist
echo -e "${YELLOW}Checking directories...${NC}"
if [ ! -d "$EXPORTS_DIR" ]; then
    echo -e "Creating exports directory: ${EXPORTS_DIR}"
    mkdir -p "$EXPORTS_DIR"
fi
echo -e "${GREEN}✓ Directories verified${NC}"
echo ""

# Check for vehicles.csv
echo -e "${YELLOW}Checking for vehicles dataset...${NC}"
if [ ! -f "$VEHICLES_CSV" ]; then
    echo -e "${YELLOW}Warning: vehicles.csv not found at ${VEHICLES_CSV}${NC}"
    echo -e "You'll need to provide this file before running the attribute filtering tools."
    echo -e "The file should be placed at: ${VEHICLES_CSV}"
else
    echo -e "${GREEN}✓ Found vehicles dataset: ${VEHICLES_CSV}${NC}"
fi
echo ""

# Make Python scripts executable
echo -e "${YELLOW}Making scripts executable...${NC}"
chmod +x "${SCRIPT_DIR}/standalone_attribute_server.py" 2>/dev/null || true
chmod +x "${SCRIPT_DIR}/attribute_proxy.py" 2>/dev/null || true
echo -e "${GREEN}✓ Scripts are now executable${NC}"
echo ""

# Check if Flask is installed
echo -e "${YELLOW}Checking for Flask...${NC}"
if python -c "import flask" &>/dev/null; then
    echo -e "${GREEN}✓ Flask is installed${NC}"
else
    echo -e "${YELLOW}Flask is not installed. Installing...${NC}"
    pip install flask
    echo -e "${GREEN}✓ Flask installed${NC}"
fi
echo ""

# Check for NumPy compatibility issues
echo -e "${YELLOW}Checking for NumPy compatibility...${NC}"
NUMPY_VERSION=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "not_installed")

if [[ $NUMPY_VERSION == "not_installed" ]]; then
    echo -e "${YELLOW}NumPy is not installed. No compatibility issues.${NC}"
elif [[ $NUMPY_VERSION =~ ^2\. ]]; then
    echo -e "${YELLOW}NumPy 2.x detected (${NUMPY_VERSION}). This may cause compatibility issues with some dependencies.${NC}"
    echo -e "${BLUE}Recommendation: Use our standalone attribute server which avoids NumPy dependencies.${NC}"
else
    echo -e "${GREEN}✓ NumPy ${NUMPY_VERSION} detected. This should be compatible with most libraries.${NC}"
fi
echo ""

# Print usage instructions
echo -e "${BLUE}=== Attribute Filtering Tools Ready ===${NC}"
echo -e "You can now use the following commands:"
echo ""
echo -e "${YELLOW}1. Run the standalone attribute server:${NC}"
echo -e "   $ ./standalone_attribute_server.py"
echo -e "   This runs a lightweight server with no NumPy dependencies, providing:"
echo -e "   - /api/attribute-query - Natural language query detection"
echo -e "   - /api/direct-count - Direct attribute counting"
echo -e "   - /api/chat-attribute - Chat-compatible attribute queries"
echo ""
echo -e "${YELLOW}2. Run the attribute proxy (optional):${NC}"
echo -e "   $ ./attribute_proxy.py"
echo -e "   This runs a proxy that tries both the standalone server and main app, providing:"
echo -e "   - Seamless integration with the frontend"
echo -e "   - Automatic fallback between servers"
echo -e "   - Consistent API regardless of which backend is running"
echo ""
echo -e "${BLUE}Recommended setup:${NC}"
echo -e "1. Run the standalone attribute server: ./standalone_attribute_server.py"
echo -e "2. Run the attribute proxy: ./attribute_proxy.py"
echo -e "3. Configure your frontend to use the proxy URL (default: http://localhost:8080)"
echo ""
echo -e "${GREEN}Setup complete!${NC}" 