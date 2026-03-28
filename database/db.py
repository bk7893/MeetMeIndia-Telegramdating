# file: database/db.py
"""
Database operations for MeetMe India Bot
All functions are async and use parameterized queries (no SQL injection)
"""

import aiosqlite
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import config

logger = logging.getLogger(__name__)


# ============= USER OPERATIONS =============

async def add_user(user_id: int, first_name: str, username: Optional[str] = None) -> None:
    """Add or update user"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users (user_id, first_name, username)
               VALUES (?, ?, ?)""",
            (user_id, first_name, username)
        )
        await db.commit()
    logger.info(f"✅ User added/updated: {user_id}")


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
    return dict(row) if row else None


async def user_exists(user_id: int) -> bool:
    """Check if user has completed onboarding"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM profiles WHERE user_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
    return result is not None


async def set_language(user_id: int, language: str) -> None:
    """Set user's language preference"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "UPDATE users SET language = ? WHERE user_id = ?",
            (language, user_id)
        )
        await db.commit()


async def get_user_count_by_gender(gender: Optional[str] = None) -> int:
    """Get total user count, optionally filtered by gender"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        if gender:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM profiles WHERE gender = ?",
                (gender,)
            )
        else:
            cursor = await db.execute("SELECT COUNT(*) FROM profiles")
        result = await cursor.fetchone()
    return result[0] if result else 0


# ============= PROFILE OPERATIONS =============

async def create_or_update_profile(
    user_id: int,
    name: str,
    age: int,
    gender: str,
    city: str,
    interests: str,
    purpose: str,
    bio: str = "",
    photo_url: Optional[str] = None
) -> None:
    """Create or update user profile"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            """INSERT INTO profiles 
               (user_id, name, age, gender, city, interests, purpose, bio, photo_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                   name=excluded.name, age=excluded.age, gender=excluded.gender,
                   city=excluded.city, interests=excluded.interests, purpose=excluded.purpose,
                   bio=excluded.bio, photo_url=excluded.photo_url, updated_at=CURRENT_TIMESTAMP""",
            (user_id, name, age, gender, city, interests, purpose, bio, photo_url)
        )
        await db.commit()
    logger.info(f"✅ Profile created/updated: {user_id}")


async def get_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user profile"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM profiles WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
    return dict(row) if row else None


async def get_profiles_for_swipe(
    user_id: int,
    gender: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get profiles for swiping with smart filtering:
    - Exclude self
    - Exclude already swiped
    - Exclude blocked users
    - Filter by gender if specified
    """
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        params = [user_id, user_id, user_id]
        
        gender_filter = ""
        if gender:
            gender_filter = "AND p.gender = ?"
            params.insert(2, gender)
        
        cursor = await db.execute(f"""
            SELECT p.* FROM profiles p
            WHERE p.user_id != ?
                AND p.user_id NOT IN (
                    SELECT target_user_id FROM swipes WHERE user_id = ?
                )
                AND p.user_id NOT IN (
                    SELECT blocked_user_id FROM blocked_users WHERE user_id = ?
                )
                {gender_filter}
            ORDER BY RANDOM() LIMIT ?
        """, params + [limit])
        
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


# ============= SWIPE OPERATIONS =============

async def record_swipe(user_id: int, target_user_id: int, swipe_type: str) -> None:
    """Record a swipe (like/skip/super)"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Record swipe
        await db.execute(
            "INSERT INTO swipes (user_id, target_user_id, swipe_type) VALUES (?, ?, ?)",
            (user_id, target_user_id, swipe_type)
        )
        
        # Update daily swipe usage
        today = datetime.now().date()
        await db.execute(
            """INSERT INTO swipe_usage (user_id, date, swipes_used)
               VALUES (?, ?, 1)
               ON CONFLICT(user_id, date) DO UPDATE SET swipes_used = swipes_used + 1""",
            (user_id, today)
        )
        
        await db.commit()
    logger.info(f"✅ Swipe recorded: {user_id} -> {target_user_id} ({swipe_type})")


async def get_daily_swipe_count(user_id: int) -> int:
    """Get swipes used today"""
    today = datetime.now().date()
    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute(
            "SELECT swipes_used FROM swipe_usage WHERE user_id = ? AND date = ?",
            (user_id, today)
        )
        result = await cursor.fetchone()
    return result[0] if result else 0


async def has_swipes_remaining(user_id: int) -> bool:
    """Check if user has swipes remaining today"""
    today = datetime.now().date()
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Check if premium
        cursor = await db.execute(
            """SELECT is_active FROM subscriptions 
               WHERE user_id = ? AND end_date > datetime('now')""",
            (user_id,)
        )
        is_premium = await cursor.fetchone()
        
        max_swipes = config.PREMIUM_SWIPES_DAILY if is_premium else config.FREE_SWIPES_DAILY
        
        # Get swipes used
        cursor = await db.execute(
            "SELECT swipes_used FROM swipe_usage WHERE user_id = ? AND date = ?",
            (user_id, today)
        )
        result = await cursor.fetchone()
        swipes_used = result[0] if result else 0
    
    return swipes_used < max_swipes


async def reset_daily_swipes() -> None:
    """Reset daily swipe counters (should run at midnight)"""
    today = datetime.now().date()
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Get all users and reset their swipe usage
        cursor = await db.execute("SELECT DISTINCT user_id FROM users")
        users = await cursor.fetchall()
        
        for (user_id,) in users:
            await db.execute(
                """INSERT INTO swipe_usage (user_id, date, swipes_used)
                   VALUES (?, ?, 0)
                   ON CONFLICT(user_id, date) DO NOTHING""",
                (user_id, today + timedelta(days=1))
            )
        await db.commit()
    logger.info("✅ Daily swipes reset")


async def get_swipe_usage(user_id: int) -> Dict[str, int]:
    """Get swipe usage for today"""
    today = datetime.now().date()
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Check premium
        cursor = await db.execute(
            "SELECT is_active FROM subscriptions WHERE user_id = ? AND end_date > datetime('now')",
            (user_id,)
        )
        is_premium = await cursor.fetchone()
        
        max_swipes = config.PREMIUM_SWIPES_DAILY if is_premium else config.FREE_SWIPES_DAILY
        
        # Get used
        cursor = await db.execute(
            "SELECT swipes_used FROM swipe_usage WHERE user_id = ? AND date = ?",
            (user_id, today)
        )
        result = await cursor.fetchone()
        swipes_used = result[0] if result else 0
    
    return {
        "max": max_swipes,
        "used": swipes_used,
        "remaining": max(0, max_swipes - swipes_used),
        "is_premium": bool(is_premium)
    }


# ============= MATCH OPERATIONS =============

async def check_mutual_match(user_id_1: int, user_id_2: int) -> bool:
    """Check if two users have mutual likes"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute(
            """SELECT 1 FROM swipes 
               WHERE user_id = ? AND target_user_id = ? AND swipe_type IN ('like', 'super')
               AND EXISTS (
                   SELECT 1 FROM swipes s2 
                   WHERE s2.user_id = ? AND s2.target_user_id = ? AND s2.swipe_type IN ('like', 'super')
               )""",
            (user_id_1, user_id_2, user_id_2, user_id_1)
        )
        result = await cursor.fetchone()
    return bool(result)


