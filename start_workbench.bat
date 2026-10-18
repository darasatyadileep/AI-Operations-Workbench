@echo off
setlocal
cd /d "%~dp0"

echo ===============================================
echo        AI OPERATIONS WORKBENCH - STARTING
echo ===============================================
echo.

echo [1/5] Starting Compressor Health API on port 8001...
start "Compressor Health API" /D "%~dp0Compressor Health Module" cmd /k python -m uvicorn app:app --port 8001

timeout /t 2 /nobreak >nul

echo [2/5] Starting Feed Optimizer API on port 8002...
start "Feed Optimizer API" /D "%~dp0Feed Allocation Optimizer" cmd /k python -m uvicorn app:app --port 8002

timeout /t 2 /nobreak >nul

echo [3/5] Starting Visual Operator Rounds API on port 8003...
start "Visual Operator Rounds API" /D "%~dp0Computer Vision" cmd /k python -m uvicorn app:app --port 8003

timeout /t 2 /nobreak >nul

echo [4/5] Starting Technology Intelligence API on port 8004...
start "Technology Intelligence API" /D "%~dp0Market Intelligence" cmd /k python -m uvicorn app:app --port 8004

timeout /t 2 /nobreak >nul

echo [5/5] Starting unified Streamlit website...
start "AI Operations Workbench" /D "%~dp0" cmd /k python -m streamlit run Home.py

echo.
echo All services have been launched.
echo Workbench URL: http://localhost:8501
echo Keep the five command windows open while using the Workbench.
echo.
pause
