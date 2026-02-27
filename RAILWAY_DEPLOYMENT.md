# 🚀 Railway Deployment Guide

Railway is the best platform for MaskGuard because:

✅ **Full Feature Support**
- WebSocket (live detection)
- Long-running processes (video)
- Persistent storage
- Background jobs
- Automatic HTTPS

✅ **Excellent Performance**
- No cold starts
- Global CDN
- Automatic scaling
- <100ms response times

✅ **Free Tier**
- $5/month credit (covers typical usage)
- Deploy unlimited projects
- Automatic SSL certificates

---

## 🎯 Quick Deploy (2 minutes)

### Step 1: Install Railway CLI

```bash
# Install globally
npm install -g @railway/cli

# Or use with npx (no install needed)
npx @railway/cli@latest init
```

### Step 2: Login to Railway

```bash
railway login
# Opens browser → Authorize with GitHub
```

### Step 3: Deploy

```bash
# Navigate to project root
cd /workspaces/Mask-Detector

# Initialize Railway project
railway init

# Follow prompts:
# - Project name: maskguard
# - Environment: production

# Deploy!
railway up
```

Deployment takes 2-3 minutes. You'll see your app URL at the end.

### Step 4: Get Your Live URL

```bash
railway open
# Opens your deployed app in browser OR

railway logs
# Stream live logs
```

---

## 🔧 Configuration

Railway automatically detects Python/Docker and configures:

- **Buildpack**: Python (via Dockerfile)
- **Port mapping**: $PORT (auto-assigned)
- **Environment variables**: Set in dashboard

### Custom Environment Variables

In Railway dashboard (Variables tab):

```
DUMMY_MODEL=true                    # Use faster predictions initially
ALERT_COOLDOWN_SECONDS=10           # Seconds between alerts
SNAPSHOTS_ENABLED=false             # Save snapshots to /tmp
MAX_VIDEO_MB=100                    # Max video size
LIVE_FPS_CAP=30                     # Live webcam FPS limit
```

---

## ✅ Test Deployment

After deployment completes:

```bash
# Replace with your Railway URL
RAIL_URL="https://your-app.up.railway.app"

# 1. Health check
curl $RAIL_URL/api/health

# 2. Homepage
curl $RAIL_URL/

# 3. Live detection (WebSocket - works!)
# Open in browser: $RAIL_URL/live

# 4. Image detection
curl -X POST \
  -F "file=@test.jpg" \
  $RAIL_URL/api/detect/image

# 5. Video upload (works!)
curl -X POST \
  -F "file=@test.mp4" \
  $RAIL_URL/api/jobs/video

# 6. Dashboard
curl $RAIL_URL/dashboard
```

---

## 🚀 Features That Now Work

| Feature | Status | Railway Support |
|---------|--------|-----------------|
| Live Webcam (WebSocket) | ✅ | Full support |
| Video Processing | ✅ | Long timeouts allowed |
| Database Logging | ✅ | Persistent storage |
| Background Jobs | ✅ | Full support |
| Image Detection | ✅ | Works perfectly |
| Dashboard | ✅ | Full functionality |
| CSV Export | ✅ | Works |

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Real-time logs
railway logs

# Tail logs
railway logs --follow

# Filter by service
railway logs -s api
```

### Monitor in Dashboard

1. Go to [railway.app](https://railway.app)
2. Select your project "maskguard"
3. View:
   - **Deployments** - Build history
   - **Logs** - Real-time output
   - **Metrics** - CPU, RAM, disk usage
   - **Variables** - Environment variables
   - **Domain** - Your public URL

---

## 🔄 Update & Redeploy

After making changes:

```bash
# Commit changes
git add .
git commit -m "Update MaskGuard"
git push origin main

# Redeploy (option 1 - automatic)
# Railway auto-deploys on push if connected to GitHub

