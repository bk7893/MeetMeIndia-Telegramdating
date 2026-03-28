# file: bot/middlewares/rate_limit_mw.py
"""Rate limiting middleware"""

import logging
import asyncio
from typing import Callable, Any, Awaitable, Union
from datetime import datetime, timedelta
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.db import (
    add_user, get_user, log_action
)

logger = logging.getLogger(__name__)

# In-memory rate limit storage (for development)
# Production: use Redis or database
RATE_LIMITS = {}


class RateLimitMiddleware(BaseMiddleware):
    """Simple rate limiting middleware"""
    
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: dict[str, Any]
    ) -> Any:
        """Check rate limits before processing"""
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id:
            # Simple check: max 100 updates per minute
            key = f"{user_id}:{datetime.now().minute}"
            RATE_LIMITS[key] = RATE_LIMITS.get(key, 0) + 1
            
            if RATE_LIMITS[key] > 100:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                if isinstance(event, Message):
                    await event.answer("⚠️ You're doing that too fast. Please wait a moment.")
                return
        
        return await handler(event, data)
