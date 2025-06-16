"""Auth Middleware for Aiogram 3.x
This middleware checks if the user is authenticated based on the event's 'from_user' attribute.
It sets 'is_authenticated' in the data dictionary for further processing.
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

# Import the configuration
import config as app_config

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")

        if user:
            # Pass the full user object to check_user_auth
            data["is_authenticated"] = await self.check_user_auth(user, data)
            data["user_id"] = user.id
            logger.debug(
                f"AuthMiddleware: User ID {user.id} ({user.full_name}), "
                f"is_authenticated: {data['is_authenticated']}"
            )
        else:
            data["is_authenticated"] = False
            logger.debug("AuthMiddleware: No user found in event, is_authenticated: False")

        return await handler(event, data)

    async def check_user_auth(self, user: User, data: Dict[str, Any]) -> bool:
        """
        Checks if the user is authenticated.
        Prioritizes checking against AUTHORIZED_FULL_NAME if set in config.
        """
        # Check against the configured full name if it's set
        if app_config.AUTHORIZED_FULL_NAME:
            if user.full_name == app_config.AUTHORIZED_FULL_NAME:
                logger.info(
                    f"User '{user.full_name}' (ID: {user.id}) MATCHES configured AUTHORIZED_FULL_NAME. Authenticated."
                )
                return True
            else:
                logger.warning(
                    f"User '{user.full_name}' (ID: {user.id}) does NOT MATCH configured "
                    f"AUTHORIZED_FULL_NAME ('{app_config.AUTHORIZED_FULL_NAME}'). Not authenticated by this rule."
                )
                return False  # If AUTHORIZED_FULL_NAME is set, it's the sole criteria by this logic

        # If AUTHORIZED_FULL_NAME is not set, fall back to other logic or default to True.
        # For now, let's default to True if no specific name is configured for restriction.
        # In a real scenario, you might have database lookups or other checks here.
        logger.debug(
            f"AUTHORIZED_FULL_NAME not set in config. Defaulting user '{user.full_name}' (ID: {user.id}) "
            f"to authenticated (or apply other auth rules here)."
        )
        return True  # Default to authenticated if no specific full name is configured for restriction


# No need to instantiate it here (auth_middleware = AuthMiddleware())
# It's instantiated in main.py during dispatcher setup.
