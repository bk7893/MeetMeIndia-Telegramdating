# file: bot/services/matching.py
"""Matching algorithm and logic"""

import logging
from typing import Tuple
from database.db import (
    check_mutual_match, create_match, record_swipe
)

logger = logging.getLogger(__name__)


async def process_swipe(
    user_id: int,
    target_user_id: int,
    swipe_type: str
) -> Tuple[bool, str]:
    """
    Process a swipe and check for mutual match
    Returns (is_match, message)
    """
    
    # Record the swipe
    await record_swipe(user_id, target_user_id, swipe_type)
    
    if swipe_type in ["like", "super"]:
        # Check for mutual match
        is_mutual = await check_mutual_match(user_id, target_user_id)
        
        if is_mutual:
            # Create match
            await create_match(user_id, target_user_id)
            logger.info(f"💕 Match created: {user_id} <-> {target_user_id}")
            return True, "🎉 It's a match!"
    
    return False, None