# Redeploy (option 2 - manual)
railway up --detach
```

---

## 💰 Pricing

**Free Tier:**
- $5/month credit
- Covers:
  - Small app running 24/7 (~$3/month)
  - Development/testing
  - Low traffic apps

**If you exceed:**
- Pay-as-you-go after free credit
- Typical usage: $5-20/month
- Scale automatically

**Cost Breakdown:**
- Compute: $0.0000115/second (shared CPU)
- Storage: $0.30/GB/month (for persistent data)
- Network: Free inbound, $0.02/GB outbound

---

## 🔐 Security

### Environment Variables

Set sensitive data in Railway dashboard (never in code):

```
# Dashboard → Variables tab
DB_PASSWORD=your-secret-password
API_KEY=your-api-key
```

Access in code:
```python
import os
password = os.getenv("DB_PASSWORD")
```

### HTTPS

✅ Automatic SSL/TLS certificate (Railway provides)

No configuration needed!

---

## 📈 Scaling

Railway automatically scales your app:

- **Shared CPU**: $0 (free tier)
- **CPU**: Can upgrade to dedicated
- **Memory**: Default 256MB, can increase
- **Replicas**: Set multiple instances

To scale:
1. Go to Railway dashboard
2. Select your service
3. Click "Settings"
4. Adjust CPU/memory/replicas

---

## ⚙️ Advanced Configuration

### Custom Dockerfile

If you want custom build steps, Railway uses:

```bash
# Railway looks for Dockerfile in repo root
# Falls back to detected runtime (Python)
```

Current setup uses our existing `Dockerfile` ✅

### Cron Jobs (Background Tasks)

To run periodic tasks (cleanup, checks, etc.):

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=0)
def cleanup_logs():
    # Clean database every midnight
    pass

scheduler.start()
```

---

## 🆘 Troubleshooting

### Build Fails

```bash
# Check logs
railway logs

# Common issues:
# - Missing requirements.txt (should be in maskguard/)
# - Python version mismatch
# - Port not set correctly
```

**Fix:**
- Ensure `maskguard/Dockerfile` exists
- Check `maskguard/requirements.txt`
- Verify port is `$PORT` (not hardcoded 8000)

### App Crashes

```bash
# View crash logs
railway logs --follow

# Common issues:
# - Import error
# - Missing environment variable
# - Out of memory
```

**Fix:**
- Install missing dependency: `pip install ...`
- Add environment variable in dashboard
- Increase memory allocation

### WebSocket Not Working

```bash
# Should work on Railway!
# Check logs for errors

railway logs | grep -i websocket
```

### Slow Image Detection

Reduce inference time:
```bash
# Set in Variables:
DUMMY_MODEL=true           # Faster predictions
LIVE_FPS_CAP=15            # Lower FPS
MAX_VIDEO_MB=50            # Smaller videos
```

---

## 🔄 CI/CD Integration

### Auto-Deploy on Push

1. Go to railway.app dashboard
2. Select project → Settings
3. Connect GitHub repository
4. Enable "Automatic Deployments"

Now:
- Every push to `main` auto-deploys
- Build logs shown in dashboard
- Rollback if build fails

### Preview Deployments

Enable preview environments:
```bash
# Deploy on pull request
railway up --environment=preview
```

---

## 📞 Support

**Railway Help:**
- Docs: [docs.railway.app](https://docs.railway.app)
- Discord: [railway.app/discord](https://railway.app/discord)
- Email: support@railway.app

**MaskGuard Issues:**
- Check logs: `railway logs`
- Verify config: `railway list`
- Check variables: Dashboard → Variables

---

## ✨ Example Workflow

### First Time Setup (One-time)
```bash
npm install -g @railway/cli
railway login
cd /workspaces/Mask-Detector
railway init
# Select project name: maskguard
railway up
railway open  # Get your live URL
```

### After Changes
```bash
git add .
git commit -m "Fix detection"
git push origin main
# Railway auto-deploys (if connected)
# OR manually: railway up --detach
```

### Monitor
```bash
railway logs --follow
# or
railway open  # View dashboard
```

### Scale Up
```bash
# In dashboard:
# Settings → Resources → Increase CPU/Memory
```

---

## 🎉 Success Checklist

- ✅ Railway CLI installed
- ✅ GitHub account connected to Railway
- ✅ MaskGuard pushed to GitHub
- ✅ Procfile in repository root
- ✅ railway.toml in repository root
- ✅ Deploy initiated
- ✅ App running at railway.app URL
- ✅ All features working:
  - ✅ Live webcam detection
  - ✅ Video processing
  - ✅ Image detection
  - ✅ Dashboard
  - ✅ Database persistence

You're all set! 🚀

---

**Next:** Deploy with `railway up`, then test at your new Railway URL!
