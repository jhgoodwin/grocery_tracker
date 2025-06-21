"""Store routes and views."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/stores", tags=["stores"])
templates = Jinja2Templates(directory="src/webapp/templates")

@router.get("/", response_class=HTMLResponse)
async def list_stores(request: Request):
    """List all stores."""
    return templates.TemplateResponse(
        "stores/list.html",
        {"request": request}
    )
