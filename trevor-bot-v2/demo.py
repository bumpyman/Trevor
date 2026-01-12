"""Interactive demo mode - Test the bot without external services."""
import asyncio
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="<level>{message}</level>")


class MockBot:
    """Mock bot for testing locally without API keys."""

    def __init__(self):
        """Initialize mock bot."""
        from src.llm.agent import TrevorAgent
        self.agent = TrevorAgent()
        self.conversation_history = []

    async def detect_intent_and_emergency(self, message: str):
        """Show what the bot detects."""
        print(f"\n🔍 Analyzing: '{message}'")

        # Detect emergency
        is_emergency = await self.agent.detect_emergency(message)
        if is_emergency:
            print("🚨 EMERGENCY DETECTED!")
            print("   → Bot would recommend calling 144 or going to HUG urgences")

        # Detect intent
        intent = await self.agent.classify_intent(message)
        print(f"💡 Intent detected: {intent}")

        # Show what would happen
        if intent == "symptom_report":
            print("   → Bot would log symptom in database")
            print("   → Bot would ask follow-up questions")
            print("   → Bot would provide relevant medical advice")
        elif intent == "appointment":
            print("   → Bot would collect appointment details")
            print("   → Bot would send email to HUG hematology")
        elif intent == "medication":
            print("   → Bot would retrieve medication information")
            print("   → Bot would check adherence history")
        elif intent == "emotional_support":
            print("   → Bot would provide empathetic response")
            print("   → Bot would offer peer support options")
        else:
            print("   → Bot would search medical knowledge base")
            print("   → Bot would provide evidence-based answer")

        return intent, is_emergency


async def demo_mode():
    """Run interactive demo."""
    print("=" * 60)
    print("🤖 Trevor Bot 2.0 - Interactive Demo Mode")
    print("=" * 60)
    print("\nThis demo shows how the bot would respond to your messages.")
    print("No API keys needed - this runs 100% locally!\n")
    print("Type your messages in French or English.")
    print("Type 'quit' to exit.\n")
    print("=" * 60)

    bot = MockBot()

    # Show some examples first
    print("\n📚 Let me show you some examples first...\n")

    examples = [
        "J'ai mal à la tête depuis ce matin",
        "Je voudrais un rendez-vous urgent",
        "Douleur thoracique sévère",
        "Comment prévenir les crises?",
        "J'ai oublié mon traitement hier"
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n--- Example {i} ---")
        await bot.detect_intent_and_emergency(example)
        await asyncio.sleep(0.5)

    print("\n" + "=" * 60)
    print("\n✨ Now it's your turn! Type a message:\n")

    # Interactive mode
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Au revoir! See you next time!")
                break

            await bot.detect_intent_and_emergency(user_input)

            print("\n" + "-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


async def quick_test():
    """Quick automated test."""
    print("\n🧪 Quick Test Mode")
    print("=" * 60)

    bot = MockBot()

    test_cases = [
        ("Symptom report", "J'ai de la fièvre et je suis fatigué"),
        ("Emergency", "Douleur thoracique intense, difficultés à respirer"),
        ("Appointment", "Je voudrais prendre rendez-vous à HUG@Home"),
        ("Question", "Dois-je augmenter mon hydratation en été?"),
        ("Medication", "À quoi sert l'hydroxyurée?"),
    ]

    print("\nTesting different scenarios:\n")

    for name, message in test_cases:
        print(f"\n📝 Test: {name}")
        await bot.detect_intent_and_emergency(message)
        print()

    print("=" * 60)
    print("✅ All scenarios tested!")


def main():
    """Main entry point."""
    print("\nChoose a mode:")
    print("1. Interactive Demo (chat with the bot)")
    print("2. Quick Test (automated scenarios)")
    print("3. Both\n")

    try:
        choice = input("Enter choice (1/2/3): ").strip()
    except KeyboardInterrupt:
        print("\n\nBye!")
        return

    if choice == "1":
        asyncio.run(demo_mode())
    elif choice == "2":
        asyncio.run(quick_test())
    elif choice == "3":
        asyncio.run(quick_test())
        print("\n" + "=" * 60)
        print("\n🎮 Now let's go interactive!\n")
        asyncio.run(demo_mode())
    else:
        print("Invalid choice. Running interactive demo...")
        asyncio.run(demo_mode())


if __name__ == "__main__":
    main()
