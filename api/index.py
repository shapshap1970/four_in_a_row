"""
Vercel serverless function entry point
Note: WebSocket support is limited on Vercel serverless.
For full WebSocket support, consider using a dedicated server.
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the FastAPI app from web_server
# We'll create a simplified version without WebSocket for Vercel
from web_server import app

# Export for Vercel
handler = app
