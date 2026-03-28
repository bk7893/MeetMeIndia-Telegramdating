# file: bot/keyboards/swipe.py
"""Swiping keyboards"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_swipe_keyboard(profile_id: int) -> InlineKeyboardMarkup:
    """Swipe action buttons"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="❌ SKIP", callback_data=f"swipe:skip:{profile_id}")
    builder.button(text="❤️ LIKE", callback_data=f"swipe:like:{profile_id}")
    builder.button(text="⭐ SUPER", callback_data=f"swipe:super:{profile_id}")
    
    builder.adjust(3)
    return builder.as_markup()
