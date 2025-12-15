@echo off
echo ============================================================
echo    RAG System - Web Interface Launcher
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
) else (
    echo [OK] Dependencies are installed
)

echo.
echo [2/3] Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama is not running!
    echo Please start Ollama or change API_TYPE to "openai" in config.py
    echo.
    echo To start Ollama: Run "ollama serve" in another terminal
    echo.
) else (
    echo [OK] Ollama is running
)

echo.
echo [3/3] Starting Flask server...
echo.
echo ============================================================
echo    Server will start at http://localhost:5000
echo    Press Ctrl+C to stop the server
echo ============================================================
echo.

python backend.py
