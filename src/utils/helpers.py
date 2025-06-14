def format_response(message: str) -> str:
    return message.strip().capitalize()

def log_error(error_message: str) -> None:
    with open('error_log.txt', 'a') as log_file:
        log_file.write(f"{error_message}\n")

def is_valid_command(command: str, valid_commands: list) -> bool:
    return command in valid_commands

def extract_user_id(message) -> int:
    return message.from_user.id if message.from_user else None

def create_keyboard(buttons: list) -> dict:
    from aiogram.types import ReplyKeyboardMarkup
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard