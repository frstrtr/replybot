"""Main entry point for the Telegram bot using Aiogram framework."""

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError

import config as app_config  # Use an alias to avoid potential conflicts and clarify origin
from handlers import register_all_handlers
from middlewares.auth_middleware import AuthMiddleware

log_format = "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"

# More explicit setup:
root_logger = logging.getLogger() # Get the root logger

# Clear any existing handlers from the root logger
if root_logger.hasHandlers():
    root_logger.handlers.clear()

# Set the desired level on the root logger
root_logger.setLevel(logging.INFO)

# Create a stream handler to output to stdout (or stderr)
stream_handler = logging.StreamHandler(sys.stdout) # Change to sys.stderr if preferred
stream_handler.setLevel(logging.INFO) # Set level on handler as well

# Create a formatter
formatter = logging.Formatter(log_format) # The formatter uses the updated log_format
stream_handler.setFormatter(formatter)

# Add the handler to the root logger
root_logger.addHandler(stream_handler)

# Now, get your module-specific logger. It will inherit from the root logger's setup.
logger = logging.getLogger(__name__) # __name__ will be 'src.main' or '__main__'

# Test log immediately after setup
logger.info("Logging explicitly configured in main.py. Application starting...")
# --- End of Logging Setup ---


async def main():
    # Initialize bot and dispatcher
    default_props = DefaultBotProperties(parse_mode=ParseMode.HTML)
    # Use app_config for clarity if you aliased the import
    bot = Bot(token=app_config.BOT_TOKEN, default=default_props)

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
    """
    Setup comprehensive business information for the bot using Bot API.
    Ensure the corresponding variables are defined in your config.py (or .env).
    """
    try:
        # Basic Info
        if (
            hasattr(app_config, "BUSINESS_DESCRIPTION")
            and app_config.BUSINESS_DESCRIPTION
        ):
            await bot.set_my_description(description=app_config.BUSINESS_DESCRIPTION)
            logging.info("Business description set.")
        business_short_desc_val = getattr(
            app_config, "BUSINESS_SHORT_DESCRIPTION", None
        )
        if business_short_desc_val:
            await bot.set_my_short_description(
                short_description=business_short_desc_val
            )
            logging.info("Business short description set.")

        # Business Intro (Example)
        # To use this, define BUSINESS_INTRO_TITLE, BUSINESS_INTRO_MESSAGE,
        # and optionally BUSINESS_INTRO_STICKER_FILE_ID in your config
        # business_intro_title_val = getattr(app_config, "BUSINESS_INTRO_TITLE", None)
        # business_intro_message_val = getattr(app_config, "BUSINESS_INTRO_MESSAGE", None)

        # if business_intro_title_val and business_intro_message_val:
        #     intro_sticker_obj = None
        #     business_intro_sticker_file_id_val = getattr(
        #         app_config, "BUSINESS_INTRO_STICKER_FILE_ID", None
        #     )
        #     if business_intro_sticker_file_id_val:
        #         # Assuming 'tgs' format and a generic emoji. Adjust as needed.
        #         intro_sticker_obj = InputSticker(
        #             sticker=business_intro_sticker_file_id_val,
        #             format="tgs",
        #             emoji_list=["⭐"],
        #         )

        #     business_intro = BusinessIntro(
        #         title=business_intro_title_val,
        #         message=business_intro_message_val,
        #         sticker=intro_sticker_obj,
        #     )
        #     await bot.set_my_business_intro(intro=business_intro)
        #     logging.info("Business intro set.")

        # Business Location (Example)
        # To use this, define BUSINESS_LOCATION_LATITUDE, BUSINESS_LOCATION_LONGITUDE,
        # and BUSINESS_LOCATION_ADDRESS in your config
        # if (
        #     hasattr(app_config, "BUSINESS_LOCATION_LATITUDE")
        #     and hasattr(app_config, "BUSINESS_LOCATION_LONGITUDE")
        #     and hasattr(app_config, "BUSINESS_LOCATION_ADDRESS")
        # ):
        #     business_location = BusinessLocation(
        #         latitude=float(app_config.BUSINESS_LOCATION_LATITUDE),
        #         longitude=float(app_config.BUSINESS_LOCATION_LONGITUDE),
        #         address=app_config.BUSINESS_LOCATION_ADDRESS,
        #     )
        #     await bot.set_my_business_location(location=business_location)
        #     logging.info("Business location set.")

        # Business Opening Hours (Example - more complex structure)
        # To use this, define BUSINESS_OPENING_HOURS_TIME_ZONE and BUSINESS_OPENING_HOURS_INTERVALS (a list of dicts)
        # e.g., BUSINESS_OPENING_HOURS_INTERVALS = [{"opening_minute": 540, "closing_minute": 1080}] # 9 AM to 6 PM
        # See https://core.telegram.org/bots/api#businessopeninghoursinterval
        # if hasattr(app_config, "BUSINESS_OPENING_HOURS_TIME_ZONE") and hasattr(
        #     app_config, "BUSINESS_OPENING_HOURS_INTERVALS"
        # ):
        #     opening_hours = BusinessOpeningHours(
        #         time_zone_name=app_config.BUSINESS_OPENING_HOURS_TIME_ZONE,
        #         opening_hours=app_config.BUSINESS_OPENING_HOURS_INTERVALS,  # This should be a list of BusinessOpeningHoursInterval objects
        #     )
        #     # Note: You'll need to construct BusinessOpeningHoursInterval objects for the list above.
        #     # For simplicity, this example assumes app_config.BUSINESS_OPENING_HOURS_INTERVALS is already correctly formatted.
        #     # A more robust implementation would involve creating these objects from your config data.
        #     logging.info("Business opening hours set.")

        logging.info("Business information setup process completed.")
    except TelegramAPIError as e:
        logging.error(f"Failed to set up some business information: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
