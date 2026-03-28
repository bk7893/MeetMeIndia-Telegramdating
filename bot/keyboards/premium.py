# file: bot/keyboards/premium.py
"""Premium tier keyboards"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import config


def get_premium_tiers_keyboard() -> InlineKeyboardMarkup:
    """Premium membership tiers"""
    builder = InlineKeyboardBuilder()
    
    for tier_id, tier_data in config.PREMIUM_TIERS.items():
        price = f"${tier_data['price_usd']} / {tier_data['price_stars']}⭐"
        text = f"{tier_data['name']} - {price}"
        builder.button(text=text, callback_data=f"premium:buy:{tier_id}")
    
    builder.button(text="❌ Close", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()
