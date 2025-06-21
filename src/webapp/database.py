"""Database configuration and utilities."""
from sqlmodel import Session

from webapp.config import engine

def get_session():
    """Get a database session."""
    with Session(engine) as session:
        yield session
