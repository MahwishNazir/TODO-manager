"""Vercel serverless function entrypoint."""
import sys
from pathlib import Path

# Add backend directory to Python path for local imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import FastAPI app from existing module
from src.main import app

__all__ = ["app"]
