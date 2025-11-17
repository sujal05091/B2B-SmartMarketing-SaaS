# 🎯 B2B Smart Marketing - Quick Reference

## 🌐 Servers

```
Backend:  http://localhost:8000
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
```

## 🗂️ Project Structure

```
B2B smart marketing/
├── backend/
│   ├── main.py                          # FastAPI app entry point
│   ├── models/
│   │   ├── user.py                      # User model with AI & Sheets config
│   │   ├── lead.py                      # Lead model
│   │   └── task.py                      # Task tracking model
│   ├── services/
│   │   ├── search_service.py            # 🆕 SerpAPI + Hunter.io integration
│   │   ├── ai_service.py                # 🆕 Ollama + OpenAI email generation
│   │   ├── google_sheets_service.py     # 🆕 Google Sheets auto-export
│   │   ├── email_service.py             # SMTP email sending
│   │   └── lead_discovery_service.py    # 🔄 Rewritten - orchestrates all APIs
│   ├── api/
│   │   ├── auth.py                      # JWT authentication
│   │   ├── settings.py                  # 🔄 Enhanced - AI & Sheets endpoints
│   │   ├── leads.py                     # Lead management
│   │   └── emails.py                    # Email sending
│   └── core/
│       ├── database.py                  # MongoDB + Beanie
│       └── security.py                  # Password hashing, JWT
│
└── frontend/
    └── app/
        └── dashboard/
            ├── settings/page.tsx        # 🔄 Complete redesign - AI toggle, Sheets config
            ├── discover/page.tsx        # Lead discovery form
            └── leads/page.tsx           # Lead list with email sending
```

## 🔑 New Features Added (Steps 3 & 4)

### Backend Services

#### 1. SearchService (`services/search_service.py`)
```python
# Find businesses using Google search
businesses = await SearchService.search_businesses(user, industry, location, limit)

# Find email for a domain
email = await SearchService.find_email(user, domain, company_name)
```

**APIs Used**:
- SerpAPI: Google organic + local results (businesses)
- Hunter.io: Domain email search

#### 2. AIService (`services/ai_service.py`)
```python
# Generate personalized email
email_data = await AIService.generate_email(user, company_name, industry, description)
# Returns: {"subject": "...", "body": "..."}
```

**Providers**:
- Ollama: Local, free, customizable model (llama2, mistral, codellama)
- OpenAI: Cloud, GPT-3.5-turbo, requires API key

#### 3. GoogleSheetsService (`services/google_sheets_service.py`)
```python
# Create or get existing sheet
sheet_id = await GoogleSheetsService.create_or_get_sheet(user, sheet_name)

# Export leads to sheet
result = await GoogleSheetsService.export_leads(user, leads)
# Returns: {"sheet_url": "...", "leads_exported": 10}
```

**Features**:
- Auto-creates sheet with formatted headers
- Appends new leads
- Returns shareable URL

### User Model Fields

```python
# AI Configuration
ai_provider: str = "ollama"              # "ollama" or "openai"
openai_api_key: Optional[str] = None     # sk-...
ollama_base_url: str = "http://localhost:11434"
ollama_model: str = "llama2"             # llama2, mistral, codellama

# Google Sheets
google_sheets_enabled: bool = False
google_sheets_credentials: Optional[str] = None  # Service account JSON
google_sheet_id: Optional[str] = None    # Optional, auto-created if empty
```

### Settings API Endpoints

```python
# Get all settings (returns masked secrets)
GET /api/settings/

# Update API keys + AI config
PUT /api/settings/api-keys
{
  "serpapi_key": "...",
  "hunter_api_key": "...",
  "ai_provider": "ollama",           # or "openai"
  "ollama_base_url": "...",
  "ollama_model": "llama2",
  "openai_api_key": "sk-..."
}

# Update Google Sheets config
PUT /api/settings/google-sheets
{
  "google_sheets_enabled": true,
  "google_sheets_credentials": "{...}",  # Service account JSON
  "google_sheet_id": "..."               # Optional
}
```

## 🎨 Frontend Updates

### Settings Page New Sections

#### 1. AI Provider Selection
```tsx
// Visual toggle between Ollama and OpenAI
<button>🦙 Ollama (Local) - Free, runs on your machine</button>
<button>🤖 OpenAI - Cloud-based, requires API key</button>

// Conditional rendering based on selection
{aiProvider === 'ollama' ? (
  // Ollama config: URL + Model inputs
) : (
  // OpenAI config: API key input
)}
```

#### 2. Google Sheets Integration
```tsx
// Enable checkbox
<input type="checkbox" checked={googleSheetsEnabled} />

// Service account credentials
<textarea placeholder='{"type": "service_account", ...}' />

// Optional sheet ID
<input placeholder="Leave empty to create new sheet" />

// Dedicated save button
<Button onClick={saveGoogleSheets}>Save Google Sheets Settings</Button>
```

## 🔄 Lead Discovery Flow

### Old Flow (CLI Wrapper)
```
User submits → Call CLI module → Return fake data
```

