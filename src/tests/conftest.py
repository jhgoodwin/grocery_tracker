"""Test configuration and fixtures."""
import pytest
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture
def session():
    """Create a fresh database session for a test."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
