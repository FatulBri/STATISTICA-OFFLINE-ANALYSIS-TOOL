@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-statistica.ps1"
echo.
echo STATISTICA has stopped. Press any key to close this window.
pause >nul
