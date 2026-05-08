# Deploying to Vercel

## Quick Setup

### 1. Prerequisites
- GitHub account with this repository
- Vercel account (sign up at https://vercel.com)

### 2. Import Project to Vercel

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/new

2. **Import Git Repository**
   - Click "Import Git Repository"
   - Select "GitHub" 
   - Authenticate with GitHub if needed
   - Select `shapshap1970/four_in_a_row` repository

3. **Configure Project**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: Leave empty (not needed for Python)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Environment Variables** (Optional)
   - No environment variables needed for basic setup

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (~2-3 minutes)

### 3. Automatic Deployments

Once connected, Vercel will automatically:
- ✅ Deploy on every push to `main` branch
- ✅ Create preview deployments for pull requests
- ✅ Run builds and tests

## Important Notes

⚠️ **WebSocket Limitations**:
Vercel's serverless functions have limited WebSocket support. The AI progress updates (WebSocket) may not work on Vercel. 

For full WebSocket support, consider:
- Railway.app
- Render.com
- Fly.io
- Traditional VPS (DigitalOcean, Linode, etc.)

## What Works on Vercel
✅ Game creation (HTTP API)
✅ Player moves (HTTP API)
✅ Game state retrieval
✅ Basic HTML interface

❌ AI move progress updates (requires persistent WebSocket connection)

## Alternative: Run Locally or on a Server

For the full experience with WebSocket support:

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python web_server.py

# Visit http://localhost:8000
```

## Files for Vercel Deployment

- `vercel.json` - Vercel configuration
- `requirements.txt` - Python dependencies
- `api/index.py` - Serverless function entry point
- `web_server.py` - Main FastAPI application

## Troubleshooting

### Build Fails
- Check build logs in Vercel dashboard
- Ensure all dependencies are in `requirements.txt`

### App Not Loading
- Check function logs in Vercel dashboard
- Verify `api/index.py` is present

### WebSocket Not Working
- This is expected on Vercel serverless
- Consider alternative hosting for WebSocket support
