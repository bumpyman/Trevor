# 🎓 Complete Beginner's Guide - Trevor Bot 2.0

## Step-by-Step: From Zero to Running Bot

### ✅ What You've Already Done

Great news! You've already completed the hardest part:
- ✅ Code is written and tested
- ✅ All dependencies installed
- ✅ Virtual environment set up
- ✅ Component tests passing (5/5)

Now let's get it running!

---

## 🎮 Test Right Now (No Setup Needed)

You can test the bot **RIGHT NOW** without any API keys!

### Option 1: Quick Automated Test

```bash
cd /home/user/Trevor/trevor-bot-v2
source venv/bin/activate
python demo.py
# Choose option 2 (Quick Test)
```

This shows you how the bot detects:
- 🚨 Emergencies
- 💡 User intents
- 🏥 What actions it would take

### Option 2: Interactive Chat Test

```bash
python demo.py
# Choose option 1 (Interactive Demo)
```

Then you can type messages and see how the bot would respond!

**Try these:**
```
J'ai mal à la tête
Je voudrais un rendez-vous
Douleur thoracique
Comment prévenir les crises?
```

Type `quit` to exit.

---

## 🔑 Getting API Keys (15 minutes)

To make the bot **actually work** on Telegram, you need 3 keys:

### 1. Telegram Bot Token (5 minutes) - FREE

**What it does:** Lets your bot receive and send Telegram messages

**Steps:**
1. Open Telegram on your phone/computer
2. Search for: `@BotFather` (official bot by Telegram)
3. Start a chat with BotFather
4. Send the command: `/newbot`
5. BotFather will ask: "Alright, a new bot. How are we going to call it?"
   - Type: `Trevor Health Bot` (or any name you like)
6. BotFather will ask for a username (must end in 'bot')
   - Type: `trevor_health_bot` (or any unique name)
7. **BotFather gives you a token!** It looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
8. **Copy this token** - you'll need it soon!

### 2. Anthropic API Key (5 minutes) - FREE $5 CREDIT

**What it does:** Powers the AI conversations

