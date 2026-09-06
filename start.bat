@echo off
echo ============================================
echo   AlfaazAI - Automatic Setup and Launch
echo ============================================
echo.

cd /d "%~dp0backend"

echo [1/4] Creating virtual environment (if not already created)...
if not exist venv (
    py -3.12 -m venv venv 2>nul
    if not exist venv (
        echo Python 3.12 not found, trying default Python version...
        py -m venv venv
    )
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo [4/4] Starting AlfaazAI server...
echo.
echo ============================================
echo   Server starting at http://127.0.0.1:8000
echo   Now open frontend\index.html in your browser
echo   Keep this window open while testing!
echo ============================================
echo.

uvicorn main:app --reload --port 8000

pause
