"""Module for handling business connections and messages in a Telegram bot using aiogram."""

import logging
from aiogram import Router, Bot, Dispatcher
from aiogram.types import (
    Message,
    BusinessConnection,
    # BusinessMessagesDeleted,
    User,
    CallbackQuery,
)
import aiofiles # Import aiofiles
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramAPIError
import html
import os

# Import the configuration and menu modules
import config as app_config
from menu_config import get_menu_for_client
from keyboards.inline_keyboards import build_keyboard_from_config


# Define conversation states
class UserConversationState(StatesGroup):
    in_menu = State()
    in_support = State()


business_router = Router()

# Dictionary to store active business connections
active_business_connections: dict = {}

# --- Hardcoded Business Connection Details (Loaded from Config) ---
if app_config.HC_BUSINESS_CONNECTION_ID and app_config.HC_BUSINESS_OWNER_CHAT_ID:
    active_business_connections[app_config.HC_BUSINESS_CONNECTION_ID] = {
        "user_chat_id": app_config.HC_BUSINESS_OWNER_CHAT_ID,
        "user": User(id=app_config.HC_BUSINESS_OWNER_CHAT_ID, is_bot=False, first_name="Owner"),
    }
    logging.info(f"Initialized with business connection from config: ID='{app_config.HC_BUSINESS_CONNECTION_ID}'")

RESPONSES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static/responses'))


@business_router.business_connection()
async def handle_business_connection(business_connection: BusinessConnection, bot: Bot):
    """Handles BusinessConnection updates."""
    connection_id = business_connection.id
    user_chat_id = business_connection.user_chat_id
    is_enabled = business_connection.is_enabled

    logging.info(f"BusinessConnection Update: ID={connection_id}, UserChatID={user_chat_id}, IsEnabled={is_enabled}")

    if is_enabled:
        active_business_connections[connection_id] = {
            "user_chat_id": user_chat_id,
            "user": business_connection.user,
        }
        await bot.send_message(chat_id=user_chat_id, text=f"Business connection (ID: {connection_id}) is now active.")
    elif not is_enabled and connection_id in active_business_connections:
        del active_business_connections[connection_id]
        await bot.send_message(chat_id=user_chat_id, text=f"Business connection (ID: {connection_id}) has been disabled.")


