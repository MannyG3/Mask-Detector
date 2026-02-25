# Vercel Deployment Guide (MaskGuard)

This guide deploys the `maskguard/` app to Vercel with the existing serverless adapter in `api/index.py`.

## Known limitations on Vercel

MaskGuard is a real-time CV app, and Vercel serverless has constraints:

1. **No stable WebSocket session support** for this architecture (live camera mode is not reliable)
2. **Function timeout** (configured to 60s) affects long video jobs
3. **Ephemeral filesystem** (`/tmp` only, reset between invocations)
4. **No persistent background workers** for long-running processing

Use Vercel for demo/static + basic API usage. For full production features, prefer Railway/Render/Fly.io.

## What works after deployment

- Homepage and page routes
- Image upload endpoint
- Basic dashboard rendering
- Static assets and templates

## What will not be production-ready on Vercel

- Live webcam WebSocket pipeline
- Long video processing jobs
- Persistent event history in SQLite

## Prerequisites

- A Vercel account
- Repository pushed to GitHub
- Vercel CLI installed (optional but recommended)

```bash
npm install -g vercel
```

## Option A: Deploy from Vercel Dashboard (recommended)

1. In Vercel, click **Add New Project** and import your GitHub repo.
2. In **Project Settings** during import:
	- **Framework Preset**: `Other`
	- **Root Directory**: `maskguard`
	- **Build Command**: leave empty
	- **Output Directory**: leave empty
3. Add these environment variables:

```env
DUMMY_MODEL=true
ALERT_COOLDOWN_SECONDS=10
SNAPSHOTS_ENABLED=false
DB_PATH=/tmp/events.db
UPLOADS_DIR=/tmp/uploads
OUTPUTS_DIR=/tmp/outputs
CAPTURES_DIR=/tmp/captures
```

4. Click **Deploy**.

## Option B: Deploy with CLI

From repo root:

```bash
cd maskguard
vercel login
vercel
```

When prompted:
- Link to existing project: choose as needed
- Set project root: current directory (`maskguard`)

Deploy to production:

```bash
vercel --prod
```

Set environment variables via CLI:

```bash
vercel env add DUMMY_MODEL production
vercel env add ALERT_COOLDOWN_SECONDS production
vercel env add SNAPSHOTS_ENABLED production
vercel env add DB_PATH production
vercel env add UPLOADS_DIR production
vercel env add OUTPUTS_DIR production
vercel env add CAPTURES_DIR production
```

Redeploy after env changes:

```bash
vercel --prod
```

## Verify deployment

Replace `<your-url>` with your Vercel domain:

```bash
curl -s https://<your-url>/api/health
curl -I https://<your-url>/static/css/app.css
```

Health should return JSON and static CSS should return `200`.

## Troubleshooting

### 404 on every route
- Confirm Vercel project **Root Directory** is `maskguard`
- Confirm `vercel.json` exists at `maskguard/vercel.json`

### Static or template files missing
- Confirm deployment uses `api/index.py` entrypoint
- Re-deploy after pulling latest `vercel.json`

### Data/logs disappear
- Expected on Vercel serverless due to ephemeral filesystem
- Move to managed database/storage for persistence

## Recommended production platforms for full features

- **Railway** (simple, supports long-running services)
- **Render** (easy GitHub-based deploy)
- **Fly.io** (container + persistent volumes)

These platforms better match MaskGuard’s WebSocket and background-processing requirements.
