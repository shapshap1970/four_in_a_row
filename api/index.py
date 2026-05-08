"""
Vercel serverless function entry point
Note: Limitations on Vercel:
- No Rust binary execution (falls back to Python AI)
- No WebSocket support (disabled)
- 10-60s timeout limits
- Reduced AI depth for faster responses
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set environment variable to disable Rust AI on Vercel
os.environ['VERCEL_DEPLOYMENT'] = '1'
os.environ['DISABLE_RUST_AI'] = '1'

# Import the FastAPI app from web_server
from web_server import app

# Export for Vercel
handler = app
