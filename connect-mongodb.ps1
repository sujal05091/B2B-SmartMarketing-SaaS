# Quick MongoDB Connection Setup
Write-Host "`n🔗 MongoDB Atlas Connection Setup" -ForegroundColor Green
Write-Host "=================================`n" -ForegroundColor Green

Write-Host "📋 In MongoDB Atlas browser:" -ForegroundColor Cyan
Write-Host "1. Click 'Connect' on Cluster0" -ForegroundColor White
Write-Host "2. Choose 'Drivers'" -ForegroundColor White
Write-Host "3. Select Python 3.6+" -ForegroundColor White
Write-Host "4. Copy connection string" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Replace <password> and add /leadgen_db" -ForegroundColor Yellow
Write-Host "Example:" -ForegroundColor Gray
Write-Host "mongodb+srv://user:pass@cluster0.xxx.mongodb.net/leadgen_db?retryWrites=true&w=majority" -ForegroundColor Cyan
Write-Host ""

$connectionString = Read-Host "Paste your connection string here"

if ([string]::IsNullOrWhiteSpace($connectionString)) {
    Write-Host "`n❌ No connection string provided!" -ForegroundColor Red
    exit 1
}

if (-not ($connectionString -match "mongodb")) {
    Write-Host "❌ Invalid connection string!" -ForegroundColor Red
    exit 1
}

if (-not ($connectionString -match "/leadgen_db")) {
    Write-Host "`n⚠️  Adding /leadgen_db to connection string..." -ForegroundColor Yellow
    if ($connectionString -match "\?") {
        $connectionString = $connectionString -replace "\?", "/leadgen_db?"
        Write-Host "✅ Added /leadgen_db" -ForegroundColor Green
    }
}

Write-Host "`n🔄 Updating configuration..." -ForegroundColor Yellow

$envPath = "backend\.env.production"
if (Test-Path $envPath) {
    $content = Get-Content $envPath -Raw
    $content = $content -replace "MONGODB_URL=.*", "MONGODB_URL=$connectionString"
    Set-Content -Path $envPath -Value $content -NoNewline
    Write-Host "✅ Updated $envPath" -ForegroundColor Green
}

Copy-Item "backend\.env.production" "backend\.env" -Force
Write-Host "✅ Created backend\.env" -ForegroundColor Green

Write-Host "`n✅ Configuration complete!" -ForegroundColor Green
Write-Host "`nStart backend? (Y/N): " -ForegroundColor Cyan -NoNewline
$start = Read-Host

if ($start -eq "Y" -or $start -eq "y") {
    Write-Host "`n🚀 Starting backend...`n" -ForegroundColor Green
    Set-Location "backend"
    uvicorn main:app --reload --port 8000
} else {
    Write-Host "`n✅ Done! Start manually:" -ForegroundColor Green
    Write-Host "cd backend" -ForegroundColor White
    Write-Host "uvicorn main:app --reload --port 8000" -ForegroundColor White
}
