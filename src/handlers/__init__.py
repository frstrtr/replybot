"""Module for registering all handlers in the bot"""
from aiogram import Dispatcher
from .common import register_common_handlers
from .user_commands import register_user_command_handlers
from .business_handlers import register_business_handlers  # For Business API events
from .business_features import (
    register_business_command_handlers,
)  # For /business command features


def register_all_handlers(dp: Dispatcher):
    """Register all handlers for the bot"""
    # Order can be important.
    # Business API event handlers (specific updates)
    register_business_handlers(dp)

    # Command-based business features
    register_business_command_handlers(dp)

    # General user commands
    register_user_command_handlers(dp)

    # Fallback handlers last
    register_common_handlers(dp)
