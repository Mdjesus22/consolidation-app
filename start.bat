@echo off
title Reconciliation Tool
echo.
echo  ============================================
echo   Reconciliation Tool - Starting...
echo  ============================================
echo.

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found. Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install / upgrade required packages silently
echo  Installing / checking required packages...
python -m pip install --quiet --upgrade flask flask-cors pandas openpyxl
if errorlevel 1 (
    echo  ERROR: Failed to install packages. Try running as Administrator.
    pause
    exit /b 1
)

echo  Packages ready.
echo.
echo  Starting server at http://localhost:5050
echo  (A browser window will open automatically)
echo.
echo  Keep this window open while using the app.
echo  Close it to stop the server.
echo.

REM Change to the directory where this .bat lives, then start server
cd /d "%~dp0"
python server.py

pause
