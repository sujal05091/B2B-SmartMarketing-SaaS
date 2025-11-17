# Interactive MongoDB Atlas Connection String Updater
# ===================================================

$envFile = "d:\project by sujal\B2B smart marketing\backend\.env.production"

Write-Host "`n🔗 MongoDB Atlas Connection String Setup" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Your MongoDB Atlas connection string should look like this:" -ForegroundColor Yellow
Write-Host "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`n" -ForegroundColor Cyan

Write-Host "📋 Follow these steps to get it:" -ForegroundColor Yellow
Write-Host "1. Go to https://cloud.mongodb.com" -ForegroundColor White
Write-Host "2. Sign in to your account" -ForegroundColor White
Write-Host "3. Click 'Database' in the left sidebar" -ForegroundColor White
Write-Host "4. Click 'Connect' button on your cluster" -ForegroundColor White
Write-Host "5. Choose 'Drivers'" -ForegroundColor White
Write-Host "6. Select 'Python' and copy the connection string" -ForegroundColor White
Write-Host "7. Replace <password> with your actual password`n" -ForegroundColor White

Write-Host "⚠️  Important: Make sure to:" -ForegroundColor Red
Write-Host "   - Replace <password> with your actual password" -ForegroundColor White
Write-Host "   - Add /leadgen_db before the ? (database name)" -ForegroundColor White
Write-Host "   Example: mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/leadgen_db?retryWrites=true`n" -ForegroundColor Cyan

$connectionString = Read-Host "Paste your MongoDB Atlas connection string here"

if ([string]::IsNullOrWhiteSpace($connectionString)) {
    Write-Host "`n❌ No connection string provided. Exiting..." -ForegroundColor Red
    exit 1
}

# Validate it looks like a MongoDB connection string
if (-not ($connectionString -match "mongodb(\+srv)?://")) {
    Write-Host "`n❌ This doesn't look like a valid MongoDB connection string!" -ForegroundColor Red
    Write-Host "   It should start with 'mongodb://' or 'mongodb+srv://'" -ForegroundColor Yellow
    exit 1
}

# Add database name if not present
if (-not ($connectionString -match "/leadgen_db\?")) {
    if ($connectionString -match "\?") {
        $connectionString = $connectionString -replace "\?", "/leadgen_db?"
        Write-Host "`n✓ Added database name '/leadgen_db' to connection string" -ForegroundColor Green
    }
}

Write-Host "`n🔄 Updating .env.production file..." -ForegroundColor Yellow

# Read the file
$content = Get-Content $envFile -Raw

# Replace the MongoDB URL
$content = $content -replace "MONGODB_URL=.*", "MONGODB_URL=$connectionString"

# Write back
Set-Content -Path $envFile -Value $content -NoNewline

Write-Host "✅ MongoDB connection string updated successfully!`n" -ForegroundColor Green

Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Rename .env.production to .env:" -ForegroundColor White
Write-Host "   Copy-Item 'backend\.env.production' 'backend\.env' -Force`n" -ForegroundColor Yellow

Write-Host "2. Start the backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Yellow
Write-Host "   uvicorn main:app --reload --port 8000`n" -ForegroundColor Yellow

Write-Host "3. Access API docs:" -ForegroundColor White
Write-Host "   http://localhost:8000/docs`n" -ForegroundColor Cyan

Write-Host "Would you like me to start the backend now? (Y/N): " -ForegroundColor Green -NoNewline
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    # Copy .env file
    Copy-Item "$envFile" "d:\project by sujal\B2B smart marketing\backend\.env" -Force
    Write-Host "`n✅ Copied .env.production to .env" -ForegroundColor Green
    
    Write-Host "`n🚀 Starting backend server..." -ForegroundColor Green
    Write-Host "   Press Ctrl+C to stop the server`n" -ForegroundColor Yellow
    
    Set-Location "d:\project by sujal\B2B smart marketing\backend"
    uvicorn main:app --reload --port 8000
} else {
    Write-Host "`n✅ Configuration complete! Start the server manually when ready." -ForegroundColor Green
}
