# LeadGen AI - Quick Setup Script for Windows

Write-Host "🚀 LeadGen AI - SaaS Platform Setup" -ForegroundColor Green
Write-Host "====================================`n" -ForegroundColor Green

$projectRoot = "d:\project by sujal\B2B smart marketing"

# Check if Python is installed
Write-Host "✓ Checking Python installation..." -ForegroundColor Yellow
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCheck) {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
Write-Host "`n✓ Checking Node.js installation..." -ForegroundColor Yellow
$nodeCheck = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCheck) {
    $nodeVersion = node --version 2>&1
    Write-Host "  Found: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Node.js not found! Please install Node.js 20+" -ForegroundColor Red
    exit 1
}

# Install backend dependencies
Write-Host "`n✓ Installing backend dependencies..." -ForegroundColor Yellow
Set-Location "$projectRoot\backend"
pip install -r requirements-web.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Backend dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "  ❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host "`n✓ Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Frontend dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "  ❌ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
Write-Host "`n✓ Checking Docker..." -ForegroundColor Yellow
$dockerCheck = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCheck) {
    docker ps 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Docker is running!" -ForegroundColor Green
        
        # Start MongoDB and Redis
        Write-Host "`n✓ Starting MongoDB and Redis..." -ForegroundColor Yellow
        Set-Location $projectRoot
        docker-compose up -d mongodb redis
        Start-Sleep -Seconds 5
        Write-Host "  ✅ MongoDB and Redis started!" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Docker not running. Please start Docker Desktop." -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️  Docker not installed. Please install Docker Desktop." -ForegroundColor Yellow
    Write-Host "     Or install MongoDB and Redis manually." -ForegroundColor Cyan
}

# Final instructions
Write-Host "`n" -NoNewline
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "==================`n" -ForegroundColor Green

Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Start Ollama (for AI):" -ForegroundColor Yellow
Write-Host "   ollama serve`n" -ForegroundColor White

Write-Host "2️⃣  Start Backend (Terminal 1):" -ForegroundColor Yellow
Write-Host "   cd '$projectRoot\backend'" -ForegroundColor White
Write-Host "   uvicorn main:app --reload --port 8000`n" -ForegroundColor White

Write-Host "3️⃣  Start Frontend (Terminal 2):" -ForegroundColor Yellow
Write-Host "   cd '$projectRoot\frontend'" -ForegroundColor White
Write-Host "   npm run dev`n" -ForegroundColor White

Write-Host "4️⃣  Access the app:" -ForegroundColor Yellow
Write-Host "   Frontend:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:   " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs`n" -ForegroundColor Cyan

Write-Host "📖 Read SAAS_SETUP_README.md for detailed instructions!`n" -ForegroundColor Green

Set-Location $projectRoot
