# Advanced Deployment Guide

## 🚀 Production Deployment Checklist

### Pre-Deployment

- [ ] Update Python to 3.11+
- [ ] Test all FSM flows locally
- [ ] Verify Telegram Stars sandbox mode
- [ ] Set up monitoring (Sentry, DataDog, etc.)
- [ ] Configure logging to file
- [ ] Setup database backups
- [ ] Create admin users list
- [ ] Test bot with 10+ concurrent users

### Environment

**Development:**
```env
ENV=dev
BOT_TOKEN=dev_token_from_botfather
ADMIN_IDS=your_telegram_id
LOG_LEVEL=DEBUG
DB_PATH=bot_dev.db
```

**Production:**
```env
ENV=prod
BOT_TOKEN=prod_token_from_botfather
ADMIN_IDS=admin1_id,admin2_id,admin3_id
LOG_LEVEL=WARNING
DB_PATH=/var/lib/meetme/bot.db
RATE_LIMIT_SWIPES_PER_HOUR=100
RATE_LIMIT_MESSAGES_PER_MINUTE=10
AI_API_BASE_URL=https://api.openai.com/v1
```

---

## 🐳 Docker Deployment (Recommended)

### Single Container

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create volume for database
VOLUME ["/data"]

# Environment defaults
ENV DB_PATH=/data/bot.db

# Run
CMD ["python", "main.py"]
```

**docker-compose.yml (Single Bot):**
```yaml
version: '3.8'

services:
  bot:
    build: .
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      ADMIN_IDS: ${ADMIN_IDS}
      DB_PATH: /data/bot.db
      LOG_LEVEL: WARNING
    volumes:
      - ./data:/data
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Deploy:**
```bash
# Create .env
echo "BOT_TOKEN=..." > .env
echo "ADMIN_IDS=..." >> .env

# Run
docker-compose up -d

# Check logs
docker-compose logs -f bot

# Stop
docker-compose down
```

### Docker with PostgreSQL

**docker-compose.yml (Production Scale):**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: meetme
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: meetme_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: always

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: always
    volumes:
      - redis_data:/data

  bot:
    build: .
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      ADMIN_IDS: ${ADMIN_IDS}
      DATABASE_URL: postgresql://meetme:${POSTGRES_PASSWORD}@postgres:5432/meetme_db
      REDIS_URL: redis://redis:6379/0
      LOG_LEVEL: WARNING
    depends_on:
      - postgres
      - redis
    restart: always

volumes:
  postgres_data:
  redis_data:
```

---

## 🖥️ VPS Deployment (Linode, DigitalOcean, AWS)

### Step 1: Server Setup

```bash
# SSH into server
ssh root@server_ip

# Update system
apt update && apt upgrade -y

# Install Python & dependencies
apt install -y python3.11 python3-pip python3-venv git

# Install PostgreSQL (optional)
apt install -y postgresql postgresql-contrib

# Install Redis (for caching)
apt install -y redis-server

# Create app user
useradd -m -s /bin/bash meetme
su - meetme
```

### Step 2: Deploy Application

```bash
# Clone repository
git clone https://github.com/yourusername/meetme-india.git
cd meetme-india

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create config
cp .env.example .env
nano .env  # Edit with actual values
```

### Step 3: Systemd Service

Create `/etc/systemd/system/meetme-bot.service`:

```ini
[Unit]
Description=MeetMe India Telegram Bot
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=meetme
WorkingDirectory=/home/meetme/meetme-india
Environment="PATH=/home/meetme/meetme-india/venv/bin"
EnvironmentFile=/home/meetme/meetme-india/.env
ExecStart=/home/meetme/meetme-india/venv/bin/python main.py
Restart=on-failure
RestartSec=10s

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=meetme-bot

# Resource limits
MemoryMax=1G
CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

**Enable & Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable meetme-bot
sudo systemctl start meetme-bot
sudo systemctl status meetme-bot

