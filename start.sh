#!/bin/bash
# SamFWTool - ONE CLICK START
# Just run: ./start.sh

cd "$(dirname "$0")"

# Auto-install if needed (silent)
if ! python3 -c "import click, tqdm, lz4" 2>/dev/null; then
    echo "Installing dependencies (one-time)..."
    pip install -q click tqdm lz4 python-magic 2>/dev/null || pip install click tqdm lz4 python-magic
fi

# Set path and run
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# If argument provided, run CLI with it
if [ $# -gt 0 ]; then
    python3 -m samfwtool.cli.main "$@"
else
    # No args = show interactive menu
    python3 -m samfwtool.cli.main --help
    echo ""
    echo "Examples:"
    echo "  ./start.sh info firmware.tar.md5      # Show firmware info"
    echo "  ./start.sh extract firmware.tar.md5   # Extract firmware"
    echo "  ./start.sh devices                    # List connected devices"
    echo "  ./start.sh scan firmware.tar.md5      # Security scan"
fi
