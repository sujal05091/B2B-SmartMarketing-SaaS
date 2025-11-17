# 🚀 Smart Marketing Assistant

An AI-powered command-line tool that automates B2B lead discovery, personalized outreach, and portfolio generation for marketing teams.

## 📋 Overview

This Smart Marketing Assistant helps B2B businesses:
- **Analyze** your business website to identify key services
- **Discover** potential clients worldwide using legal open-web sources
- **Generate** personalized outreach emails highlighting relevant services
- **Create** customized PDF portfolios styled dynamically by industry
- **Manage** all leads in Google Sheets with complete tracking

## ✨ Features

### Core Features
- ✅ Automated website analysis and service extraction
- ✅ Lead discovery using free-tier APIs (SerpAPI, Hunter.io, Snov.io)
- ✅ AI-powered email generation (OpenAI GPT or local LLaMA)
- ✅ Dynamic PDF portfolio creation
- ✅ Google Sheets integration with duplicate prevention
- ✅ Comprehensive logging and error handling

### Bonus Features
- 📁 Google Drive integration for portfolio storage
- ⏰ Scheduled weekly discovery automation
- 📊 Analytics dashboard (leads per run, industries found)
- 📧 Automatic email sending via SMTP (optional)

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **AI Models**: OpenAI GPT-4 / GPT-3.5-turbo or LLaMA (via Ollama)
- **Web Scraping**: BeautifulSoup4, Requests
- **PDF Generation**: ReportLab
- **Cloud Services**: Google Sheets API, Google Drive API
- **Data Sources**: SerpAPI, Hunter.io, Snov.io (free tiers)

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "B2B smart marketing"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
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
