# file: bot/handlers/profile.py
"""Profile handler"""

import logging
from aiogram import Router, types

router = Router()
logger = logging.getLogger(__name__)


@router.message(lambda m: m.text == "👤 My Profile")
async def my_profile(message: types.Message) -> None:
    """Show user's profile"""
    from database.db import get_profile
    
    user_id = message.from_user.id
    profile = await get_profile(user_id)
    
    if not profile:
        await message.answer("❌ Create profile first!")
        return
    
    profile_text = f"""
👤 YOUR PROFILE

Name: {profile['name']}
Age: {profile['age']}
Location: {profile['city']}
Purpose: {profile['purpose']}
Bio: {profile['bio']}
Interests: {profile['interests']}

✏️ /edit_profile to update
"""
    
    if profile['photo_url']:
        try:
            await message.answer_photo(photo=profile['photo_url'], caption=profile_text)
        except:
            await message.answer(profile_text)
    else:
        await message.answer(profile_text)
