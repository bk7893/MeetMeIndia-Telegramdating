# file: bot/handlers/errors.py
"""Error handling"""

import logging
from typing import Any, Callable, Awaitable
from aiogram import Router, types, BaseMiddleware
from aiogram.types import Update

router = Router()
logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    """Handle exceptions during message processing"""
    
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any]
    ) -> Any:
        """Wrap handler with error handling"""
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Exception during update processing: {e}", exc_info=True)
            
            # Try to send error message to user
            try:
                if event.message:
                    await event.message.answer("❌ An error occurred. Please try again later.")
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
            
            # Don't re-raise - just log and return
            return None
