"""ETL functions for product data."""
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import csv
from sqlmodel import Session, select, insert, Column

from webapp.products.models import PluCommodity, Product


def import_all_plu_to_products(session: Session) -> List[Product]:
    """Import all PLU commodities to Products.
    
    Args:
        session: Database session
        
    Returns:
        List of created Products
    """
    stmt = select(PluCommodity)
    plus = session.exec(stmt).all()
    products = []
    
    for plu in plus:
        # Check if product already exists
        stmt = select(Product).where(Product.upc == plu.plu)
        existing = session.exec(stmt).first()
        if existing:
            products.append(existing)
            continue
            
        # Create new product
        product = Product(
            name=f"{plu.commodity} - {plu.variety}".title(),
            upc=plu.plu,
            unit="lb" if plu.measures_na else "each",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=plu.deleted_at is None
        )
        
        session.add(product)
        products.append(product)
    
    session.commit()
    return products

def import_plu_to_product(session: Session, plu_id: int) -> Optional[Product]:
    """Import a PLU commodity to a Product.
    
    Args:
        session: Database session
        plu_id: ID of PLU commodity to import
        
    Returns:
        Created Product or None if PLU not found
    """
    stmt = select(PluCommodity).where(PluCommodity.id == plu_id)
    plu = session.exec(stmt).first()
    if not plu:
        return None
        
    # Check if product with PLU already exists
    stmt = select(Product).where(Product.upc == plu.plu)
    existing = session.exec(stmt).first()
    if existing:
        return existing
        
    # Create new product from PLU
    product = Product(
        name=f"{plu.commodity} - {plu.variety}".title(),
        upc=plu.plu,
        unit="lb" if plu.measures_na else "each",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=plu.deleted_at is None
    )
    
    session.add(product)
    session.commit()
    session.refresh(product)
    
    return product


def load_plu_commodities(csv_path: Optional[Path] = None) -> List[PluCommodity]:
    """Load PLU commodities from CSV file.
    
    Args:
        csv_path: Path to CSV file, defaults to data/commodities.csv
        
    Returns:
        List of PLU commodity instances (not yet persisted)
    """
    if csv_path is None:
        csv_path = Path('data/commodities.csv')
        
    if not csv_path.exists():
        raise FileNotFoundError(f'CSV file not found: {csv_path}')
        
    commodities = []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            plu = PluCommodity(
                plu=row['Plu'],
                type=row['Type'],
                category=row['Category'],
                commodity=row['Commodity'],
                variety=row['Variety'],
                size=row['Size'],
                measures_na=row.get('Measures_na'),
                measures_row=row.get('Measures_row'),
                restrictions=row.get('Restrictions'),
                botanical=row.get('Botanical'),
                aka=row.get('Aka'),
                status=row['Status'],
                link=row.get('Link'),
                notes=row.get('Notes'),
                updated_by=row['Updated_by'],
                updated_at=datetime.strptime(row['Updated_at'], '%Y-%m-%d %H:%M:%S'),
                created_at=datetime.strptime(row['Created_at'], '%Y-%m-%d %H:%M:%S'),
                deleted_at=datetime.strptime(row['Deleted_at'], '%Y-%m-%d %H:%M:%S') if row.get('Deleted_at') else None,
                language=row['Language']
            )
            commodities.append(plu)
            
    return commodities


def save_plu_commodities(session: Session, commodities: List[PluCommodity]) -> List[PluCommodity]:
    """Save PLU commodities to database using bulk upsert.
    
    Args:
        session: Database session
        commodities: List of PLU commodity instances to save
        
    Returns:
        List of saved PLU commodities
    """
    if not commodities:
        return []
    
    saved_plus = []
    for plu in commodities:
        # Check if PLU already exists
        stmt = select(PluCommodity).where(PluCommodity.plu == plu.plu)
        existing = session.exec(stmt).first()
        
        if existing:
            # Update existing PLU
            for key, value in plu.model_dump().items():
                if key not in ['id']:
                    setattr(existing, key, value)
            saved_plus.append(existing)
        else:
            # Add new PLU
            session.add(plu)
            saved_plus.append(plu)
    
    session.commit()
    return saved_plus


def import_plu_commodities(session: Session, csv_path: Optional[Path] = None) -> List[PluCommodity]:
    """Import PLU commodities from CSV file.
    
    Args:
        session: Database session
        csv_path: Path to CSV file, defaults to data/commodities.csv
        
    Returns:
        List of created/updated PLU commodities
    """
    commodities = load_plu_commodities(csv_path)
    return save_plu_commodities(session, commodities)
