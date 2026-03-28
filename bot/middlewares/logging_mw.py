# file: bot/middlewares/logging_mw.py
"""Logging middleware for request/response tracking"""

import logging
from typing import Callable, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Log all updates"""
    
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: dict[str, Any]
    ) -> Any:
        """Log update and call handler"""
        user_id = None
        update_type = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            update_type = "message"
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            update_type = "callback"
        
        if user_id and update_type:
            logger.debug(f"Update from {user_id}: type={update_type}")
        
        return await handler(event, data)
