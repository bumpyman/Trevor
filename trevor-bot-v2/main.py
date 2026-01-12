"""Main entry point for Trevor Bot."""
import asyncio
import sys
from loguru import logger
from src.bot.platforms.telegram_bot import TelegramBot


def setup_logging():
    """Configure logging."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    logger.add(
        "logs/trevor_bot_{time}.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level="DEBUG",
    )


async def main():
    """Main function to start the bot."""
    setup_logging()

    logger.info("=" * 60)
    logger.info("🤖 Starting Trevor Bot - AI Health Companion")
    logger.info("=" * 60)

    try:
        # Create and run Telegram bot
        bot = TelegramBot()
        await bot.run()

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
