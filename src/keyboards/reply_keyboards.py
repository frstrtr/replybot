from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Start")
    button2 = KeyboardButton("Help")
    keyboard.add(button1, button2)
    return keyboard

def create_business_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Business Feature 1")
    button2 = KeyboardButton("Business Feature 2")
    keyboard.add(button1, button2)
    return keyboard

def create_cancel_button():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Cancel")
    keyboard.add(button)
    return keyboard

def get_business_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard for business menu"""
    keyboard = [
        [KeyboardButton(text="Business Hours")],
        [KeyboardButton(text="Contact Us")],
        [KeyboardButton(text="Send Business Message")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)