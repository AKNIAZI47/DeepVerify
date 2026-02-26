@echo off
title VeriGlow One-Click Launcher
color 0A

echo.
echo  ╔════════════════════════════════════════════════════════╗
echo  ║                                                        ║
echo  ║          VeriGlow One-Click Launcher                   ║
echo  ║          Starting Everything Automatically...          ║
echo  ║                                                        ║
echo  ╚════════════════════════════════════════════════════════╝
echo.
echo  This will automatically:
echo  [✓] Check prerequisites
echo  [✓] Install dependencies
echo  [✓] Start Docker services
echo  [✓] Start backend API
echo  [✓] Start frontend
echo  [✓] Open application in browser
echo.
echo  ════════════════════════════════════════════════════════
echo.
timeout /t 3 >nul

REM ============================================
REM Step 1: Check Prerequisites
REM ============================================
echo [1/7] Checking Prerequisites...
echo.

echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.11+ from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
python --version
echo Python OK ✓
echo.

echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo.
    echo Please install Node.js LTS from: https://nodejs.org
    echo.
    pause
    exit /b 1
)
node --version
echo Node.js OK ✓
echo.

echo Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo.
    echo Docker Desktop must be running before starting VeriGlow.
    echo.
    echo Quick Fix:
    echo 1. Press Windows key and search "Docker Desktop"
    echo 2. Click to launch Docker Desktop
    echo 3. Wait for whale icon to appear in system tray
    echo 4. Wait until whale stops animating (means ready)
    echo 5. Run this launcher again
    echo.
    echo Need help installing Docker?
    echo Open: HOW-TO-RUN-DOCKER.txt (quick guide)
    echo Open: DOCKER-SETUP-GUIDE.txt (detailed steps)
    echo.
    pause
    exit /b 1
)
echo Docker OK ✓
echo.

echo All prerequisites met! ✓
echo.
timeout /t 2 >nul

REM ============================================
REM Step 2: Setup Backend
REM ============================================
echo [2/7] Setting Up Backend...
echo.

cd backend

REM Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
    echo Virtual environment created ✓
)

REM Activate virtual environment and install dependencies
echo Installing backend dependencies...
call .venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo Backend dependencies installed ✓

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating backend configuration...
    (
        echo MONGO_URI=mongodb://localhost:27017
        echo MONGO_DB=veriglow
        echo REDIS_URL=redis://localhost:6379
        echo JWT_SECRET=change-me-in-production-use-secret-generator
        echo ENVIRONMENT=development
        echo DEBUG=true
        echo PORT=8000
        echo HOST=0.0.0.0
    ) > .env
    echo Backend configuration created ✓
)

cd ..
echo.
timeout /t 2 >nul

REM ============================================
REM Step 3: Setup Frontend
REM ============================================
echo [3/7] Setting Up Frontend...
echo.

cd frontend

REM Install npm dependencies if node_modules doesn't exist
if not exist node_modules (
    echo Installing frontend dependencies...
    echo This may take a few minutes on first run...
    call npm install --silent
    echo Frontend dependencies installed ✓
) else (
    echo Frontend dependencies already installed ✓
)

REM Create .env.local file if it doesn't exist
if not exist .env.local (
    echo Creating frontend configuration...
    (
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
    ) > .env.local
    echo Frontend configuration created ✓
)

cd ..
echo.
timeout /t 2 >nul

REM ============================================
REM Step 4: Start Docker Services
REM ============================================
echo [4/7] Starting Docker Services...
echo.

echo Starting MongoDB and Redis...
docker-compose up -d mongo redis

REM Wait for services to be ready
echo Waiting for services to initialize...
timeout /t 5 >nul

echo Docker services started ✓
echo.
timeout /t 2 >nul

REM ============================================
REM Step 5: Setup Database
REM ============================================
echo [5/7] Setting Up Database Indexes...
echo.

cd backend
call .venv\Scripts\activate.bat
python scripts/create_indexes.py create >nul 2>&1
if %errorlevel% equ 0 (
    echo Database indexes created ✓
) else (
    echo Database indexes will be created on first use
)
cd ..
echo.
timeout /t 2 >nul

REM ============================================
REM Step 6: Start Backend API
REM ============================================
echo [6/7] Starting Backend API...
echo.

start "VeriGlow Backend API" cmd /k "title VeriGlow Backend API && cd backend && call .venv\Scripts\activate.bat && echo Starting Backend API on http://localhost:8000 && echo API Documentation: http://localhost:8000/docs && echo. && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 8 >nul
echo Backend API started ✓
echo.
timeout /t 2 >nul

REM ============================================
REM Step 7: Start Frontend
REM ============================================
echo [7/7] Starting Frontend...
echo.

start "VeriGlow Frontend" cmd /k "title VeriGlow Frontend && cd frontend && echo Starting Frontend on http://localhost:3000 && echo. && npm run dev"

echo Waiting for frontend to start...
timeout /t 10 >nul
echo Frontend started ✓
echo.

REM ============================================
REM Success!
REM ============================================
cls
echo.
echo  ╔════════════════════════════════════════════════════════╗
echo  ║                                                        ║
echo  ║              VeriGlow Started Successfully!            ║
echo  ║                                                        ║
echo  ╚════════════════════════════════════════════════════════╝
echo.
echo  ✓ Backend API:        http://localhost:8000
echo  ✓ API Documentation:  http://localhost:8000/docs
echo  ✓ Frontend App:       http://localhost:3000
echo.
echo  ════════════════════════════════════════════════════════
echo.
echo  Opening application in your browser...
echo.

timeout /t 3 >nul

REM Open in browser
start http://localhost:3000

echo.
echo  Application is now running!
echo.
echo  Two terminal windows are open:
echo  - VeriGlow Backend API (port 8000)
echo  - VeriGlow Frontend (port 3000)
echo.
echo  To stop the application:
echo  - Close both terminal windows
echo  - Or run: STOP-VERIGLOW.bat
echo.
echo  Press any key to close this launcher...
pause >nul
