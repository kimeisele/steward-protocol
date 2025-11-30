@echo off
REM ╔════════════════════════════════════════════════════════════════════════╗
REM ║                      PROJECT VIMANA: LAUNCHER (Windows)                ║
REM ║                   "One Binary to rule them all"                        ║
REM ║                                                                        ║
REM ║  Batch wrapper for the VibeOS bootloader on Windows.                 ║
REM ║  Usage: vibe.bat [--port 8000] [--debug]                             ║
REM ╚════════════════════════════════════════════════════════════════════════╝

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
for /f "delims=" %%A in ('cd') do set "SCRIPT_DIR=%%~dpA"

REM Check if Python 3 is available
python3 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python 3 is not installed or not in PATH
    echo Please install Python 3.10 or later and try again.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Run the launcher with all arguments passed through
python3 vibe_launcher.py %*

pause
