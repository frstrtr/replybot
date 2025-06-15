"""Reply Keyboards for the Telegram Bot"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_main_menu() -> ReplyKeyboardMarkup:
    """Creates the main menu keyboard."""
    buttons = [[KeyboardButton(text="Start"), KeyboardButton(text="Help")]]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def create_business_menu() -> ReplyKeyboardMarkup:
    """Creates the business menu keyboard."""
    buttons = [
        [KeyboardButton(text="Business Feature 1")],
        [KeyboardButton(text="Business Feature 2")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def create_cancel_button() -> ReplyKeyboardMarkup:
    """Creates a cancel button keyboard."""
    buttons = [[KeyboardButton(text="Cancel")]]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_business_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard for business menu"""
    keyboard = [
        [KeyboardButton(text="Business Hours")],
        [KeyboardButton(text="Contact Us")],
        [KeyboardButton(text="Send Business Message")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