async def create_match(user_id_1: int, user_id_2: int) -> None:
    """Create a match between two users (ordered by ID)"""
    # Ensure consistent ordering
    if user_id_1 > user_id_2:
        user_id_1, user_id_2 = user_id_2, user_id_1
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO matches (user_id_1, user_id_2) VALUES (?, ?)",
            (user_id_1, user_id_2)
        )
        await db.commit()
    logger.info(f"💕 Match created: {user_id_1} <-> {user_id_2}")


async def get_matches_for_user(user_id: int) -> List[int]:
    """Get all match IDs for a user"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute(
            """SELECT CASE 
                   WHEN user_id_1 = ? THEN user_id_2 
                   ELSE user_id_1 
               END as match_id
               FROM matches WHERE (user_id_1 = ? OR user_id_2 = ?) AND is_active = 1""",
            (user_id, user_id, user_id)
        )
        results = await cursor.fetchall()
    return [r[0] for r in results]


# ============= MESSAGE OPERATIONS =============

async def send_message(from_user_id: int, to_user_id: int, text: str) -> None:
    """Send a message between two users"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (from_user_id, to_user_id, message_text) VALUES (?, ?, ?)",
            (from_user_id, to_user_id, text)
        )
        await db.commit()
    logger.info(f"💬 Message sent: {from_user_id} -> {to_user_id}")


async def get_conversation(user_id_1: int, user_id_2: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get message history between two users"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM messages 
               WHERE (from_user_id = ? AND to_user_id = ?) OR (from_user_id = ? AND to_user_id = ?)
               ORDER BY sent_at DESC LIMIT ?""",
            (user_id_1, user_id_2, user_id_2, user_id_1, limit)
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in reversed(rows)]  # Reverse to chronological order


async def get_recent_conversations(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent conversations for a user"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT DISTINCT 
                   CASE WHEN from_user_id = ? THEN to_user_id ELSE from_user_id END as partner_id,
                   MAX(sent_at) as last_message_time
               FROM messages 
               WHERE from_user_id = ? OR to_user_id = ?
               GROUP BY partner_id 
               ORDER BY last_message_time DESC 
               LIMIT ?""",
            (user_id, user_id, user_id, limit)
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


# ============= PREMIUM OPERATIONS =============

async def create_subscription(user_id: int, tier: str, days: int) -> None:
    """Create a premium subscription"""
    end_date = datetime.now() + timedelta(days=days)
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            """INSERT INTO subscriptions (user_id, tier, end_date, is_active)
               VALUES (?, ?, ?, 1)
               ON CONFLICT(user_id) DO UPDATE SET tier=excluded.tier, end_date=excluded.end_date, is_active=1""",
            (user_id, tier, end_date)
        )
        await db.commit()
    logger.info(f"💎 Premium subscription created: {user_id} - {tier}")


