
import logging
import sys

from pythonjsonlogger import jsonlogger

def setup_logging():
    """
    Configures the logging for the application to output structured JSON logs.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Use a handler that outputs to stdout
    log_handler = logging.StreamHandler(sys.stdout)
    
    # Use JsonFormatter for structured logs
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    
    log_handler.setFormatter(formatter)
    
    # Avoid adding duplicate handlers
    if not logger.handlers:
        logger.addHandler(log_handler)

