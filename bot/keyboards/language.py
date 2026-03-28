# file: bot/keyboards/language.py
"""Language selection keyboard"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import config


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard"""
    buttons = [
        [InlineKeyboardButton(
            text=name,
            callback_data=f"lang:{code}"
        )]
        for code, name in config.LANGUAGES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
