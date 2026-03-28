# file: bot/handlers/admin.py
"""Admin commands handler"""

import logging
from aiogram import Router, types
from aiogram.filters import Command
from database.db import get_daily_stats
from bot.keyboards.admin import get_admin_keyboard
from config import config

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in config.ADMIN_IDS


@router.message(Command("admin"))
async def admin_dashboard(message: types.Message) -> None:
    """Admin dashboard"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Admin only!")
        return
    
    stats = await get_daily_stats()
    
    dashboard = f"""
📊 ADMIN DASHBOARD

👥 USERS
Total: {stats['total_users']}
Active Today: {stats['active_today']}

🔥 ACTIVITY
Swipes Today: {stats['swipes_today']}
Matches Today: {stats['matches_today']}

👑 PREMIUM
Active Subs: {stats['premium_users']}

💰 REVENUE
Today: {stats['revenue_today']}
"""
    
    await message.answer(dashboard, reply_markup=get_admin_keyboard())
    logger.info(f"Admin accessed dashboard: {message.from_user.id}")


@router.callback_query(lambda c: c.data.startswith("admin:") and is_admin(c.from_user.id))
async def admin_action(query: types.CallbackQuery) -> None:
    """Handle admin actions"""
    action = query.data.split(":")[1]
    
    if action == "stats":
        stats = await get_daily_stats()
        text = f"📈 Stats: {stats}"
        await query.message.edit_text(text)
    elif action == "users":
        await query.message.edit_text("👥 User management - Coming soon!")
    elif action == "payments":
        await query.message.edit_text("💰 Payment management - Coming soon!")
    elif action == "reports":
        await query.message.edit_text("⚠️ User reports - Coming soon!")
    elif action == "broadcast":
        await query.message.edit_text("📢 Broadcast - Coming soon!")
    
    await query.answer()
