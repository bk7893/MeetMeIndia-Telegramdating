# file: database/migrations.py
"""Database migrations for MeetMe India Bot"""

import aiosqlite
import logging
from config import config

logger = logging.getLogger(__name__)


async def run_migrations() -> None:
    """Create all necessary tables and indexes"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.executescript("""
            -- Users table
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                first_name TEXT,
                username TEXT,
                language TEXT DEFAULT 'en',
                is_banned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Profiles table
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                city TEXT NOT NULL,
                bio TEXT,
                interests TEXT,
                purpose TEXT NOT NULL,
                photo_url TEXT,
                verified INTEGER DEFAULT 0,
                rating REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );

            -- Swipes table
            CREATE TABLE IF NOT EXISTS swipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                swipe_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(target_user_id) REFERENCES users(user_id)
            );

            -- Matches table
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id_1 INTEGER NOT NULL,
                user_id_2 INTEGER NOT NULL,
                matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY(user_id_1) REFERENCES users(user_id),
                FOREIGN KEY(user_id_2) REFERENCES users(user_id),
                UNIQUE(user_id_1, user_id_2)
            );

            -- Messages table
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0,
                FOREIGN KEY(from_user_id) REFERENCES users(user_id),
                FOREIGN KEY(to_user_id) REFERENCES users(user_id)
            );

            -- Subscriptions table
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                tier TEXT NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );

            -- Payments table
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount_usd REAL NOT NULL,
                amount_stars INTEGER,
                tier TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                telegram_payment_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );

            -- Swipe usage tracking
            CREATE TABLE IF NOT EXISTS swipe_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                swipes_used INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                UNIQUE(user_id, date)
            );

            -- Blocked users
            CREATE TABLE IF NOT EXISTS blocked_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                blocked_user_id INTEGER NOT NULL,
                reason TEXT,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(blocked_user_id) REFERENCES users(user_id),
                UNIQUE(user_id, blocked_user_id)
            );

            -- Reports
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL,
                reported_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(reporter_id) REFERENCES users(user_id),
                FOREIGN KEY(reported_id) REFERENCES users(user_id)
            );

            -- Rate limits
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                reset_at TIMESTAMP NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );

            -- Analytics
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );

            -- Profile boosts
            CREATE TABLE IF NOT EXISTS profile_boosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                boost_type TEXT NOT NULL,
                visibility_count INTEGER,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );

            -- Create indexes for performance
            CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
            CREATE INDEX IF NOT EXISTS idx_profiles_gender_age ON profiles(gender, age);
            CREATE INDEX IF NOT EXISTS idx_swipes_user_id ON swipes(user_id);
            CREATE INDEX IF NOT EXISTS idx_swipes_created ON swipes(created_at);
            CREATE INDEX IF NOT EXISTS idx_matches_user_1 ON matches(user_id_1);
            CREATE INDEX IF NOT EXISTS idx_matches_user_2 ON matches(user_id_2);
            CREATE INDEX IF NOT EXISTS idx_messages_from_to ON messages(from_user_id, to_user_id);
            CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(sent_at);
            CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(user_id, is_active);
            CREATE INDEX IF NOT EXISTS idx_swipe_usage ON swipe_usage(user_id, date);
            CREATE INDEX IF NOT EXISTS idx_blocked_users ON blocked_users(user_id);
            CREATE INDEX IF NOT EXISTS idx_analytics_user ON analytics(user_id);
        """)
        await db.commit()
    
    logger.info("✅ Database migrations completed successfully")
