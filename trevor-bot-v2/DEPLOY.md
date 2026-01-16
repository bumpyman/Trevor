# 🚀 Deployment Guide - Trevor Bot 2.0

## ✅ Tests Passed!

Your bot has passed all component tests and is ready for deployment!

## 📋 What You Need

### 1. Get API Keys (15 minutes)

#### Telegram Bot Token (Required)
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Choose name: "Trevor Health Bot"
5. Choose username: "trevor_health_bot" (or your choice)
6. **Copy the token** (looks like: `1234567890:ABCdefGHI...`)

#### Anthropic API Key (Required)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up (free $5 credit for testing)
3. Go to "API Keys"
4. Create new key
5. **Copy the key** (starts with `sk-ant-...`)

#### SendGrid API Key (Required for appointments)
1. Go to [sendgrid.com](https://sendgrid.com)
2. Sign up (free tier: 100 emails/day)
3. Settings → API Keys
4. Create key with "Mail Send" permission
5. **Copy the key** (starts with `SG.`)

## 🎯 Option 1: Deploy to Railway (Recommended - Easiest)

**Cost**: ~$5/month | **Time**: 10 minutes

### Step 1: Push Code to GitHub

```bash
# Already done! Your code is at:
# https://github.com/bumpyman/Trevor
```

### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository: `bumpyman/Trevor`
6. Set root directory: `trevor-bot-v2`

### Step 3: Add Services

Railway will detect `docker-compose.yml` and create:
- ✅ PostgreSQL database (automatic)
- ✅ Your Python bot

### Step 4: Set Environment Variables

In Railway dashboard → Variables:

```env
TELEGRAM_BOT_TOKEN=your_telegram_token_here
ANTHROPIC_API_KEY=your_anthropic_key_here
SENDGRID_API_KEY=your_sendgrid_key_here
HUG_HEMATOLOGY_EMAIL=hematology@hug.ch
FROM_EMAIL=trevorbot@yourdomain.com
SECRET_KEY=your_secret_key_here
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-filled by Railway
FHIR_BASE_URL=http://fhir:8080/fhir
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 5: Deploy

Railway will automatically deploy! Monitor logs in dashboard.

### Step 6: Test

Open Telegram → search for your bot → Send `/start`

---

## 🎯 Option 2: Deploy to Fly.io (More Control)

**Cost**: ~$5/month | **Time**: 15 minutes

### Prerequisites

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login
```

### Step 1: Create Fly App

```bash
cd trevor-bot-v2

# Create app
flyctl apps create trevor-bot

# Create PostgreSQL
flyctl postgres create --name trevor-db --region cdg

# Attach database
flyctl postgres attach --app trevor-bot trevor-db
```

### Step 2: Create fly.toml

```toml
app = "trevor-bot"
primary_region = "cdg"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  ENVIRONMENT = "production"
  LOG_LEVEL = "INFO"
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
  [[services.ports]]
    port = 443
```

### Step 3: Set Secrets

```bash
flyctl secrets set TELEGRAM_BOT_TOKEN="your_token"
flyctl secrets set ANTHROPIC_API_KEY="your_key"
flyctl secrets set SENDGRID_API_KEY="your_key"
flyctl secrets set HUG_HEMATOLOGY_EMAIL="hematology@hug.ch"
flyctl secrets set FROM_EMAIL="trevorbot@domain.com"
flyctl secrets set SECRET_KEY="your_secret"
```

### Step 4: Deploy

```bash
flyctl deploy
```

---

## 🎯 Option 3: Deploy to DigitalOcean App Platform

**Cost**: ~$5/month | **Time**: 15 minutes

### Step 1: Create App

1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
2. Create → Apps
3. Connect GitHub → Select `trevor-bot-v2` directory

### Step 2: Configure

- **Service Name**: trevor-bot
- **Environment**: Python 3.11
- **Build Command**: `pip install -r requirements.txt`
- **Run Command**: `python main.py`

### Step 3: Add Database

- Create → Databases → PostgreSQL
- Attach to app

### Step 4: Environment Variables

Add in app settings:

```
TELEGRAM_BOT_TOKEN=...
ANTHROPIC_API_KEY=...
SENDGRID_API_KEY=...
HUG_HEMATOLOGY_EMAIL=hematology@hug.ch
FROM_EMAIL=trevorbot@domain.com
SECRET_KEY=...
DATABASE_URL=${database.DATABASE_URL}
ENVIRONMENT=production
```

---

## 🎯 Option 4: Deploy Locally with Docker (For Testing)

**Cost**: $0 | **Time**: 5 minutes

### Prerequisites

- Docker installed on your machine
- Docker Compose installed

### Step 1: Update .env

```bash
cd trevor-bot-v2
nano .env  # Add real API keys
```

### Step 2: Start Services

```bash
# Start PostgreSQL and FHIR server
docker-compose up -d

# Wait 30 seconds for FHIR to start
sleep 30

# Start bot (in another terminal)
source venv/bin/activate
python main.py
```

### Step 3: Test

Open Telegram → message your bot

---

## 📊 Monitoring & Logs

### Railway
- Dashboard → Logs tab
- Real-time log streaming

### Fly.io
```bash
flyctl logs
```

### DigitalOcean
- App → Runtime Logs

### Local
```bash
tail -f logs/trevor_bot_*.log
```

---

## 🔧 Troubleshooting

### Bot doesn't respond

1. Check logs for errors
2. Verify API keys are correct
3. Test Telegram token:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```

### Database errors

1. Ensure DATABASE_URL is set correctly
2. Check database is running
3. Run migrations if needed

### FHIR errors

1. Check FHIR_BASE_URL
2. Verify FHIR server is running
3. Test: `curl $FHIR_BASE_URL/metadata`

### Out of memory

1. Upgrade plan (Railway/Fly/DO)
2. Or use lightweight requirements-minimal.txt

---

## 💰 Cost Comparison

| Platform | Cost/Month | Free Tier | Best For |
|----------|------------|-----------|----------|
| **Railway** | $5 | $5 credit | Easiest setup |
| **Fly.io** | $5 | Limited | More control |
| **DigitalOcean** | $5 | $200 credit | Familiar platform |
| **Local** | $0 | N/A | Testing only |

---

## 🎓 Post-Deployment Checklist

- [ ] Bot responds to `/start`
- [ ] Bot answers health questions
- [ ] Emergency detection works
- [ ] Test appointment request
- [ ] Check email arrives at HUG
- [ ] Monitor for 24 hours
- [ ] Set up alerts/monitoring
- [ ] Document any issues

---

## 🚀 Next Steps After Deployment

1. **Add WhatsApp**: Follow instructions in README.md
2. **Add Messenger**: Follow instructions in README.md
3. **Expand Knowledge Base**: Add more medical documents
4. **Enable Peer Coaching**: Implement community features
5. **Connect to HUG EHR**: Direct integration with hospital

---

## 🆘 Support

- **Issues**: https://github.com/bumpyman/Trevor/issues
- **Documentation**: See README.md, QUICKSTART.md, MIGRATION.md
- **Logs**: Always check logs first!

---

## 🎉 Success!

Once deployed, your bot will:
- ✅ Chat naturally with patients in French
- ✅ Provide evidence-based medical information
- ✅ Detect emergencies automatically
- ✅ Schedule HUG@Home appointments via email
- ✅ Store data in FHIR format
- ✅ Scale to handle many users

**Congratulations on deploying Trevor Bot 2.0!** 🤖💙
