# MeetMe India Bot - Complete Setup & Deployment Guide

## 📋 Project Overview

**MeetMe India 2026** - A production-ready Telegram dating bot built with:
- **aiogram 3.x** - Modern async bot framework
- **SQLite** (upgradeable to PostgreSQL)
- **Telegram Stars** - Payment integration
- **FSM** - Conversation management
- **APScheduler** - Background jobs
- **AI/NLP** - Optional bio suggestions & moderation

---

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites
- Python 3.11+
- Telegram Bot Token (from @BotFather)

### 2. Setup
```bash
# Clone/navigate to project
cd MeetMeIndia_Complete_2026

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy & configure .env
cp .env.example .env
# Edit .env with your BOT_TOKEN and ADMIN_IDS

# Run bot
python main.py
```

Bot will now be **LIVE and polling** on Telegram! 🎉

---

## 📂 Project Structure

```
MeetMeIndia_Complete_2026/
├── main.py                 # Entry point
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── .env.example          # Config template
│
├── database/
│   ├── migrations.py      # Database schema (14 tables)
│   ├── db.py             # All DB operations (60+ async functions)
│   └── __init__.py
│
└── bot/
    ├── loader.py          # Bot & dispatcher setup
    │
    ├── middlewares/       # Request/response processors
    │   ├── logging_mw.py     # Log all updates
    │   ├── rate_limit_mw.py  # Anti-spam
    │   └── auth_mw.py        # Auto-register users
    │
    ├── keyboards/         # Inline + Reply keyboards
    │   ├── language.py     # Language selection
    │   ├── onboarding.py   # 9-step profile
    │   ├── main_menu.py    # Main menu
    │   ├── swipe.py        # Swipe buttons
    │   ├── profile.py      # Profile edit
    │   ├── premium.py      # Subscription tiers
    │   └── admin.py        # Admin panel
    │
    ├── states/            # FSM state definitions
    │   ├── onboarding.py   # 9 profile steps
    │   ├── edit_profile.py # Profile editing
    │   ├── swipe_flow.py   # Swiping
    │   ├── premium_flow.py # Premium flow
    │   └── admin_flow.py   # Admin actions
    │
    ├── services/          # Business logic
    │   ├── matching.py     # Matching algorithm
    │   ├── swipe_logic.py  # Swipe quotas
    │   ├── premium_service.py # Subscriptions
    │   ├── analytics_service.py # Stats
    │   ├── safety_service.py   # Blocking/reports
    │   ├── notifications.py    # Match alerts
    │   ├── scheduler.py        # Background jobs
    │   └── nlp_service.py      # AI integration
    │
    └── handlers/          # Command & callback handlers
        ├── start.py           # /start command
        ├── onboarding.py      # Profile creation
        ├── swipe.py           # Swiping interface
        ├── premium.py         # Premium purchases
        ├── profile.py         # Profile viewing
        ├── matches.py         # Match listing
        ├── messages.py        # Messaging
        ├── settings.py        # User settings
        ├── admin.py           # Admin commands
        ├── payments.py        # Payment hooks
        └── errors.py          # Error handling
```

---

## 🔧 Configuration (.env)

```env
# Bot
BOT_TOKEN=123456789:ABCDefGhIjklMnoPqrsTuvWxyz  # From @BotFather
ADMIN_IDS=123456789,987654321                    # Your Telegram IDs

# Database
DB_PATH=bot.db

# Environment
ENV=dev                    # or: prod

# AI/NLP (Optional - for OpenAI, etc.)
AI_API_BASE_URL=https://api.openai.com/v1
AI_API_KEY=sk-your-key-here

# Rate Limiting
RATE_LIMIT_SWIPES_PER_HOUR=100
RATE_LIMIT_MESSAGES_PER_MINUTE=10
```

---

## 🎯 Core Features

### ✅ 1. 9-Step Profile Creation (FSM)
```
Language → Name → Age → Gender → City → Interests → Purpose → Bio → Photo
```
Uses **StateFilter** from aiogram 3 for clean state management.

### ✅ 2. Smart Swiping
- Gender-based filtering
- Prevents duplicate swipes
- Respects blocking
- Quota system (8 free / 20 premium daily)
- Match detection on mutual likes

### ✅ 3. Telegram Stars Payments
```python
await bot.send_invoice(
    user_id,
    title="Premium Membership",
    currency="XTR",  # Telegram Stars
    prices=[types.LabeledPrice(label="5 Days", amount=5)]
)
```
Fully integrated with pre-checkout & successful payment handlers.

### ✅ 4. Premium Tiers
- **5-Day Trial**: $4.99 / 5⭐
- **1 Month**: $9.99 / 20⭐  
- **3 Months**: $24.99 / 50⭐

### ✅ 5. Admin Dashboard
```
/admin → Shows:
  • Total users & active today
  • Swipes & matches today
  • Premium subscriber count
  • Revenue tracking
```

### ✅ 6. AI/NLP Integration
```python
nlp_service.generate_profile_bio_suggestion()
nlp_service.suggest_opening_line()
nlp_service.moderate_message()
```
Uses OpenAI-compatible API (configurable endpoint).

### ✅ 7. Safety Features
- Block users
- Report moderation
- Rate limiting
- Message moderation (optional AI)

