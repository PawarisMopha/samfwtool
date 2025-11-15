#!/bin/bash
# SamFWTool GUI Launcher (Linux/macOS)
# One-click launcher for SamFWTool GUI

echo "Starting SamFWTool GUI..."

# Try to run from installed location
if [ -f "$HOME/.local/share/samfwtool/samfwtool/gui/main_gui.py" ]; then
    python3 "$HOME/.local/share/samfwtool/samfwtool/gui/main_gui.py" &
    exit 0
fi

# Try to run from current directory
if [ -f "samfwtool/gui/main_gui.py" ]; then
    python3 samfwtool/gui/main_gui.py &
    exit 0
fi

# Try as module
if python3 -m samfwtool.gui.main_gui 2>/dev/null; then
    exit 0
fi

echo "ERROR: SamFWTool not found!"
echo ""
echo "Please run ./INSTALL_GUI.sh first."
exit 1
