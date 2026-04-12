@echo off
echo ========================================
echo   Data Generation AI Platform
echo   Setup and Launch Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version
echo.

REM Check if .env file exists and has API key
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create a .env file and add your GEMINI_API_KEY
    echo See QUICKSTART.md for instructions
    pause
    exit /b 1
)

findstr /C:"GEMINI_API_KEY=" .env >nul
if errorlevel 1 (
    echo ERROR: GEMINI_API_KEY not found in .env file
    echo Please add your API key to the .env file
    echo Get your free API key from: https://makersuite.google.com/app/apikey
    pause
    exit /b 1
)

REM Check if API key is empty
findstr /C:"GEMINI_API_KEY=$" .env >nul
if not errorlevel 1 (
    echo WARNING: GEMINI_API_KEY appears to be empty
    echo Please add your actual API key to the .env file
    echo Get your free API key from: https://makersuite.google.com/app/apikey
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/3] Starting the application...
echo.
echo ========================================
echo   Server will start at:
echo   http://localhost:8000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python main.py

pause
