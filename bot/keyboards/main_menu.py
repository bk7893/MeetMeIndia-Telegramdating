# file: bot/keyboards/main_menu.py
"""Main menu keyboard"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    
    builder.button(text="🔥 Start Swiping")
    builder.button(text="💕 My Matches")
    
    builder.button(text="💬 Messages")
    builder.button(text="👤 My Profile")
    
    builder.button(text="👑 Premium")
    builder.button(text="⚙️ Settings")
    
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
