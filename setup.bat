@echo off
echo ============================================
echo Novel Assistant - Setup Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install dependencies
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================
echo Dependencies installed successfully!
echo ============================================
echo.

REM Check for .env file
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your API key(s)
    echo.
    notepad .env
)

echo.
echo Setup complete! Run the application with:
echo   python main.py
echo.
pause
