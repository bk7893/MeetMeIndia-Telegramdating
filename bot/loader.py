# file: bot/loader.py
"""
Bot and Dispatcher setup for aiogram 3.x
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import config

# Create bot and dispatcher
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dispatcher = Dispatcher(storage=storage)

__all__ = ["bot", "dispatcher", "storage"]
