"""Product routes and views."""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, text, or_, col
from sqlalchemy import func, cast, String, desc, asc

from webapp.database import get_session
from webapp.products.etl import import_plu_commodities, import_all_plu_to_products
from webapp.products.models import Product, ProductPrice
from webapp.products.fakeit import make_fake_prices

router = APIRouter(prefix="/products", tags=["products"])
templates = Jinja2Templates(directory="src/webapp/templates")

@router.get("/", response_class=HTMLResponse)
async def list_products(
    request: Request,
    session: Session = Depends(get_session),
    q: str = "",
    page: int = 1
):
    """List products with search and pagination."""
    per_page = 100
    offset = (page - 1) * per_page
    
    stmt = select(Product)
    if q:
        stmt = stmt.where(cast(Product.name, String).ilike(f"%{q}%"))
    
    total = session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    products = session.exec(
        stmt.order_by(Product.name).offset(offset).limit(per_page)
    ).all()
    total_pages = (total + per_page - 1) // per_page
    
    # Get lowest prices for each product
    product_ids = [p.id for p in products]
    if product_ids:
        prices_stmt = (
            select(ProductPrice)
            .where(col(ProductPrice.product_id).in_(product_ids))
            .order_by(asc(ProductPrice.price))
        )
        prices = session.exec(prices_stmt).all()
        
        # Group by product_id, keeping lowest price
        prices_by_product = {}
        for price in prices:
            if price.product_id not in prices_by_product:
                prices_by_product[price.product_id] = price
    else:
        prices_by_product = {}
    
    return templates.TemplateResponse(
        "products/list.html",
        {
            "request": request,
            "products": products,
            "q": q,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "prices": prices_by_product
        }
    )

@router.post("/fake-prices")
async def generate_fake_prices(
    request: Request,
    session: Session = Depends(get_session)
):
    """Generate fake prices for products."""
    prices = make_fake_prices(session)
    for price in prices:
        session.add(price)
    session.commit()
    return RedirectResponse(url="/products", status_code=303)

@router.post("/import-plu")
async def import_plu(
    request: Request,
    session: Session = Depends(get_session)
) -> RedirectResponse:
    """Import PLU commodities from default CSV."""
    try:
        commodities = import_plu_commodities(session)
        request.session["flash"] = [{"type": "success", "text": f"Successfully imported {len(commodities)} PLU commodities"}]
    except Exception as e:
        request.session["flash"] = [{"type": "error", "text": f"Failed to import PLU commodities: {str(e)}"}]
    return RedirectResponse(url="/products", status_code=303)

@router.post("/import-plu-products")
async def import_plu_products(
    request: Request,
    session: Session = Depends(get_session)
) -> RedirectResponse:
    """Convert all PLU commodities to products."""
    try:
        products = import_all_plu_to_products(session)
        request.session["flash"] = [{"type": "success", "text": f"Successfully converted {len(products)} PLUs to products"}]
    except Exception as e:
        request.session["flash"] = [{"type": "error", "text": f"Failed to convert PLUs to products: {str(e)}"}]
    return RedirectResponse(url="/products", status_code=303)
