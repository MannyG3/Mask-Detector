# Vercel Deployment Guide for MaskGuard

## ⚠️ Important Limitations

Vercel is **NOT recommended** for this application due to:

1. **No WebSocket Support** - Live camera detection will not work
2. **60-second timeout** - Video processing will fail for longer videos
3. **Ephemeral filesystem** - Database resets on each deployment
4. **Serverless architecture** - Background jobs won't work

## Recommended Alternatives

For full functionality, deploy to:
- **Railway** (recommended) - `railway up`
- **Render** - Connect GitHub repo
- **Fly.io** - `fly launch`
- **Google Cloud Run** - Container-based deployment

## Deploy to Vercel (Limited Functionality)

If you still want to try Vercel:

### Prerequisites
```bash
npm install -g vercel
```

### Deploy
```bash
cd maskguard
vercel
```

### What Works on Vercel
- ✅ Homepage
- ✅ Image upload detection
- ✅ Dashboard (view-only, no persistent data)
- ✅ Static files

### What Doesn't Work
- ❌ Live webcam detection (WebSocket)
- ❌ Video processing (timeout)
- ❌ Persistent logging (ephemeral storage)
- ❌ Background jobs

## Environment Variables

Set these in Vercel dashboard:
```
DUMMY_MODEL=true
ALERT_COOLDOWN_SECONDS=10
SNAPSHOTS_ENABLED=false
```

## Better Deployment: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd maskguard
railway init
railway up
```

Railway supports:
- ✅ WebSockets
- ✅ Long-running processes
- ✅ Persistent volumes
- ✅ PostgreSQL/SQLite databases
