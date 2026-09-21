@echo off
echo.
echo ============================================================
echo   WeatherGPT v2.0 — AI Weather Intelligence Platform
echo ============================================================
echo.

:: Check for Python venv
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] No .venv found, using system Python.
)

:: Install / update dependencies
echo [1/3] Checking dependencies...
pip install -r requirements.txt -q

:: Verify API keys are not placeholders
findstr /C:"your_" .env >nul 2>&1
if %errorlevel%==0 (
    echo.
    echo [WARNING] .env still has placeholder keys!
    echo   Please edit .env and add your real API keys:
    echo   - OPENWEATHERMAP_API_KEY  (free at openweathermap.org)
    echo   - GEMINI_API_KEY          (free at aistudio.google.com)
    echo.
    pause
)

:: Start the unified server (FastAPI serves both API + frontend)
echo [2/3] Starting WeatherGPT server...
echo.
echo ============================================================
echo   App      → http://localhost:8000
echo   API Docs → http://localhost:8000/docs
echo   Health   → http://localhost:8000/health
echo ============================================================
echo.
echo Press Ctrl+C to stop.
echo.

python -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0