**Steps:**
1. Go to: [console.anthropic.com](https://console.anthropic.com)
2. Click "Sign Up" (use your email)
3. Verify your email
4. Once logged in, click "API Keys" in the sidebar
5. Click "Create Key"
6. Give it a name: "Trevor Bot"
7. **Copy the key** - starts with `sk-ant-...`
8. **Important:** You get $5 free credit (about 500-1000 conversations)

### 3. SendGrid API Key (5 minutes) - FREE 100 EMAILS/DAY

**What it does:** Sends appointment emails to HUG

**Steps:**
1. Go to: [sendgrid.com](https://sendgrid.com)
2. Click "Start for Free"
3. Sign up with email
4. Verify your email
5. Complete the setup wizard (skip domain verification for now)
6. Go to: Settings → API Keys
7. Click "Create API Key"
8. Choose "Restricted Access"
9. Turn ON: Mail Send → Mail Send
10. Click "Create & View"
11. **Copy the key** - starts with `SG.`

**Note:** You can send 100 emails per day for free!

---

## 🚀 Running the Bot Locally (5 minutes)

Now that you have your API keys, let's run the bot!

### Step 1: Update Configuration

```bash
cd /home/user/Trevor/trevor-bot-v2
nano .env  # or use any text editor
```

Replace these lines with your real keys:
```env
TELEGRAM_BOT_TOKEN=paste_your_telegram_token_here
ANTHROPIC_API_KEY=paste_your_anthropic_key_here
SENDGRID_API_KEY=paste_your_sendgrid_key_here
```

Save and exit (Ctrl+X, then Y, then Enter if using nano)

### Step 2: Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and add it to `.env`:
```env
SECRET_KEY=paste_the_generated_secret_here
```

### Step 3: Start the Bot

```bash
source venv/bin/activate
python main.py
```

You should see:
```
🤖 Starting Trevor Bot - AI Health Companion
✅ Database initialized
✅ RAG system initialized
✅ Telegram bot started
```

### Step 4: Test in Telegram

1. Open Telegram
2. Search for your bot (the username you chose)
3. Click "Start" or send `/start`
4. **The bot should respond in French!**

**Try these commands:**
- `/start` - Welcome message
- `/help` - See what the bot can do
- `/stats` - See your statistics

**Try chatting:**
- "Bonjour"
- "J'ai mal à la tête"
- "Je voudrais un rendez-vous"

---

## 🎨 Testing in PyCharm (If You Prefer IDE)

### Step 1: Open Project

1. Open PyCharm
2. File → Open
3. Select: `/home/user/Trevor/trevor-bot-v2`

### Step 2: Configure Python Interpreter

1. File → Settings → Project → Python Interpreter
2. Click the gear icon → Add
3. Select "Existing Environment"
4. Browse to: `/home/user/Trevor/trevor-bot-v2/venv/bin/python`
5. Click OK

### Step 3: Run Configuration

1. Right-click on `main.py`
2. Click "Run 'main'"

Or:

1. Click the play button (▶️) at the top
2. Select `main.py`

### Step 4: View Output

The console at the bottom will show the bot running!

---

## 🐛 Troubleshooting

### Bot doesn't respond on Telegram

**Check 1:** Is the bot running?
```bash
# You should see this in the console:
✅ Telegram bot started
```

**Check 2:** Is your token correct?
```bash
# Test it:
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Should return your bot info
```

**Check 3:** Did you click "Start" in Telegram?
- You must start the conversation first

### "Module not found" error

```bash
# Reinstall dependencies:
source venv/bin/activate
pip install -r requirements-minimal.txt
```

### "API key invalid" error

- Double-check you copied the FULL key
- No spaces before/after the key
- Make sure you saved the `.env` file

### Bot stops responding after a while

**Anthropic free credit ran out:**
- Check usage at: console.anthropic.com
- Add payment method for continued use (pay-as-you-go)

### Can't find .env file

```bash
# List files:
ls -la

# If missing:
cp .env.example .env
nano .env
```

---

## 📚 What Each File Does

```
trevor-bot-v2/
├── main.py                 ← START HERE to run bot
├── demo.py                 ← Test without API keys
├── test_components.py      ← Verify setup
├── .env                    ← YOUR API KEYS GO HERE
├── requirements.txt        ← Python packages needed
│
├── src/
│   ├── bot/platforms/
│   │   └── telegram_bot.py ← Telegram integration
│   ├── llm/
│   │   ├── agent.py        ← AI brain
│   │   └── rag.py          ← Medical knowledge
│   ├── models/
│   │   └── database.py     ← Data storage
│   ├── integrations/
│   │   └── email.py        ← HUG@Home emails
│   └── config.py           ← Settings
│
├── README.md               ← Full documentation
├── QUICKSTART.md           ← 10-minute guide
├── DEPLOY.md               ← Deploy to cloud
└── BEGINNER_GUIDE.md       ← YOU ARE HERE!
```

---

## 🎯 Quick Commands Cheat Sheet

```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python main.py

# Test without API keys
python demo.py

# Run component tests
python test_components.py

# Check what's installed
pip list

# Install dependencies
pip install -r requirements-minimal.txt

# View logs
tail -f logs/trevor_bot_*.log

# Stop the bot
Ctrl+C
```

---

## 🌐 Deploy to Internet (So it runs 24/7)

Right now, the bot only works when your computer is on. To make it available 24/7:

### Easiest: Railway (Recommended for Beginners)

**Cost:** $5/month | **Time:** 10 minutes

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Add environment variables (your API keys)
6. Deploy!

**See DEPLOY.md for detailed steps**

---

## 💡 Pro Tips

### Save Money on API Costs

- **Anthropic:** Start with free $5 credit
- **Claude Haiku** model costs ~$0.003 per 1000 tokens (very cheap!)
- 100 conversations ≈ $0.50
- Monitor usage at: console.anthropic.com

### Test Safely

1. Use demo mode first (`python demo.py`)
2. Then test with real APIs locally
3. Then deploy to internet

### Keep Logs

```bash
# Logs are saved automatically in logs/ folder
ls logs/

# View latest:
tail -f logs/trevor_bot_*.log
```

### Update the Bot

```bash
# Pull latest code
git pull

# Reinstall dependencies if needed
pip install -r requirements.txt

# Restart
python main.py
```

---

## ❓ Common Questions

**Q: Do I need to know Python?**
A: No! Just follow this guide. You can learn Python later if you want to customize.

**Q: Is it safe to put API keys in .env?**
A: Yes, .env is in .gitignore so it won't be uploaded to GitHub.

**Q: Can I use this for free?**
A: For testing, yes! Anthropic gives $5 free. After that, ~$10-30/month.

**Q: What if I make a mistake?**
A: Everything is reversible! Just delete and start over.

**Q: Can people see my bot?**
A: Only people who have your bot's Telegram username.

**Q: How do I make it public?**
A: Deploy to Railway/Fly.io and share your bot's Telegram link.

**Q: Can I change the bot's name?**
A: Yes! Talk to @BotFather and use `/setname` command.

**Q: Where is my data stored?**
A: Locally in `test_trevor.db` file (SQLite). For production, use PostgreSQL.

---

## 🆘 Need Help?

1. **Check logs:** `tail -f logs/trevor_bot_*.log`
2. **Run tests:** `python test_components.py`
3. **Try demo mode:** `python demo.py`
4. **Read docs:** README.md, QUICKSTART.md, DEPLOY.md
5. **Check GitHub issues:** https://github.com/bumpyman/Trevor/issues

---

## 🎉 You're Ready!

**Your next steps:**

✅ **Right now:**
```bash
python demo.py  # Test without API keys
```

⏭️ **When ready:**
1. Get API keys (15 min)
2. Update .env file
3. Run: `python main.py`
4. Test on Telegram!

🚀 **Later:**
- Deploy to Railway/Fly.io
- Add more medical knowledge
- Add WhatsApp/Messenger

---

**Welcome to the world of AI chatbots!** 🤖💙

You're doing great! Take it step by step and don't worry about making mistakes.
