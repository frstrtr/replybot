import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # Import DefaultBotProperties

from src import config  # Ensure src. is used if running from project root
from src.handlers import register_all_handlers
from src.middlewares.auth_middleware import AuthMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main():
    # Initialize bot and dispatcher
    # Use DefaultBotProperties for parse_mode
    default_props = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=config.BOT_TOKEN, default=default_props)  # Updated this line

    dp = Dispatcher(storage=MemoryStorage())

    # Register middleware
    # If AuthMiddleware required arguments (e.g., db_pool), they would be passed here.
    dp.update.outer_middleware(AuthMiddleware())

    # Register all handlers
    register_all_handlers(dp)

    # Set up business info for the bot
    await setup_business_info(bot)

    # Start polling
    logging.info("Starting bot")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()  # Gracefully close bot session


async def setup_business_info(bot: Bot):
    """Setup business features for the bot using Bot API"""
    from src.config import BUSINESS_DESCRIPTION  # Using src. prefix for consistency

    try:
        # Set business info using Telegram Bot API
        await bot.set_my_description(description=BUSINESS_DESCRIPTION)

        # For more business features, refer to Telegram Bot API documentation:
        # https://core.telegram.org/bots/api#setmybusinessintro
        # https://core.telegram.org/bots/api#setmybusinesslocation
        # https://core.telegram.org/bots/api#setmybusinessopeninghours
        # Aiogram might provide direct methods or you can use bot.request(...)

        logging.info("Business information (description) has been set up successfully")
    except Exception as e:
        logging.error(f"Failed to set up business information: {e}")


if __name__ == "__main__":
    asyncio.run(main())
