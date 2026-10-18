@echo off
setlocal
cd /d "%~dp0"
echo.
echo ================================================
echo   AI Operations Workbench V3 - Product Experience
echo ================================================
echo.
where node >nul 2>&1
if errorlevel 1 (
  echo Node.js is required. Install Node.js LTS first.
  pause
  exit /b 1
)
where python >nul 2>&1
if errorlevel 1 (
  echo Python is not available in PATH.
  pause
  exit /b 1
)

echo Stopping any previous Workbench processes on ports 5173, 8001-8004...
for %%P in (5173 8001 8002 8003 8004) do (
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr ":%%P " ^| findstr LISTENING') do taskkill /PID %%A /F >nul 2>&1
)

echo Starting backend services...
start "Compressor API - V3" cmd /k "cd /d "%~dp0Compressor Health Module" && python -m uvicorn app:app --port 8001"
start "Optimizer API - V3" cmd /k "cd /d "%~dp0Feed Allocation Optimizer" && python -m uvicorn app:app --port 8002"
start "Vision API - V3" cmd /k "cd /d "%~dp0Computer Vision" && python -m uvicorn app:app --port 8003"
start "Intelligence API - V3" cmd /k "cd /d "%~dp0Market Intelligence" && python -m uvicorn app:app --port 8004"

echo Starting V3 website...
cd /d "%~dp0professional_web"
if not exist node_modules call npm install
start "AI Operations Workbench V3" cmd /k "npm run dev"
timeout /t 6 >nul
start http://127.0.0.1:5173
endlocal
