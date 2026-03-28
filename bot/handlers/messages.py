# file: bot/handlers/messages.py
"""Messaging handler"""

import logging
from aiogram import Router, types
from database.db import get_recent_conversations, get_conversation

router = Router()
logger = logging.getLogger(__name__)


@router.message(lambda m: m.text == "💬 Messages")
async def messages_menu(message: types.Message) -> None:
    """Show recent conversations"""
    user_id = message.from_user.id
    
    convos = await get_recent_conversations(user_id)
    
    if not convos:
        await message.answer("💬 No messages yet!\n\n🔥 Start swiping to find matches!")
        return
    
    text = "💬 YOUR MESSAGES\n\n"
    for convo in convos[:10]:
        text += f"👤 User #{convo['partner_id']} - {convo['last_message_time']}\n"
    
    text += "\n💭 Message format: /msg_[USER_ID] [MESSAGE]"
    
    await message.answer(text)