# View logs
sudo journalctl -u meetme-bot -f
```

### Step 4: Nginx Reverse Proxy (for Webhooks)

Create `/etc/nginx/sites-available/meetme`:

```nginx
server {
    listen 80;
    server_name api.meetme-india.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.meetme-india.com;
    
    ssl_certificate /etc/letsencrypt/live/api.meetme-india.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.meetme-india.com/privkey.pem;
    
    location /webhook {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Setup SSL:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.meetme-india.com
```

### Step 5: Database Setup

**PostgreSQL:**
```bash
sudo -u postgres psql

CREATE USER meetme WITH PASSWORD 'strongpassword';
CREATE DATABASE meetme_db OWNER meetme;
GRANT ALL PRIVILEGES ON DATABASE meetme_db TO meetme;
\q
```

**Update .env:**
```env
DATABASE_URL=postgresql://meetme:strongpassword@localhost/meetme_db
```

---

## 🔍 Monitoring & Logging

### Sentry (Error Tracking)

```python
# In main.py
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration

sentry_sdk.init(
    dsn="https://key@sentry.io/project",
    integrations=[AsyncioIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

### Logging to File

```python
import logging
from logging.handlers import RotatingFileHandler

# Create logger
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'bot.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# Metrics
swipes_counter = Counter('swipes_total', 'Total swipes')
matches_counter = Counter('matches_total', 'Total matches')
message_latency = Histogram('message_latency_seconds', 'Message send latency')

# Start metrics server
start_http_server(8000)  # Expose at :8000/metrics

# Use in handlers
@router.message.handler(Command("start"))
async def cmd_start(message: Message):
    swipes_counter.inc()
    # ...
```

---

## 🚨 Backup & Recovery

### Database Backups

**PostgreSQL Backup (daily):**
```bash
#!/bin/bash
BACKUP_DIR="/backups/meetme"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p $BACKUP_DIR

pg_dump -U meetme meetme_db | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/db_$TIMESTAMP.sql.gz"
```

**Crontab (automated daily at 3 AM):**
```bash
0 3 * * * /home/meetme/backup_db.sh
```

### SQLite Backup

```bash
#!/bin/bash
cp /data/bot.db /backups/bot_$(date +%Y%m%d_%H%M%S).db
```

### Recovery

```bash
# Restore PostgreSQL
gunzip < /backups/db_20240115_030000.sql.gz | psql -U meetme meetme_db

# Restore SQLite
cp /backups/bot_20240115_030000.db /data/bot.db
```

---

## 📊 Performance Tuning

### Database Indexes

The schema includes 15 indexes for optimal performance:

```sql
CREATE INDEX idx_users_language ON users(language);
CREATE INDEX idx_profiles_gender ON profiles(gender);
CREATE INDEX idx_swipes_user_id ON swipes(user_id);
CREATE INDEX idx_matches_user_id ON matches(user_id);
-- ... (12 more)
```

### Redis Caching

```python
import aioredis

redis = await aioredis.create_redis_pool('redis://localhost')

# Cache profile for 1 hour
await redis.setex(
    f"profile:{user_id}",
    3600,
    json.dumps(profile_data)
)

# Retrieve
cached = await redis.get(f"profile:{user_id}")
```

### Connection Pooling (PostgreSQL)

```python
import asyncpg

pool = await asyncpg.create_pool(
    'postgresql://meetme:pass@localhost/meetme_db',
    min_size=10,
    max_size=20
)

async with pool.acquire() as conn:
    await conn.fetch('SELECT * FROM users')
```

---

## 🔐 Security Hardening

### Environment Variables
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use strong secrets
openssl rand -base64 32  # For JWT tokens if needed
```

### SQL Injection Prevention
✅ All queries use parameterized statements:
```python
# ✅ SAFE
await db.executescript("SELECT * FROM profiles WHERE user_id = ?", (user_id,))

# ❌ UNSAFE
await db.executescript(f"SELECT * FROM profiles WHERE user_id = {user_id}")
```

### Rate Limiting
Implemented in middleware - verified in production with:
```python
# 100 swipes per hour
await rate_limit_mw.check_rate(user_id, "swipe", limit=100)
```

---

## 🆘 Troubleshooting Production Issues

### Bot Not Responding

```bash
# Check if running
ps aux | grep python

# View logs
sudo journalctl -u meetme-bot -n 50

# Restart
sudo systemctl restart meetme-bot
```

### Database Connection Error

```bash
# Test PostgreSQL
psql -U meetme -h localhost -d meetme_db

# Verify .env DATABASE_URL
cat .env | grep DATABASE_URL

# Check database logs
sudo -u postgres tail -f /var/log/postgresql/postgresql.log
```

### High Memory Usage

```bash
# Monitor process
top -p $(pgrep -f "python main.py")

# Check for memory leaks
python -m memory_profiler main.py
```

### Webhook Not Receiving Updates

```bash
# Test webhook
curl -X POST https://api.meetme-india.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"update_id": 1}'

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
```

---

## 📈 Scaling to 100k+ Users

1. **Database Sharding**: Split users by region/ID range
2. **Read Replicas**: PostgreSQL read-only replicas
3. **Message Queue**: RabbitMQ for async tasks
4. **Microservices**: Separate services for matching, notifications
5. **CDN**: CloudFlare for media delivery
6. **Load Balancer**: HAProxy/AWS ALB for bot instances
7. **Cache Layer**: Redis Cluster
8. **Monitoring**: Full observability stack

---

**Ready to go live? Deploy with confidence! 🚀**
