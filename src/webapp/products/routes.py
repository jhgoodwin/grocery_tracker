"""Product routes and views."""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from sqlmodel.orm.session import Session

from webapp.database import get_session
from webapp.products.etl import import_plu_commodities, import_all_plu_to_products

router = APIRouter(prefix="/products", tags=["products"])
templates = Jinja2Templates(directory="src/webapp/templates")

@router.get("/", response_class=HTMLResponse)
async def list_products(request: Request):
    """List all products."""
    return templates.TemplateResponse(
        "products/list.html",
        {"request": request}
    )

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
