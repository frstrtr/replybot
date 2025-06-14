from aiogram import types
from aiogram.dispatcher import Dispatcher

async def start_command(message: types.Message):
    await message.answer("Welcome to the Business Bot! How can I assist you today?")

async def help_command(message: types.Message):
    await message.answer("Here are the commands you can use:\n/start - Start the bot\n/help - Get help") 

def register_user_commands(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])