# file: bot/handlers/start.py
"""Start command handler"""

import logging
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from database.db import add_user, user_exists, get_profile
from bot.states.onboarding import OnboardingStates
from bot.keyboards.language import get_language_keyboard
from bot.keyboards.main_menu import get_main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext) -> None:
    """Start command - entry point"""
    user_id = message.from_user.id
    
    # Ensure user exists
    await add_user(user_id, message.from_user.first_name or "User", message.from_user.username)
    
    # Check if profile exists
    if await user_exists(user_id):
        profile = await get_profile(user_id)
        welcome = f"""
🎉🎉🎉 WELCOME BACK! 🎉🎉🎉

Hi {profile['name']}! 👋

Ready to find your perfect match? Let's go! 🔥"""
        await message.answer(welcome, reply_markup=get_main_menu_keyboard())
    else:
        welcome = """
🌟 WELCOME TO MEETME INDIA 🌟

The #1 dating app for finding your vibe! 💕

Let's create your profile in 9 easy steps:

1️⃣  Language
2️⃣  Name
3️⃣  Age
4️⃣  Gender
5️⃣  City
6️⃣  Interests
7️⃣  Purpose
8️⃣  Bio
9️⃣  Photo

Let's begin! Select your language:"""
        await message.answer(welcome, reply_markup=get_language_keyboard())
        await state.set_state(OnboardingStates.language)
    
    logger.info(f"User started: {user_id}")
