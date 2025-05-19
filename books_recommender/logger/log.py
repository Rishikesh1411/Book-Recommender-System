import logging
import os
from datetime import datetime

# Configure logging at module level
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file = os.path.join(LOG_DIR, f"log_{timestamp}.log")

logging.basicConfig(
    filename=log_file,
    filemode='w',
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Create and export the logger
logger = logging.getLogger(__name__)