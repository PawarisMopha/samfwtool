#!/bin/bash
# SamFWTool - ONE CLICK START (GUI)
cd "$(dirname "$0")"

# Auto-install dependencies silently
pip install -q click tqdm lz4 python-magic 2>/dev/null || pip install click tqdm lz4 python-magic 2>/dev/null

# Install tkinter if missing (Linux)
if [ "$(uname)" == "Linux" ] && ! python3 -c "import tkinter" 2>/dev/null; then
    echo "Installing GUI dependencies..."
    sudo apt-get install -y python3-tk 2>/dev/null || true
fi

# Run GUI
export PYTHONPATH="${PWD}:${PYTHONPATH}"
python3 -m samfwtool.gui.main_gui "$@"
