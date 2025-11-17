# Stop all LeadGen AI services

Write-Host "🛑 Stopping LeadGen AI Platform..." -ForegroundColor Red
Write-Host "==================================`n" -ForegroundColor Red

$projectRoot = "d:\project by sujal\B2B smart marketing"

# Stop Docker containers
Write-Host "Stopping Docker containers..." -ForegroundColor Yellow
Set-Location $projectRoot
docker-compose down
Write-Host "✅ Docker containers stopped!`n" -ForegroundColor Green

# Kill processes on specific ports
function Stop-ProcessOnPort {
    param([int]$Port)
    
    $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
    
    if ($processes) {
        foreach ($pid in $processes) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "  Stopped process on port $Port (PID: $pid)" -ForegroundColor Yellow
        }
    }
}

Write-Host "Stopping services on ports..." -ForegroundColor Yellow
Stop-ProcessOnPort -Port 3000  # Frontend
Stop-ProcessOnPort -Port 8000  # Backend
Stop-ProcessOnPort -Port 11434 # Ollama

Write-Host "`n✅ All services stopped!" -ForegroundColor Green
