# 🔧 Troubleshooting Guide - B2B Smart Marketing

## 🐛 Common Issues and Solutions

### Issue 1: "Leads show previous leads only, new leads not appearing"

**Symptoms:**
- Click "Discover Leads" button
- Get success message
- But leads page shows old leads only
- No new leads appear

**Root Causes:**
1. Background task is running but failing silently
2. Database connection issues
3. Frontend not refreshing properly

**Solutions:**

#### Step 1: Check Backend Logs
Look at your backend terminal (where you ran `uvicorn main:app --reload`):

```
🚀 Starting lead discovery task: discover_xxx_xxx
   User ID: xxx
📊 Discovering leads for Software Companies in United States
⚠️ SerpAPI not configured, creating demo leads
Creating demo leads for testing...
   💾 Created demo lead: Demo Software Companies Company 1
   💾 Created demo lead: Sample Software Companies Business 2
✅ Created 3 demo leads for testing
🏁 Lead discovery task completed: discover_xxx_xxx
```

**If you see errors:**
- MongoDB connection error → Check MongoDB is running: `docker ps`
- User not found → Re-login to get fresh token
- Task not starting → Check FastAPI is running properly

#### Step 2: Test API Directly
Open http://localhost:8000/docs and test:

1. **Check your stats:**
   - Go to `GET /api/leads/stats`
   - Click "Try it out" → "Execute"
   - This shows total leads count and settings

2. **List leads:**
   - Go to `GET /api/leads/`
   - Set limit to 20
   - Click "Execute"
   - Check if new leads appear here

#### Step 3: Force Frontend Refresh
In your browser:
1. Press `Ctrl + Shift + R` (hard refresh)
2. Or clear browser cache
3. Or open in incognito mode

---

### Issue 2: "Emails not sent automatically"

**Important:** Emails are **NOT** sent automatically during lead discovery!

**How it actually works:**
1. Lead discovery creates leads with **email content** (subject + body)
2. You must **manually send** emails from the leads page
3. Click "Send Email" button on each lead

**To send emails:**
1. Configure SMTP in Settings first
2. Go to Leads page
3. Click "Send Email" on a lead
4. Email will be sent immediately

**Why not automatic?**
- Prevents accidental spam
- Gives you control over which leads to contact
- Allows you to review emails before sending

**Future Enhancement:**
We can add a "Send All" or "Campaign" feature to send bulk emails.

---

### Issue 3: "Google Sheets not updating"

**Symptoms:**
- Google Sheets integration enabled
- Leads discovered successfully
- But Google Sheet is empty or not updating

**Checklist:**

#### 1. Verify Settings
Go to http://localhost:3000/dashboard/settings:
- [ ] "Auto-export leads to Google Sheets" is checked
- [ ] Google credentials JSON is pasted
- [ ] Sheet ID is provided (or leave empty for auto-create)

#### 2. Check Backend Logs
Look for these messages:
```
📊 Attempting to export 3 demo leads to Google Sheets...
✅ Exported demo leads to Google Sheets: https://docs.google.com/spreadsheets/d/xxx
```

**If you see errors:**

**Error: "Google Sheets credentials not configured"**
- Solution: Paste your service account JSON in Settings

**Error: "Failed to authenticate"**
- Solution: Check JSON is valid (copy entire content from downloaded file)

**Error: "Permission denied"**
- Solution: Share the Google Sheet with the service account email
- Find email in JSON: `"client_email": "xxx@xxx.iam.gserviceaccount.com"`
- Share sheet with this email as Editor

**Error: "Spreadsheet not found"**
- Solution: Leave Sheet ID empty to auto-create
- Or verify the Sheet ID is correct

#### 3. Test Manually
1. Go to http://localhost:8000/docs
2. Find `PUT /api/settings/google-sheets`
3. Test with your credentials
4. Check response for errors

---

### Issue 4: "Background task not running"

**Check if task is actually running:**

1. Look at backend terminal immediately after clicking "Discover Leads"
2. You should see:
   ```
   🎯 DISCOVER LEADS ENDPOINT HIT!
      User: your@email.com
      Task ID: discover_xxx_xxx
      Adding background task...
      ✅ Background task added!
   ```

3. Then within 5-10 seconds:
   ```
   🚀 Starting lead discovery task: discover_xxx_xxx
   ```

**If task doesn't start:**
- FastAPI might have crashed → Restart backend
- MongoDB not connected → Check `docker ps`
- Python error → Check terminal for stack trace

---

### Issue 5: "Only seeing demo leads, not real businesses"

**This is expected if:**
- You haven't configured SerpAPI key
- SerpAPI key is invalid
- SerpAPI free tier limit exceeded (100/month)

**To get real businesses:**

1. Get SerpAPI key:
   - Sign up: https://serpapi.com/users/sign_up
   - Copy your API key
   - Free tier: 100 searches/month

2. Add to Settings:
   - Go to http://localhost:3000/dashboard/settings
   - Paste SerpAPI key
   - Save settings

3. Test again:
   - Discover leads
   - Check backend logs for: `🔍 Searching Google: Software Companies in United States`

**Backend logs will show:**
```
✅ Found 10 businesses
   ✓ Found: Microsoft Corporation
   ✓ Found: Google LLC
   ...
```

---

### Issue 6: "No emails found for leads"

