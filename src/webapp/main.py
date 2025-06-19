from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from dotenv import load_dotenv
import logging
import os
from pathlib import Path
from webapp.adapters.render import RenderDecorator

load_dotenv()

logger = logging.getLogger(__name__)
app = FastAPI()

# Configure static files and templates
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
render = RenderDecorator(templates)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root(request: Request):
    logger.info("Root endpoint called")
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request}
    )


@app.get("/api/status")
@render("status.html")
async def status(request: Request):
    """Return system information."""
    stat = os.statvfs("/")
    disk_total = stat.f_blocks * stat.f_frsize
    disk_free = stat.f_bfree * stat.f_frsize
    return {
        "hostname": os.uname().nodename,
        "platform": os.uname().sysname,
        "disk_free_gb": round(disk_free / (1024**3), 1),
        "disk_total_gb": round(disk_total / (1024**3), 1)
    }


def main():
    host = os.getenv('SERVER_HOST', '127.0.0.1')
    port = int(os.getenv('SERVER_PORT', '8000'))
    protocol = os.getenv('SERVER_PROTOCOL', 'http')
    logger.info(f"Starting server at: {protocol}://{host}:{port}")
    uvicorn.run(
        "webapp.main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=["src/webapp"],
        factory=False,
        log_config=None,
        access_log=False
    )

if __name__ == '__main__':
    main()
