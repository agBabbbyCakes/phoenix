# 🚀 Deploying to Render.com

## Quick Deploy (5 minutes)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com
2. Sign up / Log in (free account)
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub account
5. Select your repository
6. Render will **auto-detect** `render.yaml` ✅
7. Click **"Create Web Service"**
8. Wait 2-3 minutes for first deployment

### Step 3: Access Your Dashboard
- Render provides a URL like: `https://botscope.onrender.com`
- Your dashboard is live! 🎉

## What Render Auto-Configures

Your `render.yaml` already sets:
- ✅ Python environment
- ✅ Build command: `pip install -r requirements.txt`
- ✅ Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ Health check: `/health`
- ✅ Sample mode enabled: `FORCE_SAMPLE=1`
- ✅ Auto-deploy on git push

## Environment Variables (Optional)

You can add these in Render Dashboard → Environment:
- `FORCE_SAMPLE=1` (already set, enables demo mode)
- `SILVERBACK_LOG_PATH=/path/to/logs.jsonl` (for real bot logs)
- `APP_VERSION=1.0.0` (version displayed in API)

## After Deployment

Your dashboard is available at:
- Main Dashboard: `https://your-app.onrender.com/`
- Logs Viewer: `https://your-app.onrender.com/logs`
- Daily Report: `https://your-app.onrender.com/report`
- Health Check: `https://your-app.onrender.com/health`

## Troubleshooting

### Build Fails
- Check Render logs for errors
- Ensure `requirements.txt` is valid
- Verify Python 3.11+ is used (set in runtime.txt)

### App Won't Start
- Check that PORT is set (Render does this automatically)
- Verify `/health` endpoint works
- Check Render logs for startup errors

### Slow First Load
- Free tier has cold starts (15-30 seconds)
- Paid tier is instant

## Updating Your App

Just push to GitHub:
```bash
git push origin main
```

Render auto-deploys on every push! ✅

---

**Need help?** Check Render docs: https://render.com/docs
