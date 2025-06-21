"""Test PLU import functionality."""
from datetime import datetime
from pathlib import Path
import pytest
from sqlmodel import Session, select

from webapp.products.etl import import_plu_commodities, save_plu_commodities
from webapp.products.models import PluCommodity


def test_save_plu_commodities_handles_duplicates(session: Session):
    """Test that save_plu_commodities handles duplicate PLUs correctly."""
    # Create initial PLU
    plu1 = PluCommodity(
        plu="4014",
        type="Global",
        category="Fruits",
        commodity="ORANGES",
        variety="Valencia",
        size="Small",
        measures_na="113 size and smaller",
        measures_row="Average Fruit Dimensions = less than 66mm",
        botanical="Citrus spp.",
        status="Approved",
        updated_by="Test",
        language="EN"
    )
    
    # Create duplicate PLU with updated data
    plu2 = PluCommodity(
        plu="4014",  # Same PLU
        type="Global",
        category="Fruits",
        commodity="ORANGES",
        variety="Valencia",
        size="Small",
        measures_na="Updated measure",  # Different measure
        measures_row="Updated row measure",
        botanical="Citrus spp.",
        status="Approved",
        updated_by="Test2",
        language="EN"
    )
    
    # Save first PLU
    saved = save_plu_commodities(session, [plu1])
    assert len(saved) == 1
    assert saved[0].plu == "4014"
    assert saved[0].measures_na == "113 size and smaller"
    
    # Try to save duplicate PLU
    saved = save_plu_commodities(session, [plu2])
    assert len(saved) == 1
    assert saved[0].plu == "4014"
    assert saved[0].measures_na == "Updated measure"  # Should be updated
    
    # Verify only one record exists
    stmt = select(PluCommodity).where(PluCommodity.plu == "4014")
    results = session.exec(stmt).all()
    assert len(results) == 1
