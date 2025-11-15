@echo off
REM SamFWTool One-Click Installation (Windows)
REM Double-click this file to install SamFWTool with GUI

echo ========================================
echo  SamFWTool Installation Wizard
echo ========================================
echo.
echo Starting installation wizard...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found. Launching installation wizard...
echo.

REM Launch wizard
python install_wizard.py

if errorlevel 1 (
    echo.
    echo Installation failed!
    pause
    exit /b 1
)

echo.
echo Installation complete!
pause
