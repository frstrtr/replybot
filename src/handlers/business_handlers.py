"""Module for handling business connections and messages in a Telegram bot using aiogram."""

import logging
from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import (
    Message,
    BusinessConnection,
    BusinessMessagesDeleted,
    User,
    BusinessBotRights,
    CallbackQuery,
)
from aiogram.exceptions import TelegramAPIError
import html
import os

# Import the configuration module
import config as app_config

# from keyboards.reply_keyboards import get_tourism_main_keyboard
from keyboards.inline_keyboards import get_tourism_main_inline_keyboard, get_back_to_main_menu_keyboard, get_boats_submenu_keyboard

business_router = Router()

# Dictionary to store active business connections
# Key: business_connection_id (str)
# Value: dict containing "user_chat_id", "rights" (BusinessBotRights), and "user" (User)
active_business_connections: dict = {}

# --- Hardcoded Business Connection Details (Loaded from Config) ---
# These are used if the bot is intended for a single, known business account
# and persistent storage for connections isn't fully implemented.

# Define default rights for the hardcoded connection
# Adjust these if you know the specific rights for your connection.
hardcoded_rights = BusinessBotRights(
    can_reply=True,
    can_read_messages=True,
    # Set other rights as needed, defaulting to None or False if unsure
    can_delete_outgoing_messages=False,
    can_delete_all_messages=False,
    can_edit_name=False,
    can_edit_bio=False,
    can_edit_profile_photo=False,
    can_edit_username=False,
    can_change_gift_settings=False,
    can_view_gifts_and_stars=False,
    can_convert_gifts_to_stars=False,
    can_manage_stories=False,
)

# Pre-populate active_business_connections if config values are set
if app_config.HC_BUSINESS_CONNECTION_ID and app_config.HC_BUSINESS_OWNER_CHAT_ID:
    active_business_connections[app_config.HC_BUSINESS_CONNECTION_ID] = {
        "user_chat_id": app_config.HC_BUSINESS_OWNER_CHAT_ID,
        "rights": hardcoded_rights,  # Using the predefined rights object
        "user": User(
            id=app_config.HC_BUSINESS_OWNER_CHAT_ID,
            is_bot=False,
            first_name="Business Owner (from config)",
        ),  # Dummy User
    }
    logging.info(
        f"Initialized with business connection from config: "
        f"ID='{app_config.HC_BUSINESS_CONNECTION_ID}', OwnerChatID='{app_config.HC_BUSINESS_OWNER_CHAT_ID}'"
    )
else:
    logging.warning(
        "HC_BUSINESS_CONNECTION_ID or HC_BUSINESS_OWNER_CHAT_ID not found in config. "
        "Bot will rely solely on dynamic BusinessConnection updates."
    )
# --- End of Config-based Initialization ---

RESPONSES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static/responses'))


@business_router.business_connection()
async def handle_business_connection(business_connection: BusinessConnection, bot: Bot):
    """
    Handles BusinessConnection updates.
    A user has established, edited, or ended a Business Connection with the bot.
    This will override hardcoded data if a new connection event for the same ID occurs.
    """
    connection_id = business_connection.id
    user_chat_id = business_connection.user_chat_id
    is_enabled = business_connection.is_enabled
    rights = business_connection.rights

    logging.info(
        f"BusinessConnection Update Received: ID={connection_id}, UserChatID={user_chat_id}, "
        f"IsEnabled={is_enabled}, BotID={bot.id}"
    )
    if rights:
        rights_summary = ", ".join(
            f"{right_name}={getattr(rights, right_name)}"
            for right_name in [
                "can_reply",
                "can_read_messages",
                "can_delete_outgoing_messages",
                "can_delete_all_messages",
                "can_edit_name",
                "can_edit_bio",
                "can_edit_profile_photo",
                "can_edit_username",
                "can_change_gift_settings",
                "can_view_gifts_and_stars",
                "can_convert_gifts_to_stars",
                "can_transfer_and_upgrade_gifts",
                "can_transfer_stars",
                "can_manage_stories",
            ]
            if hasattr(rights, right_name) and getattr(rights, right_name) is not None
        )
        logging.info(f"Business Rights for {connection_id} from API: {rights_summary}")

    if is_enabled and rights:
        active_business_connections[connection_id] = {
            "user_chat_id": user_chat_id,
            "rights": rights,  # Use rights from the API event
            "user": business_connection.user,
        }
        logging.info(
            f"Updated/Set active_business_connections for {connection_id} from API event."
        )
        await bot.send_message(
            chat_id=user_chat_id,
            text=f"Business connection (ID: {connection_id}) is now active. Rights updated from API.",
        )
    elif not is_enabled:
        if connection_id in active_business_connections:
            del active_business_connections[connection_id]
            logging.info(
                f"Removed business connection {connection_id} from active store due to API event (is_enabled=False)."
            )
        await bot.send_message(
            chat_id=user_chat_id,
            text=f"Your business connection (ID: {connection_id}) has been disabled or removed via API event.",
        )
    else:
        logging.warning(
            f"Business connection {connection_id} update: is_enabled={is_enabled}, but rights are missing. Not updating store."
        )


