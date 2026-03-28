# file: bot/handlers/matches.py
"""Matches handler"""

import logging
from aiogram import Router, types
from database.db import get_matches_for_user, get_profile

router = Router()
logger = logging.getLogger(__name__)


@router.message(lambda m: m.text == "💕 My Matches")
async def my_matches(message: types.Message) -> None:
    """Show user's matches"""
    user_id = message.from_user.id
    
    match_ids = await get_matches_for_user(user_id)
    
    if not match_ids:
        await message.answer("💔 No matches yet!\n\nKeep swiping! 🔥")
        return
    
    text = "💕 YOUR MATCHES\n\n"
    for match_id in match_ids[:10]:
        profile = await get_profile(match_id)
        if profile:
            text += f"👤 {profile['name']}, {profile['age']} - {profile['city']}\n"
    
    if len(match_ids) > 10:
        text += f"\n... and {len(match_ids) - 10} more"
    
    text += "\n\n💬 Go to Messages to chat!"
    
    await message.answer(text)
