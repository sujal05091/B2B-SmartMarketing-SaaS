# 🚀 B2B Smart Marketing SaaS

A full-stack AI-powered web application that automates B2B lead discovery, personalized outreach generation, and lead management with real-time integrations.

## 📋 Overview

This B2B Smart Marketing platform helps businesses:
- **Discover** potential clients worldwide using real APIs (SerpAPI, Hunter.io)
- **Generate** personalized outreach emails using AI (Ollama or OpenAI)
- **Manage** all leads in a beautiful dashboard with MongoDB storage
- **Export** leads automatically to Google Sheets
- **Send** personalized emails directly via SMTP

## ✨ Features

### 🎯 Core Features
- ✅ **Real Lead Discovery**: SerpAPI integration for Google business search + local results
- ✅ **Email Finding**: Hunter.io integration for domain-based email discovery
- ✅ **Dual AI Support**: Choose between free local Ollama or cloud OpenAI for email generation
- ✅ **Auto-Export**: Automatic Google Sheets integration with formatted exports
- ✅ **Email Sending**: SMTP integration for direct email outreach
- ✅ **Beautiful Dashboard**: Modern React UI with Next.js 14

### 🚀 Advanced Features
- � Real-time task tracking and progress monitoring
- 🔐 JWT authentication with secure password hashing
- 🎨 Responsive design with Tailwind CSS + shadcn/ui
- 📈 Usage tracking and analytics
- 🔄 Background task processing
- ⚡ FastAPI backend with async operations

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB Atlas with Beanie ODM
- **Authentication**: JWT tokens with bcrypt
- **AI**: Ollama (local) + OpenAI API support
- **APIs**: SerpAPI, Hunter.io, Google Sheets API

### Frontend
- **Framework**: Next.js 14.2.0 with TypeScript
- **UI Library**: React 18, shadcn/ui components
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP**: Axios for API calls

## 📦 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- MongoDB Atlas account (free tier)
- (Optional) Ollama installed for free local AI

### 1. Clone and Setup Backend
```powershell
# Clone repository
cd "D:\project by sujal\B2B smart marketing\backend"

# Install dependencies
pip install -r requirements.txt

# Create .env file with:
# MONGODB_URL=your_mongodb_atlas_connection_string
# SECRET_KEY=your_secret_key
# ALGORITHM=HS256

# Start backend server
python -m uvicorn main:app --reload --port 8000
```

### 2. Setup Frontend
```powershell
cd "D:\project by sujal\B2B smart marketing\frontend"

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Configure Settings
1. Register an account at http://localhost:3000/register
2. Go to http://localhost:3000/dashboard/settings
3. Choose your AI provider:
   - **Ollama** (Free): Install from https://ollama.ai, run `ollama pull llama2`
   - **OpenAI**: Add your API key
4. (Optional) Add SerpAPI and Hunter.io keys for real lead discovery
5. (Optional) Configure Google Sheets and SMTP

📖 **Full Setup Guide**: See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for detailed instructions

## 📚 Documentation

- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Complete testing scenarios and setup instructions
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - API reference, commands, and pro tips
- **API Documentation** - Visit http://localhost:8000/docs when backend is running

## 🔑 API Keys (Optional)

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| SerpAPI | Google search | 100 searches/month | https://serpapi.com |
| Hunter.io | Email finder | 50 searches/month | https://hunter.io |
| OpenAI | AI emails (alternative to Ollama) | $5 credit | https://platform.openai.com |
| Google Cloud | Sheets export | Free | https://console.cloud.google.com |

**Note**: You can start with **zero API keys** by using Ollama for AI and demo leads!

## 🎯 Key Features Explained

### 1. Dual AI Support
Choose between:
- **Ollama** (🦙): Free, local, private, no internet required
  - Models: llama2, mistral, codellama
  - Setup: `ollama pull llama2`
- **OpenAI** (🤖): Cloud-based, GPT-3.5-turbo
  - Cost: ~$0.002 per email
  - Faster response times

### 2. Real Lead Discovery
- Uses SerpAPI to search Google for businesses
- Extracts organic results + Google Maps local results
- Finds email addresses with Hunter.io
- Generates personalized outreach emails
- Auto-exports to Google Sheets

### 3. Smart Fallbacks
- No API keys? Creates demo leads with AI-generated emails
- No Hunter.io? Uses business info without emails
- AI fails? Uses professional template fallback

## 🚀 Project Structure

```
B2B smart marketing/
├── backend/                    # FastAPI backend
│   ├── models/                # MongoDB models (User, Lead, Task)
│   ├── services/              # Business logic
│   │   ├── search_service.py # SerpAPI + Hunter.io
│   │   ├── ai_service.py     # Ollama + OpenAI
│   │   ├── google_sheets_service.py
│   │   ├── email_service.py  # SMTP
│   │   └── lead_discovery_service.py
│   ├── api/                   # API routes
│   └── core/                  # Auth, DB, security
│
└── frontend/                   # Next.js frontend
    └── app/
        └── dashboard/
            ├── settings/      # Configuration UI
            ├── discover/      # Lead discovery
            └── leads/         # Lead management
```

## 🐛 Troubleshooting

### Backend won't start
- Check MongoDB connection string in `.env`
- Ensure Python 3.11+ is installed

### Ollama connection failed
- Install Ollama from https://ollama.ai
- Run `ollama serve` or ensure Ollama app is running
- Test: `curl http://localhost:11434`

