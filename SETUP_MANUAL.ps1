# Simple Manual Setup Instructions

Write-Host "🚀 LeadGen AI - Manual Setup" -ForegroundColor Green
Write-Host "===========================`n" -ForegroundColor Green

Write-Host "📦 Step 1: Install Backend Dependencies" -ForegroundColor Cyan
Write-Host "cd 'd:\project by sujal\B2B smart marketing\backend'" -ForegroundColor White
Write-Host "pip install -r requirements-web.txt`n" -ForegroundColor White

Write-Host "📦 Step 2: Install Frontend Dependencies" -ForegroundColor Cyan
Write-Host "cd 'd:\project by sujal\B2B smart marketing\frontend'" -ForegroundColor White
Write-Host "npm install`n" -ForegroundColor White

Write-Host "🐳 Step 3: Start MongoDB and Redis" -ForegroundColor Cyan
Write-Host "cd 'd:\project by sujal\B2B smart marketing'" -ForegroundColor White
Write-Host "docker-compose up -d mongodb redis`n" -ForegroundColor White

Write-Host "🤖 Step 4: Start Ollama" -ForegroundColor Cyan
Write-Host "ollama serve`n" -ForegroundColor White

Write-Host "🔧 Step 5: Start Backend (new terminal)" -ForegroundColor Cyan
Write-Host "cd 'd:\project by sujal\B2B smart marketing\backend'" -ForegroundColor White
Write-Host "uvicorn main:app --reload --port 8000`n" -ForegroundColor White

Write-Host "🎨 Step 6: Start Frontend (new terminal)" -ForegroundColor Cyan
Write-Host "cd 'd:\project by sujal\B2B smart marketing\frontend'" -ForegroundColor White
Write-Host "npm run dev`n" -ForegroundColor White

Write-Host "✅ Access URLs:" -ForegroundColor Green
Write-Host "Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs:  http://localhost:8000/docs`n" -ForegroundColor Cyan
