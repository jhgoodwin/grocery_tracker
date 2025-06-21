"""Store ETL functions for importing data from various sources."""
import csv
from datetime import datetime, UTC
from pathlib import Path
from typing import Iterator, List

from sqlmodel import Session, select

from webapp.database import engine
from webapp.stores.models import Store


def load_chattanooga_stores_from_csv(csv_path: Path) -> Iterator[Store]:
    """Load Chattanooga store data from CSV file.
    
    Args:
        csv_path: Path to CSV file
        
    Yields:
        Store models
    """
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            address_parts = row["address"].split(",")
            yield Store(
                name=row["name"],
                address=address_parts[0].strip(),
                city=row["city"].split(",")[0].strip(),
                state=row["state"],
                zip_code=row["zip_code"] if row["zip_code"] else None,
                phone=row["phone"],
                rating=float(row["rating"]) if row["rating"] else None,
                is_active=row["is_active"].lower() == "true"
            )


def load_gmaps_stores_from_csv(csv_path: Path) -> List[dict]:
    """Load store data from a Google Maps export CSV file.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        List of store records as dicts
    """
    stores = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            stores.append(row)
    return stores


def convert_gmaps_stores_to_store(gmaps_stores: List[dict]) -> Iterator[Store]:
    """Convert Google Maps store format to Store models.
    
    Args:
        gmaps_stores: List of store dicts from Google Maps export
        
    Yields:
        Store models
    """
    for store in gmaps_stores:
        # Extract state and zip from address components
        address_parts = store["address"].split(",")
        state_zip = address_parts[-2].strip().split()  # ['MA', '01234']
        state = state_zip[0]
        zip_code = state_zip[1][:5]  # First 5 digits
        
        yield Store(
            name=store["name"],
            address=address_parts[0].strip(),
            city=address_parts[-3].strip(),
            state=state,
            zip_code=zip_code
        )


def import_chattanooga_stores(csv_path: Path) -> None:
    """Import Chattanooga stores from Google Maps CSV export.
    
    Args:
        csv_path: Path to CSV file
    """
    stores = load_gmaps_stores_from_csv(csv_path)
    store_models = convert_gmaps_stores_to_store(stores)
    save_stores_to_db(store_models)


def save_stores_to_db(stores: Iterator[Store]) -> None:
    """Save stores to database, updating existing records if found.
    
    Args:
        stores: Iterator of Store models to save
    """
    with Session(engine) as session:
        for store in stores:
            # Check for existing store by name and address
            stmt = select(Store).where(
                Store.name == store.name,  # type: ignore
                Store.address == store.address  # type: ignore
            )
            existing = session.exec(stmt).first()
            
            if existing:
                # Update existing store
                for field in ['city', 'state', 'zip_code']:
                    setattr(existing, field, getattr(store, field))
                existing.updated_at = datetime.now(UTC)
                session.add(existing)
                session.commit()
            else:
                # Insert new store
                session.add(store)
                
        session.commit()
