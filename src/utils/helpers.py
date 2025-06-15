def format_response(message: str) -> str:
    return message.strip().capitalize()

def log_error(error_message: str) -> None:
    # Consider using the logging module for more robust error logging
    import logging
    logging.error(error_message, exc_info=True) # exc_info=True can add stack trace
    # Fallback to file logging if needed, but logging module is preferred
    # with open('error_log.txt', 'a') as log_file:
    #     log_file.write(f"{error_message}\n")

def is_valid_command(command: str, valid_commands: list) -> bool:
    return command in valid_commands

def extract_user_id(message: "types.Message") -> int | None: # Added type hint for Message
    from aiogram import types # Local import for type hint
    return message.from_user.id if message and message.from_user else None

def create_keyboard(button_texts: list[str]) -> "ReplyKeyboardMarkup": # Corrected type hint
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton # Ensure types are imported
    # Create KeyboardButton objects from the list of texts
    kb_buttons = [KeyboardButton(text=text) for text in button_texts]
    
    # The keyboard layout for ReplyKeyboardMarkup is a list of rows,
    # where each row is a list of KeyboardButton objects.
    # We'll place all buttons from kb_buttons into a single row.
    # If kb_buttons is empty (i.e., button_texts was empty),
    # an empty list is used for the keyboard layout, resulting in an empty keyboard.
    initial_keyboard_layout = [kb_buttons] if kb_buttons else []
    
    keyboard = ReplyKeyboardMarkup(keyboard=initial_keyboard_layout, resize_keyboard=True)
    # The buttons are now included in the initial_keyboard_layout passed to the constructor,
    # so the previous keyboard.add(*kb_buttons) call is no longer needed.
    return keyboard