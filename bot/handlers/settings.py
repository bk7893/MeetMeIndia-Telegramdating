# file: bot/handlers/settings.py
"""Settings handler"""

import logging
from aiogram import Router, types

router = Router()
logger = logging.getLogger(__name__)


@router.message(lambda m: m.text == "⚙️ Settings")
async def settings_menu(message: types.Message) -> None:
    """Show settings menu"""
    from bot.keyboards.admin import get_admin_keyboard
    
    settings_text = """
⚙️ SETTINGS

🔔 Notifications: Coming soon
🔒 Privacy: Coming soon
❌ Delete Account: /delete_account
"""
    
    await message.answer(settings_text)
