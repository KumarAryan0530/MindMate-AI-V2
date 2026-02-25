# SafeMind-AI Voice Calls - Startup Helper
# This script will help you start all required services

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SafeMind-AI Voice Calls - Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "E:\all-projects\SafeMind-AI"

# Check if we're in the right directory
if (-not (Test-Path "$projectPath\manage.py")) {
    Write-Host "ERROR: Cannot find manage.py in $projectPath" -ForegroundColor Red
    Write-Host "Please update the projectPath variable in this script." -ForegroundColor Yellow
    exit 1
}

Set-Location $projectPath

# Step 1: Check Python environment
Write-Host "[1/7] Checking Python environment..." -ForegroundColor Yellow
if (Test-Path "$projectPath\venv\Scripts\python.exe") {
    Write-Host "  ✓ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "  ✗ Virtual environment not found at: $projectPath\venv" -ForegroundColor Red
    Write-Host "  Run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Step 2: Run diagnostic test
Write-Host ""
Write-Host "[2/7] Running diagnostic test..." -ForegroundColor Yellow
Write-Host "  This will verify your API keys and connections." -ForegroundColor Gray
Write-Host ""

$testResult = & "$projectPath\venv\Scripts\python.exe" "$projectPath\test_voice_integration.py"
Write-Host $testResult

# Check if test passed
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Diagnostic test failed!" -ForegroundColor Red
    Write-Host "Please fix the issues above before starting services." -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Step 3: Check Redis
Write-Host ""
Write-Host "[3/7] Checking Redis..." -ForegroundColor Yellow
$redisRunning = netstat -an | Select-String ":6379" | Select-String "LISTENING"
if ($redisRunning) {
    Write-Host "  ✓ Redis is running" -ForegroundColor Green
} else {
    Write-Host "  ✗ Redis is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Redis in a separate terminal:" -ForegroundColor Yellow
    Write-Host "  redis-server" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "If Redis is not installed:" -ForegroundColor Yellow
    Write-Host "  Download: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Cyan
    Write-Host "  Or install via Chocolatey: choco install redis-64" -ForegroundColor Cyan
    Write-Host ""
    pause
}

# Step 4: Check Ngrok
Write-Host ""
Write-Host "[4/7] Checking Ngrok..." -ForegroundColor Yellow
$ngrokRunning = Get-Process -Name ngrok -ErrorAction SilentlyContinue
if ($ngrokRunning) {
    Write-Host "  ✓ Ngrok is running" -ForegroundColor Green
    Write-Host ""
    Write-Host "  IMPORTANT: Copy your ngrok URL and update .env file!" -ForegroundColor Yellow
    Write-Host "  Look for: https://XXXX-XXX-XXX.ngrok-free.app" -ForegroundColor Cyan
    Write-Host "  Update NGROK_URL in .env with this URL" -ForegroundColor Cyan
} else {
    Write-Host "  ✗ Ngrok is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Ngrok in a separate terminal:" -ForegroundColor Yellow
    Write-Host "  ngrok http 8000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then copy the https:// URL and update NGROK_URL in .env file" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "If Ngrok is not installed:" -ForegroundColor Yellow
    Write-Host "  Download: https://ngrok.com/download" -ForegroundColor Cyan
    Write-Host "  Setup: https://dashboard.ngrok.com/get-started/setup" -ForegroundColor Cyan
    Write-Host ""
    pause
}

# Step 5: Offer to start Daphne
Write-Host ""
Write-Host "[5/7] Starting Daphne (Django ASGI Server)..." -ForegroundColor Yellow
Write-Host "  This will start the web server on port 8000" -ForegroundColor Gray

$choice = Read-Host "Start Daphne in a new window? (Y/n)"
if ($choice -ne "n" -and $choice -ne "N") {
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; .\venv\Scripts\Activate.ps1; Write-Host 'Starting Daphne server...' -ForegroundColor Green; python -m daphne -b 0.0.0.0 -p 8000 perplex.asgi:application"
    Write-Host "  ✓ Daphne starting in new window..." -ForegroundColor Green
    Start-Sleep -Seconds 3
} else {
    Write-Host "  ⊘ Skipped - Start manually:" -ForegroundColor Yellow
    Write-Host "    python -m daphne -b 0.0.0.0 -p 8000 perplex.asgi:application" -ForegroundColor Cyan
}

# Step 6: Offer to start Celery Worker
Write-Host ""
Write-Host "[6/7] Starting Celery Worker..." -ForegroundColor Yellow
Write-Host "  This handles background tasks" -ForegroundColor Gray

$choice = Read-Host "Start Celery Worker in a new window? (Y/n)"
if ($choice -ne "n" -and $choice -ne "N") {
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; .\venv\Scripts\Activate.ps1; Write-Host 'Starting Celery Worker...' -ForegroundColor Green; celery -A perplex worker -l info -P solo"
    Write-Host "  ✓ Celery Worker starting in new window..." -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "  ⊘ Skipped - Start manually:" -ForegroundColor Yellow
    Write-Host "    celery -A perplex worker -l info -P solo" -ForegroundColor Cyan
}

# Step 7: Offer to start Celery Beat
Write-Host ""
Write-Host "[7/7] Starting Celery Beat..." -ForegroundColor Yellow
Write-Host "  This schedules periodic calls" -ForegroundColor Gray

$choice = Read-Host "Start Celery Beat in a new window? (Y/n)"
if ($choice -ne "n" -and $choice -ne "N") {
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; .\venv\Scripts\Activate.ps1; Write-Host 'Starting Celery Beat...' -ForegroundColor Green; celery -A perplex beat -l info"
    Write-Host "  ✓ Celery Beat starting in new window..." -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "  ⊘ Skipped - Start manually:" -ForegroundColor Yellow
    Write-Host "    celery -A perplex beat -l info" -ForegroundColor Cyan
}

# Final summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✓ Startup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Make sure Redis is running (check terminal)" -ForegroundColor White
Write-Host "  2. Make sure Ngrok is running and NGROK_URL is updated in .env" -ForegroundColor White
Write-Host "  3. Wait for Daphne to show: 'Listening on TCP address 0.0.0.0:8000'" -ForegroundColor White
Write-Host "  4. Wait for Celery Worker to show: 'celery@... ready'" -ForegroundColor White
Write-Host "  5. Wait for Celery Beat to show: 'Scheduler: Starting...'" -ForegroundColor White
Write-Host ""
Write-Host "Then visit: http://localhost:8000/voice/schedule/" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop all services:" -ForegroundColor Yellow
Write-Host "  Close each terminal window (Ctrl+C then close)" -ForegroundColor White
Write-Host ""
Write-Host "For troubleshooting, see: START_VOICE_CALLS.md" -ForegroundColor Gray
Write-Host ""

# Keep window open
pause