### Settings won't save
- Check backend is running on :8000
- Check browser console (F12) for errors

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for more troubleshooting tips.

## 📈 Roadmap

- [ ] Bulk email sending
- [ ] Email templates library
- [ ] Campaign management
- [ ] Email tracking (opens, clicks)
- [ ] Lead scoring
- [ ] More AI providers (Anthropic Claude, etc.)
- [ ] Webhook integrations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is for educational and commercial use.

---

**Built with ❤️ using FastAPI, Next.js, MongoDB, and AI**

For questions or issues, please open a GitHub issue or contact the development team.

# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 5. Set Up Google Sheets API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API and Google Drive API
4. Create credentials (Service Account)
5. Download JSON credentials and save as `config/google_credentials.json`
6. Share your Google Sheet with the service account email

## 🚀 Usage

### Basic Command
```bash
python cli.py --name "AdVision Marketing" --desc "Digital Marketing & SEO Agency" --url "https://advision.com"
```

### Advanced Options
```bash
python cli.py \
  --name "TechCorp Solutions" \
  --desc "Enterprise Software Development & Cloud Solutions" \
  --url "https://techcorp.com" \
  --max-leads 20 \
  --industry "Technology" \
  --region "North America"
```

### Schedule Weekly Runs (Bonus)
```bash
python cli.py --schedule weekly
```

### View Analytics
```bash
python cli.py --analytics
```

## 📁 Project Structure

```
B2B smart marketing/
├── cli.py                          # Main command-line interface
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
│
├── src/
│   ├── __init__.py
│   ├── core/                       # Core business logic
│   │   ├── __init__.py
│   │   ├── web_analyzer.py        # Website analysis and service extraction
│   │   ├── lead_discovery.py      # Lead discovery using APIs
│   │   ├── ai_generator.py        # AI-powered content generation
│   │   ├── portfolio_generator.py # PDF portfolio creation
│   │   └── sheets_manager.py      # Google Sheets operations
│   │
│   └── utils/                      # Utility modules
│       ├── __init__.py
│       ├── logger.py              # Logging configuration
│       ├── config.py              # Configuration management
│       ├── analytics.py           # Analytics and reporting
│       ├── email_sender.py        # Email automation (bonus)
│       ├── drive_manager.py       # Google Drive integration (bonus)
│       └── scheduler.py           # Task scheduling (bonus)
│
├── config/                         # Configuration files
│   ├── google_credentials.json    # Google API credentials (not in repo)
│   └── portfolio_styles.json      # Portfolio styling templates
│
├── logs/                           # Application logs
│   └── activity.log               # Main activity log
│
├── output/                         # Generated outputs
│   └── portfolios/                # Generated PDF portfolios
│
└── tests/                          # Unit tests
    ├── __init__.py
    ├── test_web_analyzer.py
    ├── test_lead_discovery.py
    ├── test_ai_generator.py
    ├── test_portfolio_generator.py
    └── test_sheets_manager.py
```

## 🔧 Configuration

### Required API Keys
- **OpenAI API** (or Ollama for local LLaMA)
- **SerpAPI** (free tier: 100 searches/month)
- **Hunter.io** (optional, free tier: 50 searches/month)
- **Snov.io** (optional, free tier: 50 credits/month)

### Google Sheets Setup
1. Create a new Google Sheet
2. Add headers: `Company Name`, `Website`, `Industry`, `Services Matched`, `Email Draft`, `Portfolio URL`, `Date Added`, `Status`
3. Share with service account email
4. Copy spreadsheet ID from URL

## 📊 Output

### Google Sheet Columns
- Company Name
- Website URL
- Industry/Business Type
- Services Matched
- Email Draft
- Portfolio File Path/URL
- Date Added
- Status (New/Contacted/Responded)

### Portfolio PDF
- Company logo and branding
- Personalized introduction
- Relevant service highlights
- Case studies or testimonials
- Contact information
- Dynamic styling based on industry

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_web_analyzer.py -v
```

## 📝 Logging

All activities are logged to `logs/activity.log` with:
- Timestamp
- Log level (INFO, WARNING, ERROR)
- Module name
- Detailed message

## ⚖️ Legal & Ethical Considerations

- ✅ Uses only legal, open-web data sources
- ✅ Respects robots.txt and website ToS
- ✅ Rate limiting to prevent server overload
- ✅ No scraping violations or unauthorized access
- ✅ GDPR and privacy-conscious data handling

## 🎯 Evaluation Criteria

| Criteria | Weight | Description |
|----------|--------|-------------|
| Functionality | 30% | Completeness of all required modules |
| AI Quality | 25% | Relevance and clarity of email + portfolio |
| Legal Compliance | 15% | Ethical data use and no violations |
| Code Design | 15% | Clean, modular, maintainable architecture |
| Presentation | 15% | Clarity and demonstration of workflow |

## 🚧 Roadmap

- [ ] Multi-language support for international outreach
- [ ] CRM integration (HubSpot, Salesforce)
- [ ] Email open/click tracking
- [ ] A/B testing for email templates
- [ ] Machine learning for lead scoring
- [ ] Web dashboard interface

## 👥 Contributing

Contributions are welcome! Please follow:
1. Fork the repository
2. Create a feature branch
3. Commit changes with clear messages
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙋 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## 🏆 Acknowledgments

Built for the AI Marketing Automation Hackathon.

---

**Made with ❤️ for smarter B2B marketing**
