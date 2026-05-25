@echo off
REM SmartInsight AI Startup Script for Windows

echo.
echo  SmartInsight AI - Behavioral Intelligence Platform
echo  ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% detected

echo.
echo [*] Installing dependencies from requirements.txt...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

echo.
echo ============================================================
echo  Launching SmartInsight AI...
echo.
echo  Open your browser to: http://localhost:8501
echo  First run will take 2-3 minutes to train models
echo ============================================================
echo.

streamlit run Home.py
pause
