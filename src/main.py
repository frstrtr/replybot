import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.token import TokenValidationError

import config
from handlers import register_all_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.bot = bot

    # Register all handlers
    register_all_handlers(dp)

    # Set up business info for the bot
    await setup_business_info(bot)

    # Start polling
    logging.info("Starting bot")
    await dp.start_polling()


async def setup_business_info(bot: Bot):
    """Setup business features for the bot using Bot API"""
    from config import BUSINESS_CONTACT_EMAIL, BUSINESS_HOURS, BUSINESS_DESCRIPTION

    try:
        # Set business info using Telegram Bot API
        await bot.set_my_description(description=BUSINESS_DESCRIPTION)

        # You could set more business information when available in the API
        # This is a simplified version as the full business API features
        # would require specific implementation

        logging.info("Business information has been set up successfully")
    except Exception as e:
        logging.error(f"Failed to set up business information: {e}")


if __name__ == "__main__":
    asyncio.run(main())
