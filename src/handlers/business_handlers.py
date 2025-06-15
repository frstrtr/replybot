import logging
from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message, BusinessConnection
from aiogram.filters import CommandObject # For deep link args

business_router = Router()

# In a production bot, you'd store this information persistently (e.g., Redis, DB)
# keyed by business_connection.id or business_connection.user_chat_id
# For this example, we'll just log it.
active_business_connections = {} # Simple in-memory store for demo

@business_router.business_connection()
async def handle_business_connection(business_connection: BusinessConnection, bot: Bot):
    """
    Handles BusinessConnection updates.
    A user has established, edited, or ended a Business Connection with the bot.
    """
    connection_id = business_connection.id
    user_chat_id = business_connection.user_chat_id
    can_reply = business_connection.can_reply
    is_enabled = business_connection.is_enabled
    
    logging.info(
        f"BusinessConnection Update: ID={connection_id}, UserChatID={user_chat_id}, "
        f"CanReply={can_reply}, IsEnabled={is_enabled}, BotID={bot.id}"
    )

    if is_enabled:
        active_business_connections[connection_id] = {
            "user_chat_id": user_chat_id,
            "can_reply": can_reply,
            # You might want to store other details from business_connection object
        }
        await bot.send_message(
            chat_id=user_chat_id, # Send to the user who connected the bot
            text=f"Thank you for connecting your business account! Your Connection ID is {connection_id}."
                 f"\nI can reply on your behalf: {can_reply}."
        )
    else:
        if connection_id in active_business_connections:
            del active_business_connections[connection_id]
        await bot.send_message(
            chat_id=user_chat_id,
            text=f"Your business connection (ID: {connection_id}) has been disabled or removed."
        )


@business_router.message(F.business_message)
async def handle_business_message(message: Message, bot: Bot):
    """
    Handles incoming messages via a Business Connection.
    These are messages from clients to the business account.
    """
    business_connection_id = message.business_connection_id
    client_chat_id = message.chat.id # This is the chat with the client

    logging.info(
        f"Business Message: ConnectionID={business_connection_id}, ClientChatID={client_chat_id}, "
        f"Text='{message.text}'"
    )

    if not business_connection_id:
        logging.warning("Received business_message without business_connection_id")
        return

    connection_details = active_business_connections.get(business_connection_id)

    if connection_details and connection_details["can_reply"]:
        # Example: Echo the message back to the client on behalf of the business
        try:
            await bot.send_message(
                chat_id=client_chat_id,
                text=f"Business Echo: {message.text}",
                business_connection_id=business_connection_id
            )
            logging.info(f"Replied to client {client_chat_id} via business connection {business_connection_id}")
        except Exception as e:
            logging.error(f"Failed to send message via business connection {business_connection_id}: {e}")
    elif connection_details and not connection_details["can_reply"]:
        logging.info(f"Received business message for {business_connection_id}, but bot cannot reply.")
        # Here, you might notify the business owner through other means if needed
    else:
        logging.warning(f"No active or valid business connection found for ID: {business_connection_id}")


@business_router.edited_message(F.business_message) # Handle edited business messages
async def handle_edited_business_message(message: Message, bot: Bot):
    business_connection_id = message.business_connection_id
    client_chat_id = message.chat.id
    logging.info(
        f"Edited Business Message: ConnectionID={business_connection_id}, ClientChatID={client_chat_id}, "
        f"New Text='{message.text}'"
    )
    # Add logic to process edited messages if needed


# Note: To handle deleted_business_messages, you would use:
# @business_router.deleted_business_messages()
# async def handle_deleted_business_messages(event: types.BusinessMessagesDeleted, bot: Bot):
#     logging.info(f"Business messages deleted: ConnectionID={event.business_connection_id}, ChatID={event.chat.id}, MessageIDs={event.message_ids}")
# This requires `aiogram.types.BusinessMessagesDeleted` and the appropriate filter if F.deleted_business_messages exists or a custom one.
# For simplicity, I'm omitting the full implementation for deleted messages here but showing the structure.


def register_business_handlers(dp: Dispatcher):
    dp.include_router(business_router)
