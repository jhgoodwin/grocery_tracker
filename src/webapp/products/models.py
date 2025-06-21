"""Product data models."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel, Relationship
from webapp.stores.models import Store


class Product(SQLModel, table=True):
    """Product model representing a grocery item."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    brand: Optional[str] = Field(default=None, index=True)
    upc: Optional[str] = Field(default=None, unique=True)
    unit: str = Field(default="each")  # each, lb, oz, etc
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Config:
        """Model configuration."""
        
        schema_extra = {
            "example": {
                "name": "Organic Bananas",
                "brand": "Fresh Pick",
                "upc": "123456789012",
                "unit": "lb"
            }
        }


class ProductPrice(SQLModel, table=True):
    """Product price at a specific store and time."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    store_id: int = Field(foreign_key="store.id", index=True)
    price: Decimal = Field(max_digits=10, decimal_places=2)
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    
    product: Product = Relationship()
    store: Store = Relationship()
    
    class Config:
        """Model configuration."""
        
        schema_extra = {
            "example": {
                "price": "2.99",
                "observed_at": "2025-06-21T11:32:48"
            }
        }


class ProductPriceSnapshot(SQLModel, table=True):
    """Product price snapshot with validity period."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    store_id: int = Field(foreign_key="store.id", index=True)
    price: Decimal = Field(max_digits=10, decimal_places=2)
    valid_from: datetime = Field(index=True)
    valid_until: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    product: Product = Relationship()
    store: Store = Relationship()
    
    class Config:
        """Model configuration."""
        
        schema_extra = {
            "example": {
                "price": "2.99",
                "valid_from": "2025-06-21T11:44:41",
                "valid_until": "2025-12-31T23:59:59"
            }
        }


class PluCommodity(SQLModel, table=True):
    """PLU commodity representing a standardized produce item."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    plu: str = Field(unique=True, index=True)
    type: str
    category: str = Field(index=True)
    commodity: str = Field(index=True)
    variety: str
    size: str
    measures_na: Optional[str] = None
    measures_row: Optional[str] = None
    restrictions: Optional[str] = None
    botanical: Optional[str] = None
    aka: Optional[str] = None
    status: str = Field(index=True)
    link: Optional[str] = None
    notes: Optional[str] = None
    updated_by: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    language: str = Field(default="EN")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "plu": "3000",
                "type": "Global",
                "category": "Fruits",
                "commodity": "APPLES",
                "variety": "Alkmene",
                "size": "All Sizes",
                "status": "Approved",
                "language": "EN"
            }
        }
    )
