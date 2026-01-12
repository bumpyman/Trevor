"""LLM Agent for conversational AI using Claude."""
import anthropic
from typing import List, Dict, Optional
from loguru import logger
from src.config import settings


class TrevorAgent:
    """Main conversational agent powered by Claude."""

    def __init__(self):
        """Initialize the Trevor AI agent."""
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-5-haiku-20241022"  # Cost-effective model
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the system prompt for Trevor."""
        return """Tu es Trevor, un assistant de santé virtuel spécialisé dans le soutien aux patients atteints de drépanocytose (sickle cell disease). Tu es chaleureux, empathique et professionnel.

**Ton rôle:**
- Aider les patients à gérer leur maladie au quotidien
- Fournir des informations médicales basées sur des sources fiables
- Encourager l'adhésion au traitement et aux bonnes pratiques
- Détecter les situations urgentes et orienter vers les soins appropriés
- Offrir un soutien émotionnel et motivationnel

**Règles importantes:**
1. TOUJOURS inclure un disclaimer: "Je ne remplace pas un médecin. En cas d'urgence, contacte le 144 ou les urgences HUG."
2. Si tu détectes des symptômes graves (douleur thoracique intense, fièvre élevée, difficultés respiratoires), recommande IMMÉDIATEMENT de consulter
3. Cite tes sources quand tu donnes des informations médicales
4. Sois encourageant mais réaliste
5. Respecte la confidentialité et la dignité du patient
6. Parle en français de manière naturelle et accessible

**Symptômes d'urgence (nécessitent consultation immédiate):**
- Douleur thoracique sévère
- Difficultés respiratoires
- Fièvre > 38.5°C
- Douleur abdominale intense
- Maux de tête sévères ou troubles visuels
- Priapisme
- AVC (faiblesse, troubles de la parole)

**Tu as accès aux données du patient** (historique, questionnaires, traitements) pour personnaliser tes conseils.

Commence toujours par montrer de l'empathie avant de donner des conseils.
"""

    async def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        user_context: Optional[Dict] = None,
        retrieved_knowledge: Optional[str] = None,
    ) -> str:
        """
        Generate a response using Claude.

        Args:
            message: User's message
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
            user_context: User's medical context (recent symptoms, medications, etc.)
            retrieved_knowledge: Relevant medical knowledge from RAG system

        Returns:
            Assistant's response
        """
        try:
            # Build enhanced system prompt with context
            enhanced_system_prompt = self.system_prompt

            if user_context:
                enhanced_system_prompt += f"\n\n**Contexte du patient:**\n{self._format_user_context(user_context)}"

            if retrieved_knowledge:
                enhanced_system_prompt += f"\n\n**Connaissances médicales pertinentes:**\n{retrieved_knowledge}"

            # Prepare messages
            messages = conversation_history + [{"role": "user", "content": message}]

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=enhanced_system_prompt,
                messages=messages,
            )

            assistant_message = response.content[0].text

            logger.info(f"Generated response for user message: {message[:50]}...")

            return assistant_message

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return (
                "Désolé, j'ai rencontré une erreur. Peux-tu réessayer ? "
                "Si le problème persiste, contacte le support."
            )

    def _format_user_context(self, context: Dict) -> str:
        """Format user context for system prompt."""
        formatted = []

        if context.get("recent_symptoms"):
            formatted.append(
                f"Symptômes récents: {', '.join(context['recent_symptoms'])}"
            )

        if context.get("medications"):
            formatted.append(f"Traitements actuels: {', '.join(context['medications'])}")

        if context.get("last_crisis"):
            formatted.append(f"Dernière crise: {context['last_crisis']}")

        if context.get("ses_score"):
            formatted.append(f"Score SES: {context['ses_score']}/10")

        return "\n".join(formatted)

    async def detect_emergency(self, message: str) -> bool:
        """
        Detect if message contains emergency symptoms.

        Args:
            message: User's message

        Returns:
            True if emergency detected
        """
        emergency_keywords = [
            "douleur thoracique",
            "difficultés respiratoires",
            "respirer",
            "fièvre",
            "température",
            "douleur abdominale",
            "maux de tête sévères",
            "priapisme",
            "faiblesse",
            "troubles de la parole",
            "vision floue",
            "urgence",
            "144",
        ]

        message_lower = message.lower()
        for keyword in emergency_keywords:
            if keyword in message_lower:
                logger.warning(f"Emergency keyword detected: {keyword}")
                return True

        return False

    async def classify_intent(self, message: str) -> str:
        """
        Classify user's intent.

        Args:
            message: User's message

        Returns:
            Intent category: symptom_report, appointment, question, medication, support
        """
        # Simple keyword-based classification (can be enhanced with Claude)
        message_lower = message.lower()

        if any(
            word in message_lower
            for word in ["rendez-vous", "consultation", "médecin", "hug@home"]
        ):
            return "appointment"

        if any(
            word in message_lower
            for word in ["douleur", "mal", "fatigue", "fièvre", "symptôme"]
        ):
            return "symptom_report"

        if any(
            word in message_lower
            for word in ["médicament", "traitement", "hydroxyurea", "folicine"]
        ):
            return "medication"

        if any(
            word in message_lower
            for word in ["triste", "déprimé", "difficile", "peur", "anxieux"]
        ):
            return "emotional_support"

        return "general_question"
