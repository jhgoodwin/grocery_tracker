import logging
import logging.config

LOG_COLORS = {
    'DEBUG': '\033[94m',    # Blue
    'INFO': '\033[92m',     # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',    # Red
    'CRITICAL': '\033[95m'  # Magenta
}
RESET = '\033[0m'

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_message = super().format(record)
        return f"{LOG_COLORS.get(record.levelname, '')}{log_message}{RESET}"

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