"""Test individual components without requiring external services."""
import sys
from loguru import logger

logger.remove()
logger.add(sys.stdout, format="<level>{level: <8}</level> | {message}")

def test_imports():
    """Test if all modules can be imported."""
    print("\n🔍 Testing imports...")
    try:
        from src.config import settings
        print("  ✅ Config module")

        from src.models.database import Base, User, Conversation
        print("  ✅ Database models")

        from src.llm.agent import TrevorAgent
        print("  ✅ LLM agent")

        # Skip RAG for now as it requires downloads
        # from src.llm.rag import MedicalKnowledgeRAG
        # print("  ✅ RAG system")

        from src.integrations.email import EmailService
        print("  ✅ Email service")

        print("✅ All core imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_models():
    """Test database model creation."""
    print("\n🔍 Testing database models...")
    try:
        from src.models.database import Base, User, Conversation, init_db
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Create in-memory SQLite database for testing
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Create test user
        test_user = User(
            telegram_id="123456",
            username="test_user",
            full_name="Test User",
            email="test@example.com"
        )
        session.add(test_user)
        session.commit()

        # Query it back
        user = session.query(User).filter_by(telegram_id="123456").first()
        assert user is not None
        assert user.username == "test_user"

        print("  ✅ User model creation and query")

        # Create conversation
        conv = Conversation(
            user_id=user.id,
            role="user",
            content="Test message",
            platform="telegram"
        )
        session.add(conv)
        session.commit()

        print("  ✅ Conversation model creation")

        session.close()
        print("✅ Database models work correctly!")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration loading."""
    print("\n🔍 Testing configuration...")
    try:
        from src.config import settings

        assert settings.database_url is not None
        print(f"  ✅ Database URL: {settings.database_url}")

        assert settings.environment == "testing"
        print(f"  ✅ Environment: {settings.environment}")

        assert settings.log_level == "INFO"
        print(f"  ✅ Log level: {settings.log_level}")

        print("✅ Configuration loading works!")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_initialization():
    """Test LLM agent can be initialized (without making API calls)."""
    print("\n🔍 Testing LLM agent initialization...")
    try:
        from src.llm.agent import TrevorAgent

        agent = TrevorAgent()
        assert agent is not None
        assert agent.model == "claude-3-5-haiku-20241022"
        assert agent.system_prompt is not None

        print(f"  ✅ Agent initialized with model: {agent.model}")
        print(f"  ✅ System prompt loaded ({len(agent.system_prompt)} chars)")

        # Test intent classification (doesn't need API)
        import asyncio
        intent = asyncio.run(agent.classify_intent("J'ai mal à la tête"))
        print(f"  ✅ Intent classification: '{intent}'")

        # Test emergency detection
        is_emergency = asyncio.run(agent.detect_emergency("douleur thoracique sévère"))
        assert is_emergency == True
        print(f"  ✅ Emergency detection: {is_emergency}")

        print("✅ LLM agent initialization works!")
        return True
    except Exception as e:
        print(f"❌ Agent error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_email_service():
    """Test email service initialization."""
    print("\n🔍 Testing email service...")
    try:
        from src.integrations.email import EmailService

        email_service = EmailService()
        assert email_service is not None
        assert email_service.from_email is not None

        print("  ✅ Email service initialized")
        print(f"  ✅ From email: {email_service.from_email.email}")

        # Note: We won't actually send emails without real API key
        print("  ℹ️  Skipping actual email send (requires valid API key)")

        print("✅ Email service initialization works!")
        return True
    except Exception as e:
        print(f"❌ Email service error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🤖 Trevor Bot 2.0 - Component Testing")
    print("=" * 60)
    print("\n⚠️  Note: Testing without Docker/API keys")
    print("   Only testing components that work offline")

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database Models", test_database_models),
        ("LLM Agent", test_agent_initialization),
        ("Email Service", test_email_service),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")

    print(f"\nScore: {passed}/{total} tests passed ({100*passed//total}%)")

    if passed == total:
        print("\n🎉 All offline tests passed!")
        print("\nNext steps:")
        print("  1. Get API keys:")
        print("     - Telegram: @BotFather")
        print("     - Anthropic: console.anthropic.com")
        print("     - SendGrid: sendgrid.com")
        print("  2. Update .env file with real API keys")
        print("  3. Deploy to Railway/Fly.io (includes Docker)")
        print("  4. Run: python main.py")
        return 0
    else:
        print("\n⚠️  Some tests failed.")
        print("   This is expected without Docker/API keys for some components.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
