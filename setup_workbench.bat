@echo off
setlocal
cd /d "%~dp0"
echo Installing Workbench Python packages...
python -m pip install -r requirements_workbench.txt
echo.
echo Setup complete. Double-click start_workbench.bat to launch the Workbench.
pause
