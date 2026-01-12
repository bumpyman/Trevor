# TrevorBot 2.0 - AI Health Companion for Sickle Cell Disease

🤖 Modern AI-powered chatbot supporting patients with sickle cell disease (drépanocytose) across multiple platforms.

## 🌟 Features

- **Multi-Platform Support**: Telegram, WhatsApp, Facebook Messenger
- **AI-Powered Conversations**: Claude-based LLM with medical knowledge
- **RAG System**: Retrieval-Augmented Generation with curated medical sources
- **FHIR Compatibility**: Full FHIR R4 integration for healthcare interoperability
- **Personalized Coaching**: Adaptive recommendations based on patient history
- **HUG@Home Integration**: Email-based appointment scheduling
- **Multilingual**: French interface with extensible language support
- **Privacy-First**: GDPR compliant, encrypted data storage

## 🏗️ Architecture

```
trevor-bot-v2/
├── src/
│   ├── bot/
│   │   └── platforms/          # Platform-specific handlers
│   │       └── telegram_bot.py
│   ├── llm/
│   │   ├── agent.py           # Claude AI agent
│   │   └── rag.py             # RAG system
│   ├── fhir/
│   │   └── client.py          # FHIR operations
│   ├── integrations/
│   │   └── email.py           # Email service
│   ├── models/
│   │   └── database.py        # SQLAlchemy models
│   └── config.py              # Configuration
├── docker-compose.yml         # PostgreSQL + HAPI FHIR
├── requirements.txt
└── main.py                    # Entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Telegram Bot Token ([Get from @BotFather](https://t.me/botfather))
- Anthropic API Key ([Get from console.anthropic.com](https://console.anthropic.com))
- SendGrid API Key ([Get from sendgrid.com](https://sendgrid.com))

### Installation

1. **Clone the repository**
```bash
cd trevor-bot-v2
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
TELEGRAM_BOT_TOKEN=your_telegram_token
ANTHROPIC_API_KEY=your_anthropic_key
SENDGRID_API_KEY=your_sendgrid_key
HUG_HEMATOLOGY_EMAIL=hematology@hug.ch
FROM_EMAIL=trevorbot@yourdomain.com
SECRET_KEY=your-secret-key-here
```

5. **Start Docker services** (PostgreSQL + HAPI FHIR)
```bash
docker-compose up -d
```

6. **Initialize database**
```bash
# Database tables will be created automatically on first run
```

7. **Run the bot**
```bash
python main.py
```

## 📱 Getting Your Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to name your bot
4. Copy the API token provided
5. Paste it in your `.env` file

## 🔧 Configuration

### Database

The bot uses PostgreSQL for user data and HAPI FHIR for healthcare records.

**Connection string format:**
```
DATABASE_URL=postgresql://user:password@host:port/database
```

Default (from docker-compose):
```
DATABASE_URL=postgresql://trevor:trevor_dev_password@localhost:5432/trevor_bot
```

### FHIR Server

HAPI FHIR server runs on `http://localhost:8080/fhir`

**Verify it's running:**
```bash
curl http://localhost:8080/fhir/metadata
```

### LLM Configuration

**Option 1: Claude API (Recommended)**
```env
ANTHROPIC_API_KEY=sk-ant-...
USE_LOCAL_LLM=false
```

**Option 2: Local Ollama (Free, but requires good hardware)**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3

# Configure
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
```

## 🧪 Testing

### Test the bot locally

1. Start the bot: `python main.py`
2. Open Telegram and search for your bot
3. Send `/start` to begin

### Test individual components

```python
# Test database connection
python -c "from src.models.database import init_db; init_db(); print('✓ Database OK')"

# Test FHIR client
python -c "from src.fhir.client import TrevorFHIRClient; client = TrevorFHIRClient(); print('✓ FHIR OK')"

# Test RAG system
python -c "from src.llm.rag import MedicalKnowledgeRAG; rag = MedicalKnowledgeRAG(); print('✓ RAG OK')"
```

## 📊 Database Schema

### Main Tables

- **users**: Patient accounts and preferences
- **conversations**: Chat history for context
- **observations**: Health observations (symptoms, vitals)
- **coaching_plans**: Personalized care plans
- **recommendations**: Individual coaching recommendations
- **appointment_requests**: HUG@Home appointment requests
- **knowledge_sources**: Medical knowledge base

## 🏥 FHIR Resources

The bot creates and manages these FHIR resources:

- **Patient**: User profiles
- **Observation**: Symptoms, questionnaire responses
- **CarePlan**: Coaching plans
- **CommunicationRequest**: HUG@Home appointments

## 📧 Email Templates

### HUG@Home Appointment Request

Sent to: `HUG_HEMATOLOGY_EMAIL`

Contains:
- Patient information
- Urgency level
- Reason for consultation
- Recent medical context
- Preferred appointment times

### Patient Confirmation

Sent to: Patient's email

Confirms:
- Request received
- Next steps
- Expected response time

## 🔐 Security

- **Authentication**: User-based sessions with platform IDs
- **Encryption**: TLS for all communications
- **Data Privacy**: GDPR compliant, data minimization
- **Secrets**: Environment variables, never committed
- **FHIR**: Compliant with healthcare data standards

## 💰 Cost Estimation

### Monthly Costs (Low Usage)

| Service | Free Tier | Cost |
|---------|-----------|------|
| Railway/Fly.io | - | $5-10/mo |
| PostgreSQL | Included | $0 |
| Claude API | Pay-per-use | $5-20/mo |
| SendGrid | 100 emails/day | $0 |
| **Total** | | **$10-30/mo** |

### Scaling Costs

- Claude Haiku: ~$0.003 per 1K tokens
- 1000 conversations/day ≈ $5-15/mo
- Use caching to reduce costs

## 🎯 Roadmap

### Phase 2: Enhanced Features (Completed ✓)
- ✅ Telegram integration
- ✅ Claude LLM with RAG
- ✅ FHIR integration
- ✅ Email service

### Phase 3: Multi-Platform (Next)
- ⏳ WhatsApp integration
- ⏳ Facebook Messenger integration
- ⏳ Unified message handler

### Phase 4: Advanced AI (Future)
- ⏳ Personalized coaching engine
- ⏳ Peer matching system
- ⏳ Proactive health monitoring
- ⏳ Community forum

### Phase 5: Clinical Integration (Future)
- ⏳ Direct HUG EHR integration
- ⏳ Real-time appointment scheduling
- ⏳ Lab results integration
- ⏳ Medication reminders

## 🤝 Contributing

This is a healthcare application. All contributions should:

1. Follow medical accuracy standards
2. Respect patient privacy (GDPR, HIPAA)
3. Include tests for new features
4. Be reviewed by medical professionals

## 📝 License

[Specify your license here]

## 🆘 Support

- **Issues**: Open a GitHub issue
- **Email**: [Your support email]
- **Medical Emergencies**: Always call 144 or go to HUG emergency

## 👥 Credits

- **Original Bot**: BotSIMED by m3lies
- **Modernization**: TrevorBot 2.0
- **Medical Guidance**: HUG Hematology Department

## ⚠️ Disclaimer

TrevorBot is an informational tool and does not replace medical advice.
Always consult healthcare professionals for medical decisions.

---

Made with ❤️ for sickle cell disease patients
