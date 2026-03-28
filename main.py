# file: main.py
"""
MeetMe India Bot - Main Entry Point
Production-ready Telegram Dating Bot using aiogram 3.x
Complete 2026 Edition with Telegram Stars, FSM, and AI/NLP
"""

import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.migrations import run_migrations
from database.db import reset_daily_swipes
from bot.loader import bot, dispatcher
from bot.middlewares.logging_mw import LoggingMiddleware
from bot.middlewares.rate_limit_mw import RateLimitMiddleware
from bot.middlewares.auth_mw import AuthMiddleware
from bot.services.scheduler import setup_scheduler

# Import all handlers
from bot.handlers import start, onboarding, swipe, premium, profile, matches, messages, settings, admin, errors

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

"""
╔════════════════════════════════════════════════════════════════╗
║  MEETME INDIA BOT - PRODUCTION READY TELEGRAM BOT             ║
║  Built with aiogram 3.x + Telegram Stars + FSM                ║
╠════════════════════════════════════════════════════════════════╣
║  Features:                                                      ║
║  ✅ Complete 9-step profile creation (FSM)                    ║
║  ✅ Smart swiping algorithm with matching                     ║
║  ✅ Telegram Stars payments (premium subscriptions)           ║
║  ✅ Rate limiting & safety features                           ║
║  ✅ Admin dashboard with analytics                            ║
║  ✅ AI/NLP integration (bio suggestions, moderation)          ║
║  ✅ Background scheduler (daily swipe reset, etc.)            ║
║  ✅ Modern UI with InlineKeyboardBuilder                      ║
║                                                                ║
║  Infrastructure:                                              ║
║  • Database: SQLite (easily upgradeable to PostgreSQL)        ║
║  • Async: Full async/await, no blocking calls                 ║
║  • Type Hints: 100% coverage                                  ║
║  • Structure: Modular, scalable design                        ║
║                                                                ║
║  Deployment Notes:                                            ║
║  → For production: Use webhook instead of polling              ║
║  → Use PostgreSQL instead of SQLite                           ║
║  → Add Redis for session management                           ║
║  → Deploy in Docker with proper env vars                      ║
║  → Configure logging to external service                      ║
║  → Setup reverse proxy (Nginx)                                ║
║                                                                ║
║  Scaling Considerations:                                      ║
║  → Database indexes are in place for 10k+ users               ║
║  → Use load balancer for multiple bot instances               ║
║  → Implement Redis cache for hot data                        ║
║  → Monitor with APM tools (Sentry, New Relic)                 ║
║  → Setup alerting for payment failures                        ║
╚════════════════════════════════════════════════════════════════╝
"""


async def setup_dispatcher() -> Dispatcher:
    """Setup dispatcher with routers and middlewares"""
    
    # Register middlewares (in order)
    dispatcher.message.middleware(LoggingMiddleware())
    dispatcher.message.middleware(RateLimitMiddleware())
    dispatcher.message.middleware(AuthMiddleware())
    dispatcher.message.middleware(errors.ErrorMiddleware())
    
    dispatcher.callback_query.middleware(LoggingMiddleware())
    dispatcher.callback_query.middleware(RateLimitMiddleware())
    dispatcher.callback_query.middleware(AuthMiddleware())
    dispatcher.callback_query.middleware(errors.ErrorMiddleware())
    
    # Register all handler routers
    dispatcher.include_router(start.router)
    dispatcher.include_router(onboarding.router)
    dispatcher.include_router(swipe.router)
    dispatcher.include_router(premium.router)
    dispatcher.include_router(profile.router)
    dispatcher.include_router(matches.router)
    dispatcher.include_router(messages.router)
    dispatcher.include_router(settings.router)
    dispatcher.include_router(admin.router)
    
    logger.info("✅ Dispatcher setup complete")
    return dispatcher


async def on_startup() -> None:
    """Startup tasks"""
    logger.info("🚀 Starting MeetMe India Bot...")
    
    # Run database migrations
    await run_migrations()
    logger.info("✅ Database ready")
    
    # Setup scheduler
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("✅ Scheduler started")
    
    # Set bot commands
    commands = [
        types.BotCommand(command="start", description="Start the bot"),
        types.BotCommand(command="admin", description="Admin dashboard"),
        types.BotCommand(command="help", description="Get help"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Bot commands set")
    
    logger.info("✅ Bot startup complete!")


async def on_shutdown() -> None:
    """Shutdown tasks"""
    logger.info("🛑 MeetMe India Bot shutting down...")
    await bot.session.close()
    logger.info("✅ Bot shutdown complete")


async def main() -> None:
    """Main entry point"""
    
    # Setup bot properties
    bot.session.default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    
    # Setup dispatcher
    await setup_dispatcher()
    
    # Startup
    await on_startup()
    
    try:
        logger.info("🔄 Starting polling...")
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
            skip_updates=True
        )
    except KeyboardInterrupt:
        logger.info("⌨️ Polling interrupted")
    finally:
        await on_shutdown()


if __name__ == "__main__":
    logger.info(f"🌟 MeetMe India Bot v2026.03.28")
    logger.info(f"Environment: {config.ENV}")
    logger.info(f"Admin IDs: {config.ADMIN_IDS}")
    logger.info(f"AI Enabled: {config.AI_ENABLED}")
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
