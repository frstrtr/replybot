import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User # User for type hint

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Aiogram 3 automatically provides 'event_from_user' in 'data'
        # if the event (Message, CallbackQuery etc.) has a 'from_user' attribute.
        user: User | None = data.get('event_from_user') 
        
        if user:
            # Here you can implement your authentication logic.
            # For example, check if the user is in the database.
            # You might need to pass a database session/pool to the middleware's constructor
            # or access it from `data` if set up by another middleware or in the bot/dispatcher instance.
            data['is_authenticated'] = await self.check_user_auth(user.id, data)
            data['user_id'] = user.id # Optionally pass user_id further
        else:
            # For events without a direct user (e.g., channel post, some poll updates)
            data['is_authenticated'] = False
        
        return await handler(event, data)

    async def check_user_auth(self, user_id: int, data: Dict[str, Any]) -> bool:
        # Implement your user authentication check logic here.
        # This is a placeholder for demonstration purposes.
        # Example:
        # db_session = data.get('db_session') # If you pass session via data
        # if db_session:
        #     # Perform database query
        #     # existing_user = await db_session.get(UserDBModel, user_id)
        #     # return bool(existing_user and existing_user.is_active)
        #     pass
        logging.debug(f"AuthMiddleware: Checking auth for user_id: {user_id}") # Use logging
        return True  # Assume all users are authenticated for now

# No need to instantiate it here (auth_middleware = AuthMiddleware())
# It's instantiated in main.py during dispatcher setup.