### ✅ 8. Background Jobs (APScheduler)
- **Midnight**: Reset daily swipes
- **Hourly**: Check subscription expiry
- **Daily**: Generate analytics

---

## 📊 Database Schema (14 Tables)

| Table | Purpose |
|-------|---------|
| **users** | User registration |
| **profiles** | 9-step profile data |
| **swipes** | Swipe history |
| **matches** | Mutual matches |
| **messages** | Chat history |
| **subscriptions** | Premium tiers |
| **payments** | Transaction history |
| **swipe_usage** | Daily quota tracking |
| **blocked_users** | Blocking relationships |
| **reports** | Moderation reports |
| **rate_limits** | Anti-spam tracking |
| **analytics** | User action logging |
| **profile_boosts** | Visibility boosters |

All tables have **performance indexes** for 10k+ user scalability.

---

## 🔌 Deployment

### Docker (Recommended)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

**Build & Run:**
```bash
docker build -t meetme-india .
docker run -e BOT_TOKEN=... -e ADMIN_IDS=... meetme-india
```

### VPS/Cloud

```bash
# SSH into server
ssh user@server_ip

# Setup
git clone ...
cd MeetMeIndia_Complete_2026
pip install -r requirements.txt

# Set environment
echo "BOT_TOKEN=..." > .env
echo "ADMIN_IDS=..." >> .env

# Run with systemd
sudo nano /etc/systemd/system/meetme.service
```

**Systemd service:**
```ini
[Unit]
Description=MeetMe India Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MeetMeIndia_Complete_2026
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable meetme
sudo systemctl start meetme
```

### Webhook Setup (Production)

Replace polling with webhook:

```python
# In main.py
async def main():
    # Instead of polling:
    # await dispatcher.start_polling(bot, ...)
    
    # Use webhook:
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web
    
    app = web.Application()
    setup_application(app, dispatcher, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    # Set webhook with Telegram
    await bot.set_webhook_info(
        url="https://yourdomain.com/webhook",
        allowed_updates=["message", "callback_query"]
    )
```

---

## 📈 Scaling to 10,000+ Users

### Database
```bash
# Switch from SQLite to PostgreSQL
pip install asyncpg

# Update DB connection string
DATABASE_URL=postgresql://user:pass@localhost/meetme
```

### Caching (Redis)
```python
import aioredis

redis = await aioredis.create_redis_pool('redis://localhost')
await redis.set(f"user:{user_id}:swipes", swipes_count)
```

### Load Balancing
```
Nginx → Load Balancer
  ├── Bot Instance 1
  ├── Bot Instance 2
  └── Bot Instance 3
      ↓
   PostgreSQL Cluster
```

### Monitoring
```python
# Add Sentry for error tracking
import sentry_sdk
sentry_sdk.init("https://key@sentry.io/project")

# Add Prometheus for metrics
from prometheus_client import Counter
swipes_counter = Counter('swipes_total', 'Total swipes')
```

---

## 🧪 Testing

```bash
# Unit tests (create bot/tests/)
python -m pytest bot/tests/ -v

# Load test (simulated users)
from locust import HttpUser, task

class BotUser(HttpUser):
    @task
    def swipe(self):
        self.client.post("/swipe", json={"action": "like"})
```

---

## 📝 Common Commands

| Command | Purpose |
|---------|---------|
| `/start` | Begin onboarding |
| `/admin` | Admin dashboard |
| `/delete_account` | GDPR account deletion |
| `🔥 Start Swiping` | Main swiping interface |
| `💕 My Matches` | View matches |
| `💬 Messages` | Chat interface |
| `👑 Premium` | Subscription menu |

---

## 🐛 Troubleshooting

**"Module not found: aiogram"**
```bash
pip install --upgrade aiogram
```

**"Bot token invalid"**
- Check `.env` file
- Verify token from @BotFather
- Restart bot

**"Database locked"**
- SQLite doesn't handle concurrent writes well
- Switch to PostgreSQL for production

**"No swipes remaining"**
- Expected for free users after 8 swipes
- Show premium upgrade offer

---

## 🌟 Next Steps

1. **Test locally**: `python main.py`
2. **Deploy to VPS**: Use Docker or systemd
3. **Scale database**: PostgreSQL + Redis
4. **Add analytics**: Sentry, Datadog
5. **Monitor performance**: APM tools
6. **A/B test**: Premium offers, UI changes

---

## 📚 Documentation Links

- [aiogram 3.x Docs](https://docs.aiogram.dev)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Payments](https://core.telegram.org/bots/api#payments)
- [SQLite Async](https://aiosqlite.readthedocs.io)
- [APScheduler](https://apscheduler.readthedocs.io)

---

## 💡 Tips for Production

✅ Use **environment variables** for secrets  
✅ Enable **logging** to files (bot.log)  
✅ Setup **error alerting** (Sentry)  
✅ Monitor **database performance** (slow queries)  
✅ Cache **hot data** (Redis)  
✅ Use **CDN** for photos  
✅ Implement **rate limiting** on all endpoints  
✅ Add **request validation** before DB calls  
✅ Setup **SSL certificates** (Nginx)  
✅ Regular **database backups**  

---

**Built with ❤️ for the 2026 era of Telegram bots.**  
**Let's match people! 💕 🚀**
