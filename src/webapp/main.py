from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
import logging
import os

load_dotenv()

logger = logging.getLogger(__name__)
app = FastAPI()

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}


def main(host: str = '127.0.0.1', port: int = 8000):
    logger.info(f"Starting server on {host}:{port}")
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
