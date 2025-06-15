from aiogram import Dispatcher
from .common import register_common_handlers
from .user_commands import register_user_command_handlers
from .business_handlers import register_business_handlers

def register_all_handlers(dp: Dispatcher):
    """Register all handlers for the bot"""
    # Order can be important. Specific business handlers first.
    register_business_handlers(dp) # For BusinessConnection, business_message
    register_user_command_handlers(dp) # For /start, /help
    register_common_handlers(dp) # Fallback handlers last
