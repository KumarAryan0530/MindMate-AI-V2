# SafeMind-AI Voice Calls - Start All Services
# Run this in PowerShell

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "SafeMind-AI Voice Calls Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "E:\all-projects\SafeMind-AI\venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Virtual environment found" -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path "E:\all-projects\SafeMind-AI\.env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create .env file with required variables" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Cyan
Write-Host "Please start these in SEPARATE terminal windows:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. NGROK (Required for webhooks):" -ForegroundColor Magenta
Write-Host "   ngrok http 8000" -ForegroundColor White
Write-Host "   Copy the HTTPS URL and add to .env as NGROK_URL" -ForegroundColor Gray
Write-Host ""

Write-Host "2. REDIS (Required for Celery & Channels):" -ForegroundColor Magenta
Write-Host "   redis-server" -ForegroundColor White
Write-Host ""

Write-Host "3. DAPHNE Server (Required for WebSockets):" -ForegroundColor Magenta
Write-Host "   cd E:\all-projects\SafeMind-AI" -ForegroundColor White
Write-Host "   E:\all-projects\SafeMind-AI\venv\Scripts\python.exe -m daphne -b 0.0.0.0 -p 8000 perplex.asgi:application" -ForegroundColor White
Write-Host ""

Write-Host "4. CELERY Worker (Required for call processing):" -ForegroundColor Magenta
Write-Host "   cd E:\all-projects\SafeMind-AI" -ForegroundColor White
Write-Host "   E:\all-projects\SafeMind-AI\venv\Scripts\celery.exe -A perplex worker -l info -P solo" -ForegroundColor White
Write-Host ""

Write-Host "5. CELERY Beat (Required for scheduled calls):" -ForegroundColor Magenta
Write-Host "   cd E:\all-projects\SafeMind-AI" -ForegroundColor White
Write-Host "   E:\all-projects\SafeMind-AI\venv\Scripts\celery.exe -A perplex beat -l info" -ForegroundColor White
Write-Host ""

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Quick Troubleshooting Checklist" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[ ] All 5 services are running" -ForegroundColor White
Write-Host "[ ] NGROK_URL is set in .env file" -ForegroundColor White
Write-Host "[ ] TWILIO_ACCOUNT_SID is set in .env" -ForegroundColor White
Write-Host "[ ] TWILIO_AUTH_TOKEN is set in .env" -ForegroundColor White
Write-Host "[ ] TWILIO_PHONE_NUMBER is set in .env" -ForegroundColor White
Write-Host "[ ] ELEVENLABS_API_KEY is set in .env" -ForegroundColor White
Write-Host "[ ] ELEVENLABS_AGENT_ID is set in .env" -ForegroundColor White
Write-Host "[ ] Phone number verified in Twilio Console" -ForegroundColor White
Write-Host ""

Write-Host "For detailed troubleshooting, see:" -ForegroundColor Yellow
Write-Host "  TWILIO_TRIAL_ACCOUNT_FIX.md" -ForegroundColor White
Write-Host ""

# Offer to create a quick start batch file
$createBatch = Read-Host "Would you like to create quick-start batch files? (y/n)"

if ($createBatch -eq 'y' -or $createBatch -eq 'Y') {
    # Create batch files for each service
    
    # 1. Daphne Server
    @"
@echo off
cd /d E:\all-projects\SafeMind-AI
echo Starting Daphne Server...
E:\all-projects\SafeMind-AI\venv\Scripts\python.exe -m daphne -b 0.0.0.0 -p 8000 perplex.asgi:application
pause
"@ | Out-File -FilePath "E:\all-projects\SafeMind-AI\start-daphne.bat" -Encoding ASCII
    
    # 2. Celery Worker
    @"
@echo off
cd /d E:\all-projects\SafeMind-AI
echo Starting Celery Worker...
E:\all-projects\SafeMind-AI\venv\Scripts\celery.exe -A perplex worker -l info -P solo
pause
"@ | Out-File -FilePath "E:\all-projects\SafeMind-AI\start-celery-worker.bat" -Encoding ASCII
    
    # 3. Celery Beat
    @"
@echo off
cd /d E:\all-projects\SafeMind-AI
echo Starting Celery Beat...
E:\all-projects\SafeMind-AI\venv\Scripts\celery.exe -A perplex beat -l info
pause
"@ | Out-File -FilePath "E:\all-projects\SafeMind-AI\start-celery-beat.bat" -Encoding ASCII
    
    Write-Host ""
    Write-Host "✓ Batch files created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick start files created:" -ForegroundColor Cyan
    Write-Host "  - start-daphne.bat" -ForegroundColor White
    Write-Host "  - start-celery-worker.bat" -ForegroundColor White
    Write-Host "  - start-celery-beat.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "Double-click these files to start each service!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete! Start the services and test your voice calls." -ForegroundColor Green
Write-Host ""
