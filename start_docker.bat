@echo off
cd /d "%~dp0"
echo Starting containerized AI Operations Workbench...
docker compose up --build
pause
