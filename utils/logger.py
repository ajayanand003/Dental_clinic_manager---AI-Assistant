import logging
import os
from config.config import LOG_DIR, LOG_FILE_PATH

def setup_logger():
    # Create logs directory if it doesn't exist
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
            print(f"Created logs directory at: {LOG_DIR}")
    except Exception as e:
        print(f"Error creating logs directory: {str(e)}")
        return None

    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE_PATH),
                logging.StreamHandler()
            ]
        )
        print(f"Logger initialized. Log file at: {LOG_FILE_PATH}")
        return logging.getLogger(__name__)
    except Exception as e:
        print(f"Error setting up logger: {str(e)}")
        return None

logger = setup_logger()