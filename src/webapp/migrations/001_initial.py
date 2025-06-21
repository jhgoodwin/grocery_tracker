from sqlmodel import SQLModel
from webapp.stores.models import Store
from webapp.products.models import Product

def run_migration(engine):
    """Create initial tables"""
    SQLModel.metadata.create_all(engine)
