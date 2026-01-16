# 🚀 Quick Start Guide - Trevor Bot 2.0

Get Trevor Bot running in **10 minutes**!

## Prerequisites Checklist

- [ ] Python 3.10 or higher installed
- [ ] Docker installed and running
- [ ] Telegram account
- [ ] Text editor

## Step-by-Step Setup

### 1️⃣ Get Your API Keys (5 minutes)

#### Telegram Bot Token
1. Open Telegram, search for `@BotFather`
2. Send `/newbot` command
3. Choose a name (e.g., "Trevor Health Bot")
4. Choose a username (e.g., "trevor_health_bot")
5. **Copy the token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to "API Keys"
4. Create new key
5. **Copy the key** (starts with `sk-ant-...`)

#### SendGrid API Key (for emails)
1. Go to [sendgrid.com](https://sendgrid.com)
2. Sign up for free account
3. Go to Settings → API Keys
4. Create new key with "Mail Send" permissions
5. **Copy the key** (starts with `SG.`)

### 2️⃣ Install Trevor Bot (2 minutes)

```bash
# Navigate to the bot directory
cd trevor-bot-v2

# Run the automated setup script
./setup.sh
```

This will:
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Start PostgreSQL and FHIR server
- ✅ Create `.env` file

### 3️⃣ Configure Your Bot (2 minutes)

Edit the `.env` file:

```bash
nano .env  # or use your favorite editor
```

**Required settings:**
```env
TELEGRAM_BOT_TOKEN=paste_your_telegram_token_here
ANTHROPIC_API_KEY=paste_your_anthropic_key_here
SENDGRID_API_KEY=paste_your_sendgrid_key_here
HUG_HEMATOLOGY_EMAIL=hematology@hug.ch
FROM_EMAIL=your-email@domain.com
SECRET_KEY=generate_random_string_here
```

**Generate a secret key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Save and close the file.

### 4️⃣ Start the Bot (1 minute)

```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python main.py
```

You should see:
```
🤖 Starting Trevor Bot - AI Health Companion
✅ Database initialized
✅ FHIR client initialized
✅ RAG system initialized
✅ Telegram bot started
```

### 5️⃣ Test Your Bot

1. Open Telegram
2. Search for your bot username (e.g., `@trevor_health_bot`)
3. Click "Start" or send `/start`
4. You should receive a welcome message in French!

## 🧪 Test Conversation

Try these messages:

```
Hello!
→ Should receive French welcome message

J'ai mal à la tête
→ Should ask about symptoms and give advice

Je voudrais un rendez-vous
→ Should offer to schedule HUG@Home appointment

Comment prévenir les crises?
→ Should provide evidence-based prevention tips
```

## 🐛 Troubleshooting

### Bot doesn't respond
```bash
# Check if services are running
docker ps

# Should show:
# - trevor-postgres
# - trevor-fhir

# Check bot logs
tail -f logs/trevor_bot_*.log
```

### Database connection error
```bash
# Restart Docker services
docker-compose down
docker-compose up -d

# Wait 10 seconds
sleep 10

# Restart bot
python main.py
```

### FHIR server not ready
```bash
# Check FHIR logs
docker logs trevor-fhir

# Wait for it to fully start (may take 1-2 minutes first time)
# You'll see: "Started Application in XX seconds"
```

### "Module not found" error
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 📊 Verify Everything Works

```bash
# Test database
python -c "from src.models.database import init_db; init_db(); print('✅ DB OK')"

# Test FHIR
curl http://localhost:8080/fhir/metadata

# Test RAG
python -c "from src.llm.rag import MedicalKnowledgeRAG; rag = MedicalKnowledgeRAG(); print(rag.get_collection_stats())"
```

All should return success!

## 🎯 What's Next?

### Customize Medical Knowledge
Add your own medical documents to the RAG system:

```python
from src.llm.rag import MedicalKnowledgeRAG

rag = MedicalKnowledgeRAG()
rag.add_document(
    content="Your medical content here...",
    metadata={
        "title": "Document title",
        "source": "WHO Guidelines",
        "category": "prevention",
    },
    doc_id="unique_id_123"
)
```

### Monitor Usage
```bash
# View database stats
docker exec -it trevor-postgres psql -U trevor -d trevor_bot -c "SELECT COUNT(*) FROM users;"

# View logs
tail -f logs/trevor_bot_*.log
```

### Add WhatsApp
See `README.md` for WhatsApp integration guide.

## 💰 Cost Tracking

Monitor your API usage:

**Anthropic (Claude):**
- Dashboard: [console.anthropic.com](https://console.anthropic.com)
- Current model: Claude Haiku (~$0.003 per 1K tokens)
- 100 conversations ≈ $0.50

**SendGrid:**
- Dashboard: [app.sendgrid.com](https://app.sendgrid.com)
- Free tier: 100 emails/day

## 🆘 Need Help?

1. **Check logs**: `tail -f logs/trevor_bot_*.log`
2. **Check README**: More detailed documentation
3. **Check Docker**: `docker ps` and `docker logs`
4. **Open an issue**: GitHub issues

## 🎉 Success!

Your Trevor Bot is now running! It can:
- ✅ Chat naturally in French
- ✅ Answer medical questions with sources
- ✅ Detect emergencies
- ✅ Help schedule appointments
- ✅ Track patient conversations
- ✅ Store data in FHIR format

**Made with ❤️ for sickle cell disease patients**
