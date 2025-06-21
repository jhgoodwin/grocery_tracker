"""Application configuration."""
from pathlib import Path
from sqlmodel import create_engine

# Database setup
DATA_DIR = Path(__file__).parent.parent.parent / 'data'
DATABASE_URL = f"sqlite:///{DATA_DIR}/grocery_tracker.sqlite"
engine = create_engine(DATABASE_URL, echo=False)
