@echo off
REM SamFWTool - One-Click Installation Script for Windows
REM This script installs SamFWTool with all dependencies

echo ======================================
echo   SamFWTool Installation Wizard
echo ======================================
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel --quiet
echo [OK] Pip upgraded

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt --quiet
echo [OK] Dependencies installed

REM Install SamFWTool
echo Installing SamFWTool...
python -m pip install -e . --use-pep517 --quiet 2>nul
if errorlevel 1 (
    echo [WARNING] Standard install failed, using PYTHONPATH method...
    set PYTHONPATH=%CD%;%PYTHONPATH%
)

REM Verify installation
echo Verifying installation...
python -m samfwtool.cli.main --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)
echo [OK] Installation verified

REM Create launcher scripts
echo Creating launcher scripts...

REM CLI Launcher
(
echo @echo off
echo cd /d "%%~dp0"
echo set PYTHONPATH=%%CD%%;%%PYTHONPATH%%
echo python -m samfwtool.cli.main %%*
) > samfwtool-run.bat
echo [OK] Created CLI launcher: samfwtool-run.bat

REM GUI Launcher
(
echo @echo off
echo cd /d "%%~dp0"
echo set PYTHONPATH=%%CD%%;%%PYTHONPATH%%
echo python -m samfwtool.gui.main_gui %%*
) > samfwtool-gui-run.bat
echo [OK] Created GUI launcher: samfwtool-gui-run.bat

echo.
echo ======================================
echo   Installation Complete!
echo ======================================
echo.
echo [OK] SamFWTool is ready to use!
echo.
echo Quick Start:
echo.
echo   CLI Usage:
echo     samfwtool-run.bat --help
echo     samfwtool-run.bat compare
echo     samfwtool-run.bat devices
echo.
echo   GUI Usage:
echo     samfwtool-gui-run.bat
echo.
echo   Direct Python:
echo     python -m samfwtool.cli.main --help
echo     python -m samfwtool.gui.main_gui
echo.
pause
