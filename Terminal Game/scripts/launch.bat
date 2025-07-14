@echo off
title Legends of the Realm - Game Launcher

echo ================================================================
echo                  LEGENDS OF THE REALM
echo                    Game Launcher
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python detected. Checking dependencies...
echo.

REM Try to import required modules
python -c "import colorama, pygame, prettytable, tabulate, keyboard" >nul 2>&1
if errorlevel 1 (
    echo Some dependencies are missing. Installing from requirements.txt...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies.
        echo Please run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

echo Starting Legends of the Realm...
echo.

REM Navigate to the parent directory and run the game
cd /d "%~dp0\.."
python main.py

echo.
echo Game exited. Press any key to close...
pause >nul
