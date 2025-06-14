from aiogram import types, Router, Dispatcher, Bot
from aiogram.filters import CommandStart, Command, CommandObject
import logging

# Create a new Router instance
router = Router()

@router.message(CommandStart(deep_link=True, deep_link_encoded=False))
async def start_command_deeplink(message: types.Message, command: CommandObject, bot: Bot):
    """Handles /start command, potentially with a deep link."""
    args = command.args
    logging.info(f"Received /start command with args: {args} from user {message.from_user.id}")

    if args and args.startswith("bizChat"):
        try:
            business_user_chat_id = args.replace("bizChat", "")
            # You might want to validate if business_user_chat_id is an integer
            # And potentially store this linkage or perform actions
            await message.answer(
                f"Welcome, Business User from chat {business_user_chat_id}!\n"
                f"You've been redirected from managing a chat. How can I assist with your business setup?"
            )
            # Example: Send a message to the business user who clicked "Manage Bot"
            # This message.chat.id is the chat between the bot and the business user.
            # The business_user_chat_id is the ID of the chat the business user was managing.
            logging.info(f"Business user {message.from_user.id} (chatting in {message.chat.id}) "
                         f"was managing bizChatID: {business_user_chat_id}")

        except ValueError:
            await message.answer("Welcome to the Business Bot! Invalid deep link format.")
    else:
        # Standard /start command without specific deep link
        await start_command(message) # Call the non-deeplink version

@router.message(CommandStart())
async def start_command(message: types.Message):
    """Handles /start command without deep link."""
    await message.answer("Welcome to the Business Bot! How can I assist you today?")

@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "Here are the commands you can use:\n"
        "/start - Start the bot\n"
        "/help - Get help\n"
        "If you are a Telegram Business user, connect this bot via @BotFather (enable Business Mode) "
        "to manage client interactions."
    )

def register_user_command_handlers(dp: Dispatcher):
    dp.include_router(router)