@business_router.business_message()
async def handle_business_message(message: Message, bot: Bot):
    """
    Handles incoming messages via a Business Connection.
    These are messages from clients to the business account.
    """
    logging.info("--- handle_business_message TRIGGERED ---")
    logging.debug(
        f"Incoming Business Message Object: {message.model_dump_json(indent=2)}"
    )

    business_connection_id = message.business_connection_id
    # The 'user' who sent the message to the business account (the client)
    client_user: User | None = message.from_user
    # The chat where the message occurred (between client and business)
    client_chat_id = message.chat.id

    if not business_connection_id:
        logging.warning(
            "CRITICAL: Received business_message WITHOUT business_connection_id. Cannot process."
        )
        return

    logging.info(
        f"\nProcessing Business Message:\n"
        f"Business ConnectionID='{business_connection_id}', ClientChatID='{client_chat_id}', "
        f"ClientUser='{client_user.full_name if client_user else 'Unknown Client'}', Text:\n'{message.text}', "
    )

    logging.debug(
        f"Current active_business_connections state: {active_business_connections}"
    )
    connection_details = active_business_connections.get(business_connection_id)

    if not connection_details:
        logging.warning(
            f"No business connection found in store for ID: '{business_connection_id}'."
        )
        # If HC_BUSINESS_CONNECTION_ID was set but doesn't match, this log is important.
        # If it wasn't set, this is expected until a BusinessConnection update.
        return

    logging.debug(
        f"Found connection details for '{business_connection_id}': {connection_details}"
    )

    if "rights" not in connection_details or not connection_details["rights"]:
        logging.warning(
            f"Connection details for '{business_connection_id}' exist, but 'rights' are missing or empty."
        )
        return

    current_rights = connection_details["rights"]
    logging.info(
        f"Rights for connection '{business_connection_id}': can_reply={current_rights.can_reply}"
    )

    if (
        current_rights.can_reply
        and client_user.full_name != app_config.AUTHORIZED_FULL_NAME
    ):
        response_text = "Пожалуйста, выберите нужный вопрос ниже или задайте свой."
        try:
            await bot.send_message(
                chat_id=client_chat_id,
                text=response_text,
                business_connection_id=business_connection_id,
                reply_markup=get_tourism_main_inline_keyboard(),
            )
            logging.info(f"Sent tourism main menu to client in chat {client_chat_id}.")
        except TelegramAPIError as e:
            logging.error(f"Failed to send menu: {e}", exc_info=True)

        business_owner_chat_id = connection_details.get("user_chat_id")
        client_name = client_user.full_name if client_user else "A client"
        # Escape HTML special characters in the name
        safe_name = html.escape(client_name)
        client_link = ""
        android_link = ""
        apple_link = ""
        if client_user:
            client_link = f"tg://user?id={client_user.id}"
            android_link = f"tg://openmessage?user_id={client_user.id}"
            apple_link = f"https://t.me/@id{client_user.id}"
            client_name_html = f"<a href='{client_link}'>{safe_name}</a>"
        else:
            client_name_html = safe_name

        try:
            await bot.send_message(
                chat_id=business_owner_chat_id,
                text=(
                    f"FYI: Received a message from {client_name_html} in chat {client_chat_id} (with your business): "
                    f"'{html.escape(message.text or '')}'.\n"
                    f"I can reply directly as 'can_reply' right is currently True for this connection.\n"
                    f"{client_link}\n"
                    f"{android_link}\n"
                    f"{apple_link}"
                ),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            logging.info(
                f"Notified business owner ({business_owner_chat_id}) about message from client."
            )
        except TelegramAPIError as e:
            logging.error(
                f"ERROR: Failed to notify business owner {business_owner_chat_id}: {e}",
                exc_info=True,
            )

    elif (
        current_rights.can_reply is False
        and client_user.full_name != app_config.AUTHORIZED_FULL_NAME
    ):
        logging.info(
            f"Bot cannot reply for business connection '{business_connection_id}' as 'can_reply' is False."
        )
        business_owner_chat_id = connection_details.get("user_chat_id")
        client_name = client_user.full_name if client_user else "A client"
        # Escape HTML special characters in the name
        safe_name = html.escape(client_name)
        client_link = ""
        android_link = ""
        apple_link = ""
        if client_user:
            client_link = f"tg://user?id={client_user.id}"
            android_link = f"tg://openmessage?user_id={client_user.id}"
            apple_link = f"https://t.me/@id{client_user.id}"
            client_name_html = f"<a href='{client_link}'>{safe_name}</a>"
        else:
            client_name_html = safe_name

        try:
            await bot.send_message(
                chat_id=business_owner_chat_id,
                text=(
                    f"FYI: Received a message from {client_name_html} in chat {client_chat_id} (with your business): "
                    f"'{html.escape(message.text or '')}'.\n"
                    f"I cannot reply directly as 'can_reply' right is currently False for this connection.\n"
                    f"{client_link}\n"
                    f"{android_link}\n"
                    f"{apple_link}"
                ),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            logging.info(
                f"Notified business owner ({business_owner_chat_id}) about unanswerable message from client."
            )
        except TelegramAPIError as e:
            logging.error(
                f"ERROR: Failed to notify business owner {business_owner_chat_id}: {e}",
                exc_info=True,
            )


@business_router.edited_business_message(
    F.business_message
)  # Handle edited business messages
async def handle_edited_business_message(message: Message, bot: Bot):
    """Handles edited messages in a Business Connection.
    This is triggered when a client edits their message in the business chat.
    """
    business_connection_id = message.business_connection_id
    client_chat_id = message.chat.id
    logging.info(
        f"Edited Business Message: ConnectionID={business_connection_id}, ClientChatID={client_chat_id}, "
        f"New Text='{message.text}'"
    )
    # Add logic to process edited messages if needed, similar to handle_business_message
    await bot.send_message(
        chat_id=client_chat_id,
        text=f"Your message was edited: {message.text}",
        business_connection_id=business_connection_id,  # Ensure this is sent on behalf of the business
    )


@business_router.deleted_business_messages()
async def handle_deleted_business_messages(event: BusinessMessagesDeleted, bot: Bot):
    """
    Handles when messages are deleted from a connected business account.
    """
    logging.info(
        f"Business messages deleted: ConnectionID={event.business_connection_id}, "
        f"ChatID={event.chat.id}, MessageIDs={event.message_ids}"
    )
    # You might want to notify the business owner or log this for auditing.
    connection_details = active_business_connections.get(event.business_connection_id)
    if connection_details:
        business_owner_chat_id = connection_details.get("user_chat_id")
        if business_owner_chat_id:
            await bot.send_message(
                chat_id=business_owner_chat_id,
                text=f"{len(event.message_ids)} message(s) were deleted in your managed chat {event.chat.id}.",
            )


@business_router.callback_query()
async def handle_tourism_menu_callback(callback: CallbackQuery):
    """
    Handles callbacks from the main tourism inline keyboard.
    - If a user clicks an info button (e.g., FAQ, Prices), it shows the relevant text
      and a keyboard with "Back" and "Main Menu" buttons.
    - If a user clicks "Back" or "Main Menu", it returns to the full main menu.
    """
    data = callback.data

    # Handler for "Back" and "Main Menu" buttons to return to the main keyboard
    if data == "main_menu" or data == "back":
        try:
            await callback.message.edit_text(
                "Вы вернулись в главное меню.",
                reply_markup=get_tourism_main_inline_keyboard(),
            )
        except TelegramAPIError as e:
            if "message is not modified" in str(e):
                # Just answer the callback to remove the loading state
                await callback.answer()
                return
            else:
                logging.error(f"Failed to edit main menu: {e}", exc_info=True)
        await callback.answer()
        return

    # Словарь: callback_data -> (текст, file_id или None)
    text_and_image_responses = {
        "faq": ("Здесь будут ответы на часто задаваемые вопросы.", None),
        "prices": ("Это информация о наших ценах.", None),
        "contacts": ("Наши контактные данные: ...", None),
        "excursions": ("Информация о доступных экскурсиях.", None),
        "boats": ("Информация об аренде лодок.", None),
        "fishing": ("Все о рыбалке с нами.", None),
        "surfing": ("Информация о серфинге.", None),
        "whales": ("Все о китах и дельфинах.", None),
        "reviews": ("Отзывы наших довольных клиентов.", None),
        "about": ("Краткая информация о нашей компании.", None),
        "support": ("Свяжитесь с нашей службой поддержки.", None),
        "help": ("Раздел помощи.", None),
        "boat1": ("Информация о лодке 1.", None),
        "boat2": ("Информация о лодке 2.", None),
        "boat3": ("Информация о лодке 3.", None),
        "boat4": ("Информация о лодке 4.", None),
        "boats_back": ("Выберите тип лодки:", None),  # For the boats submenu
    }

    response = text_and_image_responses.get(data)

    # For all buttons except help, back, main_menu, use text from html files
    if response:
        text, file_id = response
        if data in ("help", "back", "main_menu"):
            if data == "help":
                await callback.message.edit_text(
                    "Зову оператора! Для возврата к меню используйте команду /menu"
                )
                await callback.answer()
                return
            # back/main_menu handled above
        elif data == "boats":
            await callback.message.edit_text(
                "Выберите тип лодки:",
                reply_markup=get_boats_submenu_keyboard()
            )
            await callback.answer()
            return
        elif data in ("boat1", "boat2", "boat3", "boat4"):
            await callback.message.edit_text(
                f"Информация о {data}",
                reply_markup=get_back_to_main_menu_keyboard(back_callback_data="boats")
            )
            await callback.answer()
            return
        else:
            # Try to load HTML from file
            try:
                with open(os.path.join(RESPONSES_DIR, f"{data}.html"), encoding="utf-8") as f:
                    text = f.read()
            except OSError as e:
                logging.error(f"Failed to load response for {data}: {e}")
                text = "<i>Ответ временно недоступен</i>"
        if file_id and data not in ("help", "back", "main_menu"):
            try:
                await callback.message.answer_photo(
                    photo=file_id,
                    caption=text,
                    reply_markup=get_back_to_main_menu_keyboard(),
                    parse_mode="HTML"
                )
            except TelegramAPIError as e:
                logging.error(f"Failed to send photo: {e}. Sending text only.", exc_info=True)
                await callback.message.edit_text(
                    text,
                    reply_markup=get_back_to_main_menu_keyboard(),
                    parse_mode="HTML"
                )
            await callback.answer()
        elif data == "boats_back":
            try:
                await callback.message.edit_text(
                    "Выберите тип лодки:",
                    reply_markup=get_boats_submenu_keyboard()
                )
            except TelegramAPIError as e:
                if "message is not modified" in str(e):
                    await callback.answer()
                    return
                else:
                    logging.error(f"Failed to edit boats submenu: {e}", exc_info=True)
            await callback.answer()
            return
        elif data not in ("help", "back", "main_menu"):
            await callback.message.edit_text(
                text,
                reply_markup=get_back_to_main_menu_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()

    else:
        await callback.answer("Неизвестная команда.")


def register_business_handlers(
    dp: Dispatcher,
):  # This is for the new Business API events
    dp.include_router(business_router)
