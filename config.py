# file: config.py
"""
Configuration for MeetMe India Bot - Complete 2026 Edition
Loads from .env file with proper validation
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
env_file = Path(__file__).parent / ".env"
load_dotenv(env_file, override=True)  # override=True ensures .env values take precedence


@dataclass
class Config:
    """Configuration dataclass with type validation"""
    
    # Bot Token
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Admin IDs
    ADMIN_IDS: list[int] = None
    
    # Database
    DB_PATH: str = os.getenv("DB_PATH", "bot.db")
    
    # Environment
    ENV: str = os.getenv("ENV", "dev")
    IS_DEV: bool = ENV == "dev"
    
    # AI/NLP Configuration
    AI_API_BASE_URL: str = os.getenv("AI_API_BASE_URL", "")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_ENABLED: bool = bool(AI_API_BASE_URL and AI_API_KEY)
    
    # Rate Limiting
    RATE_LIMIT_SWIPES_PER_HOUR: int = int(os.getenv("RATE_LIMIT_SWIPES_PER_HOUR", "100"))
    RATE_LIMIT_MESSAGES_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_MESSAGES_PER_MINUTE", "10"))
    
    # App Settings
    FREE_SWIPES_DAILY: int = 8
    PREMIUM_SWIPES_DAILY: int = 20
    MIN_AGE: int = 18
    MAX_AGE: int = 65
    MAX_BIO_LENGTH: int = 500
    MAX_INTERESTS: int = 12
    
    # Languages
    LANGUAGES: dict[str, str] = None
    
    # Genders
    GENDERS: dict[str, str] = None
    
    # Purposes
    PURPOSES: dict[str, str] = None
    
    # Interests with Emojis
    INTERESTS: dict[str, str] = None
    
    # Premium Tiers
    PREMIUM_TIERS: dict = None
    
    def __post_init__(self):
        """Initialize defaults after dataclass creation"""
        if self.ADMIN_IDS is None:
            admin_str = os.getenv("ADMIN_IDS", "")
            self.ADMIN_IDS = [int(x.strip()) for x in admin_str.split(",") if x.strip()]
        
        if self.LANGUAGES is None:
            self.LANGUAGES = {
                "en": "English 🇬🇧",
                "hi": "हिन्दी 🇮🇳",
            }
        
        if self.GENDERS is None:
            self.GENDERS = {
                "male": "♂️ Male",
                "female": "♀️ Female",
                "other": "⚪ Other",
            }
        
        if self.PURPOSES is None:
            self.PURPOSES = {
                "dating": "💕 Dating",
                "relationship": "👰 Serious Relationship",
                "friendship": "🤝 Friendship",
                "networking": "💼 Networking",
            }
        
        if self.INTERESTS is None:
            self.INTERESTS = {
                "Movies": "🎬",
                "Music": "🎵",
                "Sports": "⚽",
                "Gaming": "🎮",
                "Travel": "✈️",
                "Photography": "📸",
                "Cooking": "🍳",
                "Reading": "📚",
                "Fitness": "💪",
                "Art": "🎨",
                "Dancing": "💃",
                "Adventure": "🏔️",
            }
        
        if self.PREMIUM_TIERS is None:
            self.PREMIUM_TIERS = {
                "5_days": {
                    "name": "5-Day Trial",
                    "days": 5,
                    "price_usd": 4.99,
                    "price_stars": 5,
                    "benefits": [
                        "20 swipes daily",
                        "Unlimited super-likes",
                        "See who liked you",
                        "Profile boost",
                    ]
                },
                "30_days": {
                    "name": "1 Month",
                    "days": 30,
                    "price_usd": 9.99,
                    "price_stars": 20,
                    "benefits": [
                        "20 swipes daily",
                        "Unlimited super-likes",
                        "See who liked you",
                        "Profile boost",
                        "Priority in search",
                    ]
                },
                "90_days": {
                    "name": "3 Months",
                    "days": 90,
                    "price_usd": 24.99,
                    "price_stars": 50,
                    "benefits": [
                        "20 swipes daily",
                        "Unlimited super-likes",
                        "See who liked you",
                        "Profile boost",
                        "Priority in search",
                        "Save favorites",
                        "VIP badge",
                    ]
                }
            }
        
        # Validate critical config
        if not self.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN must be set in .env file")
        
        if not self.ADMIN_IDS:
            raise ValueError("❌ ADMIN_IDS must be set in .env file")


# Global config instance
config = Config()
