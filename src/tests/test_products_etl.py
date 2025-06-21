from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine

from webapp.products.etl import import_plu_commodities
from webapp.products.models import PluCommodity

def test_import_plu_commodities():
    """Test importing PLU commodities from test CSV file."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        test_csv = Path("data/commodities.test.csv")
        commodities = import_plu_commodities(session, test_csv)
        
        assert len(commodities) == 2, "Should import 2 test commodities"
        
        apple = session.get(PluCommodity, 1)
        assert apple is not None, "Should find apple with id 1"
        assert apple.plu == "3000", "Should have correct PLU code"
        assert apple.commodity == "APPLES", "Should have correct commodity name"
        assert apple.variety == "Alkmene", "Should have correct variety"
        
        aurora = session.get(PluCommodity, 2)
        assert aurora is not None, "Should find Aurora apple with id 2"
        assert aurora.plu == "3001", "Should have correct PLU code"
        assert aurora.measures_na == "100 size and smaller", "Should have correct NA measures"
        
        # Test metadata fields
        assert apple.updated_by == "Netsetters Admin", "Should have correct updater"
        assert apple.updated_at.strftime("%Y-%m-%d %H:%M:%S") == "2024-02-02 19:50:24", "Should have correct update time"
        assert apple.created_at.strftime("%Y-%m-%d %H:%M:%S") == "1999-12-30 23:00:00", "Should have correct creation time"
        assert apple.deleted_at is None, "Should have no deletion time"
        assert apple.language == "EN", "Should have correct language"
