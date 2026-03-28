# file: bot/keyboards/onboarding.py
"""Onboarding keyboards"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import config


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Gender selection keyboard"""
    builder = InlineKeyboardBuilder()
    for gender, label in config.GENDERS.items():
        builder.button(text=label, callback_data=f"gender:{gender}")
    builder.adjust(1)
    return builder.as_markup()


def get_purpose_keyboard() -> InlineKeyboardMarkup:
    """Purpose selection keyboard"""
    builder = InlineKeyboardBuilder()
    for purpose, label in config.PURPOSES.items():
        builder.button(text=label, callback_data=f"purpose:{purpose}")
    builder.adjust(1)
    return builder.as_markup()


def get_interests_keyboard(selected: set[str] = None) -> InlineKeyboardMarkup:
    """Interests multi-select keyboard"""
    if selected is None:
        selected = set()
    
    builder = InlineKeyboardBuilder()
    
    for interest, emoji in config.INTERESTS.items():
        is_selected = interest in selected
        prefix = "✅ " if is_selected else "🤍 "
        text = f"{prefix} {emoji} {interest}"
        builder.button(
            text=text,
            callback_data=f"interest:{interest}"
        )
    
    builder.adjust(2)
    builder.row(InlineKeyboardButton(
        text=f"✨ DONE ({len(selected)}/{config.MAX_INTERESTS})",
        callback_data="interests:done"
    ))
    
    return builder.as_markup()
