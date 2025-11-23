@echo off
REM SamFWTool - ONE CLICK START (Windows)
cd /d "%~dp0"

REM Auto-install dependencies
pip install -q click tqdm lz4 python-magic 2>nul

REM Run GUI
set PYTHONPATH=%CD%;%PYTHONPATH%
python -m samfwtool.gui.main_gui %*
