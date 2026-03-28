# file: bot/services/premium_service.py
"""Premium subscription management"""

import logging
from datetime import timedelta
from database.db import (
    create_subscription, get_active_subscription, is_premium,
    record_payment, create_or_update_profile
)
from config import config

logger = logging.getLogger(__name__)


async def activate_premium(user_id: int, tier: str, amount_usd: float, amount_stars: int, payment_id: str) -> bool:
    """Activate premium subscription and record payment"""
    
    if tier not in config.PREMIUM_TIERS:
        logger.error(f"Invalid tier: {tier}")
        return False
    
    try:
        tier_data = config.PREMIUM_TIERS[tier]
        
        # Record payment
        await record_payment(user_id, amount_usd, amount_stars, tier, payment_id)
        
        # Create subscription
        await create_subscription(user_id, tier, tier_data["days"])
        
        logger.info(f"✅ Premium activated: {user_id} - {tier}")
        return True
    except Exception as e:
        logger.error(f"Error activating premium: {e}")
        return False


async def get_premium_benefits(user_id: int) -> str:
    """Get premium benefits message"""
    sub = await get_active_subscription(user_id)
    
    if not sub:
        return "❌ No active premium subscription"
    
    tier_data = config.PREMIUM_TIERS.get(sub['tier'], {})
    benefits = tier_data.get('benefits', [])
    
    benefits_text = "\n".join([f"✅ {b}" for b in benefits])
    return f"""👑 YOUR PREMIUM BENEFITS

{benefits_text}

📅 Expires: {sub['end_date']}"""
