from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
import logging.config
import os

load_dotenv()

def setup_logging():
    """Configure logging with YAML if available, otherwise use basic config"""
    try:
        import yaml
        with open('logging_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    except (ImportError, FileNotFoundError):
        # Set up default console logging if config fails
        logger = logging.getLogger()
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

setup_logging()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


def main(host: str = '127.0.0.1', port: int = 8000):
    uvicorn.run("webapp.main:app", host=host, port=port, reload=True, reload_dirs=["webapp"], factory=False)

if __name__ == '__main__':
    main()
