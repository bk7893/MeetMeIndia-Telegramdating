# file: bot/keyboards/profile.py
"""Profile keyboards"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Profile menu in"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✏️ Edit Profile", callback_data="profile:edit")
    builder.button(text="🔒 Block User", callback_data="profile:block")
    builder.button(text="⚠️ Report", callback_data="profile:report")
    
    builder.adjust(1)
    return builder.as_markup()


def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Edit profile options"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✏️ Edit Name", callback_data="edit:name")
    builder.button(text="✏️ Edit Age", callback_data="edit:age")
    builder.button(text="✏️ Edit Bio", callback_data="edit:bio")
    builder.button(text="✏️ Edit City", callback_data="edit:city")
    builder.button(text="✏️ Edit Interests", callback_data="edit:interests")
    builder.button(text="📸 Change Photo", callback_data="edit:photo")
    builder.button(text="❌ Back", callback_data="menu:main")
    
    builder.adjust(1)
    return builder.as_markup()
