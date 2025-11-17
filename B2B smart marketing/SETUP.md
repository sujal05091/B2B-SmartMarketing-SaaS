# 🚀 Quick Start Guide - Smart Marketing Assistant

## 📋 Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (optional)
- Google Cloud account (for Sheets/Drive integration)
- OpenAI API key OR Ollama installed locally

## 🔧 Installation Steps

### 1. Set Up Virtual Environment

```powershell
# Navigate to project directory
cd "d:\project by sujal\B2B smart marketing"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
```

### 2. Install Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Configure Environment Variables

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env with your favorite text editor
notepad .env
```

**Required Configuration in `.env`:**

```ini
# AI Configuration (choose one)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# OR use local LLaMA
# USE_OLLAMA=true
# OLLAMA_MODEL=llama2

# Search API (at least one required)
SERPAPI_KEY=your-serpapi-key-here

# Google Sheets
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id-here
GOOGLE_SHEETS_CREDENTIALS_FILE=config/google_credentials.json
```

### 4. Set Up Google Sheets API

1. **Create Google Cloud Project:**
   - Go to https://console.cloud.google.com/
   - Create a new project

2. **Enable APIs:**
   - Enable "Google Sheets API"
   - Enable "Google Drive API" (for bonus features)

3. **Create Service Account:**
   - Go to "IAM & Admin" > "Service Accounts"
   - Create a new service account
   - Download JSON credentials
   - Save as `config/google_credentials.json`

4. **Create Google Sheet:**
   - Create a new Google Sheet
   - Copy the spreadsheet ID from URL:
     `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`
   - Share the sheet with your service account email
     (found in the credentials JSON: `client_email`)

### 5. Get API Keys

**OpenAI (Option 1 - Recommended):**
- Sign up at https://platform.openai.com/
- Create API key at https://platform.openai.com/api-keys
- Free trial: $5 credit

**Ollama (Option 2 - Free Local AI):**
```powershell
# Install Ollama from https://ollama.ai/
# Then pull a model:
ollama pull llama2
```

**SerpAPI (Required for Search):**
- Sign up at https://serpapi.com/
- Free tier: 100 searches/month
- Get API key from dashboard

**Hunter.io & Snov.io (Optional - for email discovery):**
- Hunter.io: https://hunter.io/ (50 searches/month free)
- Snov.io: https://snov.io/ (50 credits/month free)

## ✅ Verify Installation

```powershell
# Validate configuration
python cli.py --validate

# View help
python cli.py --help
```

## 🎯 First Run

### Basic Example

```powershell
python cli.py --name "AdVision Marketing" --desc "Digital Marketing & SEO Agency" --url "https://advision.com"
```

### Advanced Example

```powershell
python cli.py --name "TechCorp Solutions" --desc "Enterprise Software Development & Cloud Solutions" --url "https://techcorp.com" --max-leads 20 --region "North America" --industry "Technology"
```

## 📊 Expected Output

```
====================================================================
 🚀 SMART MARKETING ASSISTANT
====================================================================
Business: AdVision Marketing
Target Leads: 10
====================================================================

📊 Analyzing your business website...
✅ Found 5 services

🔍 Discovering potential leads (max: 10)...
✅ Discovered 10 potential leads

🚀 Processing leads...

[1/10] Processing: Example Company
  📄 Analyzing website...
  🎯 Matching services...
  ✉️  Generating personalized email...
  📁 Creating PDF portfolio...
  📊 Updating Google Sheets...
  ✅ Added to Google Sheets

...

====================================================================
 📊 EXECUTION SUMMARY
====================================================================
Total Leads Discovered: 10
Successfully Processed: 10
Emails Generated: 10
Portfolios Created: 10
Duplicates Skipped: 0
Errors: 0
====================================================================

✅ Workflow completed successfully!
📁 Portfolios saved to: output/portfolios
📊 Data recorded in Google Sheets
📝 Logs available at: logs/activity.log
```

## 📁 Output Files

After running, you'll find:

```
B2B smart marketing/
├── output/
│   └── portfolios/
│       ├── Portfolio_CompanyA_20250125_143022.pdf
│       ├── Portfolio_CompanyB_20250125_143145.pdf
│       └── ...
├── logs/
│   ├── activity.log       # Detailed execution logs
│   └── analytics.json     # Analytics data
└── [Your Google Sheet will be updated with all lead data]
```

## 🔍 View Analytics

```powershell
# View analytics dashboard
python cli.py --analytics
```

Output:
```
============================================================
 📊 ANALYTICS SUMMARY
============================================================
Total Runs: 3
Total Leads Discovered: 28
Total Emails Generated: 28
Total Portfolios Created: 28
Duplicates Prevented: 2
Average Leads per Run: 9.33
Success Rate: 100.0%

Unique Industries: 5

Top Industries:
  • Technology: 12 leads
  • Marketing: 8 leads
  • Healthcare: 5 leads
  • Finance: 2 leads
  • Education: 1 leads

Last Run:
  • Date: 2025-01-25T14:30:22
  • Business: AdVision Marketing
  • Leads: 10
  • Status: ✅ Success
============================================================
```

## 🐛 Troubleshooting

### Issue: "Configuration Error: Missing required settings"
**Solution:** Check your `.env` file has all required keys

### Issue: "Failed to initialize Google Sheets service"
**Solution:** 
- Verify `config/google_credentials.json` exists
- Check service account email has access to spreadsheet
- Verify APIs are enabled in Google Cloud

### Issue: "No leads found"
**Solution:**
- Check your search API key is valid
- Try different search terms (adjust business description)
- Increase `--max-leads` parameter

### Issue: Import errors when running
**Solution:**
```powershell
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## 📚 Next Steps

1. **Customize Portfolio Styling:**
   - Edit `config/portfolio_styles.json`
   - Add your company logo

2. **Enable Email Sending (Bonus):**
   - Configure SMTP settings in `.env`
   - Uncomment email-related configuration

3. **Set Up Scheduling (Bonus):**
   ```powershell
   python cli.py --schedule weekly
   ```

4. **Upload to Google Drive (Bonus):**
   - Configure `GOOGLE_DRIVE_FOLDER_ID` in `.env`

## 💡 Tips

- Start with `--max-leads 5` for testing
- Check `logs/activity.log` for detailed information
- Use `--validate` before each run to verify configuration
- Review generated portfolios in `output/portfolios/`
- Monitor your API usage to stay within free tier limits

## 📞 Support

- Check logs: `logs/activity.log`
- Review documentation: `README.md`
- Verify configuration: `python cli.py --validate`

## 🎉 You're Ready!

Your Smart Marketing Assistant is now set up and ready to automate your B2B lead discovery and outreach!

Start discovering leads with:
```powershell
python cli.py --name "Your Company" --desc "Your Description" --url "https://your-website.com"
```

Happy marketing! 🚀
