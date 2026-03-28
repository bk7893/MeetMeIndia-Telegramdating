# file: bot/middlewares/auth_mw.py
"""Authentication middleware - ensures user exists in database"""

import logging
from typing import Callable, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.db import add_user, get_user

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Ensure user is registered in database"""
    
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: dict[str, Any]
    ) -> Any:
        """Auto-register user if needed"""
        user = None
        
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if user:
            # Ensure user exists in database
            await add_user(
                user_id=user.id,
                first_name=user.first_name or "User",
                username=user.username
            )
        
        return await handler(event, data)
