@echo off
REM SamFWTool - One-Click Run Script for Windows
REM This script auto-installs (if needed) and runs SamFWTool

cd /d "%~dp0"

echo ========================================
echo      SamFWTool - Quick Launcher
echo ========================================
echo.

REM Check if already installed
if not exist "samfwtool-run.bat" (
    echo First-time setup detected. Running installation...
    echo.
    call INSTALL.bat
    echo.
)

REM Set PYTHONPATH
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Show menu
echo What would you like to do?
echo.
echo   1) Run CLI (command line)
echo   2) Run GUI (graphical interface)
echo   3) Show help
echo   4) Show tool comparison
echo   5) Exit
echo.
set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" goto CLI
if "%choice%"=="2" goto GUI
if "%choice%"=="3" goto HELP
if "%choice%"=="4" goto COMPARE
if "%choice%"=="5" goto EXIT
goto CLI

:CLI
echo.
echo Launching SamFWTool CLI...
echo.
python -m samfwtool.cli.main
goto END

:GUI
echo.
echo Launching SamFWTool GUI...
echo.
python -m samfwtool.gui.main_gui
goto END

:HELP
echo.
python -m samfwtool.cli.main --help
pause
goto END

:COMPARE
echo.
python -m samfwtool.cli.main compare
pause
goto END

:EXIT
echo Goodbye!
goto END

:END
