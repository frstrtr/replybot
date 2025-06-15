from aiogram import types, Router, Dispatcher
import logging # Added for logging

# Create a new Router instance for common handlers
router = Router()

# The send_welcome and send_help functions from the original file are not registered here
# as /start and /help are typically handled by user_commands.py.
# If they were meant for other purposes, they'd need their own registration logic.

@router.message()
async def handle_unknown_message(message: types.Message):
    """
    Handles any message that wasn't caught by other more specific handlers.
    This works because the common_router is registered last.
    """
    logging.info(f"Received an unhandled message from {message.from_user.id}: {message.text}")
    await message.answer("Sorry, I didn't understand that. Type /help for a list of commands.")

def register_common_handlers(dp: Dispatcher):
    """Register common handlers for the bot. This router should be registered last."""
    dp.include_router(router)