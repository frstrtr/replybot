"""Module for handling business connections and messages in a Telegram bot using aiogram."""

import logging
from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message, BusinessConnection, BusinessMessagesDeleted, User

business_router = Router()

# IMPORTANT: For a production bot, `active_business_connections` MUST be stored persistently
# (e.g., in a database like PostgreSQL with asyncpg, or a Redis cache).
# The current in-memory dictionary will lose all connection data if the bot restarts,
# potentially disrupting service until new BusinessConnection updates are received.
active_business_connections = {}  # Simple in-memory store for demo


@business_router.business_connection()
async def handle_business_connection(business_connection: BusinessConnection, bot: Bot):
    """
    Handles BusinessConnection updates.
    A user has established, edited, or ended a Business Connection with the bot.
    """
    connection_id = business_connection.id
    user_chat_id = business_connection.user_chat_id
    is_enabled = business_connection.is_enabled
    rights = business_connection.rights  # Use the rights object

    logging.info(
        f"BusinessConnection Update: ID={connection_id}, UserChatID={user_chat_id}, "
        f"IsEnabled={is_enabled}, BotID={bot.id}"
    )
    if rights:
        # Log all available rights from the BusinessBotRights object
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
        logging.info(f"Business Rights for {connection_id}: {rights_summary}")

    if is_enabled and rights:
        active_business_connections[connection_id] = {
            "user_chat_id": user_chat_id,
            "rights": rights,  # Store the whole rights object
            "user": business_connection.user,  # Store user info if needed
        }
        await bot.send_message(
            chat_id=user_chat_id,  # Send to the user who connected the bot
            text=f"Thank you for connecting your business account! Connection ID: {connection_id}.\n"
            f"I can reply on your behalf: {rights.can_reply}.\n"
            f"I can read messages: {rights.can_read_messages}.",
        )
    elif not is_enabled:
        if connection_id in active_business_connections:
            del active_business_connections[connection_id]
        await bot.send_message(
            chat_id=user_chat_id,
            text=f"Your business connection (ID: {connection_id}) has been disabled or removed.",
        )
    else:
        logging.warning(
            f"Business connection {connection_id} status: is_enabled={is_enabled}, but rights are missing."
        )


@business_router.business_message()  # This filter is correct for business messages
async def handle_business_message(message: Message, bot: Bot):
    """
    Handles incoming messages via a Business Connection.
    These are messages from clients to the business account.
    """
    logging.info(f"--- handle_business_message TRIGGERED ---")
    # Log the entire incoming message object for detailed inspection
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
        f"Processing Business Message: ConnectionID='{business_connection_id}', ClientChatID='{client_chat_id}', "
        f"ClientUser='{client_user.full_name if client_user else 'Unknown Client'}', Text='{message.text}'"
    )

    logging.debug(
        f"Current active_business_connections state: {active_business_connections}"
    )
    connection_details = active_business_connections.get(business_connection_id)

    if not connection_details:
        logging.warning(
            f"No active business connection found in local store for ID: '{business_connection_id}'. "
            f"Bot may have restarted or connection was not properly established/logged."
        )
        # Optionally, you could try to inform the business owner if you had a way to get their user_chat_id
        # without relying on active_business_connections, but that's tricky.
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

    if current_rights.can_reply:
        # Your response logic. For now, let's use a simple echo.
        # You can replace this with more complex logic (keyword matching, AI, etc.)
        response_text = f"Business Echo: {message.text}"

        try:
            await bot.send_message(
                chat_id=client_chat_id,  # Send to the client's chat with the business
                text=response_text,
                business_connection_id=business_connection_id,  # Crucial for sending on behalf of the business
            )
            logging.info(
                f"SUCCESS: Replied to client in chat {client_chat_id} via business connection {business_connection_id}. Text: '{response_text}'"
            )
        except Exception as e:
            logging.error(
                f"ERROR: Failed to send message via business connection {business_connection_id} to chat {client_chat_id}: {e}",
                exc_info=True,
            )
    else:
        logging.info(
            f"Bot cannot reply for business connection '{business_connection_id}' as 'can_reply' is False."
        )
        business_owner_chat_id = connection_details.get("user_chat_id")
        if business_owner_chat_id:
            client_name = client_user.full_name if client_user else "A client"
            try:
                await bot.send_message(
                    chat_id=business_owner_chat_id,  # Notify the business owner directly
                    text=f"FYI: Received a message from {client_name} in chat {client_chat_id} (with your business): '{message.text}'. "
                    f"I cannot reply directly as 'can_reply' right is currently False for this connection.",
                )
                logging.info(
                    f"Notified business owner ({business_owner_chat_id}) about unanswerable message from client."
                )
            except Exception as e:
                logging.error(
                    f"ERROR: Failed to notify business owner {business_owner_chat_id}: {e}",
                    exc_info=True,
                )


@business_router.edited_message(F.business_message)  # Handle edited business messages
async def handle_edited_business_message(message: Message, bot: Bot):
    business_connection_id = message.business_connection_id
    client_chat_id = message.chat.id
    logging.info(
        f"Edited Business Message: ConnectionID={business_connection_id}, ClientChatID={client_chat_id}, "
        f"New Text='{message.text}'"
    )
    # Add logic to process edited messages if needed, similar to handle_business_message


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


def register_business_handlers(
    dp: Dispatcher,
):  # This is for the new Business API events
    dp.include_router(business_router)
