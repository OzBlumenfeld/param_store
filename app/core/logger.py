import logging
import sys

def setup_logging():
    # Standard format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Create the specialized params logger
    params_logger = logging.getLogger("params")
    params_logger.setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

logger = setup_logging()
