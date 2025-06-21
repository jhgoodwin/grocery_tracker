from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from dotenv import load_dotenv
import logging
import os
from pathlib import Path
from sqlmodel import SQLModel
import glob
from webapp.adapters.render import RenderDecorator
from webapp.stores.routes import router as stores_router
from webapp.products.routes import router as products_router

load_dotenv()

logger = logging.getLogger(__name__)
app = FastAPI()

from webapp.config import engine

def run_migrations():
    """Run all migrations in order"""
    migrations_dir = Path(__file__).parent / 'migrations'
    migration_files = sorted(glob.glob(str(migrations_dir / '*.py')))
    
    for migration_file in migration_files:
        if migration_file.endswith('__init__.py'):
            continue
        module_path = f"webapp.migrations.{Path(migration_file).stem}"
        migration_module = __import__(module_path, fromlist=['run_migration'])
        migration_module.run_migration(engine)
        logger.info(f"Ran migration {module_path}")

# Ensure database and tables exist
run_migrations()

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv('SESSION_SECRET_KEY', 'dev-secret-key-do-not-use-in-production')
)

# Include routers
app.include_router(stores_router)
app.include_router(products_router)

# Configure static files and templates
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
render = RenderDecorator(str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
@render("index.html", always=True)
async def root(request: Request):
    logger.info("Root endpoint called")
    return {}


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
