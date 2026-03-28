# file: bot/keyboards/admin.py
"""Admin keyboards"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin dashboard buttons"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📊 Stats", callback_data="admin:stats")
    builder.button(text="👥 Users", callback_data="admin:users")
    builder.button(text="💰 Payments", callback_data="admin:payments")
    builder.button(text="⚠️ Reports", callback_data="admin:reports")
    builder.button(text="📢 Broadcast", callback_data="admin:broadcast")
    
    builder.adjust(1)
    return builder.as_markup()