@business_router.business_message()
async def handle_business_message(message: Message, bot: Bot, state: FSMContext):
    """Handles incoming messages via a Business Connection."""
    business_connection_id = message.business_connection_id
    client_user: User | None = message.from_user
    client_chat_id = message.chat.id

    if not business_connection_id or not client_user:
        return

    # --- Send menu only if explicitly requested or it's the first interaction ---
    current_state = await state.get_state()
    
    # Condition to send menu: /menu command, first message (state is None), or user is already in the menu.
    if (
        (message.text and message.text.strip().startswith('/menu'))
        or current_state is None
        or current_state == UserConversationState.in_menu
    ):
        if client_user.full_name != app_config.AUTHORIZED_FULL_NAME:
            menu_structure = get_menu_for_client(business_connection_id)
            main_menu_node = menu_structure.get("main_menu")
            
            if main_menu_node:
                keyboard = build_keyboard_from_config(main_menu_node["buttons"])
                await bot.send_message(
                    chat_id=client_chat_id,
                    text=main_menu_node["text"],
                    business_connection_id=business_connection_id,
                    reply_markup=keyboard,
                )
            await state.set_state(UserConversationState.in_menu)
            # If it was a /menu command, we don't need to notify the owner.
            if message.text and message.text.strip().startswith('/menu'):
                return
    
    # --- Notify business owner (runs for all messages that are not an explicit /menu command) ---
    connection_details = active_business_connections.get(business_connection_id)
    if connection_details and connection_details.get("user_chat_id"):
        owner_chat_id = connection_details["user_chat_id"]
        client_name_html = f"<a href='tg://user?id={client_user.id}'>{html.escape(client_user.full_name)}</a>"
        notification_text = (
            f"Received message from {client_name_html} (Chat ID: {client_chat_id}):\n"
            f"<i>{html.escape(message.text or '[No Text]')}</i>"
        )
        try:
            await bot.send_message(
                chat_id=owner_chat_id,
                text=notification_text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except TelegramAPIError as e:
            logging.error(f"Failed to notify business owner {owner_chat_id}: {e}")


@business_router.callback_query()
async def handle_tourism_menu_callback(callback: CallbackQuery, state: FSMContext):
    """
    Universal callback handler driven by the menu configuration.
    """
    await callback.answer()  # Acknowledge the query immediately to prevent timeouts

    business_connection_id = callback.message.business_connection_id
    if not business_connection_id:
        logging.error("Callback received without a business_connection_id.")
        return

    menu_structure = get_menu_for_client(business_connection_id)
    node_key = callback.data
    node = menu_structure.get(node_key)

    if not node:
        logging.warning(f"Unknown node key '{node_key}' for client '{business_connection_id}'.")
        return

    node_type = node.get("type")
    
    try:
        if node_type == "menu":
            text = node.get("text", "Меню")  # Default text

            # If a text_path is provided for a menu, try to load it.
            if "text_path" in node:
                client_response_path = os.path.join(RESPONSES_DIR, business_connection_id, node["text_path"])
                try: # Use aiofiles for async file reading
                    async with aiofiles.open(client_response_path, mode='r', encoding="utf-8") as f:
                        text = await f.read()
                except FileNotFoundError:
                    logging.warning(f"Menu text file not found: {client_response_path}. Using default text.")
                except OSError as e:
                    logging.error(f"Could not read menu text file {client_response_path}: {e}")

            keyboard = build_keyboard_from_config(node["buttons"])
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await state.set_state(UserConversationState.in_menu)

        elif node_type == "content":
            text = ""
            # Construct the client-specific path for the response file
            client_response_path = os.path.join(RESPONSES_DIR, business_connection_id, node["text_path"])
            
            try: # Use aiofiles for async file reading
                async with aiofiles.open(client_response_path, mode='r', encoding="utf-8") as f:
                    text = await f.read()
            except FileNotFoundError:
                logging.warning(f"Response file not found at client-specific path: {client_response_path}")
                text = "<i>Контент временно недоступен.</i>"
            except OSError as e:
                logging.error(f"Could not read response file {client_response_path}: {e}")
                text = "<i>Контент временно недоступен.</i>"

            file_id = node.get("file_id")
            back_to = node.get("back_to")
            is_final = node.get("is_final", False)

            # Set the state before sending the message
            if is_final:
                await state.set_state(UserConversationState.in_support)
            else:
                await state.set_state(UserConversationState.in_menu)

            keyboard = None
            if not is_final and back_to:
                if back_to == "main_menu":
                    # If "back" is the main menu, just show one button to go there.
                    nav_buttons = [{"text": "🏠 Главное меню", "target": "main_menu"}]
                else:
                    # For deeper menus, show both "Back" and "Home".
                    nav_buttons = [
                        {"text": "⬅️ Назад", "target": back_to},
                        {"text": "🏠 Главное меню", "target": "main_menu"}
                    ]
                keyboard = build_keyboard_from_config([nav_buttons])

            if file_id and file_id.startswith('http'):
                full_text = f"{text}\n\n{file_id}"
                await callback.message.edit_text(
                    full_text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                    disable_web_page_preview=False
                )
            elif file_id: # It's a photo ID
                if len(text) > 1024:
                    await callback.message.answer_photo(photo=file_id)
                    await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
                else:
                    await callback.message.answer_photo(photo=file_id, caption=text, reply_markup=keyboard, parse_mode="HTML")
                await callback.message.edit_reply_markup(reply_markup=None) # Clean up old message
            else: # Just text
                await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

    except TelegramAPIError as e:
        if "message is not modified" not in str(e):
            logging.error(f"API Error on callback '{node_key}': {e}", exc_info=True)


def register_business_handlers(dp: Dispatcher):
    dp.include_router(business_router)
