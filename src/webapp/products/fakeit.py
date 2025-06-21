"""Generate fake product prices for testing."""
from datetime import datetime
from decimal import Decimal
import random
from sqlmodel import Session, select
from itertools import groupby
from typing import List

from webapp.products.models import Product, ProductPrice, PluCommodity
from webapp.stores.models import Store


def make_fake_prices(session: Session) -> List[ProductPrice]:
    """Generate fake prices for products across stores.
    
    Takes 90% of non-retailer categories and 50% of products within each category.
    Prices range from $0.79 to $5.99, always ending in .99
    """
    # Get all stores
    stores = session.exec(select(Store)).all()
    
    # Get products with PLU codes, excluding retailer assigned
    stmt = select(Product, PluCommodity).join(
        PluCommodity,
        Product.upc == PluCommodity.plu
    ).where(PluCommodity.category != 'Retailer Assigned')
    products_with_plu = session.exec(stmt).all()
    
    # Group by category
    by_category = {}
    for prod, plu in products_with_plu:
        if plu.category != 'Retailer Assigned':
            by_category.setdefault(plu.category, []).append(prod)
    
    # Take 90% of categories
    categories = list(by_category.keys())
    num_categories = int(len(categories) * 0.9)
    selected_categories = random.sample(categories, num_categories)
    
    prices = []
    for category in selected_categories:
        # Take 50% of products in category
        products = by_category[category]
        num_products = int(len(products) * 0.5)
        selected_products = random.sample(products, num_products)
        
        # Create prices for each store
        for product in selected_products:
            for store in stores:
                base_price = random.randint(79, 500) / 100
                cents = base_price % 1
                dollars = int(base_price)
                
                # Normalize cents to common retail endings
                if cents < 0.125:
                    cents = 0
                elif cents < 0.29:
                    cents = 0.25
                elif cents < 0.415:
                    cents = 0.33
                elif cents < 0.625:
                    cents = 0.50
                elif cents < 0.875:
                    cents = 0.75
                else:
                    cents = 0.99
                
                price = Decimal(str(dollars + cents)).quantize(Decimal('.01'))
                prices.append(
                    ProductPrice(
                        product_id=product.id,
                        store_id=store.id,
                        price=price,
                        observed_at=datetime.utcnow()
                    )
                )
    
    return prices


def save_product_prices(session: Session, prices: List[ProductPrice]) -> None:
    """Save generated product prices to database."""
    for price in prices:
        session.add(price)
    session.commit()