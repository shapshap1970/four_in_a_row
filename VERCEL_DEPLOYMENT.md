# Vercel Deployment Guide

## Overview
Four-in-a-Row game with AI opponent, deployable to Vercel serverless platform.

## Architecture Differences

### Local Development
- ✅ Rust AI at depth 12 (1-3 seconds per move)
- ✅ Python AI fallback
- ✅ Dynamic tree extension
- ✅ Opening book cache (67K positions)
- ✅ Full WebSocket support

### Vercel Deployment
- ⚠️ Python AI only at depth 6 (Rust binaries not supported)
- ⚠️ No persistent caching between requests
- ⚠️ WebSocket support limited
- ⚠️ 10-60s timeout limits
- ✅ Fast deployment and CDN distribution

## Deployment Steps

### 1. Prerequisites
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
```

### 2. Deploy
```bash
# From project root
vercel

# Or for production
vercel --prod
```

### 3. Environment Configuration
The app automatically detects Vercel environment and adjusts:
- Disables Rust AI
- Reduces search depth to 6
- Uses Python AI fallback

## Testing Before Deploy

### Run all tests
```bash
# Start local server
python web_server.py &

# Run comprehensive tests
python test_all_game_scenarios.py

# Test error handling
python test_web_error_handling.py
```

### Expected Results
- ✅ All scenarios pass
- ✅ AI responds in 1-3 seconds (local) or 0.5-2s (Vercel depth 6)
- ✅ Error handling works correctly
- ✅ 2-move rule enforced
- ✅ Game state consistent

## Performance Comparison

| Environment | AI Engine | Depth | Avg Response Time |
|-------------|-----------|-------|-------------------|
| Local       | Rust      | 12    | 1-3 seconds       |
| Local       | Python    | 6     | 0.5-2 seconds     |
| Vercel      | Python    | 6     | 1-3 seconds       |

## Known Limitations on Vercel

1. **No Rust Binary Execution**
   - Rust AI automatically disabled
   - Falls back to Python implementation

2. **Timeout Limits**
   - Hobby plan: 10 seconds
   - Pro plan: 60 seconds
   - Depth 6 Python AI stays well within limits

3. **No Persistent State**
   - Each request is fresh instance
   - Opening book and dynamic cache not persisted
   - Games stored in memory per instance

4. **WebSocket Limitations**
   - REST API works fine
   - WebSocket endpoints may not work properly

## Recommendations

### For Best Performance
- **Use Vercel for**: Web UI, REST API, global distribution
- **Use separate server for**: Rust AI, WebSocket, persistent caching

### Alternative: Hybrid Architecture
1. Deploy static files + REST API to Vercel
2. Deploy Rust AI worker to Railway/Render/Fly.io
3. Connect via API calls

## Files Structure

```
/
├── api/
│   └── index.py          # Vercel entry point
├── web_server.py         # Main FastAPI app
├── board.py              # Game logic
├── four_in_a_row_*.py    # AI engines
├── rust_ai_wrapper.py    # Rust AI wrapper (disabled on Vercel)
├── requirements-web.txt  # Dependencies
├── vercel.json          # Vercel config
└── .vercelignore        # Files to exclude
```

## Troubleshooting

### Deployment Fails
```bash
# Check logs
vercel logs

# Redeploy with verbose
vercel --debug
```

### Slow Response Times
- Depth 6 should respond in < 2 seconds
- Check Vercel function logs for errors
- Consider upgrading to Pro plan for better performance

### 504 Timeout Errors
- Reduce search depth further (depth 5 or 4)
- Or deploy to platform with longer timeouts

## Success Checklist

Before deploying to production:
- [x] All tests pass locally
- [x] Vercel configuration correct
- [x] Dependencies in requirements-web.txt
- [x] Environment detection working
- [ ] Test deployed version thoroughly
- [ ] Monitor performance metrics
- [ ] Set up error tracking (optional)

## Contact & Support

For issues related to:
- Game logic: Check test files
- Deployment: See Vercel documentation
- Performance: Adjust search depth in web_server.py