### New Flow (Real APIs)
```
1. Check SerpAPI configured?
   ├─ NO → Create demo leads with AI-generated emails
   └─ YES → Continue to step 2

2. Search businesses using SerpAPI
   - Searches Google for "{industry} in {region}"
   - Extracts company names, websites, descriptions

3. For each business:
   a. Find email (Hunter.io) if configured
   b. Generate personalized email (AI)
      - Ollama: http://localhost:11434/api/generate
      - OpenAI: https://api.openai.com/v1/chat/completions
   c. Save lead to MongoDB

4. Auto-export to Google Sheets if enabled
   - Creates/gets sheet
   - Appends all leads
   - Returns sheet URL

5. Update task status + usage tracking
```

## 📋 Testing Checklist

### Basic Tests (No API Keys Required)
- [ ] Settings page loads
- [ ] AI provider toggle works (Ollama ↔ OpenAI)
- [ ] Save buttons enable/disable correctly
- [ ] Discover leads with no API keys → Creates demo leads

### Ollama Tests (Free)
- [ ] Install Ollama
- [ ] Pull llama2 model
- [ ] Configure in Settings
- [ ] Discover leads → AI-generated emails

### Full Integration Tests (Requires API Keys)
- [ ] Add SerpAPI key → Real business search
- [ ] Add Hunter.io key → Email discovery
- [ ] Add OpenAI key → Cloud AI emails
- [ ] Configure Google Sheets → Auto-export

### Email Tests (Optional)
- [ ] Configure SMTP (Gmail)
- [ ] Send test email
- [ ] Lead status updates

## 🚀 Quick Start Commands

### Start Backend
```powershell
cd "D:\project by sujal\B2B smart marketing\backend"
python -m uvicorn main:app --reload --port 8000
```

### Start Frontend
```powershell
cd "D:\project by sujal\B2B smart marketing\frontend"
npm run dev
```

### Install Ollama
```powershell
# Download from https://ollama.ai
# Then pull a model:
ollama pull llama2
```

### Test Ollama
```powershell
# Should respond with "Ollama is running"
curl http://localhost:11434
```

## 🔐 API Keys You'll Need

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| SerpAPI | Google search | 100/month | https://serpapi.com/users/sign_up |
| Hunter.io | Email finder | 50/month | https://hunter.io/users/sign_up |
| OpenAI | AI emails (optional) | $5 credit | https://platform.openai.com/api-keys |
| Google Cloud | Sheets export | Free | https://console.cloud.google.com |

## 💰 Cost Breakdown

### Free Option (Ollama + Demo Leads)
- **Cost**: $0/month
- **Features**: AI email generation, demo lead creation
- **Best For**: Testing, development

### Budget Option (SerpAPI + Hunter.io + Ollama)
- **Cost**: $0/month (within free tiers)
- **Features**: Real business search, email finding, AI emails
- **Limits**: 50 leads/month (Hunter.io limit)
- **Best For**: Small projects, freelancers

### Full Option (All APIs + OpenAI)
- **Cost**: ~$10-20/month
- **Features**: Everything + cloud AI
- **Best For**: Production, agencies

## 🎓 Learning Resources

### Ollama Models
- `llama2` - General purpose, 7B params (Recommended)
- `mistral` - Fast, high quality, 7B params
- `codellama` - Code-focused, 7B params
- See all: https://ollama.ai/library

### API Documentation
- **SerpAPI**: https://serpapi.com/search-api
- **Hunter.io**: https://hunter.io/api-documentation
- **OpenAI**: https://platform.openai.com/docs/guides/text-generation
- **Google Sheets**: https://developers.google.com/sheets/api

## 🐛 Common Errors

### "Ollama is not running"
```powershell
# Start Ollama (it runs as a service)
# Just open Ollama app or run:
ollama serve
```

### "SerpAPI quota exceeded"
```
Free tier: 100 searches/month
Solution: Wait for next month or upgrade
```

### "Hunter.io limit reached"
```
Free tier: 50 searches/month
Solution: Wait for next month or upgrade
```

### "Invalid Google credentials"
```
Check: Service account JSON is valid
Check: Google Sheets API is enabled
Check: Sheet is shared with service account email
```

## ✨ Pro Tips

1. **Test Incrementally**: Add one API key at a time
2. **Use Ollama First**: It's free and doesn't require internet for AI
3. **Monitor Usage**: Check API dashboards to track free tier limits
4. **Cache Responses**: Lead data is saved, no need to re-discover
5. **Batch Processing**: Discover 5-10 leads at once for efficiency

## 📊 What to Expect

### Demo Leads (No API Keys)
- 3 fake businesses
- ✅ AI-generated emails (if Ollama/OpenAI configured)
- ❌ No real contact emails
- ⏱️ Fast (~5 seconds)

### Real Leads (With API Keys)
- Real businesses from Google
- ✅ AI-generated personalized emails
- ✅ Real contact emails (when found)
- ✅ Auto-exported to Google Sheets
- ⏱️ Slower (~30 seconds for 10 leads)

---

**Ready?** Start with the TESTING_GUIDE.md for step-by-step instructions! 🚀
