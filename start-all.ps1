# Start all services for LeadGen AI SaaS Platform

Write-Host "🚀 Starting LeadGen AI Platform..." -ForegroundColor Green
Write-Host "==================================`n" -ForegroundColor Green

$projectRoot = "d:\project by sujal\B2B smart marketing"

# Function to start a process in a new window
function Start-InNewWindow {
    param(
        [string]$Title,
        [string]$Command,
        [string]$WorkingDirectory
    )
    
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.Arguments = "-NoExit -Command `"cd '$WorkingDirectory'; Write-Host '$Title' -ForegroundColor Green; $Command`""
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Normal
    
    [System.Diagnostics.Process]::Start($psi) | Out-Null
}

# Start Docker services
Write-Host "1️⃣  Starting MongoDB and Redis..." -ForegroundColor Yellow
Set-Location $projectRoot
docker-compose up -d mongodb redis
Start-Sleep -Seconds 3
Write-Host "   ✅ Database services started!`n" -ForegroundColor Green

# Start Ollama
Write-Host "2️⃣  Starting Ollama (AI Service)..." -ForegroundColor Yellow
Start-InNewWindow -Title "🤖 Ollama AI Service" -Command "ollama serve" -WorkingDirectory $projectRoot
Start-Sleep -Seconds 2
Write-Host "   ✅ Ollama started in new window!`n" -ForegroundColor Green

# Start Backend
Write-Host "3️⃣  Starting Backend API..." -ForegroundColor Yellow
Start-InNewWindow -Title "🔧 FastAPI Backend" -Command "uvicorn main:app --reload --port 8000" -WorkingDirectory "$projectRoot\backend"
Start-Sleep -Seconds 2
Write-Host "   ✅ Backend started in new window!`n" -ForegroundColor Green

# Start Frontend
Write-Host "4️⃣  Starting Frontend..." -ForegroundColor Yellow
Start-InNewWindow -Title "🎨 Next.js Frontend" -Command "npm run dev" -WorkingDirectory "$projectRoot\frontend"
Start-Sleep -Seconds 2
Write-Host "   ✅ Frontend started in new window!`n" -ForegroundColor Green

Write-Host "🎉 All services started!" -ForegroundColor Green
Write-Host "========================`n" -ForegroundColor Green

Write-Host "📱 Access your app:" -ForegroundColor Cyan
Write-Host "   Frontend:  " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Green
Write-Host "   Backend:   " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Green
Write-Host "   API Docs:  " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Green

Write-Host "`n⚡ 4 PowerShell windows opened:" -ForegroundColor Yellow
Write-Host "   - Ollama (AI Service)" -ForegroundColor White
Write-Host "   - Backend (FastAPI)" -ForegroundColor White
Write-Host "   - Frontend (Next.js)" -ForegroundColor White
Write-Host "   - This window`n" -ForegroundColor White

Write-Host "Press Ctrl+C in each window to stop services`n" -ForegroundColor Cyan
