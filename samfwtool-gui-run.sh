#!/bin/bash
# SamFWTool GUI Launcher
cd "$(dirname "$0")"
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Check if display is available
if [ -z "$DISPLAY" ] && [ "$(uname)" == "Linux" ]; then
    echo "ERROR: No display available. GUI requires X11."
    echo "Use samfwtool-run.sh for CLI version instead."
    exit 1
fi

python3 -m samfwtool.gui.main_gui "$@"
