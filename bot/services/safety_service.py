# file: bot/services/safety_service.py
"""Safety and moderation services"""

import logging
from database.db import block_user, is_blocked, report_user

logger = logging.getLogger(__name__)


async def safe_block_user(user_id: int, blocked_user_id: int, reason: str = "") -> bool:
    """Block a user safely"""
    try:
        await block_user(user_id, blocked_user_id, reason)
        logger.info(f"User blocked: {user_id} blocked {blocked_user_id}")
        return True
    except Exception as e:
        logger.error(f"Error blocking user: {e}")
        return False


async def safe_report_user(
    reporter_id: int,
    reported_id: int,
    reason: str,
    description: str = ""
) -> bool:
    """Report a user for moderation"""
    try:
        await report_user(reporter_id, reported_id, reason, description)
        logger.info(f"User reported: {reported_id} by {reporter_id}")
        return True
    except Exception as e:
        logger.error(f"Error reporting user: {e}")
        return False


async def check_if_blocked(user_id: int, other_user_id: int) -> bool:
    """Check if blocked by user"""
    return await is_blocked(user_id, other_user_id)
