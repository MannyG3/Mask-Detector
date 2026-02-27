# Deploy MaskGuard to Vercel

## ⚠️ Important Limitations

Vercel is a serverless platform designed for stateless applications. MaskGuard has features that **don't work well on Vercel:**

| Feature | Status | Reason |
|---------|--------|--------|
| Homepage | ✅ Works | Static HTML rendering |
| Image Detection | ✅ Works | Fits within 60s timeout |
| Live Webcam | ❌ Fails | No WebSocket support |
| Video Processing | ❌ Fails | Exceeds 60s timeout |
| Database Logging | ⚠️ Limited | Ephemeral /tmp, resets on redeploy |
| Background Jobs | ❌ Fails | No long-running processes |

## Why Consider Alternatives?

**Recommended Platforms for Full Functionality:**
- **Railway** (⭐ Best) - $0-5/month, supports everything
- **Render** - Free tier, full feature support
- **Fly.io** - Per-second billing, excellent performance
- **Replit** - Easy for development/demo

## Deploy to Vercel (Limited)

### Prerequisites
1. GitHub account with Mask-Detector repository
2. Vercel account (create at vercel.com)

### Steps

#### Option 1: Using Vercel CLI (Recommended)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Navigate to project
cd /workspaces/Mask-Detector/maskguard

# 4. Deploy
vercel --prod

# Follow prompts:
# - Select existing project or create new
# - Choose "." for root directory
# - Let Vercel detect Python project
```

#### Option 2: GitHub Integration (Easiest)

1. Go to [vercel.com/import](https://vercel.com/import)
2. Connect your GitHub account
3. Select `MannyG3/Mask-Detector` repository
4. Under "Root Directory", select: `maskguard`
5. Set environment variables:
   ```
   DUMMY_MODEL=true
   ALERT_COOLDOWN_SECONDS=10
   SNAPSHOTS_ENABLED=false
   ```
6. Click "Deploy"

Vercel will automatically redeploy on every push to `main`.

### Verification

After deployment:

```bash
# Test health endpoint
curl https://your-vercel-app.vercel.app/api/health

# Should return:
# {"status":"ok","timestamp":"..."}

# Test homepage
curl https://your-vercel-app.vercel.app/

# Should return HTML page
```

## What to Test on Vercel

### ✅ Working Features
```bash
# 1. Homepage
curl https://your-app.vercel.app/

# 2. Image Detection
curl -X POST \
  -F "file=@test.jpg" \
  https://your-app.vercel.app/api/detect/image

# 3. Dashboard
https://your-app.vercel.app/dashboard

# 4. Static Files
https://your-app.vercel.app/static/css/app.css
https://your-app.vercel.app/static/js/live.js
```

### ❌ Features Not Working
- `https://your-app.vercel.app/live` (WebSocket fails)
- `https://your-app.vercel.app/upload/video` (60s timeout)
- Database persistence (resets on redeploy)

## Configuration

Vercel uses `vercel.json` for configuration. Current settings:

```json
{
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": ".",
  "env": {
    "DUMMY_MODEL": "true",
    "DB_PATH": "/tmp/events.db",
    "UPLOADS_DIR": "/tmp/uploads",
    "OUTPUTS_DIR": "/tmp/outputs"
  }
}
```

**Note:** All file paths use `/tmp/` which is ephemeral (temporary).

## Environment Variables

Set these in Vercel dashboard (Settings → Environment Variables):

```
DUMMY_MODEL=true                    # Use pixel-based predictions (faster)
ALERT_COOLDOWN_SECONDS=10           # Cooldown between alerts
SNAPSHOTS_ENABLED=false             # Disable snapshot saving (storage limited)
MAX_VIDEO_MB=10                     # Reduce video size limit
LIVE_FPS_CAP=15                     # Reduce frame rate
```

## Troubleshooting

### Build Fails
- Check Python version in `runtime.txt` (should be `3.12`)
- Verify `requirements.txt` has all dependencies
- Check `.vercelignore` isn't excluding needed files

### 504 Timeout Errors
- Happens on image detection if model is too slow
- Set `DUMMY_MODEL=true` for faster predictions
- Reduce input image size

### Database Not Persisting
- Expected behavior on Vercel
- Use external database (Supabase, MongoDB Atlas) for production
- For demo, data resets on redeploy

### WebSocket Connection Fails
- Normal on Vercel (no WebSocket support)
- Try image/video upload instead
- For live detection, deploy to Railway/Render

## Better Alternative: Deploy to Railway

Railway is 100% compatible with MaskGuard:

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
cd /workspaces/Mask-Detector/maskguard
railway init

# 4. Deploy
railway up

# Get URL
railway open
```

**Railway Features:**
- ✅ WebSocket support
- ✅ No timeout limits
- ✅ Persistent file storage
- ✅ $5/month free credit
- ✅ Automatic SSL/HTTPS

## Better Alternative: Deploy to Render

Render is also fully compatible:

1. Go to [render.com/dashboard](https://render.com/dashboard)
2. Create New → Web Service
3. Connect your GitHub repository
4. Settings:
   - Name: `maskguard`
   - Root Directory: `maskguard`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Environment: Python 3.12
5. Set environment variables
6. Deploy

**Cost:** Free tier available (sleep after 15 min inactivity)

## Comparison Table

| Aspect | Vercel | Railway | Render | Fly.io |
|--------|--------|---------|--------|--------|
| WebSocket | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Long Running | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Storage | ❌ /tmp only | ✅ Yes | ✅ Yes | ✅ Yes |
| Database | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Free Tier | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Cold Starts | ⚠️ Up to 10s | ✅ <1s | ✅ <1s | ✅ <1s |
| Best For | Static + API | Full App | Full App | Global |

## Next Steps

### If deploying to Vercel:
1. ✅ Prepare deployment with `vercel login && vercel --prod`
2. ✅ Test endpoints listed above
3. ⚠️ Understand feature limitations
4. 💡 Consider migrating to Railway/Render later

### If deploying to Railway/Render:
1. ✅ Full feature support (recommended!)
2. ✅ All detection modes work
3. ✅ Database persistence
4. ✅ Better performance

---

**Questions?** See main [README.md](README.md) or [DEPLOYMENT.md](DEPLOYMENT.md)
