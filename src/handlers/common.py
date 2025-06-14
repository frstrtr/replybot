from aiogram import types, Dispatcher

async def send_welcome(message: types.Message):
    await message.answer("Welcome to our Telegram Bot! How can I assist you today?")

async def send_help(message: types.Message):
    help_text = (
        "Here are the commands you can use:\n"
        "/start - Start the bot\n"
        "/help - Get help information\n"
        # Add more commands as needed
    )
    await message.answer(help_text)

async def handle_unknown_command(message: types.Message):
    await message.answer("Sorry, I didn't understand that command. Please use /help to see the available commands.")

def register_common_handlers(dp: Dispatcher):
    """Register common handlers for the bot"""
    # Add your common handlers registration code here
    pass