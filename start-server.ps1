# MindMate Application Startup Script
# This script starts the Django server with Daphne (for WebSocket support)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   MindMate - Starting Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Redis
Write-Host "[1/2] Checking Redis..." -ForegroundColor Yellow
$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
if ($redisProcess) {
    Write-Host "[OK] Redis is running (PID: $($redisProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Redis is not running!" -ForegroundColor Red
    Write-Host "Starting Redis..." -ForegroundColor Yellow
    .\start-redis.ps1
}

Write-Host ""

# Step 2: Start Daphne Server
Write-Host "[2/2] Starting Daphne ASGI Server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Server Starting on http://localhost:8000" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Activate virtual environment and start Daphne
& ".\venv\Scripts\Activate.ps1"
& ".\venv\Scripts\python.exe" -m daphne -b 0.0.0.0 -p 8000 perplex.asgi:application
