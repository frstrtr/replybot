from aiogram import Dispatcher
from .common import register_common_handlers
from .business_features import register_business_handlers
from .user_commands import register_user_command_handlers

def register_all_handlers(dp: Dispatcher):
    """Register all handlers for the bot"""
    # The order matters: common handlers should be registered last
    register_business_handlers(dp)
    register_user_command_handlers(dp)
    register_common_handlers(dp)