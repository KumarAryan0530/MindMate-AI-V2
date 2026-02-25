# Start Redis Server (Portable - No Admin Required)
# This script starts Redis in the background

$redisPath = "$env:USERPROFILE\redis\redis-server.exe"

# Check if Redis is already running
$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue

if ($redisProcess) {
    Write-Host "[OK] Redis is already running (PID: $($redisProcess.Id))" -ForegroundColor  Green
} else {
    # Start Redis in the background
    Start-Process -FilePath $redisPath -WindowStyle Minimized
    Start-Sleep -Seconds 2
    
    # Verify it started
    $redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
    if ($redisProcess) {
        Write-Host "[OK] Redis started successfully on port 6379 (PID: $($redisProcess.Id))" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to start Redis" -ForegroundColor Red
        exit 1
    }
}

# Test connection
$testResult = & "$env:USERPROFILE\redis\redis-cli.exe" ping 2>$null
if ($testResult -eq "PONG") {
    Write-Host "[OK] Redis connection test: PASSED" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Redis connection test: FAILED" -ForegroundColor Red
}
