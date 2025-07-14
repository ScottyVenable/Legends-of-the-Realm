@echo off
echo === Legends of the Realm - Game Launcher ===
echo.
echo Choose your launch option:
echo 1. Run game normally
echo 2. Run game with debugger support
echo 3. Run in new PowerShell window
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting game normally...
    python game.py
) else if "%choice%"=="2" (
    echo Starting game with debugger...
    echo Install debugpy if needed...
    python -m pip install debugpy --quiet
    echo.
    echo Game is starting with debugger on port 5678
    echo To attach from VS Code: Press F5 and select "Attach to Running Game"
    echo.
    python -m debugpy --listen 5678 --wait-for-client game.py
) else if "%choice%"=="3" (
    echo Opening new PowerShell window...
    start powershell -NoExit -Command "cd '%~dp0'; python game.py"
) else (
    echo Invalid choice. Running normally...
    python game.py
)

echo.
pause
