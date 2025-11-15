#!/bin/bash
# SamFWTool One-Click Installation (Linux/macOS)
# Run this script to install SamFWTool with GUI

set -e

echo "========================================"
echo " SamFWTool Installation Wizard"
echo "========================================"
echo ""
echo "Starting installation wizard..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    echo ""
    echo "Please install Python 3.8+ from:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    echo "  macOS: brew install python-tk"
    echo "  Fedora: sudo dnf install python3 python3-tkinter"
    exit 1
fi

echo "Python found: $(python3 --version)"

# Check tkinter
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "WARNING: tkinter not found!"
    echo ""
    echo "Installing tkinter..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3-tk
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-tkinter
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-tkinter
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "Please install tkinter:"
        echo "  brew install python-tk"
        exit 1
    fi
fi

echo ""
echo "Launching installation wizard..."
echo ""

# Launch wizard
python3 install_wizard.py

echo ""
echo "Installation complete!"
