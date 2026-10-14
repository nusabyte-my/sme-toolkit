@echo off
echo ========================================
echo SME Toolkit - Quick Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python and Node.js found
echo.

REM Setup Backend
echo ========================================
echo Setting up Backend...
echo ========================================
cd /d "%~dp0..\sme-toolkit-backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Please edit sme-toolkit-backend\.env and add your API keys!
    echo At minimum, add your GEMINI_API_KEY
    echo.
)

echo.
echo ========================================
echo Setting up Frontend...
echo ========================================
cd /d "%~dp0.."

echo Installing npm dependencies...
call npm install

if not exist ".env.local" (
    echo Creating .env.local...
    echo VITE_API_BASE_URL=http://localhost:8000 > .env.local
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit sme-toolkit-backend\.env and add your GEMINI_API_KEY
echo 2. Run start.bat to start both servers
echo.
pause
