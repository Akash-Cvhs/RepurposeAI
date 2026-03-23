@echo off
echo ========================================
echo VHS Drug Repurposing Platform
echo Starting Unified Backend Server
echo ========================================
echo.

cd backend

echo [1/2] Checking Python environment...
python --version
echo.

echo [2/2] Starting backend on port 8000...
echo.
echo Backend will be available at: http://localhost:8000
echo Health check: http://localhost:8000/health
echo API docs: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

python app.py

pause
