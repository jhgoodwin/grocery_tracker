"""Store data models."""
from datetime import datetime
from typing import Optional
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class Store(SQLModel, table=True):
    """Store model representing a grocery store location."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str
    city: str = Field(index=True)
    state: str = Field(max_length=2, index=True)
    zip_code: str = Field(max_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Market Fresh",
                "address": "123 Main St",
                "city": "Springfield",
                "state": "MA",
                "zip_code": "01234"
            }
        }
    )
