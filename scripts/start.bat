@echo off
echo ========================================
echo SME Toolkit - Starting Servers
echo ========================================
echo.

REM Start Backend in new window
echo Starting Backend Server (port 8000)...
start "SME Toolkit Backend" cmd /k "cd /d %~dp0..\sme-toolkit-backend && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend in new window
echo Starting Frontend Server (port 5173)...
start "SME Toolkit Frontend" cmd /k "cd /d %~dp0.. && npm run dev"

echo.
echo ========================================
echo Servers Started!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Frontend: http://localhost:5173
echo.
echo Press any key to exit this window...
echo (Server windows will remain open)
pause >nul
