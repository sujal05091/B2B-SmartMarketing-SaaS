# MongoDB Atlas Setup Guide
# ========================

Write-Host "`n🎯 MongoDB Atlas Setup - Step by Step" -ForegroundColor Green
Write-Host "======================================`n" -ForegroundColor Green

Write-Host "📋 STEP 1: Sign Up" -ForegroundColor Cyan
Write-Host "   ✓ Browser opened to: https://www.mongodb.com/cloud/atlas/register"
Write-Host "   ✓ Sign up with Google/GitHub or email"
Write-Host "   ✓ Select FREE tier (M0 Sandbox - 512 MB storage)"
Write-Host "   ✓ Choose AWS provider"
Write-Host "   ✓ Select closest region (Mumbai/Singapore for India)`n"

Write-Host "📋 STEP 2: Create Database User" -ForegroundColor Cyan
Write-Host "   ✓ After cluster is created, click 'Database Access' in left menu"
Write-Host "   ✓ Click '+ ADD NEW DATABASE USER'"
Write-Host "   ✓ Choose 'Password' authentication"
Write-Host "   ✓ Username: leadgenai"
Write-Host "   ✓ Password: (create a strong password - SAVE THIS!)"
Write-Host "   ✓ User Privileges: 'Atlas admin'"
Write-Host "   ✓ Click 'Add User'`n"

Write-Host "📋 STEP 3: Whitelist Your IP" -ForegroundColor Cyan
Write-Host "   ✓ Click 'Network Access' in left menu"
Write-Host "   ✓ Click '+ ADD IP ADDRESS'"
Write-Host "   ✓ Click 'ALLOW ACCESS FROM ANYWHERE' (for development)"
Write-Host "   ✓ Click 'Confirm'`n"

Write-Host "📋 STEP 4: Get Connection String" -ForegroundColor Cyan
Write-Host "   ✓ Click 'Database' in left menu"
Write-Host "   ✓ Click 'Connect' button on your cluster"
Write-Host "   ✓ Select 'Drivers'"
Write-Host "   ✓ Choose 'Python' and version '3.6 or later'"
Write-Host "   ✓ Copy the connection string (looks like this):"
Write-Host "     mongodb+srv://leadgenai:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority" -ForegroundColor Yellow
Write-Host "   ✓ Replace <password> with your actual password`n"

Write-Host "📋 STEP 5: Update .env File" -ForegroundColor Cyan
Write-Host "   ✓ I'll help you update the .env file next"
Write-Host "   ✓ Just paste your connection string when prompted`n"

Write-Host "🔄 When ready, press Enter to continue..." -ForegroundColor Green
$null = Read-Host
