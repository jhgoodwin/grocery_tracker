"""Tests for store ETL functions."""
from pathlib import Path

import pytest
from sqlmodel import Session, select

from webapp.database import engine
from webapp.stores.etl import (
    load_gmaps_stores_from_csv,
    convert_gmaps_stores_to_store,
    save_stores_to_db,
)
from webapp.stores.models import Store


@pytest.fixture
def test_csv_path() -> Path:
    """Path to test CSV file."""
    return Path("data/grocery_stores_chattanooga.test.csv")


@pytest.fixture
def db_session():
    """Database session fixture."""
    with Session(engine) as session:
        yield session
        # Cleanup
        for store in session.exec(select(Store)):
            session.delete(store)
        session.commit()


def test_load_gmaps_stores(test_csv_path):
    """Should load store data from CSV."""
    stores = load_gmaps_stores_from_csv(test_csv_path)
    assert len(stores) > 0, "Should load at least one store"
    store = stores[0]
    assert store["name"] == "Publix Super Market on North Market Street", "Should load store name"
    assert "400 N Market St" in store["address"], "Should load store address"


def test_convert_gmaps_stores():
    """Should convert Google Maps format to Store models."""
    gmaps_data = [{
        "name": "Test Store",
        "address": "123 Main St, Springfield, MA 01234, USA"
    }]
    
    stores = list(convert_gmaps_stores_to_store(gmaps_data))
    assert len(stores) == 1, "Should convert one store"
    
    store = stores[0]
    assert store.name == "Test Store"
    assert store.address == "123 Main St"
    assert store.city == "Springfield"
    assert store.state == "MA"
    assert store.zip_code == "01234"


def test_save_stores_upsert(db_session):
    """Should handle both inserts and updates."""
    # Create test store
    store1 = Store(
        name="Test Store",
        address="123 Main St",
        city="Old City",
        state="MA",
        zip_code="01234"
    )
    
    # Initial save
    save_stores_to_db(iter([store1]))
    saved = db_session.exec(
        select(Store).where(Store.name == "Test Store")
    ).first()
    assert saved is not None, "Should insert new store"
    assert saved.city == "Old City"
    
    # Update with new city
    store2 = Store(
        name="Test Store",
        address="123 Main St",
        city="New City",
        state="MA",
        zip_code="01234"
    )
    save_stores_to_db(iter([store2]))
    
    # Verify update
    db_session.refresh(saved)
    updated = saved
    assert updated.id == saved.id, "Should keep same ID"
    assert updated.city == "New City", "Should update city"
