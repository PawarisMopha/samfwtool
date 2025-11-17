#!/bin/bash
# SamFWTool - One-Click Run Script
# This script auto-installs (if needed) and runs SamFWTool

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     SamFWTool - Quick Launcher        ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo ""

# Check if already installed
if [ ! -f "samfwtool-run.sh" ]; then
    echo -e "${YELLOW}First-time setup detected. Running installation...${NC}"
    echo ""
    chmod +x INSTALL.sh
    ./INSTALL.sh
    echo ""
fi

# Set PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Show menu
echo -e "${GREEN}What would you like to do?${NC}"
echo ""
echo "  1) Run CLI (command line)"
echo "  2) Run GUI (graphical interface)"
echo "  3) Show help"
echo "  4) Show tool comparison"
echo "  5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Launching SamFWTool CLI...${NC}"
        echo ""
        python3 -m samfwtool.cli.main
        ;;
    2)
        echo ""
        echo -e "${BLUE}Launching SamFWTool GUI...${NC}"
        echo ""
        if [ -z "$DISPLAY" ] && [ "$(uname)" == "Linux" ]; then
            echo -e "${YELLOW}WARNING: No display available.${NC}"
            echo "GUI requires X11. Use option 1 for CLI instead."
        else
            python3 -m samfwtool.gui.main_gui
        fi
        ;;
    3)
        echo ""
        python3 -m samfwtool.cli.main --help
        ;;
    4)
        echo ""
        python3 -m samfwtool.cli.main compare
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Running CLI..."
        python3 -m samfwtool.cli.main --help
        ;;
esac