**This is expected if:**
- You haven't configured Hunter.io key
- Hunter.io free tier limit exceeded (50/month)
- Website doesn't have public emails

**To find emails:**

1. Get Hunter.io key:
   - Sign up: https://hunter.io/users/sign_up
   - Copy API key
   - Free tier: 50 searches/month

2. Add to Settings:
   - Paste Hunter.io key
   - Save settings

3. Test again:
   - Backend logs will show: `🔍 Finding email for example.com`
   - If found: `✅ Found email: contact@example.com`
   - If not: `⚠️ No email found for example.com`

---

## 🔍 Debugging Steps

### Step 1: Check All Services Running

```powershell
# Check Docker containers
docker ps

# Should show:
# - mongodb
# - redis (optional)

# Check Ollama (if using)
curl http://localhost:11434
# Should return: "Ollama is running"

# Check Backend
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Check Frontend
# Open: http://localhost:3000
```

### Step 2: Check Database Connection

```powershell
# In backend terminal, look for:
✅ Connected to MongoDB successfully!
✅ Beanie initialized successfully!

# If you see warnings:
⚠️  MongoDB connection failed
# Then run:
docker-compose up -d mongodb
```

### Step 3: Test Lead Discovery Flow

1. **Open 3 browser tabs:**
   - Tab 1: http://localhost:3000/dashboard/discover
   - Tab 2: http://localhost:3000/dashboard/leads
   - Tab 3: http://localhost:8000/docs (API docs)

2. **In Tab 3 (API docs):**
   - Test `GET /api/leads/stats`
   - Note the `total_leads` count

3. **In Tab 1 (Discover):**
   - Fill form and click "Discover Leads"
   - Watch backend terminal for logs

4. **Wait 10 seconds, then Tab 2 (Leads):**
   - Refresh page (F5)
   - Check if new leads appear

5. **In Tab 3 (API docs):**
   - Test `GET /api/leads/stats` again
   - `total_leads` should have increased

### Step 4: Check User Settings

Go to http://localhost:8000/docs:
- Test `GET /api/settings/`
- Verify your API keys are saved (they'll be masked like `sk-***`)
- Check `google_sheets_enabled` is true if you want exports

---

## 📊 Understanding the Flow

### Lead Discovery Flow:
```
1. User clicks "Discover Leads"
   ↓
2. Frontend sends POST /api/leads/discover
   ↓
3. Backend creates background task
   ↓
4. Task runs (5-30 seconds):
   - Search businesses (SerpAPI or demo)
   - Find emails (Hunter.io if configured)
   - Generate email content (AI)
   - Save to MongoDB
   - Export to Google Sheets (if enabled)
   ↓
5. Task completes
   ↓
6. Frontend refreshes leads list
```

### Email Sending Flow:
```
1. User clicks "Send Email" on a lead
   ↓
2. Frontend sends POST /api/emails/send
   ↓
3. Backend validates SMTP settings
   ↓
4. Connects to SMTP server
   ↓
5. Sends email
   ↓
6. Updates lead status to "contacted"
   ↓
7. Returns success/error to frontend
```

---

## 🆘 Still Having Issues?

### Get Detailed Logs:

1. **Backend logs:**
   - Check the terminal where you ran `uvicorn`
   - All operations are logged with emojis for easy scanning

2. **Frontend logs:**
   - Open browser console (F12)
   - Check "Console" tab for errors
   - Check "Network" tab for failed API calls

3. **Database logs:**
   ```powershell
   docker-compose logs mongodb
   ```

### Test Each Component:

1. **Test MongoDB:**
   ```powershell
   docker exec -it b2b-smart-marketing-mongodb-1 mongosh
   # In mongo shell:
   use leadgen_db
   db.leads.countDocuments()
   db.leads.find().limit(5)
   ```

2. **Test Backend API:**
   - http://localhost:8000/docs
   - Try all endpoints manually

3. **Test AI (Ollama):**
   ```powershell
   curl http://localhost:11434/api/generate -d '{
     "model": "llama2",
     "prompt": "Say hello",
     "stream": false
   }'
   ```

---

## 📝 Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "MongoDB connection failed" | MongoDB not running | `docker-compose up -d mongodb` |
| "User not found" | Invalid/expired token | Re-login |
| "SerpAPI not configured" | No API key | Add in Settings or use demo mode |
| "SMTP authentication failed" | Wrong password | Use App Password for Gmail |
| "Google Sheets credentials not configured" | Missing JSON | Paste service account JSON |
| "Lead not found" | Wrong lead ID | Check lead exists in database |
| "Not authorized" | Wrong user | Lead belongs to different user |

---

## ✅ Quick Fixes

### Fix 1: Restart Everything
```powershell
# Stop all
docker-compose down
# Ctrl+C in all terminal windows

# Start fresh
docker-compose up -d mongodb redis
.\start-all.ps1
```

### Fix 2: Clear Database (CAUTION!)
```powershell
docker exec -it b2b-smart-marketing-mongodb-1 mongosh
# In mongo shell:
use leadgen_db
db.leads.deleteMany({})  # Delete all leads
db.users.deleteMany({})  # Delete all users
```

### Fix 3: Reset Frontend
```powershell
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

---

**Need more help?** Check the backend terminal logs - they're very detailed!
