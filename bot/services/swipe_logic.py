# file: bot/services/swipe_logic.py
"""Swipe logic and quota management"""

import logging
from typing import Tuple
from database.db import has_swipes_remaining, get_swipe_usage

logger = logging.getLogger(__name__)


async def can_swipe(user_id: int) -> Tuple[bool, str]:
    """Check if user can swipe"""
    has_remaining = await has_swipes_remaining(user_id)
    
    if not has_remaining:
        usage = await get_swipe_usage(user_id)
        return False, f"❌ No swipes left today! You've used all {usage['max']} swipes."
    
    return True, ""


async def get_quota_message(user_id: int) -> str:
    """Get swipe quota message"""
    usage = await get_swipe_usage(user_id)
    return f"🔥 Swipes: {usage['remaining']}/{usage['max']}" + (" 👑 PREMIUM" if usage['is_premium'] else "")
