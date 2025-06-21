"""Store routes and views."""
from pathlib import Path
import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from sqlalchemy import cast, String, func
from fastapi.templating import Jinja2Templates

from webapp.database import get_session
from webapp.stores.models import Store
from webapp.stores.etl import import_chattanooga_stores

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stores", tags=["stores"])
templates = Jinja2Templates(directory="src/webapp/templates")

# Dummy data


@router.get("/", response_class=HTMLResponse)
async def list_stores(
    request: Request,
    session: Session = Depends(get_session),
    q: str = "",
    page: int = 1
):
    """List stores with search and pagination."""
    per_page = 100
    offset = (page - 1) * per_page
    
    stmt = select(Store).where(Store.is_active == True)
    if q:
        stmt = stmt.where(cast(Store.name, String).ilike(f"%{q}%"))
    
    total = session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stores = session.exec(
        stmt.order_by(Store.name).offset(offset).limit(per_page)
    ).all()
    total_pages = (total + per_page - 1) // per_page
    
    return templates.TemplateResponse(
        "stores/list.html",
        {
            "request": request,
            "stores": stores,
            "q": q,
            "page": page,
            "total_pages": total_pages,
            "total": total
        }
    )


@router.post("/import-chattanooga")
async def import_chattanooga(
    request: Request,
    session: Session = Depends(get_session)
):
    """Import Chattanooga stores from Google Maps CSV."""
    try:
        logger.info("Starting Chattanooga stores import")
        csv_path = Path("data/grocery_stores_chattanooga.csv")
        import_chattanooga_stores(csv_path)
        logger.info("Completed Chattanooga stores import")
        request.session["flash"] = [{"type": "success", "text": "Successfully imported Chattanooga stores"}]
    except Exception as e:
        logger.error(f"Failed to import Chattanooga stores: {e}")
        request.session["flash"] = [{"type": "error", "text": f"Failed to import stores: {str(e)}"}]
    return RedirectResponse(url="/stores", status_code=303)
