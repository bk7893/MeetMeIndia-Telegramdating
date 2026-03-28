# file: bot/services/analytics_service.py
"""Analytics and statistics"""

import logging
from database.db import log_action, get_daily_stats

logger = logging.getLogger(__name__)


async def log_user_action(user_id: int, action: str, metadata: str = "") -> None:
    """Log user action for analytics"""
    await log_action(user_id, action, metadata)
    logger.debug(f"Action logged: {user_id} - {action}")


async def get_dashboard_stats() -> dict:
    """Get admin dashboard statistics"""
    stats = await get_daily_stats()
    return stats
