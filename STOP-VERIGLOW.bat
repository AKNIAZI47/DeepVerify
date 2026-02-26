@echo off
title VeriGlow Shutdown
color 0C

echo.
echo  ╔════════════════════════════════════════════════════════╗
echo  ║                                                        ║
echo  ║              Stopping VeriGlow Application             ║
echo  ║                                                        ║
echo  ╚════════════════════════════════════════════════════════╝
echo.

echo [1/3] Stopping Backend API...
taskkill /F /FI "WINDOWTITLE eq VeriGlow Backend*" >nul 2>&1
echo Backend stopped ✓
echo.

echo [2/3] Stopping Frontend...
taskkill /F /FI "WINDOWTITLE eq VeriGlow Frontend*" >nul 2>&1
echo Frontend stopped ✓
echo.

echo [3/3] Stopping Docker Services...
docker-compose down
echo Docker services stopped ✓
echo.

echo  ════════════════════════════════════════════════════════
echo.
echo  VeriGlow stopped successfully!
echo.
echo  To start again, run: START-VERIGLOW.bat
echo.
timeout /t 3 >nul
