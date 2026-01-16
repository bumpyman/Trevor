"""Test script to verify Trevor Bot setup."""
import sys
import asyncio
from loguru import logger

logger.remove()
logger.add(sys.stdout, format="<level>{level: <8}</level> | {message}")


async def test_imports():
    """Test if all modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from src.config import settings
        from src.models.database import init_db, SessionLocal
        from src.llm.agent import TrevorAgent
        from src.llm.rag import MedicalKnowledgeRAG
        from src.fhir.client import TrevorFHIRClient
        from src.integrations.email import EmailService

        print("  ✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False


async def test_database():
    """Test database connection."""
    print("\n🔍 Testing database...")
    try:
        from src.models.database import init_db, SessionLocal

        init_db()
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("  ✅ Database connection successful")
        return True
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False


async def test_fhir():
    """Test FHIR server connection."""
    print("\n🔍 Testing FHIR server...")
    try:
        import httpx

        response = httpx.get("http://localhost:8080/fhir/metadata", timeout=5)
        if response.status_code == 200:
            print("  ✅ FHIR server is running")
            return True
        else:
            print(f"  ❌ FHIR server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ FHIR server error: {e}")
        print("  💡 Tip: Check if Docker services are running: docker ps")
        return False


async def test_rag():
    """Test RAG system."""
    print("\n🔍 Testing RAG system...")
    try:
        from src.llm.rag import MedicalKnowledgeRAG, initialize_knowledge_base

        rag = MedicalKnowledgeRAG()

        # Initialize if empty
        stats = rag.get_collection_stats()
        if stats["total_documents"] == 0:
            print("  📚 Initializing knowledge base...")
            initialize_knowledge_base(rag)
            stats = rag.get_collection_stats()

        print(f"  ✅ RAG system initialized ({stats['total_documents']} documents)")

        # Test retrieval
        results = rag.retrieve("hydratation", n_results=1)
        if results:
            print(f"  ✅ Document retrieval working")
            return True
        else:
            print("  ⚠️  No documents found in retrieval test")
            return False
    except Exception as e:
        print(f"  ❌ RAG system error: {e}")
        return False


async def test_llm():
    """Test LLM agent."""
    print("\n🔍 Testing LLM agent...")
    try:
        from src.llm.agent import TrevorAgent

        agent = TrevorAgent()

        # Test a simple conversation
        response = await agent.chat(
            message="Bonjour",
            conversation_history=[],
            user_context=None,
            retrieved_knowledge=None,
        )

        if response and len(response) > 10:
            print(f"  ✅ LLM agent responding (response length: {len(response)} chars)")
            print(f"  💬 Sample response: {response[:100]}...")
            return True
        else:
            print("  ❌ LLM response too short or empty")
            return False
    except Exception as e:
        print(f"  ❌ LLM agent error: {e}")
        if "api_key" in str(e).lower():
            print("  💡 Tip: Check your ANTHROPIC_API_KEY in .env file")
        return False


async def test_config():
    """Test configuration."""
    print("\n🔍 Testing configuration...")
    try:
        from src.config import settings

        checks = {
            "Telegram token": bool(settings.telegram_bot_token),
            "Anthropic API key": bool(settings.anthropic_api_key),
            "SendGrid API key": bool(settings.sendgrid_api_key),
            "Database URL": bool(settings.database_url),
            "FHIR URL": bool(settings.fhir_base_url),
        }

        all_ok = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {'configured' if result else 'MISSING'}")
            if not result:
                all_ok = False

        if all_ok:
            print("  ✅ All required configuration present")
        else:
            print("  💡 Tip: Check your .env file")

        return all_ok
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🤖 Trevor Bot 2.0 - Setup Verification")
    print("=" * 60)

    tests = [
        ("Configuration", test_config),
        ("Imports", test_imports),
        ("Database", test_database),
        ("FHIR Server", test_fhir),
        ("RAG System", test_rag),
        ("LLM Agent", test_llm),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
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

    print(f"\nScore: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your Trevor Bot is ready to run!")
        print("\nNext steps:")
        print("  1. Run: python main.py")
        print("  2. Open Telegram and message your bot")
        print("  3. Send /start to begin")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before running the bot.")
        print("\nCommon fixes:")
        print("  - Missing config: Edit .env file with your API keys")
        print("  - Database error: Run 'docker-compose up -d'")
        print("  - FHIR error: Wait for services to start, then try again")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
