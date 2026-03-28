# file: bot/handlers/onboarding.py
"""Onboarding flow (9-step profile creation)"""

import logging
from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from database.db import create_or_update_profile, set_language
from bot.states.onboarding import OnboardingStates
from bot.keyboards.onboarding import (
    get_gender_keyboard, get_purpose_keyboard, get_interests_keyboard
)
from bot.keyboards.main_menu import get_main_menu_keyboard
from config import config

router = Router()
logger = logging.getLogger(__name__)


# Step 1: Language
@router.callback_query(StateFilter(OnboardingStates.language))
async def language_chosen(query: types.CallbackQuery, state: FSMContext) -> None:
    language = query.data.split(":")[1]
    await state.update_data(language=language)
    await set_language(query.from_user.id, language)
    await state.set_state(OnboardingStates.name)
    
    await query.answer()
    await query.message.edit_text(
        "✅ STEP 1/9 COMPLETE!\n\n👋 What's your first name?",
        reply_markup=None
    )
    await query.message.answer("(2-30 characters)")


# Step 2: Name
@router.message(StateFilter(OnboardingStates.name))
async def name_entered(message: types.Message, state:FSMContext) -> None:
    name = message.text[:30]
    if len(name) < 2:
        await message.answer("❌ Name too short (min 2 chars)")
        return
    
    await state.update_data(name=name)
    await state.set_state(OnboardingStates.age)
    await message.answer(f"✅ STEP 2/9: {name}!\n\n🎂 What's your age? (18-65)")


# Step 3: Age
@router.message(StateFilter(OnboardingStates.age))
async def age_entered(message: types.Message, state: FSMContext) -> None:
    try:
        age = int(message.text)
        if not (18 <= age <= 65):
            await message.answer("❌ Age must be 18-65")
            return
        await state.update_data(age=age)
        await state.set_state(OnboardingStates.gender)
        await message.answer(
            f"✅ STEP 3/9: {age}!\n\n♂️/♀️ Select your gender:",
            reply_markup=get_gender_keyboard()
        )
    except ValueError:
        await message.answer("❌ Enter a valid number")


# Step 4: Gender
@router.callback_query(StateFilter(OnboardingStates.gender))
async def gender_chosen(query: types.CallbackQuery, state: FSMContext) -> None:
    gender = query.data.split(":")[1]
    await state.update_data(gender=gender)
    await state.set_state(OnboardingStates.city)
    await query.answer()
    await query.message.edit_text(
        f"✅ STEP 4/9: {config.GENDERS[gender]}!\n\n📍 What's your city?",
        reply_markup=None
    )
    await query.message.answer("(City name)")


# Step 5: City
@router.message(StateFilter(OnboardingStates.city))
async def city_entered(message: types.Message, state: FSMContext) -> None:
    city = message.text[:30]
    await state.update_data(city=city)
    await state.set_state(OnboardingStates.interests)
    await message.answer(
        f"✅ STEP 5/9: {city}!\n\n❤️ Select your interests (max {config.MAX_INTERESTS}):",
        reply_markup=get_interests_keyboard()
    )


# Step 6: Interests
@router.callback_query(StateFilter(OnboardingStates.interests))
async def interests_callback(query: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    selected = set(data.get("interests", "").split(",")) if data.get("interests") else set()
    
    if query.data == "interests:done":
        if not selected:
            await query.answer("❌ Select at least 1 interest!")
            return
        
        await state.set_state(OnboardingStates.purpose)
        interests_str = ",".join(sorted(selected))
        await state.update_data(interests=interests_str)
        
        await query.answer()
        await query.message.edit_text(
            f"✅ STEP 6/9: {len(selected)} interests!\n\n💕 What are you looking for?",
            reply_markup=get_purpose_keyboard()
        )
    else:
        interest = query.data.split(":")[1]
        if interest in selected:
            selected.discard(interest)
        elif len(selected) < config.MAX_INTERESTS:
            selected.add(interest)
        
        await state.update_data(interests=",".join(sorted(selected)))
        await query.answer(f"✨ {len(selected)}/{config.MAX_INTERESTS}")
        await query.message.edit_reply_markup(reply_markup=get_interests_keyboard(selected))


# Step 7: Purpose
@router.callback_query(StateFilter(OnboardingStates.purpose))
async def purpose_chosen(query: types.CallbackQuery, state: FSMContext) -> None:
    purpose = query.data.split(":")[1]
    await state.update_data(purpose=purpose)
    await state.set_state(OnboardingStates.bio)
    await query.answer()
    await query.message.edit_text(
        f"✅ STEP 7/9: {config.PURPOSES[purpose]}!\n\n💬 Tell us about yourself:",
        reply_markup=None
    )
    await query.message.answer("(50-150 chars)")


# Step 8: Bio
@router.message(StateFilter(OnboardingStates.bio))
async def bio_entered(message: types.Message, state: FSMContext) -> None:
    bio = message.text[:150]
    if len(bio) < 10:
        await message.answer("❌ Bio too short (min 10 chars)")
        return
    
    await state.update_data(bio=bio)
    await state.set_state(OnboardingStates.photo)
    await message.answer(
        f"✅ STEP 8/9: Bio saved!\n\n📸 FINAL STEP: Upload your photo!\n\n(Max 9MB)"
    )


# Step 9: Photo
@router.message(StateFilter(OnboardingStates.photo))
async def photo_uploaded(message: types.Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer("❌ Send a valid photo")
        return
    
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    
    # Create profile
    await create_or_update_profile(
        user_id=message.from_user.id,
        name=data['name'],
        age=data['age'],
        gender=data['gender'],
        city=data['city'],
        interests=data['interests'],
        purpose=data['purpose'],
        bio=data['bio'],
        photo_url=photo_id
    )
    
    await state.clear()
    
    success_msg = f"""
✅✅✅ PROFILE COMPLETE! ✅✅✅

🎉 Welcome to MeetMe India, {data['name']}!

Your profile is now LIVE! 🔥

🎯 Next: Start swiping to find your match!
💕 Go to Main Menu and tap "🔥 Start Swiping"
"""
    await message.answer(success_msg, reply_markup=get_main_menu_keyboard())
    logger.info(f"Profile created: {message.from_user.id}")
