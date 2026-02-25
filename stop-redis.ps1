# Stop Redis Server
# This script stops the Redis server process

$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue

if ($redisProcess) {
    Write-Host "Stopping Redis (PID: $($redisProcess.Id))..." -ForegroundColor Yellow
    Stop-Process -Name "redis-server" -Force
    Start-Sleep -Seconds 1
    Write-Host "[OK] Redis stopped successfully" -ForegroundColor Green
} else {
    Write-Host "Redis is not running" -ForegroundColor Yellow
}