async def get_active_subscription(user_id: int) -> Optional[Dict[str, Any]]:
    """Get active subscription if exists"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM subscriptions 
               WHERE user_id = ? AND is_active = 1 AND end_date > datetime('now')""",
            (user_id,)
        )
        row = await cursor.fetchone()
    return dict(row) if row else None


async def is_premium(user_id: int) -> bool:
    """Check if user has active premium"""
    sub = await get_active_subscription(user_id)
    return sub is not None


async def record_payment(
    user_id: int,
    amount_usd: float,
    amount_stars: int,
    tier: str,
    payment_id: Optional[str] = None
) -> None:
    """Record a payment"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            """INSERT INTO payments 
               (user_id, amount_usd, amount_stars, tier, telegram_payment_id, status)
               VALUES (?, ?, ?, ?, ?, 'completed')""",
            (user_id, amount_usd, amount_stars, tier, payment_id)
        )
        await db.commit()
    logger.info(f"💰 Payment recorded: {user_id} - ${amount_usd}")


# ============= SAFETY OPERATIONS =============

async def block_user(user_id: int, blocked_user_id: int, reason: str = "") -> None:
    """Block a user"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO blocked_users (user_id, blocked_user_id, reason) VALUES (?, ?, ?)",
            (user_id, blocked_user_id, reason)
        )
        await db.commit()
    logger.info(f"🚫 User blocked: {user_id} blocked {blocked_user_id}")


async def is_blocked(user_id: int, other_user_id: int) -> bool:
    """Check if user is blocked"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM blocked_users WHERE user_id = ? AND blocked_user_id = ?",
            (user_id, other_user_id)
        )
        result = await cursor.fetchone()
    return bool(result)


async def get_blocked_list(user_id: int) -> List[int]:
    """Get list of blocked user IDs"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute(
            "SELECT blocked_user_id FROM blocked_users WHERE user_id = ?",
            (user_id,)
        )
        results = await cursor.fetchall()
    return [r[0] for r in results]


async def report_user(
    reporter_id: int,
    reported_id: int,
    reason: str,
    description: str = ""
) -> None:
    """Report a user for moderation"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            """INSERT INTO reports (reporter_id, reported_id, reason, description, status)
               VALUES (?, ?, ?, ?, 'pending')""",
            (reporter_id, reported_id, reason, description)
        )
        await db.commit()
    logger.info(f"⚠️ User reported: {reported_id} by {reporter_id}")


# ============= ANALYTICS =============

async def log_action(user_id: int, action: str, metadata: str = "") -> None:
    """Log user action for analytics"""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT INTO analytics (user_id, action, metadata) VALUES (?, ?, ?)",
            (user_id, action, metadata)
        )
        await db.commit()


async def get_daily_stats() -> Dict[str, Any]:
    """Get daily statistics for admin dashboard"""
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Total users
        cursor = await db.execute("SELECT COUNT(*) FROM profiles")
        total_users = (await cursor.fetchone())[0]
        
        # Active today
        cursor = await db.execute(
            "SELECT COUNT(DISTINCT user_id) FROM analytics WHERE DATE(timestamp) = ?",
            (today,)
        )
        active_today = (await cursor.fetchone())[0]
        
        # Swipes today
        cursor = await db.execute(
            "SELECT COUNT(*) FROM swipes WHERE DATE(created_at) = ?",
            (today,)
        )
        swipes_today = (await cursor.fetchone())[0]
        
        # Matches today
        cursor = await db.execute(
            "SELECT COUNT(*) FROM matches WHERE DATE(matched_at) = ?",
            (today,)
        )
        matches_today = (await cursor.fetchone())[0]
        
        # Premium users
        cursor = await db.execute(
            "SELECT COUNT(*) FROM subscriptions WHERE is_active = 1 AND end_date > datetime('now')"
        )
        premium_users = (await cursor.fetchone())[0]
        
        # Revenue
        cursor = await db.execute(
            "SELECT COALESCE(SUM(amount_usd), 0) FROM payments WHERE DATE(created_at) = ? AND status = 'completed'",
            (today,)
        )
        revenue_today = (await cursor.fetchone())[0]
    
    return {
        "total_users": total_users,
        "active_today": active_today,
        "swipes_today": swipes_today,
        "matches_today": matches_today,
        "premium_users": premium_users,
        "revenue_today": f"${revenue_today:.2f}",
        "timestamp": datetime.now().isoformat()
    }
