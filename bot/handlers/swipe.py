# file: bot/handlers/swipe.py
"""Swiping handler"""

import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from database.db import get_profile, get_profiles_for_swipe, get_swipe_usage
from bot.services.matching import process_swipe
from bot.services.swipe_logic import can_swipe, get_quota_message
from bot.services.notifications import send_match_notification
from bot.keyboards.swipe import get_swipe_keyboard
from bot.loader import bot

router = Router()
logger = logging.getLogger(__name__)


@router.message(lambda m: m.text == "🔥 Start Swiping")
async def start_swiping(message: types.Message) -> None:
    """Start swiping interface"""
    user_id = message.from_user.id
    
    # Check swipes
    can, reason = await can_swipe(user_id)
    if not can:
        await message.answer(reason + "\n\n👑 Upgrade to Premium for 20 swipes/day!")
        return
    
    # Get user profile
    profile = await get_profile(user_id)
    if not profile:
        await message.answer("❌ Create profile first!")
        return
    
    # Get opposite gender profiles (example: filter by gender)
    gender = "female" if profile['gender'] == "male" else "male"
    profiles = await get_profiles_for_swipe(user_id, gender=gender, limit=10)
    
    if not profiles:
        await message.answer("😔 No new profiles right now. Check back later!")
        return
    
    # Show first profile
    target = profiles[0]
    quota = await get_quota_message(user_id)
    
    profile_text = f"""
✨ {target['name'].upper()} ✨

🎂 Age: {target['age']}
📍 Location: {target['city']}
💭 Bio: {target['bio']}
❤️ Interests: {target['interests'][:50]}...

{quota}"""
    
    if target['photo_url']:
        try:
            await message.answer_photo(
                photo=target['photo_url'],
                caption=profile_text,
                reply_markup=get_swipe_keyboard(target['user_id'])
            )
        except:
            await message.answer(profile_text, reply_markup=get_swipe_keyboard(target['user_id']))
    else:
        await message.answer(profile_text, reply_markup=get_swipe_keyboard(target['user_id']))


@router.callback_query(lambda c: c.data.startswith("swipe:"))
async def swipe_action(query: types.CallbackQuery) -> None:
    """Handle swipe actions"""
    parts = query.data.split(":")
    swipe_type = parts[1]  # skip, like, super
    target_user_id = int(parts[2])
    user_id = query.from_user.id
    
    # Process swipe
    is_match, match_msg = await process_swipe(user_id, target_user_id, swipe_type)
    
    if is_match:
        await query.answer("🎉 It's a match!", show_alert=True)
        # Send notifications
        target_profile = await get_profile(target_user_id)
        user_profile = await get_profile(user_id)
        await send_match_notification(bot, user_id, target_user_id, target_profile['name'])
        await send_match_notification(bot, target_user_id, user_id, user_profile['name'])
    else:
        if swipe_type == "like":
            await query.answer("❤️ LIKED!")
        elif swipe_type == "skip":
            await query.answer("⏭️ SKIPPED")
        else:
            await query.answer("⭐ SUPER LIKED!")
    
    logger.info(f"Swipe: {user_id} -> {target_user_id} ({swipe_type})")
