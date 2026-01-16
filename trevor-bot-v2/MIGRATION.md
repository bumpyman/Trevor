# Migration Guide: C# Bot Framework → Python Multi-Platform

## Overview

This guide explains the differences between the old TrevorBot (C# Bot Framework v3) and the new TrevorBot 2.0 (Python multi-platform).

## Architecture Comparison

### Old System (C# Bot Framework)
```
MessagesController → RootDialog → InscriptionDialog/ConnexionDialog
                                → MenuDialog → SESForm/SelfMonitoringForm
```

### New System (Python)
```
Telegram Bot → TrevorAgent (LLM) → RAG System → Response
            ↓
        Database (PostgreSQL + FHIR)
            ↓
        Email Service (HUG@Home)
```

## Key Changes

### 1. Conversational Model

**Old:** Dialog-based with FormFlow
- Rigid question-answer flow
- Pre-defined dialog trees
- Limited flexibility

**New:** LLM-powered natural conversation
- Free-form conversation
- Context-aware responses
- Adaptive to user needs

### 2. Platform Support

**Old:** Microsoft Bot Framework channels
- Microsoft Teams
- Skype
- Web Chat
- Facebook (through connector)

**New:** Direct platform integration
- ✅ Telegram (implemented)
- ⏳ WhatsApp (planned)
- ⏳ Messenger (planned)

### 3. Data Storage

**Old:**
- In-memory by default
- Optional: Azure Table Storage, CosmosDB

**New:**
- PostgreSQL for application data
- HAPI FHIR for healthcare data
- ChromaDB for vector embeddings

### 4. Medical Knowledge

**Old:**
- Hard-coded questions and responses
- Static form validation
- No external knowledge sources

**New:**
- RAG system with curated medical documents
- Real-time retrieval of relevant information
- Sources cited in responses
- Extensible knowledge base

### 5. Appointment System

**Old:**
- Direct API integration (deprecated)
- Built into dialog flow

**New:**
- Email-based workflow to HUG
- FHIR CommunicationRequest resources
- Professional HTML email templates

## Feature Mapping

| Old Feature | New Implementation | Status |
|-------------|-------------------|--------|
| User Registration | User model + FHIR Patient | ✅ |
| Email/Password Auth | Platform-based auth (Telegram ID) | ✅ |
| SES Questionnaire | Conversational data collection + FHIR Observation | ⏳ |
| Self-Monitoring | Symptom tracking + FHIR Observation | ⏳ |
| Menu System | Natural language intent detection | ✅ |
| RadarChart visualization | Planned with data export | ⏳ |
| Telemedicine Booking | Email to HUG hematology | ✅ |

## Data Migration (if needed)

### Export from Old System

1. **User Data**
```csharp
// Export users to JSON
var users = dbContext.Users.ToList();
File.WriteAllText("users.json", JsonConvert.SerializeObject(users));
```

2. **Questionnaire Responses**
```csharp
// Export SES responses
var sesResponses = dbContext.SESResponses.ToList();
File.WriteAllText("ses_responses.json", JsonConvert.SerializeObject(sesResponses));
```

### Import to New System

```python
import json
from src.models.database import SessionLocal, User
from src.fhir.client import TrevorFHIRClient

# Load old data
with open('users.json') as f:
    old_users = json.load(f)

db = SessionLocal()
fhir = TrevorFHIRClient()

for old_user in old_users:
    # Create new user
    new_user = User(
        email=old_user['Email'],
        username=old_user['Username'],
        full_name=old_user.get('FullName'),
    )
    db.add(new_user)
    db.commit()

    # Create FHIR Patient
    patient_id = fhir.create_patient(
        given_name=old_user.get('FirstName', ''),
        family_name=old_user.get('LastName', ''),
        email=old_user['Email'],
    )

    new_user.fhir_patient_id = patient_id
    db.commit()

db.close()
```

## Questionnaire Conversion

### Old: SES Form (C#)
```csharp
[Serializable]
public class SESQuery
{
    [Prompt("Quel est ton âge?")]
    public int Age { get; set; }

    [Prompt("Quel est ton sexe?")]
    public string Gender { get; set; }
    // ... more fields
}
```

### New: Conversational Collection (Python)
```python
async def collect_ses_data(user_message, agent):
    # LLM naturally asks questions based on context
    response = await agent.chat(
        message=user_message,
        conversation_history=history,
        retrieved_knowledge="SES questionnaire guidelines..."
    )

    # Extract structured data from conversation
    ses_data = parse_ses_from_conversation(history)

    # Store in FHIR
    fhir.create_observation(
        patient_id=user.fhir_patient_id,
        observation_type="ses_questionnaire",
        value=ses_data
    )
```

## Code Comparison Examples

### Example 1: Greeting User

**Old (C#):**
```csharp
public async Task StartAsync(IDialogContext context)
{
    await context.PostAsync("Bonjour mon nom est Trevor. Je peux t'aider à mieux gérer ta drépanocytose!");
    context.Wait(MessageReceivedAsync);
}
```

**New (Python):**
```python
async def start_command(self, update: Update, context):
    welcome = """👋 Bonjour! Je suis Trevor...
    Je suis là pour t'aider à:
    🩺 Suivre tes symptômes
    💊 Gérer ton traitement
    ..."""
    await update.message.reply_text(welcome)
```

### Example 2: Collecting User Information

**Old (C#):**
```csharp
[Serializable]
public class InscriptionQuery
{
    [Prompt("Quel est ton email?")]
    [Pattern(@"^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$")]
    public string Email { get; set; }
}
```

**New (Python):**
```python
# Natural conversation, LLM handles validation
async def handle_message(self, update, context):
    response = await self.agent.chat(
        message=user_message,
        conversation_history=history,
        user_context=context
    )
    # LLM naturally asks for email, validates format, handles errors
```

## Configuration Changes

### Old: Web.config
```xml
<appSettings>
  <add key="MicrosoftAppId" value="" />
  <add key="MicrosoftAppPassword" value="" />
</appSettings>
```

### New: .env
```env
TELEGRAM_BOT_TOKEN=...
ANTHROPIC_API_KEY=...
SENDGRID_API_KEY=...
DATABASE_URL=postgresql://...
FHIR_BASE_URL=http://localhost:8080/fhir
```

## Deployment Changes

### Old: Azure App Service
```
- Requires Azure subscription
- Deploy to App Service
- Configure Bot Framework channels
- Set up Application Insights
```

### New: Flexible Deployment
```
Option 1: Railway.app ($5/mo)
Option 2: Fly.io ($5/mo)
Option 3: DigitalOcean App Platform ($5/mo)
Option 4: Your own VPS
Option 5: Local development
```

## Cost Comparison

### Old System
- Azure App Service: $10-50/mo
- Azure Table Storage: $1-5/mo
- Application Insights: $5-20/mo
- **Total: $16-75/mo**

### New System
- Hosting (Railway/Fly.io): $5-10/mo
- PostgreSQL: Included
- Claude API: $5-20/mo (usage-based)
- SendGrid: Free (100 emails/day)
- **Total: $10-30/mo**

## Benefits of Migration

### Technical
✅ Modern LLM-powered conversations
✅ FHIR-compliant healthcare data
✅ Better platform support (Telegram, WhatsApp, Messenger)
✅ Extensible knowledge base with RAG
✅ Easier to maintain and extend

### User Experience
✅ Natural conversations vs rigid forms
✅ Instant medical knowledge retrieval
✅ Context-aware responses
✅ Better emergency detection
✅ More platforms (mobile-first)

### Cost
✅ 40-60% cheaper to run
✅ No Azure lock-in
✅ Pay-per-use for LLM
✅ Free email tier

### Development
✅ Python ecosystem
✅ Easier to find developers
✅ Simpler architecture
✅ Better testing tools
✅ Faster iteration

## Gradual Migration Strategy

If you want to run both systems in parallel:

1. **Week 1-2: Pilot**
   - Deploy new Python bot to small user group
   - Keep old C# bot running for everyone else
   - Monitor feedback and performance

2. **Week 3-4: Data Migration**
   - Export user data from old system
   - Import into new system with FHIR mapping
   - Verify data integrity

3. **Week 5-6: Feature Parity**
   - Implement any missing features from old system
   - Train LLM on specific questionnaires
   - Test thoroughly

4. **Week 7-8: Full Migration**
   - Announce migration to all users
   - Redirect old bot to new bot
   - Keep old system as backup for 1 month
   - Delete old system after verification

## Testing Checklist

Before retiring old system:

- [ ] All users can authenticate
- [ ] Questionnaires collect same data
- [ ] Email notifications work
- [ ] Data exports to FHIR correctly
- [ ] Emergency detection working
- [ ] HUG@Home appointments functional
- [ ] Performance acceptable (< 2s response time)
- [ ] Costs within budget
- [ ] User satisfaction >= old system

## Rollback Plan

If migration fails:

1. Keep old C# bot running during migration
2. Set DNS/routing to point back to old system
3. Data sync: New → Old if users added data
4. Announce temporary rollback to users
5. Fix issues in new system
6. Retry migration

## Support

For migration help:
- Check QUICKSTART.md for setup
- See README.md for detailed docs
- Run test_setup.py to verify
- Check logs in logs/ directory

---

**Recommendation:** Start with Telegram-only deployment, verify it works well, then add WhatsApp and Messenger. This reduces risk and allows iterative improvement.
