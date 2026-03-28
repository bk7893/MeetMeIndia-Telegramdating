# file: bot/services/notifications.py
"""Notification delivery service"""

import logging
from aiogram import Bot

logger = logging.getLogger(__name__)


async def send_match_notification(bot: Bot, user_id: int, match_user_id: int, match_name: str) -> bool:
    """Send match notification to user"""
    try:
        message = f"""🎉🎉🎉 IT'S A MATCH! 🎉🎉🎉

You and {match_name} (ID: {match_user_id}) BOTH liked each other!

💬 Go to Messages to say hi!
👋 Start with something fun and genuine."""
        
        await bot.send_message(user_id, message)
        logger.info(f"Match notification sent: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error sending match notification: {e}")
        return False


async def send_premium_expiration_warning(bot: Bot, user_id: int) -> bool:
    """Send premium expiration warning"""
    try:
        message = """⏰ YOUR PREMIUM IS EXPIRING SOON!

Your premium membership expires tomorrow.
Do you want to renew? 

👑 Tap /premium to extend your benefits!"""
        
        await bot.send_message(user_id, message)
        logger.info(f"Premium warning sent: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error sending premium warning: {e}")
        return False
