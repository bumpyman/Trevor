"""Telegram bot implementation."""
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from loguru import logger
from src.config import settings
from src.llm.agent import TrevorAgent
from src.llm.rag import MedicalKnowledgeRAG, initialize_knowledge_base
from src.models.database import SessionLocal, User, Conversation, init_db
from datetime import datetime


class TelegramBot:
    """Telegram bot handler for Trevor."""

    def __init__(self):
        """Initialize Telegram bot."""
        self.agent = TrevorAgent()
        self.rag = MedicalKnowledgeRAG()

        # Initialize knowledge base
        stats = self.rag.get_collection_stats()
        if stats["total_documents"] == 0:
            logger.info("Knowledge base empty, initializing...")
            initialize_knowledge_base(self.rag)

        # Initialize database
        init_db()

        # Build application
        self.application = Application.builder().token(settings.telegram_bot_token).build()

        # Register handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("Telegram bot initialized")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        telegram_id = str(user.id)

        # Get or create user in database
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.telegram_id == telegram_id).first()

            if not db_user:
                db_user = User(
                    telegram_id=telegram_id,
                    username=user.username,
                    full_name=user.full_name,
                )
                db.add(db_user)
                db.commit()
                logger.info(f"New user created: {telegram_id}")

            # Update last active
            db_user.last_active = datetime.utcnow()
            db.commit()

        finally:
            db.close()

        welcome_message = """👋 Bonjour! Je suis Trevor, ton assistant de santé personnel pour la gestion de la drépanocytose.

Je suis là pour t'aider à:
🩺 Suivre tes symptômes et observations
💊 Gérer ton traitement
📅 Prendre des rendez-vous HUG@Home
❓ Répondre à tes questions médicales
💪 T'accompagner avec des conseils personnalisés

**Important:** Je ne remplace pas un médecin. En cas d'urgence, appelle le 144 ou va aux urgences HUG.

Comment puis-je t'aider aujourd'hui?"""

        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """🆘 **Comment utiliser Trevor:**

Tu peux me parler naturellement! Voici quelques exemples:

📝 **Reporter des symptômes:**
"J'ai mal au bras gauche depuis ce matin"
"Je me sens très fatigué"

💊 **Questions sur le traitement:**
"À quoi sert l'hydroxyurée?"
"J'ai oublié de prendre mon médicament hier"

📅 **Rendez-vous:**
"Je voudrais un rendez-vous HUG@Home"
"C'est urgent, j'ai besoin de voir un médecin"

❓ **Questions générales:**
"Comment prévenir les crises?"
"Puis-je faire du sport?"

📊 **Commandes:**
/start - Démarrer une conversation
/help - Voir ce message
/stats - Voir mes statistiques

N'hésite pas à me poser n'importe quelle question!"""

        await update.message.reply_text(help_text)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - show user statistics."""
        telegram_id = str(update.effective_user.id)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()

            if not user:
                await update.message.reply_text(
                    "Je n'ai pas encore de données sur toi. Commence par me parler! 😊"
                )
                return

            # Count conversations
            conversation_count = (
                db.query(Conversation).filter(Conversation.user_id == user.id).count()
            )

            stats_text = f"""📊 **Tes statistiques:**

💬 Messages échangés: {conversation_count}
📅 Membre depuis: {user.created_at.strftime('%d/%m/%Y')}
🕐 Dernière activité: {user.last_active.strftime('%d/%m/%Y à %H:%M')}

Continue à utiliser Trevor pour un meilleur suivi de ta santé! 💪"""

            await update.message.reply_text(stats_text)

        finally:
            db.close()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_message = update.message.text
        telegram_id = str(update.effective_user.id)

        logger.info(f"Message from {telegram_id}: {user_message}")

        # Show typing indicator
        await update.message.chat.send_action("typing")

        db = SessionLocal()
        try:
            # Get user
            user = db.query(User).filter(User.telegram_id == telegram_id).first()

            if not user:
                # Create user if doesn't exist
                user = User(
                    telegram_id=telegram_id,
                    username=update.effective_user.username,
                    full_name=update.effective_user.full_name,
                )
                db.add(user)
                db.commit()

            # Update last active
            user.last_active = datetime.utcnow()
            db.commit()

            # Check for emergency
            is_emergency = await self.agent.detect_emergency(user_message)
            if is_emergency:
                emergency_message = """⚠️ **ATTENTION: Situation potentiellement urgente détectée**

Si tu as:
- Douleur thoracique sévère
- Difficultés à respirer
- Fièvre > 38.5°C
- Symptômes graves

👉 **APPELLE IMMÉDIATEMENT LE 144** ou va aux urgences HUG

Ne tarde pas, ta santé est prioritaire!

Veux-tu que je t'aide à prendre un rendez-vous urgent HUG@Home?"""

                await update.message.reply_text(emergency_message)
                return

            # Classify intent
            intent = await self.agent.classify_intent(user_message)

            # Get conversation history (last 10 messages)
            conversation_history = []
            recent_conversations = (
                db.query(Conversation)
                .filter(Conversation.user_id == user.id)
                .order_by(Conversation.created_at.desc())
                .limit(10)
                .all()
            )

            for conv in reversed(recent_conversations):
                conversation_history.append({"role": conv.role, "content": conv.content})

            # Retrieve relevant knowledge using RAG
            retrieved_docs = self.rag.retrieve(user_message, n_results=2)
            retrieved_knowledge = self.rag.format_retrieved_knowledge(retrieved_docs)

            # Build user context
            user_context = {
                "member_since": user.created_at.strftime("%Y-%m-%d"),
                "language": user.language,
            }

            # Generate response
            response = await self.agent.chat(
                message=user_message,
                conversation_history=conversation_history,
                user_context=user_context,
                retrieved_knowledge=retrieved_knowledge,
            )

            # Save conversation
            user_conv = Conversation(
                user_id=user.id,
                role="user",
                content=user_message,
                platform="telegram",
                intent=intent,
            )
            db.add(user_conv)

            assistant_conv = Conversation(
                user_id=user.id,
                role="assistant",
                content=response,
                platform="telegram",
            )
            db.add(assistant_conv)
            db.commit()

            # Send response
            await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                "Désolé, j'ai rencontré une erreur. Peux-tu réessayer dans quelques instants?"
            )

        finally:
            db.close()

    async def run(self):
        """Run the bot."""
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

        # Keep running
        try:
            await asyncio.Event().wait()
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()


async def main():
    """Main entry point for Telegram bot."""
    bot = TelegramBot()
    await bot.run()


if __name__ == "__main__":
    from loguru import logger

    logger.add("logs/telegram_bot.log", rotation="1 day", retention="7 days")
    asyncio.run(main())
