# 🚀 Railway Deployment Guide

## What is Railway?

Railway is a modern cloud platform for deploying apps. It's affordable, easy to use, and perfect for Telegram bots:
- **Free tier:** 0.5GB RAM, limited hours/month
- **Paid tier:** $0.50/hour (~$5-10/month for a bot)
- **Automatic SSL:** ✅
- **Environment variables:** ✅ Built-in
- **Database:** ✅ PostgreSQL included

## Step 1: Prepare Your Code for Railway

### Create `.railwayenv` file (Railway-specific config)

```bash
PYTHON_VERSION=3.12
```

### Create `railway.json` (Railway metadata)

```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "Always"
  }
}
```

### Create `Procfile` (for Railway to know how to start)

```
worker: python main.py
```

## Step 2: Create Dockerization (Optional but Recommended)

Create `Dockerfile` in root directory:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory for SQLite
RUN mkdir -p data/

# Run bot
CMD ["python", "main.py"]
```

Create `.dockerignore`:

```
venv/
.git/
.gitignore
__pycache__/
*.pyc
.pytest_cache/
.env
.DS_Store
```

## Step 3: Deploy to Railway

### Option A: Railway CLI (Easiest)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login
# This opens browser for authentication

# 3. Create new project
railway init
# Follow prompts

# 4. Connect your GitHub (optional but recommended)
railway link
# Or push directly:
railway up

# 5. View logs
railway logs

# 6. Check status
railway status
```

### Option B: GitHub Integration (Best for CI/CD)

1. Go to [railway.app](https://railway.app)
2. Sign up / Log in
3. Click "Create New Project"
4. Select "Deploy from GitHub"
5. Connect your GitHub account
6. Select the repository
7. Railway auto-deploys on every push to main branch

### Option C: Web Dashboard (Manual)

1. Go to [railway.app](https://railway.app)
2. Create new project
3. Click "Deploy from repo"
4. Upload your code or connect GitHub
5. Railway detects Python and auto-configures

## Step 4: Configure Environment Variables

### In Railway Dashboard:

1. Go to your project
2. Select your environment (e.g., "production")
3. Click "Variables"
4. Add these variables:

```
BOT_TOKEN = (your telegram bot token from @BotFather)
ADMIN_IDS = (your telegram user id, get from @userinfobot)
ENVIRONMENT = production
AI_ENABLED = false
DATABASE_PATH = data/meetme.db
LOG_LEVEL = INFO
```

### For PostgreSQL (Production):

Railway automatically provides `DATABASE_URL`:

```
DATABASE_URL = postgresql://user:pwd@host:port/db
```

Use it in your `config.py`:

```python
import os
db_url = os.getenv('DATABASE_URL')
if db_url:
    # Use PostgreSQL
else:
    # Use SQLite fallback
```

## Step 5: Set Up Database Persistence

### Option A: Volume Storage (Recommended)

In Railway, add a volume:

1. Go to Variables
2. Add volume mount: `/app/data`
3. This persists SQLite data between restarts

### Option B: PostgreSQL (Better for production)

1. In Railway dashboard, click "+" to add service
2. Select "PostgreSQL"
3. Railway auto-provides `DATABASE_URL` in environment
4. Migration runs automatically on `run_migrations()`

## Step 6: Configure Bot Webhook (Optional)

For production, webhook is better than polling:

```python
# In main.py, replace polling with:
WEBHOOK_URL = "https://your-railway-app.up.railway.app/webhook"
WEBHOOK_PATH = "/webhook"

await bot.set_webhook_info(
    url=WEBHOOK_URL,
    drop_pending_updates=True
)

# Setup webhook handler
app = web.Application()
app.router.post("/webhook", webhook_handler)
```

## Step 7: Monitoring & Logs

### View Logs

```bash
# Via CLI
railway logs

# Via Dashboard
# Click your project → Deployments → View Logs
```

### Common Issues

| Issue | Solution |
|-------|----------|
| `BOT_TOKEN not found` | Add to Railway Variables |
| `Database connection failed` | Check `DATABASE_URL` in Variables |
| `Module not found` | Ensure `requirements.txt` has all imports |
| `Memory exceeded` | Upgrade to paid tier or optimize code |

## Step 8: Scaling

### For 1K-10K users:

- Keep on Railway free tier
- Use SQLite with volume storage
- Monitor memory with: `railway status`

### For 10K-100K users:

- Upgrade to Railway Pro ($0.50/hour)
- Switch to PostgreSQL
- Use webhook instead of polling
- Add Redis for caching

### For 100K+ users:

- Multiple Railway instances with load balancer
- Dedicated PostgreSQL database
- CDN for media (Cloudflare, S3)
- Consider VPS or Kubernetes

## Step 9: Continuous Deployment

### Auto-Deploy on GitHub Push

```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: railwayapp/railway-action@v1
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}
```

## Step 10: Cost Estimation

### Free Tier
- **Cost:** $0/month
- **Uptime:** ~50 hours/month
- **RAM:** 0.5GB
- **Perfect for:** Dev/testing, low-volume bots

### Pro Tier
- **Cost:** ~$5-10/month depending on usage
- **Uptime:** 24/7
- **RAM:** 2GB+
- **Perfect for:** Production bots with active users

### PostgreSQL Add-on
- **Cost:** ~$5-15/month
- **Storage:** Up to 256GB
- **Backups:** Automatic
- **Perfect for:** Scaling to 10K+ users

## Troubleshooting

### Bot not responding

```bash
# Check if bot is running
railway status

# View latest logs
railway logs -n 50

# Restart bot
railway redeploy
```

### Environment variable not working

```bash
# Re-set variables (Railway caches them)
railway variables set BOT_TOKEN=your_new_token

# Redeploy
railway redeploy
```

### Database errors

```bash
# Check if database file exists in volume
railway shell
ls -la data/

# For PostgreSQL, test connection
PGPASSWORD=pwd psql -h host -U user -d db -c "SELECT 1"
```

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Test bot on Telegram
3. ✅ Setup monitoring with Sentry
4. ✅ Create backup strategy
5. ✅ Document API endpoints
6. ✅ Prepare for monetization

---

**Questions?** Check Railway docs: https://docs.railway.app
