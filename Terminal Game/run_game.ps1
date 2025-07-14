# PowerShell script to run the game with debugger support
# This script allows you to run the game and then attach VS Code debugger

param(
    [switch]$WithDebugger,
    [int]$DebugPort = 5678
)

# Set the working directory to the script location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=== Legends of the Realm - Game Launcher ===" -ForegroundColor Cyan
Write-Host "Working Directory: $ScriptDir" -ForegroundColor Yellow

if ($WithDebugger) {
    Write-Host "Starting game with debugger support on port $DebugPort..." -ForegroundColor Green
    Write-Host "To attach debugger from VS Code:" -ForegroundColor Yellow
    Write-Host "1. Set breakpoints in your code" -ForegroundColor White
    Write-Host "2. Press F5 and select 'Attach to Running Game'" -ForegroundColor White
    Write-Host "3. The debugger will connect automatically" -ForegroundColor White
    Write-Host ""
    
    # Install debugpy if not already installed
    python -m pip install debugpy --quiet
    
    # Start the game with debugger
    python -m debugpy --listen $DebugPort --wait-for-client game.py
} else {
    Write-Host "Starting game normally..." -ForegroundColor Green
    python game.py
}

Write-Host ""
Write-Host "Game session ended. Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
