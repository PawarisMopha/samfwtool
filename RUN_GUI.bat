@echo off
REM SamFWTool GUI Launcher (Windows)
REM One-click launcher for SamFWTool GUI

echo Starting SamFWTool GUI...

REM Try to run from installed location
if exist "%LOCALAPPDATA%\SamFWTool\samfwtool\gui\main_gui.py" (
    python "%LOCALAPPDATA%\SamFWTool\samfwtool\gui\main_gui.py"
    exit /b 0
)

REM Try to run from current directory
if exist "samfwtool\gui\main_gui.py" (
    python samfwtool\gui\main_gui.py
    exit /b 0
)

REM Try as module
python -m samfwtool.gui.main_gui 2>nul
if errorlevel 1 (
    echo ERROR: SamFWTool not found!
    echo.
    echo Please run INSTALL_GUI.bat first.
    pause
    exit /b 1
)
