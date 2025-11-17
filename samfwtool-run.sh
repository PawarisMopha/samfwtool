#!/bin/bash
# SamFWTool CLI Launcher
cd "$(dirname "$0")"
export PYTHONPATH="${PWD}:${PYTHONPATH}"
python3 -m samfwtool.cli.main "$@"
